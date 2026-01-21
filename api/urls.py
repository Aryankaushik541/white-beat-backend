from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login, name='login'),
    path('verify-admin/', views.verify_admin, name='verify-admin'),
    path('make-admin/', views.make_admin, name='make-admin'),
    
    # Chat
    path('chat/', views.chat, name='chat'),
    
    # OSINT
    path('osint/', views.osint_lookup, name='osint'),
    
    # Admin
    path('admin/stats/', views.admin_stats, name='admin-stats'),
    
    # Health
    path('health/', views.health_check, name='health'),
]
