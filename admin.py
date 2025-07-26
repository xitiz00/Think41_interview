"""
Django admin configuration for conversation management.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    UserProfile, ConversationSession, Message, 
    ConversationAnalytics, MessageReaction, ConversationTemplate
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model."""
    list_display = ['user', 'total_conversations', 'total_messages', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'total_conversations', 'total_messages']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'is_active')
        }),
        ('Statistics', {
            'fields': ('total_conversations', 'total_messages')
        }),
        ('Preferences', {
            'fields': ('preferences',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class MessageInline(admin.TabularInline):
    """Inline admin for messages within conversation sessions."""
    model = Message
    extra = 0
    readonly_fields = ['id', 'timestamp', 'word_count', 'character_count']
    fields = ['sequence_number', 'message_type', 'content', 'status', 'timestamp']
    ordering = ['sequence_number']


@admin.register(ConversationSession)
class ConversationSessionAdmin(admin.ModelAdmin):
    """Admin interface for ConversationSession model."""
    list_display = [
        'short_id', 'user', 'title', 'status', 'message_count', 
        'last_activity_at', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'last_activity_at']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'last_activity_at', 'message_count'
    ]
    inlines = [MessageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'title', 'description', 'status')
        }),
        ('Metadata', {
            'fields': ('ai_model_version', 'session_context', 'tags'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('message_count', 'avg_response_time', 'total_tokens_used')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_activity_at'),
            'classes': ('collapse',)
        }),
    )
    
    def short_id(self, obj):
        """Display shortened UUID."""
        return str(obj.id)[:8] + "..."
    short_id.short_description = "Session ID"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""
    list_display = [
        'short_id', 'session_link', 'message_type', 'sequence_number', 
        'content_preview', 'status', 'timestamp'
    ]
    list_filter = ['message_type', 'status', 'timestamp', 'ai_model']
    search_fields = ['content', 'session__title', 'session__user__username']
    readonly_fields = [
        'id', 'timestamp', 'word_count', 'character_count', 'sequence_number'
    ]
    
    fieldsets = (
        ('Message Information', {
            'fields': ('id', 'session', 'message_type', 'content', 'status')
        }),
        ('Sequence', {
            'fields': ('sequence_number', 'timestamp')
        }),
        ('AI Information', {
            'fields': ('ai_model', 'response_time_ms', 'tokens_used', 'confidence_score'),
            'classes': ('collapse',)
        }),
        ('Content Analysis', {
            'fields': ('word_count', 'character_count', 'language'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'attachments'),
            'classes': ('collapse',)
        }),
    )
    
    def short_id(self, obj):
        """Display shortened UUID."""
        return str(obj.id)[:8] + "..."
    short_id.short_description = "Message ID"
    
    def session_link(self, obj):
        """Link to the conversation session."""
        url = reverse('admin:conversations_conversationsession_change', args=[obj.session.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.session.id)[:8] + "...")
    session_link.short_description = "Session"
    
    def content_preview(self, obj):
        """Show preview of message content."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content Preview"


@admin.register(ConversationAnalytics)
class ConversationAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for ConversationAnalytics model."""
    list_display = [
        'session_link', 'user_message_count', 'ai_message_count', 
        'total_duration_seconds', 'session_rating', 'updated_at'
    ]
    list_filter = ['session_rating', 'user_satisfaction', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Session', {
            'fields': ('session',)
        }),
        ('Timing Metrics', {
            'fields': ('total_duration_seconds', 'avg_user_response_time', 'avg_ai_response_time')
        }),
        ('Content Metrics', {
            'fields': (
                'total_user_words', 'total_ai_words', 
                'total_user_characters', 'total_ai_characters'
            )
        }),
        ('Interaction Metrics', {
            'fields': ('user_message_count', 'ai_message_count', 'system_message_count')
        }),
        ('Quality Metrics', {
            'fields': ('avg_confidence_score', 'failed_message_count', 'session_rating', 'user_satisfaction')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def session_link(self, obj):
        """Link to the conversation session."""
        url = reverse('admin:conversations_conversationsession_change', args=[obj.session.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.session.id)[:8] + "...")
    session_link.short_description = "Session"


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    """Admin interface for MessageReaction model."""
    list_display = ['user', 'message_link', 'reaction_type', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__username', 'comment']
    
    def message_link(self, obj):
        """Link to the message."""
        url = reverse('admin:conversations_message_change', args=[obj.message.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.message.id)[:8] + "...")
    message_link.short_description = "Message"


@admin.register(ConversationTemplate)
class ConversationTemplateAdmin(admin.ModelAdmin):
    """Admin interface for ConversationTemplate model."""
    list_display = ['name', 'category', 'is_active', 'usage_count', 'created_by', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'description', 'category', 'is_active')
        }),
        ('Template Data', {
            'fields': ('template_data',)
        }),
        ('Statistics', {
            'fields': ('usage_count', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
