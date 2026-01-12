"""
Script para cargar recetas desde JSON a MongoDB
"""
import json
import asyncio
import sys
import os

# Añadir el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import Recipe

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "despensa")


async def load_recipes_from_json(json_file):
    """
    Carga recetas desde un archivo JSON a MongoDB

    Args:
        json_file: Ruta al archivo JSON con las recetas
    """
    # Leer JSON
    print(f"📖 Leyendo archivo: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    recipes_data = data.get('recipes', [])
    print(f"📦 Encontradas {len(recipes_data)} recetas")

    if not recipes_data:
        print("⚠️ No se encontraron recetas en el JSON")
        return

    # Conectar a MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    await init_beanie(database=client[MONGODB_DB_NAME], document_models=[Recipe])

    print(f"✅ Conectado a MongoDB: {MONGODB_URL}/{MONGODB_DB_NAME}")

    added_count = 0
    skipped_count = 0

    for recipe_data in recipes_data:
        try:
            # Crear receta
            recipe = Recipe(
                name=recipe_data['name'],
                description=recipe_data['description'],
                instructions=recipe_data['instructions'],
                cooking_time=recipe_data['cooking_time'],
                difficulty=recipe_data['difficulty'],
                servings=recipe_data['servings'],
                image_url=recipe_data.get('image_url'),
                ingredients=recipe_data.get('ingredients', []),
                nutrition=recipe_data.get('nutrition'),
                estimated_price=recipe_data.get('estimated_price'),
                equipment=recipe_data.get('equipment', [])
            )

            await recipe.insert()
            added_count += 1
            print(f"  ✅ {recipe.name}")

        except Exception as e:
            print(f"  ❌ Error con '{recipe_data.get('name', 'Desconocida')}': {e}")
            skipped_count += 1
            continue

    print("\n" + "="*60)
    print(f"✅ Carga completada!")
    print(f"  - Recetas añadidas: {added_count}")
    print(f"  - Recetas omitidas: {skipped_count}")
    print("="*60)

    # Reindexar vectorstore
    print("\n🔄 Reindexando vectorstore...")
    try:
        from app.rag_system import rag_system
        await rag_system.reindex_recipes()
        print("✅ Vectorstore reindexado correctamente")
    except Exception as e:
        print(f"⚠️ No se pudo reindexar el vectorstore: {e}")
        print("   Ejecuta manualmente: POST http://localhost:8000/api/admin/reindex")


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Cargar recetas desde JSON a MongoDB')
    parser.add_argument('json_file', help='Ruta al archivo JSON con las recetas')
    args = parser.parse_args()

    if not os.path.exists(args.json_file):
        print(f"❌ Error: El archivo '{args.json_file}' no existe")
        return

    print("🍳 Cargando recetas a MongoDB...")
    print("-" * 60)

    asyncio.run(load_recipes_from_json(args.json_file))

    print("\n💡 Las recetas ya están disponibles en la API!")
    print("   Puedes verlas en: http://localhost:8000/api/recipes")


if __name__ == "__main__":
    main()
