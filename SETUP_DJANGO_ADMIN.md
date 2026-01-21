# 🚀 Django Admin Setup Guide

Complete guide to set up Django admin dashboard with database integration.

---

## 📋 **Step-by-Step Setup**

### **Step 1: Pull Latest Code**

```bash
cd white-beat-backend
git pull origin main
```

### **Step 2: Run Migrations**

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

**You should see:**
```
Running migrations:
  Applying api.0001_initial... OK
  Applying api.0002_userprofile... OK
  Applying api.0003_chatmessage... OK
  Applying api.0004_apilog... OK
  Applying api.0005_systemstats... OK
```

### **Step 3: Create Superuser**

```bash
python manage.py createsuperuser
```

**Enter details:**
```
Username: admin
Email: admin@whitebeat.com
Password: admin123
Password (again): admin123
```

**Note:** Agar "password too common" warning aaye, type `y` to bypass.

### **Step 4: Start Server**

```bash
python manage.py runserver
```

### **Step 5: Access Django Admin**

Open browser:
```
http://localhost:8000/admin
```

**Login with:**
- Username: `admin`
- Password: `admin123`

---

## 🎯 **What You'll See in Django Admin**

### **1. Users Section**
- View all registered users
- See user profiles with roles (admin/user)
- Track total messages per user
- Monitor active sessions
- Edit user details

### **2. Chat Messages**
- All chat conversations
- Prompts and responses
- Model used (GPT-3.5-turbo or demo)
- Tokens consumed
- Response times
- Search and filter by user/date

### **3. API Logs**
- Every API request logged
- Endpoint, method, status code
- Response times
- User who made request
- IP addresses
- User agents
- Filter by date/status/method

### **4. System Stats**
- Daily statistics
- Total users, active users
- Total messages, API calls
- Revenue tracking

---

## 🔗 **Frontend Integration**

### **Update Frontend**

```bash
cd white-beat-frontend
git pull origin main
npm start
```

### **Admin Dashboard Features**

1. **Overview Tab:**
   - Real-time stats from database
   - User growth charts
   - API usage charts
   - Quick access buttons to Django admin

2. **Users Tab:**
   - List of recent users from database
   - Click "Edit" to open Django admin
   - Real status (Active/Inactive)
   - Total messages count

3. **API Logs Tab:**
   - Recent API requests
   - Real response times
   - Status codes
   - Timestamps

4. **Django Admin Button:**
   - Direct link to full Django admin
   - Opens in new tab

---

## 📊 **Testing the Integration**

### **Test 1: Create Users**

```bash
# Login as different users in frontend
http://localhost:3000

# Login with:
Username: testuser1
Password: password

# Then check Django admin:
http://localhost:8000/admin/auth/user/
```

You'll see `testuser1` created!

### **Test 2: Send Messages**

```bash
# In user dashboard, send chat messages
# Then check Django admin:
http://localhost:8000/admin/api/chatmessage/
```

All messages logged!

### **Test 3: View API Logs**

```bash
# Make some API requests
# Then check:
http://localhost:8000/admin/api/apilog/
```

Every request logged with timing!

---

## 🎨 **Customize Django Admin**

### **Change Site Header**

Edit `api/admin.py`:
```python
admin.site.site_header = 'Your Company Admin'
admin.site.site_title = 'Your Company'
admin.site.index_title = 'Welcome to Administration'
```

### **Add More Fields to User List**

Edit `api/admin.py` in `UserAdmin`:
```python
list_display = ('username', 'email', 'get_role', 'get_total_messages', 'is_active', 'date_joined', 'last_login')
```

---

## 🔧 **Common Issues & Fixes**

### **Issue 1: "no such table" error**

```bash
# Delete database and recreate
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### **Issue 2: "Migrations not applied"**

```bash
python manage.py makemigrations
python manage.py migrate
```

### **Issue 3: "Admin login not working"**

```bash
# Recreate superuser
python manage.py createsuperuser
```

### **Issue 4: "Frontend not showing data"**

```bash
# Check API endpoint
curl http://localhost:8000/api/admin/stats/

# Should return JSON with stats
```

---

## 📱 **Admin Dashboard URLs**

| Feature | URL |
|---------|-----|
| Main Admin | http://localhost:8000/admin |
| Users | http://localhost:8000/admin/auth/user/ |
| Chat Messages | http://localhost:8000/admin/api/chatmessage/ |
| API Logs | http://localhost:8000/admin/api/apilog/ |
| System Stats | http://localhost:8000/admin/api/systemstats/ |
| Add User | http://localhost:8000/admin/auth/user/add/ |

---

## 🚀 **Production Deployment**

### **For Production:**

1. **Use PostgreSQL instead of SQLite:**

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'whitebeat_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

2. **Secure Admin URL:**

```python
# urls.py
urlpatterns = [
    path('secure-admin-panel/', admin.site.urls),  # Change from 'admin/'
]
```

3. **Enable HTTPS:**

```python
# settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## 📚 **Next Steps**

1. ✅ **Explore Django Admin** - Click around, add users, view logs
2. ✅ **Test Frontend Integration** - See real data in React dashboard
3. ✅ **Customize Admin** - Add your branding
4. ✅ **Add More Models** - Create custom data models
5. ✅ **Deploy** - Push to production

---

## 🎉 **You're All Set!**

Your White Beat platform now has:
- ✅ Full Django admin dashboard
- ✅ Database integration
- ✅ Real-time data in React frontend
- ✅ User management
- ✅ Chat message logging
- ✅ API request tracking
- ✅ System statistics

**Access:**
- **Frontend:** http://localhost:3000
- **Django Admin:** http://localhost:8000/admin
- **API:** http://localhost:8000/api

---

<div align="center">

**Happy Administrating! 🚀**

</div>