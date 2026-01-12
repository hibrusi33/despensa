from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime


class InventoryItem(Document):
    """Productos en la despensa del usuario"""
    name: str
    qty: int
    expiry: Optional[str] = None  # Formato: YYYY-MM-DD
    category: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "inventory_items"
        indexes = [
            "name",
            "category",
            "expiry"
        ]


class RecipeIngredient(Document):
    """Ingredientes de cada receta (embedded)"""
    ingredient_name: str
    quantity: str  # Ej: "200g", "2 unidades"
    is_optional: bool = False


class NutritionalInfo(Document):
    """Información nutricional por porción (embedded)"""
    calories: float
    proteins: float  # Gramos
    carbs: float  # Gramos
    fats: float  # Gramos
    fiber: Optional[float] = None  # Gramos
    sodium: Optional[float] = None  # Miligramos


class Recipe(Document):
    """Recetas disponibles"""
    name: str
    description: str
    instructions: str
    cooking_time: int  # Minutos
    difficulty: str  # Fácil, Media, Difícil
    servings: int
    image_url: Optional[str] = None

    # Subdocumentos embebidos
    ingredients: List[dict] = []  # Lista de ingredientes como dict
    nutrition: Optional[dict] = None  # Info nutricional como dict

    # Campos adicionales del scraping
    estimated_price: Optional[float] = None
    equipment: Optional[List[dict]] = None  # [{"primary": "Wok", "alternatives": ["Sartén"]}]

    class Settings:
        name = "recipes"
        indexes = [
            "name",
            "difficulty",
            "cooking_time"
        ]


class ChatMessage(Document):
    """Historial de conversaciones del chatbot"""
    role: str  # 'user' o 'assistant'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None  # Para agrupar conversaciones

    class Settings:
        name = "chat_messages"
        indexes = [
            "session_id",
            "created_at"
        ]
