from django.db import models
from django.core.exceptions import ValidationError
import re

def validate_name_format(value):
    if not value:
        raise ValidationError('El nombre es obligatorio')
    value = value.strip()
    if len(value) < 2 or len(value) > 100:
        raise ValidationError('El nombre debe tener entre 2 y 100 caracteres')
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value):
        raise ValidationError('El nombre solo puede contener letras y espacios')

def validate_coordinates(latitude, longitude):
    if not (-4.5 <= latitude <= 13.5):
        raise ValidationError('Latitud fuera del rango válido para Colombia')
    if not (-79 <= longitude <= -66):
        raise ValidationError('Longitud fuera del rango válido para Colombia')

def validate_phone_number(value):
    if not value:
        return
    phone = re.sub(r'[\s\-\(\)]', '', str(value))
    if not re.match(r'^(\+57)?[36]\d{9}$|^(\+57)?[1-8]\d{6,7}$', phone):
        raise ValidationError('Número de teléfono inválido')

def validate_address_format(value):
    if not value:
        return
    value = value.strip()
    if not (5 <= len(value) <= 200):
        raise ValidationError('La dirección debe tener entre 5 y 200 caracteres')
    if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s#\-,.°]+$', value):
        raise ValidationError('La dirección contiene caracteres no permitidos')

class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True, validators=[validate_name_format])
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField(blank=True, null=True, validators=[validate_address_format])
    phone = models.CharField(max_length=20, blank=True, null=True, validators=[validate_phone_number])
    capacity = models.PositiveIntegerField(default=50000)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_current_stock(self):
        return self.inventories.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    def get_available_capacity(self):
        return self.capacity - self.get_current_stock()

class Inventory(models.Model):
    product_id = models.IntegerField()  # ID del producto en el servicio de productos
    product_name = models.CharField(max_length=100)  # Cache del nombre del producto
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventories')
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    last_restock_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        unique_together = [('product_id', 'warehouse')]
    
    def __str__(self):
        return f"{self.product_name} @ {self.warehouse.name} — {self.quantity} u"
    
    def get_available_quantity(self):
        return self.quantity - self.reserved_quantity

class Measurement(models.Model):
    variable_name = models.CharField(max_length=50)
    value = models.FloatField(null=True, blank=True, default=None)
    unit = models.CharField(max_length=50)
    dateTime = models.DateTimeField(auto_now_add=True)
    place = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product_id = models.IntegerField(null=True, blank=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        product_name = self.product_name if self.product_name else "N/A"
        return f"{product_name} - {self.value} {self.unit}"

