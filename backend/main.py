from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId
import stripe
import os

from app.database import init_db, close_db
from app.models import InventoryItem, Recipe, ChatMessage, User, Ticket, MealPlan, UsageStats, SubscriptionTier
from app.rag_system import rag_system
from app.auth import create_access_token, get_current_user, require_premium, get_password_hash, verify_password
from app.meal_planner import meal_planner

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = FastAPI(title="Despensa API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for requests/responses
class InventoryItemCreate(BaseModel):
    name: str
    qty: int
    expiry: Optional[str] = None
    category: str

class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    qty: Optional[int] = None
    expiry: Optional[str] = None
    category: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = None

class ChatResponse(BaseModel):
    response: str
    suggested_recipes: Optional[List[dict]] = None

# Authentication models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    household_size: Optional[int] = None
    accepts_data_analysis: bool = False
    accepts_anonymized_sale: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

# Meal plan models
class MealPlanRequest(BaseModel):
    month: int
    year: int
    target_calories: int = 2000
    dietary_preferences: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    meals_per_day: int = 3

# Subscription models
class SubscriptionUpgrade(BaseModel):
    tier: SubscriptionTier
    payment_method_id: str

# Ticket models
class TicketCreate(BaseModel):
    supermarket: str
    total_amount: float
    items: List[dict]

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and RAG system"""
    await init_db()
    print("✅ Database initialized")

    # Initialize RAG system
    await rag_system.initialize_vectorstore()
    print("✅ RAG system initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection"""
    await close_db()

# Health check
@app.get("/")
async def root():
    return {"status": "ok", "message": "Despensa API is running with MongoDB"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "MongoDB"}

# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register a new user"""
    # Check if user already exists
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name,
        age=user_data.age,
        gender=user_data.gender,
        household_size=user_data.household_size,
        accepts_data_analysis=user_data.accepts_data_analysis,
        accepts_anonymized_sale=user_data.accepts_anonymized_sale
    )

    await user.insert()

    # Create usage stats for new user
    usage_stats = UsageStats(user_id=str(user.id))
    await usage_stats.insert()

    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "subscription_tier": user.subscription_tier
        }
    }

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user"""
    # Find user by email
    user = await User.find_one(User.email == credentials.email)
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "subscription_tier": user.subscription_tier
        }
    }

@app.get("/api/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "age": current_user.age,
        "gender": current_user.gender,
        "household_size": current_user.household_size,
        "subscription_tier": current_user.subscription_tier,
        "subscription_status": current_user.subscription_status,
        "created_at": current_user.created_at.isoformat()
    }

# ===== INVENTORY ENDPOINTS =====

@app.get("/api/inventory")
async def get_inventory(current_user: User = Depends(get_current_user)):
    """Get all inventory items for current user"""
    items = await InventoryItem.find(
        InventoryItem.user_id == str(current_user.id)
    ).to_list()
    return [
        {
            "id": str(item.id),
            "name": item.name,
            "qty": item.qty,
            "expiry": item.expiry,
            "category": item.category
        }
        for item in items
    ]

@app.post("/api/inventory")
async def create_inventory_item(
    item: InventoryItemCreate,
    current_user: User = Depends(get_current_user)
):
    """Add item to inventory"""
    db_item = InventoryItem(
        **item.dict(),
        user_id=str(current_user.id)
    )
    await db_item.insert()
    return {
        "id": str(db_item.id),
        "name": db_item.name,
        "qty": db_item.qty,
        "expiry": db_item.expiry,
        "category": db_item.category
    }

@app.put("/api/inventory/{item_id}")
async def update_inventory_item(
    item_id: str,
    item_update: InventoryItemUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update inventory item"""
    db_item = await InventoryItem.get(PydanticObjectId(item_id))

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check ownership
    if db_item.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this item")

    # Update fields
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db_item.updated_at = datetime.utcnow()
    await db_item.save()

    return {
        "id": str(db_item.id),
        "name": db_item.name,
        "qty": db_item.qty,
        "expiry": db_item.expiry,
        "category": db_item.category
    }

