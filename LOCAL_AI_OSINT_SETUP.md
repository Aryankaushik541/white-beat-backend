# 🤖 Local AI + OSINT Setup Guide

Complete guide to setup White Beat with local AI (no OpenAI API) and OSINT capabilities!

---

## 🎯 **What's New**

### **1. Local AI Engine** 🤖
- ✅ **No OpenAI API required!**
- ✅ Runs completely offline
- ✅ Multiple model options:
  - **DialoGPT** (Microsoft) - Conversational AI
  - **BlenderBot** (Facebook) - Advanced conversations
  - **FLAN-T5** (Google) - Instruction following
- ✅ ChatGPT-like experience
- ✅ Free and open-source

### **2. OSINT Engine** 🔍
- ✅ Username search across platforms
- ✅ Email validation and lookup
- ✅ Phone number analysis
- ✅ IP geolocation
- ✅ Domain information
- ✅ GitHub profile details
- ✅ Social media search

### **3. Admin Control** 🔐
- ✅ Only superusers can make others admin
- ✅ Secure admin access
- ✅ User management from admin panel

---

## 🚀 **Quick Setup (5 Minutes)**

### **Step 1: Update Backend**

```bash
cd white-beat-backend
git pull origin main

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install new dependencies
pip install -r requirements.txt

# This will install:
# - transformers (Hugging Face)
# - torch (PyTorch)
# - requests, beautifulsoup4 (OSINT)
# - dnspython (DNS lookups)
```

**⚠️ Note:** First-time model download will take 5-10 minutes (models are ~500MB-1GB)

### **Step 2: Run Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

### **Step 3: Create Superuser**

```bash
python manage.py createsuperuser

# Enter details:
Username: admin
Email: admin@whitebeat.com
Password: (your secure password)
```

### **Step 4: Start Backend**

```bash
python manage.py runserver
```

**First startup will:**
1. Download AI model (DialoGPT-medium, ~355MB)
2. Initialize AI engine
3. Setup OSINT engine

### **Step 5: Update Frontend**

```bash
cd white-beat-frontend
git pull origin main
npm start
```

---

## 🤖 **Local AI Models**

### **Available Models:**

#### **1. DialoGPT (Default)** ⭐
```python
# In api/ai_engine.py
ai_engine_type = "dialogpt"
```
- **Size:** 355MB (medium), 762MB (large)
- **Best for:** General conversations
- **Speed:** Fast
- **Quality:** Good

#### **2. BlenderBot**
```python
ai_engine_type = "blenderbot"
```
- **Size:** 400MB
- **Best for:** Natural conversations
- **Speed:** Medium
- **Quality:** Excellent

#### **3. FLAN-T5**
```python
ai_engine_type = "flan-t5"
```
- **Size:** 250MB
- **Best for:** Task-oriented chat
- **Speed:** Fast
- **Quality:** Very Good

### **Change Model:**

Edit `api/ai_engine.py`:
```python
# Line 200
ai_engine_type = "dialogpt"  # Change to: blenderbot, flan-t5
```

---

## 🔍 **OSINT Features**

### **1. Username Search**
```bash
POST /api/osint/
{
  "query": "username",
  "type": "username"
}
```

**Searches:**
- GitHub
- Twitter
- Instagram
- Reddit
- LinkedIn
- Medium
- Dev.to
- StackOverflow

### **2. Email Lookup**
```bash
POST /api/osint/
{
  "query": "email@example.com",
  "type": "email"
}
```

**Returns:**
- Email format validation
- Domain existence check
- MX records

### **3. IP Geolocation**
```bash
POST /api/osint/
{
  "query": "8.8.8.8",
  "type": "ip"
}
```

**Returns:**
- Country, Region, City
- ISP and Organization
- Latitude/Longitude
- Timezone

### **4. Domain Info**
```bash
POST /api/osint/
{
  "query": "example.com",
  "type": "domain"
}
```

**Returns:**
- DNS records (A, MX, NS)
- Domain accessibility
- Status code

### **5. GitHub Profile**
```bash
POST /api/osint/
{
  "query": "username",
  "type": "username"
}
```

**Returns:**
- Name, Bio, Location
- Public repos, Followers
- Company, Email, Twitter
- Profile URL, Avatar

---

## 🔐 **Admin Control**

### **Make User Admin (Superuser Only)**

```bash
POST /api/make-admin/
{
  "admin_username": "admin",
  "admin_password": "admin_password",
  "target_username": "user_to_make_admin"
}
```

**Requirements:**
- Only superusers can make others admin
- Admin must provide valid credentials
- Target user must exist

### **Verify Admin Status**

```bash
POST /api/verify-admin/
{
  "username": "username"
}
```

**Returns:**
```json
{
  "is_admin": true,
  "is_staff": true,
  "is_superuser": false,
  "username": "username"
}
```

---

## 🧪 **Testing**

### **Test 1: Local AI Chat**

```bash
# Start backend
python manage.py runserver

# In another terminal
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello! How are you?", "username": "testuser"}'
```

**Expected Response:**
```json
{
  "response": "I'm doing great! How can I help you today?",
  "model": "microsoft/DialoGPT-medium",
  "demo": false,
  "engine": "local-ai"
}
```

### **Test 2: OSINT Username Search**

