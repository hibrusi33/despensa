from beanie import Document
from pydantic import Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SubscriptionTier(str, Enum):
    """Niveles de suscripción"""
    FREE = "free"
    PREMIUM = "premium"
    PREMIUM_PLUS = "premium_plus"


class PaymentStatus(str, Enum):
    """Estado de pagos"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"


class User(Document):
    """Usuario de la aplicación"""
    email: EmailStr
    password_hash: str
    name: str

    # Información demográfica
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[dict] = None  # {city, country, lat, lng}
    household_size: Optional[int] = None

    # Suscripción
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    subscription_status: PaymentStatus = PaymentStatus.ACTIVE
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None

    # Consentimientos GDPR
    accepts_data_analysis: bool = False
    accepts_anonymized_sale: bool = False

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True

    class Settings:
        name = "users"
        indexes = [
            "email",
            "subscription_tier",
            "stripe_customer_id"
        ]


class Ticket(Document):
    """Ticket de compra escaneado"""
    user_id: str  # ObjectId del usuario

    # Información del ticket
    supermarket: str
    supermarket_chain: Optional[str] = None
    total_amount: float
    purchase_date: datetime

    # Items del ticket
    items: List[dict] = []  # [{name, quantity, price, category}]

    # Metadata
    scanned_at: datetime = Field(default_factory=datetime.utcnow)
    synced_to_analytics: bool = False

    # OCR info (si se implementa)
    ocr_confidence: Optional[float] = None
    raw_ocr_text: Optional[str] = None

    class Settings:
        name = "tickets"
        indexes = [
            "user_id",
            "supermarket",
            "purchase_date",
            "synced_to_analytics"
        ]


class MealPlan(Document):
    """Plan de comidas mensual (Feature Premium)"""
    user_id: str

    # Plan info
    month: int  # 1-12
    year: int
    name: str  # "Plan de Enero 2025"
    description: Optional[str] = None

    # Configuración
    target_calories: Optional[int] = None
    dietary_preferences: List[str] = []  # ["vegetarian", "low-carb", etc.]
    allergies: List[str] = []
    meals_per_day: int = 3

    # Plan generado
    weekly_plans: List[dict] = []  # Array de semanas con días y comidas
    """
    weekly_plans formato:
    [
        {
            "week": 1,
            "days": [
                {
                    "day": "Lunes",
                    "meals": {
                        "breakfast": {recipe_id, recipe_name, calories},
                        "lunch": {recipe_id, recipe_name, calories},
                        "dinner": {recipe_id, recipe_name, calories}
                    }
                }
            ]
        }
    ]
    """

    # Shopping list generada
    shopping_list: List[dict] = []  # Ingredientes necesarios para el mes

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by_ai: bool = True

    class Settings:
        name = "meal_plans"
        indexes = [
            "user_id",
            ("year", "month")
        ]


class InventoryItem(Document):
    """Productos en la despensa del usuario"""
    user_id: str  # Añadido para multi-usuario
    name: str
    qty: int
    expiry: Optional[str] = None
    category: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "inventory_items"
        indexes = [
            "user_id",
            "name",
            "category",
            "expiry"
        ]


class Recipe(Document):
    """Recetas disponibles"""
    name: str
    description: str
    instructions: str
    cooking_time: int
    difficulty: str
    servings: int
    image_url: Optional[str] = None

    # Subdocumentos embebidos
    ingredients: List[dict] = []
    nutrition: Optional[dict] = None

    # Campos adicionales
    estimated_price: Optional[float] = None
    equipment: Optional[List[dict]] = None

    # Premium features
    is_premium: bool = False  # Solo accesible para usuarios premium
    dietary_tags: List[str] = []  # ["vegetarian", "vegan", "gluten-free", etc.]

    class Settings:
        name = "recipes"
        indexes = [
            "name",
            "difficulty",
            "cooking_time",
            "is_premium",
            "dietary_tags"
        ]


class ChatMessage(Document):
    """Historial de conversaciones del chatbot"""
    user_id: str  # Añadido para multi-usuario
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None

    # AI model usado
    model_used: Optional[str] = None  # "ollama:llama3.1:8b" o "groq:llama-3.1-70b"

    class Settings:
        name = "chat_messages"
        indexes = [
            "user_id",
            "session_id",
            "created_at"
        ]


class UsageStats(Document):
    """Estadísticas de uso para rate limiting"""
    user_id: str
    date: datetime

    # Contadores
    chat_messages: int = 0
    recipes_viewed: int = 0
    meal_plans_generated: int = 0
    ai_calls: int = 0

    class Settings:
        name = "usage_stats"
        indexes = [
            ("user_id", "date")
        ]
