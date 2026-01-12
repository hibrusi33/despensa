"""
Script para buscar recetas por términos de búsqueda (sin URLs específicas)
Usa Google/Bing para encontrar recetas automáticamente
"""
import json
import os
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# Configurar LLM
llm = ChatGroq(
    temperature=0.7,
    model_name="llama-3.1-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# Tools (requiere SERPER_API_KEY de https://serper.dev)
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()


def search_and_scrape_recipes(query, num_recipes=5):
    """
    Busca recetas por término de búsqueda y las procesa

    Args:
        query: Término de búsqueda (ej: "recetas veganas fáciles")
        num_recipes: Número de recetas a obtener

    Returns:
        JSON con las recetas procesadas
    """

    # Agente Buscador
    searcher = Agent(
        role='Buscador de Recetas en Internet',
        goal=f'Encontrar {num_recipes} URLs de recetas de calidad relacionadas con: {query}',
        backstory="""Eres un experto en encontrar las mejores recetas en internet.
        Sabes identificar sitios web confiables con recetas bien estructuradas.
        Prefieres sitios con información nutricional completa.""",
        tools=[search_tool],
        llm=llm,
        verbose=True
    )

    # Agente Scraper
    scraper = Agent(
        role='Extractor de Recetas',
        goal='Extraer información completa de las recetas encontradas',
        backstory="""Eres experto en extraer datos estructurados de sitios web de cocina.
        Puedes identificar ingredientes, instrucciones, tiempos y valores nutricionales.""",
        tools=[scrape_tool],
        llm=llm,
        verbose=True
    )

    # Agente Procesador
    processor = Agent(
        role='Procesador de Datos Culinarios',
        goal='Convertir recetas extraídas en JSON estructurado con estimaciones precisas',
        backstory="""Eres chef y nutricionista. Estimas valores nutricionales, precios
        y dificultad de recetas con precisión. Conoces utensilios de cocina y sus alternativas.""",
        llm=llm,
        verbose=True
    )

    # Tasks
    search_task = Task(
        description=f"""Busca en internet {num_recipes} recetas sobre: "{query}"

        Criterios de búsqueda:
        - Sitios web en español
        - Recetas con instrucciones detalladas
        - Preferiblemente con información nutricional
        - De sitios confiables (recetasderechupete.com, directoalpaladar.com, etc.)

        Devuelve una lista de URLs de las mejores recetas encontradas.""",
        agent=searcher,
        expected_output=f"Lista de {num_recipes} URLs de recetas de calidad"
    )

    scrape_task = Task(
        description="""Extrae la información completa de cada URL encontrada:
        - Nombre de la receta
        - Descripción
        - Ingredientes con cantidades
        - Instrucciones paso a paso
        - Tiempo de cocción
        - Porciones
        - Información nutricional (si está disponible)
        - Nivel de dificultad (si está especificado)

        Devuelve toda la información en texto estructurado.""",
        agent=scraper,
        expected_output="Información completa de todas las recetas extraídas",
        context=[search_task]
    )

    process_task = Task(
        description="""Convierte las recetas en formato JSON siguiendo esta estructura:

{
  "recipes": [
    {
      "name": "Nombre de la receta",
      "description": "Descripción atractiva",
      "instructions": "Pasos numerados",
      "cooking_time": 30,
      "difficulty": "Fácil",
      "servings": 4,
      "ingredients": [
        {"name": "Ingrediente", "quantity": "200g", "is_optional": false}
      ],
      "nutrition": {
        "calories": 400.0,
        "proteins": 25.0,
        "carbs": 45.0,
        "fats": 15.0,
        "fiber": 3.0,
        "sodium": 500.0
      },
      "estimated_price": 10.50,
      "equipment": [
        {"primary": "Sartén", "alternatives": ["Wok", "Cazuela"]}
      ]
    }
  ]
}

ESTIMA los valores nutricionales y precios basándote en los ingredientes.
RETORNA SOLO EL JSON VÁLIDO.""",
        agent=processor,
        expected_output="JSON válido con todas las recetas estructuradas",
        context=[scrape_task]
    )

    # Crear y ejecutar crew
    crew = Crew(
        agents=[searcher, scraper, processor],
        tasks=[search_task, scrape_task, process_task],
        process=Process.sequential,
        verbose=2
    )

    result = crew.kickoff()
    return result


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Buscar y scrapear recetas por término de búsqueda')
    parser.add_argument('query', help='Término de búsqueda (ej: "recetas veganas")')
    parser.add_argument('-n', '--num', type=int, default=5, help='Número de recetas a buscar (default: 5)')
    args = parser.parse_args()

    # Verificar API keys
    if not os.getenv("GROQ_API_KEY"):
        print("❌ ERROR: GROQ_API_KEY no configurada")
        print("Añádela en .env: https://console.groq.com/")
        return

    if not os.getenv("SERPER_API_KEY"):
        print("❌ ERROR: SERPER_API_KEY no configurada")
        print("Obtén una gratis en: https://serper.dev/")
        print("\nAlternativa: Usa run_scraper.py con URLs específicas")
        return

    print(f"🔍 Buscando recetas sobre: '{args.query}'")
    print(f"📊 Número de recetas: {args.num}")
    print("-" * 60)

    try:
        result = search_and_scrape_recipes(args.query, args.num)

        # Guardar resultado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recipes_{args.query.replace(' ', '_')}_{timestamp}.json"

        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", filename)

        # Extraer JSON de la respuesta
        if isinstance(result, str):
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start != -1:
                json_str = result[json_start:json_end]
                data = json.loads(json_str)
            else:
                print("⚠️ No se encontró JSON válido")
                return
        else:
            data = result

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Recetas guardadas en: {filepath}")
        print(f"\n💡 Usa load_to_db.py para cargarlas a la base de datos:")
        print(f"   python load_to_db.py {filepath}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
