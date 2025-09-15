"""
Tests for AI Content Generation Assistant API (P5-006)
"""
import json
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import CreatorProfile

User = get_user_model()
from ai_services.models import (
    ContentGenerationRequest, GeneratedContent, ContentTemplate,
    ContentCategory, UserUsageTracking
)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    },
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {}
    }
)
class ContentGenerationAPITestCase(APITestCase):
    """Test AI Content Generation Assistant API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testcreator',
            email='test@example.com',
            password='testpass123'
        )
        self.creator_profile = CreatorProfile.objects.create(
            user=self.user,
            display_name='Test Creator',
            category='musician',
            experience_level='intermediate',
            bio='Test bio for creator'
        )
        self.client.force_authenticate(user=self.user)
    
    @patch('ai_services.content_generation_service.content_generation_service._get_client')
    def test_create_content_request(self, mock_get_client):
        """Test creating a content generation request"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated social media post content"
        mock_response.usage.total_tokens = 150
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        url = reverse('ai_services:content-requests-list')
        data = {
            'content_type': 'social_media_post',
            'platform': 'instagram',
            'prompt': 'Create a post about music production tips',
            'topic': 'Music Production',
            'target_audience': 'Aspiring musicians',
            'tone': 'Friendly and encouraging',
            'word_count': 100,
            'temperature': 0.8,
            'max_tokens': 500
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('request', response.data)
        self.assertIn('generated_content', response.data)
        
        # Verify request was created
        request_obj = ContentGenerationRequest.objects.get(
            id=response.data['request']['id']
        )
        self.assertEqual(request_obj.user, self.creator_profile)
        self.assertEqual(request_obj.content_type, 'social_media_post')
        self.assertEqual(request_obj.status, 'completed')
        
        # Verify generated content was created
        generated_content = GeneratedContent.objects.get(
            id=response.data['generated_content']['id']
        )
        self.assertEqual(generated_content.request, request_obj)
        self.assertIn('Generated social media post content', generated_content.content)
    
    def test_create_content_request_validation(self):
        """Test content request validation"""
        url = reverse('ai_services:content-requests-list')
        
        # Test missing required fields
        data = {
            'content_type': 'social_media_post',
            # Missing prompt and topic
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test invalid temperature
        data = {
            'content_type': 'social_media_post',
            'prompt': 'Test prompt',
            'topic': 'Test topic',
            'temperature': 3.0  # Invalid, should be 0.0-2.0
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('temperature', response.data)
    
    def test_list_content_requests(self):
        """Test listing content requests with filters"""
        # Create test requests
        request1 = ContentGenerationRequest.objects.create(
            user=self.creator_profile,
            content_type='social_media_post',
            platform='instagram',
            prompt='Test prompt 1',
            topic='Topic 1',
            status='completed'
        )
        request2 = ContentGenerationRequest.objects.create(
            user=self.creator_profile,
            content_type='blog_post',
            platform='general',
            prompt='Test prompt 2',
            topic='Topic 2',
            status='pending'
        )
        
        url = reverse('ai_services:content-requests-list')
        
        # Test list all
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Test filter by status
        response = self.client.get(url, {'status': 'completed'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], str(request1.id))
        
        # Test filter by content type
        response = self.client.get(url, {'content_type': 'blog_post'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], str(request2.id))
    
    @patch('ai_services.content_generation_service.content_generation_service._get_client')
    def test_regenerate_content(self, mock_get_client):
        """Test regenerating content for a request"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Regenerated content"
        mock_response.usage.total_tokens = 120
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # Create a request
        request_obj = ContentGenerationRequest.objects.create(
            user=self.creator_profile,
            content_type='social_media_post',
            platform='instagram',
            prompt='Test prompt',
            topic='Test topic',
            status='completed'
        )
        
        url = reverse('ai_services:content-requests-regenerate', kwargs={'pk': request_obj.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('content', response.data)
        self.assertIn('Regenerated content', response.data['content'])
    
    def test_create_template_from_request(self):
        """Test creating a template from a request"""
        request_obj = ContentGenerationRequest.objects.create(
            user=self.creator_profile,
            content_type='social_media_post',
            platform='instagram',
            prompt='Create engaging post about {topic}',
            topic='Music tips',
            status='completed'
        )
        
        url = reverse('ai_services:content-requests-create-template', kwargs={'pk': request_obj.id})
        data = {
            'name': 'Music Tips Template',
            'description': 'Template for creating music tip posts'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify template was created
        template = ContentTemplate.objects.get(id=response.data['id'])
        self.assertEqual(template.creator, self.creator_profile)
        self.assertEqual(template.name, 'Music Tips Template')
        self.assertEqual(template.content_type, 'social_media_post')
    
    def test_rate_generated_content(self):
        """Test rating generated content"""
        request_obj = ContentGenerationRequest.objects.create(
            user=self.creator_profile,
            content_type='social_media_post',
            platform='instagram',
            prompt='Test prompt',
            topic='Test topic'
        )
        
        content = GeneratedContent.objects.create(
            request=request_obj,
            content='Test generated content',
            title='Test Title'
        )
        
        url = reverse('ai_services:generated-content-rate', kwargs={'pk': content.id})
        data = {
            'rating': 4,
            'feedback': 'Great content, very helpful!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify rating was saved
        content.refresh_from_db()
        self.assertEqual(content.user_rating, 4)
        self.assertEqual(content.user_feedback, 'Great content, very helpful!')
    
    def test_toggle_favorite_content(self):
        """Test toggling favorite status of content"""
        request_obj = ContentGenerationRequest.objects.create(
            user=self.creator_profile,
            content_type='social_media_post',
            platform='instagram',
            prompt='Test prompt',
            topic='Test topic'
        )
        
        content = GeneratedContent.objects.create(
            request=request_obj,
            content='Test generated content',
            is_favorite=False
        )
        
        url = reverse('ai_services:generated-content-toggle-favorite', kwargs={'pk': content.id})
        
        # Toggle to favorite
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_favorite'])
        
        content.refresh_from_db()
        self.assertTrue(content.is_favorite)
        
        # Toggle back to not favorite
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_favorite'])
    
    def test_content_templates_crud(self):
        """Test content template CRUD operations"""
        # Create template
        url = reverse('ai_services:templates-list')
        data = {
            'name': 'Social Media Template',
            'description': 'Template for social media posts',
            'template_type': 'prompt',
            'content_type': 'social_media_post',
            'prompt_template': 'Create a {tone} post about {topic} for {platform}',
            'default_parameters': {
                'tone': 'engaging',
                'platform': 'instagram'
            },
            'is_public': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        template_id = response.data['id']
        
        # List templates
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Get specific template
        detail_url = reverse('ai_services:templates-detail', kwargs={'pk': template_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Social Media Template')
        
        # Update template
        update_data = {'name': 'Updated Template Name'}
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Template Name')
    
    @patch('ai_services.content_generation_service.content_generation_service._get_client')
    def test_use_template(self, mock_get_client):
        """Test using a template to generate content"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Template-generated content"
        mock_response.usage.total_tokens = 100
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # Create template
        template = ContentTemplate.objects.create(
            creator=self.creator_profile,
            name='Test Template',
            template_type='prompt',
            content_type='social_media_post',
            prompt_template='Create a post about {topic}',
            default_parameters={'platform': 'instagram'}
        )
        
        url = reverse('ai_services:templates-use-template', kwargs={'pk': template.id})
        data = {
            'parameters': {
                'topic': 'Music production tips'
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('request', response.data)
        self.assertIn('generated_content', response.data)
        
        # Verify template usage count increased
        template.refresh_from_db()
        self.assertEqual(template.usage_count, 1)
    
    def test_content_generation_stats(self):
        """Test content generation statistics endpoint"""
        # Create test data
        request1 = ContentGenerationRequest.objects.create(
            user=self.creator_profile,
            content_type='social_media_post',
            platform='instagram',
            prompt='Test 1',
            topic='Topic 1',
            status='completed',
            tokens_used=100,
            cost_estimate=Decimal('0.01')
        )
        
        request2 = ContentGenerationRequest.objects.create(
            user=self.creator_profile,
            content_type='blog_post',
            platform='general',
            prompt='Test 2',
            topic='Topic 2',
            status='failed'
        )
        
        GeneratedContent.objects.create(
            request=request1,
            content='Test content',
            quality_score=0.8
        )
        
        url = reverse('ai_services:content_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_requests'], 2)
        self.assertEqual(response.data['completed_requests'], 1)
        self.assertEqual(response.data['failed_requests'], 1)
        self.assertEqual(response.data['total_tokens_used'], 100)
        self.assertEqual(float(response.data['total_cost']), 0.01)
        self.assertEqual(response.data['average_quality_score'], 0.8)
    
    def test_usage_tracking(self):
        """Test usage tracking endpoint"""
        # Create usage tracking data
        UserUsageTracking.objects.create(
            user=self.creator_profile,
            usage_type='content_generation',
            tokens_consumed=150,
            cost_incurred=Decimal('0.015'),
            daily_count=5,
            monthly_count=25
        )
        
        url = reverse('ai_services:usage_tracking')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['tokens_consumed'], 150)
        self.assertEqual(response.data[0]['daily_count'], 5)
    
    @patch('ai_services.content_generation_service.content_generation_service._get_client')
    def test_batch_generate(self, mock_get_client):
        """Test batch content generation"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Batch generated content"
        mock_response.usage.total_tokens = 80
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        url = reverse('ai_services:batch_generate')
        data = {
            'requests': [
                {
                    'content_type': 'social_media_post',
                    'platform': 'instagram',
                    'prompt': 'Post about music',
                    'topic': 'Music'
                },
                {
                    'content_type': 'blog_post',
                    'platform': 'general',
                    'prompt': 'Article about creativity',
                    'topic': 'Creativity'
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['results']), 2)
        
        # Verify all requests succeeded
        for result in response.data['results']:
            self.assertTrue(result['success'])
            self.assertIn('request', result)
            self.assertIn('generated_content', result)
    
    def test_rate_limiting(self):
        """Test rate limiting for content generation"""
        # Create usage tracking to simulate hitting daily limit
        UserUsageTracking.objects.create(
            user=self.creator_profile,
            usage_type='content_generation',
            daily_count=50,  # At daily limit
            monthly_count=200
        )
        
        url = reverse('ai_services:content-requests-list')
        data = {
            'content_type': 'social_media_post',
            'prompt': 'Test prompt',
            'topic': 'Test topic'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('Daily request limit exceeded', response.data['error'])
    
    def test_permission_checks(self):
        """Test permission checks for content operations"""
        # Create another user and content
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        other_profile = CreatorProfile.objects.create(
            user=other_user,
            display_name='Other Creator',
            category='artist'
        )
        
        other_request = ContentGenerationRequest.objects.create(
            user=other_profile,
            content_type='social_media_post',
            prompt='Other user prompt',
            topic='Other topic'
        )
        
        other_content = GeneratedContent.objects.create(
            request=other_request,
            content='Other user content'
        )
        
        # Try to regenerate other user's content
        url = reverse('ai_services:content-requests-regenerate', kwargs={'pk': other_request.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try to rate other user's content
        url = reverse('ai_services:generated-content-rate', kwargs={'pk': other_content.id})
        response = self.client.post(url, {'rating': 5})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
)
class ContentGenerationServiceTestCase(TestCase):
    """Test AI Content Generation Service business logic"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testcreator',
            email='test@example.com',
            password='testpass123'
        )
        self.creator_profile = CreatorProfile.objects.create(
            user=self.user,
            display_name='Test Creator',
            category='musician',
            experience_level='intermediate'
        )
    
    def test_prompt_building(self):
        """Test prompt building for different content types"""
        from ai_services.content_generation_service import content_generation_service
        
        request_obj = ContentGenerationRequest(
            user=self.creator_profile,
            content_type='social_media_post',
            platform='instagram',
            prompt='Create a post about music production',
            topic='Music Production',
            target_audience='Musicians',
            tone='Inspiring',
            word_count=100
        )
        
        system_prompt, user_prompt = content_generation_service._build_prompts(request_obj)
        
        self.assertIn('social media expert', system_prompt.lower())
        self.assertIn('Music Production', user_prompt)
        self.assertIn('Musicians', user_prompt)
        self.assertIn('Inspiring', user_prompt)
        self.assertIn('100 words', user_prompt)
        self.assertIn('instagram', user_prompt.lower())
    
    def test_platform_guidelines(self):
        """Test platform-specific guidelines"""
        from ai_services.content_generation_service import content_generation_service
        
        instagram_guidelines = content_generation_service._get_platform_guidelines('instagram')
        self.assertIn('hashtags', instagram_guidelines.lower())
        self.assertIn('visual', instagram_guidelines.lower())
        
        twitter_guidelines = content_generation_service._get_platform_guidelines('twitter')
        self.assertIn('280 characters', twitter_guidelines)
        
        unknown_guidelines = content_generation_service._get_platform_guidelines('unknown')
        self.assertIn('best practices', unknown_guidelines.lower())
    
    def test_title_extraction(self):
        """Test title extraction from content"""
        from ai_services.content_generation_service import content_generation_service
        
        # Test with markdown header
        content_with_header = "# Amazing Music Tips\n\nHere are some great tips..."
        title = content_generation_service._extract_title(content_with_header, 'blog_post')
        self.assertEqual(title, 'Amazing Music Tips')
        
        # Test with uppercase line
        content_with_caps = "MUSIC PRODUCTION GUIDE\n\nThis guide covers..."
        title = content_generation_service._extract_title(content_with_caps, 'blog_post')
        self.assertEqual(title, 'MUSIC PRODUCTION GUIDE')
        
        # Test fallback to generic title
        content_no_title = "This is just regular content without a clear title structure."
        title = content_generation_service._extract_title(content_no_title, 'blog_post')
        self.assertEqual(title, 'Blog Post')
    
    def test_cost_calculation(self):
        """Test token cost calculation"""
        from ai_services.content_generation_service import content_generation_service
        
        cost_100_tokens = content_generation_service._calculate_cost(100)
        self.assertEqual(cost_100_tokens, Decimal('0.001'))
        
        cost_1000_tokens = content_generation_service._calculate_cost(1000)
        self.assertEqual(cost_1000_tokens, Decimal('0.01'))
    
    def test_usage_tracking(self):
        """Test usage tracking functionality"""
        from ai_services.content_generation_service import content_generation_service
        
        # Track initial usage
        content_generation_service._track_usage(self.creator_profile, 'content_generation')
        
        usage = UserUsageTracking.objects.get(
            user=self.creator_profile,
            usage_type='content_generation'
        )
        self.assertEqual(usage.daily_count, 1)
        self.assertEqual(usage.monthly_count, 1)
        
        # Track additional usage
        content_generation_service._track_usage(self.creator_profile, 'content_generation')
        
        usage.refresh_from_db()
        self.assertEqual(usage.daily_count, 2)
        self.assertEqual(usage.monthly_count, 2)
    
    def test_template_creation_from_request(self):
        """Test creating templates from successful requests"""
        from ai_services.content_generation_service import content_generation_service
        
        request_obj = ContentGenerationRequest.objects.create(
            user=self.creator_profile,
            content_type='social_media_post',
            platform='instagram',
            prompt='Create engaging post about {topic}',
            topic='Music tips',
            target_audience='Musicians',
            tone='Friendly'
        )
        
        template = content_generation_service.create_template_from_request(
            request_obj,
            'Music Tips Template',
            'Template for music-related posts'
        )
        
        self.assertEqual(template.creator, self.creator_profile)
        self.assertEqual(template.name, 'Music Tips Template')
        self.assertEqual(template.content_type, 'social_media_post')
        self.assertEqual(template.prompt_template, 'Create engaging post about {topic}')
        self.assertIn('instagram', template.default_parameters['platform'])
