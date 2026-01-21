from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('verify-admin/', views.verify_admin, name='verify-admin'),
    path('make-admin/', views.make_admin, name='make-admin'),
    path('remove-admin/', views.remove_admin, name='remove-admin'),
    
    # User-to-User Messaging
    path('users/', views.get_users, name='get-users'),
    path('conversations/', views.get_conversations, name='get-conversations'),
    path('messages/', views.get_messages, name='get-messages'),
    path('send-message/', views.send_message, name='send-message'),
    path('mark-as-read/', views.mark_as_read, name='mark-as-read'),
    
    # Admin
    path('admin/stats/', views.admin_stats, name='admin-stats'),
    
    # Health
    path('health/', views.health_check, name='health'),
]
