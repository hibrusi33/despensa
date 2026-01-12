# Sistema de Suscripción Premium

Se ha implementado un sistema completo de suscripción premium con 3 niveles de servicio.

## 📊 Niveles de Suscripción

### 🆓 FREE (Gratis)
- Gestión básica de inventario
- Chat con IA usando Llama 3.1 8B local (Ollama)
- Búsqueda de recetas básica
- Historial de conversaciones
- Escaneo y almacenamiento de tickets

### ⭐ PREMIUM
- Todo lo de FREE +
- Generador de planes de comidas mensuales con IA
- Llama 3.1 70B via Groq (modelo más potente)
- Recetas premium exclusivas
- Listas de compras automáticas
- Recomendaciones personalizadas avanzadas
- Soporte prioritario

### 💎 PREMIUM PLUS
- Todo lo de PREMIUM +
- IA aún más avanzada
- Análisis nutricional detallado
- Consultas ilimitadas
- Acceso anticipado a nuevas funciones

## 🔑 Características Implementadas

### 1. Autenticación JWT
- Registro de usuarios con datos demográficos
- Login con email y contraseña
- Tokens JWT seguros con bcrypt
- Endpoint `/api/auth/me` para obtener datos del usuario actual

**Archivos:**
- `backend/app/auth.py` - Sistema de autenticación completo
- `backend/app/models.py` - Modelo User con campos de suscripción

### 2. Generador de Planes de Comidas (Premium)
- Genera planes mensuales completos con IA
- Considera preferencias dietéticas y alergias
- Optimiza uso de inventario actual
- Crea listas de compras automáticas
- Balance nutricional con objetivos calóricos

**Archivos:**
- `backend/app/meal_planner.py` - Generador de planes con Groq Llama 3.1 70B

### 3. Gestión de Suscripciones con Stripe
- Upgrade a Premium/Premium Plus
- Cancelación de suscripción
- Webhook para eventos de pago
- Manejo de fallos de pago

### 4. Control de Acceso
- Middleware de autenticación con `@Depends(get_current_user)`
- Decorador `@require_premium` para funciones premium
- Validación de nivel de suscripción en endpoints

### 5. Multi-usuario
- Todos los datos están asociados a usuarios
- Inventario, mensajes de chat, planes de comida por usuario
- Privacidad y aislamiento de datos

## 🚀 Endpoints Añadidos

### Autenticación
```
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

### Planes de Comida (Premium)
```
POST /api/meal-plans/generate
GET  /api/meal-plans
GET  /api/meal-plans/{plan_id}
```

### Suscripciones
```
POST /api/subscriptions/upgrade
POST /api/subscriptions/cancel
GET  /api/subscriptions/status
```

### Tickets
```
POST /api/tickets
```

### Webhook Stripe
```
POST /api/webhooks/stripe
```

## 📝 Configuración Requerida

### 1. Variables de Entorno

Copia `.env.example` a `.env` y configura:

```bash
# JWT
JWT_SECRET_KEY=genera-una-clave-segura-aqui
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 días

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PREMIUM_PRICE_ID=price_...
STRIPE_PREMIUM_PLUS_PRICE_ID=price_...

# Groq (Premium AI)
GROQ_API_KEY=tu_api_key
```

### 2. Instalación de Dependencias

```bash
cd backend
pip install -r requirements.txt
```

Nuevas dependencias añadidas:
- `passlib[bcrypt]` - Hash de contraseñas
- `python-jose[cryptography]` - JWT tokens
- `stripe` - Pagos
- `groq` - IA premium

### 3. Configurar Stripe

1. Crear cuenta en [Stripe](https://stripe.com)
2. Obtener API keys (Dashboard > Developers > API keys)
3. Crear productos y precios:
   - Premium: ~9.99€/mes
   - Premium Plus: ~19.99€/mes
4. Configurar webhook:
   - URL: `https://tu-dominio.com/api/webhooks/stripe`
   - Eventos: `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`

### 4. Obtener API Key de Groq

1. Crear cuenta en [Groq](https://groq.com)
2. Obtener API key del dashboard
3. Añadir a `.env`

## 💻 Ejemplo de Uso

### Registro de Usuario
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "password": "password123",
    "name": "Juan Pérez",
    "age": 30,
    "gender": "M",
    "household_size": 2,
    "accepts_data_analysis": true
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "password": "password123"
  }'
```

Respuesta:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "usuario@ejemplo.com",
    "name": "Juan Pérez",
    "subscription_tier": "free"
  }
}
```

