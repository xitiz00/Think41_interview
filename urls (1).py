"""
URL configuration for conversations app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='userprofile')
router.register(r'sessions', views.ConversationSessionViewSet, basename='conversationsession')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'analytics', views.ConversationAnalyticsViewSet, basename='conversationanalytics')
router.register(r'templates', views.ConversationTemplateViewSet, basename='conversationtemplate')

urlpatterns = [
    path('', views.api_root, name='api_root'),
    path('', include(router.urls)),
]
