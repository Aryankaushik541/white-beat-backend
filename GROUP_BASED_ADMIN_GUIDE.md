# 🔐 Group-Based Admin Access Guide

Complete guide for Django group-based admin access in White Beat!

---

## 🎯 **Overview**

### **New System:**
- ✅ **Admin access** based on Django **Groups**
- ✅ Only users in **"Admin" group** can access Admin Dashboard
- ✅ Regular users → User Dashboard
- ✅ Admin users (in Admin group) → Admin Dashboard

### **Key Changes:**
- ❌ No more `is_superuser` check
- ✅ Now checks `user.groups.filter(name='Admin').exists()`
- ✅ More flexible and scalable
- ✅ Easy to add/remove admin access

---

## 🚀 **Quick Start**

### **Step 1: Create Admin Group & Test Users**
```bash
cd white-beat-backend
python create_test_users.py
```

**Output:**
```
✅ Test users creation complete!

Regular Users (→ User Dashboard):
  Username: aryan        | Password: aryan123
  Username: john         | Password: john123

Admin Users (→ Admin Dashboard - in 'Admin' group):
  Username: admin        | Password: admin123
  Username: superadmin   | Password: super123
```

### **Step 2: Test Login**
```bash
# Start backend
python manage.py runserver

# Start frontend (new terminal)
cd white-beat-frontend
npm start

# Go to http://localhost:3000
```

**Test Regular User:**
```
Username: aryan
Password: aryan123
→ User Dashboard ✅
```

**Test Admin User:**
```
Username: admin
Password: admin123
→ Admin Dashboard ✅
```

---

## 📋 **Admin Group Management**

### **Method 1: Using API (Recommended)**

**Add User to Admin Group:**
```bash
curl -X POST http://localhost:8000/api/make-admin/ \
  -H "Content-Type: application/json" \
  -d '{
    "admin_username": "admin",
    "admin_password": "admin123",
    "target_username": "aryan"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "aryan is now an admin",
  "username": "aryan",
  "is_admin_group": true,
  "groups": ["Admin"]
}
```

**Remove User from Admin Group:**
```bash
curl -X POST http://localhost:8000/api/remove-admin/ \
  -H "Content-Type: application/json" \
  -d '{
    "admin_username": "admin",
    "admin_password": "admin123",
    "target_username": "aryan"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "aryan is no longer an admin",
  "username": "aryan",
  "is_admin_group": false,
  "groups": []
}
```

### **Method 2: Django Shell**

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User, Group

# Get or create Admin group
admin_group, created = Group.objects.get_or_create(name='Admin')

# Add user to Admin group
user = User.objects.get(username='aryan')
user.groups.add(admin_group)
user.save()

# Remove user from Admin group
user.groups.remove(admin_group)
user.save()

# Check if user is admin
user.groups.filter(name='Admin').exists()

# List all admin users
User.objects.filter(groups__name='Admin')
```

### **Method 3: Django Admin Panel**

```
1. Go to http://localhost:8000/admin
2. Login with admin credentials
3. Click "Users"
4. Select user
5. In "Groups" section, add "Admin" group
6. Click "Save"
```

---

## 🔍 **How It Works**

### **Backend Logic:**

```python
def is_user_admin(user):
    """Check if user is in Admin group"""
    return user.groups.filter(name='Admin').exists()

@api_view(['POST'])
def login(request):
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # Check if user is in Admin group
        is_admin = is_user_admin(user)
        
        if is_admin:
            # Admin Dashboard
            return Response({
                'role': 'admin',
                'is_admin_group': True,
                'groups': ['Admin']
            })
        else:
            # User Dashboard
            return Response({
                'role': 'user',
                'is_admin_group': False,
                'groups': []
            })
```

### **Frontend Routing:**

```javascript
// After successful login
const { role } = response.data;

if (role === 'admin') {
  navigate('/admin-dashboard');  // Admin group users
} else {
  navigate('/user-dashboard');   // Regular users
}
```

---

## 🧪 **Testing**

### **Test 1: Regular User Login**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "aryan",
    "password": "aryan123"
  }'
```

**Expected Response:**
```json
{
  "role": "user",
  "username": "aryan",
  "email": "aryan@whitebeat.com",
  "user_id": 2,
  "is_admin_group": false,
  "groups": [],
  "message": "User login successful"
}
```

### **Test 2: Admin User Login**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Expected Response:**
```json
{
  "role": "admin",
  "username": "admin",
  "email": "admin@whitebeat.com",
  "user_id": 1,
  "is_admin_group": true,
  "groups": ["Admin"],
  "message": "Admin login successful"
}
```

