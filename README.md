# 💬 White Beat Backend - Full Featured Chat Platform

<div align="center">

![Django](https://img.shields.io/badge/Django-4.2-092e20?style=for-the-badge&logo=django)
![REST API](https://img.shields.io/badge/REST-API-009688?style=for-the-badge)
![WhatsApp](https://img.shields.io/badge/WhatsApp-Like-25D366?style=for-the-badge&logo=whatsapp)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Django REST API for Full-Featured Messaging Platform (WhatsApp + Telegram Features)**

[Frontend Repo](https://github.com/Aryankaushik541/white-beat-frontend) • [API Docs](API_DOCUMENTATION.md) • [Migration Guide](MIGRATION_GUIDE.md)

</div>

---

## ✨ Features

### 💬 Messaging
- ✅ **User-to-User Chat** - Direct messaging between users
- ✅ **Group Chat** - Create and manage group conversations
- ✅ **Media Messages** - Send images, videos, audio, documents
- ✅ **Message Reactions** - React with emojis (👍 ❤️ 😂 😮 😢 😠)
- ✅ **Reply to Messages** - Quote and reply to specific messages
- ✅ **Edit Messages** - Edit sent messages
- ✅ **Delete Messages** - Delete for self or everyone
- ✅ **Forward Messages** - Forward messages to other chats
- ✅ **Read Receipts** - Track message read status
- ✅ **Typing Indicators** - See when someone is typing

### 📞 Calls
- ✅ **Voice Calls** - One-on-one audio calls
- ✅ **Video Calls** - One-on-one video calls
- ✅ **Group Calls** - Audio/video calls in groups
- ✅ **Call History** - Track all calls with duration
- ✅ **Call Status** - Missed, rejected, completed tracking

### 📸 Status Updates
- ✅ **24-Hour Stories** - WhatsApp-like status updates
- ✅ **Text Status** - Text with custom backgrounds
- ✅ **Image Status** - Share photos as status
- ✅ **Video Status** - Share videos as status
- ✅ **View Tracking** - See who viewed your status
- ✅ **Privacy Controls** - Control who sees your status

### 👥 User Features
- ✅ **User Profiles** - Avatar, bio, status message
- ✅ **Online Status** - Real-time online/offline tracking
- ✅ **Last Seen** - Track when users were last active
- ✅ **Privacy Settings** - Control profile visibility
- ✅ **Contact Management** - Add/manage contacts
- ✅ **Block Users** - Block unwanted users
- ✅ **Favorite Contacts** - Mark favorite contacts

### 🎯 Group Features
- ✅ **Create Groups** - Create group chats
- ✅ **Group Admin** - Multiple admins per group
- ✅ **Add/Remove Members** - Manage group members
- ✅ **Group Settings** - Control who can send messages
- ✅ **Group Info** - Name, description, avatar
- ✅ **Member Permissions** - Admin-only messaging option

### 🔐 Security & Admin
- ✅ **User Authentication** - Secure login/signup
- ✅ **Role-Based Access** - Admin and user roles
- ✅ **Admin Dashboard** - Comprehensive statistics
- ✅ **API Logging** - Track all API requests
- ✅ **Privacy Controls** - Granular privacy settings

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

## 📡 API Endpoints Overview

### Authentication
- `POST /api/signup/` - Create account
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout

### User Management
- `GET /api/users/` - List all users
- `GET /api/user-profile/` - Get user profile
- `POST /api/update-profile/` - Update profile

### Messaging
- `GET /api/conversations/` - Get conversations
- `GET /api/messages/` - Get messages
- `POST /api/send-message/` - Send message
- `POST /api/delete-message/` - Delete message
- `POST /api/edit-message/` - Edit message
- `POST /api/react-message/` - React to message
- `POST /api/mark-as-read/` - Mark as read

### Groups
- `POST /api/create-group/` - Create group
- `GET /api/groups/` - Get user's groups
- `GET /api/group-messages/` - Get group messages
- `POST /api/add-group-member/` - Add member
- `POST /api/remove-group-member/` - Remove member

### Calls
- `POST /api/initiate-call/` - Start call
- `POST /api/update-call-status/` - Update call
- `GET /api/call-history/` - Get call history

### Status
- `POST /api/create-status/` - Create status
- `GET /api/statuses/` - Get statuses
- `POST /api/view-status/` - View status

### Contacts
- `POST /api/add-contact/` - Add contact
- `GET /api/contacts/` - Get contacts

### Admin
- `GET /api/admin/stats/` - Dashboard stats
- `POST /api/make-admin/` - Make user admin
- `POST /api/remove-admin/` - Remove admin

### Health
- `GET /api/health/` - Service health check

**Full API Documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## 📊 Database Models

### Core Models

#### UserProfile
Extended user information with privacy settings
- Avatar, status message, bio
- Online status, last seen
- Privacy controls
- Message count tracking

#### Conversation
One-on-one chat conversations
- Links two users
- Archive and mute options
- Last update tracking

#### Message
Individual chat messages
- Text, image, video, audio, document, etc.
- Read/unread status
- Reply, forward, edit support
- Reaction support

#### MessageReaction
Emoji reactions to messages
- 6 reaction types (like, love, laugh, wow, sad, angry)
- One reaction per user per message

### Group Models

#### Group
Group chat management
- Name, description, avatar
- Admin management
- Member management
- Group settings

#### GroupMembership
Track group members and roles
- Member join date
- Admin status

### Communication Models

#### Call
Voice and video calls
- One-on-one and group calls
- Call duration tracking
- Call status (initiated, ongoing, completed, etc.)
- WebRTC room ID

#### Status
24-hour status updates
- Text, image, video types
- Privacy controls
- View tracking
- Auto-expiry after 24 hours

#### StatusView
Track who viewed statuses
- User and timestamp

### Contact Models

#### Contact
User contact management
- Nickname support
- Block/favorite options
- Add date tracking

### System Models

#### APILog
Request logging and monitoring
- Endpoint, method, status
- Response time tracking
- User and IP tracking

#### SystemStats
Daily system statistics
- User counts
- Message, group, call counts
- Revenue tracking

---

## 🗄️ Message Types

- **text** - Plain text message
- **image** - Image file
- **video** - Video file
- **audio** - Voice message
- **document** - PDF, DOC, etc.
- **location** - GPS coordinates
- **contact** - Contact card
- **sticker** - Sticker/emoji
- **gif** - Animated GIF

---

## 🎭 Reaction Types

- **like** - 👍
- **love** - ❤️
- **laugh** - 😂
- **wow** - 😮
- **sad** - 😢
- **angry** - 😠

---

## 📞 Call Status

- **initiated** - Call started
- **ringing** - Ringing
- **ongoing** - In progress
- **completed** - Ended normally
- **missed** - Not answered
- **rejected** - Declined
- **failed** - Error occurred

---

## 🔒 Privacy Settings

- **everyone** - Visible to all
- **contacts** - Contacts only
- **selected** - Selected users
- **except** - All except selected
- **nobody** - Hidden from all

---

## 🛠️ Tech Stack

- **Django 4.2** - Web framework
- **Django REST Framework** - API toolkit
- **django-cors-headers** - CORS support
- **SQLite** - Development database
- **PostgreSQL** - Production database (optional)
- **Gunicorn** - Production WSGI server

---

## 📁 Project Structure

```
white-beat-backend/
├── whitebeat_backend/
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL config
│   ├── wsgi.py              # WSGI config
│   └── asgi.py              # ASGI config
├── api/
│   ├── models.py            # Database models
│   ├── views.py             # API endpoints
│   ├── urls.py              # API routes
│   ├── admin.py             # Django admin
│   └── tests.py             # Unit tests
├── manage.py
├── requirements.txt
├── README.md
├── API_DOCUMENTATION.md     # Full API docs
├── MIGRATION_GUIDE.md       # Migration guide
└── CHANGELOG.md             # Version history
```

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

## 📝 Example Usage

### JavaScript/Fetch
```javascript
// Login
const login = await fetch('http://localhost:8000/api/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'john', password: 'pass123' })
});

// Send message
const msg = await fetch('http://localhost:8000/api/send-message/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sender: 'john',
    receiver: 'jane',
    content: 'Hello!',
    message_type: 'text'
  })
});

// Create group
const group = await fetch('http://localhost:8000/api/create-group/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    creator: 'john',
    name: 'Team Chat',
    members: ['jane', 'bob']
  })
});
```

### Python/Requests
```python
import requests

# Signup
response = requests.post('http://localhost:8000/api/signup/', 
    json={'username': 'john', 'password': 'pass123', 'email': 'john@example.com'})

# Get conversations
conversations = requests.get('http://localhost:8000/api/conversations/',
    params={'username': 'john'})

# Initiate call
call = requests.post('http://localhost:8000/api/initiate-call/',
    json={'caller': 'john', 'receiver': 'jane', 'call_type': 'video'})
```

---

## 🎯 Roadmap

- [ ] WebSocket support for real-time messaging
- [ ] End-to-end encryption
- [ ] Voice message transcription
- [ ] Message search functionality
- [ ] File upload to cloud storage
- [ ] Push notifications
- [ ] Multi-device sync
- [ ] Backup and restore
- [ ] Broadcast messages
- [ ] Scheduled messages

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

## 📞 Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/Aryankaushik541/white-beat-backend/issues)
- Documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- Migration Guide: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

---

<div align="center">

**Made with ❤️ using Django**

⭐ Star this repo if you find it helpful!

</div>
