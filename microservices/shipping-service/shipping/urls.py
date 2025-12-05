from django.urls import path
from . import views

urlpatterns = [
    path('carriers/', views.carrier_list, name='carrier_list'),
    path('carriers/<int:carrier_id>/', views.carrier_detail, name='carrier_detail'),
    path('guides/', views.shipping_guide_list, name='shipping_guide_list'),
    path('guides/<int:guide_id>/', views.shipping_guide_detail, name='shipping_guide_detail'),
    path('guides/order/<int:order_id>/', views.shipping_guide_by_order, name='shipping_guide_by_order'),
    path('guides/generate/', views.generate_guide, name='generate_guide'),
    path('guides/statistics/', views.guide_statistics, name='guide_statistics'),
]

