# 📝 Changelog

All notable changes to this project will be documented in this file.

---

## [2.0.0] - 2026-01-21

### 🎉 Major Release: User-to-User Chat System

Complete conversion from AI chat platform to WhatsApp-like user-to-user messaging system.

### ✨ Added

#### New Models
- **Conversation** - Manages chat conversations between two users
  - Unique user pairs (user1, user2)
  - Automatic timestamp tracking
  - Helper method to get other user in conversation

- **Message** - Individual chat messages
  - Sender and receiver tracking
  - Read/unread status
  - Content storage
  - Timestamp tracking

#### New API Endpoints
- `GET /api/users/` - Get list of all users for chat
- `GET /api/conversations/` - Get all conversations for a user
- `GET /api/messages/` - Get all messages in a conversation
- `POST /api/send-message/` - Send a message to another user
- `POST /api/mark-as-read/` - Mark messages as read

#### New Features
- User online/offline status tracking
- Custom user status messages
- Unread message counting
- Automatic conversation creation
- Message read receipts
- User profile avatars (URL field)

### 🔄 Changed

#### Updated Models
- **UserProfile**
  - Added `avatar` field (URLField)
  - Added `status` field (CharField, default: "Hey there! I am using White Beat")
  - Kept existing fields: role, joined_date, is_active_session, last_activity, total_messages

#### Updated API Endpoints
- `POST /api/signup/` - Enhanced with better validation
- `POST /api/login/` - Improved response format
- `GET /api/admin/stats/` - Updated to show message statistics instead of AI chat stats
- `GET /api/health/` - Updated to reflect new features

#### Updated Admin Panel
- Registered `Conversation` model with custom admin
- Registered `Message` model with custom admin
- Updated admin site title to "User Chat Administration Panel"
- Removed `ChatMessage` admin

### ❌ Removed

#### Removed Models
- **ChatMessage** - AI chat message storage (replaced by Message model)

#### Removed API Endpoints
- `POST /api/chat/` - AI chat endpoint
- `POST /api/osint/` - OSINT lookup endpoint

#### Removed Files
- `api/ai_engine.py` - Local AI engine (can be deleted)
- `api/osint_engine.py` - OSINT engine (can be deleted)

#### Removed Dependencies
- OpenAI API integration
- Transformers library requirement
- OSINT-related packages

#### Removed Environment Variables
- `OPENAI_API_KEY` - No longer needed

### 🔧 Technical Changes

#### Database Schema
- Removed `api_chatmessage` table
- Added `api_conversation` table
- Added `api_message` table
- Added `avatar` column to `api_userprofile`
- Added `status` column to `api_userprofile`

#### Code Structure
- Simplified `views.py` - removed AI/OSINT logic
- Updated `urls.py` - new messaging routes
- Updated `admin.py` - new model registrations
- Updated `models.py` - new conversation/message models

### 📚 Documentation

#### New Files
- `MIGRATION_GUIDE.md` - Step-by-step migration instructions
- `CHANGELOG.md` - This file

#### Updated Files
- `README.md` - Complete rewrite for user chat system
  - New API documentation
  - Updated features list
  - New endpoint examples
  - Database model documentation

### 🐛 Bug Fixes
- Fixed admin panel access control
- Improved error handling in messaging endpoints
- Better validation for user inputs

### 🔒 Security
- Maintained group-based admin access
- Kept authentication system intact
- Preserved API logging functionality

---

## [1.0.0] - 2026-01-21

### Initial Release - AI Chat Platform

#### Features
- OpenAI GPT-3.5-turbo integration
- Local AI engine support
- OSINT intelligence gathering
- Admin/user role system
- Django admin dashboard
- API logging
- Health check endpoint

---

## Migration Path

### From 1.0.0 to 2.0.0

**Breaking Changes:**
- All AI chat functionality removed
- OSINT features removed
- Database schema changed significantly
- API endpoints changed

**Migration Required:**
- Follow `MIGRATION_GUIDE.md` for detailed instructions
- Backup database before upgrading
- Run new migrations
- Update frontend to use new API endpoints

**Data Loss:**
- Old `ChatMessage` data will be lost
- Consider exporting if needed before migration

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

---

## Links

- [GitHub Repository](https://github.com/Aryankaushik541/white-beat-backend)
- [Frontend Repository](https://github.com/Aryankaushik541/white-beat-frontend)
- [Migration Guide](MIGRATION_GUIDE.md)
- [README](README.md)

---

**Last Updated:** 2026-01-21
