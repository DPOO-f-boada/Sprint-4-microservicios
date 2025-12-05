from rest_framework import serializers
from .models import Warehouse, Inventory, Measurement

class WarehouseSerializer(serializers.ModelSerializer):
    current_stock = serializers.SerializerMethodField()
    available_capacity = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = [
            'id', 'name', 'latitude', 'longitude', 'address', 'phone',
            'capacity', 'is_active', 'current_stock', 'available_capacity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'current_stock', 'available_capacity']
    
    def get_current_stock(self, obj):
        return obj.get_current_stock()
    
    def get_available_capacity(self, obj):
        return obj.get_available_capacity()

class InventorySerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    available_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'product_id', 'product_name', 'warehouse', 'warehouse_name',
            'quantity', 'reserved_quantity', 'available_quantity',
            'updated_at', 'last_restock_date'
        ]
        read_only_fields = ['updated_at', 'available_quantity']
    
    def get_available_quantity(self, obj):
        return obj.get_available_quantity()

class MeasurementSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(source='place.name', read_only=True)
    
    class Meta:
        model = Measurement
        fields = [
            'id', 'variable_name', 'value', 'unit', 'dateTime',
            'place', 'place_name', 'product_id', 'product_name'
        ]
        read_only_fields = ['dateTime']

