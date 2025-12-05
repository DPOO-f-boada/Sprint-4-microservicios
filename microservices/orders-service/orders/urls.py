from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<str:product_name>/', views.place_order, name='place_order'),
    path('orders/create/', views.create_order_view, name='create_order'),
]

