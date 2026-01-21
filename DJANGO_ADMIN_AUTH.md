# 🔐 Django Admin Authentication Setup

Complete guide for Django-based admin authentication.

---

## 🎯 **What Changed**

### **Before:**
- ❌ Hardcoded admin credentials (`admin/admin123`)
- ❌ Anyone could access admin dashboard
- ❌ No real authentication

### **After:**
- ✅ Django authentication system
- ✅ Only Django staff/superuser can access admin dashboard
- ✅ Real user management
- ✅ Secure authentication

---

## 🚀 **Complete Setup**

### **Step 1: Update Backend**

```bash
cd white-beat-backend

# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### **Step 2: Create Django Superuser**

```bash
python manage.py createsuperuser
```

**Enter details:**
```
Username: admin
Email address: admin@whitebeat.com
Password: your_secure_password
Password (again): your_secure_password
```

**⚠️ Important:** Remember this password! You'll use it to login.

### **Step 3: Start Backend**

```bash
python manage.py runserver
```

### **Step 4: Update Frontend**

**New terminal:**
```bash
cd white-beat-frontend

# Pull latest code
git pull origin main

# Start frontend
npm start
```

---

## 🔑 **How Authentication Works**

### **Admin Login Flow:**

1. **User enters credentials** in frontend
2. **Frontend sends** to `/api/login/`
3. **Django authenticates** using `authenticate()`
4. **Check if user is staff/superuser:**
   - ✅ Yes → Return `role: 'admin'` → Redirect to Admin Dashboard
   - ❌ No → Return `role: 'user'` → Redirect to User Dashboard

### **Code Flow:**

```python
# Backend: api/views.py
user = authenticate(username=username, password=password)

if user is not None:
    if user.is_staff or user.is_superuser:
        return Response({'role': 'admin'})  # Admin access
    else:
        return Response({'role': 'user'})   # User access
else:
    # Create new regular user or return error
```

---

## 👥 **User Types**

### **1. Django Superuser (Admin)**
- Created with `python manage.py createsuperuser`
- Has `is_staff=True` and `is_superuser=True`
- Can access:
  - ✅ Admin Dashboard (React)
  - ✅ Django Admin Panel (`/admin`)
  - ✅ All admin features

### **2. Django Staff User (Admin)**
- Created in Django admin
- Has `is_staff=True`
- Can access:
  - ✅ Admin Dashboard (React)
  - ✅ Django Admin Panel (`/admin`)

### **3. Regular User**
- Auto-created on first login
- Has `is_staff=False`
- Can access:
  - ✅ User Dashboard (Chat)
  - ❌ Admin Dashboard (blocked)
  - ❌ Django Admin Panel (blocked)

---

## 🧪 **Testing**

### **Test 1: Admin Login**

```bash
# Open: http://localhost:3000
# Login with Django superuser credentials:
Username: admin
Password: your_secure_password

# Should redirect to: /admin-dashboard
# Should see: Real stats from database
```

### **Test 2: User Login**

```bash
# Open: http://localhost:3000
# Login with any credentials:
Username: testuser
Password: password123

# Should redirect to: /user-dashboard
# Should see: Chat interface
```

### **Test 3: Invalid Admin Attempt**

```bash
# Try to login as admin with wrong password
# Should see error: "Invalid credentials"
```

---

## 🛠️ **Create Additional Admin Users**

### **Method 1: Django Admin Panel**

1. Login to Django admin: http://localhost:8000/admin
2. Go to **Users** → **Add User**
3. Enter username and password
4. Click **Save**
5. Check **Staff status** checkbox
6. Click **Save** again

### **Method 2: Django Shell**

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Create staff user
user = User.objects.create_user(
    username='manager',
    password='manager123',
    email='manager@whitebeat.com'
)
user.is_staff = True
user.save()

print(f"Created staff user: {user.username}")
exit()
```

### **Method 3: Management Command**

```bash
python manage.py createsuperuser --username manager --email manager@whitebeat.com
```

---

