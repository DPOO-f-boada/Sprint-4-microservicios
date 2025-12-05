from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class User(AbstractUser):
    ADMIN = 'ADMIN'
    OPERARIO = 'OPERARIO'
    CLIENTE = 'CLIENTE'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrador'),
        (OPERARIO, 'Operario'),
        (CLIENTE, 'CLIENTE'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CLIENTE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    document_type = models.CharField(
        max_length=10,
        choices=[('CC', 'Cédula'), ('CE', 'Extranjería'), ('NIT', 'NIT'), ('PASSPORT', 'Pasaporte')],
        blank=True, null=True
    )
    document_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
        indexes = [
            models.Index(fields=['username']), 
            models.Index(fields=['email']),
            models.Index(fields=['role']), 
            models.Index(fields=['document_number'])
        ]
    
    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.get_role_display()})"
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == self.ADMIN
    
    def is_operario(self):
        return self.role == self.OPERARIO
    
    def is_cliente(self):
        return self.role == self.CLIENTE
    
    def has_role(self, *roles):
        return self.role in roles

