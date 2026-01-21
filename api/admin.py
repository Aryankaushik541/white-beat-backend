from django.contrib import admin
from django.contrib.auth.models import User, Group as DjangoGroup
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    UserProfile, Conversation, Message, MessageReaction,
    Call, Status, StatusView, Contact, Group, GroupMembership,
    APILog, SystemStats
)

# Customize User Admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'role', 'is_active_session', 'total_messages', 'status', 'bio',
        'phone_number', 'avatar', 'is_online', 'last_seen',
        'profile_photo_privacy', 'status_privacy', 'last_seen_privacy',
        'joined_date', 'last_activity'
    )
    readonly_fields = ('joined_date', 'last_activity', 'total_messages', 'last_seen')

class CustomUserAdmin(BaseUserAdmin):
    """Simplified User Admin for business use"""
    inlines = (UserProfileInline,)
    
    list_display = (
        'username', 
        'email', 
        'get_groups', 
        'is_active', 
        'get_total_messages',
        'get_is_online',
        'date_joined'
    )
    
    list_filter = ('is_active', 'groups', 'date_joined', 'profile__is_online')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
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
    
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'groups'),
        }),
    )
    
    def get_groups(self, obj):
        groups = obj.groups.all()
        return ', '.join([g.name for g in groups]) if groups else 'None'
    get_groups.short_description = 'Groups'
    
    def get_total_messages(self, obj):
        return obj.profile.total_messages if hasattr(obj, 'profile') else 0
    get_total_messages.short_description = 'Messages'
    
    def get_is_online(self, obj):
        return obj.profile.is_online if hasattr(obj, 'profile') else False
    get_is_online.short_description = 'Online'
    get_is_online.boolean = True

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Conversation Admin
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'get_message_count', 'is_archived', 'is_muted', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'is_archived_by_user1', 'is_archived_by_user2')
    search_fields = ('user1__username', 'user2__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',)
    
    def get_message_count(self, obj):
        return obj.messages.count()
    get_message_count.short_description = 'Messages'
    
    def is_archived(self, obj):
        return obj.is_archived_by_user1 or obj.is_archived_by_user2
    is_archived.short_description = 'Archived'
    is_archived.boolean = True
    
    def is_muted(self, obj):
        return obj.is_muted_by_user1 or obj.is_muted_by_user2
    is_muted.short_description = 'Muted'
    is_muted.boolean = True

# Message Admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'group', 'message_type', 'short_content', 'is_read', 'is_deleted', 'created_at')
    list_filter = ('message_type', 'is_read', 'is_deleted', 'deleted_for_everyone', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'content', 'group__name')
    readonly_fields = ('created_at', 'edited_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    def short_content(self, obj):
        if obj.message_type == 'text' and obj.content:
            return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return f'[{obj.message_type}]'
    short_content.short_description = 'Content'
    
    fieldsets = (
        ('Conversation', {
            'fields': ('conversation', 'group')
        }),
        ('Participants', {
            'fields': ('sender', 'receiver')
        }),
        ('Message', {
            'fields': ('message_type', 'content', 'media_url', 'thumbnail_url')
        }),
        ('Status', {
            'fields': ('is_read', 'is_deleted', 'deleted_for_everyone', 'is_forwarded')
        }),
        ('Reply/Edit', {
            'fields': ('reply_to', 'edited_at')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )

# Message Reaction Admin
@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__username', 'message__content')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

# Group Admin
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'get_member_count', 'get_admin_count', 'only_admins_can_send', 'created_at')
    list_filter = ('created_at', 'only_admins_can_send', 'only_admins_can_edit_info')
    search_fields = ('name', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',)
    filter_horizontal = ('admins',)
    
    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = 'Members'
    
    def get_admin_count(self, obj):
        return obj.admins.count()
    get_admin_count.short_description = 'Admins'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'avatar', 'created_by')
        }),
        ('Admins', {
            'fields': ('admins',)
        }),
        ('Settings', {
            'fields': ('only_admins_can_send', 'only_admins_can_edit_info')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

# Group Membership Admin
@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'user', 'is_admin', 'joined_at')
    list_filter = ('is_admin', 'joined_at')
    search_fields = ('group__name', 'user__username')
    readonly_fields = ('joined_at',)
    date_hierarchy = 'joined_at'
    ordering = ('-joined_at',)

# Call Admin
@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('id', 'caller', 'receiver', 'group', 'call_type', 'status', 'duration', 'started_at')
    list_filter = ('call_type', 'status', 'started_at')
    search_fields = ('caller__username', 'receiver__username', 'group__name', 'room_id')
    readonly_fields = ('started_at', 'answered_at', 'ended_at')
    date_hierarchy = 'started_at'
    ordering = ('-started_at',)
    
    fieldsets = (
        ('Participants', {
            'fields': ('caller', 'receiver', 'group')
        }),
        ('Call Info', {
            'fields': ('call_type', 'status', 'room_id')
        }),
        ('Timing', {
            'fields': ('started_at', 'answered_at', 'ended_at', 'duration')
        }),
    )

# Status Admin
@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status_type', 'short_content', 'privacy', 'get_view_count', 'created_at', 'expires_at')
    list_filter = ('status_type', 'privacy', 'created_at')
    search_fields = ('user__username', 'content')
    readonly_fields = ('created_at', 'expires_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    filter_horizontal = ('visible_to', 'hidden_from')
    
    def short_content(self, obj):
        if obj.status_type == 'text' and obj.content:
            return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return f'[{obj.status_type}]'
    short_content.short_description = 'Content'
    
    def get_view_count(self, obj):
        return obj.viewed_by.count()
    get_view_count.short_description = 'Views'
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Content', {
            'fields': ('status_type', 'content', 'media_url', 'background_color')
        }),
        ('Privacy', {
            'fields': ('privacy', 'visible_to', 'hidden_from')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at')
        }),
    )

# Status View Admin
@admin.register(StatusView)
class StatusViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'user', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('status__user__username', 'user__username')
    readonly_fields = ('viewed_at',)
    date_hierarchy = 'viewed_at'
    ordering = ('-viewed_at',)

# Contact Admin
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'contact', 'nickname', 'is_blocked', 'is_favorite', 'added_at')
    list_filter = ('is_blocked', 'is_favorite', 'added_at')
    search_fields = ('user__username', 'contact__username', 'nickname')
    readonly_fields = ('added_at',)
    date_hierarchy = 'added_at'
    ordering = ('-added_at',)
    
    fieldsets = (
        ('Users', {
            'fields': ('user', 'contact', 'nickname')
        }),
        ('Settings', {
            'fields': ('is_blocked', 'is_favorite')
        }),
        ('Timestamp', {
            'fields': ('added_at',)
        }),
    )

# API Log Admin
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

# System Stats Admin
@admin.register(SystemStats)
class SystemStatsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_users', 'active_users', 'total_messages', 'total_groups', 'total_calls', 'total_statuses', 'revenue')
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
            'fields': ('total_messages', 'total_groups', 'total_calls', 'total_statuses', 'total_api_calls')
        }),
        ('Financial', {
            'fields': ('revenue',)
        }),
    )

# Customize Group Admin
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_user_count')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)
    
    def get_user_count(self, obj):
        return obj.user_set.count()
    get_user_count.short_description = 'Users'

admin.site.unregister(DjangoGroup)
admin.site.register(DjangoGroup, CustomGroupAdmin)

# Customize admin site
admin.site.site_header = 'White Beat Admin Dashboard'
admin.site.site_title = 'White Beat Admin'
admin.site.index_title = 'Full Featured Chat Administration'