## 🔒 **Security Features**

### **1. Password Hashing**
- Passwords stored with Django's PBKDF2 algorithm
- Never stored in plain text

### **2. Authentication Required**
- Django's `authenticate()` function validates credentials
- Prevents brute force with proper rate limiting (add in production)

### **3. Role-Based Access**
- `is_staff` check for admin access
- `is_superuser` for full Django admin access

### **4. Session Management**
- User sessions tracked in database
- Automatic logout on browser close (configurable)

---

## 📊 **Database Schema**

### **User Model (Django Built-in)**
```python
User:
  - username (unique)
  - password (hashed)
  - email
  - is_staff (Boolean)
  - is_superuser (Boolean)
  - date_joined
  - last_login
```

### **UserProfile Model (Custom)**
```python
UserProfile:
  - user (ForeignKey to User)
  - role ('admin' or 'user')
  - is_active_session (Boolean)
  - total_messages (Integer)
  - joined_date
  - last_activity
```

---

## 🎯 **API Endpoints**

### **1. Login**
```http
POST /api/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

**Response (Admin):**
```json
{
  "role": "admin",
  "username": "admin",
  "message": "Admin login successful",
  "user_id": 1,
  "is_staff": true,
  "is_superuser": true
}
```

**Response (User):**
```json
{
  "role": "user",
  "username": "testuser",
  "message": "User login successful",
  "user_id": 2
}
```

**Response (Invalid):**
```json
{
  "error": "Invalid credentials"
}
```

### **2. Verify Admin**
```http
POST /api/verify-admin/
Content-Type: application/json

{
  "username": "admin"
}
```

**Response:**
```json
{
  "is_admin": true,
  "is_staff": true,
  "is_superuser": true,
  "username": "admin"
}
```

---

## 🚨 **Troubleshooting**

### **Issue 1: "Invalid credentials" for admin**

**Solution:**
```bash
# Reset admin password
python manage.py shell
```

```python
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
user.set_password('new_password')
user.save()
exit()
```

### **Issue 2: Admin user not created**

**Solution:**
```bash
# Create superuser
python manage.py createsuperuser
```

### **Issue 3: Regular user can't login**

**Solution:**
- Regular users are auto-created on first login
- Just enter any username/password
- They'll be created as regular users

### **Issue 4: Database errors**

**Solution:**
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 🔐 **Production Security**

### **1. Use Strong Passwords**
```python
# settings.py
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

### **2. Enable HTTPS**
```python
# settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### **3. Add Rate Limiting**
```bash
pip install django-ratelimit
```

```python
# views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m')
@api_view(['POST'])
def login(request):
    # ... login logic
```

### **4. Use Environment Variables**
```python
# settings.py
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
```

---

## 📚 **Quick Commands**

```bash
# Create superuser
python manage.py createsuperuser

# Reset password
python manage.py changepassword admin

# List all users
python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.all())"

# Make user staff
python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='testuser'); u.is_staff=True; u.save()"

# Check user permissions
python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='admin'); print(f'Staff: {u.is_staff}, Super: {u.is_superuser}')"
```

---

## ✅ **Verification Checklist**

- [ ] Backend migrations applied
- [ ] Superuser created
- [ ] Backend server running
- [ ] Frontend updated and running
- [ ] Can login as admin with Django credentials
- [ ] Admin dashboard shows real data
- [ ] Can login as regular user
- [ ] User dashboard works
- [ ] Django admin panel accessible at `/admin`
- [ ] All data syncing to database

---

## 🎉 **You're Done!**

Your White Beat platform now has:
- ✅ **Secure Django authentication**
- ✅ **Role-based access control**
- ✅ **Real user management**
- ✅ **Database integration**
- ✅ **Admin dashboard with real data**

**Login URLs:**
- **Frontend:** http://localhost:3000
- **Django Admin:** http://localhost:8000/admin

**Credentials:**
- Use Django superuser credentials for admin access
- Any username/password for user access

---

<div align="center">

**Secure & Professional! 🔐**

</div>