"""
Optimized AI-powered Recommendation Engine - Phase 5 Guardian Fixes
Addresses N+1 query issues and performance bottlenecks
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
import logging
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Prefetch, Q, Count, Avg
from datetime import timedelta
from .models import CreatorProfile, MatchingResult, SearchQuery
from collaborations.models import NewCollaborationInvite
from notifications.models import Notification
from analytics.services import AnalyticsCollector

User = get_user_model()
logger = logging.getLogger(__name__)


class OptimizedRecommendationEngine:
    """
    Optimized AI-powered recommendation engine with performance fixes
    - Eliminates N+1 queries through proper prefetch_related usage
    - Implements Redis caching for expensive operations
    - Adds database query optimization
    """
    
    def __init__(self):
        self.tfidf_vectorizer = None
        self.svd_model = None
        self.user_clusters = None
        self.cache_timeout = 300  # 5 minutes cache
        self.project_categories = [
            'web_development', 'mobile_app', 'data_science', 'machine_learning',
            'design', 'marketing', 'content_creation', 'e_commerce', 'gaming',
            'blockchain', 'iot', 'ai_research', 'social_media', 'education'
        ]
        
    def get_user_recommendations(self, user_id: int, limit: int = 10) -> list:
        """
        Get personalized recommendations for a user
        OPTIMIZED: Uses select_related and prefetch_related to avoid N+1 queries
        """
        cache_key = f"user_recommendations_{user_id}_{limit}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            logger.info(f"Cache hit for user recommendations: {user_id}")
            return cached_result
        
        try:
            # OPTIMIZATION: Single query with all related data
            user_profile = CreatorProfile.objects.select_related(
                'user',
                'user__profile'
            ).prefetch_related(
                'skills',
                'interests',
                'user__sent_invites__recipient',
                'user__received_invites__sender'
            ).get(user_id=user_id)
            
            # Get potential matches with optimized query
            potential_matches = self._get_potential_matches_optimized(user_profile, limit * 2)
            
            # Score and rank matches
            scored_matches = self._score_matches_batch(user_profile, potential_matches)
            
            # Get top recommendations
            recommendations = scored_matches[:limit]
            
            # Cache results
            cache.set(cache_key, recommendations, self.cache_timeout)
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations
            
        except CreatorProfile.DoesNotExist:
            logger.warning(f"CreatorProfile not found for user {user_id}")
            return []
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {str(e)}")
            return []
    
    def _get_potential_matches_optimized(self, user_profile, limit: int) -> list:
        """
        Get potential matches with optimized database queries
        OPTIMIZATION: Single query with proper joins and filtering
        """
        # Build exclusion list (users already connected)
        excluded_users = set()
        
        # Add users with existing invitations
        existing_connections = NewCollaborationInvite.objects.filter(
            Q(sender=user_profile.user) | Q(recipient=user_profile.user)
        ).values_list('sender_id', 'recipient_id')
        
        for sender_id, recipient_id in existing_connections:
            excluded_users.add(sender_id)
            excluded_users.add(recipient_id)
        
        # Add self
        excluded_users.add(user_profile.user_id)
        
        # OPTIMIZATION: Single query with all necessary data
        potential_matches = CreatorProfile.objects.select_related(
            'user'
        ).prefetch_related(
            'skills',
            'interests',
            'user__sent_invites',
            'user__received_invites'
        ).exclude(
            user_id__in=excluded_users
        ).filter(
            user__is_active=True,
            is_available=True
        ).annotate(
            invite_count=Count('user__sent_invites'),
            avg_rating=Avg('user__received_invites__rating')
        )[:limit]
        
        return list(potential_matches)
    
    def _score_matches_batch(self, user_profile, potential_matches: list) -> list:
        """
        Score multiple matches in batch to improve performance
        OPTIMIZATION: Vectorized operations where possible
        """
        if not potential_matches:
            return []
        
        scored_matches = []
        user_skills = set(skill.name for skill in user_profile.skills.all())
        user_interests = set(interest.name for interest in user_profile.interests.all())
        
        for match in potential_matches:
            try:
                # Calculate similarity scores
                match_skills = set(skill.name for skill in match.skills.all())
                match_interests = set(interest.name for interest in match.interests.all())
                
                # Skill similarity (Jaccard coefficient)
                skill_similarity = self._jaccard_similarity(user_skills, match_skills)
                
                # Interest similarity
                interest_similarity = self._jaccard_similarity(user_interests, match_interests)
                
                # Location proximity (if available)
                location_score = self._calculate_location_proximity(user_profile, match)
                
                # Activity score (based on recent activity)
                activity_score = self._calculate_activity_score(match)
                
                # Reputation score
                reputation_score = self._calculate_reputation_score(match)
                
                # Combined score with weights
                total_score = (
                    skill_similarity * 0.3 +
                    interest_similarity * 0.2 +
                    location_score * 0.15 +
                    activity_score * 0.15 +
                    reputation_score * 0.2
                )
                
                scored_matches.append({
                    'user_id': match.user_id,
                    'username': match.user.username,
                    'profile': match,
                    'score': total_score,
                    'skill_similarity': skill_similarity,
                    'interest_similarity': interest_similarity,
                    'location_score': location_score,
                    'activity_score': activity_score,
                    'reputation_score': reputation_score
                })
                
            except Exception as e:
                logger.error(f"Error scoring match {match.user_id}: {str(e)}")
                continue
        
        # Sort by score (descending)
        scored_matches.sort(key=lambda x: x['score'], reverse=True)
        return scored_matches
    
    def _jaccard_similarity(self, set1: set, set2: set) -> float:
        """Calculate Jaccard similarity between two sets"""
        if not set1 and not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_location_proximity(self, user_profile, match_profile) -> float:
        """Calculate location proximity score"""
        try:
            if not (user_profile.location and match_profile.location):
                return 0.5  # Neutral score if location not available
            
            # Simple location matching (can be enhanced with geospatial calculations)
            if user_profile.location.lower() == match_profile.location.lower():
                return 1.0
            
            # Check if same city/region (basic string matching)
            user_location_parts = user_profile.location.lower().split(',')
            match_location_parts = match_profile.location.lower().split(',')
            
            for user_part in user_location_parts:
                for match_part in match_location_parts:
                    if user_part.strip() == match_part.strip():
                        return 0.7
            
            return 0.3  # Different locations
            
        except Exception as e:
            logger.error(f"Error calculating location proximity: {str(e)}")
            return 0.5
    
    def _calculate_activity_score(self, profile) -> float:
        """Calculate user activity score based on recent activity"""
        try:
            # Check recent login (if available)
            if hasattr(profile.user, 'last_login') and profile.user.last_login:
                days_since_login = (timezone.now() - profile.user.last_login).days
                if days_since_login <= 1:
                    return 1.0
                elif days_since_login <= 7:
                    return 0.8
                elif days_since_login <= 30:
                    return 0.6
                else:
                    return 0.3
            
            return 0.5  # Default if no login data
            
        except Exception as e:
            logger.error(f"Error calculating activity score: {str(e)}")
            return 0.5
    
    def _calculate_reputation_score(self, profile) -> float:
        """Calculate reputation score based on past collaborations"""
        try:
            # Use the annotated avg_rating if available
            if hasattr(profile, 'avg_rating') and profile.avg_rating:
                # Normalize rating (assuming 1-5 scale)
                return min(profile.avg_rating / 5.0, 1.0)
            
            # Fallback: count successful collaborations
            invite_count = getattr(profile, 'invite_count', 0)
            if invite_count > 10:
                return 0.9
            elif invite_count > 5:
                return 0.7
            elif invite_count > 0:
                return 0.6
            else:
                return 0.5  # New user
                
        except Exception as e:
            logger.error(f"Error calculating reputation score: {str(e)}")
            return 0.5
    
    def get_project_recommendations(self, user_id: int, project_category: str = None, limit: int = 10) -> list:
        """
        Get project recommendations for a user
        OPTIMIZED: Uses caching and batch processing
        """
        cache_key = f"project_recommendations_{user_id}_{project_category}_{limit}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        try:
            # This would integrate with a project model when available
            # For now, return mock recommendations based on user profile
            user_profile = CreatorProfile.objects.select_related('user').get(user_id=user_id)
            
            recommendations = self._generate_project_recommendations(user_profile, project_category, limit)
            
            cache.set(cache_key, recommendations, self.cache_timeout)
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating project recommendations: {str(e)}")
            return []
    
    def _generate_project_recommendations(self, user_profile, category: str, limit: int) -> list:
        """Generate project recommendations based on user skills and interests"""
        # This is a placeholder implementation
        # In a real system, this would query actual project data
        
        user_skills = [skill.name for skill in user_profile.skills.all()]
        recommendations = []
        
        # Mock project recommendations based on skills
        project_templates = {
            'web_development': ['E-commerce Platform', 'Portfolio Website', 'Blog Platform'],
            'mobile_app': ['Social Media App', 'Fitness Tracker', 'Food Delivery App'],
            'data_science': ['Data Visualization Dashboard', 'Predictive Analytics', 'ML Model'],
            'design': ['Brand Identity Package', 'UI/UX Design', 'Marketing Materials']
        }
        
        for skill in user_skills:
            if skill in project_templates:
                for project in project_templates[skill]:
                    if len(recommendations) < limit:
                        recommendations.append({
                            'title': project,
                            'category': skill,
                            'match_score': 0.8 + (len(recommendations) * 0.02),
                            'estimated_duration': '2-4 weeks',
                            'skill_match': skill
                        })
        
        return recommendations[:limit]
    
    def clear_user_cache(self, user_id: int):
        """Clear cached recommendations for a user"""
        cache_keys = [
            f"user_recommendations_{user_id}_*",
            f"project_recommendations_{user_id}_*"
        ]
        
        for pattern in cache_keys:
            cache.delete_pattern(pattern)
        
        logger.info(f"Cleared recommendation cache for user {user_id}")


# Singleton instance
recommendation_engine = OptimizedRecommendationEngine()
