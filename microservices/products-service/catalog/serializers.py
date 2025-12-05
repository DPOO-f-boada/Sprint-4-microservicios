from rest_framework import serializers
from .models import Product, Supplier, Variable

class SupplierSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'nit', 'email', 'phone', 'address', 'city',
            'contact_person', 'is_active', 'credit_days', 'rating',
            'notes', 'products_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'products_count']
    
    def get_products_count(self, obj):
        return obj.products.count()

class ProductSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    profit_margin = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'sku', 'supplier', 'supplier_name',
            'unit_price', 'cost_price', 'category', 'min_stock', 'max_stock',
            'is_active', 'requires_special_handling', 'profit_margin',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'profit_margin']
    
    def get_profit_margin(self, obj):
        return round(obj.get_profit_margin(), 2)

class VariableSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Variable
        fields = ['id', 'name', 'product', 'product_name']

