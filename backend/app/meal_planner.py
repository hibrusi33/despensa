"""
Generador de planes de comidas mensuales (Premium Feature)
Usa Groq Llama 3.1 70B para mejor calidad
"""
import os
from typing import List, Dict
from groq import Groq
from .models import Recipe, MealPlan, InventoryItem, User
import json
import calendar
from datetime import datetime


class MealPlanGenerator:
    """Generador de planes de comidas usando IA"""

    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-70b-versatile"  # Modelo premium

    async def generate_monthly_plan(
        self,
        user: User,
        month: int,
        year: int,
        target_calories: int = 2000,
        dietary_preferences: List[str] = None,
        allergies: List[str] = None,
        meals_per_day: int = 3
    ) -> MealPlan:
        """
        Genera un plan de comidas mensual completo

        Args:
            user: Usuario
            month: Mes (1-12)
            year: Año
            target_calories: Calorías objetivo diarias
            dietary_preferences: ["vegetarian", "vegan", "low-carb", "mediterranean"]
            allergies: Lista de alérgenos
            meals_per_day: Número de comidas por día (2-5)

        Returns:
            MealPlan object
        """
        dietary_preferences = dietary_preferences or []
        allergies = allergies or []

        # Obtener recetas disponibles
        recipes = await self._get_available_recipes(user, dietary_preferences, allergies)

        if len(recipes) < meals_per_day * 7:  # Al menos una semana
            raise Exception("No hay suficientes recetas disponibles para el plan")

        # Obtener inventario del usuario
        inventory = await InventoryItem.find(
            InventoryItem.user_id == str(user.id)
        ).to_list()

        # Generar plan con IA
        weekly_plans = await self._generate_weekly_plans(
            recipes=recipes,
            inventory=inventory,
            target_calories=target_calories,
            dietary_preferences=dietary_preferences,
            meals_per_day=meals_per_day,
            num_weeks=self._get_weeks_in_month(year, month)
        )

        # Generar lista de compras
        shopping_list = await self._generate_shopping_list(
            weekly_plans, inventory
        )

        # Crear meal plan
        meal_plan = MealPlan(
            user_id=str(user.id),
            month=month,
            year=year,
            name=f"Plan {calendar.month_name[month]} {year}",
            description=f"Plan personalizado con {target_calories} kcal/día",
            target_calories=target_calories,
            dietary_preferences=dietary_preferences,
            allergies=allergies,
            meals_per_day=meals_per_day,
            weekly_plans=weekly_plans,
            shopping_list=shopping_list,
            generated_by_ai=True
        )

        await meal_plan.insert()
        return meal_plan

    async def _get_available_recipes(
        self,
        user: User,
        dietary_preferences: List[str],
        allergies: List[str]
    ) -> List[Recipe]:
        """Obtiene recetas disponibles según preferencias y alergias"""

        # Query base
        query = {}

        # Si no es premium, excluir recetas premium
        if user.subscription_tier == "free":
            query["is_premium"] = False

        # Filtrar por preferencias dietéticas si existen
        if dietary_preferences:
            query["dietary_tags"] = {"$in": dietary_preferences}

        # Obtener recetas
        recipes = await Recipe.find(query).to_list()

        # Filtrar por alergias (buscar en ingredientes)
        if allergies:
            filtered_recipes = []
            for recipe in recipes:
                has_allergen = False
                for ingredient in recipe.ingredients:
                    ing_name = ingredient.get("name", "").lower()
                    if any(allergen.lower() in ing_name for allergen in allergies):
                        has_allergen = True
                        break
                if not has_allergen:
                    filtered_recipes.append(recipe)
            recipes = filtered_recipes

        return recipes

    async def _generate_weekly_plans(
        self,
        recipes: List[Recipe],
        inventory: List[InventoryItem],
        target_calories: int,
        dietary_preferences: List[str],
        meals_per_day: int,
        num_weeks: int
    ) -> List[Dict]:
        """Genera planes semanales usando IA"""

        # Preparar contexto para la IA
        recipes_context = self._format_recipes_for_ai(recipes)
        inventory_context = self._format_inventory_for_ai(inventory)

        prompt = f"""Eres un nutricionista experto. Genera un plan de comidas balanceado y variado.

RECETAS DISPONIBLES:
{recipes_context}

INVENTARIO ACTUAL:
{inventory_context}

REQUISITOS:
- Objetivo calórico: {target_calories} kcal/día
- Comidas por día: {meals_per_day}
- Número de semanas: {num_weeks}
- Preferencias: {', '.join(dietary_preferences) if dietary_preferences else 'Ninguna'}
- Priorizar uso de ingredientes del inventario
- Variedad: No repetir la misma receta más de 2 veces por semana
- Balance nutricional: Incluir proteínas, carbohidratos y vegetales

FORMATO DE SALIDA (JSON):
{{
  "weeks": [
    {{
      "week": 1,
      "days": [
        {{
          "day": "Lunes",
          "meals": {{
            "breakfast": {{"recipe_id": "...", "recipe_name": "...", "calories": 400}},
            "lunch": {{"recipe_id": "...", "recipe_name": "...", "calories": 700}},
            "dinner": {{"recipe_id": "...", "recipe_name": "...", "calories": 600}}
          }},
          "total_calories": 1700
        }}
      ]
    }}
  ]
}}

IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional."""

        # Llamar a Groq con Llama 3.1 70B
        response = self.groq_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Eres un nutricionista experto que genera planes de comidas en formato JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )

        # Parsear respuesta
        content = response.choices[0].message.content

        # Extraer JSON
        try:
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            json_str = content[json_start:json_end]
            result = json.loads(json_str)
            return result.get("weeks", [])
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            # Fallback: generar plan simple sin IA
            return self._generate_simple_plan(recipes, meals_per_day, num_weeks)

    def _format_recipes_for_ai(self, recipes: List[Recipe]) -> str:
        """Formatea recetas para el prompt de IA"""
        lines = []
        for i, recipe in enumerate(recipes[:50], 1):  # Limitar a 50 para no exceder tokens
            nutr = recipe.nutrition or {}
            lines.append(
                f"{i}. {recipe.name} (ID: {recipe.id})\n"
                f"   - Tiempo: {recipe.cooking_time}min, Dificultad: {recipe.difficulty}\n"
                f"   - Calorías: {nutr.get('calories', 'N/A')} kcal\n"
                f"   - Ingredientes: {', '.join([ing.get('name', '') for ing in recipe.ingredients[:5]])}"
            )
        return "\n".join(lines)

    def _format_inventory_for_ai(self, inventory: List[InventoryItem]) -> str:
        """Formatea inventario para el prompt de IA"""
        if not inventory:
            return "Inventario vacío"

        lines = []
        for item in inventory[:20]:  # Primeros 20 items
            lines.append(f"- {item.name}: {item.qty} unidades")
        return "\n".join(lines)

    def _generate_simple_plan(
        self,
        recipes: List[Recipe],
        meals_per_day: int,
        num_weeks: int
    ) -> List[Dict]:
        """Genera plan simple sin IA (fallback)"""
        weeks = []
        recipe_index = 0
        days_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        for week_num in range(1, num_weeks + 1):
            week = {"week": week_num, "days": []}

            for day_name in days_names:
                meals = {}
                meal_names = ["breakfast", "lunch", "dinner", "snack"][:meals_per_day]

                for meal_name in meal_names:
                    recipe = recipes[recipe_index % len(recipes)]
                    nutr = recipe.nutrition or {}
                    meals[meal_name] = {
                        "recipe_id": str(recipe.id),
                        "recipe_name": recipe.name,
                        "calories": nutr.get("calories", 0)
                    }
                    recipe_index += 1

                week["days"].append({
                    "day": day_name,
                    "meals": meals,
                    "total_calories": sum(m.get("calories", 0) for m in meals.values())
                })

            weeks.append(week)

        return weeks

    async def _generate_shopping_list(
        self,
        weekly_plans: List[Dict],
        inventory: List[InventoryItem]
    ) -> List[Dict]:
        """Genera lista de compras basada en el plan"""
        needed_ingredients = {}

        # Recopilar todos los ingredientes necesarios
        for week in weekly_plans:
            for day in week.get("days", []):
                for meal_name, meal_data in day.get("meals", {}).items():
                    recipe_id = meal_data.get("recipe_id")
                    if recipe_id:
                        recipe = await Recipe.get(recipe_id)
                        if recipe:
                            for ingredient in recipe.ingredients:
                                name = ingredient.get("name")
                                quantity = ingredient.get("quantity")
                                if name:
                                    if name not in needed_ingredients:
                                        needed_ingredients[name] = []
                                    needed_ingredients[name].append(quantity)

        # Comparar con inventario
        inventory_dict = {item.name.lower(): item.qty for item in inventory}

        shopping_list = []
        for ingredient, quantities in needed_ingredients.items():
            current_stock = inventory_dict.get(ingredient.lower(), 0)
            # Simplificado: asumir que necesitamos comprar si no está en inventario
            if current_stock == 0:
                shopping_list.append({
                    "name": ingredient,
                    "quantities_needed": quantities,
                    "estimated_amount": len(quantities),  # Número de veces que se usa
                    "in_stock": False
                })

        return shopping_list

    def _get_weeks_in_month(self, year: int, month: int) -> int:
        """Calcula número de semanas en un mes"""
        num_days = calendar.monthrange(year, month)[1]
        return (num_days + 6) // 7  # Redondear hacia arriba


# Instancia global
meal_planner = MealPlanGenerator()