### Usar el Token

Añade el header en todas las peticiones:
```
Authorization: Bearer eyJhbGc...
```

### Generar Plan de Comidas (Premium)
```bash
curl -X POST http://localhost:8000/api/meal-plans/generate \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "month": 2,
    "year": 2026,
    "target_calories": 2000,
    "dietary_preferences": ["vegetarian"],
    "allergies": ["nueces"],
    "meals_per_day": 3
  }'
```

## 📊 Modelos de Datos

### User
```python
{
  "email": "usuario@ejemplo.com",
  "password_hash": "...",
  "name": "Juan Pérez",
  "age": 30,
  "gender": "M",
  "household_size": 2,
  "subscription_tier": "premium",  # free, premium, premium_plus
  "subscription_status": "active",  # active, cancelled, past_due, trial, expired
  "stripe_customer_id": "cus_...",
  "stripe_subscription_id": "sub_...",
  "accepts_data_analysis": true,
  "accepts_anonymized_sale": false
}
```

### MealPlan
```python
{
  "user_id": "...",
  "month": 2,
  "year": 2026,
  "name": "Plan Febrero 2026",
  "target_calories": 2000,
  "dietary_preferences": ["vegetarian"],
  "allergies": ["nueces"],
  "meals_per_day": 3,
  "weekly_plans": [
    {
      "week": 1,
      "days": [
        {
          "day": "Lunes",
          "meals": {
            "breakfast": {
              "recipe_id": "...",
              "recipe_name": "Tostadas con aguacate",
              "calories": 400
            },
            "lunch": {...},
            "dinner": {...}
          },
          "total_calories": 2000
        }
      ]
    }
  ],
  "shopping_list": [
    {
      "name": "Aguacate",
      "quantities_needed": ["2 unidades", "1 unidad"],
      "estimated_amount": 3,
      "in_stock": false
    }
  ]
}
```

### UsageStats
```python
{
  "user_id": "...",
  "chat_messages": 45,
  "meal_plans_generated": 2,
  "ai_calls": 67,
  "period_start": "2026-01-01T00:00:00",
  "period_end": "2026-02-01T00:00:00"
}
```

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt (costo 12)
- ✅ JWT con expiración de 7 días
- ✅ Validación de propiedad de recursos (user_id)
- ✅ Webhook de Stripe con verificación de firma
- ✅ GDPR: Campos de consentimiento para análisis de datos

## 📈 Métricas y Límites

### Rate Limits (Futuro)
Se puede implementar rate limiting basado en UsageStats:

**FREE:**
- 50 mensajes de chat/mes
- No meal plans

**PREMIUM:**
- 500 mensajes de chat/mes
- 4 meal plans/mes

**PREMIUM PLUS:**
- Ilimitado

## 🔄 Flujo de Pago

1. Usuario hace click en "Upgrade to Premium"
2. Frontend llama a `/api/subscriptions/upgrade` con payment_method_id de Stripe
3. Backend crea/actualiza customer en Stripe
4. Backend crea subscription en Stripe
5. Stripe envía webhook a `/api/webhooks/stripe`
6. Backend actualiza estado de suscripción
7. Usuario obtiene acceso a features premium

## 🐛 Troubleshooting

### Error: "Premium subscription required"
- Verificar que el usuario tenga `subscription_tier` = "premium" o "premium_plus"
- Verificar que `subscription_status` = "active"

### Error: Stripe webhook signature invalid
- Verificar que `STRIPE_WEBHOOK_SECRET` esté correctamente configurado
- En desarrollo, usar Stripe CLI: `stripe listen --forward-to localhost:8000/api/webhooks/stripe`

### Error: JWT token expired
- Token expira después de 7 días
- Usuario debe hacer login de nuevo

## 📚 Próximos Pasos

### Frontend
1. Crear componentes de login/registro
2. Añadir UI de upgrade de suscripción con Stripe Elements
3. Mostrar planes de comida generados
4. Añadir badges "Premium" en recetas exclusivas

### Backend
1. Implementar rate limiting real
2. Añadir analytics de uso
3. Sistema de notificaciones por email
4. ETL a ClickHouse para análisis de datos
5. Tests unitarios y de integración

## 📞 Soporte

Para problemas o preguntas:
1. Revisar logs del servidor
2. Verificar configuración de .env
3. Consultar documentación de Stripe/Groq
4. Revisar modelos en `backend/app/models.py`
