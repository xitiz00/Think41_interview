"""
Django REST Framework views for conversation management API.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
import logging

from .models import (
    UserProfile, ConversationSession, Message, 
    ConversationAnalytics, MessageReaction, ConversationTemplate
)
from .serializers import (
    UserProfileSerializer, ConversationSessionSerializer,
    ConversationSessionListSerializer, MessageSerializer,
    ConversationAnalyticsSerializer, MessageReactionSerializer,
    ConversationTemplateSerializer, CreateMessageSerializer,
    ConversationStatsSerializer
)

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API responses."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user profiles."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Return user profiles based on permissions."""
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile."""
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConversationSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversation sessions."""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Return conversation sessions for the current user."""
        queryset = ConversationSession.objects.filter(user=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Search by title or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('-last_activity_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ConversationSessionListSerializer
        return ConversationSessionSerializer
    
    def perform_create(self, serializer):
        """Create a new conversation session."""
        serializer.save(user=self.request.user)
        logger.info(f"Created new conversation session for user {self.request.user.username}")
    
    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """Add a new message to the conversation session."""
        session = self.get_object()
        serializer = CreateMessageSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create the message
            message = Message.objects.create(
                session=session,
                content=serializer.validated_data['content'],
                message_type=serializer.validated_data['message_type'],
                ai_model=serializer.validated_data.get('ai_model', ''),
                metadata=serializer.validated_data.get('metadata', {}),
                attachments=serializer.validated_data.get('attachments', [])
            )
            
            # Return the created message
            message_serializer = MessageSerializer(message)
            logger.info(f"Added message to session {session.id}")
            return Response(message_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages for a conversation session."""
        session = self.get_object()
        messages = session.messages.all().order_by('sequence_number')
        
        # Pagination for messages
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a conversation session."""
        session = self.get_object()
        session.status = 'archived'
        session.save()
        logger.info(f"Archived session {session.id}")
        return Response({'status': 'archived'})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a conversation session."""
        session = self.get_object()
        session.status = 'active'
        session.save()
        logger.info(f"Activated session {session.id}")
        return Response({'status': 'active'})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get conversation statistics for the current user."""
        user_sessions = ConversationSession.objects.filter(user=request.user)
        
        stats = {
            'total_sessions': user_sessions.count(),
            'active_sessions': user_sessions.filter(status='active').count(),
            'total_messages': Message.objects.filter(session__user=request.user).count(),
            'avg_messages_per_session': user_sessions.aggregate(
                avg=Avg('message_count')
            )['avg'] or 0,
            'recent_activity': user_sessions.filter(
                last_activity_at__gte=timezone.now() - timedelta(days=7)
            ).count()
        }
        
        return Response(stats)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing individual messages."""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Return messages for the current user's sessions."""
        return Message.objects.filter(session__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Add a reaction to a message."""
        message = self.get_object()
        reaction_type = request.data.get('reaction_type')
        comment = request.data.get('comment', '')
        
        if not reaction_type:
            return Response(
                {'error': 'reaction_type is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or update reaction
        reaction, created = MessageReaction.objects.update_or_create(
            message=message,
            user=request.user,
            reaction_type=reaction_type,
            defaults={'comment': comment}
        )
        
        serializer = MessageReactionSerializer(reaction)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)
    
    @action(detail=True, methods=['get'])
    def reactions(self, request, pk=None):
        """Get all reactions for a message."""
        message = self.get_object()
        reactions = message.reactions.all()
        serializer = MessageReactionSerializer(reactions, many=True)
        return Response(serializer.data)


class ConversationAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for conversation analytics (read-only)."""
    serializer_class = ConversationAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return analytics for the current user's sessions."""
        return ConversationAnalytics.objects.filter(session__user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get analytics summary for all user's conversations."""
        user_analytics = self.get_queryset()
        
        summary = {
            'total_conversations': user_analytics.count(),
            'total_duration': sum(a.total_duration_seconds for a in user_analytics),
            'avg_messages_per_conversation': user_analytics.aggregate(
                avg=Avg('user_message_count')
            )['avg'] or 0,
            'avg_response_time': user_analytics.aggregate(
                avg=Avg('avg_ai_response_time')
            )['avg'] or 0,
            'total_words_exchanged': sum(
                a.total_user_words + a.total_ai_words for a in user_analytics
            ),
            'avg_satisfaction': user_analytics.exclude(
                session_rating__isnull=True
            ).aggregate(avg=Avg('session_rating'))['avg'] or 0
        }
        
        return Response(summary)


class ConversationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversation templates."""
    serializer_class = ConversationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return active conversation templates."""
        return ConversationTemplate.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        """Create a new conversation template."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """Create a new conversation session from a template."""
        template = self.get_object()
        
        # Create new session based on template
        session = ConversationSession.objects.create(
            user=request.user,
            title=f"From template: {template.name}",
            description=template.description,
            session_context=template.template_data,
            tags=[template.category]
        )
        
        # Increment usage count
        template.usage_count = F('usage_count') + 1
        template.save(update_fields=['usage_count'])
        
        serializer = ConversationSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# API Root view
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_root(request):
    """API root endpoint with available endpoints."""
    return Response({
        'message': 'Conversation Management API',
        'version': '1.0.0',
        'user': request.user.username,
        'endpoints': {
            'profiles': '/api/profiles/',
            'sessions': '/api/sessions/',
            'messages': '/api/messages/',
            'analytics': '/api/analytics/',
            'templates': '/api/templates/',
            'auth': '/api/auth/token/',
        },
        'documentation': '/api/docs/',
        'timestamp': timezone.now().isoformat()
    })
