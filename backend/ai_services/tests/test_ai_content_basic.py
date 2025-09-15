"""
Basic tests for AI Content Generation Assistant (P5-006)
"""
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from accounts.models import CreatorProfile
from ai_services.models import (
    ContentGenerationRequest, GeneratedContent, ContentTemplate,
    UserUsageTracking
)
from ai_services.content_generation_service import content_generation_service

User = get_user_model()


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
)
class AIContentGenerationBasicTestCase(TestCase):
    """Basic tests for AI Content Generation functionality"""
    
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
    
    def test_content_generation_request_model(self):
        """Test ContentGenerationRequest model creation"""
        request = ContentGenerationRequest.objects.create(
            user=self.creator_profile,
            content_type='social_media_post',
            platform='instagram',
            prompt='Create a post about music production',
            topic='Music Production',
            target_audience='Musicians',
            tone='Inspiring',
            word_count=100
        )
        
        self.assertEqual(request.user, self.creator_profile)
        self.assertEqual(request.content_type, 'social_media_post')
        self.assertEqual(request.platform, 'instagram')
        self.assertEqual(request.status, 'pending')
        self.assertEqual(str(request), f"{self.creator_profile.display_name} - social_media_post - pending")
    
    def test_generated_content_model(self):
        """Test GeneratedContent model creation"""
        request = ContentGenerationRequest.objects.create(
            user=self.creator_profile,
            content_type='blog_post',
            prompt='Write about creativity',
            topic='Creativity'
        )
        
        content = GeneratedContent.objects.create(
            request=request,
            content='This is a great blog post about creativity...',
            title='The Art of Creativity',
            quality_score=0.85
        )
        
        self.assertEqual(content.request, request)
        self.assertEqual(content.title, 'The Art of Creativity')
        self.assertEqual(content.quality_score, 0.85)
        self.assertEqual(content.version, 1)
        self.assertFalse(content.is_favorite)
        self.assertFalse(content.is_published)
    
    def test_content_template_model(self):
        """Test ContentTemplate model creation"""
        template = ContentTemplate.objects.create(
            creator=self.creator_profile,
            name='Music Post Template',
            description='Template for music-related posts',
            template_type='prompt',
            content_type='social_media_post',
            prompt_template='Create a {tone} post about {topic} for musicians',
            default_parameters={'tone': 'inspiring', 'platform': 'instagram'},
            is_public=True
        )
        
        self.assertEqual(template.creator, self.creator_profile)
        self.assertEqual(template.name, 'Music Post Template')
        self.assertEqual(template.usage_count, 0)
        self.assertTrue(template.is_public)
        self.assertFalse(template.is_featured)
    
    def test_user_usage_tracking_model(self):
        """Test UserUsageTracking model creation"""
        usage = UserUsageTracking.objects.create(
            user=self.creator_profile,
            usage_type='content_generation',
            tokens_consumed=150,
            cost_incurred=0.015,
            daily_count=5,
            monthly_count=25
        )
        
        self.assertEqual(usage.user, self.creator_profile)
        self.assertEqual(usage.usage_type, 'content_generation')
        self.assertEqual(usage.tokens_consumed, 150)
        self.assertEqual(usage.daily_count, 5)
    
    def test_content_generation_service_prompt_building(self):
        """Test prompt building functionality"""
        request = ContentGenerationRequest(
            user=self.creator_profile,
            content_type='social_media_post',
            platform='instagram',
            prompt='Create a post about music production',
            topic='Music Production',
            target_audience='Musicians',
            tone='Inspiring',
            word_count=100
        )
        
        system_prompt, user_prompt = content_generation_service._build_prompts(request)
        
        self.assertIn('social media expert', system_prompt.lower())
        self.assertIn('Music Production', user_prompt)
        self.assertIn('Musicians', user_prompt)
        self.assertIn('Inspiring', user_prompt)
        self.assertIn('100 words', user_prompt)
    
    def test_platform_guidelines(self):
        """Test platform-specific guidelines"""
        instagram_guidelines = content_generation_service._get_platform_guidelines('instagram')
        self.assertIn('hashtags', instagram_guidelines.lower())
        self.assertIn('visual', instagram_guidelines.lower())
        
        twitter_guidelines = content_generation_service._get_platform_guidelines('twitter')
        self.assertIn('280 characters', twitter_guidelines)
        
        unknown_guidelines = content_generation_service._get_platform_guidelines('unknown')
        self.assertIn('best practices', unknown_guidelines.lower())
    
    def test_title_extraction(self):
        """Test title extraction from content"""
        # Test with markdown header
        content_with_header = "# Amazing Music Tips\n\nHere are some great tips..."
        title = content_generation_service._extract_title(content_with_header, 'blog_post')
        self.assertEqual(title, 'Amazing Music Tips')
        
        # Test with uppercase line
        content_with_caps = "MUSIC PRODUCTION GUIDE\n\nThis guide covers..."
        title = content_generation_service._extract_title(content_with_caps, 'blog_post')
        self.assertEqual(title, 'MUSIC PRODUCTION GUIDE')
        
        # Test fallback to generic title
        content_no_title = "This is just regular content without a clear title structure that goes on and on."
        title = content_generation_service._extract_title(content_no_title, 'blog_post')
        self.assertEqual(title, 'Blog Post')
    
    def test_cost_calculation(self):
        """Test token cost calculation"""
        from decimal import Decimal
        
        cost_100_tokens = content_generation_service._calculate_cost(100)
        self.assertEqual(cost_100_tokens, Decimal('0.001'))
        
        cost_1000_tokens = content_generation_service._calculate_cost(1000)
        self.assertEqual(cost_1000_tokens, Decimal('0.01'))
    
    def test_usage_tracking_service(self):
        """Test usage tracking functionality"""
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
        request = ContentGenerationRequest.objects.create(
            user=self.creator_profile,
            content_type='social_media_post',
            platform='instagram',
            prompt='Create engaging post about {topic}',
            topic='Music tips',
            target_audience='Musicians',
            tone='Friendly'
        )
        
        template = content_generation_service.create_template_from_request(
            request,
            'Music Tips Template',
            'Template for music-related posts'
        )
        
        self.assertEqual(template.creator, self.creator_profile)
        self.assertEqual(template.name, 'Music Tips Template')
        self.assertEqual(template.content_type, 'social_media_post')
        self.assertEqual(template.prompt_template, 'Create engaging post about {topic}')
        self.assertIn('instagram', template.default_parameters['platform'])
    
    def test_model_string_representations(self):
        """Test string representations of models"""
        request = ContentGenerationRequest.objects.create(
            user=self.creator_profile,
            content_type='blog_post',
            prompt='Test prompt',
            topic='Test topic'
        )
        
        content = GeneratedContent.objects.create(
            request=request,
            content='Test content',
            title='Test Title'
        )
        
        template = ContentTemplate.objects.create(
            creator=self.creator_profile,
            name='Test Template',
            content_type='social_media_post',
            prompt_template='Test prompt'
        )
        
        usage = UserUsageTracking.objects.create(
            user=self.creator_profile,
            usage_type='content_generation'
        )
        
        # Test string representations
        self.assertIn('Test Creator', str(request))
        self.assertIn('blog_post', str(request))
        
        self.assertIn('blog_post', str(content))
        self.assertIn('Test Title', str(content))
        
        self.assertIn('Test Template', str(template))
        self.assertIn('social_media_post', str(template))
        
        self.assertIn('Test Creator', str(usage))
        self.assertIn('content_generation', str(usage))
    
    def test_content_choices_and_validation(self):
        """Test content type choices and validation"""
        # Test valid content types
        valid_types = [
            'social_media_post', 'video_script', 'blog_post', 'marketing_copy',
            'creative_writing', 'product_description', 'email_campaign', 'press_release'
        ]
        
        for content_type in valid_types:
            request = ContentGenerationRequest.objects.create(
                user=self.creator_profile,
                content_type=content_type,
                prompt='Test prompt',
                topic='Test topic'
            )
            self.assertEqual(request.content_type, content_type)
        
        # Test platform choices
        valid_platforms = [
            'instagram', 'tiktok', 'youtube', 'twitter', 'linkedin', 'facebook', 'general'
        ]
        
        for platform in valid_platforms:
            request = ContentGenerationRequest.objects.create(
                user=self.creator_profile,
                content_type='social_media_post',
                platform=platform,
                prompt='Test prompt',
                topic='Test topic'
            )
            self.assertEqual(request.platform, platform)
