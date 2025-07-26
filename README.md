# E-commerce AI Full-Stack Application

A comprehensive full-stack e-commerce application with AI-powered recommendations, featuring a React/Next.js frontend and FastAPI backend with MySQL database. Additionally, it includes a robust Django REST Framework backend service for managing conversation histories between users and AI systems.

## 🏗️ Architecture

\`\`\`
ecommerce-fullstack/
├── backend/                 # FastAPI backend service
│   ├── api/                # API endpoints
│   │   └── main.py         # Main FastAPI application
│   ├── database/           # Database schema and migrations
│   │   └── schema.sql      # MySQL schema
│   ├── scripts/            # Utility scripts
│   │   ├── load_data.py    # Data loading script
│   │   └── setup.sh        # Backend setup script
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend Docker configuration
├── frontend/               # Next.js frontend application
│   ├── app/               # Next.js app directory
│   │   ├── page.tsx       # Main dashboard page
│   │   ├── layout.tsx     # Root layout
│   │   └── globals.css    # Global styles
│   ├── package.json       # Node.js dependencies
│   └── Dockerfile        # Frontend Docker configuration
├── conversation-backend/   # Django REST Framework backend service
│   ├── conversation_backend/ # Django project directory
│   │   ├── api/            # API endpoints
│   │   │   └── views.py    # API views
│   │   ├── database/       # Database schema and migrations
│   │   │   └── models.py   # Django models
│   │   ├── scripts/        # Utility scripts
│   │   │   ├── setup_database.py # Database setup script
│   │   │   └── run_server.py   # Server start script
│   │   ├── requirements.txt # Python dependencies
│   │   └── settings.py    # Django settings
│   ├── manage.py          # Django management script
│   └── Dockerfile         # Conversation backend Docker configuration
├── docker-compose.yml     # Multi-service Docker setup
└── README.md             # This file
\`\`\`

## 🚀 Features

### Backend (FastAPI + MySQL)
- **RESTful API** with comprehensive endpoints
- **MySQL Database** with optimized schema
- **AI Recommendations** using collaborative and content-based filtering
- **Real-time Analytics** and sales reporting
- **Data Loading Scripts** for CSV import
- **CORS Support** for frontend integration

### Conversation Backend (Django REST Framework)
- **Multi-user Support**: Each user can have multiple conversation sessions
- **Session Management**: Distinct sessions with status tracking (active, paused, completed, archived)
- **Chronological Ordering**: Messages stored with sequence numbers and timestamps
- **Rich Metadata**: Support for AI model versions, response times, confidence scores
- **Analytics**: Comprehensive conversation analytics and metrics
- **Reactions**: User feedback system for AI responses
- **Templates**: Reusable conversation starters
- **Token-based Authentication**: Secure API access
- **Admin Interface**: Manage users, profiles, sessions, and analytics

### Frontend (Next.js + React)
- **Modern Dashboard** with real-time data
- **Responsive Design** with Tailwind CSS
- **API Integration** with backend services
- **Sales Analytics** visualization
- **Product Management** interface
- **Conversation Management**: Interface for managing user conversations

## 🛠️ Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository and navigate to project:**
   \`\`\`bash
   cd ecommerce-fullstack
   \`\`\`

2. **Start all services:**
   \`\`\`bash
   docker-compose up -d
   \`\`\`

3. **Load sample data:**
   \`\`\`bash
   docker-compose exec backend python scripts/load_data.py
   \`\`\`

4. **Access the applications:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Conversation Backend API: http://localhost:8000/api/
   - Conversation Backend Admin Interface: http://localhost:8000/admin/ (admin/admin123)
   - Conversation Backend API Documentation: Available through Django REST Framework browsable API

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory:**
   \`\`\`bash
   cd backend
   \`\`\`

2. **Install dependencies:**
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   \`\`\`

3. **Setup MySQL database:**
   \`\`\`bash
   mysql -u root -p -e "CREATE DATABASE ecommerce_db;"
   mysql -u root -p ecommerce_db < database/schema.sql
   \`\`\`

4. **Load sample data:**
   \`\`\`bash
   python scripts/load_data.py
   \`\`\`

5. **Start backend server:**
   \`\`\`bash
   python api/main.py
   \`\`\`

#### Conversation Backend Setup

1. **Navigate to conversation backend directory:**
   \`\`\`bash
   cd conversation-backend/conversation_backend
   \`\`\`

2. **Install dependencies:**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Setup database:**
   \`\`\`bash
   python scripts/setup_database.py
   \`\`\`

4. **Start the server:**
   \`\`\`bash
   python scripts/run_server.py
   \`\`\`

#### Frontend Setup

1. **Navigate to frontend directory:**
   \`\`\`bash
   cd frontend
   \`\`\`

2. **Install dependencies:**
   \`\`\`bash
   npm install
   \`\`\`

3. **Start development server:**
   \`\`\`bash
   npm run dev
   \`\`\`

## 📊 API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /distribution-centers` - Distribution centers
- `GET /users` - User management
- `GET /products` - Product catalog
- `GET /orders` - Order management

### AI & Analytics
- `POST /ai/recommendations` - Personalized recommendations
- `GET /analytics/sales-summary` - Sales analytics
- `GET /analytics/top-products` - Top-selling products

