import ollama
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import Recipe, RecipeIngredient, NutritionalInfo, InventoryItem
from typing import List, Dict
import os

class RAGSystem:
    def __init__(self):
        # Embeddings en español
        self.embeddings = HuggingFaceEmbeddings(
            model_name="hiiamsid/sentence_similarity_spanish_es",
            model_kwargs={'device': 'cuda'}  # Cambia a 'cpu' si no tienes GPU
        )

        # ChromaDB para almacenar vectores
        self.persist_directory = "./chroma_db"
        self.vectorstore = None

        # Modelo Ollama
        self.model_name = "llama3.1:8b"

    async def initialize_vectorstore(self, db: AsyncSession):
        """Inicializa o carga el vectorstore con las recetas"""
        if os.path.exists(self.persist_directory):
            # Cargar vectorstore existente
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print("✅ Vectorstore cargado desde disco")
        else:
            # Crear nuevo vectorstore
            await self.index_recipes(db)
            print("✅ Vectorstore creado y guardado")

    async def index_recipes(self, db: AsyncSession):
        """Indexa todas las recetas en el vectorstore"""
        # Obtener todas las recetas con sus ingredientes y nutrición
        result = await db.execute(
            select(Recipe).options(
                selectinload(Recipe.ingredients),
                selectinload(Recipe.nutrition)
            )
        )
        recipes = result.scalars().all()

        documents = []
        for recipe in recipes:
            # Crear documento con toda la información
            ingredients_text = ", ".join([
                f"{ing.quantity} de {ing.ingredient_name}"
                for ing in recipe.ingredients
            ])

            nutrition_text = ""
            if recipe.nutrition:
                n = recipe.nutrition
                nutrition_text = (
                    f"Por porción: {n.calories} kcal, "
                    f"{n.proteins}g proteínas, {n.carbs}g carbohidratos, "
                    f"{n.fats}g grasas"
                )

            content = (
                f"Receta: {recipe.name}\n"
                f"Descripción: {recipe.description}\n"
                f"Ingredientes: {ingredients_text}\n"
                f"Tiempo de cocción: {recipe.cooking_time} minutos\n"
                f"Dificultad: {recipe.difficulty}\n"
                f"Porciones: {recipe.servings}\n"
                f"Información nutricional: {nutrition_text}\n"
                f"Instrucciones: {recipe.instructions}"
            )

            documents.append(Document(
                page_content=content,
                metadata={
                    "recipe_id": recipe.id,
                    "recipe_name": recipe.name,
                    "cooking_time": recipe.cooking_time,
                    "difficulty": recipe.difficulty
                }
            ))

        # Dividir documentos si son muy largos
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        split_docs = text_splitter.split_documents(documents)

        # Crear vectorstore
        self.vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        self.vectorstore.persist()

    async def get_user_inventory(self, db: AsyncSession) -> List[Dict]:
        """Obtiene el inventario actual del usuario"""
        result = await db.execute(select(InventoryItem))
        items = result.scalars().all()
        return [
            {
                "name": item.name,
                "qty": item.qty,
                "category": item.category,
                "expiry": item.expiry
            }
            for item in items
        ]

    async def find_matching_recipes(self, db: AsyncSession, query: str = None) -> List[Dict]:
        """Encuentra recetas que coincidan con el inventario del usuario"""
        inventory = await self.get_user_inventory(db)

        if not inventory:
            return []

        # Crear query basada en ingredientes disponibles
        available_ingredients = [item["name"] for item in inventory]
        search_query = query if query else f"Recetas con {', '.join(available_ingredients[:5])}"

        # Buscar recetas similares
        results = self.vectorstore.similarity_search_with_score(
            search_query,
            k=5  # Top 5 recetas
        )

        matching_recipes = []
        for doc, score in results:
            matching_recipes.append({
                "recipe_id": doc.metadata.get("recipe_id"),
                "recipe_name": doc.metadata.get("recipe_name"),
                "content": doc.page_content,
                "similarity_score": float(score),
                "cooking_time": doc.metadata.get("cooking_time"),
                "difficulty": doc.metadata.get("difficulty")
            })

        return matching_recipes

    async def chat(self, db: AsyncSession, user_message: str, conversation_history: List[Dict] = None) -> str:
        """Procesa mensaje del usuario con contexto RAG"""
        # Obtener inventario
        inventory = await self.get_user_inventory(db)
        inventory_text = "\n".join([
            f"- {item['name']}: {item['qty']} unidades (Categoría: {item['category']})"
            for item in inventory
        ])

        # Buscar recetas relevantes
        matching_recipes = await self.find_matching_recipes(db, user_message)
        recipes_context = "\n\n".join([
            f"**{r['recipe_name']}** (Tiempo: {r['cooking_time']}min, Dificultad: {r['difficulty']})\n{r['content']}"
            for r in matching_recipes[:3]  # Top 3
        ])

        # Construir prompt con contexto
        system_prompt = f"""Eres un asistente culinario experto que ayuda a gestionar la despensa y sugerir recetas.

INVENTARIO ACTUAL DEL USUARIO:
{inventory_text if inventory else "La despensa está vacía"}

RECETAS DISPONIBLES QUE COINCIDEN:
{recipes_context if recipes_context else "No hay recetas que coincidan exactamente"}

Tu trabajo es:
1. Sugerir recetas basadas en los ingredientes disponibles
2. Informar sobre información nutricional cuando se pregunte
3. Ayudar a planificar comidas
4. Avisar sobre productos próximos a caducar
5. Dar consejos sobre cocina y conservación de alimentos

Responde en español de forma amigable y concisa."""

        # Preparar mensajes para Ollama
        messages = [{"role": "system", "content": system_prompt}]

        # Añadir historial de conversación
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Últimos 6 mensajes

        messages.append({"role": "user", "content": user_message})

        # Llamar a Ollama
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            )
            return response['message']['content']
        except Exception as e:
            return f"Error al comunicar con el modelo: {str(e)}"

    async def reindex_recipes(self, db: AsyncSession):
        """Re-indexa todas las recetas (útil después de añadir nuevas)"""
        # Borrar vectorstore existente
        if os.path.exists(self.persist_directory):
            import shutil
            shutil.rmtree(self.persist_directory)

        # Crear nuevo índice
        await self.index_recipes(db)
        print("✅ Recetas re-indexadas correctamente")

# Instancia global
rag_system = RAGSystem()
