from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database import init_db, get_db
from app.models import InventoryItem, Recipe, RecipeIngredient, NutritionalInfo, ChatMessage
from app.rag_system import rag_system

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

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and RAG system"""
    await init_db()
    print("✅ Database initialized")

    # Initialize RAG system with a database session
    async for db in get_db():
        await rag_system.initialize_vectorstore(db)
        break
    print("✅ RAG system initialized")

# Health check
@app.get("/")
async def root():
    return {"status": "ok", "message": "Despensa API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ===== INVENTORY ENDPOINTS =====

@app.get("/api/inventory")
async def get_inventory(db: AsyncSession = Depends(get_db)):
    """Get all inventory items"""
    result = await db.execute(select(InventoryItem))
    items = result.scalars().all()
    return [
        {
            "id": item.id,
            "name": item.name,
            "qty": item.qty,
            "expiry": item.expiry,
            "category": item.category
        }
        for item in items
    ]

@app.post("/api/inventory")
async def create_inventory_item(item: InventoryItemCreate, db: AsyncSession = Depends(get_db)):
    """Add item to inventory"""
    db_item = InventoryItem(**item.dict())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return {
        "id": db_item.id,
        "name": db_item.name,
        "qty": db_item.qty,
        "expiry": db_item.expiry,
        "category": db_item.category
    }

@app.put("/api/inventory/{item_id}")
async def update_inventory_item(
    item_id: int,
    item_update: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update inventory item"""
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update fields
    for field, value in item_update.dict(exclude_unset=True).items():
        setattr(db_item, field, value)

    db_item.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_item)

    return {
        "id": db_item.id,
        "name": db_item.name,
        "qty": db_item.qty,
        "expiry": db_item.expiry,
        "category": db_item.category
    }

@app.delete("/api/inventory/{item_id}")
async def delete_inventory_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Delete inventory item"""
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(db_item)
    await db.commit()
    return {"message": "Item deleted successfully"}

# ===== RECIPES ENDPOINTS =====

@app.get("/api/recipes")
async def get_recipes(db: AsyncSession = Depends(get_db)):
    """Get all recipes"""
    result = await db.execute(
        select(Recipe).options(
            selectinload(Recipe.ingredients),
            selectinload(Recipe.nutrition)
        )
    )
    recipes = result.scalars().all()

    return [
        {
            "id": recipe.id,
            "name": recipe.name,
            "description": recipe.description,
            "cooking_time": recipe.cooking_time,
            "difficulty": recipe.difficulty,
            "servings": recipe.servings,
            "ingredients": [
                {
                    "name": ing.ingredient_name,
                    "quantity": ing.quantity,
                    "is_optional": bool(ing.is_optional)
                }
                for ing in recipe.ingredients
            ],
            "nutrition": {
                "calories": recipe.nutrition.calories,
                "proteins": recipe.nutrition.proteins,
                "carbs": recipe.nutrition.carbs,
                "fats": recipe.nutrition.fats
            } if recipe.nutrition else None
        }
        for recipe in recipes
    ]

@app.get("/api/recipes/suggested")
async def get_suggested_recipes(db: AsyncSession = Depends(get_db)):
    """Get recipes suggested based on current inventory"""
    matching_recipes = await rag_system.find_matching_recipes(db)
    return matching_recipes

# ===== CHAT ENDPOINTS =====

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Chat with AI assistant"""
    # Get AI response
    response = await rag_system.chat(
        db,
        request.message,
        request.conversation_history
    )

    # Save message to history
    user_msg = ChatMessage(role="user", content=request.message)
    assistant_msg = ChatMessage(role="assistant", content=response)

    db.add(user_msg)
    db.add(assistant_msg)
    await db.commit()

    # Get suggested recipes
    suggested_recipes = await rag_system.find_matching_recipes(db, request.message)

    return {
        "response": response,
        "suggested_recipes": suggested_recipes[:3] if suggested_recipes else None
    }

@app.get("/api/chat/history")
async def get_chat_history(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Get chat history"""
    result = await db.execute(
        select(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(limit)
    )
    messages = result.scalars().all()

    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in reversed(messages)
    ]

# ===== ADMIN ENDPOINTS =====

@app.post("/api/admin/reindex")
async def reindex_recipes(db: AsyncSession = Depends(get_db)):
    """Re-index all recipes in vector database"""
    await rag_system.reindex_recipes(db)
    return {"message": "Recipes re-indexed successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