@app.delete("/api/inventory/{item_id}")
async def delete_inventory_item(
    item_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete inventory item"""
    db_item = await InventoryItem.get(PydanticObjectId(item_id))

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check ownership
    if db_item.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this item")

    await db_item.delete()
    return {"message": "Item deleted successfully"}

# ===== RECIPES ENDPOINTS =====

@app.get("/api/recipes")
async def get_recipes():
    """Get all recipes"""
    recipes = await Recipe.find_all().to_list()

    return [
        {
            "id": str(recipe.id),
            "name": recipe.name,
            "description": recipe.description,
            "cooking_time": recipe.cooking_time,
            "difficulty": recipe.difficulty,
            "servings": recipe.servings,
            "ingredients": recipe.ingredients,
            "nutrition": recipe.nutrition,
            "estimated_price": recipe.estimated_price,
            "equipment": recipe.equipment
        }
        for recipe in recipes
    ]

@app.get("/api/recipes/suggested")
async def get_suggested_recipes(current_user: User = Depends(get_current_user)):
    """Get recipes suggested based on current inventory"""
    matching_recipes = await rag_system.find_matching_recipes(user_id=str(current_user.id))
    return matching_recipes

# ===== CHAT ENDPOINTS =====

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Chat with AI assistant"""
    # Update usage stats
    stats = await UsageStats.find_one(UsageStats.user_id == str(current_user.id))
    if stats:
        stats.chat_messages += 1
        stats.ai_calls += 1
        await stats.save()

    # Get AI response
    response = await rag_system.chat(
        user_message=request.message,
        conversation_history=request.conversation_history,
        user_id=str(current_user.id)
    )

    # Save message to history
    user_msg = ChatMessage(
        role="user",
        content=request.message,
        user_id=str(current_user.id)
    )
    assistant_msg = ChatMessage(
        role="assistant",
        content=response,
        user_id=str(current_user.id)
    )

    await user_msg.insert()
    await assistant_msg.insert()

    # Get suggested recipes
    suggested_recipes = await rag_system.find_matching_recipes(
        query=request.message,
        user_id=str(current_user.id)
    )

    return {
        "response": response,
        "suggested_recipes": suggested_recipes[:3] if suggested_recipes else None
    }

@app.get("/api/chat/history")
async def get_chat_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get chat history for current user"""
    messages = await ChatMessage.find(
        ChatMessage.user_id == str(current_user.id)
    ).sort("-created_at").limit(limit).to_list()

    return [
        {
            "id": str(msg.id),
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in reversed(messages)
    ]

# ===== MEAL PLAN ENDPOINTS (PREMIUM) =====

@app.post("/api/meal-plans/generate")
async def generate_meal_plan(
    request: MealPlanRequest,
    current_user: User = Depends(require_premium)
):
    """Generate monthly meal plan (Premium feature)"""
    try:
        # Generate meal plan
        meal_plan = await meal_planner.generate_monthly_plan(
            user=current_user,
            month=request.month,
            year=request.year,
            target_calories=request.target_calories,
            dietary_preferences=request.dietary_preferences,
            allergies=request.allergies,
            meals_per_day=request.meals_per_day
        )

        # Update usage stats
        stats = await UsageStats.find_one(UsageStats.user_id == str(current_user.id))
        if stats:
            stats.meal_plans_generated += 1
            await stats.save()

        return {
            "id": str(meal_plan.id),
            "name": meal_plan.name,
            "month": meal_plan.month,
            "year": meal_plan.year,
            "target_calories": meal_plan.target_calories,
            "meals_per_day": meal_plan.meals_per_day,
            "weekly_plans": meal_plan.weekly_plans,
            "shopping_list": meal_plan.shopping_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meal-plans")
async def get_meal_plans(current_user: User = Depends(require_premium)):
    """Get all meal plans for current user (Premium feature)"""
    meal_plans = await MealPlan.find(
        MealPlan.user_id == str(current_user.id)
    ).sort("-created_at").to_list()

    return [
        {
            "id": str(plan.id),
            "name": plan.name,
            "month": plan.month,
            "year": plan.year,
            "target_calories": plan.target_calories,
            "created_at": plan.created_at.isoformat()
        }
        for plan in meal_plans
    ]

@app.get("/api/meal-plans/{plan_id}")
async def get_meal_plan(plan_id: str, current_user: User = Depends(require_premium)):
    """Get specific meal plan (Premium feature)"""
    meal_plan = await MealPlan.get(PydanticObjectId(plan_id))

    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    if meal_plan.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this meal plan")

    return {
        "id": str(meal_plan.id),
        "name": meal_plan.name,
        "description": meal_plan.description,
        "month": meal_plan.month,
        "year": meal_plan.year,
        "target_calories": meal_plan.target_calories,
        "dietary_preferences": meal_plan.dietary_preferences,
        "allergies": meal_plan.allergies,
        "meals_per_day": meal_plan.meals_per_day,
        "weekly_plans": meal_plan.weekly_plans,
        "shopping_list": meal_plan.shopping_list,
        "created_at": meal_plan.created_at.isoformat()
    }

# ===== TICKET ENDPOINTS =====

@app.post("/api/tickets")
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user)
):
    """Upload a scanned ticket"""
    ticket = Ticket(
        user_id=str(current_user.id),
        supermarket=ticket_data.supermarket,
        total_amount=ticket_data.total_amount,
        items=ticket_data.items
    )

    await ticket.insert()

    return {
        "id": str(ticket.id),
        "message": "Ticket uploaded successfully"
    }

# ===== SUBSCRIPTION ENDPOINTS =====

@app.post("/api/subscriptions/upgrade")
async def upgrade_subscription(
    upgrade_data: SubscriptionUpgrade,
    current_user: User = Depends(get_current_user)
):
    """Upgrade user subscription"""
    try:
        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.name,
                payment_method=upgrade_data.payment_method_id,
                invoice_settings={"default_payment_method": upgrade_data.payment_method_id}
            )
            current_user.stripe_customer_id = customer.id
        else:
            # Attach payment method to existing customer
            stripe.PaymentMethod.attach(
                upgrade_data.payment_method_id,
                customer=current_user.stripe_customer_id
            )
            stripe.Customer.modify(
                current_user.stripe_customer_id,
                invoice_settings={"default_payment_method": upgrade_data.payment_method_id}
            )

        # Determine price ID based on tier
        price_ids = {
            SubscriptionTier.PREMIUM: os.getenv("STRIPE_PREMIUM_PRICE_ID"),
            SubscriptionTier.PREMIUM_PLUS: os.getenv("STRIPE_PREMIUM_PLUS_PRICE_ID")
        }

        price_id = price_ids.get(upgrade_data.tier)
        if not price_id:
            raise HTTPException(status_code=400, detail="Invalid subscription tier")

        # Create subscription
        subscription = stripe.Subscription.create(
            customer=current_user.stripe_customer_id,
            items=[{"price": price_id}],
            expand=["latest_invoice.payment_intent"]
        )

        # Update user subscription
        current_user.subscription_tier = upgrade_data.tier
        current_user.subscription_status = "active"
        current_user.stripe_subscription_id = subscription.id

        await current_user.save()

        return {
            "message": f"Successfully upgraded to {upgrade_data.tier}",
            "subscription_tier": current_user.subscription_tier,
            "subscription_status": current_user.subscription_status
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/subscriptions/cancel")
async def cancel_subscription(current_user: User = Depends(get_current_user)):
    """Cancel user subscription"""
    if current_user.subscription_tier == SubscriptionTier.FREE:
        raise HTTPException(status_code=400, detail="No active subscription to cancel")

    try:
        if current_user.stripe_subscription_id:
            # Cancel at period end (user keeps access until end of billing period)
            stripe.Subscription.modify(
                current_user.stripe_subscription_id,
                cancel_at_period_end=True
            )

        current_user.subscription_status = "cancelled"
        await current_user.save()

        return {
            "message": "Subscription cancelled. Access will continue until end of billing period.",
            "subscription_status": current_user.subscription_status
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/subscriptions/status")
async def get_subscription_status(current_user: User = Depends(get_current_user)):
    """Get subscription status"""
    subscription_info = {
        "subscription_tier": current_user.subscription_tier,
        "subscription_status": current_user.subscription_status,
        "features": {
            "meal_plan_generation": current_user.subscription_tier != SubscriptionTier.FREE,
            "premium_recipes": current_user.subscription_tier != SubscriptionTier.FREE,
            "advanced_ai": current_user.subscription_tier == SubscriptionTier.PREMIUM_PLUS
        }
    }

    # Get usage stats
    stats = await UsageStats.find_one(UsageStats.user_id == str(current_user.id))
    if stats:
        subscription_info["usage"] = {
            "chat_messages": stats.chat_messages,
            "meal_plans_generated": stats.meal_plans_generated,
            "ai_calls": stats.ai_calls,
            "period_start": stats.period_start.isoformat(),
            "period_end": stats.period_end.isoformat()
        }

    # Get Stripe subscription details if exists
    if current_user.stripe_subscription_id:
        try:
            stripe_subscription = stripe.Subscription.retrieve(current_user.stripe_subscription_id)
            subscription_info["billing"] = {
                "current_period_end": datetime.fromtimestamp(stripe_subscription.current_period_end).isoformat(),
                "cancel_at_period_end": stripe_subscription.cancel_at_period_end
            }
        except stripe.error.StripeError:
            pass

    return subscription_info

# ===== STRIPE WEBHOOK =====

@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle different event types
    if event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]

        # Find user by Stripe customer ID
        user = await User.find_one(User.stripe_customer_id == customer_id)
        if user:
            # Update subscription status
            if subscription["status"] == "active":
                user.subscription_status = "active"
            elif subscription["status"] == "canceled":
                user.subscription_status = "cancelled"
                user.subscription_tier = SubscriptionTier.FREE
            elif subscription["status"] == "past_due":
                user.subscription_status = "past_due"

            await user.save()

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]

        # Find user and downgrade to free
        user = await User.find_one(User.stripe_customer_id == customer_id)
        if user:
            user.subscription_tier = SubscriptionTier.FREE
            user.subscription_status = "cancelled"
            user.stripe_subscription_id = None
            await user.save()

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        customer_id = invoice["customer"]

        # Find user and mark subscription as past due
        user = await User.find_one(User.stripe_customer_id == customer_id)
        if user:
            user.subscription_status = "past_due"
            await user.save()

    return {"status": "success"}

# ===== ADMIN ENDPOINTS =====

@app.post("/api/admin/reindex")
async def reindex_recipes():
    """Re-index all recipes in vector database"""
    await rag_system.reindex_recipes()
    return {"message": "Recipes re-indexed successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