### **Test 3: Verify Admin Status**
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
  "is_admin_group": true,
  "username": "admin",
  "groups": ["Admin"]
}
```

### **Test 4: Make User Admin**
```bash
curl -X POST http://localhost:8000/api/make-admin/ \
  -H "Content-Type: application/json" \
  -d '{
    "admin_username": "admin",
    "admin_password": "admin123",
    "target_username": "john"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "john is now an admin",
  "username": "john",
  "is_admin_group": true,
  "groups": ["Admin"]
}
```

### **Test 5: Remove Admin Access**
```bash
curl -X POST http://localhost:8000/api/remove-admin/ \
  -H "Content-Type: application/json" \
  -d '{
    "admin_username": "admin",
    "admin_password": "admin123",
    "target_username": "john"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "john is no longer an admin",
  "username": "john",
  "is_admin_group": false,
  "groups": []
}
```

---

## 📊 **User Roles Comparison**

| Feature | Regular User | Admin User (in Admin group) |
|---------|-------------|----------------------------|
| **Creation** | Signup page | Add to Admin group |
| **Dashboard** | User Dashboard | Admin Dashboard |
| **AI Chat** | ✅ Yes | ✅ Yes |
| **OSINT** | ✅ Yes | ✅ Yes |
| **View Stats** | ❌ No | ✅ Yes |
| **User Management** | ❌ No | ✅ Yes |
| **API Logs** | ❌ No | ✅ Yes |
| **Make Admin** | ❌ No | ✅ Yes |
| **Remove Admin** | ❌ No | ✅ Yes |
| **Group** | None | Admin |

---

## 🔒 **Security**

### **Admin Actions Require:**
1. ✅ Valid admin credentials
2. ✅ User must be in Admin group
3. ✅ Password verification for sensitive actions

### **Example:**
```python
# Only users in Admin group can make others admin
admin_user = authenticate(username=admin_username, password=admin_password)

if not admin_user or not is_user_admin(admin_user):
    return Response(
        {'error': 'Only users in Admin group can make other users admin'},
        status=status.HTTP_403_FORBIDDEN
    )
```

---

## 🎯 **Best Practices**

### **For Admins:**
1. ✅ Only add trusted users to Admin group
2. ✅ Regularly review Admin group members
3. ✅ Use strong passwords for admin accounts
4. ✅ Monitor admin actions in API logs
5. ✅ Remove admin access when no longer needed

### **For Developers:**
1. ✅ Always check group membership for admin actions
2. ✅ Log all admin operations
3. ✅ Validate admin credentials before sensitive operations
4. ✅ Use Django's built-in Group system
5. ✅ Keep group names consistent

---

## 🐛 **Troubleshooting**

### **Issue 1: Admin group doesn't exist**

**Error:**
```
Admin group does not exist
```

**Solution:**
```bash
python manage.py shell
>>> from django.contrib.auth.models import Group
>>> Group.objects.create(name='Admin')

# Or run test users script
python create_test_users.py
```

### **Issue 2: User not in Admin group**

**Check:**
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='admin')
>>> user.groups.filter(name='Admin').exists()
False

# Add to Admin group
>>> from django.contrib.auth.models import Group
>>> admin_group = Group.objects.get(name='Admin')
>>> user.groups.add(admin_group)
>>> user.save()
```

### **Issue 3: Can't access Admin Dashboard**

**Solution:**
```bash
# Verify user is in Admin group
curl -X POST http://localhost:8000/api/verify-admin/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin"}'

# If is_admin_group is false, add to group
python manage.py shell
>>> from django.contrib.auth.models import User, Group
>>> user = User.objects.get(username='admin')
>>> admin_group = Group.objects.get(name='Admin')
>>> user.groups.add(admin_group)
```

---

## 📚 **API Endpoints**

### **Authentication:**
- `POST /api/signup/` - Create new user account
- `POST /api/login/` - Login (checks Admin group)
- `POST /api/verify-admin/` - Check if user is in Admin group

### **Admin Management:**
- `POST /api/make-admin/` - Add user to Admin group
- `POST /api/remove-admin/` - Remove user from Admin group

### **Features:**
- `POST /api/chat/` - AI chat
- `POST /api/osint/` - OSINT lookup
- `GET /api/admin/stats/` - Admin statistics
- `GET /api/health/` - System health (includes admin group status)

---

## 🎉 **Summary**

**Old System:**
```
✅ is_superuser = True → Admin
❌ is_superuser = False → User
```

**New System:**
```
✅ In 'Admin' group → Admin Dashboard
✅ Not in 'Admin' group → User Dashboard
```

**Benefits:**
- ✅ More flexible
- ✅ Easy to manage
- ✅ Scalable
- ✅ Standard Django approach
- ✅ Can have multiple admin groups
- ✅ Easy to add/remove access

**Test Credentials:**
```
Regular Users:
  aryan / aryan123
  john / john123

Admin Users (in Admin group):
  admin / admin123
  superadmin / super123
```

**Quick Commands:**
```bash
# Create test users with Admin group
python create_test_users.py

# Add user to Admin group
python manage.py shell
>>> from django.contrib.auth.models import User, Group
>>> user = User.objects.get(username='username')
>>> admin_group = Group.objects.get(name='Admin')
>>> user.groups.add(admin_group)

# Check admin users
>>> User.objects.filter(groups__name='Admin')
```

---

<div align="center">

**Group-Based Admin Access! 🔐**

Only "Admin" group members can access Admin Dashboard!

</div>