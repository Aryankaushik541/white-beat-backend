from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, Conversation, Message, APILog, SystemStats

# Customize User Admin - Simplified for business use
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'is_active_session', 'total_messages', 'status', 'joined_date', 'last_activity')
    readonly_fields = ('joined_date', 'last_activity', 'total_messages')

class CustomUserAdmin(BaseUserAdmin):
    """
    Simplified User Admin for business use
    - Only Active and Groups (Admin) fields
    - Full read/write access to user data
    - Shows all Django users
    - Shows chat messages and groups
    """
    inlines = (UserProfileInline,)
    
    # List display
    list_display = (
        'username', 
        'email', 
        'get_groups', 
        'is_active', 
        'get_total_messages',
        'date_joined'
    )
    
    # Filters
    list_filter = ('is_active', 'groups', 'date_joined')
    
    # Search
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Ordering
    ordering = ('-date_joined',)
    
    # Fieldsets - Simplified
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'password', 'email', 'first_name', 'last_name')
        }),
        ('Permissions', {
            'fields': ('is_active', 'groups'),
            'description': 'Active: User can login | Groups: Add to "Admin" group for admin access'
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Add user fieldsets
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'groups'),
        }),
    )
    
    # Custom methods
    def get_groups(self, obj):
        """Show user groups"""
        groups = obj.groups.all()
        if groups:
            return ', '.join([g.name for g in groups])
        return 'None'
    get_groups.short_description = 'Groups'
    
    def get_total_messages(self, obj):
        """Show total messages"""
        return obj.profile.total_messages if hasattr(obj, 'profile') else 0
    get_total_messages.short_description = 'Messages'
    
    # Enable full read/write access
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True
    
    def has_view_permission(self, request, obj=None):
        return True

# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Conversation Admin
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'get_message_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user1__username', 'user2__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',)
    
    def get_message_count(self, obj):
        return obj.messages.count()
    get_message_count.short_description = 'Messages'
    
    fieldsets = (
        ('Participants', {
            'fields': ('user1', 'user2')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

# Message Admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'short_content', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'sender', 'receiver')
    search_fields = ('sender__username', 'receiver__username', 'content')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'
    
    fieldsets = (
        ('Conversation', {
            'fields': ('conversation',)
        }),
        ('Participants', {
            'fields': ('sender', 'receiver')
        }),
        ('Message', {
            'fields': ('content', 'is_read')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )

# API Log Admin - Full access
@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'method', 'user', 'status_code', 'response_time', 'ip_address', 'created_at')
    list_filter = ('method', 'status_code', 'created_at')
    search_fields = ('endpoint', 'user__username', 'ip_address')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
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
    
    # Full access
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True

# System Stats Admin - Full access
@admin.register(SystemStats)
class SystemStatsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_users', 'active_users', 'total_messages', 'total_api_calls', 'revenue')
    list_filter = ('date',)
    date_hierarchy = 'date'
    readonly_fields = ('date',)
    ordering = ('-date',)
    
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
    
    # Full access
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True

# Customize Group Admin - Full access
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_user_count')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)
    
    def get_user_count(self, obj):
        return obj.user_set.count()
    get_user_count.short_description = 'Users'
    
    # Full access
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True

# Unregister default Group admin and register custom one
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)

# Customize admin site
admin.site.site_header = 'White Beat Admin Dashboard'
admin.site.site_title = 'White Beat Admin'
admin.site.index_title = 'User Chat Administration Panel'
