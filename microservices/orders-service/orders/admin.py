from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_name', 'units', 'status', 'warehouse_name', 'customer_name', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['product_name', 'customer_name']

