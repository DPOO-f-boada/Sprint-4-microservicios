from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.db.models import F
from django.conf import settings
import requests
from .models import Warehouse, Inventory, Measurement
from .serializers import WarehouseSerializer, InventorySerializer, MeasurementSerializer

@api_view(['GET'])
def warehouse_list(request):
    """Listar todas las bodegas"""
    warehouses = Warehouse.objects.filter(is_active=True)
    serializer = WarehouseSerializer(warehouses, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def warehouse_detail(request, warehouse_id):
    """Obtener detalles de una bodega"""
    try:
        warehouse = Warehouse.objects.get(id=warehouse_id)
        serializer = WarehouseSerializer(warehouse)
        return Response(serializer.data)
    except Warehouse.DoesNotExist:
        return Response({'error': 'Bodega no encontrada'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def inventory_by_product(request, product_name):
    """Obtener inventario de un producto por nombre"""
    try:
        products_url = f"{settings.PRODUCTS_SERVICE_URL}/api/products/name/{product_name}/"
        product_response = requests.get(products_url, timeout=5)
        
        if product_response.status_code != 200:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        product_data = product_response.json()
        product_id = product_data['id']
        
        inventories = Inventory.objects.filter(product_id=product_id)
        serializer = InventorySerializer(inventories, many=True)
        return Response(serializer.data)
    except requests.RequestException:
        return Response({'error': 'Error al comunicarse con el servicio de productos'}, 
                       status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['POST'])
def inventory_restock(request, product_name):
    """Reabastecer inventario de un producto (units puede ser negativo para restar)"""
    try:
        units = int(request.data.get('units', 0))
        warehouse_name = request.data.get('warehouse')
        
        if units == 0:
            return Response({'error': 'La cantidad no puede ser cero'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        products_url = f"{settings.PRODUCTS_SERVICE_URL}/api/products/name/{product_name}/"
        product_response = requests.get(products_url, timeout=5)
        
        if product_response.status_code != 200:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        product_data = product_response.json()
        product_id = product_data['id']
        product_name_cache = product_data['name']
        
        warehouse, _ = Warehouse.objects.get_or_create(
            name=warehouse_name,
            defaults={'latitude': 0.0, 'longitude': 0.0}
        )
        
        with transaction.atomic():
            inventory, created = Inventory.objects.select_for_update().get_or_create(
                product_id=product_id,
                warehouse=warehouse,
                defaults={'product_name': product_name_cache, 'quantity': 0}
            )
            
            if units < 0 and inventory.quantity + units < 0:
                return Response(
                    {'error': f'Stock insuficiente. Disponible: {inventory.quantity}, Solicitado: {abs(units)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            Inventory.objects.filter(pk=inventory.pk).update(
                quantity=F('quantity') + units
            )
            inventory.refresh_from_db()
        
        serializer = InventorySerializer(inventory)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except (ValueError, KeyError) as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except requests.RequestException:
        return Response({'error': 'Error al comunicarse con el servicio de productos'}, 
                       status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['GET'])
def measurement_list(request):
    """Listar todas las mediciones"""
    measurements = Measurement.objects.all()
    serializer = MeasurementSerializer(measurements, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def measurement_create(request):
    """Crear una nueva medición"""
    serializer = MeasurementSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

