"""
Script para cargar recetas desde JSON a la base de datos
"""
import json
import asyncio
import sys
import os

# Añadir el directorio padre al path para importar los modelos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Base, Recipe, RecipeIngredient, NutritionalInfo

DATABASE_URL = "sqlite+aiosqlite:///./despensa.db"


async def load_recipes_from_json(json_file):
    """
    Carga recetas desde un archivo JSON a la base de datos

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

    # Conectar a la base de datos
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
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
                    image_url=recipe_data.get('image_url')
                )

                # Añadir ingredientes
                for ing_data in recipe_data.get('ingredients', []):
                    ingredient = RecipeIngredient(
                        recipe=recipe,
                        ingredient_name=ing_data['name'],
                        quantity=ing_data['quantity'],
                        is_optional=1 if ing_data.get('is_optional', False) else 0
                    )
                    session.add(ingredient)

                # Añadir información nutricional
                if 'nutrition' in recipe_data:
                    nutr = recipe_data['nutrition']
                    nutrition = NutritionalInfo(
                        recipe=recipe,
                        calories=float(nutr.get('calories', 0)),
                        proteins=float(nutr.get('proteins', 0)),
                        carbs=float(nutr.get('carbs', 0)),
                        fats=float(nutr.get('fats', 0)),
                        fiber=float(nutr.get('fiber', 0)) if nutr.get('fiber') else None,
                        sodium=float(nutr.get('sodium', 0)) if nutr.get('sodium') else None
                    )
                    session.add(nutrition)

                session.add(recipe)
                added_count += 1
                print(f"  ✅ {recipe.name}")

            except Exception as e:
                print(f"  ❌ Error con '{recipe_data.get('name', 'Desconocida')}': {e}")
                skipped_count += 1
                continue

        # Commit todas las recetas
        await session.commit()

        print("\n" + "="*60)
        print(f"✅ Carga completada!")
        print(f"  - Recetas añadidas: {added_count}")
        print(f"  - Recetas omitidas: {skipped_count}")
        print("="*60)

        # Reindexar vectorstore
        print("\n🔄 Reindexando vectorstore...")
        try:
            # Importar el sistema RAG
            from app.rag_system import rag_system
            await rag_system.reindex_recipes(session)
            print("✅ Vectorstore reindexado correctamente")
        except Exception as e:
            print(f"⚠️ No se pudo reindexar el vectorstore: {e}")
            print("   Ejecuta manualmente: POST http://localhost:8000/api/admin/reindex")


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Cargar recetas desde JSON a la base de datos')
    parser.add_argument('json_file', help='Ruta al archivo JSON con las recetas')
    args = parser.parse_args()

    if not os.path.exists(args.json_file):
        print(f"❌ Error: El archivo '{args.json_file}' no existe")
        return

    print("🍳 Cargando recetas a la base de datos...")
    print("-" * 60)

    asyncio.run(load_recipes_from_json(args.json_file))

    print("\n💡 Las recetas ya están disponibles en la API!")
    print("   Puedes verlas en: http://localhost:8000/api/recipes")


if __name__ == "__main__":
    main()
