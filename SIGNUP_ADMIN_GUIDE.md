# 🔐 Signup & Admin Access Guide

Complete guide for user signup and admin access in White Beat platform!

---

## 🎯 **Overview**

### **Two Types of Users:**

#### **1. Regular Users** 👤
- Created via **Signup** on login page
- Access **User Dashboard**
- Features:
  - AI Chat
  - OSINT Lookup
  - Message History
  - Profile Management

#### **2. Admin Users** 🔐
- Created via **Django createsuperuser** command
- Access **Admin Dashboard**
- Features:
  - All user features
  - User management
  - System statistics
  - API logs
  - Revenue tracking
  - Make other users admin

---

## 🚀 **Quick Start**

### **For Regular Users:**
```
1. Go to login page
2. Click "Sign Up"
3. Enter username, email (optional), password
4. Click "Sign Up" button
5. Login with credentials
6. → Redirected to User Dashboard
```

### **For Admin Users:**
```
1. Create superuser:
   python manage.py createsuperuser

2. Login with superuser credentials
3. → Redirected to Admin Dashboard
```

---

## 📝 **User Signup**

### **Frontend (Login Page):**

**Features:**
- ✅ Toggle between Login/Signup
- ✅ Username validation
- ✅ Email (optional)
- ✅ Password validation
- ✅ Success/Error messages
- ✅ Beautiful glassmorphism UI

**Signup Flow:**
```
1. User clicks "Sign Up" button
2. Form shows username, email, password fields
3. User fills details
4. Click "Sign Up"
5. Backend creates user account
6. Success message shown
7. Form switches to Login mode
8. User can now login
```

### **Backend API:**

**Endpoint:** `POST /api/signup/`

**Request:**
```json
{
  "username": "john_doe",
  "password": "secure_password",
  "email": "john@example.com"  // Optional
}
```

**Success Response (201):**
```json
{
  "success": true,
  "role": "user",
  "username": "john_doe",
  "email": "john@example.com",
  "user_id": 123,
  "message": "Account created successfully! You can now login."
}
```

**Error Responses:**

**Username exists (400):**
```json
{
  "error": "Username already exists"
}
```

**Email exists (400):**
```json
{
  "error": "Email already exists"
}
```

**Missing fields (400):**
```json
{
  "error": "Username and password are required"
}
```

---

## 🔐 **Admin Access**

### **Method 1: Create Superuser (Recommended)**

```bash
# In backend directory
python manage.py createsuperuser

# Enter details:
Username: admin
Email address: admin@whitebeat.com
Password: ********
Password (again): ********

# Output:
Superuser created successfully.
```

**Login:**
```
1. Go to login page
2. Enter superuser credentials
3. Click "Login"
4. → Redirected to Admin Dashboard
```

### **Method 2: Promote Existing User**

**Via API (Requires superuser credentials):**

```bash
POST /api/make-admin/
{
  "admin_username": "admin",
  "admin_password": "admin_password",
  "target_username": "user_to_promote"
}
```

**Response:**
```json
{
  "success": true,
  "message": "user_to_promote is now an admin",
  "username": "user_to_promote",
  "is_staff": true,
  "is_superuser": true
}
```

### **Method 3: Django Admin Panel**

```
1. Go to http://localhost:8000/admin
2. Login with superuser credentials
3. Click "Users"
4. Select user
5. Check "Staff status" and "Superuser status"
6. Click "Save"
```

---

## 🔄 **Login Flow**

### **User Login:**
```
POST /api/login/
{
  "username": "john_doe",
  "password": "password"
}

Response:
{
  "role": "user",
  "username": "john_doe",
  "email": "john@example.com",
  "user_id": 123,
  "message": "User login successful"
}

→ Frontend redirects to User Dashboard
```

### **Admin Login:**
```
POST /api/login/
{
  "username": "admin",
  "password": "admin_password"
}

Response:
{
  "role": "admin",
  "username": "admin",
  "email": "admin@whitebeat.com",
  "user_id": 1,
  "is_staff": true,
  "is_superuser": true,
  "message": "Admin login successful"
}

→ Frontend redirects to Admin Dashboard
```

---

## 🎨 **Frontend Features**

### **Login Page:**

**Toggle Mode:**
```javascript
// Switch between Login and Signup
const [isSignup, setIsSignup] = useState(false);

// Toggle function
const toggleMode = () => {
  setIsSignup(!isSignup);
  setError('');
  setSuccess('');
};
```

**Signup Form:**
```javascript
// Signup request
const response = await axios.post(`${API_URL}/signup/`, {
  username,
  password,
  email: email || `${username}@whitebeat.com`
});

// Show success message
setSuccess('Account created successfully! Please login.');
setIsSignup(false);
```

**Login Form:**
```javascript
// Login request
const response = await axios.post(`${API_URL}/login/`, {
  username,
  password
});

// Check role and redirect
const { role } = response.data;
if (role === 'admin') {
  // Redirect to Admin Dashboard
} else {
  // Redirect to User Dashboard
}
```

### **UI Components:**

**Info Cards:**
```jsx
<div className="info-card">
  <div className="info-icon">👤</div>
  <div className="info-content">
    <h3>User Access</h3>
    <p>Sign up to create a user account</p>
    <p className="hint-text">Access chat and OSINT features</p>
  </div>
</div>

<div className="info-card">
  <div className="info-icon">🔐</div>
  <div className="info-content">
    <h3>Admin Access</h3>
    <p>Login with superuser credentials</p>
    <p className="hint-text">
      Create: <code>python manage.py createsuperuser</code>
    </p>
  </div>
</div>
```

