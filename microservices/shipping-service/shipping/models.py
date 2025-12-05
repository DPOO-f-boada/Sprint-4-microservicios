from django.db import models
from django.core.exceptions import ValidationError

class Carrier(models.Model):
    """Modelo para transportadoras"""
    name = models.CharField(max_length=100, unique=True)
    api_endpoint = models.URLField(blank=True, null=True)
    api_key = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    response_time_avg = models.FloatField(default=3.0, help_text="Tiempo promedio de respuesta en segundos")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Transportadora'
        verbose_name_plural = 'Transportadoras'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ShippingGuide(models.Model):
    """Modelo para guías de envío"""
    PENDING = 'PENDING'
    GENERATED = 'GENERATED'
    FAILED = 'FAILED'
    TIMEOUT = 'TIMEOUT'
    
    STATUS_CHOICES = [
        (PENDING, 'Pendiente'),
        (GENERATED, 'Generada'),
        (FAILED, 'Fallida'),
        (TIMEOUT, 'Timeout'),
    ]
    
    order_id = models.IntegerField(help_text="ID del pedido en el servicio de orders")
    carrier = models.ForeignKey(Carrier, on_delete=models.PROTECT, related_name='shipping_guides')
    guide_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    origin_address = models.TextField()
    destination_address = models.TextField()
    recipient_name = models.CharField(max_length=150)
    recipient_phone = models.CharField(max_length=20)
    recipient_document = models.CharField(max_length=20, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    dimensions = models.CharField(max_length=100, blank=True, null=True, help_text="Largo x Ancho x Alto (cm)")
    declared_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    carrier_response = models.JSONField(blank=True, null=True, help_text="Respuesta completa de la transportadora")
    carrier_tracking_number = models.CharField(max_length=100, blank=True, null=True)
    generation_time_seconds = models.FloatField(null=True, blank=True, help_text="Tiempo que tomó generar la guía")
    meets_performance_ASR = models.BooleanField(default=False, help_text="Cumple con el ASR de 8 segundos")
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Guía de Envío'
        verbose_name_plural = 'Guías de Envío'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_id']),
            models.Index(fields=['status']),
            models.Index(fields=['carrier']),
            models.Index(fields=['guide_number']),
        ]
    
    def __str__(self):
        guide_num = self.guide_number or "Pendiente"
        return f"Guía {guide_num} - Pedido #{self.order_id} - {self.carrier.name}"

