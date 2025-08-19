"""
Advanced Search Service with AI Recommendations
Implements REQ-5: Advanced search with filters and REQ-7: AI-recommended profile browsing
"""
from django.db.models import Q, Count, Avg, F
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Optional
import openai
from django.conf import settings
from .models import CreatorProfile, PortfolioItem
from .personality_models import PersonalityProfile, CollaborationMatch

class ProfileSearchService:
    """
    Advanced profile search with AI recommendations
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
    
    def advanced_search(self, search_params: Dict, requesting_profile: Optional[CreatorProfile] = None) -> Dict:
        """
        Advanced search with multiple filters (REQ-5)
        
        Args:
            search_params: Dictionary containing search parameters
            requesting_profile: Profile making the search request
        
        Returns:
            Dictionary with search results and metadata
        """
        
        # Start with base queryset
        queryset = CreatorProfile.objects.filter(
            is_validated=True,
            user__is_active=True
        ).select_related('user').prefetch_related('portfolio_items')
        
        # Apply filters
        queryset = self._apply_category_filter(queryset, search_params.get('categories'))
        queryset = self._apply_location_filter(queryset, search_params.get('location'))
        queryset = self._apply_experience_filter(queryset, search_params.get('experience_levels'))
        queryset = self._apply_text_search(queryset, search_params.get('query'))
        queryset = self._apply_portfolio_filters(queryset, search_params)
        queryset = self._apply_availability_filter(queryset, search_params.get('availability'))
        
        # Apply sorting
        sort_by = search_params.get('sort_by', 'relevance')
        queryset = self._apply_sorting(queryset, sort_by, search_params.get('query'))
        
        # Pagination
        page = search_params.get('page', 1)
        page_size = min(search_params.get('page_size', 20), 50)
        offset = (page - 1) * page_size
        
        total_count = queryset.count()
        results = list(queryset[offset:offset + page_size])
        
        # Enhance results with AI recommendations if requesting profile exists
        if requesting_profile:
            results = self._enhance_with_ai_recommendations(results, requesting_profile)
        
        return {
            'results': [self._serialize_search_result(profile, requesting_profile) for profile in results],
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'has_next': offset + page_size < total_count,
            'filters_applied': self._get_applied_filters(search_params)
        }
    
    def get_ai_recommendations(self, profile: CreatorProfile, recommendation_type: str = 'collaboration') -> List[Dict]:
        """
        Get AI-powered profile recommendations (REQ-7)
        
        Args:
            profile: Profile to get recommendations for
            recommendation_type: Type of recommendations ('collaboration', 'inspiration', 'networking')
        
        Returns:
            List of recommended profiles with AI explanations
        """
        
        recommendations = []
        
        if recommendation_type == 'collaboration':
            recommendations = self._get_collaboration_recommendations(profile)
        elif recommendation_type == 'inspiration':
            recommendations = self._get_inspiration_recommendations(profile)
        elif recommendation_type == 'networking':
            recommendations = self._get_networking_recommendations(profile)
        
        # Enhance with AI explanations
        enhanced_recommendations = []
        for rec in recommendations:
            ai_explanation = self._generate_recommendation_explanation(profile, rec, recommendation_type)
            rec['ai_explanation'] = ai_explanation
            enhanced_recommendations.append(rec)
        
        return enhanced_recommendations
    
    def _apply_category_filter(self, queryset, categories):
        """Apply category filter"""
        if categories:
            if isinstance(categories, str):
                categories = [categories]
            queryset = queryset.filter(category__in=categories)
        return queryset
    
    def _apply_location_filter(self, queryset, location):
        """Apply location filter with radius support"""
        if location:
            if isinstance(location, dict):
                # Structured location with radius
                city = location.get('city')
                radius = location.get('radius', 50)  # km
                
                if city:
                    queryset = queryset.filter(
                        Q(location__icontains=city) |
                        Q(city__icontains=city)
                    )
            else:
                # Simple text location
                queryset = queryset.filter(
                    Q(location__icontains=location) |
                    Q(city__icontains=location)
                )
        return queryset
    
    def _apply_experience_filter(self, queryset, experience_levels):
        """Apply experience level filter"""
        if experience_levels:
            if isinstance(experience_levels, str):
                experience_levels = [experience_levels]
            queryset = queryset.filter(experience_level__in=experience_levels)
        return queryset
    
    def _apply_text_search(self, queryset, query):
        """Apply full-text search"""
        if query:
            search_vector = SearchVector('display_name', 'bio', 'skills')
            search_query = SearchQuery(query)
            queryset = queryset.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query)
        return queryset
    
    def _apply_portfolio_filters(self, queryset, search_params):
        """Apply portfolio-related filters"""
        
        # Portfolio count filter
        min_portfolio = search_params.get('min_portfolio_items')
        if min_portfolio:
            queryset = queryset.annotate(
                portfolio_count=Count('portfolio_items')
            ).filter(portfolio_count__gte=min_portfolio)
        
        # Media type filter
        media_types = search_params.get('media_types')
        if media_types:
            queryset = queryset.filter(
                portfolio_items__media_type__in=media_types
            ).distinct()
        
        # AI validation filter
        if search_params.get('ai_validated_only'):
            queryset = queryset.filter(
                portfolio_items__is_ai_validated=True
            ).distinct()
        
        return queryset
    
    def _apply_availability_filter(self, queryset, availability):
        """Apply availability filter"""
        if availability:
            # This would require an availability field in the model
            # For now, we'll use a simple active filter
            queryset = queryset.filter(
                user__last_login__gte=timezone.now() - timedelta(days=30)
            )
        return queryset
    
    def _apply_sorting(self, queryset, sort_by, query=None):
        """Apply sorting to queryset"""
        
        if sort_by == 'relevance' and query:
            return queryset.order_by('-rank', '-created_at')
        elif sort_by == 'newest':
            return queryset.order_by('-created_at')
        elif sort_by == 'experience':
            # Custom ordering by experience level
            experience_order = {
                'professional': 4,
                'advanced': 3,
                'intermediate': 2,
                'beginner': 1
            }
            case_statements = []
            for k, v in experience_order.items():
                case_statements.append(f"WHEN experience_level = '{k}' THEN {v}")
            case_sql = f"CASE {' '.join(case_statements)} END"
            return queryset.extra(
                select={'experience_order': case_sql}
            ).order_by('-experience_order', '-created_at')
        elif sort_by == 'portfolio_count':
            return queryset.annotate(
                portfolio_count=Count('portfolio_items')
            ).order_by('-portfolio_count', '-created_at')
        elif sort_by == 'rating':
            return queryset.annotate(
                avg_rating=Avg('feedback_received__rating')
            ).order_by('-avg_rating', '-created_at')
        else:
            return queryset.order_by('-created_at')
    
    def _get_collaboration_recommendations(self, profile: CreatorProfile) -> List[Dict]:
        """Get collaboration-focused recommendations"""
        
        recommendations = []
        
        # Get existing matches
        existing_matches = CollaborationMatch.objects.filter(
            Q(profile_a=profile) | Q(profile_b=profile)
        ).values_list('profile_a_id', 'profile_b_id')
        
        excluded_ids = set()
        for match in existing_matches:
            excluded_ids.update(match)
        excluded_ids.add(profile.id)
        
        # Find complementary categories
        complementary_categories = self._get_complementary_categories(profile.category)
        
        # Get candidates
        candidates = CreatorProfile.objects.filter(
            is_validated=True,
            category__in=complementary_categories
        ).exclude(id__in=excluded_ids)[:20]
        
        for candidate in candidates:
            compatibility_score = self._calculate_compatibility_score(profile, candidate)
            if compatibility_score > 0.6:
                recommendations.append({
                    'profile': candidate,
                    'score': compatibility_score,
                    'reason': 'collaboration_compatibility'
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:10]
    
    def _get_inspiration_recommendations(self, profile: CreatorProfile) -> List[Dict]:
        """Get inspiration-focused recommendations"""
        
        recommendations = []
        
        # Find profiles in same category with higher experience
        experience_levels = ['beginner', 'intermediate', 'advanced', 'professional']
        current_level_index = experience_levels.index(profile.experience_level) if profile.experience_level in experience_levels else 0
        
        higher_levels = experience_levels[current_level_index + 1:]
        
        if higher_levels:
            candidates = CreatorProfile.objects.filter(
                category=profile.category,
                experience_level__in=higher_levels,
                is_validated=True
            ).annotate(
                portfolio_count=Count('portfolio_items'),
                avg_rating=Avg('feedback_received__rating')
            ).filter(
                portfolio_count__gte=3
            ).order_by('-avg_rating', '-portfolio_count')[:15]
            
            for candidate in candidates:
                inspiration_score = self._calculate_inspiration_score(profile, candidate)
                recommendations.append({
                    'profile': candidate,
                    'score': inspiration_score,
                    'reason': 'inspiration_potential'
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:10]
    
    def _get_networking_recommendations(self, profile: CreatorProfile) -> List[Dict]:
        """Get networking-focused recommendations"""
        
        recommendations = []
        
        # Find profiles in same location or similar interests
        candidates = CreatorProfile.objects.filter(
            is_validated=True,
            location__icontains=profile.location.split(',')[0] if profile.location else ''
        ).exclude(id=profile.id)[:20]
        
        for candidate in candidates:
            networking_score = self._calculate_networking_score(profile, candidate)
            if networking_score > 0.5:
                recommendations.append({
                    'profile': candidate,
                    'score': networking_score,
                    'reason': 'networking_potential'
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:10]
    
    def _calculate_compatibility_score(self, profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate compatibility score between two profiles"""
        
        score = 0.0
        
        # Category complementarity
        if profile1.category != profile2.category:
            score += 0.3
        
        # Experience level compatibility
        levels = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'professional': 4}
        level1 = levels.get(profile1.experience_level, 2)
        level2 = levels.get(profile2.experience_level, 2)
        
        level_diff = abs(level1 - level2)
        if level_diff <= 1:
            score += 0.2
        
        # Portfolio quality
        if profile2.portfolio_items.filter(is_ai_validated=True).exists():
            score += 0.2
        
        # Feedback score
        avg_feedback = profile2.feedback_received.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        
        if avg_feedback and avg_feedback >= 4.0:
            score += 0.3
        
        return min(1.0, score)
    
    def _calculate_inspiration_score(self, profile: CreatorProfile, candidate: CreatorProfile) -> float:
        """Calculate inspiration potential score"""
        
        score = 0.0
        
        # Experience gap (higher is better for inspiration)
        levels = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'professional': 4}
        profile_level = levels.get(profile.experience_level, 1)
        candidate_level = levels.get(candidate.experience_level, 1)
        
        if candidate_level > profile_level:
            score += 0.4
        
        # Portfolio quality and quantity
        portfolio_count = candidate.portfolio_items.count()
        if portfolio_count >= 5:
            score += 0.3
        
        # Feedback rating
        avg_rating = candidate.feedback_received.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        
        if avg_rating:
            score += (avg_rating / 5.0) * 0.3
        
        return min(1.0, score)
    
    def _calculate_networking_score(self, profile: CreatorProfile, candidate: CreatorProfile) -> float:
        """Calculate networking potential score"""
        
        score = 0.0
        
        # Location proximity
        if profile.location and candidate.location:
            if profile.location.split(',')[0].strip().lower() == candidate.location.split(',')[0].strip().lower():
                score += 0.4
        
        # Similar experience level
        if profile.experience_level == candidate.experience_level:
            score += 0.3
        
        # Active profile
        if candidate.user.last_login and candidate.user.last_login >= timezone.now() - timedelta(days=7):
            score += 0.3
        
        return min(1.0, score)
    
    def _get_complementary_categories(self, category: str) -> List[str]:
        """Get categories that complement the given category"""
        
        complementary_map = {
            'visual_arts': ['performing_arts', 'media_arts', 'literary_arts'],
            'performing_arts': ['visual_arts', 'media_arts', 'digital_arts'],
            'literary_arts': ['visual_arts', 'media_arts', 'performing_arts'],
            'design': ['digital_arts', 'visual_arts', 'media_arts'],
            'digital_arts': ['design', 'visual_arts', 'performing_arts'],
            'crafts': ['design', 'visual_arts', 'media_arts'],
            'media_arts': ['visual_arts', 'performing_arts', 'digital_arts'],
            'culinary_arts': ['media_arts', 'visual_arts', 'design'],
            'architecture': ['design', 'visual_arts', 'digital_arts'],
        }
        
        return complementary_map.get(category, ['visual_arts', 'performing_arts', 'media_arts'])
    
    def _enhance_with_ai_recommendations(self, profiles: List[CreatorProfile], requesting_profile: CreatorProfile) -> List[CreatorProfile]:
        """Enhance search results with AI-powered insights"""
        
        # This could be expanded to reorder results based on AI recommendations
        # For now, we'll just add metadata
        
        for profile in profiles:
            # Add compatibility score
            profile._compatibility_score = self._calculate_compatibility_score(requesting_profile, profile)
            
            # Add recommendation reason
            if profile._compatibility_score > 0.7:
                profile._recommendation_reason = 'High compatibility match'
            elif profile.category != requesting_profile.category:
                profile._recommendation_reason = 'Cross-disciplinary collaboration potential'
            else:
                profile._recommendation_reason = 'Similar interests and skills'
        
        return profiles
    
    def _generate_recommendation_explanation(self, profile: CreatorProfile, recommendation: Dict, rec_type: str) -> str:
        """Generate AI explanation for recommendation"""
        
        client = self._get_client()
        if not client:
            return self._generate_fallback_explanation(profile, recommendation, rec_type)
        
        try:
            prompt = f"""
            Explain why {recommendation['profile'].display_name} ({recommendation['profile'].get_category_display()}, {recommendation['profile'].get_experience_level_display()}) 
            would be a good {rec_type} match for {profile.display_name} ({profile.get_category_display()}, {profile.get_experience_level_display()}).
            
            Compatibility score: {recommendation['score']:.2f}
            Reason: {recommendation['reason']}
            
            Provide a brief, engaging explanation (2-3 sentences) focusing on creative synergy and potential collaboration benefits.
            """
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative collaboration expert. Provide engaging, personalized explanations for why two creators would work well together."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception:
            return self._generate_fallback_explanation(profile, recommendation, rec_type)
    
    def _generate_fallback_explanation(self, profile: CreatorProfile, recommendation: Dict, rec_type: str) -> str:
        """Generate fallback explanation without AI"""
        
        candidate = recommendation['profile']
        score = recommendation['score']
        
        if rec_type == 'collaboration':
            if profile.category != candidate.category:
                return f"Great cross-disciplinary match! {candidate.display_name}'s {candidate.get_category_display()} expertise could complement your {profile.get_category_display()} skills perfectly."
            else:
                return f"Strong collaboration potential with {candidate.display_name}. Similar creative focus with complementary experience levels."
        
        elif rec_type == 'inspiration':
            return f"{candidate.display_name} is an experienced {candidate.get_category_display()} creator whose portfolio and achievements could provide valuable inspiration for your creative journey."
        
        else:  # networking
            return f"Connect with {candidate.display_name} for networking opportunities. Shared interests and similar experience level make for great professional connections."
    
    def _serialize_search_result(self, profile: CreatorProfile, requesting_profile: Optional[CreatorProfile]) -> Dict:
        """Serialize profile for search results"""
        
        result = {
            'id': str(profile.id),
            'display_name': profile.display_name,
            'category': profile.get_category_display(),
            'experience_level': profile.get_experience_level_display(),
            'location': profile.location,
            'bio': profile.bio[:200] + '...' if len(profile.bio) > 200 else profile.bio,
            'avatar_url': profile.avatar.url if profile.avatar else None,
            'portfolio_count': profile.portfolio_items.count(),
            'is_validated': profile.is_validated,
            'created_at': profile.created_at
        }
        
        # Add AI-enhanced fields if available
        if hasattr(profile, '_compatibility_score'):
            result['compatibility_score'] = profile._compatibility_score
        
        if hasattr(profile, '_recommendation_reason'):
            result['recommendation_reason'] = profile._recommendation_reason
        
        # Add feedback summary
        feedback_stats = profile.feedback_received.aggregate(
            avg_rating=Avg('rating'),
            count=Count('rating')
        )
        
        result['feedback'] = {
            'average_rating': feedback_stats['avg_rating'],
            'total_reviews': feedback_stats['count']
        }
        
        return result
    
    def _get_applied_filters(self, search_params: Dict) -> Dict:
        """Get summary of applied filters"""
        
        applied = {}
        
        if search_params.get('categories'):
            applied['categories'] = search_params['categories']
        
        if search_params.get('location'):
            applied['location'] = search_params['location']
        
        if search_params.get('experience_levels'):
            applied['experience_levels'] = search_params['experience_levels']
        
        if search_params.get('query'):
            applied['text_search'] = search_params['query']
        
        if search_params.get('min_portfolio_items'):
            applied['min_portfolio_items'] = search_params['min_portfolio_items']
        
        return applied

# Service instance
search_service = ProfileSearchService()
