"""
Robust database models for conversation history management.
Supports multiple users, sessions, and chronological message storage.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinLengthValidator
import uuid


class UserProfile(models.Model):
    """
    Extended user profile for additional conversation-related data.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    preferences = models.JSONField(default=dict, blank=True)
    total_conversations = models.PositiveIntegerField(default=0)
    total_messages = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class ConversationSession(models.Model):
    """
    Represents a distinct conversation session between a user and AI.
    Each session contains multiple messages in chronological order.
    """
    SESSION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_sessions')
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='active')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    
    # Session metadata
    message_count = models.PositiveIntegerField(default=0)
    ai_model_version = models.CharField(max_length=100, blank=True)
    session_context = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Performance metrics
    avg_response_time = models.FloatField(null=True, blank=True)
    total_tokens_used = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'conversation_sessions'
        ordering = ['-last_activity_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-last_activity_at']),
            models.Index(fields=['user', 'status']),
        ]
        verbose_name = 'Conversation Session'
        verbose_name_plural = 'Conversation Sessions'
    
    def __str__(self):
        return f"Session {self.id} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Auto-generate title if not provided
        if not self.title and self.message_count > 0:
            first_message = self.messages.filter(message_type='user').first()
            if first_message:
                self.title = first_message.content[:50] + "..." if len(first_message.content) > 50 else first_message.content
        
        super().save(*args, **kwargs)


class Message(models.Model):
    """
    Individual messages within a conversation session.
    Stores both user queries and AI responses in chronological order.
    """
    MESSAGE_TYPE_CHOICES = [
        ('user', 'User Query'),
        ('ai', 'AI Response'),
        ('system', 'System Message'),
    ]
    
    MESSAGE_STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('processing', 'Processing'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ConversationSession, on_delete=models.CASCADE, related_name='messages')
    
    # Message content and metadata
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField(validators=[MinLengthValidator(1)])
    status = models.CharField(max_length=20, choices=MESSAGE_STATUS_CHOICES, default='sent')
    
    # Chronological ordering
    sequence_number = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # AI-specific fields
    ai_model = models.CharField(max_length=100, blank=True)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    
    # Message metadata
    metadata = models.JSONField(default=dict, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    
    # Content analysis
    word_count = models.PositiveIntegerField(default=0)
    character_count = models.PositiveIntegerField(default=0)
    language = models.CharField(max_length=10, default='en')
    
    class Meta:
        db_table = 'messages'
        ordering = ['session', 'sequence_number']
        unique_together = ['session', 'sequence_number']
        indexes = [
            models.Index(fields=['session', 'sequence_number']),
            models.Index(fields=['session', 'message_type', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['message_type', 'status']),
        ]
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    
    def __str__(self):
        return f"{self.message_type.title()} #{self.sequence_number} in {self.session.id}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate word and character counts
        if self.content:
            self.word_count = len(self.content.split())
            self.character_count = len(self.content)
        
        # Auto-assign sequence number if not provided
        if not self.sequence_number:
            last_message = Message.objects.filter(session=self.session).order_by('-sequence_number').first()
            self.sequence_number = (last_message.sequence_number + 1) if last_message else 1
        
        super().save(*args, **kwargs)
        
        # Update session message count and last activity
        self.session.message_count = self.session.messages.count()
        self.session.last_activity_at = timezone.now()
        self.session.save(update_fields=['message_count', 'last_activity_at'])


class ConversationAnalytics(models.Model):
    """
    Analytics and metrics for conversation sessions.
    """
    session = models.OneToOneField(ConversationSession, on_delete=models.CASCADE, related_name='analytics')
    
    # Timing metrics
    total_duration_seconds = models.PositiveIntegerField(default=0)
    avg_user_response_time = models.FloatField(null=True, blank=True)
    avg_ai_response_time = models.FloatField(null=True, blank=True)
    
    # Content metrics
    total_user_words = models.PositiveIntegerField(default=0)
    total_ai_words = models.PositiveIntegerField(default=0)
    total_user_characters = models.PositiveIntegerField(default=0)
    total_ai_characters = models.PositiveIntegerField(default=0)
    
    # Interaction metrics
    user_message_count = models.PositiveIntegerField(default=0)
    ai_message_count = models.PositiveIntegerField(default=0)
    system_message_count = models.PositiveIntegerField(default=0)
    
    # Quality metrics
    avg_confidence_score = models.FloatField(null=True, blank=True)
    failed_message_count = models.PositiveIntegerField(default=0)
    
    # Engagement metrics
    session_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5 scale
    user_satisfaction = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversation_analytics'
        verbose_name = 'Conversation Analytics'
        verbose_name_plural = 'Conversation Analytics'
    
    def __str__(self):
        return f"Analytics for {self.session.id}"


class MessageReaction(models.Model):
    """
    User reactions to AI messages (like, dislike, helpful, etc.)
    """
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('helpful', 'Helpful'),
        ('not_helpful', 'Not Helpful'),
        ('accurate', 'Accurate'),
        ('inaccurate', 'Inaccurate'),
    ]
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_reactions'
        unique_together = ['message', 'user', 'reaction_type']
        indexes = [
            models.Index(fields=['message', 'reaction_type']),
        ]
        verbose_name = 'Message Reaction'
        verbose_name_plural = 'Message Reactions'
    
    def __str__(self):
        return f"{self.user.username} {self.reaction_type} on {self.message.id}"


class ConversationTemplate(models.Model):
    """
    Predefined conversation templates for common use cases.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50)
    template_data = models.JSONField()
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversation_templates'
        ordering = ['category', 'name']
        verbose_name = 'Conversation Template'
        verbose_name_plural = 'Conversation Templates'
    
    def __str__(self):
        return f"{self.name} ({self.category})"
