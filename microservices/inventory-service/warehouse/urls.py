from django.urls import path
from . import views

urlpatterns = [
    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/<int:warehouse_id>/', views.warehouse_detail, name='warehouse_detail'),
    path('inventory/<str:product_name>/', views.inventory_by_product, name='inventory_by_product'),
    path('inventory/<str:product_name>/restock/', views.inventory_restock, name='inventory_restock'),
    path('measurements/', views.measurement_list, name='measurement_list'),
    path('measurements/create/', views.measurement_create, name='measurement_create'),
]

