# Microservicio de Shipping - Generación de Guías de Envío

## ASR Implementado

**Generación de guías de envío**: Cuando el operario solicite la generación de una guía con una transportadora, el sistema debe obtener la respuesta en un tiempo máximo de 8 segundos, garantizando la continuidad del proceso de despacho sin bloqueos.

## Descripción

El microservicio de Shipping gestiona la generación de guías de envío con diferentes transportadoras. Implementa un sistema de timeout de 8 segundos para garantizar que el proceso de despacho no se bloquee.

## Características

- ✅ **Timeout de 8 segundos**: Garantiza respuesta en máximo 8 segundos
- ✅ **No bloqueante**: El proceso de despacho continúa sin interrupciones
- ✅ **Múltiples transportadoras**: Soporte para diferentes transportadoras
- ✅ **Monitoreo de rendimiento**: Tracking del tiempo de generación
- ✅ **Manejo de errores**: Gestión robusta de timeouts y fallos
- ✅ **Integración simulada**: Preparado para integración con APIs reales

## Modelos

### Carrier (Transportadora)
- `name`: Nombre de la transportadora
- `api_endpoint`: URL del API (opcional, para integración real)
- `api_key`: Clave de API (opcional)
- `is_active`: Estado activo/inactivo
- `response_time_avg`: Tiempo promedio de respuesta en segundos

### ShippingGuide (Guía de Envío)
- `order_id`: ID del pedido
- `carrier`: Transportadora asignada
- `guide_number`: Número de guía generado
- `status`: Estado (PENDING, GENERATED, FAILED, TIMEOUT)
- `generation_time_seconds`: Tiempo que tomó generar la guía
- `meets_performance_ASR`: Indica si cumple con el ASR de 8 segundos
- Información del envío (origen, destino, destinatario)
- Información del paquete (peso, dimensiones, valor declarado)

## Endpoints

### Transportadoras

- `GET /api/carriers/` - Listar transportadoras activas
- `GET /api/carriers/<id>/` - Detalles de una transportadora

### Guías de Envío

- `GET /api/guides/` - Listar todas las guías
- `GET /api/guides/<id>/` - Detalles de una guía
- `GET /api/guides/order/<order_id>/` - Guías de un pedido específico
- `POST /api/guides/generate/` - **Generar una guía de envío (ASR: 8 segundos)**
- `GET /api/guides/statistics/` - Estadísticas de generación

## Ejemplo de Uso

### Generar una guía de envío

```bash
curl -X POST http://localhost:8000/api/shipping/guides/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "carrier_id": 1,
    "origin_address": "Bodega Norte, Calle 100 #50-30, Bogotá",
    "destination_address": "Carrera 15 #93-47, Bogotá",
    "recipient_name": "Juan Pérez",
    "recipient_phone": "3001234567",
    "recipient_document": "1234567890",
    "weight_kg": 2.5,
    "dimensions": "30x20x15",
    "declared_value": 150000
  }'
```

### Respuesta exitosa

```json
{
  "guide": {
    "id": 1,
    "order_id": 1,
    "carrier": 1,
    "carrier_name": "Servientrega",
    "guide_number": "SER0000011234",
    "status": "GENERATED",
    "status_display": "Generada",
    "carrier_tracking_number": "TRACK1234567",
    "generation_time_seconds": 2.456,
    "meets_performance_ASR": true,
    "generated_at": "2025-05-12T12:00:00Z"
  },
  "success": true,
  "generation_time_seconds": 2.456,
  "meets_performance_ASR": true
}
```

### Respuesta con timeout

```json
{
  "guide": {
    "id": 2,
    "status": "TIMEOUT",
    "status_display": "Timeout",
    "generation_time_seconds": 8.001,
    "meets_performance_ASR": false,
    "error_message": "Timeout: La transportadora no respondió en 8 segundos"
  },
  "success": false,
  "generation_time_seconds": 8.001,
  "meets_performance_ASR": false,
  "error": "Timeout: La transportadora no respondió en 8 segundos"
}
```

## Estadísticas

Para monitorear el cumplimiento del ASR:

```bash
curl http://localhost:8000/api/shipping/guides/statistics/
```

Respuesta:
```json
{
  "total_guides": 100,
  "generated": 95,
  "failed": 3,
  "timeout": 2,
  "meets_performance_ASR": 98,
  "asr_compliance_rate": 98.0,
  "average_generation_time_seconds": 2.345
}
```

## Integración con Transportadoras

El servicio está preparado para integrarse con APIs reales de transportadoras. Para configurar una transportadora real:

1. Configurar `api_endpoint` y `api_key` en el modelo Carrier
2. El sistema automáticamente usará la API real en lugar de la simulación

### Transportadoras Simuladas

Por defecto, el servicio simula las respuestas de las transportadoras con tiempos de respuesta realistas basados en `response_time_avg`.

## Configuración

### Variables de Entorno

- `SHIPPING_GUIDE_TIMEOUT`: Timeout en segundos (default: 8)
- `ORDERS_SERVICE_URL`: URL del servicio de pedidos
- `INVENTORY_SERVICE_URL`: URL del servicio de inventario

### Crear Transportadoras de Prueba

```bash
docker-compose exec shipping-service python manage.py create_test_carriers
```

Esto crea:
- Servientrega (2.5s promedio)
- Coordinadora (3.0s promedio)
- Interrapidisimo (2.8s promedio)
- DHL (4.0s promedio)

## Garantías del ASR

1. **Timeout de 8 segundos**: El sistema garantiza respuesta en máximo 8 segundos
2. **No bloqueante**: Si hay timeout, el proceso continúa y se marca el estado
3. **Monitoreo**: Todas las generaciones se registran con su tiempo de ejecución
4. **Métricas**: Estadísticas disponibles para verificar cumplimiento del ASR

## Mejoras Futuras

- [ ] Integración real con APIs de transportadoras
- [ ] Cola de mensajes para procesamiento asíncrono
- [ ] Reintentos automáticos en caso de fallo
- [ ] Notificaciones cuando se genera una guía
- [ ] Dashboard de monitoreo en tiempo real

