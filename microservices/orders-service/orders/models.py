from django.db import models
from django.core.exceptions import ValidationError

def validate_positive_quantity(value):
    if value is None or value <= 0:
        raise ValidationError('La cantidad debe ser mayor a cero')

def validate_address_format(value):
    if not value:
        return
    value = value.strip()
    if not (5 <= len(value) <= 200):
        raise ValidationError('La dirección debe tener entre 5 y 200 caracteres')

class Order(models.Model):
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    REJECTED = 'REJECTED'
    CANCELLED = 'CANCELLED'
    IN_TRANSIT = 'IN_TRANSIT'
    DELIVERED = 'DELIVERED'

    STATUS_CHOICES = [
        (PENDING, 'Pendiente'),
        (CONFIRMED, 'Confirmado'),
        (REJECTED, 'Rechazado'),
        (CANCELLED, 'Cancelado'),
        (IN_TRANSIT, 'En Tránsito'),
        (DELIVERED, 'Entregado'),
    ]

    product_id = models.IntegerField()  # ID del producto en el servicio de productos
    product_name = models.CharField(max_length=100)  # Cache del nombre del producto
    units = models.PositiveIntegerField(validators=[validate_positive_quantity])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    warehouse_id = models.IntegerField(null=True, blank=True)  # ID de la bodega en el servicio de inventario
    warehouse_name = models.CharField(max_length=100, null=True, blank=True)  # Cache del nombre
    customer_id = models.IntegerField(null=True, blank=True)  # ID del usuario en el servicio de autenticación
    customer_name = models.CharField(max_length=150, null=True, blank=True)  # Cache del nombre
    delivery_address = models.TextField(blank=True, null=True, validators=[validate_address_format])
    delivery_zone = models.CharField(max_length=50, blank=True, null=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.product_name} x{self.units} [{self.get_status_display()}]"

