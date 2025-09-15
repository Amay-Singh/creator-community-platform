"""
AI-Powered Creator Matching Service for P5-001
Implements intelligent creator matching using vector embeddings and similarity search
"""
import json
import hashlib
import time
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Avg, Count
from django.core.cache import cache

from accounts.models import CreatorProfile
from .models import CreatorEmbedding, MatchResult, MatchFeedback, MatchHistory

# Optional imports with fallbacks
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None


class AIMatchingService:
    """
    Core service for AI-powered creator matching using vector embeddings
    """
    
    def __init__(self):
        self.openai_client = None
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        self.cache_timeout = 3600  # 1 hour
        
    def _get_openai_client(self):
        """Lazy initialization of OpenAI client"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed")
            
        if not self.openai_client:
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if not api_key:
                raise ValueError("OPENAI_API_KEY not configured")
            self.openai_client = openai.OpenAI(api_key=api_key)
        return self.openai_client
    
    def _extract_profile_text(self, creator: CreatorProfile) -> str:
        """Extract text representation of creator profile for embedding"""
        text_parts = []
        
        # Basic info
        if creator.bio:
            text_parts.append(f"Bio: {creator.bio}")
        
        # Skills
        if hasattr(creator, 'skills') and creator.skills:
            skills_text = ", ".join(creator.skills) if isinstance(creator.skills, list) else str(creator.skills)
            text_parts.append(f"Skills: {skills_text}")
        
        # Interests
        if hasattr(creator, 'interests') and creator.interests:
            interests_text = ", ".join(creator.interests) if isinstance(creator.interests, list) else str(creator.interests)
            text_parts.append(f"Interests: {interests_text}")
        
        # Location
        if creator.location:
            text_parts.append(f"Location: {creator.location}")
        
        # Experience level
        if hasattr(creator, 'experience_level') and creator.experience_level:
            text_parts.append(f"Experience: {creator.experience_level}")
        
        # Portfolio items (titles and descriptions)
        portfolio_items = creator.portfolio_items.all()[:5]  # Limit to avoid token limits
        for item in portfolio_items:
            if item.title:
                text_parts.append(f"Project: {item.title}")
            if item.description:
                text_parts.append(f"Description: {item.description[:200]}")  # Truncate long descriptions
        
        return " | ".join(text_parts)
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content to track changes"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def generate_embedding(self, creator: CreatorProfile) -> Optional[List[float]]:
        """Generate embedding vector for creator profile"""
        try:
            client = self._get_openai_client()
            profile_text = self._extract_profile_text(creator)
            
            if not profile_text.strip():
                return None
            
            response = client.embeddings.create(
                model=self.embedding_model,
                input=profile_text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            print(f"Error generating embedding for {creator.display_name}: {e}")
            return None
    
    def update_creator_embedding(self, creator: CreatorProfile, force_update: bool = False) -> bool:
        """Update or create embedding for a creator"""
        try:
            # Get or create embedding record
            embedding, created = CreatorEmbedding.objects.get_or_create(
                creator=creator,
                defaults={'embedding_vector': []}
            )
            
            # Check if update is needed
            if not force_update and not created and not embedding.needs_update:
                return True
            
            # Extract profile data and generate hashes
            profile_text = self._extract_profile_text(creator)
            skills_text = str(getattr(creator, 'skills', ''))
            bio_text = creator.bio or ''
            interests_text = str(getattr(creator, 'interests', ''))
            
            skills_hash = self._generate_content_hash(skills_text)
            bio_hash = self._generate_content_hash(bio_text)
            interests_hash = self._generate_content_hash(interests_text)
            
            # Generate new embedding
            embedding_vector = self.generate_embedding(creator)
            if not embedding_vector:
                return False
            
            # Update embedding record
            embedding.embedding_vector = embedding_vector
            embedding.skills_hash = skills_hash
            embedding.bio_hash = bio_hash
            embedding.interests_hash = interests_hash
            embedding.last_profile_update = creator.updated_at
            embedding.save()
            
            return True
            
        except Exception as e:
            print(f"Error updating embedding for {creator.display_name}: {e}")
            return False
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not NUMPY_AVAILABLE:
            # Fallback implementation
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot_product / (norm1 * norm2)
        
        # NumPy implementation
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def _calculate_compatibility_score(self, similarity: float, shared_skills: List[str], 
                                     complementary_skills: List[str]) -> float:
        """Calculate overall compatibility score from similarity and skills"""
        base_score = similarity * 60  # Base score from similarity (0-60)
        
        # Bonus for shared skills (0-20)
        shared_bonus = min(len(shared_skills) * 3, 20)
        
        # Bonus for complementary skills (0-20)
        complementary_bonus = min(len(complementary_skills) * 2, 20)
        
        total_score = base_score + shared_bonus + complementary_bonus
        return min(total_score, 100.0)
    
    def _analyze_skills_compatibility(self, creator1: CreatorProfile, creator2: CreatorProfile) -> Tuple[List[str], List[str]]:
        """Analyze shared and complementary skills between creators"""
        skills1 = set(getattr(creator1, 'skills', []) or [])
        skills2 = set(getattr(creator2, 'skills', []) or [])
        
        shared_skills = list(skills1.intersection(skills2))
        
        # Simple complementary skills logic (can be enhanced with skill taxonomy)
        complementary_skills = []
        skill_complements = {
            'music_production': ['vocals', 'songwriting', 'mixing'],
            'vocals': ['music_production', 'songwriting'],
            'video_editing': ['cinematography', 'motion_graphics'],
            'photography': ['photo_editing', 'graphic_design'],
            'writing': ['editing', 'proofreading', 'content_strategy'],
            'marketing': ['social_media', 'content_creation', 'analytics'],
        }
        
        for skill in skills1:
            complements = skill_complements.get(skill, [])
            for complement in complements:
                if complement in skills2:
                    complementary_skills.append(f"{skill} ↔ {complement}")
        
        return shared_skills, complementary_skills
    
    def _generate_match_reasons(self, creator1: CreatorProfile, creator2: CreatorProfile, 
                               similarity: float, shared_skills: List[str], 
                               complementary_skills: List[str]) -> List[str]:
        """Generate human-readable reasons for the match"""
        reasons = []
        
        if similarity > 0.8:
            reasons.append("Very high profile similarity")
        elif similarity > 0.6:
            reasons.append("High profile similarity")
        elif similarity > 0.4:
            reasons.append("Good profile similarity")
        
        if shared_skills:
            reasons.append(f"Shared skills: {', '.join(shared_skills[:3])}")
        
        if complementary_skills:
            reasons.append(f"Complementary skills: {', '.join(complementary_skills[:2])}")
        
        # Location-based reasons
        if creator1.location and creator2.location:
            if creator1.location.lower() == creator2.location.lower():
                reasons.append("Same location")
            elif any(word in creator1.location.lower() for word in creator2.location.lower().split()):
                reasons.append("Similar location")
        
        return reasons
    
    def find_matches(self, creator: CreatorProfile, limit: int = 10, 
                    filters: Optional[Dict] = None) -> List[MatchResult]:
        """Find matching creators using vector similarity"""
        start_time = time.time()
        
        try:
            # Ensure creator has embedding
            if not self.update_creator_embedding(creator):
                return []
            
            creator_embedding = CreatorEmbedding.objects.get(creator=creator)
            creator_vector = creator_embedding.embedding_vector
            
            # Get all other creators with embeddings
            other_embeddings = CreatorEmbedding.objects.exclude(creator=creator).select_related('creator')
            
            # Apply filters
            if filters:
                if 'location' in filters and filters['location']:
                    other_embeddings = other_embeddings.filter(
                        creator__location__icontains=filters['location']
                    )
                
                if 'skills' in filters and filters['skills']:
                    # This would need proper skill filtering implementation
                    pass
                
                if 'experience_level' in filters and filters['experience_level']:
                    # This would need experience level filtering
                    pass
            
            matches = []
            
            for embedding in other_embeddings[:1000]:  # Limit for performance
                other_creator = embedding.creator
                other_vector = embedding.embedding_vector
                
                if not other_vector:
                    continue
                
                # Calculate similarity
                similarity = self._cosine_similarity(creator_vector, other_vector)
                
                # Analyze skills
                shared_skills, complementary_skills = self._analyze_skills_compatibility(creator, other_creator)
                
                # Calculate compatibility score
                compatibility = self._calculate_compatibility_score(similarity, shared_skills, complementary_skills)
                
                # Generate match reasons
                reasons = self._generate_match_reasons(creator, other_creator, similarity, shared_skills, complementary_skills)
                
                # Create match result
                match = MatchResult(
                    requester=creator,
                    matched_creator=other_creator,
                    similarity_score=similarity,
                    compatibility_score=compatibility,
                    match_reasons=reasons,
                    shared_skills=shared_skills,
                    complementary_skills=complementary_skills,
                    match_type='general',
                    match_filters=filters or {},
                    expires_at=timezone.now() + timedelta(days=30)
                )
                
                matches.append(match)
            
            # Sort by compatibility score and limit results
            matches.sort(key=lambda x: x.compatibility_score, reverse=True)
            top_matches = matches[:limit]
            
            # Save matches to database
            MatchResult.objects.bulk_create(top_matches, ignore_conflicts=True)
            
            # Record match history
            processing_time = int((time.time() - start_time) * 1000)
            MatchHistory.objects.create(
                user=creator,
                request_type='find_matches',
                filters_used=filters or {},
                results_count=len(top_matches),
                processing_time_ms=processing_time,
                embedding_version='v1.0',
                top_similarity_score=top_matches[0].similarity_score if top_matches else None,
                average_compatibility=sum(m.compatibility_score for m in top_matches) / len(top_matches) if top_matches else None
            )
            
            return top_matches
            
        except Exception as e:
            print(f"Error finding matches for {creator.display_name}: {e}")
            return []
    
    def batch_update_embeddings(self, creator_ids: Optional[List] = None, force_update: bool = False) -> Dict[str, int]:
        """Batch update embeddings for multiple creators"""
        if creator_ids:
            creators = CreatorProfile.objects.filter(id__in=creator_ids)
        else:
            creators = CreatorProfile.objects.all()
        
        results = {'updated': 0, 'failed': 0, 'skipped': 0}
        
        for creator in creators:
            try:
                if self.update_creator_embedding(creator, force_update):
                    results['updated'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                print(f"Error updating embedding for {creator.display_name}: {e}")
                results['failed'] += 1
        
        return results
    
    def get_match_statistics(self, creator: CreatorProfile) -> Dict:
        """Get matching statistics for a creator"""
        cache_key = f"match_stats_{creator.id}"
        stats = cache.get(cache_key)
        
        if not stats:
            stats = {
                'total_matches': MatchResult.objects.filter(requester=creator).count(),
                'matches_viewed': MatchResult.objects.filter(requester=creator, status='viewed').count(),
                'matches_contacted': MatchResult.objects.filter(requester=creator, status='contacted').count(),
                'average_compatibility': MatchResult.objects.filter(requester=creator).aggregate(
                    avg=Avg('compatibility_score')
                )['avg'] or 0,
                'feedback_given': MatchFeedback.objects.filter(user=creator).count(),
                'average_feedback': MatchFeedback.objects.filter(user=creator).aggregate(
                    avg=Avg('rating')
                )['avg'] or 0,
                'recent_matches': MatchResult.objects.filter(
                    requester=creator,
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).count()
            }
            cache.set(cache_key, stats, self.cache_timeout)
        
        return stats


# Global service instance
matching_service = AIMatchingService()
