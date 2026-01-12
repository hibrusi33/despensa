"""Script para poblar la base de datos con recetas de ejemplo"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Base, Recipe, RecipeIngredient, NutritionalInfo

DATABASE_URL = "sqlite+aiosqlite:///./despensa.db"

async def seed_recipes():
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
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
            servings=4
        )

        ingredients1 = [
            RecipeIngredient(recipe=recipe1, ingredient_name="Patatas", quantity="4 unidades medianas", is_optional=0),
            RecipeIngredient(recipe=recipe1, ingredient_name="Huevos", quantity="6 unidades", is_optional=0),
            RecipeIngredient(recipe=recipe1, ingredient_name="Aceite de oliva", quantity="200ml", is_optional=0),
            RecipeIngredient(recipe=recipe1, ingredient_name="Sal", quantity="al gusto", is_optional=0),
            RecipeIngredient(recipe=recipe1, ingredient_name="Cebolla", quantity="1 unidad", is_optional=1),
        ]

        nutrition1 = NutritionalInfo(
            recipe=recipe1,
            calories=320,
            proteins=14.5,
            carbs=24.0,
            fats=19.0,
            fiber=2.5,
            sodium=380
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
            servings=4
        )

        ingredients2 = [
            RecipeIngredient(recipe=recipe2, ingredient_name="Pollo", quantity="600g (muslos o pechuga)", is_optional=0),
            RecipeIngredient(recipe=recipe2, ingredient_name="Arroz", quantity="400g", is_optional=0),
            RecipeIngredient(recipe=recipe2, ingredient_name="Pimientos", quantity="2 unidades", is_optional=0),
            RecipeIngredient(recipe=recipe2, ingredient_name="Tomate", quantity="400g triturado", is_optional=0),
            RecipeIngredient(recipe=recipe2, ingredient_name="Caldo de pollo", quantity="1.2 litros", is_optional=0),
            RecipeIngredient(recipe=recipe2, ingredient_name="Ajo", quantity="3 dientes", is_optional=0),
            RecipeIngredient(recipe=recipe2, ingredient_name="Cebolla", quantity="1 unidad", is_optional=0),
        ]

        nutrition2 = NutritionalInfo(
            recipe=recipe2,
            calories=485,
            proteins=32.0,
            carbs=68.0,
            fats=10.5,
            fiber=3.2,
            sodium=580
        )

        # Receta 3: Pasta Carbonara
        recipe3 = Recipe(
            name="Pasta Carbonara",
            description="Pasta cremosa con panceta, huevo y queso parmesano",
            instructions="""1. Pon agua con sal a hervir para la pasta
2. Corta la panceta en dados pequeños
3. Fríe la panceta sin aceite hasta que esté crujiente
4. Bate los huevos con el queso parmesano rallado
5. Añade pimienta negra recién molida
6. Cuece la pasta según las instrucciones del paquete
7. Reserva 1 taza del agua de cocción
8. Escurre la pasta y mézclala con la panceta
9. Retira del fuego y añade la mezcla de huevo
10. Remueve rápidamente, añadiendo agua de cocción si está seca
11. Sirve inmediatamente con más queso y pimienta""",
            cooking_time=20,
            difficulty="Fácil",
            servings=4
        )

        ingredients3 = [
            RecipeIngredient(recipe=recipe3, ingredient_name="Pasta", quantity="400g (espaguetis o fettuccine)", is_optional=0),
            RecipeIngredient(recipe=recipe3, ingredient_name="Panceta", quantity="200g", is_optional=0),
            RecipeIngredient(recipe=recipe3, ingredient_name="Huevos", quantity="4 unidades", is_optional=0),
            RecipeIngredient(recipe=recipe3, ingredient_name="Queso parmesano", quantity="100g rallado", is_optional=0),
            RecipeIngredient(recipe=recipe3, ingredient_name="Pimienta negra", quantity="al gusto", is_optional=0),
            RecipeIngredient(recipe=recipe3, ingredient_name="Sal", quantity="para el agua", is_optional=0),
        ]

        nutrition3 = NutritionalInfo(
            recipe=recipe3,
            calories=620,
            proteins=28.0,
            carbs=72.0,
            fats=24.0,
            fiber=3.0,
            sodium=720
        )

        # Receta 4: Ensalada César
        recipe4 = Recipe(
            name="Ensalada César",
            description="Ensalada fresca con pollo, lechuga romana y salsa césar",
            instructions="""1. Corta el pollo en tiras y sazónalo
