#!/usr/bin/env python
"""
Script to create test users for White Beat platform with Admin group
Run: python create_test_users.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_beat.settings')
django.setup()

from django.contrib.auth.models import User, Group
from api.models import UserProfile

def create_test_users():
    """Create test users for development"""
    
    print("🚀 Creating test users with Admin group...\n")
    
    # Create Admin group if it doesn't exist
    print("📋 Creating Admin group...")
    admin_group, created = Group.objects.get_or_create(name='Admin')
    if created:
        print("   ✅ Admin group created successfully!\n")
    else:
        print("   ℹ️ Admin group already exists\n")
    
    # Test User 1: Regular user
    print("1️⃣ Creating regular user 'aryan'...")
    try:
        user1, created = User.objects.get_or_create(
            username='aryan',
            defaults={
                'email': 'aryan@whitebeat.com',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            user1.set_password('aryan123')
            user1.save()
        
        profile1, _ = UserProfile.objects.get_or_create(
            user=user1,
            defaults={'role': 'user'}
        )
        
        if created:
            print("   ✅ User 'aryan' created successfully!")
        else:
            print("   ℹ️ User 'aryan' already exists")
        print(f"   📧 Email: aryan@whitebeat.com")
        print(f"   🔑 Password: aryan123")
        print(f"   👤 Role: User")
        print(f"   🏷️ Groups: {list(user1.groups.values_list('name', flat=True))}\n")
    except Exception as e:
        print(f"   ⚠️ Error with user 'aryan': {e}\n")
    
    # Test User 2: Another regular user
    print("2️⃣ Creating regular user 'john'...")
    try:
        user2, created = User.objects.get_or_create(
            username='john',
            defaults={
                'email': 'john@whitebeat.com',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            user2.set_password('john123')
            user2.save()
        
        profile2, _ = UserProfile.objects.get_or_create(
            user=user2,
            defaults={'role': 'user'}
        )
        
        if created:
            print("   ✅ User 'john' created successfully!")
        else:
            print("   ℹ️ User 'john' already exists")
        print(f"   📧 Email: john@whitebeat.com")
        print(f"   🔑 Password: john123")
        print(f"   👤 Role: User")
        print(f"   🏷️ Groups: {list(user2.groups.values_list('name', flat=True))}\n")
    except Exception as e:
        print(f"   ⚠️ Error with user 'john': {e}\n")
    
    # Test Admin: User in Admin group
    print("3️⃣ Creating admin user 'admin' (in Admin group)...")
    try:
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@whitebeat.com',
                'is_staff': True,
                'is_superuser': False
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        
        # Add to Admin group
        admin.groups.add(admin_group)
        admin.save()
        
        profile_admin, _ = UserProfile.objects.get_or_create(
            user=admin,
            defaults={'role': 'admin'}
        )
        profile_admin.role = 'admin'
        profile_admin.save()
        
        if created:
            print("   ✅ Admin 'admin' created successfully!")
        else:
            print("   ℹ️ Admin 'admin' already exists")
        print(f"   📧 Email: admin@whitebeat.com")
        print(f"   🔑 Password: admin123")
        print(f"   🔐 Role: Admin")
        print(f"   🏷️ Groups: {list(admin.groups.values_list('name', flat=True))}\n")
    except Exception as e:
        print(f"   ⚠️ Error with admin 'admin': {e}\n")
    
    # Test Admin 2: Another admin user
    print("4️⃣ Creating admin user 'superadmin' (in Admin group)...")
    try:
        superadmin, created = User.objects.get_or_create(
            username='superadmin',
            defaults={
                'email': 'superadmin@whitebeat.com',
                'is_staff': True,
                'is_superuser': False
            }
        )
        if created:
            superadmin.set_password('super123')
            superadmin.save()
        
        # Add to Admin group
        superadmin.groups.add(admin_group)
        superadmin.save()
        
        profile_superadmin, _ = UserProfile.objects.get_or_create(
            user=superadmin,
            defaults={'role': 'admin'}
        )
        profile_superadmin.role = 'admin'
        profile_superadmin.save()
        
        if created:
            print("   ✅ Admin 'superadmin' created successfully!")
        else:
            print("   ℹ️ Admin 'superadmin' already exists")
        print(f"   📧 Email: superadmin@whitebeat.com")
        print(f"   🔑 Password: super123")
        print(f"   🔐 Role: Admin")
        print(f"   🏷️ Groups: {list(superadmin.groups.values_list('name', flat=True))}\n")
    except Exception as e:
        print(f"   ⚠️ Error with admin 'superadmin': {e}\n")
    
    print("=" * 70)
    print("✅ Test users creation complete!\n")
    print("📝 Login Credentials:\n")
    print("Regular Users (→ User Dashboard):")
    print("  Username: aryan        | Password: aryan123")
    print("  Username: john         | Password: john123\n")
    print("Admin Users (→ Admin Dashboard - in 'Admin' group):")
    print("  Username: admin        | Password: admin123")
    print("  Username: superadmin   | Password: super123\n")
    print("🔐 Admin Access:")
    print("  - Only users in 'Admin' group can access Admin Dashboard")
    print("  - Use /api/make-admin/ to add users to Admin group")
    print("  - Use /api/remove-admin/ to remove users from Admin group\n")
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend:  http://localhost:8000")
    print("=" * 70)
    
    # Show group summary
    print("\n📊 Group Summary:")
    print(f"   Total users: {User.objects.count()}")
    print(f"   Admin group members: {User.objects.filter(groups__name='Admin').count()}")
    print(f"   Regular users: {User.objects.exclude(groups__name='Admin').count()}")

if __name__ == '__main__':
    create_test_users()
