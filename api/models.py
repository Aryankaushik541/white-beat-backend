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
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"

class ChatMessage(models.Model):
    """Store chat messages for analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    prompt = models.TextField()
    response = models.TextField()
    model_used = models.CharField(max_length=50, default='gpt-3.5-turbo')
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    response_time = models.FloatField(default=0.0)  # in seconds
    
    class Meta:
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

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
    total_api_calls = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'System Statistics'
        verbose_name_plural = 'System Statistics'
        ordering = ['-date']
    
    def __str__(self):
        return f"Stats for {self.date}"