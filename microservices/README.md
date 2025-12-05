# Arquitectura de Microservicios - PROVESI S.A.S.

Este proyecto ha sido convertido de una arquitectura monolítica a una arquitectura de microservicios.

## Estructura de Microservicios

```
microservices/
├── auth-service/          # Microservicio de Autenticación
├── products-service/      # Microservicio de Productos
├── inventory-service/     # Microservicio de Inventario
├── orders-service/        # Microservicio de Pedidos
├── shipping-service/      # Microservicio de Shipping (Guías de envío)
├── api-gateway/           # API Gateway (enrutador)
└── docker-compose.yml     # Orquestación de servicios
```

## Servicios

### 1. Auth Service (Puerto 8001)
- Gestión de usuarios y autenticación
- Roles: ADMIN, OPERARIO, CLIENTE
- Endpoints de login, logout, registro

### 2. Products Service (Puerto 8002)
- Gestión de productos y catálogo
- Variables de productos
- Proveedores

### 3. Inventory Service (Puerto 8003)
- Gestión de inventario
- Bodegas (Warehouses)
- Mediciones de stock

### 4. Orders Service (Puerto 8004)
- Gestión de pedidos
- Asignación de bodegas
- Cálculo de distancias

### 5. Shipping Service (Puerto 8005)
- Generación de guías de envío
- Integración con transportadoras
- ASR: Respuesta en máximo 8 segundos

### 6. API Gateway (Puerto 8000)
- Enrutamiento de peticiones
- Autenticación centralizada
- Balanceo de carga

## Comunicación entre Servicios

Los servicios se comunican mediante HTTP/REST:
- Orders Service → Products Service (verificar productos)
- Orders Service → Inventory Service (verificar stock)
- Orders Service → Auth Service (verificar usuarios)
- Shipping Service → Orders Service (obtener información de pedidos)
- Todos los servicios → Auth Service (validar tokens)

## Base de Datos

Cada microservicio tiene su propia base de datos:
- `auth_db`: Base de datos de autenticación
- `products_db`: Base de datos de productos
- `inventory_db`: Base de datos de inventario
- `orders_db`: Base de datos de pedidos
- `shipping_db`: Base de datos de shipping

## Ejecución

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

## Endpoints Principales

### API Gateway (http://localhost:8000)
- `POST /api/auth/login/` - Login
- `GET /api/products/` - Listar productos
- `GET /api/inventory/{product}/` - Consultar inventario
- `POST /api/orders/create/` - Crear pedido
- `POST /api/shipping/guides/generate/` - Generar guía de envío

