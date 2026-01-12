"""Script para poblar la base de datos MongoDB con recetas de ejemplo"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import Recipe
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "despensa")


async def seed_recipes():
    """Poblar MongoDB con recetas de ejemplo"""
    # Conectar a MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    await init_beanie(database=client[MONGODB_DB_NAME], document_models=[Recipe])

    print(f"📦 Conectado a MongoDB: {MONGODB_URL}/{MONGODB_DB_NAME}")

    # Limpiar recetas existentes (opcional)
    await Recipe.delete_all()
    print("🗑️  Recetas anteriores eliminadas")

    # Receta 1: Tortilla Española
    recipe1 = Recipe(
        name="Tortilla Española",
        description="Clásica tortilla de patatas española, jugosa y deliciosa",
        instructions="""1. Pela y corta las patatas en rodajas finas
2. Fríe las patatas en aceite de oliva a fuego medio hasta que estén tiernas
3. Escurre el exceso de aceite
4. Bate los huevos en un bol grande
5. Mezcla las patatas con los huevos batidos
6. En una sartén caliente con un poco de aceite, vierte la mezcla
7. Cocina a fuego medio durante 5 minutos
8. Dale la vuelta con ayuda de un plato y cocina otros 3-4 minutos
9. Deja reposar 5 minutos antes de servir""",
        cooking_time=30,
        difficulty="Media",
        servings=4,
        ingredients=[
            {"name": "Patatas", "quantity": "4 unidades medianas", "is_optional": False},
            {"name": "Huevos", "quantity": "6 unidades", "is_optional": False},
            {"name": "Aceite de oliva", "quantity": "200ml", "is_optional": False},
            {"name": "Sal", "quantity": "al gusto", "is_optional": False},
            {"name": "Cebolla", "quantity": "1 unidad", "is_optional": True},
        ],
        nutrition={
            "calories": 320.0,
            "proteins": 14.5,
            "carbs": 24.0,
            "fats": 19.0,
            "fiber": 2.5,
            "sodium": 380.0
        },
        estimated_price=3.50,
        equipment=[
            {"primary": "Sartén antiadherente", "alternatives": ["Sartén de hierro", "Sartén normal"]}
        ]
    )

    # Receta 2: Arroz con Pollo
    recipe2 = Recipe(
        name="Arroz con Pollo",
        description="Arroz caldoso con pollo, pimiento y especias",
        instructions="""1. Corta el pollo en trozos y sazónalos
2. Dora el pollo en una cazuela con aceite
3. Retira el pollo y sofríe ajo, cebolla y pimientos
4. Añade el tomate triturado y cocina 5 minutos
5. Incorpora el arroz y mézclalo bien
6. Agrega el caldo caliente (3 veces el volumen del arroz)
7. Coloca el pollo encima
8. Cocina a fuego medio-bajo durante 18-20 minutos
9. Deja reposar 5 minutos antes de servir""",
        cooking_time=45,
        difficulty="Media",
        servings=4,
        ingredients=[
            {"name": "Pollo", "quantity": "600g (muslos o pechuga)", "is_optional": False},
            {"name": "Arroz", "quantity": "400g", "is_optional": False},
            {"name": "Pimientos", "quantity": "2 unidades", "is_optional": False},
            {"name": "Tomate", "quantity": "400g triturado", "is_optional": False},
            {"name": "Caldo de pollo", "quantity": "1.2 litros", "is_optional": False},
        ],
        nutrition={
            "calories": 485.0,
            "proteins": 32.0,
            "carbs": 68.0,
            "fats": 10.5,
            "fiber": 3.2,
            "sodium": 580.0
        },
        estimated_price=8.50,
        equipment=[
            {"primary": "Cazuela grande", "alternatives": ["Paellera", "Olla honda"]}
        ]
    )

    # Más recetas (Carbonara, César, Gazpacho)...
    recipe3 = Recipe(
        name="Pasta Carbonara",
        description="Pasta cremosa con panceta, huevo y queso parmesano",
        instructions="1. Cuece la pasta\n2. Fríe la panceta\n3. Mezcla huevo y parmesano\n4. Combina todo",
        cooking_time=20,
        difficulty="Fácil",
        servings=4,
        ingredients=[
            {"name": "Pasta", "quantity": "400g", "is_optional": False},
            {"name": "Panceta", "quantity": "200g", "is_optional": False},
            {"name": "Huevos", "quantity": "4 unidades", "is_optional": False},
        ],
        nutrition={"calories": 620.0, "proteins": 28.0, "carbs": 72.0, "fats": 24.0},
        estimated_price=5.50
    )

    # Insertar todas las recetas
    await recipe1.insert()
    await recipe2.insert()
    await recipe3.insert()

    print("✅ Se han añadido 3 recetas de ejemplo a MongoDB")


if __name__ == "__main__":
    asyncio.run(seed_recipes())
