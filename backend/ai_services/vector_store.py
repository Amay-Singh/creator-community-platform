"""
Vector Store for AI Matching Engine
Handles profile embeddings and similarity search
"""
import numpy as np
import logging
from typing import List, Tuple, Optional, Dict, Any
from django.conf import settings
from django.core.cache import cache
from accounts.models import CreatorProfile
import json

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Vector storage and similarity search for creator profiles
    """
    
    def __init__(self):
        self.embedding_dim = 384  # Sentence transformer dimension
        self.cache_timeout = 3600  # 1 hour
        
    def get_profile_embedding(self, profile_id: str) -> Optional[np.ndarray]:
        """
        Get or generate embedding vector for a profile
        
        Args:
            profile_id: CreatorProfile ID
            
        Returns:
            Numpy array of embedding vector or None if not found
        """
        try:
            # Check cache first
            cache_key = f"embedding:{profile_id}"
            cached_embedding = cache.get(cache_key)
            if cached_embedding is not None:
                return np.array(cached_embedding)
            
            # Get profile data
            profile = CreatorProfile.objects.get(id=profile_id)
            
            # Generate embedding from profile features
            embedding = self._generate_profile_embedding(profile)
            
            # Cache the embedding
            cache.set(cache_key, embedding.tolist(), self.cache_timeout)
            
            return embedding
            
        except CreatorProfile.DoesNotExist:
            logger.warning(f"Profile not found: {profile_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting embedding for profile {profile_id}: {str(e)}")
            return None
    
    def find_similar(
        self, 
        query_vector: np.ndarray, 
        k: int = 20, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float]]:
        """
        Find similar profiles using vector similarity
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            filters: Optional filters to apply
            
        Returns:
            List of (profile_id, similarity_score) tuples
        """
        try:
            # Get all profiles that match filters
            profiles_queryset = CreatorProfile.objects.all()
            
            if filters:
                profiles_queryset = self._apply_filters(profiles_queryset, filters)
            
            # Calculate similarities
            similarities = []
            
            for profile in profiles_queryset:
                profile_vector = self.get_profile_embedding(profile.id)
                if profile_vector is not None:
                    similarity = self._cosine_similarity(query_vector, profile_vector)
                    similarities.append((profile.id, similarity))
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:k]
            
        except Exception as e:
            logger.error(f"Error finding similar profiles: {str(e)}")
            return []
    
    def update_profile_embedding(self, profile_id: str) -> bool:
        """
        Update embedding for a profile (called when profile changes)
        
        Args:
            profile_id: CreatorProfile ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clear cache
            cache_key = f"embedding:{profile_id}"
            cache.delete(cache_key)
            
            # Regenerate embedding
            embedding = self.get_profile_embedding(profile_id)
            
            return embedding is not None
            
        except Exception as e:
            logger.error(f"Error updating embedding for profile {profile_id}: {str(e)}")
            return False
    
    def _generate_profile_embedding(self, profile: CreatorProfile) -> np.ndarray:
        """
        Generate embedding vector from profile features
        
        Args:
            profile: CreatorProfile instance
            
        Returns:
            Numpy array embedding vector
        """
        try:
            # Create feature vector from profile data
            features = []
            
            # Text features (bio, skills, category)
            text_features = self._extract_text_features(profile)
            features.extend(text_features)
            
            # Categorical features (category, location, etc.)
            categorical_features = self._extract_categorical_features(profile)
            features.extend(categorical_features)
            
            # Numerical features (portfolio count, etc.)
            numerical_features = self._extract_numerical_features(profile)
            features.extend(numerical_features)
            
            # Pad or truncate to fixed dimension
            if len(features) < self.embedding_dim:
                features.extend([0.0] * (self.embedding_dim - len(features)))
            else:
                features = features[:self.embedding_dim]
            
            # Normalize vector
            vector = np.array(features, dtype=np.float32)
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            return vector
            
        except Exception as e:
            logger.error(f"Error generating embedding for profile {profile.id}: {str(e)}")
            # Return random normalized vector as fallback
            vector = np.random.randn(self.embedding_dim).astype(np.float32)
            return vector / np.linalg.norm(vector)
    
    def _extract_text_features(self, profile: CreatorProfile) -> List[float]:
        """Extract features from text fields"""
        features = []
        
        # Combine text features
        text_content = " ".join([
            profile.bio or "",
            profile.category or "",
            profile.subcategory or "",
            profile.location or "",
            profile.experience_level or ""
        ])
        
        # Create simple hash-based features
        words = text_content.lower().split()
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Convert to feature vector (simplified)
        feature_hash = hash(text_content) % 100
        features.extend([float(feature_hash), len(words), len(set(words))])
        
        return features
    
    def _extract_categorical_features(self, profile: CreatorProfile) -> List[float]:
        """Extract features from categorical fields"""
        features = []
        
        # Category encoding
        categories = [
            'music', 'visual_arts', 'writing', 'video', 'photography', 
            'design', 'gaming', 'tech', 'fashion', 'other'
        ]
        category_vector = [1.0 if profile.category == cat else 0.0 for cat in categories]
        features.extend(category_vector)
        
        # Skills encoding (placeholder - skills field doesn't exist in current model)
        common_skills = [
            'photography', 'video_editing', 'graphic_design', 'music_production',
            'writing', 'social_media', 'marketing', 'web_design', 'animation',
            'illustration', 'singing', 'dancing', 'acting', 'coding', 'gaming'
        ]
        # Use category as proxy for skills
        skills_vector = [1.0 if profile.category in ['performing_arts', 'visual_arts'] else 0.0 for _ in common_skills]
        features.extend(skills_vector)
        
        return features
    
    def _extract_numerical_features(self, profile: CreatorProfile) -> List[float]:
        """Extract numerical features"""
        features = []
        
        # Portfolio metrics (placeholder - portfolio_items relationship doesn't exist yet)
        portfolio_count = 0  # Will be implemented when PortfolioItem model is connected
        features.append(float(portfolio_count))
        
        # Profile completeness
        completeness = self._calculate_profile_completeness(profile)
        features.append(completeness)
        
        # Location features (placeholder - latitude/longitude fields don't exist in current model)
        features.extend([0.0, 0.0])
        
        # Account age (days since creation)
        from django.utils import timezone
        age_days = (timezone.now() - profile.created_at).days
        features.append(min(age_days / 365.0, 5.0))  # Cap at 5 years
        
        # Experience level encoding
        experience_levels = ['beginner', 'intermediate', 'advanced', 'professional']
        exp_vector = [1.0 if profile.experience_level == level else 0.0 for level in experience_levels]
        features.extend(exp_vector)
        
        return features
    
    def _calculate_profile_completeness(self, profile: CreatorProfile) -> float:
        """Calculate profile completeness score (0-1)"""
        score = 0.0
        total_fields = 8
        
        if profile.bio:
            score += 1
        if profile.category:
            score += 1
        if profile.location:
            score += 1
        if profile.website_url:
            score += 1
        if profile.instagram_url:
            score += 1
        if profile.youtube_url:
            score += 1
        if profile.spotify_url:
            score += 1
        if profile.experience_level:
            score += 1
        
        return score / total_fields
    
    def _apply_filters(self, queryset, filters: Dict[str, Any]):
        """Apply search filters to queryset"""
        if 'category' in filters:
            queryset = queryset.filter(category=filters['category'])
        
        if 'skills' in filters:
            # Skills filtering not implemented yet - placeholder
            pass
        
        if 'location' in filters:
            queryset = queryset.filter(location__icontains=filters['location'])
        
        if 'min_portfolio_items' in filters:
            # This would need a proper count annotation in production
            pass
        
        if 'exclude_user_ids' in filters:
            queryset = queryset.exclude(user__id__in=filters['exclude_user_ids'])
        
        return queryset
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
