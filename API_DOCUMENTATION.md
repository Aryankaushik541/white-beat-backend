# 📡 White Beat API Documentation

Complete API reference for the White Beat backend.

**Base URL:** `http://localhost:8000/api` (development)

---

## 📋 Table of Contents

- [Authentication](#authentication)
- [AI Chat](#ai-chat)
- [Admin](#admin)
- [Health Check](#health-check)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

---

## 🔐 Authentication

### Login

Authenticate users and determine their role (admin or user).

**Endpoint:** `POST /api/login/`

**Request:**
```http
POST /api/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Success Response (Admin):**
```json
{
  "role": "admin",
  "username": "admin",
  "message": "Admin login successful"
}
```
- **Status Code:** `200 OK`

**Success Response (User):**
```json
{
  "role": "user",
  "username": "testuser",
  "message": "User login successful"
}
```
- **Status Code:** `200 OK`

**Error Response:**
```json
{
  "error": "Username and password are required"
}
```
- **Status Code:** `400 Bad Request`

**Credentials:**
- **Admin:** username=`admin`, password=`admin123`
- **User:** Any other username/password combination

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/api/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});
const data = await response.json();
console.log(data.role); // "admin" or "user"
```

---

## 🤖 AI Chat

### Send Message

Send a message to the AI and receive a response.

**Endpoint:** `POST /api/chat/`

**Request:**
```http
POST /api/chat/
Content-Type: application/json

{
  "prompt": "What is artificial intelligence?"
}
```

**Success Response:**
```json
{
  "response": "Artificial intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, and self-correction.",
  "model": "gpt-3.5-turbo"
}
```
- **Status Code:** `200 OK`

**Response (No API Key Configured):**
```json
{
  "response": "OpenAI API not configured. Your message: \"What is artificial intelligence?\". Please add OPENAI_API_KEY to .env file."
}
```
- **Status Code:** `200 OK`

**Error Response (Missing Prompt):**
```json
{
  "error": "Prompt is required"
}
```
- **Status Code:** `400 Bad Request`

**Error Response (OpenAI Error):**
```json
{
  "error": "OpenAI API error: Rate limit exceeded"
}
```
- **Status Code:** `500 Internal Server Error`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| prompt | string | Yes | The message to send to AI |

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain quantum computing"}'
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/api/chat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'Explain quantum computing'
  })
});
const data = await response.json();
console.log(data.response);
```

**Example (Python):**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/chat/',
    json={'prompt': 'Explain quantum computing'}
)
print(response.json()['response'])
```

---

## 👨‍💼 Admin

### Get Statistics

Retrieve admin dashboard statistics.

**Endpoint:** `GET /api/admin/stats/`

**Request:**
```http
GET /api/admin/stats/
```

**Success Response:**
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
- **Status Code:** `200 OK`

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| total_users | integer | Total registered users |
| api_calls_today | integer | Number of API calls today |
| active_sessions | integer | Currently active sessions |
| revenue | integer | Total revenue in dollars |
| user_growth | array | User growth data (6 data points) |
| api_usage | array | API usage data (6 data points) |

**Example (cURL):**
```bash
curl http://localhost:8000/api/admin/stats/
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/api/admin/stats/');
const stats = await response.json();
console.log(`Total Users: ${stats.total_users}`);
```

---

## 🏥 Health Check

### Check Service Status

Verify the API is running and check OpenAI configuration.

**Endpoint:** `GET /api/health/`

**Request:**
```http
GET /api/health/
```

**Success Response:**
```json
{
  "status": "healthy",
  "service": "White Beat Backend",
  "openai_configured": true
}
```
- **Status Code:** `200 OK`

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| status | string | Service status ("healthy") |
| service | string | Service name |
| openai_configured | boolean | Whether OpenAI API key is set |

**Example (cURL):**
```bash
curl http://localhost:8000/api/health/
```

**Use Cases:**
- Monitoring service availability
- Checking deployment status
- Verifying OpenAI configuration

---

## ⚠️ Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "error": "Error message description"
}
```

### HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Missing or invalid parameters |
| 401 | Unauthorized | Invalid credentials (future) |
| 404 | Not Found | Endpoint doesn't exist |
| 500 | Internal Server Error | Server or OpenAI API error |

### Common Errors

**Missing Required Field:**
```json
{
  "error": "Prompt is required"
}
```

**OpenAI API Error:**
```json
{
  "error": "OpenAI API error: Rate limit exceeded"
}
```

**Invalid Endpoint:**
```json
{
  "detail": "Not found."
}
```

---

## 🚦 Rate Limiting

Currently, there are **no rate limits** on the API endpoints.

**Recommendations for Production:**
- Implement rate limiting (e.g., 100 requests/hour per IP)
- Use Django REST Framework throttling
- Monitor OpenAI API usage to avoid rate limits

**Example Rate Limit Configuration:**
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

---

## 🔒 CORS Configuration

The API accepts requests from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

**To add production URLs:**
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-frontend-domain.com",
]
```

---

## 📊 Request/Response Examples

### Complete Chat Flow

**1. User logs in:**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"pass123"}'
```

**Response:**
```json
{"role":"user","username":"testuser","message":"User login successful"}
```

**2. User sends chat message:**
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello, how are you?"}'
```

**Response:**
```json
{
  "response": "Hello! I'm doing well, thank you for asking. How can I assist you today?",
  "model": "gpt-3.5-turbo"
}
```

### Complete Admin Flow

**1. Admin logs in:**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Response:**
```json
{"role":"admin","username":"admin","message":"Admin login successful"}
```

**2. Admin fetches stats:**
```bash
curl http://localhost:8000/api/admin/stats/
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

## 🧪 Testing

### Using Postman

1. **Import Collection:**
   - Create new collection "White Beat API"
   - Add requests for each endpoint

2. **Set Environment:**
   - Variable: `base_url`
   - Value: `http://localhost:8000/api`

3. **Test Endpoints:**
   - Login: `{{base_url}}/login/`
   - Chat: `{{base_url}}/chat/`
   - Stats: `{{base_url}}/admin/stats/`
   - Health: `{{base_url}}/health/`

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Test login
login_response = requests.post(
    f"{BASE_URL}/login/",
    json={"username": "admin", "password": "admin123"}
)
print(login_response.json())

# Test chat
chat_response = requests.post(
    f"{BASE_URL}/chat/",
    json={"prompt": "Hello!"}
)
print(chat_response.json())

# Test stats
stats_response = requests.get(f"{BASE_URL}/admin/stats/")
print(stats_response.json())

# Test health
health_response = requests.get(f"{BASE_URL}/health/")
print(health_response.json())
```

---

## 🔧 Development

### Adding New Endpoints

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

## 📚 Additional Resources

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Frontend Repository](https://github.com/Aryankaushik541/white-beat-frontend)

---

## 🆘 Support

- 📧 [Open an Issue](https://github.com/Aryankaushik541/white-beat-backend/issues)
- 📖 [Read the README](./README.md)
- 💬 Check [Frontend Docs](https://github.com/Aryankaushik541/white-beat-frontend)

---

<div align="center">

**White Beat API - Simple, Powerful, Well-Documented**

⭐ Star the repo if this documentation helped you!

</div>