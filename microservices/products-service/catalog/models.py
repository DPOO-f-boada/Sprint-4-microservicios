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

def validate_nit(value):
    if not value:
        return
    if not re.match(r'^\d{9}-\d$', str(value).strip()):
        raise ValidationError('NIT inválido. Formato: 123456789-0')

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

def validate_non_negative(value):
    if value is None:
        raise ValidationError('Este campo es obligatorio')
    if value < 0:
        raise ValidationError('El valor no puede ser negativo')

def product_name_validator(value):
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s\-]+$', value):
        raise ValidationError('Nombre de producto inválido')

class Supplier(models.Model):
    name = models.CharField(max_length=150, unique=True, validators=[validate_name_format])
    nit = models.CharField(max_length=12, unique=True, validators=[validate_nit])
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, validators=[validate_phone_number])
    address = models.TextField(validators=[validate_address_format])
    city = models.CharField(max_length=100, validators=[validate_name_format])
    contact_person = models.CharField(max_length=150, validators=[validate_name_format])
    is_active = models.BooleanField(default=True)
    credit_days = models.PositiveIntegerField(default=30)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.nit})"

class Product(models.Model):
    name = models.CharField(max_length=100, unique=True, validators=[product_name_validator])
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='products', null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[validate_non_negative])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[validate_non_negative])
    category = models.CharField(max_length=100, blank=True, null=True)
    min_stock = models.PositiveIntegerField(default=0)
    max_stock = models.PositiveIntegerField(default=10000)
    is_active = models.BooleanField(default=True)
    requires_special_handling = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_profit_margin(self):
        if self.cost_price and self.cost_price > 0:
            return ((self.unit_price - self.cost_price) / self.cost_price) * 100
        return 0

class Variable(models.Model):
    name = models.CharField(max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='variables')
    
    def __str__(self):
        return f'{self.name}'

