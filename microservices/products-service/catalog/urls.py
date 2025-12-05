from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/name/<str:product_name>/', views.product_by_name, name='product_by_name'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('variables/', views.variable_list, name='variable_list'),
]

