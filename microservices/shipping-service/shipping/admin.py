from django.contrib import admin
from .models import Carrier, ShippingGuide

@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'response_time_avg', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(ShippingGuide)
class ShippingGuideAdmin(admin.ModelAdmin):
    list_display = ['guide_number', 'order_id', 'carrier', 'status', 'created_at']
    list_filter = ['status', 'carrier', 'created_at']
    search_fields = ['guide_number', 'order_id', 'recipient_name']
    readonly_fields = ['generated_at']

