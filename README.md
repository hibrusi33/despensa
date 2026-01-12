# 🏠 Despensa - App de Gestión de Inventario con IA

Aplicación móvil para gestionar tu despensa, escanear tickets de compra y recibir sugerencias de recetas usando Inteligencia Artificial con sistema RAG y Llama 3.1 8B.

## ✨ Características

### Frontend (React + Vite)
- 📱 Diseño móvil optimizado (390px)
- 🏠 Gestión de inventario de productos
- 📷 Escáner de tickets (simulado)
- 💬 Chatbot inteligente con IA
- 📊 Estadísticas de gastos
- 🎨 Iconos SVG profesionales
- 📱 PWA (instalable como app)

### Backend (Python + FastAPI)
- 🤖 Sistema RAG con LangChain + ChromaDB
- 🦙 Llama 3.1 8B (vía Ollama)
- 🔍 Búsqueda vectorial de recetas
- 📚 Base de datos con recetas e información nutricional
- 🎯 Sugerencias contextuales basadas en inventario
- 🌐 API REST completa

## 🚀 Setup completo

### Requisitos previos

1. **Node.js 18+** (para el frontend)
2. **Python 3.10+** (para el backend)
3. **Ollama** (para ejecutar Llama 3.1)
4. **GPU recomendada** (NVIDIA con CUDA para Llama 8B)

---

## 📦 Instalación paso a paso

### 1. Instalar Ollama y Llama 3.1

#### Linux/macOS:
```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Descargar Llama 3.1 8B
ollama pull llama3.1:8b

# Verificar que funciona
ollama run llama3.1:8b "Hola"
```

#### Windows:
1. Descargar instalador desde: https://ollama.com/download
2. Instalar Ollama
3. Abrir PowerShell y ejecutar:
```powershell
ollama pull llama3.1:8b
ollama run llama3.1:8b "Hola"
```

### 2. Configurar Backend (Python)

```bash
# Ir a carpeta backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Poblar base de datos con recetas de ejemplo
python seed_data.py
```

### 3. Configurar Frontend (React)

```bash
# Ir a carpeta frontend
cd frontend

# Instalar dependencias
npm install
```

---

## ▶️ Ejecutar la aplicación

### Opción A: Comandos rápidos desde la raíz (recomendado)

```bash
# Instalar dependencias (solo la primera vez)
npm run install:frontend
npm run install:backend

# Poblar base de datos (solo la primera vez)
npm run seed

# En terminales separadas:
npm run dev:frontend   # Terminal 1
npm run dev:backend    # Terminal 2
```

### Opción B: Manualmente

#### Terminal 1: Backend

```bash
cd backend

# Activar entorno virtual si no está activo
# Linux/Mac: source venv/bin/activate
# Windows: venv\Scripts\activate

# Iniciar servidor FastAPI
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará en: http://localhost:8000

Documentación API: http://localhost:8000/docs

#### Terminal 2: Frontend

```bash
# Ir a carpeta frontend
cd frontend

