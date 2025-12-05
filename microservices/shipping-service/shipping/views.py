from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Carrier, ShippingGuide
from .serializers import CarrierSerializer, ShippingGuideSerializer, ShippingGuideCreateSerializer
from .carrier_integration import generate_shipping_guide

@api_view(['GET'])
def carrier_list(request):
    """Listar todas las transportadoras activas"""
    carriers = Carrier.objects.filter(is_active=True)
    serializer = CarrierSerializer(carriers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def carrier_detail(request, carrier_id):
    """Obtener detalles de una transportadora"""
    try:
        carrier = Carrier.objects.get(id=carrier_id)
        serializer = CarrierSerializer(carrier)
        return Response(serializer.data)
    except Carrier.DoesNotExist:
        return Response({'error': 'Transportadora no encontrada'}, 
                       status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def shipping_guide_list(request):
    """Listar todas las guías de envío"""
    guides = ShippingGuide.objects.all()
    serializer = ShippingGuideSerializer(guides, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def shipping_guide_detail(request, guide_id):
    """Obtener detalles de una guía de envío"""
    try:
        guide = ShippingGuide.objects.get(id=guide_id)
        serializer = ShippingGuideSerializer(guide)
        return Response(serializer.data)
    except ShippingGuide.DoesNotExist:
        return Response({'error': 'Guía de envío no encontrada'}, 
                       status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def shipping_guide_by_order(request, order_id):
    """Obtener guías de envío de un pedido específico"""
    guides = ShippingGuide.objects.filter(order_id=order_id)
    serializer = ShippingGuideSerializer(guides, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def generate_guide(request):
    """Generar una guía de envío con una transportadora."""
    serializer = ShippingGuideCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    guide, success, error_message = generate_shipping_guide(
        carrier_id=data['carrier_id'],
        shipping_data=data
    )
    
    if not guide:
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
    
    response_serializer = ShippingGuideSerializer(guide)
    
    response_data = {
        'guide': response_serializer.data,
        'success': success
    }
    
    if not success:
        response_data['error'] = error_message
    
    http_status = status.HTTP_200_OK if success else status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return Response(response_data, status=http_status)

@api_view(['GET'])
def guide_statistics(request):
    """Estadísticas de generación de guías"""
    total = ShippingGuide.objects.count()
    generated = ShippingGuide.objects.filter(status=ShippingGuide.GENERATED).count()
    failed = ShippingGuide.objects.filter(status=ShippingGuide.FAILED).count()
    
    return Response({
        'total_guides': total,
        'generated': generated,
        'failed': failed,
        'success_rate': round((generated / total * 100) if total > 0 else 0, 2)
    })

