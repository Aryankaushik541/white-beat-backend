from django.urls import path
from . import views
from . import views_dashboard

urlpatterns = [
    # ============= AUTHENTICATION =============
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('verify-admin/', views.verify_admin, name='verify-admin'),
    path('make-admin/', views.make_admin, name='make-admin'),
    path('remove-admin/', views.remove_admin, name='remove-admin'),
    
    # ============= USER MANAGEMENT =============
    path('users/', views.get_users, name='get-users'),
    path('user-profile/', views.get_user_profile, name='get-user-profile'),
    path('update-profile/', views.update_user_profile, name='update-user-profile'),
    
    # ============= MESSAGING =============
    path('conversations/', views.get_conversations, name='get-conversations'),
    path('messages/', views.get_messages, name='get-messages'),
    path('send-message/', views.send_message, name='send-message'),
    path('delete-message/', views.delete_message, name='delete-message'),
    path('edit-message/', views.edit_message, name='edit-message'),
    path('react-message/', views.react_to_message, name='react-message'),
    path('mark-as-read/', views.mark_as_read, name='mark-as-read'),
    
    # ============= GROUPS =============
    path('create-group/', views.create_group, name='create-group'),
    path('groups/', views.get_groups, name='get-groups'),
    path('group-messages/', views.get_group_messages, name='get-group-messages'),
    path('add-group-member/', views.add_group_member, name='add-group-member'),
    path('remove-group-member/', views.remove_group_member, name='remove-group-member'),
    
    # ============= CALLS =============
    path('initiate-call/', views.initiate_call, name='initiate-call'),
    path('update-call-status/', views.update_call_status, name='update-call-status'),
    path('call-history/', views.get_call_history, name='call-history'),
    
    # ============= STATUS =============
    path('create-status/', views.create_status, name='create-status'),
    path('statuses/', views.get_statuses, name='get-statuses'),
    path('view-status/', views.view_status, name='view-status'),
    
    # ============= CONTACTS =============
    path('add-contact/', views.add_contact, name='add-contact'),
    path('contacts/', views.get_contacts, name='get-contacts'),
    
    # ============= ADMIN =============
    path('admin/stats/', views.admin_stats, name='admin-stats'),
    
    # ============= DASHBOARD ANALYTICS =============
    path('admin/api-logs/', views_dashboard.get_api_logs, name='get-api-logs'),
    path('admin/system-stats/', views_dashboard.get_system_stats, name='get-system-stats'),
    path('admin/update-stats/', views_dashboard.update_system_stats, name='update-system-stats'),
    path('analytics/', views_dashboard.get_user_analytics, name='get-user-analytics'),
    path('message-reactions/', views_dashboard.get_message_reactions, name='get-message-reactions'),
    path('status-views/', views_dashboard.get_status_views, name='get-status-views'),
    path('conversation-details/', views_dashboard.get_conversation_details, name='get-conversation-details'),
    
    # ============= HEALTH =============
    path('health/', views.health_check, name='health'),
]
