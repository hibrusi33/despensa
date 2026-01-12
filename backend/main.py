from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId

from app.database import init_db, close_db
from app.models import InventoryItem, Recipe, ChatMessage
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

# ===== INVENTORY ENDPOINTS =====

@app.get("/api/inventory")
async def get_inventory():
    """Get all inventory items"""
    items = await InventoryItem.find_all().to_list()
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
async def create_inventory_item(item: InventoryItemCreate):
    """Add item to inventory"""
    db_item = InventoryItem(**item.dict())
    await db_item.insert()
    return {
        "id": str(db_item.id),
        "name": db_item.name,
        "qty": db_item.qty,
        "expiry": db_item.expiry,
        "category": db_item.category
    }

@app.put("/api/inventory/{item_id}")
async def update_inventory_item(item_id: str, item_update: InventoryItemUpdate):
    """Update inventory item"""
    db_item = await InventoryItem.get(PydanticObjectId(item_id))

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

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
async def delete_inventory_item(item_id: str):
    """Delete inventory item"""
    db_item = await InventoryItem.get(PydanticObjectId(item_id))

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

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
async def get_suggested_recipes():
    """Get recipes suggested based on current inventory"""
    matching_recipes = await rag_system.find_matching_recipes()
    return matching_recipes

# ===== CHAT ENDPOINTS =====

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with AI assistant"""
    # Get AI response
    response = await rag_system.chat(
        request.message,
        request.conversation_history
    )

    # Save message to history
    user_msg = ChatMessage(role="user", content=request.message)
    assistant_msg = ChatMessage(role="assistant", content=response)

    await user_msg.insert()
    await assistant_msg.insert()

    # Get suggested recipes
    suggested_recipes = await rag_system.find_matching_recipes(request.message)

    return {
        "response": response,
        "suggested_recipes": suggested_recipes[:3] if suggested_recipes else None
    }

@app.get("/api/chat/history")
async def get_chat_history(limit: int = 20):
    """Get chat history"""
    messages = await ChatMessage.find_all().sort("-created_at").limit(limit).to_list()

    return [
        {
            "id": str(msg.id),
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in reversed(messages)
    ]

# ===== ADMIN ENDPOINTS =====

@app.post("/api/admin/reindex")
async def reindex_recipes():
    """Re-index all recipes in vector database"""
    await rag_system.reindex_recipes()
    return {"message": "Recipes re-indexed successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
