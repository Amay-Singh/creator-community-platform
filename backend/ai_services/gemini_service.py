"""
Google Gemini AI Service Integration
Production-ready AI service using Google Gemini API
"""
import os
import requests
import json
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    """Google Gemini AI Service"""
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY', '')
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta'
        self.model = 'gemini-pro'
    
    def is_configured(self):
        """Check if Gemini is properly configured"""
        return bool(self.api_key)
    
    def generate_content(self, prompt, max_tokens=1000):
        """Generate content using Gemini"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Gemini API key not configured',
                'content': 'AI service not available'
            }
        
        try:
            url = f"{self.base_url}/models/{self.model}:generateContent"
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                'contents': [{
                    'parts': [{
                        'text': prompt
                    }]
                }],
                'generationConfig': {
                    'maxOutputTokens': max_tokens,
                    'temperature': 0.7
                }
            }
            
            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                
                return {
                    'success': True,
                    'content': content,
                    'model': self.model,
                    'timestamp': timezone.now()
                }
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}',
                    'content': 'Error generating content'
                }
                
        except Exception as e:
            logger.error(f"Gemini service error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'content': 'Service temporarily unavailable'
            }
    
    def generate_creator_match_explanation(self, creator1, creator2):
        """Generate AI explanation for creator matching"""
        prompt = f"""
        Explain why these two creators would be a good collaboration match:
        
        Creator 1: {creator1.get('name', 'Creator')} - {creator1.get('skills', 'Various skills')}
        Creator 2: {creator2.get('name', 'Creator')} - {creator2.get('skills', 'Various skills')}
        
        Provide a brief, encouraging explanation of their collaboration potential.
        """
        
        return self.generate_content(prompt, max_tokens=200)
    
    def generate_content_ideas(self, topic, content_type='blog'):
        """Generate content ideas"""
        prompt = f"""
        Generate 3 creative {content_type} ideas about {topic}.
        Make them engaging and actionable.
        Format as a numbered list.
        """
        
        return self.generate_content(prompt, max_tokens=300)
    
    def health_check(self):
        """Check Gemini service health"""
        if not self.is_configured():
            return {
                'status': 'unhealthy',
                'error': 'API key not configured',
                'configured': False
            }
        
        try:
            # Simple test generation
            result = self.generate_content("Say 'Hello from Gemini!'", max_tokens=50)
            
            return {
                'status': 'healthy' if result['success'] else 'unhealthy',
                'configured': True,
                'model': self.model,
                'test_successful': result['success'],
                'timestamp': timezone.now()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'configured': True,
                'timestamp': timezone.now()
            }

# Global instance
gemini_service = GeminiService()