### Conversation Backend API Endpoints

#### Authentication
- `POST /api/auth/token/` - Get authentication token

#### User Profiles
- `GET /api/profiles/me/` - Get current user profile
- `GET /api/profiles/` - List all profiles (admin only)

#### Conversation Sessions
- `GET /api/sessions/` - List user's conversation sessions
- `POST /api/sessions/` - Create new conversation session
- `GET /api/sessions/{session_id}/` - Get specific session with messages
- `POST /api/sessions/{session_id}/add_message/` - Add message to session
- `GET /api/sessions/{session_id}/messages/` - Get session messages
- `POST /api/sessions/{session_id}/archive/` - Archive session
- `GET /api/sessions/stats/` - Get user's conversation statistics

#### Messages
- `GET /api/messages/` - List user's messages
- `POST /api/messages/{message_id}/react/` - Add reaction to message
- `GET /api/messages/{message_id}/reactions/` - Get message reactions

#### Analytics
- `GET /api/analytics/` - Get conversation analytics
- `GET /api/analytics/summary/` - Get analytics summary

#### Templates
- `GET /api/templates/` - List conversation templates
- `POST /api/templates/{template_id}/use_template/` - Create session from template

## 🗄️ Database Schema

### FastAPI Backend
The MySQL database includes:
- `distribution_centers` - Warehouse locations
- `users` - Customer information
- `products` - Product catalog
- `orders` - Order tracking
- `order_items` - Order line items
- `inventory_items` - Inventory management

### Conversation Backend
The system uses a comprehensive database schema designed for scalability and performance:

#### Core Models
1. **UserProfile** - Extended user information and conversation statistics
2. **ConversationSession** - Distinct conversation sessions with metadata
3. **Message** - Individual messages with chronological ordering
4. **ConversationAnalytics** - Session analytics and metrics
5. **MessageReaction** - User reactions to AI responses
6. **ConversationTemplate** - Reusable conversation templates

## 🤖 AI Recommendation Engine

The system provides intelligent product recommendations using:

1. **Collaborative Filtering**: Analyzes user behavior patterns
2. **Content-Based Filtering**: Matches product attributes
3. **Hybrid Approach**: Combines both methods for accuracy

## 🔧 Configuration

### Environment Variables

**FastAPI Backend:**
- `DB_HOST` - MySQL host (default: localhost)
- `DB_NAME` - Database name (default: ecommerce_db)
- `DB_USER` - Database user (default: root)
- `DB_PASSWORD` - Database password (default: password)
- `DB_PORT` - Database port (default: 3306)

**Conversation Backend:**
- `DJANGO_SECRET_KEY` - Secret key for Django
- `DJANGO_DEBUG` - Debug mode (default: False)
- `DATABASE_URL` - Database URL (default: SQLite)

**Frontend:**
- Automatically configured to connect to backend at `http://localhost:8000`

## 🧪 Development

### FastAPI Backend Development
\`\`\`bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python api/main.py
\`\`\`

### Conversation Backend Development
\`\`\`bash
cd conversation-backend/conversation_backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
\`\`\`

### Frontend Development
\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

### Database Management
\`\`\`bash
# Connect to MySQL
mysql -u root -p ecommerce_db

# Reset database
mysql -u root -p ecommerce_db < backend/database/schema.sql
python backend/scripts/load_data.py
\`\`\`

### Conversation Backend Database Management
\`\`\`bash
# Connect to Django database
python manage.py dbshell

# Reset database
python manage.py migrate
python manage.py loaddata initial_data.json
\`\`\`

## 🚀 Production Deployment

1. **Set production environment variables**
2. **Use production database credentials**
3. **Configure proper CORS origins**
4. **Set up SSL/TLS termination**
5. **Use production-ready web servers**

### Production Docker
\`\`\`bash
docker-compose -f docker-compose.prod.yml up -d
\`\`\`

### Conversation Backend Production Deployment
\`\`\`bash
export DJANGO_SECRET_KEY="your-secret-key"
export DJANGO_DEBUG=False
export DATABASE_URL="mysql://user:pass@host:port/dbname"
gunicorn conversation_backend.wsgi:application --bind 0.0.0.0:8000
\`\`\`

## 📈 Monitoring & Analytics

The dashboard provides:
- Real-time sales metrics
- Customer analytics
- Product performance
- Revenue tracking
- AI recommendation insights
- Conversation analytics and metrics
- User behavior tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**MySQL Connection Error:**
\`\`\`bash
# Check MySQL service
sudo systemctl status mysql
# Restart MySQL
sudo systemctl restart mysql
\`\`\`

**Port Already in Use:**
\`\`\`bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
\`\`\`

**Permission Denied on setup.sh:**
\`\`\`bash
chmod +x backend/scripts/setup.sh
\`\`\`

For more help, check the logs:
\`\`\`bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs conversation-backend
\`\`\`

## 🎯 Features Roadmap

- [ ] User authentication and authorization
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Mobile app support
- [ ] Multi-language support
- [ ] Payment gateway integration
- [ ] Inventory management system
- [ ] Advanced AI recommendations
- [ ] Enhanced conversation management features
- [ ] Improved user interface for conversation history
