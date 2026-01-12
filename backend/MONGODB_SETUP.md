# MongoDB Setup Guide

El backend ahora usa **MongoDB** en lugar de SQLite para mayor escalabilidad y flexibilidad.

## 📦 Instalar MongoDB

### Windows

1. Descargar MongoDB Community Server: https://www.mongodb.com/try/download/community
2. Ejecutar el instalador
3. MongoDB se ejecutará como servicio automáticamente

O usar Docker:
```powershell
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Linux/Mac

```bash
# Ubuntu/Debian
sudo apt-get install -y mongodb

# macOS
brew tap mongodb/brew
brew install mongodb-community

# Iniciar servicio
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # Mac
```

O usar Docker:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## ⚙️ Configuración

### 1. Crear archivo `.env`

```bash
cd backend
cp .env.example .env
```

### 2. Editar `.env`

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=despensa

# Ollama
OLLAMA_MODEL=llama3.1:8b
OLLAMA_HOST=http://localhost:11434

# Groq (para agentes)
GROQ_API_KEY=tu_api_key_aqui

# App
DEBUG=True
```

### 3. Verificar conexión

```bash
# Ver bases de datos
mongosh
> show dbs
> use despensa
> show collections
```

## 🚀 Uso

### Poblar base de datos

```bash
cd backend
python seed_data.py
```

Esto crea la base de datos `despensa` y añade 3 recetas de ejemplo.

### Ejecutar API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Cargar recetas desde JSON (agentes)

```bash
cd agents
python load_to_db.py data/recipes_20250112_143022.json
```

## 📊 Ventajas de MongoDB

1. **Sin migraciones**: Esquema flexible
2. **Documentos embebidos**: Ingredientes y nutrición en el mismo documento
3. **Escalable**: Fácil de escalar horizontalmente
4. **JSON nativo**: Perfecto para datos de agentes
5. **Búsquedas potentes**: Queries complejas sin JOINs

## 🔍 Consultas útiles

```bash
# Conectar a MongoDB
mongosh

# Usar base de datos
use despensa

# Ver todas las recetas
db.recipes.find().pretty()

# Buscar por dificultad
db.recipes.find({difficulty: "Fácil"})

# Contar recetas
db.recipes.count()

# Eliminar todas las recetas
db.recipes.deleteMany({})

# Ver inventario
db.inventory_items.find().pretty()
```

## 🛠️ Troubleshooting

### MongoDB no inicia

```bash
# Verificar estado
sudo systemctl status mongod

# Ver logs
sudo journalctl -u mongod -f

# Reiniciar
sudo systemctl restart mongod
```

### Error de conexión

```bash
# Verificar que MongoDB esté escuchando
netstat -an | grep 27017

# O con ss
ss -tunlp | grep 27017
```

### No se pueden crear índices

Los índices se crean automáticamente con Beanie al iniciar la app. Si hay problemas:

```python
# En Python
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import Recipe, InventoryItem, ChatMessage

client = AsyncIOMotorClient("mongodb://localhost:27017")
await init_beanie(
    database=client["despensa"],
    document_models=[Recipe, InventoryItem, ChatMessage]
)
```

## 📚 Recursos

- MongoDB Docs: https://www.mongodb.com/docs/
- Motor (async driver): https://motor.readthedocs.io/
- Beanie ODM: https://beanie-odm.dev/
- Mongo Express (GUI): `docker run -p 8081:8081 mongo-express`
