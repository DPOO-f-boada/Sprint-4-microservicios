from typing import Optional, Tuple
from math import radians, cos, sin, asin, sqrt
from django.db import transaction
from django.conf import settings
from django.utils import timezone
import requests
from .models import Order

def haversine_km(lon1, lat1, lon2, lat2) -> float:
    """Retorna la distancia en km entre dos puntos geográficos"""
    R = 6371.0
    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

def find_nearest_warehouse_with_stock(product_name: str, units: int, user_lat: float, user_lon: float) -> Optional[dict]:
    """Encuentra la bodega más cercana con stock suficiente"""
    try:
        inventory_url = f"{settings.INVENTORY_SERVICE_URL}/api/inventory/{product_name}/"
        response = requests.get(inventory_url, timeout=5)
        
        if response.status_code != 200:
            return None
        
        inventories = response.json()
        available_inventories = [
            inv for inv in inventories 
            if inv.get('available_quantity', 0) >= units
        ]
        
        if not available_inventories:
            return None
        
        warehouses_url = f"{settings.INVENTORY_SERVICE_URL}/api/warehouses/"
        warehouses_response = requests.get(warehouses_url, timeout=5)
        
        if warehouses_response.status_code != 200:
            return None
        
        warehouses = {w['id']: w for w in warehouses_response.json()}
        nearest = None
        min_distance = float('inf')
        
        for inv in available_inventories:
            warehouse_id = inv['warehouse']
            warehouse = warehouses.get(warehouse_id)
            if warehouse:
                distance = haversine_km(
                    user_lon, user_lat,
                    warehouse['longitude'], warehouse['latitude']
                )
                if distance < min_distance:
                    min_distance = distance
                    nearest = {
                        'warehouse_id': warehouse_id,
                        'warehouse_name': warehouse['name'],
                        'inventory_id': inv['id'],
                        'distance': distance
                    }
        
        return nearest
    except requests.RequestException:
        return None

def place_order_atomic(
    product_name: str, 
    units: int, 
    user_lat: float, 
    user_lon: float, 
    customer_id: Optional[int] = None,
    main_warehouse_name: Optional[str] = None,
    max_retries: int = 3
) -> Tuple[Order, bool]:
    """Realiza un pedido de manera atómica"""
    
    if units <= 0:
        raise ValueError("units must be > 0")
    
    try:
        products_url = f"{settings.PRODUCTS_SERVICE_URL}/api/products/name/{product_name}/"
        product_response = requests.get(products_url, timeout=5)
        
        if product_response.status_code != 200:
            raise ValueError(f"Producto {product_name} no encontrado")
        
        product_data = product_response.json()
        product_id = product_data['id']
        unit_price = float(product_data['unit_price'])
        total_price = unit_price * units
    except requests.RequestException:
        raise ValueError("Error al comunicarse con el servicio de productos")
    
    order = Order.objects.create(
        product_id=product_id,
        product_name=product_name,
        units=units,
        customer_id=customer_id,
        total_price=total_price,
        status=Order.PENDING
    )
    
    for attempt in range(1, max_retries + 1):
        try:
            if main_warehouse_name:
                try:
                    warehouses_url = f"{settings.INVENTORY_SERVICE_URL}/api/warehouses/"
                    warehouses_response = requests.get(warehouses_url, timeout=5)
                    warehouses = {w['name']: w for w in warehouses_response.json()}
                    
                    if main_warehouse_name in warehouses:
                        warehouse_id = warehouses[main_warehouse_name]['id']
                        inventory_url = f"{settings.INVENTORY_SERVICE_URL}/api/inventory/{product_name}/"
                        inv_response = requests.get(inventory_url, timeout=5)
                        
                        if inv_response.status_code == 200:
                            inventories = inv_response.json()
                            for inv in inventories:
                                if inv['warehouse'] == warehouse_id and inv['available_quantity'] >= units:
                                    restock_url = f"{settings.INVENTORY_SERVICE_URL}/api/inventory/{product_name}/restock/"
                                    restock_response = requests.post(restock_url, json={
                                        'units': -units,
                                        'warehouse': main_warehouse_name
                                    }, timeout=5)
                                    
                                    if restock_response.status_code == 200:
                                        order.status = Order.CONFIRMED
                                        order.warehouse_id = warehouse_id
                                        order.warehouse_name = main_warehouse_name
                                        order.confirmed_at = timezone.now()
                                        order.save()
                                        return order, True
                except requests.RequestException:
                    pass
            
            nearest = find_nearest_warehouse_with_stock(product_name, units, user_lat, user_lon)
            
            if nearest:
                restock_url = f"{settings.INVENTORY_SERVICE_URL}/api/inventory/{product_name}/restock/"
                restock_response = requests.post(restock_url, json={
                    'units': -units,
                    'warehouse': nearest['warehouse_name']
                }, timeout=5)
                
                if restock_response.status_code == 200:
                    order.status = Order.CONFIRMED
                    order.warehouse_id = nearest['warehouse_id']
                    order.warehouse_name = nearest['warehouse_name']
                    order.confirmed_at = timezone.now()
                    order.save()
                    return order, True
            
            order.status = Order.REJECTED
            order.save()
            return order, False
            
        except Exception as e:
            if attempt >= max_retries:
                raise
            continue
    
    order.status = Order.REJECTED
    order.save()
    return order, False

