from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class InventoryItem(Base):
    """Productos en la despensa del usuario"""
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    qty = Column(Integer, nullable=False)
    expiry = Column(String, nullable=True)  # Formato: YYYY-MM-DD
    category = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Recipe(Base):
    """Recetas disponibles"""
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    cooking_time = Column(Integer, nullable=False)  # Minutos
    difficulty = Column(String, nullable=False)  # Fácil, Media, Difícil
    servings = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)

    # Relaciones
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    nutrition = relationship("NutritionalInfo", back_populates="recipe", uselist=False, cascade="all, delete-orphan")

class RecipeIngredient(Base):
    """Ingredientes de cada receta"""
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_name = Column(String, nullable=False)
    quantity = Column(String, nullable=False)  # Ej: "200g", "2 unidades"
    is_optional = Column(Integer, default=0)  # 0=requerido, 1=opcional

    recipe = relationship("Recipe", back_populates="ingredients")

class NutritionalInfo(Base):
    """Información nutricional por porción"""
    __tablename__ = "nutritional_info"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False, unique=True)
    calories = Column(Float, nullable=False)
    proteins = Column(Float, nullable=False)  # Gramos
    carbs = Column(Float, nullable=False)  # Gramos
    fats = Column(Float, nullable=False)  # Gramos
    fiber = Column(Float, nullable=True)  # Gramos
    sodium = Column(Float, nullable=True)  # Miligramos

    recipe = relationship("Recipe", back_populates="nutrition")

class ChatMessage(Base):
    """Historial de conversaciones del chatbot"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)  # 'user' o 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String, nullable=True)  # Para agrupar conversaciones
