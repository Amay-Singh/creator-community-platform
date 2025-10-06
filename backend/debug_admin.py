#!/usr/bin/env python
"""
Debug script to test admin functionality locally with production database
This will show exact error messages and stack traces
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'creator_platform.settings')

# Load debug environment
from dotenv import load_dotenv
load_dotenv('.env.debug')

# Initialize Django
django.setup()

def test_admin_functionality():
    """Test admin functionality step by step with detailed error reporting"""
    print("🔍 DEBUGGING ADMIN FUNCTIONALITY")
    print("=" * 50)
    
    try:
        # Test 1: Import Django admin
        print("1. Testing Django admin import...")
        from django.contrib import admin
        print("   ✅ Django admin imported successfully")
        
        # Test 2: Test database connection
        print("2. Testing database connection...")
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        print(f"   ✅ Database connected: {result}")
        
        # Test 3: Test user model
        print("3. Testing user model...")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_users = User.objects.filter(is_superuser=True)
        print(f"   ✅ Found {admin_users.count()} admin users")
        
        if admin_users.exists():
            admin_user = admin_users.first()
            print(f"   📋 Admin user: {admin_user.email}")
            print(f"   📋 Is active: {admin_user.is_active}")
            print(f"   📋 Is staff: {admin_user.is_staff}")
        
        # Test 4: Test authentication
        print("4. Testing authentication...")
        from django.contrib.auth import authenticate
        user = authenticate(username='admin@creator-platform.com', password='CreatorPlatform2024!')
        if user:
            print(f"   ✅ Authentication successful for {user.email}")
        else:
            print("   ❌ Authentication failed")
            return
        
        # Test 5: Test admin site loading
        print("5. Testing admin site loading...")
        admin_models = len(admin.site._registry)
        print(f"   ✅ Admin site loaded with {admin_models} registered models")
        
        # Test 6: Test each app's admin
        print("6. Testing individual app admin modules...")
        from django.apps import apps
        
        for app_config in apps.get_app_configs():
            app_name = app_config.name
            if app_name.startswith('django.') or app_name.startswith('rest_framework'):
                continue
                
            try:
                admin_module = f"{app_name}.admin"
                __import__(admin_module)
                print(f"   ✅ {app_name}: Admin module loaded")
            except ImportError:
                print(f"   ⚠️  {app_name}: No admin module")
            except Exception as e:
                print(f"   ❌ {app_name}: Admin error - {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Test 7: Simulate admin login process
        print("7. Testing admin login simulation...")
        from django.test import RequestFactory
        from django.contrib.auth.views import LoginView
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.auth.middleware import AuthenticationMiddleware
        
        factory = RequestFactory()
        request = factory.post('/admin/login/', {
            'username': 'admin@creator-platform.com',
            'password': 'CreatorPlatform2024!',
            'next': '/admin/'
        })
        
        # Add required middleware attributes
        SessionMiddleware(lambda x: None).process_request(request)
        request.session.save()
        MessageMiddleware(lambda x: None).process_request(request)
        AuthenticationMiddleware(lambda x: None).process_request(request)
        
        print("   ✅ Admin login simulation setup complete")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("If admin is still failing, the issue might be in the actual HTTP request handling.")
        
    except Exception as e:
        print(f"\n❌ ERROR FOUND: {str(e)}")
        print("\n📋 FULL STACK TRACE:")
        import traceback
        traceback.print_exc()
        print("\n🎯 This is likely the cause of your 500 error!")

if __name__ == "__main__":
    test_admin_functionality()
