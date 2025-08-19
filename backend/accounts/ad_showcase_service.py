"""
Ad Showcase Service
Implements REQ-17: Relevant ad showcase for creators
"""
import openai
from django.conf import settings
from django.utils import timezone
from typing import Dict, List, Optional
from accounts.models import CreatorProfile, PortfolioItem

class AdShowcaseService:
    """
    Service for displaying relevant ads to creators based on their profiles and interests
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
    
    def get_relevant_ads(self, profile: CreatorProfile, context: str = 'general') -> Dict:
        """Get relevant ads for creator based on their profile and context"""
        
        try:
            # Analyze creator profile for ad targeting
            targeting_data = self._analyze_creator_profile(profile)
            
            # Generate contextual ads using AI
            ads = self._generate_contextual_ads(profile, targeting_data, context)
            
            return {
                'success': True,
                'ads': ads,
                'targeting_data': targeting_data,
                'context': context
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get relevant ads: {str(e)}',
                'ads': self._get_fallback_ads(profile)
            }
    
    def _analyze_creator_profile(self, profile: CreatorProfile) -> Dict:
        """Analyze creator profile for ad targeting"""
        
        targeting_data = {
            'category': profile.category,
            'experience_level': profile.experience_level,
            'interests': [],
            'tools_used': [],
            'content_themes': [],
            'collaboration_history': [],
            'activity_level': 'medium'
        }
        
        # Analyze portfolio items for interests and tools
        portfolio_items = profile.portfolio_items.all()[:10]
        
        for item in portfolio_items:
            # Extract themes from descriptions and tags
            if item.description:
                targeting_data['content_themes'].extend(
                    self._extract_themes_from_text(item.description)
                )
            
            if item.tags:
                targeting_data['interests'].extend(item.tags)
        
        # Analyze collaboration history
        collaborations = profile.sent_invites.filter(status='accepted').count() + \
                        profile.received_invites.filter(status='accepted').count()
        
        if collaborations > 5:
            targeting_data['activity_level'] = 'high'
        elif collaborations < 2:
            targeting_data['activity_level'] = 'low'
        
        # Clean up and deduplicate
        targeting_data['interests'] = list(set(targeting_data['interests']))[:10]
        targeting_data['content_themes'] = list(set(targeting_data['content_themes']))[:10]
        
        return targeting_data
    
    def _generate_contextual_ads(self, profile: CreatorProfile, targeting_data: Dict, context: str) -> List[Dict]:
        """Generate contextual ads using AI"""
        
        client = self._get_client()
        if not client:
            return self._get_fallback_ads(profile)
        
        try:
            prompt = f"""
            Generate 3-5 relevant advertisements for a {targeting_data['category']} creator.
            
            Creator Profile:
            - Experience Level: {targeting_data['experience_level']}
            - Interests: {', '.join(targeting_data['interests'][:5])}
            - Content Themes: {', '.join(targeting_data['content_themes'][:5])}
            - Activity Level: {targeting_data['activity_level']}
            - Context: {context}
            
            Generate ads for:
            1. Creative tools and software
            2. Learning resources and courses
            3. Hardware and equipment
            4. Services for creators
            5. Collaboration opportunities
            
            For each ad, provide:
            - title: Compelling ad title
            - description: Brief description (50-80 words)
            - category: Ad category
            - target_url: Mock URL
            - image_url: Mock image URL
            - relevance_score: 0.0-1.0 relevance score
            - call_to_action: Action button text
            
            Make ads highly relevant to their creative category and interests.
            """
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in creator economy and digital marketing. Generate relevant, helpful ads that would genuinely benefit creators."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            # Parse AI response into structured ads
            ads_content = response.choices[0].message.content.strip()
            ads = self._parse_ads_from_ai_response(ads_content, targeting_data)
            
            return ads
        
        except Exception as e:
            return self._get_fallback_ads(profile)
    
    def _parse_ads_from_ai_response(self, content: str, targeting_data: Dict) -> List[Dict]:
        """Parse AI response into structured ad format"""
        
        # This is a simplified parser - in production, use more robust parsing
        ads = []
        
        # Mock ads based on category
        if targeting_data['category'] == 'musician':
            ads = [
                {
                    'id': 'ad_1',
                    'title': 'Professional Audio Interface - 50% Off',
                    'description': 'Upgrade your home studio with the Focusrite Scarlett series. Crystal clear recording quality for musicians and producers.',
                    'category': 'equipment',
                    'target_url': 'https://example.com/audio-interface',
                    'image_url': 'https://example.com/images/audio-interface.jpg',
                    'relevance_score': 0.9,
                    'call_to_action': 'Shop Now'
                },
                {
                    'id': 'ad_2',
                    'title': 'Music Theory Masterclass',
                    'description': 'Learn advanced music theory from Grammy-winning composers. Perfect for intermediate to advanced musicians.',
                    'category': 'education',
                    'target_url': 'https://example.com/music-theory-course',
                    'image_url': 'https://example.com/images/music-course.jpg',
                    'relevance_score': 0.8,
                    'call_to_action': 'Enroll Today'
                }
            ]
        elif targeting_data['category'] == 'visual_artist':
            ads = [
                {
                    'id': 'ad_3',
                    'title': 'Adobe Creative Suite - Student Discount',
                    'description': 'Get 60% off Adobe Creative Cloud. Perfect for digital artists, designers, and content creators.',
                    'category': 'software',
                    'target_url': 'https://example.com/adobe-discount',
                    'image_url': 'https://example.com/images/adobe-suite.jpg',
                    'relevance_score': 0.95,
                    'call_to_action': 'Get Discount'
                },
                {
                    'id': 'ad_4',
                    'title': 'Digital Art Tablet - Wacom Intuos',
                    'description': 'Professional drawing tablet with pressure sensitivity. Take your digital art to the next level.',
                    'category': 'equipment',
                    'target_url': 'https://example.com/wacom-tablet',
                    'image_url': 'https://example.com/images/drawing-tablet.jpg',
                    'relevance_score': 0.85,
                    'call_to_action': 'Buy Now'
                }
            ]
        else:
            # Generic creative ads
            ads = [
                {
                    'id': 'ad_5',
                    'title': 'Creator Economy Masterclass',
                    'description': 'Learn how to monetize your creative skills. From building audience to generating revenue streams.',
                    'category': 'education',
                    'target_url': 'https://example.com/creator-masterclass',
                    'image_url': 'https://example.com/images/creator-course.jpg',
                    'relevance_score': 0.7,
                    'call_to_action': 'Learn More'
                }
            ]
        
        return ads
    
    def _extract_themes_from_text(self, text: str) -> List[str]:
        """Extract themes from text content"""
        
        # Simple keyword extraction - in production, use NLP
        keywords = []
        common_themes = [
            'abstract', 'portrait', 'landscape', 'digital', 'traditional',
            'photography', 'illustration', 'design', 'animation', 'music',
            'electronic', 'acoustic', 'jazz', 'rock', 'classical',
            'storytelling', 'narrative', 'documentary', 'fiction'
        ]
        
        text_lower = text.lower()
        for theme in common_themes:
            if theme in text_lower:
                keywords.append(theme)
        
        return keywords
    
    def _get_fallback_ads(self, profile: CreatorProfile) -> List[Dict]:
        """Get fallback ads when AI is unavailable"""
        
        return [
            {
                'id': 'fallback_1',
                'title': 'Creator Tools & Resources',
                'description': 'Discover essential tools and resources to enhance your creative workflow and grow your audience.',
                'category': 'general',
                'target_url': 'https://example.com/creator-tools',
                'image_url': 'https://example.com/images/creator-tools.jpg',
                'relevance_score': 0.5,
                'call_to_action': 'Explore'
            },
            {
                'id': 'fallback_2',
                'title': 'Join Creator Community',
                'description': 'Connect with fellow creators, share your work, and collaborate on exciting projects.',
                'category': 'community',
                'target_url': 'https://example.com/creator-community',
                'image_url': 'https://example.com/images/community.jpg',
                'relevance_score': 0.6,
                'call_to_action': 'Join Now'
            }
        ]
    
    def track_ad_interaction(self, profile: CreatorProfile, ad_id: str, interaction_type: str) -> Dict:
        """Track ad interactions for analytics"""
        
        try:
            interaction_data = {
                'profile_id': str(profile.id),
                'ad_id': ad_id,
                'interaction_type': interaction_type,  # 'view', 'click', 'dismiss'
                'timestamp': timezone.now().isoformat(),
                'context': 'platform'
            }
            
            # In production, store in analytics database
            self._store_interaction_data(interaction_data)
            
            return {
                'success': True,
                'message': 'Interaction tracked successfully'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to track interaction: {str(e)}'
            }
    
    def get_ad_performance_insights(self, profile: CreatorProfile) -> Dict:
        """Get ad performance insights for the creator"""
        
        try:
            # Mock analytics data - in production, query from analytics database
            insights = {
                'total_ads_shown': 25,
                'total_clicks': 3,
                'click_through_rate': 0.12,
                'most_relevant_category': 'software',
                'engagement_score': 0.75,
                'recommendations': [
                    'You engage most with software and tool advertisements',
                    'Consider exploring educational content ads',
                    'Equipment ads show high relevance for your profile'
                ]
            }
            
            return {
                'success': True,
                'insights': insights
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get insights: {str(e)}'
            }
    
    def _store_interaction_data(self, data: Dict):
        """Store interaction data (mock implementation)"""
        # In production, store in analytics database or send to analytics service
        pass

# Service instance
ad_showcase_service = AdShowcaseService()
