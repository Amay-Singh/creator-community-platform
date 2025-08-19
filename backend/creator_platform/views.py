"""
Main views for Creator Platform
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def api_status(request):
    """API status endpoint"""
    return JsonResponse({
        'status': 'online',
        'message': 'Creator Community Platform API is running',
        'version': '1.0.0',
        'endpoints': {
            'authentication': '/api/auth/',
            'personality_quizzes': '/api/auth/personality/quizzes/',
            'collaboration_matches': '/api/auth/matches/',
            'chat': '/api/chat/',
            'collaborations': '/api/collaborations/',
            'ai_services': '/api/ai/',
            'admin': '/admin/'
        }
    })
