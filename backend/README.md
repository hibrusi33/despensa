# Backend Despensa - API con RAG y Llama 3.1

Backend Python con FastAPI, sistema RAG usando LangChain + ChromaDB, y modelo Llama 3.1 8B para el chatbot inteligente.

## Características

- ✅ API REST con FastAPI
- ✅ Sistema RAG (Retrieval Augmented Generation)
- ✅ Llama 3.1 8B vía Ollama
- ✅ Base de datos SQLite con SQLAlchemy
- ✅ Embeddings en español
- ✅ ChromaDB para búsqueda vectorial
- ✅ Sugerencias de recetas basadas en inventario
- ✅ Información nutricional

## Requisitos previos

### 1. Instalar Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Windows
# Descargar desde https://ollama.com/download
```

### 2. Descargar Llama 3.1 8B

```bash
ollama pull llama3.1:8b
```

Verifica que funcione:
```bash
ollama run llama3.1:8b "Hola, ¿cómo estás?"
```

### 3. Python 3.10+

Asegúrate de tener Python 3.10 o superior instalado.

## Instalación

### 1. Crear entorno virtual

```bash
cd backend
python -m venv venv

# Activar en Linux/Mac
source venv/bin/activate

# Activar en Windows
venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- FastAPI y Uvicorn
- SQLAlchemy (base de datos)
- LangChain (RAG system)
- ChromaDB (vectorstore)
- sentence-transformers (embeddings español)
- ollama (cliente Python)

### 3. Configurar variables de entorno (opcional)

```bash
cp .env.example .env
# Edita .env si necesitas cambiar configuraciones
```

### 4. Poblar base de datos con recetas

```bash
python seed_data.py
```

Esto creará la base de datos y añadirá 5 recetas de ejemplo:
- Tortilla Española
- Arroz con Pollo
- Pasta Carbonara
- Ensalada César
- Gazpacho Andaluz

## Ejecutar el servidor

```bash
# Desarrollo (con recarga automática)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# O directamente con Python
python main.py
```

El servidor estará disponible en:
- API: http://localhost:8000
- Documentación: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## Endpoints principales

### Inventario

```bash
# Obtener todos los items
GET /api/inventory

# Añadir item
POST /api/inventory
{
  "name": "Tomates",
  "qty": 5,
  "expiry": "2025-02-15",
  "category": "Verduras"
}

# Actualizar item
PUT /api/inventory/{item_id}

# Eliminar item
DELETE /api/inventory/{item_id}
```

### Recetas

```bash
# Obtener todas las recetas
GET /api/recipes

# Recetas sugeridas según inventario
GET /api/recipes/suggested
```

### Chat con IA

```bash
POST /api/chat
{
  "message": "¿Qué puedo cocinar con lo que tengo?",
  "conversation_history": [
    {"role": "user", "content": "Hola"},
    {"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte?"}
  ]
}
```

### Administración

```bash
# Re-indexar recetas en vectorstore
POST /api/admin/reindex
```

## Arquitectura del sistema RAG

```
Usuario → Frontend (React)
              ↓
         FastAPI (main.py)
              ↓
         RAG System (rag_system.py)
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
ChromaDB            SQLAlchemy
(Vectores)         (Base datos)
    ↓                   ↓
Embeddings         Recetas +
(español)          Inventario
    ↓                   ↓
    └─────────┬─────────┘
              ↓
         Llama 3.1 8B
         (vía Ollama)
              ↓
         Respuesta
```

## Cómo funciona el RAG

1. **Indexación**: Las recetas se convierten en embeddings y se guardan en ChromaDB
2. **Query del usuario**: "¿Qué puedo cocinar?"
3. **Recuperación**: Se buscan recetas similares en ChromaDB
4. **Contexto**: Se añade inventario actual + recetas encontradas
5. **Generación**: Llama 3.1 genera respuesta contextualizada
6. **Respuesta**: Se devuelve al usuario con recetas sugeridas

## Añadir más recetas

### Opción 1: Directamente en seed_data.py

Edita `seed_data.py` y añade más recetas siguiendo el formato existente.

### Opción 2: Via API (próximamente)

```python
POST /api/recipes
{
  "name": "Mi Receta",
  "description": "...",
  "instructions": "...",
  ...
}
```

Después ejecuta:
```bash
POST /api/admin/reindex
```

## Troubleshooting

### Error: "No se puede conectar con Ollama"

```bash
# Verifica que Ollama esté corriendo
ollama list

# Inicia el servicio
ollama serve
```

### Error: CUDA out of memory

Si tu GPU no tiene suficiente memoria:

```python
# En rag_system.py, línea 19, cambia:
model_kwargs={'device': 'cuda'}
# Por:
model_kwargs={'device': 'cpu'}
```

### Las recetas no aparecen

```bash
# Re-poblar base de datos
python seed_data.py

# Re-indexar vectorstore
curl -X POST http://localhost:8000/api/admin/reindex
```

## Estructura del proyecto

```
backend/
├── main.py                  # FastAPI app principal
├── seed_data.py            # Script para poblar DB
├── requirements.txt        # Dependencias Python
├── .env.example           # Variables de entorno
├── despensa.db            # Base de datos SQLite (generada)
├── chroma_db/             # Vectorstore ChromaDB (generada)
└── app/
    ├── __init__.py
    ├── models.py          # Modelos SQLAlchemy
    ├── database.py        # Configuración DB
    └── rag_system.py      # Sistema RAG + LLM
```

## Próximos pasos

- [ ] Autenticación de usuarios
- [ ] Soporte multi-usuario
- [ ] API endpoint para añadir recetas
- [ ] Análisis de imágenes de tickets (OCR)
- [ ] Notificaciones de caducidad
- [ ] Exportar lista de compras

## Licencia

MIT
