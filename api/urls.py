from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('chat/', views.chat, name='chat'),
    path('admin/stats/', views.admin_stats, name='admin_stats'),
    path('health/', views.health_check, name='health_check'),
]