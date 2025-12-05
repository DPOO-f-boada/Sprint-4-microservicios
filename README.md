# PROVESI S.A.S. - Sistema de Gestión Logística

## Arquitectura de Microservicios

Este proyecto implementa una arquitectura de microservicios para la gestión logística de PROVESI S.A.S.

## Estructura del Proyecto

```
.
└── microservices/          # Arquitectura de microservicios
    ├── auth-service/       # Microservicio de Autenticación
    ├── products-service/   # Microservicio de Productos
    ├── inventory-service/  # Microservicio de Inventario
    ├── orders-service/     # Microservicio de Pedidos
    ├── shipping-service/   # Microservicio de Shipping (Guías de envío)
    ├── api-gateway/        # API Gateway (punto de entrada)
    └── docker-compose.yml  # Orquestación de servicios
```

## Inicio Rápido

### Requisitos

- Docker y Docker Compose instalados
- Python 3.11+ (para desarrollo local)

### Levantar los servicios

```bash
cd microservices
docker-compose up -d
```

Esto levantará:
- 5 bases de datos PostgreSQL (una por servicio)
- 5 microservicios Django
- 1 API Gateway (Flask)

### Verificar que los servicios están funcionando

```bash
# Health check del API Gateway
curl http://localhost:8000/health/

# Listar productos
curl http://localhost:8000/api/products/
```

## Documentación

- [Guía de Inicio Rápido](microservices/GUIA_INICIO_RAPIDO.md) - Instrucciones detalladas para comenzar
- [Arquitectura](microservices/ARQUITECTURA.md) - Documentación técnica de la arquitectura
- [Shipping Service](microservices/SHIPPING_SERVICE.md) - Documentación del servicio de guías de envío
- [README de Microservicios](microservices/README.md) - Descripción general de los microservicios

## Puertos de los Servicios

- **API Gateway**: http://localhost:8000
- **Auth Service**: http://localhost:8001
- **Products Service**: http://localhost:8002
- **Inventory Service**: http://localhost:8003
- **Orders Service**: http://localhost:8004
- **Shipping Service**: http://localhost:8005
- **Shipping Service**: http://localhost:8005

## Endpoints Principales

Todos los endpoints están disponibles a través del API Gateway en `http://localhost:8000`:

### Autenticación
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/profile/` - Perfil del usuario

### Productos
- `GET /api/products/` - Listar productos
- `GET /api/products/name/<nombre>/` - Producto por nombre

### Inventario
- `GET /api/warehouses/` - Listar bodegas
- `GET /api/inventory/<product_name>/` - Inventario de producto
- `POST /api/inventory/<product_name>/restock/` - Reabastecer

### Pedidos
- `GET /api/orders/` - Listar pedidos
- `POST /api/orders/create/` - Crear pedido

### Shipping (Guías de Envío)
- `GET /api/carriers/` - Listar transportadoras
- `POST /api/shipping/guides/generate/` - Generar guía de envío (ASR: 8 segundos)
- `GET /api/shipping/guides/` - Listar guías de envío
- `GET /api/shipping/guides/statistics/` - Estadísticas de generación

## Desarrollo

Para más información sobre desarrollo, despliegue y arquitectura, consulta la documentación en la carpeta `microservices/`.

