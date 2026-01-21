from django.urls import path
from . import views

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
    
    # ============= HEALTH =============
    path('health/', views.health_check, name='health'),
]
