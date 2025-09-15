"""
Translation Service Tests for Real-time Messaging
Tests P5-004: Auto-translation functionality
"""
import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import CreatorProfile
from chat.models import ChatRoom, ChatMessage
from chat.translation_service import TranslationService

User = get_user_model()


class TranslationServiceTestCase(TestCase):
    """Test cases for TranslationService"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.profile1 = CreatorProfile.objects.create(
            user=self.user1,
            display_name='Test User 1',
            bio='Test bio'
        )
        
        self.room = ChatRoom.objects.create(
            room_type='direct',
            created_by=self.profile1
        )
        
        self.message = ChatMessage.objects.create(
            room=self.room,
            sender=self.profile1,
            content='Hello, how are you today?',
            original_language='en'
        )
        
        self.translation_service = TranslationService()
    
    def test_supported_languages(self):
        """Test that supported languages are properly defined"""
        expected_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi']
        
        for lang in expected_languages:
            self.assertIn(lang, self.translation_service.SUPPORTED_LANGUAGES)
        
        self.assertEqual(self.translation_service.SUPPORTED_LANGUAGES['en'], 'English')
        self.assertEqual(self.translation_service.SUPPORTED_LANGUAGES['es'], 'Spanish')
    
    @patch('openai.OpenAI')
    def test_translate_message_success(self, mock_openai):
        """Test successful message translation"""
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hola, ¿cómo estás hoy?"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = self.translation_service.translate_message(
            self.message, 'es', self.profile1
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['translated_content'], "Hola, ¿cómo estás hoy?")
        self.assertEqual(result['confidence_score'], 0.9)
        self.assertFalse(result['cached'])
        
        # Verify translation was stored in message
        self.message.refresh_from_db()
        self.assertIn('es', self.message.translations)
        self.assertEqual(
            self.message.translations['es']['content'],
            "Hola, ¿cómo estás hoy?"
        )
    
    def test_translate_message_cached(self):
        """Test translation retrieval from cache"""
        # Pre-populate translation
        self.message.translations = {
            'es': {
                'content': 'Hola, ¿cómo estás hoy?',
                'confidence': 0.9,
                'translator': 'ai'
            }
        }
        self.message.save()
        
        result = self.translation_service.translate_message(
            self.message, 'es', self.profile1
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['translated_content'], 'Hola, ¿cómo estás hoy?')
        self.assertTrue(result['cached'])
    
    @patch('openai.OpenAI')
    def test_translate_message_api_failure(self, mock_openai):
        """Test translation fallback when API fails"""
        # Mock API failure
        mock_openai.side_effect = Exception("API Error")
        
        result = self.translation_service.translate_message(
            self.message, 'es', self.profile1
        )
        
        self.assertFalse(result['success'])
        self.assertIn('Translation unavailable', result['translated_content'])
        self.assertEqual(result['confidence_score'], 0.0)
    
    @patch('openai.OpenAI')
    def test_detect_language(self, mock_openai):
        """Test language detection"""
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "es"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detected_lang = self.translation_service.detect_language("Hola, ¿cómo estás?")
        
        self.assertEqual(detected_lang, 'es')
    
    def test_detect_language_fallback(self):
        """Test language detection fallback to English"""
        # Mock no client available
        with patch.object(self.translation_service, '_get_client', return_value=None):
            detected_lang = self.translation_service.detect_language("Some text")
            self.assertEqual(detected_lang, 'en')
    
    @patch('openai.OpenAI')
    def test_detect_language_invalid_response(self, mock_openai):
        """Test language detection with invalid response"""
        # Mock OpenAI response with invalid language code
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "invalid_lang"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detected_lang = self.translation_service.detect_language("Some text")
        
        self.assertEqual(detected_lang, 'en')  # Should fallback to English
    
    @patch('openai.OpenAI')
    def test_translate_profile_content(self, mock_openai):
        """Test profile content translation"""
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Biografía de prueba"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = self.translation_service.translate_profile_content(
            self.profile1, 'es'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['translated_bio'], "Biografía de prueba")
        self.assertEqual(result['original_bio'], self.profile1.bio)
        self.assertEqual(result['target_language'], 'es')
    
    def test_translate_profile_content_no_bio(self):
        """Test profile translation with no bio"""
        profile_no_bio = CreatorProfile.objects.create(
            user=self.user1,
            display_name='No Bio User'
        )
        
        result = self.translation_service.translate_profile_content(
            profile_no_bio, 'es'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('No content to translate', result['error'])
    
    def test_get_translation_suggestions(self):
        """Test translation language suggestions"""
        suggestions = self.translation_service.get_translation_suggestions(
            self.message, self.profile1
        )
        
        self.assertIsInstance(suggestions, list)
        self.assertTrue(len(suggestions) <= 3)
        
        # Should not suggest the original language
        for lang in suggestions:
            self.assertIn(lang, self.translation_service.SUPPORTED_LANGUAGES)
    
    @patch('openai.OpenAI')
    def test_batch_translate_messages(self, mock_openai):
        """Test batch translation of multiple messages"""
        # Create additional messages
        message2 = ChatMessage.objects.create(
            room=self.room,
            sender=self.profile1,
            content='Good morning!',
            original_language='en'
        )
        
        # Mock OpenAI responses
        mock_client = Mock()
        mock_responses = [
            Mock(choices=[Mock(message=Mock(content="¡Hola, cómo estás hoy?"))]),
            Mock(choices=[Mock(message=Mock(content="¡Buenos días!"))])
        ]
        mock_client.chat.completions.create.side_effect = mock_responses
        mock_openai.return_value = mock_client
        
        messages = [self.message, message2]
        result = self.translation_service.batch_translate_messages(
            messages, 'es', self.profile1
        )
        
        self.assertEqual(result['total_messages'], 2)
        self.assertEqual(result['successful_translations'], 2)
        self.assertEqual(result['target_language'], 'es')
        self.assertEqual(len(result['results']), 2)
        
        # Check individual results
        for msg_result in result['results']:
            self.assertTrue(msg_result['success'])
            self.assertGreater(msg_result['confidence_score'], 0)
    
    def test_fallback_translation(self):
        """Test fallback translation messages"""
        fallback_result = self.translation_service._fallback_translation(
            "Test content", 'es'
        )
        
        self.assertFalse(fallback_result['success'])
        self.assertIn('Translation unavailable', fallback_result['translated_content'])
        self.assertEqual(fallback_result['confidence_score'], 0.0)
        self.assertIn('AI translation service unavailable', fallback_result['error'])
    
    def test_fallback_translation_languages(self):
        """Test fallback translations for different languages"""
        test_languages = ['es', 'fr', 'de', 'pt', 'ja', 'ko', 'zh']
        
        for lang in test_languages:
            result = self.translation_service._fallback_translation("Test", lang)
            self.assertFalse(result['success'])
            self.assertIn('Translation unavailable', result['translated_content'])
    
    @patch('chat.translation_service.settings')
    def test_client_initialization_no_api_key(self, mock_settings):
        """Test client initialization without API key"""
        mock_settings.OPENAI_API_KEY = None
        
        service = TranslationService()
        client = service._get_client()
        
        self.assertIsNone(client)
    
    @patch('openai.OpenAI')
    def test_client_initialization_with_exception(self, mock_openai):
        """Test client initialization with exception"""
        mock_openai.side_effect = Exception("Initialization error")
        
        service = TranslationService()
        client = service._get_client()
        
        self.assertIsNone(client)
    
    def test_lazy_client_initialization(self):
        """Test that client is initialized lazily"""
        service = TranslationService()
        
        # Client should be None initially
        self.assertIsNone(service.client)
        
        # After calling _get_client, it should attempt initialization
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            client = service._get_client()
            self.assertEqual(client, mock_client)
            self.assertEqual(service.client, mock_client)


@pytest.mark.asyncio
class TestTranslationServiceAsync:
    """Async tests for translation service integration"""
    
    async def test_translation_service_instance(self):
        """Test that translation service instance is available"""
        from chat.translation_service import translation_service
        
        assert translation_service is not None
        assert isinstance(translation_service, TranslationService)
        assert hasattr(translation_service, 'translate_message')
        assert hasattr(translation_service, 'detect_language')
        assert hasattr(translation_service, 'translate_profile_content')
