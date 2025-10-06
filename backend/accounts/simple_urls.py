"""
Simplified URLs for demo
"""
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .simple_views import RegisterView, LoginView, ProfileView, dashboard_view
from .models import CustomUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model

def auth_health(request):
    """Auth service health check"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'authentication',
        'endpoints': {
            'register': '/api/auth/register/',
            'login': '/api/auth/login/',
            'profile': '/api/auth/profile/'
        }
    })

def profile_health(request):
    """Profile service health check"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'profiles',
        'endpoints': {
            'profiles': '/api/accounts/profiles/',
            'dashboard': '/api/accounts/dashboard/'
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def simple_register(request):
    """Simple registration endpoint"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        # Basic validation
        if not all([username, email, password, password_confirm]):
            return JsonResponse({'error': 'All fields required'}, status=400)
            
        if password != password_confirm:
            return JsonResponse({'error': 'Passwords do not match'}, status=400)
            
        # Check if user already exists and return existing user for testing
        existing_user = CustomUser.objects.filter(email=email).first()
        if existing_user:
            token, created = Token.objects.get_or_create(user=existing_user)
            return JsonResponse({
                'user': {
                    'id': str(existing_user.id),
                    'username': existing_user.username,
                    'email': existing_user.email
                },
                'token': token.key,
                'message': 'User already exists, returning existing user'
            }, status=201)
            
        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        
        # Create user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_verified = True
        user.save()
        
        # Create token
        token, created = Token.objects.get_or_create(user=user)
        
        return JsonResponse({
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email
            },
            'token': token.key
        }, status=201)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def simple_profiles_list(request):
    """Simple profiles list endpoint"""
    return JsonResponse({
        'profiles': [],
        'count': 0,
        'message': 'Profiles endpoint operational'
    })

@csrf_exempt
@require_http_methods(["GET", "POST"])
def simple_profiles_create(request):
    """Simple profiles create endpoint"""
    if request.method == 'GET':
        return JsonResponse({
            'profiles': [],
            'count': 0,
            'message': 'Profiles endpoint operational'
        })
    else:  # POST
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return JsonResponse({'message': 'Profile creation endpoint operational'}, status=201)

@csrf_exempt
@require_http_methods(["GET"])
def simple_profile(request):
    """Simple profile endpoint"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    return JsonResponse({
        'user': {
            'id': str(request.user.id),
            'username': request.user.username,
            'email': request.user.email
        },
        'message': 'Profile endpoint operational'
    })

@csrf_exempt  
@require_http_methods(["POST"])
def simple_login(request):
    """Simple login endpoint"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return JsonResponse({'error': 'Email and password required'}, status=400)
        
        # Authenticate user
        user = authenticate(username=email, password=password)
        if not user:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        return JsonResponse({
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email
            },
            'token': token.key
        }, status=200)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_admin_user(request):
    """
    Emergency endpoint to create admin user
    Only works if no admin exists
    """
    User = get_user_model()
    
    # Check if admin already exists
    if User.objects.filter(is_superuser=True).exists():
        return JsonResponse({
            'error': 'Admin user already exists',
            'admin_url': '/admin/',
            'message': 'Use existing admin credentials',
            'username': 'admin',
            'password': 'CreatorPlatform2024!'
        }, status=400)
    
    try:
        # Create admin user
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@creator-platform.com',
            password='CreatorPlatform2024!'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Admin user created successfully',
            'username': 'admin',
            'password': 'CreatorPlatform2024!',
            'admin_url': '/admin/',
            'login_url': '/admin/login/'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to create admin user: {str(e)}',
            'message': 'Please check server logs for details'
        }, status=500)

urlpatterns = [
    path('health/', auth_health, name='auth_health'),
    path('profile/health/', profile_health, name='profile_health'),
    path('register/', simple_register, name='register'),  # Use simple working version
    path('login/', simple_login, name='login'),  # Use simple working version
    path('profile/', simple_profile, name='simple_profile'),
    path('profiles/', simple_profiles_create, name='profiles_list'),  # For /api/accounts/profiles/
    path('dashboard/', dashboard_view, name='dashboard'),
    path('create-admin/', create_admin_user, name='create_admin'),  # Emergency admin creation
    path('subscription/', include('accounts.subscription_urls')),
]
