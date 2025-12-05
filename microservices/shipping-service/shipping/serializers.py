from rest_framework import serializers
from .models import Carrier, ShippingGuide

class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = [
            'id', 'name', 'api_endpoint', 'is_active', 
            'response_time_avg', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ShippingGuideSerializer(serializers.ModelSerializer):
    carrier_name = serializers.CharField(source='carrier.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ShippingGuide
        fields = [
            'id', 'order_id', 'carrier', 'carrier_name', 'guide_number', 
            'status', 'status_display', 'origin_address', 'destination_address',
            'recipient_name', 'recipient_phone', 'recipient_document',
            'weight_kg', 'dimensions', 'declared_value',
            'carrier_tracking_number', 'generation_time_seconds',
            'meets_performance_ASR', 'error_message',
            'created_at', 'updated_at', 'generated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'generated_at', 
            'generation_time_seconds', 'meets_performance_ASR'
        ]

class ShippingGuideCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    carrier_id = serializers.IntegerField()
    origin_address = serializers.CharField()
    destination_address = serializers.CharField()
    recipient_name = serializers.CharField()
    recipient_phone = serializers.CharField()
    recipient_document = serializers.CharField(required=False, allow_blank=True)
    weight_kg = serializers.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    dimensions = serializers.CharField(required=False, allow_blank=True)
    declared_value = serializers.DecimalField(max_digits=12, decimal_places=2, default=0.00)

