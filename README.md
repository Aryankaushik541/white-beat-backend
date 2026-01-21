# 🚀 White Beat Backend

<div align="center">

![Django](https://img.shields.io/badge/Django-4.2-092e20?style=for-the-badge&logo=django)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=for-the-badge&logo=openai)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Django REST API with OpenAI Integration**

[Frontend Repo](https://github.com/Aryankaushik541/white-beat-frontend) • [API Docs](#-api-endpoints) • [Deploy Guide](#-deployment)

</div>

---

## ✨ Features

- 🔐 **Authentication API** - Smart login with admin/user role detection
- 🤖 **OpenAI Integration** - GPT-3.5-turbo chat completions
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
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

```bash
# Clone repository
git clone https://github.com/Aryankaushik541/white-beat-backend.git
cd white-beat-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

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

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Django Settings
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///db.sqlite3
```

### Generate Django Secret Key
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## 📡 API Endpoints

### Authentication

#### Login
```http
POST /api/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "role": "admin",
  "username": "admin",
  "message": "Admin login successful"
}
```

**Admin Credentials:**
- Username: `admin`
- Password: `admin123`
- Returns: `role: "admin"`

**User Credentials:**
- Username: Any other username
- Password: Any password
- Returns: `role: "user"`

---

### AI Chat

#### Send Message
```http
POST /api/chat/
Content-Type: application/json

{
  "prompt": "What is artificial intelligence?"
}
```

**Response:**
```json
{
  "response": "Artificial intelligence (AI) is...",
  "model": "gpt-3.5-turbo"
}
```

**Error Response (No API Key):**
```json
{
  "response": "OpenAI API not configured. Your message: \"...\". Please add OPENAI_API_KEY to .env file."
}
```

---

### Admin Statistics

#### Get Stats
```http
GET /api/admin/stats/
```

**Response:**
```json
{
  "total_users": 1234,
  "api_calls_today": 45678,
  "active_sessions": 89,
  "revenue": 12345,
  "user_growth": [60, 75, 85, 70, 90, 95],
  "api_usage": [80, 65, 90, 75, 85, 70]
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
  "service": "White Beat Backend",
  "openai_configured": true
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
│   ├── models.py            # Database models
│   ├── admin.py             # Django admin config
│   └── tests.py             # Unit tests
├── manage.py
├── requirements.txt
├── Procfile                 # Heroku deployment
├── runtime.txt              # Python version
├── .env.example
├── .gitignore
└── README.md
```

---

## 🛠️ Tech Stack

- **Django 4.2** - Web framework
- **Django REST Framework** - API toolkit
- **OpenAI API** - GPT-3.5-turbo integration
- **django-cors-headers** - CORS support
- **python-decouple** - Environment management
- **Gunicorn** - Production WSGI server
- **PostgreSQL** - Production database (optional)

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

**Test Coverage:**
- ✅ Health check endpoint
- ✅ Admin login
- ✅ User login
- ✅ Admin statistics
- ✅ Chat endpoint (mocked)

---

## 🌐 Deployment

### Heroku

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create white-beat-backend

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set OPENAI_API_KEY="your-openai-key"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="white-beat-backend.herokuapp.com"

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variables in Railway dashboard
```

### Render

1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn whitebeat_backend.wsgi:application`
5. Add environment variables
6. Deploy

---

## 🔒 CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:3000` (React dev server)
- `http://127.0.0.1:3000`

To add production frontend URL, update `settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-frontend-domain.com",
]
```

---

## 📊 Django Admin

Access the Django admin panel at `/admin/`:

```bash
# Create superuser
python manage.py createsuperuser

# Visit http://localhost:8000/admin/
```

---

## 🔧 Development

### Add New Endpoint

1. **Create view in `api/views.py`:**
```python
@api_view(['GET'])
def my_endpoint(request):
    return Response({'message': 'Hello World'})
```

2. **Add route in `api/urls.py`:**
```python
path('my-endpoint/', views.my_endpoint, name='my_endpoint'),
```

3. **Test:**
```bash
curl http://localhost:8000/api/my-endpoint/
```

---

## 🐛 Troubleshooting

### OpenAI API Errors

**Issue:** `OpenAI API not configured`
- **Solution:** Add `OPENAI_API_KEY` to `.env` file

**Issue:** `Rate limit exceeded`
- **Solution:** Check OpenAI account usage and billing

### CORS Errors

**Issue:** `CORS policy blocked`
- **Solution:** Add frontend URL to `CORS_ALLOWED_ORIGINS` in `settings.py`

### Database Errors

**Issue:** `no such table`
- **Solution:** Run migrations: `python manage.py migrate`

---

## 📦 Dependencies

```txt
Django==4.2.7                 # Web framework
djangorestframework==3.14.0   # REST API toolkit
django-cors-headers==4.3.1    # CORS support
openai==1.6.1                 # OpenAI API client
python-decouple==3.8          # Environment variables
gunicorn==21.2.0              # Production server
psycopg2-binary==2.9.9        # PostgreSQL adapter
```

---

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Related Repositories

- **Frontend:** [white-beat-frontend](https://github.com/Aryankaushik541/white-beat-frontend)
- **Backend:** [white-beat-backend](https://github.com/Aryankaushik541/white-beat-backend)

---

## 📞 Support

- 📧 Open an issue on GitHub
- 📚 Check the [Frontend Repo](https://github.com/Aryankaushik541/white-beat-frontend)

---

<div align="center">

**Built with ❤️ using Django and OpenAI**

⭐ Star this repo if you find it helpful!

</div>