from django.contrib import admin
from .models import Product, Supplier, Variable

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'nit', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'nit', 'email']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'unit_price', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['name', 'sku']

@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ['name', 'product']
    search_fields = ['name']

