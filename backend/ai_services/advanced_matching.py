"""
Advanced AI Matching Engine with Machine Learning
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sentence_transformers import SentenceTransformer
import faiss
import joblib
import logging
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import CreatorProfile, MatchingResult, SearchQuery
from analytics.services import AnalyticsCollector
import os

User = get_user_model()
logger = logging.getLogger(__name__)


class AdvancedMatchingEngine:
    """
    Advanced AI matching engine with machine learning capabilities
    """
    
    def __init__(self):
        self.sentence_model = None
        self.tfidf_vectorizer = None
        self.ml_model = None
        self.scaler = None
        self.faiss_index = None
        self.user_embeddings = {}
        self.model_cache_timeout = 3600  # 1 hour
        
    def initialize_models(self):
        """Initialize or load ML models"""
        try:
            # Load sentence transformer model
            model_cache_key = "sentence_transformer_model"
            self.sentence_model = cache.get(model_cache_key)
            
            if not self.sentence_model:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                cache.set(model_cache_key, self.sentence_model, self.model_cache_timeout)
            
            # Initialize TF-IDF vectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Load or initialize ML model for match scoring
            self._load_or_train_ml_model()
            
            # Initialize FAISS index for fast similarity search
            self._initialize_faiss_index()
            
            logger.info("Advanced matching models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing matching models: {e}")
            raise
    
    def _load_or_train_ml_model(self):
        """Load existing ML model or train a new one"""
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'matching_model.joblib')
        scaler_path = os.path.join(settings.BASE_DIR, 'ml_models', 'matching_scaler.joblib')
        
        try:
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.ml_model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                logger.info("Loaded existing ML matching model")
            else:
                self._train_ml_model()
                logger.info("Trained new ML matching model")
                
        except Exception as e:
            logger.error(f"Error loading/training ML model: {e}")
            # Fallback to simple model
            self.ml_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.scaler = StandardScaler()
    
    def _train_ml_model(self):
        """Train ML model using historical matching data"""
        try:
            # Get historical matching data
            matching_results = MatchingResult.objects.select_related('user', 'matched_user').all()
            
            if matching_results.count() < 100:
                logger.warning("Insufficient data for ML training, using default model")
                self.ml_model = RandomForestRegressor(n_estimators=100, random_state=42)
                self.scaler = StandardScaler()
                return
            
            # Prepare training data
            features = []
            targets = []
            
            for result in matching_results:
                feature_vector = self._extract_features(result.user, result.matched_user)
                features.append(feature_vector)
                targets.append(result.match_score)
            
            X = np.array(features)
            y = np.array(targets)
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.ml_model = RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                random_state=42
            )
            self.ml_model.fit(X_scaled, y)
            
            # Save models
            os.makedirs(os.path.join(settings.BASE_DIR, 'ml_models'), exist_ok=True)
            joblib.dump(self.ml_model, os.path.join(settings.BASE_DIR, 'ml_models', 'matching_model.joblib'))
            joblib.dump(self.scaler, os.path.join(settings.BASE_DIR, 'ml_models', 'matching_scaler.joblib'))
            
            logger.info(f"ML model trained with {len(features)} samples")
            
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
            # Fallback to simple model
            self.ml_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.scaler = StandardScaler()
    
    def _initialize_faiss_index(self):
        """Initialize FAISS index for fast similarity search"""
        try:
            # Get all user profiles
            profiles = CreatorProfile.objects.select_related('user').all()
            
            if not profiles.exists():
                logger.warning("No user profiles found for FAISS index")
                return
            
            # Generate embeddings for all users
            embeddings = []
            user_ids = []
            
            for profile in profiles:
                embedding = self._get_user_embedding(profile)
                embeddings.append(embedding)
                user_ids.append(profile.user.id)
            
            # Create FAISS index
            embeddings_array = np.array(embeddings).astype('float32')
            dimension = embeddings_array.shape[1]
            
            self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings_array)
            self.faiss_index.add(embeddings_array)
            
            # Store user ID mapping
            self.user_id_mapping = {i: user_id for i, user_id in enumerate(user_ids)}
            
            logger.info(f"FAISS index initialized with {len(embeddings)} user embeddings")
            
        except Exception as e:
            logger.error(f"Error initializing FAISS index: {e}")
    
    def _get_user_embedding(self, profile):
        """Generate embedding for a user profile"""
        try:
            # Combine user information into text
            user_text = self._create_user_text(profile)
            
            # Generate sentence embedding
            embedding = self.sentence_model.encode(user_text)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating user embedding: {e}")
            # Return zero embedding as fallback
            return np.zeros(384)  # Default dimension for all-MiniLM-L6-v2
    
    def _create_user_text(self, profile):
        """Create text representation of user for embedding"""
        text_parts = []
        
        # Add skills
        if hasattr(profile, 'skills') and profile.skills:
            if isinstance(profile.skills, list):
                text_parts.append(" ".join(profile.skills))
            else:
                text_parts.append(str(profile.skills))
        
        # Add bio
        if hasattr(profile, 'bio') and profile.bio:
            text_parts.append(profile.bio)
        
        # Add location
        if hasattr(profile, 'location') and profile.location:
            text_parts.append(profile.location)
        
        # Add experience level
        if hasattr(profile, 'experience_level') and profile.experience_level:
            text_parts.append(f"Experience: {profile.experience_level}")
        
        return " ".join(text_parts) if text_parts else "No profile information"
    
    def _extract_features(self, user1, user2):
        """Extract features for ML model training/prediction"""
        try:
            profile1 = CreatorProfile.objects.get(user=user1)
            profile2 = CreatorProfile.objects.get(user=user2)
        except CreatorProfile.DoesNotExist:
            # Return default features if profiles don't exist
            return [0.0] * 10
        
        features = []
        
        # Skill similarity
        skills1 = profile1.skills if hasattr(profile1, 'skills') and profile1.skills else []
        skills2 = profile2.skills if hasattr(profile2, 'skills') and profile2.skills else []
        
        if isinstance(skills1, str):
            skills1 = skills1.split(',') if skills1 else []
        if isinstance(skills2, str):
            skills2 = skills2.split(',') if skills2 else []
        
        skill_intersection = len(set(skills1) & set(skills2))
        skill_union = len(set(skills1) | set(skills2))
        skill_similarity = skill_intersection / skill_union if skill_union > 0 else 0
        features.append(skill_similarity)
        
        # Location similarity (simplified)
        location1 = profile1.location if hasattr(profile1, 'location') else ""
        location2 = profile2.location if hasattr(profile2, 'location') else ""
        location_similarity = 1.0 if location1 == location2 else 0.0
        features.append(location_similarity)
        
        # Experience level compatibility
        exp1 = getattr(profile1, 'experience_level', 'beginner')
        exp2 = getattr(profile2, 'experience_level', 'beginner')
        exp_levels = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
        exp_diff = abs(exp_levels.get(exp1, 1) - exp_levels.get(exp2, 1))
        exp_compatibility = 1.0 - (exp_diff / 3.0)
        features.append(exp_compatibility)
        
        # Profile completeness
        completeness1 = self._calculate_profile_completeness(profile1)
        completeness2 = self._calculate_profile_completeness(profile2)
        features.extend([completeness1, completeness2])
        
        # Text similarity using embeddings
        text1 = self._create_user_text(profile1)
        text2 = self._create_user_text(profile2)
        
        if self.sentence_model:
            embedding1 = self.sentence_model.encode(text1)
            embedding2 = self.sentence_model.encode(text2)
            text_similarity = cosine_similarity([embedding1], [embedding2])[0][0]
        else:
            text_similarity = 0.0
        
        features.append(text_similarity)
        
        # Add more features as needed
        features.extend([0.0] * (10 - len(features)))  # Pad to 10 features
        
        return features[:10]  # Ensure exactly 10 features
    
    def _calculate_profile_completeness(self, profile):
        """Calculate how complete a user profile is"""
        fields = ['bio', 'skills', 'location', 'experience_level']
        completed = sum(1 for field in fields if hasattr(profile, field) and getattr(profile, field))
        return completed / len(fields)
    
    def find_advanced_matches(self, user, limit=20, filters=None):
        """Find matches using advanced ML algorithms"""
        try:
            if not self.sentence_model:
                self.initialize_models()
            
            # Get user profile
            try:
                user_profile = CreatorProfile.objects.get(user=user)
            except CreatorProfile.DoesNotExist:
                logger.warning(f"No profile found for user {user.id}")
                return []
            
            # Use FAISS for fast similarity search if available
            if self.faiss_index:
                candidate_matches = self._faiss_similarity_search(user, limit * 2)
            else:
                candidate_matches = self._traditional_similarity_search(user, limit * 2)
            
            # Apply ML scoring to candidates
            scored_matches = []
            for candidate_user in candidate_matches:
                if candidate_user.id == user.id:
                    continue
                
                # Extract features for ML model
                features = self._extract_features(user, candidate_user)
                
                # Predict match score using ML model
                if self.ml_model and self.scaler:
                    features_scaled = self.scaler.transform([features])
                    ml_score = self.ml_model.predict(features_scaled)[0]
                else:
                    ml_score = np.mean(features)  # Fallback to feature average
                
                # Combine with other factors
                final_score = self._calculate_final_score(user, candidate_user, ml_score)
                
                scored_matches.append({
                    'user': candidate_user,
                    'score': final_score,
                    'ml_score': ml_score,
                    'features': features
                })
            
            # Sort by score and return top matches
            scored_matches.sort(key=lambda x: x['score'], reverse=True)
            
            # Apply filters if provided
            if filters:
                scored_matches = self._apply_filters(scored_matches, filters)
            
            # Create MatchingResult objects
            results = []
            for match in scored_matches[:limit]:
                result = MatchingResult.objects.create(
                    user=user,
                    matched_user=match['user'],
                    match_score=match['score'],
                    algorithm_version='advanced_ml_v1',
                    metadata={
                        'ml_score': match['ml_score'],
                        'features': match['features']
                    }
                )
                results.append(result)
            
            # Track analytics
            AnalyticsCollector.track_event(
                'advanced_match_request',
                user=user,
                event_data={
                    'matches_found': len(results),
                    'algorithm': 'advanced_ml_v1',
                    'filters_applied': bool(filters)
                }
            )
            
            logger.info(f"Found {len(results)} advanced matches for user {user.id}")
            return results
            
        except Exception as e:
            logger.error(f"Error in advanced matching for user {user.id}: {e}")
            return []
    
    def _faiss_similarity_search(self, user, limit):
        """Use FAISS for fast similarity search"""
        try:
            user_profile = CreatorProfile.objects.get(user=user)
            user_embedding = self._get_user_embedding(user_profile)
            
            # Normalize for cosine similarity
            user_embedding = user_embedding.reshape(1, -1).astype('float32')
            faiss.normalize_L2(user_embedding)
            
            # Search for similar users
            scores, indices = self.faiss_index.search(user_embedding, limit)
            
            # Get user objects
            candidate_users = []
            for idx in indices[0]:
                if idx in self.user_id_mapping:
                    user_id = self.user_id_mapping[idx]
                    try:
                        candidate_user = User.objects.get(id=user_id)
                        candidate_users.append(candidate_user)
                    except User.DoesNotExist:
                        continue
            
            return candidate_users
            
        except Exception as e:
            logger.error(f"Error in FAISS similarity search: {e}")
            return self._traditional_similarity_search(user, limit)
    
    def _traditional_similarity_search(self, user, limit):
        """Traditional similarity search as fallback"""
        try:
            # Get all other users with profiles
            other_users = User.objects.exclude(id=user.id).filter(
                creatorprofile__isnull=False
            )[:limit * 3]  # Get more candidates for better selection
            
            return list(other_users)
            
        except Exception as e:
            logger.error(f"Error in traditional similarity search: {e}")
            return []
    
    def _calculate_final_score(self, user1, user2, ml_score):
        """Calculate final match score combining ML and other factors"""
        try:
            # Start with ML score
            final_score = ml_score
            
            # Apply recency boost for active users
            if hasattr(user2, 'last_login') and user2.last_login:
                from django.utils import timezone
                days_since_login = (timezone.now() - user2.last_login).days
                recency_boost = max(0, 1 - (days_since_login / 30))  # Boost for recent activity
                final_score += recency_boost * 0.1
            
            # Apply popularity boost (number of connections)
            connection_count = getattr(user2, 'connection_count', 0)
            popularity_boost = min(connection_count / 100, 0.1)  # Cap at 0.1
            final_score += popularity_boost
            
            # Ensure score is between 0 and 1
            final_score = max(0, min(1, final_score))
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating final score: {e}")
            return ml_score
    
    def _apply_filters(self, matches, filters):
        """Apply filters to match results"""
        filtered_matches = matches
        
        try:
            # Location filter
            if filters.get('location'):
                filtered_matches = [
                    match for match in filtered_matches
                    if hasattr(match['user'], 'creatorprofile') and
                    getattr(match['user'].creatorprofile, 'location', '').lower() == filters['location'].lower()
                ]
            
            # Skills filter
            if filters.get('skills'):
                required_skills = [skill.lower() for skill in filters['skills']]
                filtered_matches = [
                    match for match in filtered_matches
                    if hasattr(match['user'], 'creatorprofile') and
                    any(skill.lower() in str(getattr(match['user'].creatorprofile, 'skills', '')).lower()
                        for skill in required_skills)
                ]
            
            # Experience level filter
            if filters.get('experience_level'):
                filtered_matches = [
                    match for match in filtered_matches
                    if hasattr(match['user'], 'creatorprofile') and
                    getattr(match['user'].creatorprofile, 'experience_level', '') == filters['experience_level']
                ]
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
        
        return filtered_matches
    
    def learn_from_feedback(self, user, matched_user, feedback_score, interaction_type='view'):
        """Learn from user feedback to improve future matches"""
        try:
            # Store feedback for model retraining
            feedback_data = {
                'user_id': user.id,
                'matched_user_id': matched_user.id,
                'feedback_score': feedback_score,
                'interaction_type': interaction_type,
                'timestamp': timezone.now().isoformat()
            }
            
            # Store in cache for batch processing
            feedback_key = f"match_feedback:{user.id}"
            existing_feedback = cache.get(feedback_key, [])
            existing_feedback.append(feedback_data)
            cache.set(feedback_key, existing_feedback, 86400)  # 24 hours
            
            # Track analytics
            AnalyticsCollector.track_event(
                'match_feedback',
                user=user,
                event_data=feedback_data
            )
            
            # Trigger model retraining if enough feedback accumulated
            if len(existing_feedback) >= 100:  # Retrain after 100 feedback points
                self._retrain_model_async()
            
            logger.info(f"Recorded feedback for user {user.id} -> {matched_user.id}: {feedback_score}")
            
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
    
    def _retrain_model_async(self):
        """Trigger asynchronous model retraining"""
        try:
            # In a real implementation, this would use Celery or similar
            # For now, we'll just log the intent
            logger.info("Model retraining triggered - would run in background task")
            
            # Clear the model cache to force reloading
            cache.delete("sentence_transformer_model")
            
        except Exception as e:
            logger.error(f"Error triggering model retraining: {e}")


# Global instance
advanced_matching_engine = AdvancedMatchingEngine()
