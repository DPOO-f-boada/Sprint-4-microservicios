from django.urls import path
from . import views

urlpatterns = [
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/profile/', views.profile_view, name='profile'),
    path('auth/verify/', views.verify_token, name='verify_token'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
]

