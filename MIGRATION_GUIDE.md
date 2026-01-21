# 🔄 Migration Guide: AI Chat → User-to-User Chat

This guide will help you migrate your local database from the AI chat system to the new user-to-user messaging system.

---

## ⚠️ Important Notes

1. **Backup your database** before proceeding
2. The `ChatMessage` model has been removed and replaced with `Conversation` and `Message` models
3. All AI-related code has been removed
4. OSINT features have been removed

---

## 📋 Migration Steps

### Step 1: Backup Current Database

```bash
# Backup your SQLite database
cp db.sqlite3 db.sqlite3.backup

# Or if using PostgreSQL
pg_dump your_database > backup.sql
```

### Step 2: Pull Latest Changes

```bash
git pull origin main
```

### Step 3: Remove Old Migrations (Optional)

If you want a clean migration:

```bash
# Remove old migration files (keep __init__.py)
rm api/migrations/0*.py

# Or manually delete migration files except __init__.py
```

### Step 4: Create New Migrations

```bash
# Create migrations for the new models
python manage.py makemigrations api

# You should see:
# - Create model Conversation
# - Create model Message
# - Add field avatar to userprofile
# - Add field status to userprofile
# - Remove model ChatMessage
```

### Step 5: Apply Migrations

```bash
# Apply the migrations
python manage.py migrate

# You should see:
# - Running migrations:
#   - Applying api.000X_...
```

### Step 6: Verify Database

```bash
# Open Django shell
python manage.py shell

# Check models
from api.models import Conversation, Message, UserProfile
print(f"Conversations: {Conversation.objects.count()}")
print(f"Messages: {Message.objects.count()}")
print(f"Users: {UserProfile.objects.count()}")
```

### Step 7: Test the API

```bash
# Start the server
python manage.py runserver

# Test health endpoint
curl http://localhost:8000/api/health/

# Expected response:
# {
#   "status": "healthy",
#   "service": "White Beat Backend - User Chat",
#   "features": {
#     "user_to_user_chat": true,
#     ...
#   }
# }
```

---

## 🆕 New API Endpoints

### User Management
- `GET /api/users/?username=<username>` - Get all users
- `GET /api/conversations/?username=<username>` - Get user's conversations
- `GET /api/messages/?username=<user>&other_username=<other>` - Get messages

### Messaging
- `POST /api/send-message/` - Send a message
- `POST /api/mark-as-read/` - Mark messages as read

### Removed Endpoints
- ❌ `POST /api/chat/` - AI chat (removed)
- ❌ `POST /api/osint/` - OSINT lookup (removed)

---

## 🗑️ Removed Files

The following files are no longer needed and can be deleted:

```bash
# Remove AI and OSINT engine files
rm api/ai_engine.py
rm api/osint_engine.py

# Remove debug views if not needed
rm api/views_debug.py
```

---

## 🔧 Environment Variables

You no longer need:
- ❌ `OPENAI_API_KEY` - Not required anymore

Keep:
- ✅ `SECRET_KEY` - Django secret key
- ✅ `DEBUG` - Debug mode
- ✅ `ALLOWED_HOSTS` - Allowed hosts

---

## 📊 Database Schema Changes

### Removed Models
- `ChatMessage` - AI chat messages

### New Models
- `Conversation` - User-to-user conversations
- `Message` - Individual messages in conversations

### Updated Models
- `UserProfile` - Added `avatar` and `status` fields

---

## 🐛 Troubleshooting

### Issue: Migration conflicts

```bash
# Reset migrations (WARNING: This will delete all data)
python manage.py migrate api zero
python manage.py makemigrations api
python manage.py migrate
```

### Issue: "Table already exists"

```bash
# Fake the migration
python manage.py migrate --fake api
```

### Issue: Missing dependencies

```bash
# Reinstall requirements
pip install -r requirements.txt
```

### Issue: Admin panel errors

```bash
# Clear cache and restart
python manage.py collectstatic --clear
python manage.py runserver
```

---

## ✅ Verification Checklist

- [ ] Database backup created
- [ ] Latest code pulled from GitHub
- [ ] Old migrations removed (optional)
- [ ] New migrations created
- [ ] Migrations applied successfully
- [ ] Server starts without errors
- [ ] Health endpoint returns correct response
- [ ] Can create new users via signup
- [ ] Can login with existing users
- [ ] Can send messages between users
- [ ] Admin panel accessible
- [ ] New models visible in admin

---

## 📝 Testing the New System

### 1. Create Test Users

```bash
# Via Django shell
python manage.py shell

from django.contrib.auth.models import User
from api.models import UserProfile

# Create user 1
user1 = User.objects.create_user('alice', 'alice@test.com', 'password123')
UserProfile.objects.create(user=user1, status='Available')

# Create user 2
user2 = User.objects.create_user('bob', 'bob@test.com', 'password123')
UserProfile.objects.create(user=user2, status='Busy')
```

### 2. Test Messaging

```bash
# Send message via API
curl -X POST http://localhost:8000/api/send-message/ \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "alice",
    "receiver": "bob",
    "content": "Hello Bob!"
  }'

# Get messages
curl "http://localhost:8000/api/messages/?username=alice&other_username=bob"
```

### 3. Test Conversations

```bash
# Get conversations for alice
curl "http://localhost:8000/api/conversations/?username=alice"
```

---

## 🎉 Success!

If all steps completed successfully, you now have a fully functional user-to-user chat system!

### Next Steps:
1. Update your frontend to use the new API endpoints
2. Test all features thoroughly
3. Deploy to production when ready

---

## 📞 Need Help?

If you encounter any issues:
1. Check the error logs: `python manage.py runserver` output
2. Verify database state: `python manage.py dbshell`
3. Review migration files: `api/migrations/`
4. Check Django admin: `http://localhost:8000/admin/`

---

**Happy Coding! 🚀**
