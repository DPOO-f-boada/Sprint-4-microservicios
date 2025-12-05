# Arquitectura de Microservicios - PROVESI S.A.S.

## Visión General

Este proyecto ha sido migrado de una arquitectura monolítica Django a una arquitectura de microservicios. Cada servicio es independiente y se comunica con los demás mediante HTTP/REST.

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (Flask)                     │
│                         Puerto: 8000                          │
└──────────────┬──────────────┬──────────────┬─────────────────┘
               │              │              │
       ┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐ ┌───────▼──────┐
       │ Auth Service │ │ Products   │ │ Inventory  │ │ Orders      │
       │   (Django)   │ │ Service    │ │ Service    │ │ Service     │
       │   Puerto:    │ │ (Django)   │ │ (Django)   │ │ (Django)   │
       │    8001      │ │ Puerto:    │ │ Puerto:    │ │ Puerto:    │
       └──────┬───────┘ │   8002      │ │   8003      │ │   8004      │
              │         └─────┬───────┘ └─────┬───────┘ └──────┬──────┘
              │                │                │                │
       ┌──────▼──────┐ ┌───────▼──────┐ ┌───────▼──────┐ ┌───────▼──────┐
       │   db-auth   │ │ db-products  │ │ db-inventory │ │  db-orders  │
       │ (PostgreSQL)│ │ (PostgreSQL) │ │ (PostgreSQL)│ │ (PostgreSQL)│
       └─────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## Microservicios

### 1. Auth Service (Puerto 8001)

**Responsabilidad**: Gestión de usuarios y autenticación

**Base de Datos**: `auth_db` (PostgreSQL)

**Modelos**:
- `User`: Usuarios con roles (ADMIN, OPERARIO, CLIENTE)

**Endpoints**:
- `POST /api/auth/login/` - Autenticación
- `POST /api/auth/logout/` - Cerrar sesión
- `GET /api/auth/profile/` - Perfil del usuario
- `GET /api/auth/verify/` - Verificar token
- `GET /api/users/<id>/` - Detalles de usuario

**Dependencias**: Ninguna

### 2. Products Service (Puerto 8002)

**Responsabilidad**: Gestión de productos, proveedores y variables

**Base de Datos**: `products_db` (PostgreSQL)

**Modelos**:
- `Product`: Productos del catálogo
- `Supplier`: Proveedores
- `Variable`: Variables de productos

**Endpoints**:
- `GET /api/products/` - Listar productos
- `GET /api/products/<id>/` - Detalles de producto
- `GET /api/products/name/<nombre>/` - Producto por nombre
- `GET /api/suppliers/` - Listar proveedores
- `GET /api/variables/` - Listar variables

**Dependencias**: Ninguna

### 3. Inventory Service (Puerto 8003)

**Responsabilidad**: Gestión de inventario, bodegas y mediciones

**Base de Datos**: `inventory_db` (PostgreSQL)

**Modelos**:
- `Warehouse`: Bodegas
- `Inventory`: Inventario de productos en bodegas
- `Measurement`: Mediciones de variables

**Endpoints**:
- `GET /api/warehouses/` - Listar bodegas
- `GET /api/warehouses/<id>/` - Detalles de bodega
- `GET /api/inventory/<product_name>/` - Inventario de producto
- `POST /api/inventory/<product_name>/restock/` - Reabastecer
- `GET /api/measurements/` - Listar mediciones

**Dependencias**:
- Products Service (para verificar productos)

### 4. Orders Service (Puerto 8004)

**Responsabilidad**: Gestión de pedidos y asignación de bodegas

**Base de Datos**: `orders_db` (PostgreSQL)

**Modelos**:
- `Order`: Pedidos de productos

**Endpoints**:
- `GET /api/orders/` - Listar pedidos
- `GET /api/orders/<id>/` - Detalles de pedido
- `POST /api/orders/<product_name>/` - Crear pedido
- `POST /api/orders/create/` - Crear orden automática

**Dependencias**:
- Auth Service (para verificar usuarios)
- Products Service (para obtener información de productos)
- Inventory Service (para verificar stock y asignar bodegas)

### 5. API Gateway (Puerto 8000)

**Responsabilidad**: Enrutamiento de peticiones y punto de entrada único

**Tecnología**: Flask

**Funcionalidades**:
- Enrutamiento de peticiones a los microservicios correspondientes
- Punto de entrada único para todos los clientes
- Health checks

**Endpoints**: Todos los endpoints de los microservicios, prefijados con `/api/`

## Comunicación entre Servicios

Los servicios se comunican mediante HTTP/REST:

1. **Orders Service → Products Service**
   - Verificar existencia de productos
   - Obtener información de productos (precio, etc.)

2. **Orders Service → Inventory Service**
   - Verificar disponibilidad de stock
   - Asignar bodegas
   - Actualizar inventario al confirmar pedidos

3. **Orders Service → Auth Service**
   - Verificar usuarios
   - Obtener información de clientes

4. **Inventory Service → Products Service**
   - Verificar existencia de productos al reabastecer

## Patrones de Diseño Utilizados

### 1. Database per Service
Cada microservicio tiene su propia base de datos, garantizando independencia y escalabilidad.

### 2. API Gateway
Punto de entrada único que enruta las peticiones a los microservicios correspondientes.

### 3. Service Discovery
Los servicios se descubren mediante nombres de servicio en Docker Compose.

### 4. Eventual Consistency
Los servicios mantienen caché de datos de otros servicios (ej: `product_name` en Order).

## Ventajas de esta Arquitectura

1. **Escalabilidad**: Cada servicio puede escalarse independientemente
2. **Independencia**: Cada servicio puede desarrollarse y desplegarse por separado
3. **Tecnología**: Cada servicio puede usar diferentes tecnologías (aunque actualmente todos usan Django)
4. **Aislamiento de fallos**: Si un servicio falla, los demás continúan funcionando
5. **Equipos**: Diferentes equipos pueden trabajar en diferentes servicios

## Desafíos y Consideraciones

1. **Transacciones distribuidas**: Las operaciones que requieren múltiples servicios no son atómicas
2. **Consistencia de datos**: Se usa eventual consistency con caché
3. **Complejidad de red**: Mayor latencia debido a las llamadas HTTP entre servicios
4. **Manejo de errores**: Necesidad de manejar fallos en la comunicación entre servicios

## Mejoras Futuras

1. **Message Queue**: Implementar RabbitMQ o Kafka para comunicación asíncrona
2. **Service Mesh**: Implementar Istio para gestión de tráfico y seguridad
3. **Circuit Breaker**: Implementar patrón Circuit Breaker para manejo de fallos
4. **Distributed Tracing**: Implementar Jaeger o Zipkin para seguimiento de peticiones
5. **API Versioning**: Implementar versionado de APIs
6. **Rate Limiting**: Implementar límites de tasa en el API Gateway
7. **Caching**: Implementar Redis para caché compartido

