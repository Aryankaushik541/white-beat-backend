# 📚 White Beat API Documentation

Complete API reference for the White Beat messaging platform with WhatsApp-like features including groups, calls, status updates, and more.

**Base URL:** `http://localhost:8000/api` (development)

---

## 📋 Table of Contents

- [Authentication](#-authentication)
- [User Management](#-user-management)
- [Messaging](#-messaging)
- [Groups](#-groups)
- [Calls](#-calls)
- [Status Updates](#-status-updates)
- [Contacts](#-contacts)
- [Admin](#-admin)
- [Health Check](#-health-check)

---

## 🔐 Authentication

### Signup
Create a new user account.

```http
POST /api/signup/
Content-Type: application/json

{
  "username": "john",
  "password": "password123",
  "email": "john@example.com",
  "phone_number": "+1234567890"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "role": "user",
  "username": "john",
  "email": "john@example.com",
  "user_id": 1,
  "message": "Account created successfully!"
}
```

### Login
Authenticate and get user profile.

```http
POST /api/login/
Content-Type: application/json

{
  "username": "john",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "role": "user",
  "username": "john",
  "email": "john@example.com",
  "user_id": 1,
  "is_admin_group": false,
  "profile": {
    "avatar": "https://example.com/avatar.jpg",
    "status": "Hey there! I am using White Beat",
    "phone_number": "+1234567890",
    "bio": "Software developer"
  }
}
```

### Logout
Update online status and log out.

```http
POST /api/logout/
Content-Type: application/json

{
  "username": "john"
}
```

---

## 👥 User Management

### Get Users
List all users (with optional search).

```http
GET /api/users/?username=john&search=jane
```

**Response:** `200 OK`
```json
{
  "success": true,
  "users": [
    {
      "id": 2,
      "username": "jane",
      "full_name": "Jane Doe",
      "avatar": "https://example.com/jane.jpg",
      "status": "Available",
      "is_online": true,
      "last_seen": "2026-01-21T22:30:00Z"
    }
  ],
  "count": 1
}
```

### Get User Profile
Get detailed user profile.

```http
GET /api/user-profile/?username=jane
```

### Update Profile
Update user profile information.

```http
POST /api/update-profile/
Content-Type: application/json

{
  "username": "john",
  "avatar": "https://example.com/new-avatar.jpg",
  "status": "Busy",
  "bio": "Full stack developer",
  "profile_photo_privacy": "contacts"
}
```

---

## 💬 Messaging

### Get Conversations
List all conversations for a user.

```http
GET /api/conversations/?username=john
```

**Response:** `200 OK`
```json
{
  "success": true,
  "conversations": [
    {
      "id": 1,
      "other_user": {
        "username": "jane",
        "avatar": "https://example.com/jane.jpg",
        "is_online": true
      },
      "last_message": {
        "content": "Hey!",
        "created_at": "2026-01-21T22:30:00Z",
        "sender": "jane"
      },
      "unread_count": 2,
      "is_archived": false,
      "is_muted": false
    }
  ]
}
```

### Get Messages
Get messages in a conversation (with pagination).

```http
GET /api/messages/?username=john&other_username=jane&limit=50&offset=0
```

**Response:** `200 OK`
```json
{
  "success": true,
  "conversation_id": 1,
  "messages": [
    {
      "id": 1,
      "sender": "john",
      "message_type": "text",
      "content": "Hello!",
      "is_read": true,
      "reactions": [
        {"user": "jane", "type": "like", "emoji": "👍"}
      ],
      "created_at": "2026-01-21T22:25:00Z",
      "is_mine": true
    }
  ],
  "has_more": false
}
```

### Send Message
Send text, image, video, or other media.

```http
POST /api/send-message/
Content-Type: application/json

{
  "sender": "john",
  "receiver": "jane",
  "content": "Hello!",
  "message_type": "text",
  "media_url": "https://example.com/image.jpg",
  "reply_to": 5
}
```

**Message Types:**
- `text` - Plain text
- `image` - Image file
- `video` - Video file
- `audio` - Voice message
- `document` - Document file
- `location` - Location coordinates
- `contact` - Contact card
- `sticker` - Sticker/emoji
- `gif` - Animated GIF

### Delete Message
Delete for self or everyone.

```http
POST /api/delete-message/
Content-Type: application/json

{
  "message_id": 10,
  "username": "john",
  "delete_for_everyone": true
}
```

### Edit Message
Edit a sent message.

```http
POST /api/edit-message/
Content-Type: application/json

{
  "message_id": 10,
  "username": "john",
  "content": "Hello there!"
}
```

### React to Message
Add emoji reaction.

```http
POST /api/react-message/
Content-Type: application/json

{
  "message_id": 10,
  "username": "john",
  "reaction_type": "like"
}
```

**Reaction Types:** `like` 👍, `love` ❤️, `laugh` 😂, `wow` 😮, `sad` 😢, `angry` 😠

### Mark as Read
Mark all messages in conversation as read.

```http
POST /api/mark-as-read/
Content-Type: application/json

{
  "username": "john",
  "conversation_id": 1
}
```

---

## 👥 Groups

### Create Group
Create a new group chat.

```http
POST /api/create-group/
Content-Type: application/json

{
  "creator": "john",
  "name": "Project Team",
  "description": "Team collaboration",
  "avatar": "https://example.com/group.jpg",
  "members": ["jane", "bob", "alice"]
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "group": {
    "id": 1,
    "name": "Project Team",
    "member_count": 4,
    "created_at": "2026-01-21T22:40:00Z"
  }
}
```

### Get Groups
List all groups for a user.

```http
GET /api/groups/?username=john
```

### Get Group Messages
Get messages in a group.

```http
GET /api/group-messages/?group_id=1&limit=50&offset=0
```

### Add Group Member
Add member to group (admin only).

```http
POST /api/add-group-member/
Content-Type: application/json

{
  "group_id": 1,
  "admin": "john",
  "member": "charlie"
}
```

### Remove Group Member
Remove member from group (admin only).

```http
POST /api/remove-group-member/
Content-Type: application/json

{
  "group_id": 1,
  "admin": "john",
  "member": "charlie"
}
```

---

## 📞 Calls

### Initiate Call
Start voice or video call.

```http
POST /api/initiate-call/
Content-Type: application/json

{
  "caller": "john",
  "receiver": "jane",
  "call_type": "video"
}
```

**Call Types:** `audio`, `video`

**Response:** `201 Created`
```json
{
  "success": true,
  "call": {
    "id": 1,
    "room_id": "550e8400-e29b-41d4-a716-446655440000",
    "call_type": "video",
    "status": "initiated"
  }
}
```

### Update Call Status
Update call status.

```http
POST /api/update-call-status/
Content-Type: application/json

{
  "call_id": 1,
  "status": "ongoing"
}
```

**Call Status:** `initiated`, `ringing`, `ongoing`, `completed`, `missed`, `rejected`, `failed`

### Get Call History
Get user's call history.

```http
GET /api/call-history/?username=john
```

**Response:** `200 OK`
```json
{
  "success": true,
  "calls": [
    {
      "id": 1,
      "call_type": "video",
      "status": "completed",
      "caller": "john",
      "receiver": "jane",
      "duration": 300,
      "started_at": "2026-01-21T22:50:00Z",
      "is_incoming": false
    }
  ]
}
```

---

## 📸 Status Updates

### Create Status
Create 24-hour status update.

```http
POST /api/create-status/
Content-Type: application/json

{
  "username": "john",
  "status_type": "text",
  "content": "Having a great day!",
  "background_color": "#FF5733",
  "privacy": "everyone"
}
```

**Status Types:** `text`, `image`, `video`

**Privacy:** `everyone`, `contacts`, `selected`, `except`

### Get Statuses
Get active statuses from contacts.

```http
GET /api/statuses/?username=john
```

**Response:** `200 OK`
```json
{
  "success": true,
  "statuses": [
    {
      "user": {
        "username": "jane",
        "avatar": "https://example.com/jane.jpg"
      },
      "statuses": [
        {
          "id": 2,
          "status_type": "image",
          "media_url": "https://example.com/status.jpg",
          "created_at": "2026-01-21T20:00:00Z",
          "expires_at": "2026-01-22T20:00:00Z",
          "has_viewed": false,
          "view_count": 15
        }
      ]
    }
  ]
}
```

### View Status
Mark status as viewed.

```http
POST /api/view-status/
Content-Type: application/json

{
  "status_id": 2,
  "username": "john"
}
```

---

## 📇 Contacts

### Add Contact
Add user to contacts.

```http
POST /api/add-contact/
Content-Type: application/json

{
  "username": "john",
  "contact": "jane",
  "nickname": "Janey"
}
```

### Get Contacts
Get user's contact list.

```http
GET /api/contacts/?username=john
```

**Response:** `200 OK`
```json
{
  "success": true,
  "contacts": [
    {
      "username": "jane",
      "nickname": "Janey",
      "avatar": "https://example.com/jane.jpg",
      "is_online": true,
      "is_blocked": false,
      "is_favorite": true
    }
  ]
}
```

---

## 🔧 Admin

### Verify Admin
Check if user is admin.

```http
POST /api/verify-admin/
Content-Type: application/json

{
  "username": "admin"
}
```

### Make Admin
Add user to Admin group.

```http
POST /api/make-admin/
Content-Type: application/json

{
  "admin_username": "admin",
  "admin_password": "admin123",
  "target_username": "john"
}
```

### Remove Admin
Remove user from Admin group.

```http
POST /api/remove-admin/
Content-Type: application/json

{
  "admin_username": "admin",
  "admin_password": "admin123",
  "target_username": "john"
}
```

### Admin Statistics
Get dashboard statistics.

```http
GET /api/admin/stats/
```

**Response:** `200 OK`
```json
{
  "total_users": 150,
  "total_messages": 5678,
  "total_groups": 23,
  "total_calls": 89,
  "total_statuses": 34,
  "active_sessions": 45,
  "revenue": 11.36,
  "user_growth": [10, 15, 20, 18, 25, 30],
  "api_usage": [80, 65, 90, 75, 85, 70]
}
```

---

## ❤️ Health Check

### Service Health
Check service status and features.

```http
GET /api/health/
```

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "service": "White Beat Backend - Full Featured Chat",
  "database_connected": true,
  "features": {
    "user_to_user_chat": true,
    "group_chat": true,
    "voice_calls": true,
    "video_calls": true,
    "status_updates": true,
    "media_messages": true,
    "message_reactions": true,
    "contacts": true
  },
  "stats": {
    "total_users": 150,
    "total_messages": 5678,
    "total_groups": 23,
    "total_calls": 89,
    "active_statuses": 34
  }
}
```

---

## 🚀 Quick Start Examples

### JavaScript/Fetch
```javascript
// Login
const login = await fetch('http://localhost:8000/api/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'john', password: 'pass123' })
});

// Send message
const sendMsg = await fetch('http://localhost:8000/api/send-message/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sender: 'john',
    receiver: 'jane',
    content: 'Hello!',
    message_type: 'text'
  })
});
```

### Python/Requests
```python
import requests

# Login
response = requests.post('http://localhost:8000/api/login/', 
    json={'username': 'john', 'password': 'pass123'})

# Get conversations
conversations = requests.get('http://localhost:8000/api/conversations/',
    params={'username': 'john'})
```

### cURL
```bash
# Signup
curl -X POST http://localhost:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"pass123","email":"john@example.com"}'

# Get users
curl "http://localhost:8000/api/users/?username=john"
```

---

## 📝 Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid credentials |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

---

## 🔒 Best Practices

1. **Pagination**: Use `limit` and `offset` for large datasets
2. **Real-time**: Implement WebSocket for live updates
3. **Media**: Upload to CDN, send URLs only
4. **Caching**: Cache user profiles and group info
5. **Security**: Validate permissions before operations
6. **Error Handling**: Always check response status

---

## 📞 Support

- **GitHub**: [Aryankaushik541/white-beat-backend](https://github.com/Aryankaushik541/white-beat-backend)
- **Frontend**: [white-beat-frontend](https://github.com/Aryankaushik541/white-beat-frontend)

---

**Last Updated:** 2026-01-21 | **Version:** 2.0.0
