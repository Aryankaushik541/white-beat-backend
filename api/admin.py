from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, ChatMessage, APILog, SystemStats

# Customize User Admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'is_active_session', 'total_messages', 'joined_date', 'last_activity')
    readonly_fields = ('joined_date', 'last_activity', 'total_messages')

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'get_role', 'get_total_messages', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else 'N/A'
    get_role.short_description = 'Role'
    
    def get_total_messages(self, obj):
        return obj.profile.total_messages if hasattr(obj, 'profile') else 0
    get_total_messages.short_description = 'Messages'

# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Chat Message Admin
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_prompt', 'model_used', 'tokens_used', 'response_time', 'created_at')
    list_filter = ('model_used', 'created_at')
    search_fields = ('user__username', 'prompt', 'response')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def short_prompt(self, obj):
        return obj.prompt[:50] + '...' if len(obj.prompt) > 50 else obj.prompt
    short_prompt.short_description = 'Prompt'
    
    fieldsets = (
        ('Message Info', {
            'fields': ('user', 'prompt', 'response')
        }),
        ('Metadata', {
            'fields': ('model_used', 'tokens_used', 'response_time', 'created_at')
        }),
    )

# API Log Admin
@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'method', 'user', 'status_code', 'response_time', 'created_at')
    list_filter = ('method', 'status_code', 'created_at')
    search_fields = ('endpoint', 'user__username', 'ip_address')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Request Info', {
            'fields': ('endpoint', 'method', 'user', 'ip_address')
        }),
        ('Response Info', {
            'fields': ('status_code', 'response_time')
        }),
        ('Additional', {
            'fields': ('user_agent', 'created_at')
        }),
    )

# System Stats Admin
@admin.register(SystemStats)
class SystemStatsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_users', 'active_users', 'total_messages', 'total_api_calls', 'revenue')
    list_filter = ('date',)
    date_hierarchy = 'date'
    readonly_fields = ('date',)
    
    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('User Statistics', {
            'fields': ('total_users', 'active_users')
        }),
        ('Activity Statistics', {
            'fields': ('total_messages', 'total_api_calls')
        }),
        ('Financial', {
            'fields': ('revenue',)
        }),
    )

# Customize admin site
admin.site.site_header = 'White Beat Admin Dashboard'
admin.site.site_title = 'White Beat Admin'
admin.site.index_title = 'Welcome to White Beat Administration'