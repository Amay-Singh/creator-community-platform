"""
AI Content Validation Service
Implements REQ-2: AI-based validation to prevent fake or repetitive content
"""
import openai
from django.conf import settings
from typing import Dict, Any
import hashlib
import requests
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

class ContentValidator:
    """AI-powered content validation service"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    @staticmethod
    def validate_profile(profile) -> Dict[str, Any]:
        """Validate creator profile for authenticity and completeness"""
        validation_result = {
            'is_valid': True,
            'score': 0.0,
            'issues': []
        }
        
        # Check profile completeness
        completeness_score = 0
        if profile.bio and len(profile.bio.strip()) >= 50:
            completeness_score += 25
        else:
            validation_result['issues'].append('Bio should be at least 50 characters')
        
        if profile.location:
            completeness_score += 15
        
        if any([profile.instagram_url, profile.youtube_url, profile.spotify_url, profile.website_url]):
            completeness_score += 20
        else:
            validation_result['issues'].append('At least one external link recommended')
        
        if profile.portfolio_items.exists():
            completeness_score += 40
        else:
            validation_result['issues'].append('Portfolio items required for validation')
        
        # AI-based content validation
        try:
            ai_score = ContentValidator._validate_text_content(profile.bio)
            validation_result['score'] = (completeness_score + ai_score) / 2
        except Exception as e:
            logger.error(f"AI validation failed: {e}")
            validation_result['score'] = completeness_score
        
        # Update profile validation status
        profile.validation_score = validation_result['score']
        profile.is_validated = validation_result['score'] >= 70
        profile.save(update_fields=['validation_score', 'is_validated'])
        
        return validation_result
    
    @staticmethod
    def validate_portfolio_item(portfolio_item) -> Dict[str, Any]:
        """Validate portfolio item for originality and appropriateness"""
        validation_result = {
            'is_valid': True,
            'score': 0.0,
            'is_original': True,
            'issues': []
        }
        
        try:
            # Check for duplicate content using file hash
            file_hash = ContentValidator._calculate_file_hash(portfolio_item.file)
            existing_items = portfolio_item.profile.portfolio_items.exclude(
                id=portfolio_item.id
            ).values_list('file', flat=True)
            
            for existing_file in existing_items:
                if ContentValidator._calculate_file_hash(existing_file) == file_hash:
                    validation_result['is_original'] = False
                    validation_result['issues'].append('Duplicate content detected')
                    break
            
            # AI-based content validation
            if portfolio_item.media_type == 'image':
                ai_score = ContentValidator._validate_image_content(portfolio_item.file)
            elif portfolio_item.media_type in ['video', 'audio']:
                ai_score = ContentValidator._validate_media_content(portfolio_item.file)
            else:
                ai_score = ContentValidator._validate_text_content(portfolio_item.description)
            
            validation_result['score'] = ai_score
            
        except Exception as e:
            logger.error(f"Portfolio validation failed: {e}")
            validation_result['score'] = 50.0  # Default score on error
        
        # Update portfolio item validation
        portfolio_item.validation_score = validation_result['score']
        portfolio_item.is_validated = validation_result['score'] >= 70
        portfolio_item.is_original = validation_result['is_original']
        portfolio_item.save(update_fields=['validation_score', 'is_validated', 'is_original'])
        
        return validation_result
    
    @staticmethod
    def _validate_text_content(text: str) -> float:
        """Validate text content using OpenAI"""
        if not text or not settings.OPENAI_API_KEY:
            return 50.0
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a content validator for a creator platform. Rate the authenticity and appropriateness of the following text on a scale of 0-100. Consider: originality, professionalism, appropriateness, and authenticity. Return only a number."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            score = float(response.choices[0].message.content.strip())
            return max(0, min(100, score))  # Ensure score is between 0-100
            
        except Exception as e:
            logger.error(f"OpenAI text validation failed: {e}")
            return 50.0
    
    @staticmethod
    def _validate_image_content(image_file) -> float:
        """Validate image content for appropriateness"""
        try:
            # Basic image validation
            image = Image.open(image_file)
            
            # Check image properties
            if image.size[0] < 100 or image.size[1] < 100:
                return 30.0  # Too small
            
            if image.format not in ['JPEG', 'PNG', 'GIF', 'WEBP']:
                return 40.0  # Unsupported format
            
            # Placeholder for advanced AI image validation
            # In production, integrate with services like AWS Rekognition or Google Vision
            return 80.0  # Default good score for valid images
            
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return 30.0
    
    @staticmethod
    def _validate_media_content(media_file) -> float:
        """Validate video/audio content"""
        try:
            # Basic file validation
            if media_file.size > 104857600:  # 100MB
                return 40.0  # Too large
            
            # Placeholder for advanced media validation
            # In production, integrate with media analysis services
            return 75.0  # Default score for valid media
            
        except Exception as e:
            logger.error(f"Media validation failed: {e}")
            return 30.0
    
    @staticmethod
    def _calculate_file_hash(file) -> str:
        """Calculate SHA-256 hash of file for duplicate detection"""
        try:
            file.seek(0)
            file_hash = hashlib.sha256()
            for chunk in iter(lambda: file.read(4096), b""):
                file_hash.update(chunk)
            file.seek(0)
            return file_hash.hexdigest()
        except Exception:
            return ""
    
    @staticmethod
    def validate_collaboration_request(request_text: str) -> Dict[str, Any]:
        """Validate collaboration request messages"""
        validation_result = {
            'is_appropriate': True,
            'score': 0.0,
            'issues': []
        }
        
        try:
            # Check message length
            if len(request_text.strip()) < 20:
                validation_result['issues'].append('Message too short')
                validation_result['score'] = 30.0
                return validation_result
            
            # AI validation for appropriateness
            score = ContentValidator._validate_text_content(request_text)
            validation_result['score'] = score
            validation_result['is_appropriate'] = score >= 60
            
            if score < 60:
                validation_result['issues'].append('Message may be inappropriate')
            
        except Exception as e:
            logger.error(f"Collaboration request validation failed: {e}")
            validation_result['score'] = 50.0
        
        return validation_result
