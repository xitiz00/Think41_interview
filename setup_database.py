"""
Database setup script for conversation backend.
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conversation_backend.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User
from conversations.models import UserProfile, ConversationSession, Message


def setup_database():
    """Setup database with initial data."""
    print("🔧 Setting up conversation database...")
    
    # Run migrations
    print("📊 Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create superuser if it doesn't exist
    print("👤 Creating superuser...")
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("✅ Superuser created: admin/admin123")
    else:
        print("✅ Superuser already exists")
    
    # Create sample users and data
    print("📝 Creating sample data...")
    create_sample_data()
    
    print("🎉 Database setup completed!")
    print("\n📋 Next steps:")
    print("1. Start the server: python manage.py runserver")
    print("2. Access admin: http://localhost:8000/admin")
    print("3. API root: http://localhost:8000/api/")


def create_sample_data():
    """Create sample conversation data."""
    # Create sample users
    users_data = [
        {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
        {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
        {'username': 'bob_wilson', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Wilson'},
    ]
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name']
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
            
            # Create sample conversation session
            session = ConversationSession.objects.create(
                user=user,
                title=f"Sample conversation for {user.first_name}",
                description="This is a sample conversation session",
                status='active',
                ai_model_version='gpt-4',
                tags=['sample', 'demo']
            )
            
            # Create sample messages
            messages_data = [
                {'type': 'user', 'content': 'Hello, I need help with my project.'},
                {'type': 'ai', 'content': 'Hello! I\'d be happy to help you with your project. Could you tell me more about what you\'re working on?'},
                {'type': 'user', 'content': 'I\'m building a web application and need advice on the database design.'},
                {'type': 'ai', 'content': 'Great! Database design is crucial for web applications. What type of data will your application be handling?'},
            ]
            
            for i, msg_data in enumerate(messages_data, 1):
                Message.objects.create(
                    session=session,
                    message_type=msg_data['type'],
                    content=msg_data['content'],
                    sequence_number=i,
                    ai_model='gpt-4' if msg_data['type'] == 'ai' else '',
                    response_time_ms=150 if msg_data['type'] == 'ai' else None,
                    confidence_score=0.95 if msg_data['type'] == 'ai' else None
                )
            
            print(f"✅ Created sample data for user: {user.username}")


if __name__ == '__main__':
    setup_database()
