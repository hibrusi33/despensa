"""
Script principal para ejecutar el scraping de recetas
"""
import json
import os
from datetime import datetime
from recipe_crew import scrape_recipes

# URLs de ejemplo (sitios populares de recetas en español)
RECIPE_URLS = [
    # Recetas españolas
    "https://www.recetasderechupete.com/tortilla-de-patatas/12851/",
    "https://www.recetasderechupete.com/paella-valenciana/17815/",
    "https://www.recetasderechupete.com/gazpacho-andaluz/19679/",

    # Recetas internacionales adaptadas
    "https://www.recetasderechupete.com/pasta-carbonara/20126/",
    "https://www.recetasderechupete.com/arroz-tres-delicias/12744/",

    # Más opciones (puedes añadir tus favoritas)
    # "https://www.directoalpaladar.com/...",
    # "https://www.hogarmania.com/cocina/recetas/...",
]


def save_to_file(data, filename=None):
    """Guarda el resultado en un archivo JSON"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recipes_{timestamp}.json"

    # Crear directorio data si no existe
    os.makedirs("data", exist_ok=True)
    filepath = os.path.join("data", filename)

    # Si data es string, intentar parsearlo como JSON
    if isinstance(data, str):
        try:
            # Limpiar el texto para extraer solo el JSON
            json_start = data.find('{')
            json_end = data.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = data[json_start:json_end]
                data = json.loads(json_str)
            else:
                print("⚠️ No se pudo encontrar JSON válido en la respuesta")
                # Guardar como texto plano para inspección
                with open(filepath.replace('.json', '.txt'), 'w', encoding='utf-8') as f:
                    f.write(str(data))
                return filepath.replace('.json', '.txt')
        except json.JSONDecodeError as e:
            print(f"⚠️ Error al parsear JSON: {e}")
            # Guardar como texto plano
            with open(filepath.replace('.json', '.txt'), 'w', encoding='utf-8') as f:
                f.write(str(data))
            return filepath.replace('.json', '.txt')

    # Guardar JSON formateado
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Recetas guardadas en: {filepath}")
    return filepath


def main():
    """Función principal"""
    print("🤖 Iniciando sistema de agentes para scraping de recetas...")
    print(f"📄 URLs a procesar: {len(RECIPE_URLS)}")
    print("-" * 60)

    # Verificar que existe la API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ ERROR: GROQ_API_KEY no está configurada")
        print("Por favor, añade tu API key de Groq en el archivo .env")
        print("Puedes obtener una gratis en: https://console.groq.com/")
        return

    try:
        # Ejecutar scraping
        print("\n🔍 Iniciando scraping...")
        result = scrape_recipes(RECIPE_URLS)

        print("\n" + "="*60)
        print("✅ Scraping completado!")
        print("="*60)

        # Guardar resultado
        filepath = save_to_file(result)

        # Mostrar resumen
        if filepath.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'recipes' in data:
                    print(f"\n📊 Resumen:")
                    print(f"  - Recetas procesadas: {len(data['recipes'])}")
                    for i, recipe in enumerate(data['recipes'], 1):
                        print(f"  {i}. {recipe.get('name', 'Sin nombre')}")
                        print(f"     ⏱️  {recipe.get('cooking_time', 0)} min")
                        print(f"     🍽️  {recipe.get('servings', 0)} porciones")
                        print(f"     💪 {recipe.get('difficulty', 'N/A')}")
                        print(f"     💰 ~{recipe.get('estimated_price', 0)}€")

        print(f"\n📁 Archivo guardado: {filepath}")
        print("\n💡 Siguiente paso: Usa load_to_db.py para cargar las recetas a la base de datos")

    except Exception as e:
        print(f"\n❌ Error durante el scraping: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
