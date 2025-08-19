"""
AI Collaboration Matching Service
Implements REQ-6, REQ-7: AI-generated collaboration suggestions and recommendations
"""
import openai
from django.conf import settings
from django.db.models import Q
from accounts.models import CreatorProfile
from collaborations.models import AICollaborationSuggestion
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class CollaborationMatcher:
    """AI-powered collaboration matching service"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    @staticmethod
    def generate_suggestions_for_profile(profile: CreatorProfile, limit: int = 10) -> List[Dict[str, Any]]:
        """Generate AI-powered collaboration suggestions for a profile"""
        try:
            # Get potential matches excluding already suggested profiles
            existing_suggestions = AICollaborationSuggestion.objects.filter(
                profile=profile,
                expires_at__gt=datetime.now()
            ).values_list('suggested_profile_id', flat=True)
            
            potential_matches = CreatorProfile.objects.filter(
                is_validated=True
            ).exclude(
                Q(id=profile.id) | Q(id__in=existing_suggestions)
            )[:50]  # Limit for performance
            
            suggestions = []
            
            for candidate in potential_matches:
                match_data = CollaborationMatcher._analyze_compatibility(profile, candidate)
                if match_data['score'] >= 60:  # Minimum threshold
                    suggestions.append({
                        'candidate': candidate,
                        'match_data': match_data
                    })
            
            # Sort by score and return top matches
            suggestions.sort(key=lambda x: x['match_data']['score'], reverse=True)
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error generating suggestions for {profile.id}: {e}")
            return []
    
    @staticmethod
    def _analyze_compatibility(profile1: CreatorProfile, profile2: CreatorProfile) -> Dict[str, Any]:
        """Analyze compatibility between two profiles using AI"""
        try:
            # Prepare profile data for AI analysis
            profile1_data = {
                'category': profile1.category,
                'subcategory': profile1.subcategory,
                'experience': profile1.experience_level,
                'bio': profile1.bio,
                'location': profile1.location,
                'portfolio_count': profile1.portfolio_items.count(),
                'health_score': profile1.health_score
            }
            
            profile2_data = {
                'category': profile2.category,
                'subcategory': profile2.subcategory,
                'experience': profile2.experience_level,
                'bio': profile2.bio,
                'location': profile2.location,
                'portfolio_count': profile2.portfolio_items.count(),
                'health_score': profile2.health_score
            }
            
            # Calculate base compatibility scores
            category_score = CollaborationMatcher._calculate_category_compatibility(profile1, profile2)
            location_score = CollaborationMatcher._calculate_location_compatibility(profile1, profile2)
            experience_score = CollaborationMatcher._calculate_experience_compatibility(profile1, profile2)
            
            # Use AI for advanced matching
            ai_analysis = CollaborationMatcher._get_ai_compatibility_analysis(profile1_data, profile2_data)
            
            # Combine scores
            final_score = (
                category_score * 0.3 +
                location_score * 0.2 +
                experience_score * 0.2 +
                ai_analysis.get('ai_score', 50) * 0.3
            )
            
            return {
                'score': min(100, max(0, final_score)),
                'category_score': category_score,
                'location_score': location_score,
                'experience_score': experience_score,
                'ai_score': ai_analysis.get('ai_score', 50),
                'suggestion_type': CollaborationMatcher._determine_suggestion_type(profile1, profile2),
                'explanation': ai_analysis.get('explanation', 'Compatible profiles for collaboration'),
                'project_suggestions': ai_analysis.get('project_suggestions', [])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing compatibility: {e}")
            return {
                'score': 0,
                'explanation': 'Error analyzing compatibility',
                'project_suggestions': []
            }
    
    @staticmethod
    def _calculate_category_compatibility(profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate category-based compatibility score"""
        if profile1.category == profile2.category:
            return 90  # Same category - high compatibility
        
        # Define complementary categories
        complementary_pairs = {
            'visual_arts': ['design', 'digital_arts', 'media_arts'],
            'performing_arts': ['media_arts', 'literary_arts'],
            'literary_arts': ['performing_arts', 'media_arts'],
            'design': ['visual_arts', 'digital_arts'],
            'digital_arts': ['visual_arts', 'design', 'media_arts'],
            'media_arts': ['visual_arts', 'performing_arts', 'digital_arts'],
            'crafts': ['design', 'visual_arts'],
            'culinary_arts': ['media_arts', 'visual_arts']
        }
        
        if profile2.category in complementary_pairs.get(profile1.category, []):
            return 75  # Complementary categories
        
        return 40  # Different, non-complementary categories
    
    @staticmethod
    def _calculate_location_compatibility(profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate location-based compatibility score"""
        if not profile1.location or not profile2.location:
            return 60  # Neutral if location not specified
        
        if profile1.location.lower() == profile2.location.lower():
            return 100  # Same location
        
        # Check for same city/region (simplified)
        location1_parts = profile1.location.lower().split(',')
        location2_parts = profile2.location.lower().split(',')
        
        for part1 in location1_parts:
            for part2 in location2_parts:
                if part1.strip() == part2.strip():
                    return 80  # Partial location match
        
        return 30  # Different locations (but remote collaboration possible)
    
    @staticmethod
    def _calculate_experience_compatibility(profile1: CreatorProfile, profile2: CreatorProfile) -> float:
        """Calculate experience level compatibility"""
        experience_levels = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'professional': 4}
        
        level1 = experience_levels.get(profile1.experience_level, 2)
        level2 = experience_levels.get(profile2.experience_level, 2)
        
        difference = abs(level1 - level2)
        
        if difference == 0:
            return 100  # Same level
        elif difference == 1:
            return 80   # Adjacent levels
        elif difference == 2:
            return 60   # Mentor-mentee potential
        else:
            return 40   # Large gap
    
    @staticmethod
    def _get_ai_compatibility_analysis(profile1_data: Dict, profile2_data: Dict) -> Dict[str, Any]:
        """Get AI analysis of profile compatibility"""
        if not settings.OPENAI_API_KEY:
            return {'ai_score': 50, 'explanation': 'AI analysis unavailable'}
        
        try:
            prompt = f"""
            Analyze the compatibility between these two creator profiles for potential collaboration:
            
            Profile 1: {json.dumps(profile1_data, indent=2)}
            Profile 2: {json.dumps(profile2_data, indent=2)}
            
            Provide a JSON response with:
            1. ai_score (0-100): Overall compatibility score
            2. explanation: Brief explanation of why they're compatible
            3. project_suggestions: Array of 2-3 specific collaboration project ideas
            
            Consider their skills, experience levels, creative styles, and potential for mutual benefit.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI matchmaker for creative collaborations. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"AI compatibility analysis failed: {e}")
            return {
                'ai_score': 50,
                'explanation': 'Profiles show potential for collaboration',
                'project_suggestions': ['Creative collaboration project']
            }
    
    @staticmethod
    def _determine_suggestion_type(profile1: CreatorProfile, profile2: CreatorProfile) -> str:
        """Determine the type of collaboration suggestion"""
        if profile1.category == profile2.category:
            return 'style_similarity'
        elif profile1.location and profile2.location and profile1.location.lower() == profile2.location.lower():
            return 'location_based'
        elif profile1.portfolio_items.exists() and profile2.portfolio_items.exists():
            return 'portfolio_match'
        else:
            return 'skill_complement'
    
    @staticmethod
    def create_suggestion_records(profile: CreatorProfile, suggestions: List[Dict[str, Any]]):
        """Create AICollaborationSuggestion records in database"""
        try:
            for suggestion_data in suggestions:
                candidate = suggestion_data['candidate']
                match_data = suggestion_data['match_data']
                
                # Create suggestion record
                suggestion = AICollaborationSuggestion.objects.create(
                    profile=profile,
                    suggested_profile=candidate,
                    suggestion_type=match_data['suggestion_type'],
                    match_score=match_data['score'],
                    explanation=match_data['explanation'],
                    suggested_project_type=match_data.get('project_suggestions', ['Collaboration'])[0],
                    suggested_title=f"Collaboration with {candidate.display_name}",
                    suggested_description=match_data['explanation'],
                    expires_at=datetime.now() + timedelta(days=30)
                )
                
                logger.info(f"Created suggestion {suggestion.id} for {profile.display_name}")
                
        except Exception as e:
            logger.error(f"Error creating suggestion records: {e}")
    
    @staticmethod
    def refresh_suggestions_for_all_profiles():
        """Background task to refresh suggestions for all active profiles"""
        try:
            active_profiles = CreatorProfile.objects.filter(
                is_validated=True,
                user__is_active=True,
                last_active__gte=datetime.now() - timedelta(days=30)
            )
            
            for profile in active_profiles:
                suggestions = CollaborationMatcher.generate_suggestions_for_profile(profile, limit=5)
                CollaborationMatcher.create_suggestion_records(profile, suggestions)
                
            logger.info(f"Refreshed suggestions for {active_profiles.count()} profiles")
            
        except Exception as e:
            logger.error(f"Error refreshing suggestions: {e}")
