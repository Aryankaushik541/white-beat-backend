# White Beat Backend

Django REST API with OpenAI integration for the White Beat AI Platform.

## Features

- 🔐 Authentication API
- 🤖 OpenAI Chat Integration
- 📊 Admin Analytics API
- 🔒 CORS enabled for React frontend
- 🚀 RESTful API design

## Installation

```bash
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

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/login/` - User/Admin login

### Chat
- `POST /api/chat/` - Send message to AI

### Admin
- `GET /api/admin/stats/` - Get admin statistics

## Environment Variables

Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Tech Stack

- Django 4.2
- Django REST Framework
- OpenAI API
- CORS Headers