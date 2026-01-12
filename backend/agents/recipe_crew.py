"""
Sistema de agentes con CrewAI para scraping y procesamiento de recetas
"""
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar LLM de Groq
llm = ChatGroq(
    temperature=0.7,
    model_name="llama-3.1-70b-versatile",  # Puedes usar también: llama-3.1-8b-instant
    api_key=os.getenv("GROQ_API_KEY")
)

# Tools
scrape_tool = ScrapeWebsiteTool()


class RecipeCrew:
    """Crew de agentes para buscar y procesar recetas"""

    def __init__(self):
        self.llm = llm

    def create_agents(self):
        """Crea los agentes del crew"""

        # Agente 1: Web Scraper
        scraper_agent = Agent(
            role='Buscador de Recetas',
            goal='Encontrar recetas de cocina de calidad en sitios web especializados en gastronomía española e internacional',
            backstory="""Eres un experto buscador de recetas con años de experiencia
            navegando sitios de cocina. Conoces las mejores fuentes de recetas
            auténticas y sabes identificar recetas bien estructuradas con información
            nutricional completa. Te enfocas en recetas con instrucciones claras,
            tiempos precisos y listas de ingredientes detalladas.""",
            tools=[scrape_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

        # Agente 2: Procesador de Datos
        processor_agent = Agent(
            role='Procesador de Recetas',
            goal='Extraer y estructurar información de recetas en formato JSON válido con todos los campos requeridos',
            backstory="""Eres un experto en procesamiento de datos culinarios.
            Tu especialidad es extraer información nutricional, estimar precios
            basándote en ingredientes, evaluar niveles de dificultad y recomendar
            utensilios de cocina apropiados. Tienes un ojo clínico para identificar
            alternativas de utensilios (ej: wok vs sartén) y eres preciso en tus
            estimaciones de calorías, proteínas, carbohidratos y grasas.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

        # Agente 3: Validador de Calidad
        validator_agent = Agent(
            role='Validador de Recetas',
            goal='Verificar que las recetas procesadas cumplan con todos los estándares de calidad y completitud',
            backstory="""Eres un chef profesional y nutricionista que revisa recetas
            para asegurar su calidad. Verificas que la información nutricional sea
            realista, que los ingredientes estén bien proporcionados, que las
            instrucciones sean claras y que no falte ningún campo importante.
            También validas que los precios estimados sean razonables y que las
            recomendaciones de utensilios sean apropiadas.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

        return scraper_agent, processor_agent, validator_agent

    def create_tasks(self, agents, urls_to_scrape):
        """Crea las tareas para los agentes"""
        scraper_agent, processor_agent, validator_agent = agents

        # Task 1: Scraping
        scrape_task = Task(
            description=f"""Busca y extrae información de recetas desde las siguientes URLs:
            {', '.join(urls_to_scrape)}

            Para cada receta, extrae:
            - Nombre de la receta
            - Descripción breve
            - Lista completa de ingredientes con cantidades
            - Instrucciones paso a paso
            - Tiempo de preparación y cocción
            - Número de porciones
            - Información nutricional si está disponible
            - Nivel de dificultad si está especificado

            Devuelve un texto estructurado con toda la información encontrada.""",
            agent=scraper_agent,
            expected_output="Texto estructurado con información completa de múltiples recetas extraídas de los sitios web"
        )

        # Task 2: Procesamiento a JSON
        process_task = Task(
            description="""Procesa las recetas extraídas y conviértelas en formato JSON siguiendo esta estructura EXACTA:

{
  "recipes": [
    {
      "name": "Nombre de la receta",
      "description": "Descripción breve y atractiva",
      "instructions": "Instrucciones paso a paso numeradas",
      "cooking_time": 30,  // Tiempo total en minutos (número entero)
      "difficulty": "Fácil",  // Opciones: "Fácil", "Media", "Difícil"
      "servings": 4,  // Número de porciones (número entero)
      "ingredients": [
        {
          "name": "Nombre del ingrediente",
          "quantity": "Cantidad con unidad (ej: 200g, 2 unidades)",
          "is_optional": false  // true si es opcional
        }
      ],
      "nutrition": {
        "calories": 450.0,  // Kcal por porción (número decimal)
        "proteins": 25.5,   // Gramos de proteína
        "carbs": 45.0,      // Gramos de carbohidratos
        "fats": 18.0,       // Gramos de grasa
        "fiber": 3.5,       // Gramos de fibra (opcional)
        "sodium": 580.0     // Miligramos de sodio (opcional)
      },
      "estimated_price": 12.50,  // Precio estimado en euros
      "equipment": [
        {
          "primary": "Wok",
          "alternatives": ["Sartén grande", "Sartén honda"]
        },
        {
          "primary": "Cuchillo de chef",
          "alternatives": ["Cuchillo de cocina"]
        }
      ]
    }
  ]
}

IMPORTANTE:
- Si no hay información nutricional exacta, ESTÍMALA basándote en los ingredientes
- El precio debe ser estimado según el costo aproximado de ingredientes en España
- La dificultad debe evaluarse según técnicas requeridas y tiempo
- Los utensilios deben incluir alternativas prácticas
- RETORNA ÚNICAMENTE EL JSON VÁLIDO, sin texto adicional""",
            agent=processor_agent,
            expected_output="JSON válido con array de recetas completamente estructuradas",
            context=[scrape_task]
        )

        # Task 3: Validación
        validate_task = Task(
            description="""Valida el JSON de recetas generado y verifica:

1. ✅ Estructura JSON válida
2. ✅ Todos los campos requeridos presentes
3. ✅ Valores numéricos en rangos realistas:
   - cooking_time: 5-300 minutos
   - servings: 1-12 porciones
   - calories: 50-1500 kcal por porción
   - proteins: 0-100g
   - carbs: 0-150g
   - fats: 0-100g
   - estimated_price: 0.50-50 euros
4. ✅ Difficulty es "Fácil", "Media" o "Difícil"
5. ✅ Ingredientes tienen nombre y cantidad
6. ✅ Equipment tiene primary y alternatives
7. ✅ Instructions son claras y numeradas

Si encuentras errores, CORRÍGELOS y devuelve el JSON corregido.
Si todo está correcto, devuelve el JSON validado.

RETORNA ÚNICAMENTE EL JSON FINAL VALIDADO.""",
            agent=validator_agent,
            expected_output="JSON final validado y corregido listo para importar a base de datos",
            context=[process_task]
        )

        return [scrape_task, process_task, validate_task]

    def run(self, urls_to_scrape):
        """Ejecuta el crew completo"""
        agents = self.create_agents()
        tasks = self.create_tasks(agents, urls_to_scrape)

        crew = Crew(
            agents=list(agents),
            tasks=tasks,
            process=Process.sequential,
            verbose=2
        )

        result = crew.kickoff()
        return result


# Función helper para ejecutar con URLs específicas
def scrape_recipes(urls):
    """
    Ejecuta el crew de scraping con las URLs proporcionadas

    Args:
        urls: Lista de URLs de recetas a scrapear

    Returns:
        JSON con las recetas procesadas
    """
    crew = RecipeCrew()
    result = crew.run(urls)
    return result
