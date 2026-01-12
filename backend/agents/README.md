# 🤖 Sistema de Agentes para Scraping de Recetas

Sistema automatizado usando **CrewAI** + **Groq** (Llama 3.1) para buscar, extraer y procesar recetas de internet, llenando automáticamente la base de datos con información nutricional completa.

## ✨ Características

- 🔍 **Web Scraping inteligente** con agentes especializados
- 🤖 **3 Agentes CrewAI**:
  - **Buscador**: Encuentra recetas de calidad en sitios web
  - **Procesador**: Extrae y estructura datos en JSON
  - **Validador**: Verifica calidad y completitud
- 🦙 **Llama 3.1 70B** vía Groq (rápido y gratis)
- 📊 **Extracción completa**:
  - Información nutricional (kcal, proteínas, carbos, grasas)
  - Precio estimado
  - Tiempo de preparación
  - Nivel de dificultad
  - Utensilios necesarios y alternativas
- 💾 **Carga automática** a base de datos

## 📦 Instalación

### 1. Instalar dependencias adicionales

```bash
# Desde backend/ con venv activado
pip install -r requirements-agents.txt
```

### 2. Obtener API Keys (GRATIS)

#### Groq API Key (OBLIGATORIO)
1. Regístrate en: https://console.groq.com/
2. Crea una API key
3. Añádela al archivo `.env`:
   ```
   GROQ_API_KEY=tu_api_key_aqui
   ```

#### Serper API Key (OPCIONAL - solo para búsqueda automática)
1. Regístrate en: https://serper.dev/
2. Obtén tu API key gratuita (2,500 búsquedas/mes)
3. Añádela al `.env`:
   ```
   SERPER_API_KEY=tu_api_key_aqui
   ```

## 🚀 Uso

### Opción 1: Scraping con URLs específicas (Recomendado)

Mejor opción si ya conoces las URLs de las recetas.

```bash
cd agents

# Editar run_scraper.py y añadir tus URLs favoritas
# Por defecto incluye recetas de RecetasDeRechupete.com

python run_scraper.py
```

**Resultado**: Archivo JSON en `data/recipes_TIMESTAMP.json`

### Opción 2: Búsqueda automática por términos

Usa Google para encontrar recetas automáticamente (requiere Serper API).

```bash
cd agents

# Buscar recetas veganas
python scrape_by_query.py "recetas veganas fáciles" -n 5

# Buscar recetas mediterráneas
python scrape_by_query.py "dieta mediterránea" -n 10

# Buscar postres
python scrape_by_query.py "postres saludables" -n 8
```

## 📥 Cargar recetas a la base de datos

Una vez tengas el archivo JSON:

```bash
cd agents

# Cargar recetas
python load_to_db.py data/recipes_20250112_143022.json
```

Esto:
1. ✅ Carga las recetas a la base de datos SQLite
2. ✅ Crea ingredientes y valores nutricionales
3. ✅ Reindexá el vectorstore de ChromaDB
4. ✅ Las recetas están disponibles en la API inmediatamente

## 📋 Formato JSON generado

```json
{
  "recipes": [
    {
      "name": "Tortilla Española Clásica",
      "description": "La auténtica tortilla de patatas española",
      "instructions": "1. Pela y corta las patatas...\n2. Fríe en aceite...",
      "cooking_time": 30,
      "difficulty": "Media",
      "servings": 4,
      "ingredients": [
        {
          "name": "Patatas",
          "quantity": "4 unidades grandes",
          "is_optional": false
        },
        {
          "name": "Huevos",
          "quantity": "6 unidades",
          "is_optional": false
        }
      ],
      "nutrition": {
        "calories": 320.0,
        "proteins": 14.5,
        "carbs": 24.0,
        "fats": 19.0,
        "fiber": 2.5,
        "sodium": 380.0
      },
      "estimated_price": 3.50,
      "equipment": [
        {
          "primary": "Sartén antiadherente",
          "alternatives": ["Sartén normal", "Sartén de hierro"]
        },
        {
          "primary": "Plato grande",
          "alternatives": ["Tapa de sartén"]
        }
      ]
    }
  ]
}
```

## 🎯 Sitios web recomendados para scraping

Sitios españoles con buena estructura:
- ✅ **RecetasDeRechupete.com** - Excelente formato
- ✅ **DirectoAlPaladar.com** - Info nutricional
- ✅ **Hogarmania.com** - Recetas clásicas
- ✅ **CocinaFacil.com** - Recetas sencillas
- ✅ **CocinadeLeo.com** - Recetas caseras

## 🔧 Personalización

### Modificar agentes

Edita `recipe_crew.py` para ajustar:
- Temperatura del LLM (creatividad)
- Modelo de Groq (llama-3.1-8b-instant para más velocidad)
- Instrucciones de los agentes
- Campos del JSON

### Añadir más campos

Para añadir campos extra al JSON (ej: tipo de cocina, alérgenos):

1. Modifica el schema en `recipe_crew.py` → `process_task`
2. Actualiza los modelos en `../app/models.py`
3. Crea migración de base de datos si es necesario

## 🐛 Troubleshooting

### Error: "GROQ_API_KEY not found"
```bash
# Verifica que .env existe y tiene la key
cat ../.env | grep GROQ

# Si no existe, créala
echo "GROQ_API_KEY=tu_key_aqui" >> ../.env
```

### Error: "SERPER_API_KEY not found"
**Opción 1**: Obtén la key en https://serper.dev/ (gratis)
**Opción 2**: Usa `run_scraper.py` con URLs directas (no requiere Serper)

### JSON inválido generado
Los agentes a veces añaden texto extra. El script `run_scraper.py` automáticamente extrae solo el JSON válido del output.

Si falla:
1. Revisa el archivo `.txt` generado
2. Extrae manualmente el JSON entre `{` y `}`
3. Valida con: `python -m json.tool archivo.json`

### Recetas incompletas
Algunos sitios web tienen estructuras complejas. Recomendaciones:
- Usa sitios conocidos (lista arriba)
- Verifica que el sitio tenga datos estructurados
- Aumenta la temperatura del LLM para mejor extracción

## 📊 Ejemplos de uso

### Llenar base de datos con 20 recetas españolas

```bash
# 1. Editar run_scraper.py y añadir 20 URLs
# 2. Ejecutar
python run_scraper.py

# 3. Cargar a DB
python load_to_db.py data/recipes_20250112_143022.json
```

### Crear dataset de recetas veganas

```bash
python scrape_by_query.py "recetas veganas completas" -n 15
python load_to_db.py data/recipes_recetas_veganas_completas_20250112_150000.json
```

### Recetas por categoría

```bash
# Desayunos
python scrape_by_query.py "desayunos saludables" -n 10

# Postres
python scrape_by_query.py "postres sin azúcar" -n 10

# Platos principales
python scrape_by_query.py "recetas mediterráneas" -n 15
```

## 🚀 Próximas mejoras

- [ ] Scraping de imágenes de recetas
- [ ] Detección de alérgenos automática
- [ ] Clasificación por tipo de cocina
- [ ] Extracción de reviews/ratings
- [ ] Conversión automática de unidades
- [ ] Validación de precios con APIs de supermercados

## 📄 Licencia

MIT

---

**Hecho con ❤️ usando CrewAI, Groq y Llama 3.1**
