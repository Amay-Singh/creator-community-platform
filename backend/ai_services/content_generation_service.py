"""
AI Content Generation Service
Implements REQ-13, REQ-15: AI content generation and portfolio generator
Enhanced for P5-006: AI Content Generation Assistant
"""
try:
    import openai
except ImportError:
    openai = None
import json
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.db import models
from typing import Dict, List, Optional, Tuple
from .models import (
    AIContentGeneration, ContentGenerationRequest, GeneratedContent,
    ContentTemplate, UserUsageTracking
)
from accounts.models import CreatorProfile, PortfolioItem

class AIContentGenerationService:
    """
    AI-powered content generation service
    """
    
    def __init__(self):
        self.client = None
    
    def _get_client(self):
        """Lazy initialization of OpenAI client"""
        if self.client is None:
            try:
                if openai is None:
                    self.client = None
                else:
                    self.client = openai.OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', None))
            except Exception:
                self.client = None
        return self.client
    
    def generate_music_concept(self, profile: CreatorProfile, prompt: str, parameters: Dict = None) -> Dict:
        """Generate music concept and composition ideas"""
        
        client = self._get_client()
        if not client:
            return self._fallback_response("Music generation service unavailable")
        
        try:
            enhanced_prompt = f"""
            Create a detailed music concept for {profile.display_name}, a {profile.get_category_display()} creator.
            
            User Request: {prompt}
            
            Profile Context:
            - Experience Level: {profile.get_experience_level_display()}
            - Bio: {profile.bio[:200] if profile.bio else 'No bio provided'}
            
            Generate a comprehensive music concept including:
            1. Song/composition title
            2. Genre and style recommendations
            3. Mood and atmosphere description
            4. Suggested chord progressions or musical elements
            5. Lyrical themes or instrumental focus
            6. Production notes and arrangement ideas
            7. Target audience and use cases
            
            Make it creative, detailed, and tailored to their experience level.
            """
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional music producer and composer. Create detailed, actionable music concepts that inspire creativity."
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            generated_content = response.choices[0].message.content.strip()
            
            return self._save_generation(
                profile, 'music', prompt, generated_content, parameters or {}
            )
        
        except Exception as e:
            return self._fallback_response(f"Music generation failed: {str(e)}")
    
    def generate_artwork_concept(self, profile: CreatorProfile, prompt: str, parameters: Dict = None) -> Dict:
        """Generate visual artwork concepts and ideas"""
        
        client = self._get_client()
        if not client:
            return self._fallback_response("Artwork generation service unavailable")
        
        try:
            enhanced_prompt = f"""
            Create a detailed visual artwork concept for {profile.display_name}, a {profile.get_category_display()} creator.
            
            User Request: {prompt}
            
            Profile Context:
            - Experience Level: {profile.get_experience_level_display()}
            - Bio: {profile.bio[:200] if profile.bio else 'No bio provided'}
            
            Generate a comprehensive artwork concept including:
            1. Artwork title and concept
            2. Visual style and artistic medium recommendations
            3. Color palette and composition ideas
            4. Subject matter and themes
            5. Technical approach and materials
            6. Mood and emotional impact
            7. Inspiration sources and references
            8. Step-by-step creation process
            
            Tailor the complexity to their experience level and make it inspiring yet achievable.
            """
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional artist and art director. Create detailed, inspiring artwork concepts that guide creative execution."
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            generated_content = response.choices[0].message.content.strip()
            
            return self._save_generation(
                profile, 'artwork', prompt, generated_content, parameters or {}
            )
        
        except Exception as e:
            return self._fallback_response(f"Artwork generation failed: {str(e)}")
    
    def generate_story_concept(self, profile: CreatorProfile, prompt: str, parameters: Dict = None) -> Dict:
        """Generate story and narrative concepts"""
        
        client = self._get_client()
        if not client:
            return self._fallback_response("Story generation service unavailable")
        
        try:
            enhanced_prompt = f"""
            Create a compelling story concept for {profile.display_name}, a {profile.get_category_display()} creator.
            
            User Request: {prompt}
            
            Profile Context:
            - Experience Level: {profile.get_experience_level_display()}
            - Bio: {profile.bio[:200] if profile.bio else 'No bio provided'}
            
            Generate a detailed story concept including:
            1. Story title and logline
            2. Genre and target audience
            3. Main characters and their arcs
            4. Setting and world-building elements
            5. Plot structure and key story beats
            6. Themes and underlying messages
            7. Tone and narrative style
            8. Potential formats (short story, novel, script, etc.)
            
            Make it engaging, original, and suited to their creative level.
            """
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional storyteller and creative writing mentor. Create compelling story concepts that inspire great narratives."
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            generated_content = response.choices[0].message.content.strip()
            
            return self._save_generation(
                profile, 'story', prompt, generated_content, parameters or {}
            )
        
        except Exception as e:
            return self._fallback_response(f"Story generation failed: {str(e)}")
    
    def generate_portfolio_content(self, profile: CreatorProfile, content_type: str = 'bio') -> Dict:
        """Generate portfolio content like bios, descriptions, captions (REQ-15)"""
        
        client = self._get_client()
        if not client:
            return self._fallback_response("Portfolio generation service unavailable")
        
        try:
            if content_type == 'bio':
                prompt = self._create_bio_prompt(profile)
            elif content_type == 'project_descriptions':
                prompt = self._create_project_description_prompt(profile)
            elif content_type == 'social_captions':
                prompt = self._create_social_caption_prompt(profile)
            else:
                return self._fallback_response("Unsupported content type")
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional copywriter specializing in creative portfolios. Write compelling, authentic content that showcases artistic talent."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            generated_content = response.choices[0].message.content.strip()
            
            return self._save_generation(
                profile, content_type, f"Generate {content_type} for portfolio", generated_content, {}
            )
        
        except Exception as e:
            return self._fallback_response(f"Portfolio generation failed: {str(e)}")
    
    def _create_bio_prompt(self, profile: CreatorProfile) -> str:
        """Create bio generation prompt"""
        
        portfolio_items = profile.portfolio_items.all()[:5]
        portfolio_context = ""
        
        if portfolio_items:
            portfolio_context = "Portfolio items: " + ", ".join([
                f"{item.title} ({item.get_media_type_display()})" 
                for item in portfolio_items
            ])
        
        return f"""
        Create a compelling professional bio for {profile.display_name}, a {profile.get_category_display()} creator.
        
        Current Info:
        - Category: {profile.get_category_display()}
        - Experience Level: {profile.get_experience_level_display()}
        - Location: {profile.location or 'Not specified'}
        - Current Bio: {profile.bio if profile.bio else 'No existing bio'}
        - {portfolio_context}
        
        Create 3 versions:
        1. Short bio (50-75 words) - for social media profiles
        2. Medium bio (100-150 words) - for professional profiles  
        3. Long bio (200-250 words) - for detailed portfolios
        
        Make each version authentic, engaging, and highlight their creative strengths.
        """
    
    def _create_project_description_prompt(self, profile: CreatorProfile) -> str:
        """Create project description generation prompt"""
        
        return f"""
        Generate compelling project descriptions for {profile.display_name}'s portfolio.
        
        Creator Info:
        - Category: {profile.get_category_display()}
        - Experience Level: {profile.get_experience_level_display()}
        - Style: {profile.bio[:100] if profile.bio else 'Creative professional'}
        
        Create 5 different project description templates that they can customize:
        1. Personal project description
        2. Client work description
        3. Collaborative project description
        4. Experimental/learning project description
        5. Featured/showcase project description
        
        Each should be 50-100 words and include placeholders for specific details.
        Make them professional yet authentic to their creative voice.
        """
    
    def _create_social_caption_prompt(self, profile: CreatorProfile) -> str:
        """Create social media caption generation prompt"""
        
        return f"""
        Create engaging social media captions for {profile.display_name}'s creative content.
        
        Creator Info:
        - Category: {profile.get_category_display()}
        - Experience Level: {profile.get_experience_level_display()}
        - Tone: Professional but approachable
        
        Generate 10 different caption templates for:
        1. Work-in-progress posts
        2. Finished project reveals
        3. Behind-the-scenes content
        4. Creative process insights
        5. Inspiration and motivation posts
        6. Collaboration announcements
        7. Skill development updates
        8. Community engagement posts
        9. Achievement celebrations
        10. Creative challenges/prompts
        
        Each caption should be 20-50 words with relevant hashtag suggestions.
        """
    
    def _save_generation(self, profile: CreatorProfile, generation_type: str, prompt: str, content: str, parameters: Dict) -> Dict:
        """Save generation to database and return response"""
        
        quality_score = self._calculate_quality_score(content)
        
        generation = AIContentGeneration.objects.create(
            profile=profile,
            generation_type=generation_type,
            prompt=prompt,
            parameters=parameters,
            status='completed',
            generated_content=content,
            quality_score=quality_score,
            completed_at=timezone.now()
        )
        
        return {
            'success': True,
            'generation_id': str(generation.id),
            'generated_content': content,
            'quality_score': quality_score,
            'generation_type': generation_type
        }
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate quality score for generated content"""
        
        score = 0.5  # Base score
        
        # Length check
        if 100 <= len(content) <= 1000:
            score += 0.2
        
        # Structure check (has multiple sentences/paragraphs)
        if content.count('.') >= 2 or content.count('\n') >= 1:
            score += 0.2
        
        # Creativity indicators
        creative_words = ['unique', 'innovative', 'creative', 'original', 'inspiring', 'artistic']
        if any(word in content.lower() for word in creative_words):
            score += 0.1
        
        return min(1.0, score)
    
    def _fallback_response(self, error_message: str) -> Dict:
        """Return fallback response when AI is unavailable"""
        
        return {
            'success': False,
            'error': error_message,
            'generated_content': '',
            'quality_score': 0.0
        }
    
    def get_generation_history(self, profile: CreatorProfile, generation_type: Optional[str] = None) -> List[Dict]:
        """Get user's content generation history"""
        
        queryset = profile.ai_generations.all()
        
        if generation_type:
            queryset = queryset.filter(generation_type=generation_type)
        
        generations = queryset.order_by('-created_at')[:20]
        
        return [
            {
                'id': str(gen.id),
                'generation_type': gen.generation_type,
                'prompt': gen.prompt[:100] + '...' if len(gen.prompt) > 100 else gen.prompt,
                'quality_score': gen.quality_score,
                'status': gen.status,
                'created_at': gen.created_at,
                'preview': gen.generated_content[:150] + '...' if len(gen.generated_content) > 150 else gen.generated_content
            }
            for gen in generations
        ]
    
    def regenerate_content(self, generation_id: str, profile: CreatorProfile) -> Dict:
        """Regenerate content based on previous generation"""
        
        try:
            original_generation = AIContentGeneration.objects.get(
                id=generation_id,
                profile=profile
            )
            
            # Create new generation with same parameters
            if original_generation.generation_type == 'music':
                return self.generate_music_concept(
                    profile, 
                    original_generation.prompt, 
                    original_generation.parameters
                )
            elif original_generation.generation_type == 'artwork':
                return self.generate_artwork_concept(
                    profile, 
                    original_generation.prompt, 
                    original_generation.parameters
                )
            elif original_generation.generation_type == 'story':
                return self.generate_story_concept(
                    profile, 
                    original_generation.prompt, 
                    original_generation.parameters
                )
            else:
                return self.generate_portfolio_content(
                    profile, 
                    original_generation.generation_type
                )
        
        except AIContentGeneration.DoesNotExist:
            return self._fallback_response("Original generation not found")

    # P5-006 Enhanced Content Generation Methods
    
    def create_content_request(self, user: CreatorProfile, request_data: Dict) -> ContentGenerationRequest:
        """Create a new content generation request"""
        with transaction.atomic():
            request = ContentGenerationRequest.objects.create(
                user=user,
                content_type=request_data['content_type'],
                platform=request_data.get('platform', 'general'),
                prompt=request_data['prompt'],
                topic=request_data['topic'],
                target_audience=request_data.get('target_audience', ''),
                tone=request_data.get('tone', ''),
                word_count=request_data.get('word_count'),
                duration_minutes=request_data.get('duration_minutes'),
                temperature=request_data.get('temperature', 0.7),
                max_tokens=request_data.get('max_tokens', 1000),
                custom_parameters=request_data.get('custom_parameters', {})
            )
            
            # Track usage
            self._track_usage(user, 'content_generation')
            
            return request
    
    def process_content_request(self, request: ContentGenerationRequest) -> GeneratedContent:
        """Process a content generation request using OpenAI"""
        request.status = 'processing'
        request.save()
        
        try:
            # Generate content based on type
            content_data = self._generate_content_by_type(request)
            
            # Create generated content record
            generated_content = GeneratedContent.objects.create(
                request=request,
                content=content_data['content'],
                title=content_data.get('title', ''),
                metadata=content_data.get('metadata', {}),
                quality_score=content_data.get('quality_score', 0.0)
            )
            
            # Update request status
            request.status = 'completed'
            request.tokens_used = content_data.get('tokens_used', 0)
            request.cost_estimate = content_data.get('cost_estimate', Decimal('0.00'))
            request.completed_at = timezone.now()
            request.save()
            
            # Track token usage
            self._track_token_usage(request.user, request.tokens_used, request.cost_estimate)
            
            return generated_content
            
        except Exception as e:
            request.status = 'failed'
            request.save()
            raise e
    
    def _generate_content_by_type(self, request: ContentGenerationRequest) -> Dict:
        """Generate content based on content type"""
        client = self._get_client()
        if not client:
            raise Exception("OpenAI client not available")
        
        # Build prompt based on content type
        system_prompt, user_prompt = self._build_prompts(request)
        
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            content = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
            cost_estimate = self._calculate_cost(tokens_used)
            
            # Extract title if possible
            title = self._extract_title(content, request.content_type)
            
            return {
                'content': content,
                'title': title,
                'quality_score': self._calculate_quality_score(content),
                'tokens_used': tokens_used,
                'cost_estimate': cost_estimate,
                'metadata': {
                    'model': 'gpt-4-turbo-preview',
                    'temperature': request.temperature,
                    'max_tokens': request.max_tokens
                }
            }
            
        except Exception as e:
            raise Exception(f"Content generation failed: {str(e)}")
    
    def _build_prompts(self, request: ContentGenerationRequest) -> Tuple[str, str]:
        """Build system and user prompts based on content type"""
        
        # Content type specific system prompts
        system_prompts = {
            'social_media_post': "You are a social media expert who creates engaging, viral-worthy posts that drive engagement and build community.",
            'video_script': "You are a professional video scriptwriter who creates compelling, well-structured scripts for various video formats.",
            'blog_post': "You are a skilled blog writer who creates informative, engaging, and SEO-friendly blog content.",
            'marketing_copy': "You are a marketing copywriter who creates persuasive, conversion-focused copy that drives action.",
            'creative_writing': "You are a creative writer who crafts imaginative, compelling narratives and stories.",
            'product_description': "You are a product copywriter who creates compelling, benefit-focused product descriptions that sell.",
            'email_campaign': "You are an email marketing specialist who creates engaging, personalized email content that converts.",
            'press_release': "You are a PR professional who writes newsworthy, professional press releases that get media attention."
        }
        
        system_prompt = system_prompts.get(request.content_type, "You are a professional content writer.")
        
        # Build comprehensive user prompt
        user_prompt = f"""
        Create {request.content_type} content with the following specifications:

        Topic: {request.topic}
        Platform: {request.platform}
        Target Audience: {request.target_audience or 'General audience'}
        Tone: {request.tone or 'Professional but engaging'}
        
        User Request: {request.prompt}
        """
        
        if request.word_count:
            user_prompt += f"\nTarget Word Count: {request.word_count} words"
        
        if request.duration_minutes:
            user_prompt += f"\nTarget Duration: {request.duration_minutes} minutes"
        
        # Add platform-specific guidelines
        if request.platform != 'general':
            platform_guidelines = self._get_platform_guidelines(request.platform)
            user_prompt += f"\n\nPlatform Guidelines: {platform_guidelines}"
        
        # Add custom parameters
        if request.custom_parameters:
            user_prompt += f"\n\nAdditional Requirements: {json.dumps(request.custom_parameters, indent=2)}"
        
        user_prompt += "\n\nPlease create high-quality, original content that meets these specifications."
        
        return system_prompt, user_prompt
    
    def _get_platform_guidelines(self, platform: str) -> str:
        """Get platform-specific content guidelines"""
        guidelines = {
            'instagram': "Keep it visual-first, use relevant hashtags, engage with stories, optimal length 125-150 characters for captions",
            'tiktok': "Focus on trends, use popular sounds, keep it short and engaging, vertical video format, hook viewers in first 3 seconds",
            'youtube': "Strong hook in first 15 seconds, clear value proposition, encourage engagement, optimize for search",
            'twitter': "Keep under 280 characters, use relevant hashtags, encourage retweets, be conversational",
            'linkedin': "Professional tone, industry insights, thought leadership, longer form content acceptable",
            'facebook': "Community-focused, encourage comments and shares, mix of text and visual content"
        }
        return guidelines.get(platform, "Follow platform best practices")
    
    def _extract_title(self, content: str, content_type: str) -> str:
        """Extract or generate title from content"""
        lines = content.split('\n')
        
        # Look for title patterns in first few lines
        for line in lines[:3]:
            line = line.strip()
            # Check for markdown headers
            if line.startswith('#'):
                return line.replace('#', '').strip()
            # Check for short uppercase lines (likely titles)
            if line.isupper() and 10 <= len(line) <= 100:
                return line
            # Check for short lines that could be titles
            if 10 <= len(line) <= 80 and not line.endswith('.'):
                return line
        
        # Generate generic title based on content type
        type_titles = {
            'social_media_post': 'Social Media Post',
            'video_script': 'Video Script',
            'blog_post': 'Blog Post',
            'marketing_copy': 'Marketing Copy',
            'creative_writing': 'Creative Writing',
            'product_description': 'Product Description',
            'email_campaign': 'Email Campaign',
            'press_release': 'Press Release'
        }
        
        return type_titles.get(content_type, 'Generated Content')
    
    def _calculate_cost(self, tokens: int) -> Decimal:
        """Calculate estimated cost based on tokens"""
        # GPT-4 Turbo pricing (approximate)
        cost_per_1k_tokens = Decimal('0.01')  # $0.01 per 1K tokens
        return (Decimal(tokens) / 1000) * cost_per_1k_tokens
    
    def _track_usage(self, user: CreatorProfile, usage_type: str):
        """Track user usage for rate limiting"""
        today = timezone.now().date()
        
        usage, created = UserUsageTracking.objects.get_or_create(
            user=user,
            usage_type=usage_type,
            date=today,
            defaults={'daily_count': 0, 'monthly_count': 0}
        )
        
        usage.daily_count += 1
        usage.monthly_count += 1
        usage.save()
    
    def _track_token_usage(self, user: CreatorProfile, tokens: int, cost: Decimal):
        """Track token usage and costs"""
        today = timezone.now().date()
        
        usage, created = UserUsageTracking.objects.get_or_create(
            user=user,
            usage_type='content_generation',
            date=today,
            defaults={'tokens_consumed': 0, 'cost_incurred': Decimal('0.00')}
        )
        
        usage.tokens_consumed += tokens
        usage.cost_incurred += cost
        usage.save()
    
    def get_user_usage_stats(self, user: CreatorProfile) -> Dict:
        """Get user's usage statistics"""
        today = timezone.now().date()
        
        # Get today's usage
        today_usage = UserUsageTracking.objects.filter(
            user=user,
            date=today
        ).first()
        
        # Get monthly totals
        month_start = today.replace(day=1)
        monthly_usage = UserUsageTracking.objects.filter(
            user=user,
            date__gte=month_start
        ).aggregate(
            total_requests=models.Sum('daily_count'),
            total_tokens=models.Sum('tokens_consumed'),
            total_cost=models.Sum('cost_incurred')
        )
        
        return {
            'daily_requests': today_usage.daily_count if today_usage else 0,
            'daily_tokens': today_usage.tokens_consumed if today_usage else 0,
            'daily_cost': today_usage.cost_incurred if today_usage else Decimal('0.00'),
            'monthly_requests': monthly_usage['total_requests'] or 0,
            'monthly_tokens': monthly_usage['total_tokens'] or 0,
            'monthly_cost': monthly_usage['total_cost'] or Decimal('0.00')
        }
    
    def create_template_from_request(self, request: ContentGenerationRequest, name: str, description: str = '') -> ContentTemplate:
        """Create a reusable template from a successful request"""
        template = ContentTemplate.objects.create(
            creator=request.user,
            name=name,
            description=description,
            template_type='prompt',
            content_type=request.content_type,
            prompt_template=request.prompt,
            default_parameters={
                'platform': request.platform,
                'target_audience': request.target_audience,
                'tone': request.tone,
                'word_count': request.word_count,
                'duration_minutes': request.duration_minutes,
                'temperature': request.temperature,
                'max_tokens': request.max_tokens
            }
        )
        return template
    
    def use_template(self, template: ContentTemplate, user: CreatorProfile, custom_params: Dict = None) -> ContentGenerationRequest:
        """Create a new request using a template"""
        params = template.default_parameters.copy()
        if custom_params:
            params.update(custom_params)
        
        request_data = {
            'content_type': template.content_type,
            'prompt': template.prompt_template,
            'topic': params.get('topic', ''),
            **params
        }
        
        # Increment template usage
        template.usage_count += 1
        template.save()
        
        return self.create_content_request(user, request_data)


# Service instance
content_generation_service = AIContentGenerationService()
