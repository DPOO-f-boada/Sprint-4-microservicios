from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Product, Supplier, Variable
from .serializers import ProductSerializer, SupplierSerializer, VariableSerializer

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class SupplierViewSet(ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class VariableViewSet(ModelViewSet):
    queryset = Variable.objects.all()
    serializer_class = VariableSerializer

@api_view(['GET'])
def product_list(request):
    """Listar todos los productos"""
    products = Product.objects.filter(is_active=True)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_detail(request, product_id):
    """Obtener detalles de un producto"""
    try:
        product = Product.objects.get(id=product_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def product_by_name(request, product_name):
    """Obtener producto por nombre"""
    try:
        product = Product.objects.get(name=product_name, is_active=True)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def create_product(request):
    """Crear un producto nuevo"""
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def supplier_list(request):
    """Listar todos los proveedores"""
    suppliers = Supplier.objects.filter(is_active=True)
    serializer = SupplierSerializer(suppliers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def variable_list(request):
    """Listar todas las variables"""
    variables = Variable.objects.all()
    serializer = VariableSerializer(variables, many=True)
    return Response(serializer.data)

