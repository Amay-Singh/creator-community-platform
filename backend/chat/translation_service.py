"""
Real-time Translation Service
Implements REQ-11: Real-time translation for chats and profiles
"""
import openai
from django.conf import settings
from typing import Dict, List, Optional
from .enhanced_models import Message, TranslationRequest
from accounts.models import CreatorProfile

class TranslationService:
    """
    AI-powered real-time translation service
    """
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish', 
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
        'ar': 'Arabic',
        'hi': 'Hindi'
    }
    
    def __init__(self):
        self.client = None
    
    def _get_client(self):
        """Lazy initialization of OpenAI client"""
        if self.client is None:
            try:
                self.client = openai.OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', None))
            except Exception:
                self.client = None
        return self.client
    
    def translate_message(self, message: Message, target_language: str, requester: CreatorProfile) -> Dict:
        """
        Translate a message to target language
        
        Args:
            message: Message to translate
            target_language: Target language code
            requester: Profile requesting translation
        
        Returns:
            Dict with translation results
        """
        
        # Check if translation already exists
        existing_translation = message.translations.get(target_language)
        if existing_translation:
            return {
                'success': True,
                'translated_content': existing_translation['content'],
                'confidence_score': existing_translation.get('confidence', 0.9),
                'cached': True
            }
        
        # Perform new translation
        client = self._get_client()
        if not client:
            return self._fallback_translation(message.content, target_language)
        
        try:
            target_lang_name = self.SUPPORTED_LANGUAGES.get(target_language, target_language)
            
            prompt = f"""
            Translate the following message to {target_lang_name}. 
            Maintain the tone, context, and any creative/artistic terminology.
            If the message contains slang or creative expressions, provide culturally appropriate equivalents.
            
            Original message: "{message.content}"
            
            Provide only the translation, no explanations.
            """
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator specializing in creative and artistic communications. Translate accurately while preserving tone and cultural context."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            translated_content = response.choices[0].message.content.strip()
            confidence_score = 0.9  # High confidence for GPT-4 translations
            
            # Store translation in message
            if not message.translations:
                message.translations = {}
            
            message.translations[target_language] = {
                'content': translated_content,
                'confidence': confidence_score,
                'translator': 'ai'
            }
            message.is_translated = True
            message.save()
            
            # Create translation request record
            TranslationRequest.objects.create(
                message=message,
                requester=requester,
                target_language=target_language,
                translated_content=translated_content,
                confidence_score=confidence_score
            )
            
            return {
                'success': True,
                'translated_content': translated_content,
                'confidence_score': confidence_score,
                'cached': False
            }
        
        except Exception as e:
            return self._fallback_translation(message.content, target_language)
    
    def translate_profile_content(self, profile: CreatorProfile, target_language: str) -> Dict:
        """
        Translate profile bio and other content
        
        Args:
            profile: CreatorProfile to translate
            target_language: Target language code
        
        Returns:
            Dict with translated profile content
        """
        
        client = self._get_client()
        if not client or not profile.bio:
            return {'success': False, 'error': 'No content to translate or translation unavailable'}
        
        try:
            target_lang_name = self.SUPPORTED_LANGUAGES.get(target_language, target_language)
            
            prompt = f"""
            Translate this creator profile bio to {target_lang_name}.
            Maintain the personal tone and artistic expression.
            Keep any specific artistic terms or techniques mentioned.
            
            Bio: "{profile.bio}"
            
            Provide only the translation.
            """
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are translating creative professional profiles. Maintain artistic terminology and personal expression."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            translated_bio = response.choices[0].message.content.strip()
            
            return {
                'success': True,
                'translated_bio': translated_bio,
                'original_bio': profile.bio,
                'target_language': target_language
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of given text
        
        Args:
            text: Text to analyze
        
        Returns:
            Language code
        """
        
        client = self._get_client()
        if not client:
            return 'en'  # Default to English
        
        try:
            prompt = f"""
            Detect the language of this text and respond with only the 2-letter language code (e.g., 'en', 'es', 'fr'):
            
            "{text}"
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a language detection system. Respond only with the 2-letter ISO language code."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            detected_lang = response.choices[0].message.content.strip().lower()
            
            # Validate detected language
            if detected_lang in self.SUPPORTED_LANGUAGES:
                return detected_lang
            else:
                return 'en'  # Default to English if detection fails
        
        except Exception:
            return 'en'
    
    def get_translation_suggestions(self, message: Message, user_profile: CreatorProfile) -> List[str]:
        """
        Get suggested languages for translation based on chat participants
        
        Args:
            message: Message to get suggestions for
            user_profile: User requesting suggestions
        
        Returns:
            List of suggested language codes
        """
        
        suggestions = []
        
        # Get languages from chat room participants
        room_participants = message.room.participants.exclude(id=user_profile.id)
        
        # This would ideally check participant language preferences
        # For now, suggest common languages
        common_languages = ['es', 'fr', 'de', 'pt', 'ja', 'ko', 'zh']
        
        # Detect original message language
        original_lang = self.detect_language(message.content)
        
        # Suggest different languages from original
        for lang in common_languages:
            if lang != original_lang and len(suggestions) < 3:
                suggestions.append(lang)
        
        return suggestions
    
    def _fallback_translation(self, content: str, target_language: str) -> Dict:
        """
        Fallback translation when AI is unavailable
        """
        
        # Simple fallback messages
        fallback_translations = {
            'es': '[Traducción no disponible - Translation unavailable]',
            'fr': '[Traduction non disponible - Translation unavailable]', 
            'de': '[Übersetzung nicht verfügbar - Translation unavailable]',
            'pt': '[Tradução indisponível - Translation unavailable]',
            'ja': '[翻訳利用不可 - Translation unavailable]',
            'ko': '[번역 불가 - Translation unavailable]',
            'zh': '[翻译不可用 - Translation unavailable]'
        }
        
        fallback_content = fallback_translations.get(target_language, '[Translation unavailable]')
        
        return {
            'success': False,
            'translated_content': fallback_content,
            'confidence_score': 0.0,
            'error': 'AI translation service unavailable'
        }
    
    def batch_translate_messages(self, messages: List[Message], target_language: str, requester: CreatorProfile) -> Dict:
        """
        Translate multiple messages in batch
        
        Args:
            messages: List of messages to translate
            target_language: Target language code
            requester: Profile requesting translations
        
        Returns:
            Dict with batch translation results
        """
        
        results = []
        success_count = 0
        
        for message in messages:
            result = self.translate_message(message, target_language, requester)
            results.append({
                'message_id': str(message.id),
                'success': result['success'],
                'translated_content': result.get('translated_content', ''),
                'confidence_score': result.get('confidence_score', 0.0)
            })
            
            if result['success']:
                success_count += 1
        
        return {
            'total_messages': len(messages),
            'successful_translations': success_count,
            'target_language': target_language,
            'results': results
        }

# Service instance
translation_service = TranslationService()
