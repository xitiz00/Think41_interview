"""
URL configuration for conversation_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    path('api/conversations/', include('conversations.urls')),
    path('api/', include('conversations.urls')),  # Root API endpoints
]
