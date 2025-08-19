"""
AI Content Generation Service
Implements REQ-13, REQ-15: AI content generation and portfolio generator
"""
import openai
from django.conf import settings
from django.utils import timezone
from typing import Dict, List, Optional
from .models import AIContentGeneration
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

# Service instance
content_generation_service = AIContentGenerationService()
