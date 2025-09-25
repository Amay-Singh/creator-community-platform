#!/usr/bin/env python3
"""
Test Registration View Directly
"""
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'creator_platform.settings')
django.setup()

from django.test import RequestFactory
from accounts.simple_views import RegisterView
from django.http import HttpRequest

def test_registration_view():
    """Test registration view directly"""
    print("=== TESTING REGISTRATION VIEW ===")
    
    try:
        # Create a mock request
        factory = RequestFactory()
        data = {
            'username': 'testuser_view',
            'email': 'test_view@example.com', 
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
        request = factory.post('/api/auth/register/', 
                              data=json.dumps(data),
                              content_type='application/json')
        
        # Test the view
        view = RegisterView()
        view.request = request
        view.format_kwarg = None
        
        response = view.create(request)
        print(f"✅ Registration view successful: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Clean up
        from accounts.models import CustomUser
        try:
            user = CustomUser.objects.get(email='test_view@example.com')
            user.delete()
        except:
            pass
            
    except Exception as e:
        print(f"❌ Registration view failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_registration_view()
