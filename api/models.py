from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    """Extended user profile with additional fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=[('user', 'User'), ('admin', 'Admin')], default='user')
    joined_date = models.DateTimeField(default=timezone.now)
    is_active_session = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)
    total_messages = models.IntegerField(default=0)
    avatar = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=200, blank=True, default='Hey there! I am using White Beat')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    
    # Privacy settings
    profile_photo_privacy = models.CharField(
        max_length=20, 
        choices=[('everyone', 'Everyone'), ('contacts', 'Contacts'), ('nobody', 'Nobody')],
        default='everyone'
    )
    status_privacy = models.CharField(
        max_length=20,
        choices=[('everyone', 'Everyone'), ('contacts', 'Contacts'), ('nobody', 'Nobody')],
        default='everyone'
    )
    last_seen_privacy = models.CharField(
        max_length=20,
        choices=[('everyone', 'Everyone'), ('contacts', 'Contacts'), ('nobody', 'Nobody')],
        default='everyone'
    )
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Group(models.Model):
    """Represents a group chat"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_groups')
    admins = models.ManyToManyField(User, related_name='admin_groups', blank=True)
    members = models.ManyToManyField(User, through='GroupMembership', related_name='member_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Group settings
    only_admins_can_send = models.BooleanField(default=False)
    only_admins_can_edit_info = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name

class GroupMembership(models.Model):
    """Track group membership with roles"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    
    class Meta:
        unique_together = [['group', 'user']]
        verbose_name = 'Group Membership'
        verbose_name_plural = 'Group Memberships'
    
    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

class Conversation(models.Model):
    """Represents a chat conversation between two users"""
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived_by_user1 = models.BooleanField(default=False)
    is_archived_by_user2 = models.BooleanField(default=False)
    is_muted_by_user1 = models.BooleanField(default=False)
    is_muted_by_user2 = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-updated_at']
        unique_together = [['user1', 'user2']]
    
    def __str__(self):
        return f"{self.user1.username} <-> {self.user2.username}"
    
    def get_other_user(self, user):
        """Get the other user in the conversation"""
        return self.user2 if self.user1 == user else self.user1

class Message(models.Model):
    """Individual messages in a conversation or group"""
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('location', 'Location'),
        ('contact', 'Contact'),
        ('sticker', 'Sticker'),
        ('gif', 'GIF'),
    ]
    
    # Conversation or Group (one must be set)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    
    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField(blank=True, null=True)
    media_url = models.URLField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    
    # Message metadata
    is_read = models.BooleanField(default=False)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    delivered_to = models.ManyToManyField(User, related_name='delivered_messages', blank=True)
    
    # Reply/Forward
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    is_forwarded = models.BooleanField(default=False)
    
    # Deletion
    is_deleted = models.BooleanField(default=False)
    deleted_for_everyone = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
    
    def __str__(self):
        if self.group:
            return f"{self.sender.username} in {self.group.name}: {self.content[:50] if self.content else self.message_type}"
        return f"{self.sender.username} -> {self.receiver.username}: {self.content[:50] if self.content else self.message_type}"

class MessageReaction(models.Model):
    """Reactions to messages (like, love, laugh, etc.)"""
    REACTION_TYPES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('laugh', '😂'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😠'),
    ]
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['message', 'user']]
        verbose_name = 'Message Reaction'
        verbose_name_plural = 'Message Reactions'
    
    def __str__(self):
        return f"{self.user.username} reacted {self.get_reaction_type_display()} to message {self.message.id}"

class Call(models.Model):
    """Track voice and video calls"""
    CALL_TYPES = [
        ('audio', 'Audio Call'),
        ('video', 'Video Call'),
    ]
    
    CALL_STATUS = [
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('missed', 'Missed'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
    ]
    
    caller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calls_made')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calls_received', null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_calls', null=True, blank=True)
    
    call_type = models.CharField(max_length=20, choices=CALL_TYPES)
    status = models.CharField(max_length=20, choices=CALL_STATUS, default='initiated')
    
    started_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0, help_text='Duration in seconds')
    
    # WebRTC signaling data
    room_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Call'
        verbose_name_plural = 'Calls'
        ordering = ['-started_at']
    
    def __str__(self):
        if self.group:
            return f"{self.call_type} call in {self.group.name} by {self.caller.username}"
        return f"{self.call_type} call from {self.caller.username} to {self.receiver.username}"

class Status(models.Model):
    """WhatsApp-like status updates (24-hour stories)"""
    STATUS_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    PRIVACY_CHOICES = [
        ('everyone', 'Everyone'),
        ('contacts', 'My Contacts'),
        ('selected', 'Selected Contacts'),
        ('except', 'All Except'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='statuses')
    status_type = models.CharField(max_length=20, choices=STATUS_TYPES)
    content = models.TextField(blank=True, null=True)
    media_url = models.URLField(blank=True, null=True)
    background_color = models.CharField(max_length=7, blank=True, null=True, help_text='Hex color for text status')
    
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='everyone')
    visible_to = models.ManyToManyField(User, related_name='visible_statuses', blank=True)
    hidden_from = models.ManyToManyField(User, related_name='hidden_statuses', blank=True)
    
    viewed_by = models.ManyToManyField(User, through='StatusView', related_name='viewed_statuses')
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Statuses'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username}'s {self.status_type} status"

class StatusView(models.Model):
    """Track who viewed a status"""
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['status', 'user']]
        verbose_name = 'Status View'
        verbose_name_plural = 'Status Views'
    
    def __str__(self):
        return f"{self.user.username} viewed {self.status.user.username}'s status"

class Contact(models.Model):
    """User contacts/friends list"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacted_by')
    nickname = models.CharField(max_length=100, blank=True, null=True)
    is_blocked = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['user', 'contact']]
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
    
    def __str__(self):
        return f"{self.user.username} -> {self.contact.username}"

class APILog(models.Model):
    """Log all API requests"""
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status_code = models.IntegerField()
    response_time = models.FloatField()  # in milliseconds
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'API Log'
        verbose_name_plural = 'API Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"

class SystemStats(models.Model):
    """Store daily system statistics"""
    date = models.DateField(unique=True, default=timezone.now)
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    total_messages = models.IntegerField(default=0)
    total_groups = models.IntegerField(default=0)
    total_calls = models.IntegerField(default=0)
    total_statuses = models.IntegerField(default=0)
    total_api_calls = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'System Statistics'
        verbose_name_plural = 'System Statistics'
        ordering = ['-date']
    
    def __str__(self):
        return f"Stats for {self.date}"
