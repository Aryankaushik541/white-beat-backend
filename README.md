# 💬 White Beat Backend - User Chat System

<div align="center">

![Django](https://img.shields.io/badge/Django-4.2-092e20?style=for-the-badge&logo=django)
![REST API](https://img.shields.io/badge/REST-API-009688?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Django REST API for User-to-User Messaging (WhatsApp-like)**

[Frontend Repo](https://github.com/Aryankaushik541/white-beat-frontend) • [API Docs](#-api-endpoints) • [Deploy Guide](#-deployment)

</div>

---

## ✨ Features

- 🔐 **Authentication API** - Smart login with admin/user role detection
- 💬 **User-to-User Chat** - WhatsApp-like messaging system
- 👥 **User Management** - List users, view profiles, online status
- 📊 **Admin Analytics** - Dashboard statistics API
- 🔒 **CORS Enabled** - Ready for React frontend
- 🚀 **RESTful Design** - Clean, documented endpoints
- ✅ **Health Check** - Service monitoring endpoint
- 🧪 **Unit Tests** - Comprehensive test coverage

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip and virtualenv

### Installation

```bash
# Clone repository
git clone https://github.com/Aryankaushik541/white-beat-backend.git
cd white-beat-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (for Django admin)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit **http://localhost:8000/api/health/** to verify installation

---

## 📡 API Endpoints

### Authentication

#### Signup
```http
POST /api/signup/
Content-Type: application/json

{
  "username": "john",
  "password": "password123",
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "role": "user",
  "username": "john",
  "email": "john@example.com",
  "user_id": 1,
  "message": "Account created successfully! You can now login."
}
```

#### Login
```http
POST /api/login/
Content-Type: application/json

{
  "username": "john",
  "password": "password123"
}
```

**Response:**
```json
{
  "role": "user",
  "username": "john",
  "email": "john@example.com",
  "message": "User login successful",
  "user_id": 1,
  "is_admin_group": false
}
```

---

### User Management

#### Get All Users
```http
GET /api/users/?username=john
```

**Response:**
```json
{
  "success": true,
  "users": [
    {
      "id": 2,
      "username": "jane",
      "email": "jane@example.com",
      "status": "Hey there! I am using White Beat",
      "is_online": true,
      "last_activity": "2026-01-21T22:30:00Z"
    }
  ],
  "count": 1
}
```

---

### Messaging

#### Get Conversations
```http
GET /api/conversations/?username=john
```

**Response:**
```json
{
  "success": true,
  "conversations": [
    {
      "id": 1,
      "other_user": {
        "id": 2,
        "username": "jane",
        "email": "jane@example.com",
        "status": "Available",
        "is_online": true
      },
      "last_message": {
        "content": "Hey, how are you?",
        "created_at": "2026-01-21T22:30:00Z",
        "sender": "jane"
      },
      "unread_count": 2,
      "updated_at": "2026-01-21T22:30:00Z"
    }
  ],
  "count": 1
}
```

#### Get Messages
```http
GET /api/messages/?username=john&other_username=jane
```

**Response:**
```json
{
  "success": true,
  "conversation_id": 1,
  "messages": [
    {
      "id": 1,
      "sender": "john",
      "receiver": "jane",
      "content": "Hello!",
      "is_read": true,
      "created_at": "2026-01-21T22:25:00Z",
      "is_mine": true
    },
    {
      "id": 2,
      "sender": "jane",
      "receiver": "john",
      "content": "Hey, how are you?",
      "is_read": false,
      "created_at": "2026-01-21T22:30:00Z",
      "is_mine": false
    }
  ],
  "count": 2
}
```

#### Send Message
```http
POST /api/send-message/
Content-Type: application/json

{
  "sender": "john",
  "receiver": "jane",
  "content": "I'm doing great, thanks!"
}
```

**Response:**
```json
{
  "success": true,
  "message": {
    "id": 3,
    "sender": "john",
    "receiver": "jane",
    "content": "I'm doing great, thanks!",
    "created_at": "2026-01-21T22:35:00Z",
    "is_read": false
  }
}
```

#### Mark as Read
```http
POST /api/mark-as-read/
Content-Type: application/json

{
  "username": "john",
  "conversation_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "marked_read": 2
}
```

---

### Admin Endpoints

#### Get Statistics
```http
GET /api/admin/stats/
```

**Response:**
```json
{
  "total_users": 150,
  "api_calls_today": 1234,
  "active_sessions": 45,
  "total_messages": 5678,
  "revenue": 11.36,
  "user_growth": [10, 15, 20, 18, 25, 30],
  "api_usage": [80, 65, 90, 75, 85, 70],
  "recent_users": [...],
  "recent_logs": [...]
}
```

#### Make Admin
```http
POST /api/make-admin/
Content-Type: application/json

{
  "admin_username": "admin",
  "admin_password": "admin123",
  "target_username": "john"
}
```

#### Remove Admin
```http
POST /api/remove-admin/
Content-Type: application/json

{
  "admin_username": "admin",
  "admin_password": "admin123",
  "target_username": "john"
}
```

---

### Health Check

#### Check Service Status
```http
GET /api/health/
```

**Response:**
```json
{
  "status": "healthy",
  "service": "White Beat Backend - User Chat",
  "database_connected": true,
  "admin_group_exists": true,
  "features": {
    "user_to_user_chat": true,
    "group_based_admin": true,
    "signup": true
  },
  "stats": {
    "total_users": 150,
    "total_messages": 5678,
    "total_conversations": 89,
    "admin_users": 3
  }
}
```

---

## 📁 Project Structure

```
white-beat-backend/
├── whitebeat_backend/
│   ├── __init__.py
│   ├── settings.py          # Django settings with CORS
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI config
│   └── asgi.py              # ASGI config
├── api/
│   ├── __init__.py
│   ├── views.py             # API endpoints
│   ├── urls.py              # API routes
│   ├── models.py            # Database models (User, Conversation, Message)
│   ├── admin.py             # Django admin config
│   └── tests.py             # Unit tests
├── manage.py
├── requirements.txt
├── Procfile                 # Heroku deployment
├── runtime.txt              # Python version
├── .gitignore
└── README.md
```

---

## 🗄️ Database Models

### UserProfile
- Extended user information
- Online status tracking
- Message count
- Custom status message

### Conversation
- Links two users
- Tracks last update time
- Ensures unique user pairs

### Message
- Individual chat messages
- Read/unread status
- Sender and receiver tracking
- Timestamp

### APILog
- Request logging
- Performance monitoring
- User activity tracking

### SystemStats
- Daily statistics
- User growth metrics
- Revenue tracking

---

## 🛠️ Tech Stack

- **Django 4.2** - Web framework
- **Django REST Framework** - API toolkit
- **django-cors-headers** - CORS support
- **SQLite** - Development database
- **PostgreSQL** - Production database (optional)
- **Gunicorn** - Production WSGI server

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 🚀 Deployment

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### Environment Variables (Heroku)
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
```

---

## 📝 License

MIT License - see LICENSE file for details

---

## 👨‍💻 Author

**Aryan Kaushik**
- GitHub: [@Aryankaushik541](https://github.com/Aryankaushik541)
- Frontend: [white-beat-frontend](https://github.com/Aryankaushik541/white-beat-frontend)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<div align="center">

**Made with ❤️ using Django**

</div>
