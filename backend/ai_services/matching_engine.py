"""
AI Matching Engine for Creator Community Platform
Implements SRCH-003, SRCH-004: AI collaboration suggestions with bias mitigation
"""
import numpy as np
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from django.conf import settings
from django.core.cache import cache
from accounts.models import CreatorProfile
from .vector_store import VectorStore
from .bias_mitigation import FairnessMitigator

logger = logging.getLogger(__name__)

@dataclass
class MatchCandidate:
    """Represents a potential match candidate"""
    user_id: str
    profile_id: str
    score: float
    reasons: List[str]
    skills_overlap: List[str]
    complementary_skills: List[str]
    location_distance: Optional[float] = None
    timezone_compatibility: Optional[str] = None

@dataclass
class MatchingRequest:
    """Request parameters for matching"""
    user_id: str
    intent: str  # 'collaboration', 'networking', 'mentorship'
    k: int = 20  # number of candidates
    diversity: float = 0.3  # 0=similarity, 1=diversity
    filters: Dict[str, Any] = None
    exclude_previous: bool = True

class MatchingEngine:
    """
    AI-powered creator matching engine with fairness controls
    """
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.fairness_mitigator = FairnessMitigator()
        self.cache_timeout = 300  # 5 minutes
        
    def generate_suggestions(self, request: MatchingRequest) -> List[MatchCandidate]:
        """
        Generate AI-powered collaboration suggestions
        
        Args:
            request: MatchingRequest with user preferences
            
        Returns:
            List of MatchCandidate objects sorted by relevance
        """
        try:
            # Get user profile and embedding
            user_profile = self._get_user_profile(request.user_id)
            if not user_profile:
                logger.warning(f"User profile not found: {request.user_id}")
                return []
            
            # Check cache first
            cache_key = self._get_cache_key(request)
            cached_results = cache.get(cache_key)
            if cached_results:
                logger.info(f"Returning cached results for user {request.user_id}")
                return cached_results
            
            # Get user embedding vector
            user_vector = self.vector_store.get_profile_embedding(user_profile.id)
            if user_vector is None:
                logger.warning(f"No embedding found for profile {user_profile.id}")
                return []
            
            # Find similar profiles
            similar_profiles = self.vector_store.find_similar(
                user_vector, 
                k=request.k * 3,  # Get more candidates for filtering
                filters=request.filters
            )
            
            # Convert to match candidates with explanations
            candidates = []
            for profile_id, similarity_score in similar_profiles:
                candidate_profile = self._get_profile_by_id(profile_id)
                if not candidate_profile or candidate_profile.user.id == request.user_id:
                    continue
                
                # Check if user has opted out of suggestions (placeholder - field doesn't exist yet)
                # if hasattr(candidate_profile, 'opt_out_suggestions') and candidate_profile.opt_out_suggestions:
                #     continue
                
                # Generate match candidate with reasons
                candidate = self._create_match_candidate(
                    user_profile, 
                    candidate_profile, 
                    similarity_score,
                    request.intent
                )
                
                if candidate:
                    candidates.append(candidate)
            
            # Apply diversity and fairness controls
            candidates = self._apply_diversity_controls(
                candidates, 
                request.diversity, 
                request.k
            )
            
            # Apply bias mitigation
            candidates = self.fairness_mitigator.mitigate_bias(
                candidates, 
                user_profile
            )
            
            # Cache results
            cache.set(cache_key, candidates, self.cache_timeout)
            
            logger.info(f"Generated {len(candidates)} suggestions for user {request.user_id}")
            return candidates[:request.k]
            
        except Exception as e:
            logger.error(f"Error generating suggestions for user {request.user_id}: {str(e)}")
            return []
    
    def explain_match(self, user_id: str, candidate_id: str) -> Dict[str, Any]:
        """
        Provide detailed explanation for why a match was suggested
        
        Args:
            user_id: Requesting user ID
            candidate_id: Candidate user ID
            
        Returns:
            Dictionary with detailed match explanation
        """
        try:
            user_profile = self._get_user_profile(user_id)
            candidate_profile = self._get_user_profile(candidate_id)
            
            if not user_profile or not candidate_profile:
                return {"error": "Profile not found"}
            
            # Get embeddings and calculate similarity
            user_vector = self.vector_store.get_profile_embedding(user_profile.id)
            candidate_vector = self.vector_store.get_profile_embedding(candidate_profile.id)
            
            if user_vector is None or candidate_vector is None:
                return {"error": "Embedding not found"}
            
            similarity = np.dot(user_vector, candidate_vector) / (
                np.linalg.norm(user_vector) * np.linalg.norm(candidate_vector)
            )
            
            # Analyze skill overlap and gaps (placeholder)
            user_skills = set(['placeholder_skill'])
            candidate_skills = set(['placeholder_skill'])
            
            skills_overlap = list(user_skills.intersection(candidate_skills))
            complementary_skills = list(candidate_skills.difference(user_skills))
            
            # Calculate location compatibility (placeholder)
            location_info = {
                "distance_km": None,
                "same_city": False,
                "same_country": False,
                "timezone_diff": None
            }
            
            explanation = {
                "overall_score": round(similarity, 3),
                "skills_analysis": {
                    "overlap": skills_overlap,
                    "complementary": complementary_skills[:5],  # Top 5
                    "overlap_percentage": len(skills_overlap) / max(len(user_skills), 1) * 100
                },
                "location_compatibility": location_info,
                "category_match": user_profile.category == candidate_profile.category,
                "experience_level": {
                    "user": self._get_experience_level(user_profile),
                    "candidate": self._get_experience_level(candidate_profile)
                },
                "collaboration_history": self._get_collaboration_history(user_id, candidate_id),
                "reasons": self._generate_detailed_reasons(
                    user_profile, 
                    candidate_profile, 
                    skills_overlap, 
                    complementary_skills
                )
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error explaining match {user_id} -> {candidate_id}: {str(e)}")
            return {"error": "Failed to generate explanation"}
    
    def record_feedback(self, user_id: str, candidate_id: str, feedback: str, rating: int):
        """
        Record user feedback on match quality for model improvement
        
        Args:
            user_id: User providing feedback
            candidate_id: Candidate being rated
            feedback: Text feedback
            rating: 1-5 star rating
        """
        try:
            # Store feedback for model training
            feedback_data = {
                "user_id": user_id,
                "candidate_id": candidate_id,
                "feedback": feedback,
                "rating": rating,
                "timestamp": np.datetime64('now')
            }
            
            # TODO: Store in feedback table for model retraining
            logger.info(f"Recorded feedback: {user_id} -> {candidate_id}, rating: {rating}")
            
        except Exception as e:
            logger.error(f"Error recording feedback: {str(e)}")
    
    def _get_user_profile(self, user_id: str) -> Optional[CreatorProfile]:
        """Get user profile by user ID"""
        try:
            return CreatorProfile.objects.select_related('user').get(user__id=user_id)
        except CreatorProfile.DoesNotExist:
            return None
    
    def _get_profile_by_id(self, profile_id: str) -> Optional[CreatorProfile]:
        """Get profile by profile ID"""
        try:
            return CreatorProfile.objects.select_related('user').get(id=profile_id)
        except CreatorProfile.DoesNotExist:
            return None
    
    def _create_match_candidate(
        self, 
        user_profile: CreatorProfile, 
        candidate_profile: CreatorProfile, 
        similarity_score: float,
        intent: str
    ) -> Optional[MatchCandidate]:
        """Create a MatchCandidate with reasons and analysis"""
        try:
            # Analyze skills (placeholder since skills field doesn't exist in current model)
            user_skills = set(['placeholder_skill'])
            candidate_skills = set(['placeholder_skill'])
            
            skills_overlap = list(user_skills.intersection(candidate_skills))
            complementary_skills = list(candidate_skills.difference(user_skills))
            
            # Generate reasons based on analysis
            reasons = []
            
            if len(skills_overlap) > 0:
                reasons.append(f"Shared skills: {', '.join(skills_overlap[:3])}")
            
            if len(complementary_skills) > 0:
                reasons.append(f"Complementary skills: {', '.join(complementary_skills[:3])}")
            
            if user_profile.category == candidate_profile.category:
                reasons.append(f"Same category: {user_profile.category}")
            
            # Location analysis
            location_distance = self._calculate_distance(user_profile, candidate_profile)
            if location_distance and location_distance < 50:  # Within 50km
                reasons.append(f"Nearby location ({location_distance:.1f}km)")
            
            # Experience level compatibility
            user_exp = self._get_experience_level(user_profile)
            candidate_exp = self._get_experience_level(candidate_profile)
            
            if intent == 'mentorship':
                if candidate_exp > user_exp:
                    reasons.append("Potential mentor (higher experience)")
                elif user_exp > candidate_exp:
                    reasons.append("Potential mentee (lower experience)")
            elif abs(user_exp - candidate_exp) <= 1:
                reasons.append("Similar experience level")
            
            return MatchCandidate(
                user_id=candidate_profile.user.id,
                profile_id=candidate_profile.id,
                score=similarity_score,
                reasons=reasons,
                skills_overlap=skills_overlap,
                complementary_skills=complementary_skills,
                location_distance=location_distance,
                timezone_compatibility=self._get_timezone_compatibility(
                    user_profile, 
                    candidate_profile
                )
            )
            
        except Exception as e:
            logger.error(f"Error creating match candidate: {str(e)}")
            return None
    
    def _apply_diversity_controls(
        self, 
        candidates: List[MatchCandidate], 
        diversity: float, 
        k: int
    ) -> List[MatchCandidate]:
        """Apply diversity controls to candidate list"""
        if diversity == 0.0:
            # Pure similarity ranking
            return sorted(candidates, key=lambda x: x.score, reverse=True)
        
        # Implement diversity injection
        selected = []
        remaining = candidates.copy()
        
        # Start with highest scoring candidate
        remaining.sort(key=lambda x: x.score, reverse=True)
        if remaining:
            selected.append(remaining.pop(0))
        
        # Add diverse candidates
        while len(selected) < k and remaining:
            if np.random.random() < diversity:
                # Select diverse candidate
                diverse_candidate = self._select_diverse_candidate(selected, remaining)
                if diverse_candidate:
                    selected.append(diverse_candidate)
                    remaining.remove(diverse_candidate)
                else:
                    # Fallback to highest scoring
                    selected.append(remaining.pop(0))
            else:
                # Select highest scoring
                selected.append(remaining.pop(0))
        
        return selected
    
    def _select_diverse_candidate(
        self, 
        selected: List[MatchCandidate], 
        remaining: List[MatchCandidate]
    ) -> Optional[MatchCandidate]:
        """Select a diverse candidate from remaining list"""
        if not selected or not remaining:
            return None
        
        # Find candidate with most different skills
        selected_skills = set()
        for candidate in selected:
            selected_skills.update(candidate.skills_overlap)
            selected_skills.update(candidate.complementary_skills)
        
        best_candidate = None
        max_diversity = 0
        
        for candidate in remaining:
            candidate_skills = set(candidate.skills_overlap + candidate.complementary_skills)
            diversity_score = len(candidate_skills.difference(selected_skills))
            
            if diversity_score > max_diversity:
                max_diversity = diversity_score
                best_candidate = candidate
        
        return best_candidate
    
    def _calculate_distance(
        self, 
        profile1: CreatorProfile, 
        profile2: CreatorProfile
    ) -> Optional[float]:
        """Calculate distance between two profiles in kilometers"""
        # Placeholder - latitude/longitude fields don't exist in current model
        return None
    
    def _calculate_location_compatibility(
        self, 
        user_profile: CreatorProfile, 
        candidate_profile: CreatorProfile
    ) -> Dict[str, Any]:
        """Calculate location compatibility metrics"""
        distance = self._calculate_distance(user_profile, candidate_profile)
        
        compatibility = {
            "distance_km": distance,
            "same_city": False,
            "same_country": False,
            "timezone_diff": None
        }
        
        if user_profile.location and candidate_profile.location:
            user_location = user_profile.location.lower()
            candidate_location = candidate_profile.location.lower()
            
            # Simple city/country matching
            compatibility["same_city"] = user_location == candidate_location
            
            # Extract country (simplified)
            user_parts = user_location.split(',')
            candidate_parts = candidate_location.split(',')
            
            if len(user_parts) > 1 and len(candidate_parts) > 1:
                compatibility["same_country"] = user_parts[-1].strip() == candidate_parts[-1].strip()
        
        return compatibility
    
    def _get_experience_level(self, profile: CreatorProfile) -> int:
        """Calculate experience level (1-5) based on profile data"""
        # Map experience_level field to numeric score
        level_mapping = {
            'beginner': 1,
            'intermediate': 3,
            'advanced': 4,
            'professional': 5
        }
        return level_mapping.get(profile.experience_level, 2)
    
    def _get_timezone_compatibility(
        self, 
        user_profile: CreatorProfile, 
        candidate_profile: CreatorProfile
    ) -> Optional[str]:
        """Get timezone compatibility assessment"""
        # Simplified timezone compatibility
        # In real implementation, would use proper timezone libraries
        return "compatible"  # Placeholder
    
    def _get_collaboration_history(self, user_id: str, candidate_id: str) -> Dict[str, Any]:
        """Get collaboration history between users"""
        # TODO: Implement collaboration history lookup
        return {
            "previous_collaborations": 0,
            "successful_projects": 0,
            "last_collaboration": None
        }
    
    def _generate_detailed_reasons(
        self, 
        user_profile: CreatorProfile, 
        candidate_profile: CreatorProfile,
        skills_overlap: List[str],
        complementary_skills: List[str]
    ) -> List[str]:
        """Generate detailed reasons for the match"""
        reasons = []
        
        if skills_overlap:
            reasons.append(f"You both excel in {', '.join(skills_overlap[:3])}")
        
        if complementary_skills:
            reasons.append(f"They bring expertise in {', '.join(complementary_skills[:3])}")
        
        if user_profile.category == candidate_profile.category:
            reasons.append(f"Both work in {user_profile.category}")
        
        # Add more sophisticated reasoning based on profile analysis
        return reasons
    
    def _get_cache_key(self, request: MatchingRequest) -> str:
        """Generate cache key for matching request"""
        filters_str = str(sorted(request.filters.items())) if request.filters else ""
        return f"match:{request.user_id}:{request.intent}:{request.k}:{request.diversity}:{hash(filters_str)}"
