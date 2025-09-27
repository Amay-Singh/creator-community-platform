#!/usr/bin/env python3
"""
Debug Authentication Issues
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'creator_platform.settings')
django.setup()

from accounts.models import CustomUser
from accounts.serializers import UserRegistrationSerializer

def test_user_creation():
    """Test basic user creation"""
    print("=== TESTING USER CREATION ===")
    
    try:
        # Test direct model creation
        print("1. Testing direct CustomUser creation...")
        user_data = {
            'username': 'testuser_direct',
            'email': 'test_direct@example.com',
            'password': 'TestPass123!'
        }
        
        user = CustomUser.objects.create_user(**user_data)
        print(f"✅ Direct user creation successful: {user.username}")
        user.delete()  # Clean up
        
    except Exception as e:
        print(f"❌ Direct user creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    try:
        # Test serializer creation
        print("\n2. Testing UserRegistrationSerializer...")
        serializer_data = {
            'username': 'testuser_serializer',
            'email': 'test_serializer@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
        serializer = UserRegistrationSerializer(data=serializer_data)
        if serializer.is_valid():
            user = serializer.save()
            print(f"✅ Serializer user creation successful: {user.username}")
            user.delete()  # Clean up
        else:
            print(f"❌ Serializer validation failed: {serializer.errors}")
            
    except Exception as e:
        print(f"❌ Serializer user creation failed: {str(e)}")
        import traceback
        traceback.print_exc()

def test_imports():
    """Test all imports used in authentication"""
    print("\n=== TESTING IMPORTS ===")
    
    try:
        from accounts.models import CustomUser, CreatorProfile, PortfolioItem, ProfileFeedback
        print("✅ Models import successful")
    except Exception as e:
        print(f"❌ Models import failed: {str(e)}")
    
    try:
        from accounts.authentication import ApprovalCode
        print("✅ ApprovalCode import successful")
    except Exception as e:
        print(f"❌ ApprovalCode import failed: {str(e)}")
    
    try:
        from accounts.serializers import UserRegistrationSerializer, UserLoginSerializer
        print("✅ Serializers import successful")
    except Exception as e:
        print(f"❌ Serializers import failed: {str(e)}")

if __name__ == "__main__":
    test_imports()
    test_user_creation()
