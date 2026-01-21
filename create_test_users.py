#!/usr/bin/env python
"""
Script to create test users for White Beat platform
Run: python create_test_users.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_beat.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import UserProfile

def create_test_users():
    """Create test users for development"""
    
    print("🚀 Creating test users...\n")
    
    # Test User 1: Regular user
    print("1️⃣ Creating regular user 'aryan'...")
    try:
        user1 = User.objects.create_user(
            username='aryan',
            password='aryan123',
            email='aryan@whitebeat.com',
            is_staff=False,
            is_superuser=False
        )
        profile1, _ = UserProfile.objects.get_or_create(
            user=user1,
            defaults={'role': 'user'}
        )
        print("   ✅ User 'aryan' created successfully!")
        print(f"   📧 Email: aryan@whitebeat.com")
        print(f"   🔑 Password: aryan123")
        print(f"   👤 Role: User\n")
    except Exception as e:
        print(f"   ⚠️ User 'aryan' already exists or error: {e}\n")
    
    # Test User 2: Another regular user
    print("2️⃣ Creating regular user 'john'...")
    try:
        user2 = User.objects.create_user(
            username='john',
            password='john123',
            email='john@whitebeat.com',
            is_staff=False,
            is_superuser=False
        )
        profile2, _ = UserProfile.objects.get_or_create(
            user=user2,
            defaults={'role': 'user'}
        )
        print("   ✅ User 'john' created successfully!")
        print(f"   📧 Email: john@whitebeat.com")
        print(f"   🔑 Password: john123")
        print(f"   👤 Role: User\n")
    except Exception as e:
        print(f"   ⚠️ User 'john' already exists or error: {e}\n")
    
    # Test Admin: Superuser
    print("3️⃣ Creating admin user 'admin'...")
    try:
        admin = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@whitebeat.com'
        )
        profile_admin, _ = UserProfile.objects.get_or_create(
            user=admin,
            defaults={'role': 'admin'}
        )
        print("   ✅ Admin 'admin' created successfully!")
        print(f"   📧 Email: admin@whitebeat.com")
        print(f"   🔑 Password: admin123")
        print(f"   🔐 Role: Admin (Superuser)\n")
    except Exception as e:
        print(f"   ⚠️ Admin 'admin' already exists or error: {e}\n")
    
    print("=" * 60)
    print("✅ Test users creation complete!\n")
    print("📝 Login Credentials:\n")
    print("Regular Users:")
    print("  Username: aryan    | Password: aryan123")
    print("  Username: john     | Password: john123\n")
    print("Admin User:")
    print("  Username: admin    | Password: admin123\n")
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend:  http://localhost:8000")
    print("=" * 60)

if __name__ == '__main__':
    create_test_users()