**Admin Info Button:**
```jsx
<button 
  type="button" 
  className="admin-info-btn"
  onClick={handleAdminInfo}
>
  ℹ️ Admin Access Information
</button>
```

---

## 🔒 **Security**

### **Password Hashing:**
```python
# Django automatically hashes passwords
user = User.objects.create_user(
    username=username,
    password=password,  # Automatically hashed
    email=email
)
```

### **Authentication:**
```python
# Secure authentication
user = authenticate(username=username, password=password)

if user is not None:
    # Valid credentials
    if user.is_superuser:
        # Admin access
    else:
        # User access
else:
    # Invalid credentials
```

### **Admin Verification:**
```python
# Only superusers can make others admin
if not admin_user or not admin_user.is_superuser:
    return Response(
        {'error': 'Only superusers can make other users admin'},
        status=status.HTTP_403_FORBIDDEN
    )
```

---

## 🧪 **Testing**

### **Test 1: User Signup**
```bash
curl -X POST http://localhost:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "role": "user",
  "username": "testuser",
  "email": "test@example.com",
  "user_id": 2,
  "message": "Account created successfully! You can now login."
}
```

### **Test 2: User Login**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

**Expected Response:**
```json
{
  "role": "user",
  "username": "testuser",
  "email": "test@example.com",
  "user_id": 2,
  "message": "User login successful"
}
```

### **Test 3: Admin Login**
```bash
# First create superuser
python manage.py createsuperuser

# Then test login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin_password"
  }'
```

**Expected Response:**
```json
{
  "role": "admin",
  "username": "admin",
  "email": "admin@whitebeat.com",
  "user_id": 1,
  "is_staff": true,
  "is_superuser": true,
  "message": "Admin login successful"
}
```

### **Test 4: Verify Admin**
```bash
curl -X POST http://localhost:8000/api/verify-admin/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin"
  }'
```

**Expected Response:**
```json
{
  "is_admin": true,
  "is_staff": true,
  "is_superuser": true,
  "username": "admin"
}
```

### **Test 5: Make User Admin**
```bash
curl -X POST http://localhost:8000/api/make-admin/ \
  -H "Content-Type: application/json" \
  -d '{
    "admin_username": "admin",
    "admin_password": "admin_password",
    "target_username": "testuser"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "testuser is now an admin",
  "username": "testuser",
  "is_staff": true,
  "is_superuser": true
}
```

---

## 📊 **User Roles Comparison**

| Feature | Regular User | Admin User |
|---------|-------------|------------|
| **Creation** | Signup page | Django command |
| **Dashboard** | User Dashboard | Admin Dashboard |
| **AI Chat** | ✅ Yes | ✅ Yes |
| **OSINT** | ✅ Yes | ✅ Yes |
| **View Stats** | ❌ No | ✅ Yes |
| **User Management** | ❌ No | ✅ Yes |
| **API Logs** | ❌ No | ✅ Yes |
| **Make Admin** | ❌ No | ✅ Yes |
| **System Control** | ❌ No | ✅ Yes |

---

## 🎯 **Best Practices**

### **For Users:**
1. ✅ Use strong passwords
2. ✅ Provide valid email (optional but recommended)
3. ✅ Keep credentials secure
4. ✅ Logout after use

### **For Admins:**
1. ✅ Create superuser via Django command
2. ✅ Use very strong passwords
3. ✅ Don't share admin credentials
4. ✅ Only promote trusted users to admin
5. ✅ Monitor API logs regularly
6. ✅ Review user activity

### **For Developers:**
1. ✅ Always hash passwords
2. ✅ Validate input data
3. ✅ Use HTTPS in production
4. ✅ Implement rate limiting
5. ✅ Log all admin actions
6. ✅ Regular security audits

---

## 🐛 **Troubleshooting**

### **Issue 1: Signup fails with "Username exists"**

**Solution:**
```bash
# Check if username exists
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username='username').exists()
True

# Delete if needed
>>> User.objects.filter(username='username').delete()
```

### **Issue 2: Can't create superuser**

**Solution:**
```bash
# Make sure migrations are done
python manage.py migrate

# Try creating superuser again
python manage.py createsuperuser
```

### **Issue 3: Admin can't access admin dashboard**

**Solution:**
```bash
# Check user status
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='admin')
>>> user.is_superuser
False

# Make superuser
>>> user.is_superuser = True
>>> user.is_staff = True
>>> user.save()
```

### **Issue 4: Login redirects to wrong dashboard**

**Solution:**
```javascript
// Check role in response
const { role } = response.data;

// Correct routing
if (role === 'admin') {
  // Admin Dashboard
} else if (role === 'user') {
  // User Dashboard
}
```

---

## 📚 **API Endpoints Summary**

### **Authentication:**
- `POST /api/signup/` - Create new user account
- `POST /api/login/` - Login (admin or user)
- `POST /api/verify-admin/` - Check if user is admin
- `POST /api/make-admin/` - Promote user to admin

### **Features:**
- `POST /api/chat/` - AI chat
- `POST /api/osint/` - OSINT lookup
- `GET /api/admin/stats/` - Admin statistics
- `GET /api/health/` - System health

---

## 🎉 **Summary**

**User Flow:**
```
Signup → Login → User Dashboard → Chat/OSINT
```

**Admin Flow:**
```
createsuperuser → Login → Admin Dashboard → Full Control
```

**Key Points:**
- ✅ Signup creates regular users
- ✅ Superusers created via Django command
- ✅ Automatic role-based routing
- ✅ Secure authentication
- ✅ Beautiful UI with toggle
- ✅ Admin can promote users

---

<div align="center">

**Secure, Simple, Powerful! 🔐**

Users signup, Admins command!

</div>