```bash
curl -X POST http://localhost:8000/api/osint/ \
  -H "Content-Type: application/json" \
  -d '{"query": "torvalds", "type": "username"}'
```

**Expected Response:**
```json
{
  "success": true,
  "query": "torvalds",
  "type": "username",
  "results": {
    "username_search": {
      "github": {"exists": true, "url": "https://github.com/torvalds"},
      "twitter": {"exists": true, "url": "https://twitter.com/torvalds"}
    },
    "github": {
      "username": "torvalds",
      "name": "Linus Torvalds",
      "public_repos": 6,
      "followers": 180000
    }
  }
}
```

### **Test 3: Make User Admin**

```bash
curl -X POST http://localhost:8000/api/make-admin/ \
  -H "Content-Type: application/json" \
  -d '{
    "admin_username": "admin",
    "admin_password": "your_password",
    "target_username": "testuser"
  }'
```

### **Test 4: Health Check**

```bash
curl http://localhost:8000/api/health/
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "White Beat Backend",
  "database_connected": true,
  "ai_engine": "initialized",
  "osint_engine": "available",
  "features": {
    "local_ai": true,
    "osint": true,
    "admin_control": true
  }
}
```

---

## 📊 **Performance**

### **AI Response Times:**
- **DialoGPT:** 1-3 seconds (CPU), 0.5-1s (GPU)
- **BlenderBot:** 2-4 seconds (CPU), 1-2s (GPU)
- **FLAN-T5:** 1-2 seconds (CPU), 0.5-1s (GPU)

### **OSINT Response Times:**
- **Username Search:** 2-5 seconds
- **Email Lookup:** 1-2 seconds
- **IP Geolocation:** 1-2 seconds
- **Domain Info:** 2-3 seconds

### **GPU Acceleration:**
If you have NVIDIA GPU with CUDA:
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If True, AI will automatically use GPU (10x faster!)
```

---

## 🎨 **Frontend Integration**

### **Chat with Local AI:**
```javascript
// Already integrated in UserDashboard.js
const response = await axios.post(`${API_URL}/chat/`, {
  prompt: input,
  username: user.username
});

// Response includes:
// - response: AI generated text
// - model: Model name
// - engine: "local-ai"
```

### **OSINT Lookup:**
```javascript
// Add to your component
const osintLookup = async (query, type) => {
  const response = await axios.post(`${API_URL}/osint/`, {
    query: query,
    type: type  // username, email, ip, domain, auto
  });
  
  return response.data.results;
};
```

### **Make User Admin:**
```javascript
const makeAdmin = async (targetUsername) => {
  const response = await axios.post(`${API_URL}/make-admin/`, {
    admin_username: currentUser.username,
    admin_password: prompt('Enter your admin password:'),
    target_username: targetUsername
  });
  
  return response.data;
};
```

---

## 🐛 **Troubleshooting**

### **Issue 1: AI model not downloading**

**Solution:**
```bash
# Manual download
python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; AutoTokenizer.from_pretrained('microsoft/DialoGPT-medium'); AutoModelForCausalLM.from_pretrained('microsoft/DialoGPT-medium')"
```

### **Issue 2: Out of memory**

**Solution:**
```python
# Use smaller model in api/ai_engine.py
ai_engine.initialize("distilgpt2")  # Only 82MB
```

### **Issue 3: OSINT not working**

**Solution:**
```bash
# Install missing dependencies
pip install requests beautifulsoup4 dnspython lxml
```

### **Issue 4: Slow AI responses**

**Solution:**
```python
# Reduce max_length in ai_engine.py
def generate_response(self, prompt, max_length=100):  # Was 150
```

---

## 🔧 **Configuration**

### **AI Engine Settings:**

Edit `api/ai_engine.py`:
```python
# Model selection
ai_engine_type = "dialogpt"  # dialogpt, blenderbot, flan-t5

# Response settings
max_length = 150  # Maximum response length
temperature = 0.7  # Creativity (0.0-1.0)
```

### **OSINT Settings:**

Edit `api/osint_engine.py`:
```python
# Timeout for requests
timeout = 5  # seconds

# User agent
'User-Agent': 'Mozilla/5.0 ...'
```

---

## 📚 **API Endpoints**

### **Authentication:**
- `POST /api/login/` - Login
- `POST /api/verify-admin/` - Check admin status
- `POST /api/make-admin/` - Make user admin (superuser only)

### **AI Chat:**
- `POST /api/chat/` - Chat with local AI

### **OSINT:**
- `POST /api/osint/` - OSINT lookup

### **Admin:**
- `GET /api/admin/stats/` - Admin dashboard stats

### **Health:**
- `GET /api/health/` - System health check

---

## 🎉 **Summary**

Your White Beat platform now has:
- ✅ **Local AI** - No OpenAI API needed!
- ✅ **OSINT** - Intelligence gathering
- ✅ **Admin Control** - Secure user management
- ✅ **ChatGPT-like** - Natural conversations
- ✅ **Completely Free** - No API costs
- ✅ **Offline Capable** - Works without internet (after model download)

---

## 🚀 **Quick Start Commands**

```bash
# Backend
cd white-beat-backend
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend
cd white-beat-frontend
git pull origin main
npm start

# Test
curl http://localhost:8000/api/health/
```

---

<div align="center">

**Local AI + OSINT = Powerful! 🤖🔍**

No API keys, No costs, Full control!

</div>