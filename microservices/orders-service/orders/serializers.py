from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'product_id', 'product_name', 'units', 'status', 'status_display',
            'warehouse_id', 'warehouse_name', 'customer_id', 'customer_name',
            'delivery_address', 'delivery_zone', 'total_price', 'notes',
            'created_at', 'updated_at', 'confirmed_at', 'delivered_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'confirmed_at', 'delivered_at']

