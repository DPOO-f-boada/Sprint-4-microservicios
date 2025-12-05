from django.contrib import admin
from .models import Warehouse, Inventory, Measurement

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'latitude', 'longitude', 'is_active', 'capacity']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'warehouse', 'quantity', 'reserved_quantity']
    list_filter = ['warehouse']
    search_fields = ['product_name']

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'value', 'unit', 'place', 'dateTime']
    list_filter = ['place', 'dateTime']
    search_fields = ['product_name', 'variable_name']