2. Cocina el pollo a la plancha hasta que esté dorado
3. Lava y corta la lechuga romana
4. Prepara la salsa: mezcla mayonesa, mostaza, ajo, limón y anchoas
5. Corta el pan en cubos y tuesta en el horno
6. Mezcla la lechuga con la salsa
7. Añade el pollo en tiras
8. Incorpora los croutones y queso parmesano
9. Sirve inmediatamente""",
            cooking_time=25,
            difficulty="Fácil",
            servings=2
        )

        ingredients4 = [
            RecipeIngredient(recipe=recipe4, ingredient_name="Pechuga de pollo", quantity="300g", is_optional=0),
            RecipeIngredient(recipe=recipe4, ingredient_name="Lechuga romana", quantity="1 unidad", is_optional=0),
            RecipeIngredient(recipe=recipe4, ingredient_name="Pan", quantity="100g (para croutones)", is_optional=0),
            RecipeIngredient(recipe=recipe4, ingredient_name="Queso parmesano", quantity="50g", is_optional=0),
            RecipeIngredient(recipe=recipe4, ingredient_name="Mayonesa", quantity="100ml", is_optional=0),
            RecipeIngredient(recipe=recipe4, ingredient_name="Limón", quantity="1 unidad", is_optional=0),
            RecipeIngredient(recipe=recipe4, ingredient_name="Ajo", quantity="1 diente", is_optional=0),
            RecipeIngredient(recipe=recipe4, ingredient_name="Anchoas", quantity="4 filetes", is_optional=1),
        ]

        nutrition4 = NutritionalInfo(
            recipe=recipe4,
            calories=445,
            proteins=38.0,
            carbs=22.0,
            fats=24.0,
            fiber=3.5,
            sodium=890
        )

        # Receta 5: Gazpacho Andaluz
        recipe5 = Recipe(
            name="Gazpacho Andaluz",
            description="Sopa fría de tomate, refrescante y saludable",
            instructions="""1. Lava todos los vegetales
2. Corta los tomates en cuartos
3. Pela el pepino y córtalo en trozos
4. Corta el pimiento en trozos
5. Pela el ajo
6. Mezcla todos los ingredientes en una batidora
7. Añade pan del día anterior remojado en agua
8. Agrega aceite de oliva, vinagre y sal
9. Tritura hasta obtener textura fina
10. Refrigera al menos 2 horas
11. Sirve frío con tropezones de pepino, tomate y pan""",
            cooking_time=15,
            difficulty="Fácil",
            servings=4
        )

        ingredients5 = [
            RecipeIngredient(recipe=recipe5, ingredient_name="Tomates maduros", quantity="1kg", is_optional=0),
            RecipeIngredient(recipe=recipe5, ingredient_name="Pepino", quantity="1 unidad", is_optional=0),
            RecipeIngredient(recipe=recipe5, ingredient_name="Pimiento verde", quantity="1 unidad", is_optional=0),
            RecipeIngredient(recipe=recipe5, ingredient_name="Pan", quantity="100g", is_optional=0),
            RecipeIngredient(recipe=recipe5, ingredient_name="Ajo", quantity="1 diente", is_optional=0),
            RecipeIngredient(recipe=recipe5, ingredient_name="Aceite de oliva", quantity="100ml", is_optional=0),
            RecipeIngredient(recipe=recipe5, ingredient_name="Vinagre", quantity="2 cucharadas", is_optional=0),
            RecipeIngredient(recipe=recipe5, ingredient_name="Sal", quantity="al gusto", is_optional=0),
        ]

        nutrition5 = NutritionalInfo(
            recipe=recipe5,
            calories=180,
            proteins=3.5,
            carbs=18.0,
            fats=11.0,
            fiber=4.2,
            sodium=420
        )

        # Añadir todas las recetas a la sesión
        session.add_all([recipe1, recipe2, recipe3, recipe4, recipe5])
        session.add_all(ingredients1 + ingredients2 + ingredients3 + ingredients4 + ingredients5)
        session.add_all([nutrition1, nutrition2, nutrition3, nutrition4, nutrition5])

        await session.commit()

        print("✅ Se han añadido 5 recetas de ejemplo a la base de datos")

if __name__ == "__main__":
    asyncio.run(seed_recipes())
