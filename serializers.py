"""
Django REST Framework serializers for conversation management.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, ConversationSession, Message, 
    ConversationAnalytics, MessageReaction, ConversationTemplate
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'user', 'created_at', 'updated_at', 'is_active', 
            'preferences', 'total_conversations', 'total_messages'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_conversations', 'total_messages']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    
    class Meta:
        model = Message
        fields = [
            'id', 'session', 'message_type', 'content', 'status',
            'sequence_number', 'timestamp', 'ai_model', 'response_time_ms',
            'tokens_used', 'confidence_score', 'metadata', 'attachments',
            'word_count', 'character_count', 'language'
        ]
        read_only_fields = [
            'id', 'timestamp', 'word_count', 'character_count', 'sequence_number'
        ]
    
    def validate_content(self, value):
        """Validate message content."""
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        if len(value) > 10000:  # 10KB limit
            raise serializers.ValidationError("Message content is too long.")
        return value.strip()


class MessageReactionSerializer(serializers.ModelSerializer):
    """Serializer for MessageReaction model."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MessageReaction
        fields = ['id', 'message', 'user', 'reaction_type', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']


class ConversationAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for ConversationAnalytics model."""
    
    class Meta:
        model = ConversationAnalytics
        fields = [
            'session', 'total_duration_seconds', 'avg_user_response_time',
            'avg_ai_response_time', 'total_user_words', 'total_ai_words',
            'total_user_characters', 'total_ai_characters', 'user_message_count',
            'ai_message_count', 'system_message_count', 'avg_confidence_score',
            'failed_message_count', 'session_rating', 'user_satisfaction',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ConversationSessionSerializer(serializers.ModelSerializer):
    """Serializer for ConversationSession model."""
    user = UserSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    analytics = ConversationAnalyticsSerializer(read_only=True)
    
    class Meta:
        model = ConversationSession
        fields = [
            'id', 'user', 'title', 'description', 'status',
            'created_at', 'updated_at', 'last_activity_at',
            'message_count', 'ai_model_version', 'session_context',
            'tags', 'avg_response_time', 'total_tokens_used',
            'messages', 'analytics'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_activity_at', 'message_count'
        ]


class ConversationSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing conversation sessions."""
    user = serializers.StringRelatedField()
    
    class Meta:
        model = ConversationSession
        fields = [
            'id', 'user', 'title', 'status', 'created_at', 
            'last_activity_at', 'message_count', 'tags'
        ]


class ConversationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ConversationTemplate model."""
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ConversationTemplate
        fields = [
            'id', 'name', 'description', 'category', 'template_data',
            'is_active', 'usage_count', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at', 'updated_at']


class CreateMessageSerializer(serializers.Serializer):
    """Serializer for creating new messages in a conversation."""
    content = serializers.CharField(max_length=10000)
    message_type = serializers.ChoiceField(choices=Message.MESSAGE_TYPE_CHOICES)
    ai_model = serializers.CharField(max_length=100, required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False, default=dict)
    attachments = serializers.JSONField(required=False, default=list)
    
    def validate_content(self, value):
        """Validate message content."""
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        return value.strip()


class ConversationStatsSerializer(serializers.Serializer):
    """Serializer for conversation statistics."""
    total_sessions = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    avg_messages_per_session = serializers.FloatField()
    total_users = serializers.IntegerField()
    most_active_user = serializers.CharField()
    avg_session_duration = serializers.FloatField()
    popular_tags = serializers.ListField()