# Iniciar servidor de desarrollo
npm run dev
```

El frontend estará en: http://localhost:3000

---

## 📱 Probar en móvil

### Opción 1: Mismo WiFi

1. Inicia ambos servidores (backend y frontend)
2. Anota la IP de tu computadora:
   ```bash
   # Linux/Mac
   ifconfig | grep inet

   # Windows
   ipconfig
   ```
3. En tu móvil, abre el navegador e ingresa:
   ```
   http://TU_IP:3000
   ```

### Opción 2: Emulador en navegador

1. Abre http://localhost:3000
2. Presiona F12 (DevTools)
3. Click en el icono de móvil
4. Selecciona un dispositivo (iPhone, Android)

---

## 🏗️ Estructura del proyecto

```
despensa/
├── frontend/                   # Frontend React
│   ├── PantryApp.jsx          # Componente principal React
│   ├── main.jsx               # Entry point React
│   ├── index.html             # HTML base
│   ├── api.js                 # Cliente API
│   ├── manifest.json          # PWA manifest
│   ├── vite.config.js         # Config Vite
│   ├── package.json           # Dependencias Node
│   └── node_modules/          # (generado)
│
├── backend/                    # Backend Python
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py          # Modelos SQLAlchemy
│   │   ├── database.py        # Configuración DB
│   │   └── rag_system.py      # Sistema RAG + LLM
│   ├── main.py                # FastAPI app
│   ├── seed_data.py           # Datos iniciales
│   ├── requirements.txt       # Dependencias Python
│   ├── .env.example           # Template variables entorno
│   ├── README.md              # Docs del backend
│   └── venv/                  # (generado)
│
└── README.md                  # Este archivo
```

---

## 🔧 API Endpoints

### Inventario
```
GET    /api/inventory          # Obtener todos los items
POST   /api/inventory          # Añadir item
PUT    /api/inventory/{id}     # Actualizar item
DELETE /api/inventory/{id}     # Eliminar item
```

### Recetas
```
GET /api/recipes               # Todas las recetas
GET /api/recipes/suggested     # Recetas sugeridas según inventario
```

### Chat IA
```
POST /api/chat                 # Enviar mensaje al chatbot
GET  /api/chat/history         # Obtener historial
```

---

## 💡 Uso de la app

### 1. Gestionar Despensa (Tab Despensa 🏠)
- Ver productos actuales
- Añadir fechas de caducidad
- Eliminar productos consumidos

### 2. Escanear Tickets (Tab Escáner 📷)
- Simula escaneo de ticket de compra
- Detecta productos automáticamente
- Añade a inventario con un click

### 3. Chatbot IA (Tab Asistente 💬)
- Pregunta: "¿Qué puedo cocinar?"
- El bot analiza tu inventario
- Sugiere recetas disponibles
- Proporciona info nutricional

### 4. Ver Gastos (Tab Gastos 📊)
- Resumen mensual
- Gasto por categoría
- Gráficos visuales

---

## 🎯 Cómo funciona el Sistema RAG

```
Usuario pregunta: "¿Qué puedo cocinar?"
              ↓
    Backend recibe mensaje
              ↓
    ┌─────────────────────┐
    │ 1. Consulta inventario actual
    │ 2. Busca en ChromaDB recetas similares
    │ 3. Recupera info nutricional
    └─────────────────────┘
              ↓
    Contexto completo → Llama 3.1
              ↓
    Respuesta personalizada + recetas sugeridas
              ↓
         Usuario recibe respuesta
```

---

## 🐛 Troubleshooting

### Backend no inicia

**Error: "Ollama connection refused"**
```bash
# Verifica que Ollama esté corriendo
ollama list

# Si no funciona, inicia el servicio
ollama serve
```

**Error: "CUDA out of memory"**
```python
# En backend/app/rag_system.py línea 19:
# Cambia 'cuda' por 'cpu'
model_kwargs={'device': 'cpu'}
```

### Frontend no conecta con backend

1. Verifica que el backend esté corriendo en puerto 8000
2. Revisa CORS en `backend/main.py`
3. En producción, actualiza `allow_origins` en CORS

### Las recetas no aparecen

```bash
cd backend
python seed_data.py

# Si ya están creadas, re-indexa:
curl -X POST http://localhost:8000/api/admin/reindex
```

---

## 📚 Tecnologías utilizadas

### Frontend
- React 18
- Vite
- SVG Icons (custom)
- Fetch API

### Backend
- FastAPI
- SQLAlchemy (async)
- LangChain
- ChromaDB
- sentence-transformers
- Ollama Python client

### IA/ML
- Llama 3.1 8B (Meta)
- Embeddings en español
- Vector search

---

## 🔜 Próximas características

- [ ] Integración real de cámara para tickets
- [ ] OCR para reconocer productos
- [ ] Notificaciones push de caducidad
- [ ] Sincronización multi-dispositivo
- [ ] Lista de compras inteligente
- [ ] Más recetas (100+)
- [ ] Filtros por dieta (vegano, sin gluten, etc.)
- [ ] Integración con supermercados

---

## 📄 Licencia

MIT

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📞 Soporte

¿Problemas o preguntas? Abre un issue en GitHub.

---

**Hecho con ❤️ usando React, FastAPI y Llama 3.1**
