from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('verify-admin/', views.verify_admin, name='verify_admin'),
    path('chat/', views.chat, name='chat'),
    path('admin/stats/', views.admin_stats, name='admin_stats'),
    path('health/', views.health_check, name='health_check'),
]