import json
import time
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .logic import place_order_atomic
from .serializers import OrderSerializer
from .models import Order

@api_view(['GET'])
def order_list(request):
    """Listar todos los pedidos"""
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def order_detail(request, order_id):
    """Obtener detalles de un pedido"""
    try:
        order = Order.objects.get(id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({'error': 'Pedido no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@csrf_exempt
def place_order(request, product_name: str):
    """Crear un pedido para un producto específico"""
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
        units = int(payload.get("units", 0))
        user_lat = float(payload["lat"])
        user_lon = float(payload["lon"])
        main_warehouse_name = payload.get("mainWarehouse")
        customer_id = payload.get("customer_id")
    except (KeyError, ValueError, json.JSONDecodeError):
        return HttpResponseBadRequest('Payload: {"units":int,"lat":float,"lon":float,"mainWarehouse"?:str,"customer_id"?:int}')
    
    try:
        order, confirmed = place_order_atomic(
            product_name=product_name,
            units=units,
            user_lat=user_lat,
            user_lon=user_lon,
            customer_id=customer_id,
            main_warehouse_name=main_warehouse_name
        )
        
        serializer = OrderSerializer(order)
        return JsonResponse({"order": serializer.data, "confirmed": confirmed}, 
                          status=200 if confirmed else 409)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

@api_view(['POST'])
@csrf_exempt
def create_order_view(request):
    """Crear una orden automática verificando disponibilidad en todas las bodegas"""
    start_time = time.time()
    
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
        product_name = payload["product"]
        units = int(payload["units"])
        user_lat = float(payload["lat"])
        user_lon = float(payload["lon"])
        main_warehouse_name = payload.get("mainWarehouse")
        customer_id = payload.get("customer_id")
    except (KeyError, ValueError, json.JSONDecodeError):
        return HttpResponseBadRequest(
            'Payload inválido. Ejemplo: {"product": "Monitor LED 24\"", "units": 5, "lat": 4.6, "lon": -74.08, "mainWarehouse": "Bodega Sur"}'
        )
    
    try:
        order, confirmed = place_order_atomic(
            product_name=product_name,
            units=units,
            user_lat=user_lat,
            user_lon=user_lon,
            customer_id=customer_id,
            main_warehouse_name=main_warehouse_name
        )
        
        elapsed = round(time.time() - start_time, 3)
        
        return JsonResponse({
            "order_id": order.id,
            "product": order.product_name,
            "units": order.units,
            "status": order.status,
            "assigned_warehouse": order.warehouse_name,
            "confirmed": confirmed,
            "execution_time_seconds": elapsed,
            "meets_performance_ASR": elapsed <= 5.0
        }, status=200 if confirmed else 409)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

