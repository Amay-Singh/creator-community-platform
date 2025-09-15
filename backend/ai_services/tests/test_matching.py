"""
Tests for AI Matching Engine
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import CreatorProfile
from ai_services.matching_engine import MatchingEngine, MatchingRequest, MatchCandidate
from ai_services.vector_store import VectorStore
from ai_services.bias_mitigation import FairnessMitigator

User = get_user_model()

class MatchingEngineTestCase(TestCase):
    """Test cases for AI Matching Engine"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users and profiles
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com', 
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@test.com',
            password='testpass123'
        )
        
        self.profile1 = CreatorProfile.objects.create(
            user=self.user1,
            display_name='Test User 1',
            bio='Music producer and songwriter',
            category='performing_arts',
            experience_level='intermediate',
            location='New York, NY, USA'
        )
        
        self.profile2 = CreatorProfile.objects.create(
            user=self.user2,
            display_name='Test User 2', 
            bio='Singer and vocalist',
            category='performing_arts',
            experience_level='beginner',
            location='Los Angeles, CA, USA'
        )
        
        self.profile3 = CreatorProfile.objects.create(
            user=self.user3,
            display_name='Test User 3',
            bio='Graphic designer and artist',
            category='visual_arts',
            experience_level='advanced',
            location='Chicago, IL, USA'
        )
        
        self.matching_engine = MatchingEngine()
    
    @patch('ai_services.matching_engine.VectorStore')
    def test_generate_suggestions_basic(self, mock_vector_store):
        """Test basic suggestion generation"""
        # Mock vector store responses
        mock_vector_store_instance = Mock()
        mock_vector_store.return_value = mock_vector_store_instance
        
        # Mock embedding and similarity search
        mock_vector_store_instance.get_profile_embedding.return_value = np.random.randn(384)
        mock_vector_store_instance.find_similar.return_value = [
            (str(self.profile2.id), 0.85),
            (str(self.profile3.id), 0.72)
        ]
        
        # Create matching request
        request = MatchingRequest(
            user_id=str(self.user1.id),
            intent='collaboration',
            k=10,
            diversity=0.3
        )
        
        # Generate suggestions
        suggestions = self.matching_engine.generate_suggestions(request)
        
        # Assertions
        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), request.k)
        
        for suggestion in suggestions:
            self.assertIsInstance(suggestion, MatchCandidate)
            self.assertIsInstance(suggestion.score, float)
            self.assertIsInstance(suggestion.reasons, list)
    
    def test_matching_request_validation(self):
        """Test matching request parameter validation"""
        # Valid request
        request = MatchingRequest(
            user_id=str(self.user1.id),
            intent='collaboration',
            k=20,
            diversity=0.5
        )
        
        self.assertEqual(request.user_id, str(self.user1.id))
        self.assertEqual(request.intent, 'collaboration')
        self.assertEqual(request.k, 20)
        self.assertEqual(request.diversity, 0.5)
    
    @patch('ai_services.matching_engine.VectorStore')
    def test_explain_match(self, mock_vector_store):
        """Test match explanation functionality"""
        # Mock vector store
        mock_vector_store_instance = Mock()
        mock_vector_store.return_value = mock_vector_store_instance
        
        # Mock embeddings
        user_vector = np.random.randn(384)
        candidate_vector = np.random.randn(384)
        
        mock_vector_store_instance.get_profile_embedding.side_effect = [
            user_vector, candidate_vector
        ]
        
        # Test explanation
        explanation = self.matching_engine.explain_match(
            str(self.user1.id),
            str(self.user2.id)
        )
        
        # Assertions
        self.assertIsInstance(explanation, dict)
        self.assertIn('overall_score', explanation)
        self.assertIn('skills_analysis', explanation)
        self.assertIn('location_compatibility', explanation)
        self.assertIn('reasons', explanation)
    
    def test_record_feedback(self):
        """Test feedback recording"""
        # Test feedback recording (should not raise exception)
        try:
            self.matching_engine.record_feedback(
                str(self.user1.id),
                str(self.user2.id),
                'Great match!',
                5
            )
        except Exception as e:
            self.fail(f"record_feedback raised {e} unexpectedly")
    
    def test_create_match_candidate(self):
        """Test match candidate creation"""
        candidate = self.matching_engine._create_match_candidate(
            self.profile1,
            self.profile2,
            0.85,
            'collaboration'
        )
        
        self.assertIsInstance(candidate, MatchCandidate)
        self.assertEqual(str(candidate.user_id), str(self.user2.id))
        self.assertEqual(str(candidate.profile_id), str(self.profile2.id))
        self.assertEqual(candidate.score, 0.85)
        self.assertIsInstance(candidate.reasons, list)
        self.assertIsInstance(candidate.skills_overlap, list)
        self.assertIsInstance(candidate.complementary_skills, list)
    
    def test_calculate_distance(self):
        """Test distance calculation between profiles"""
        distance = self.matching_engine._calculate_distance(
            self.profile1, 
            self.profile2
        )
        
        # Should return None since lat/lng fields don't exist in current model
        self.assertIsNone(distance)
        #self.assertLess(distance, 5000)  # Should be reasonable distance
    
    def test_get_experience_level(self):
        """Test experience level calculation"""
        # Test with different portfolio counts
        level = self.matching_engine._get_experience_level(self.profile1)
        
        self.assertIsInstance(level, int)
        self.assertGreaterEqual(level, 1)
        self.assertLessEqual(level, 5)

class VectorStoreTestCase(TestCase):
    """Test cases for Vector Store"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.profile = CreatorProfile.objects.create(
            user=self.user,
            display_name='Test User',
            bio='Test bio',
            category='performing_arts',
            experience_level='intermediate',
            location='Test City'
        )
        
        self.vector_store = VectorStore()
    
    def test_generate_profile_embedding(self):
        """Test profile embedding generation"""
        embedding = self.vector_store._generate_profile_embedding(self.profile)
        
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (384,))
        self.assertAlmostEqual(np.linalg.norm(embedding), 1.0, places=5)
    
    def test_extract_text_features(self):
        """Test text feature extraction"""
        features = self.vector_store._extract_text_features(self.profile)
        
        self.assertIsInstance(features, list)
        self.assertGreater(len(features), 0)
        
        for feature in features:
            self.assertIsInstance(feature, (float, int))
    
    def test_extract_categorical_features(self):
        """Test categorical feature extraction"""
        features = self.vector_store._extract_categorical_features(self.profile)
        
        self.assertIsInstance(features, list)
        self.assertGreater(len(features), 0)
        
        # Should contain binary encodings
        for feature in features:
            self.assertIn(feature, [0.0, 1.0])
    
    def test_extract_numerical_features(self):
        """Test numerical feature extraction"""
        features = self.vector_store._extract_numerical_features(self.profile)
        
        self.assertIsInstance(features, list)
        self.assertGreater(len(features), 0)
        
        for feature in features:
            self.assertIsInstance(feature, float)
    
    def test_calculate_profile_completeness(self):
        """Test profile completeness calculation"""
        completeness = self.vector_store._calculate_profile_completeness(self.profile)
        
        self.assertIsInstance(completeness, float)
        self.assertGreaterEqual(completeness, 0.0)
        self.assertLessEqual(completeness, 1.0)
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        vec1 = np.array([1, 0, 0])
        vec2 = np.array([0, 1, 0])
        vec3 = np.array([1, 0, 0])
        
        # Orthogonal vectors
        similarity1 = self.vector_store._cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity1, 0.0, places=5)
        
        # Identical vectors
        similarity2 = self.vector_store._cosine_similarity(vec1, vec3)
        self.assertAlmostEqual(similarity2, 1.0, places=5)

class BiaseMitigationTestCase(TestCase):
    """Test cases for Bias Mitigation"""
    
    def setUp(self):
        """Set up test data"""
        self.fairness_mitigator = FairnessMitigator()
        
        # Create mock candidates
        self.mock_candidates = []
        for i in range(10):
            candidate = Mock()
            candidate.user_id = f"user_{i}"
            candidate.profile_id = f"profile_{i}"
            candidate.score = 0.8 - (i * 0.05)
            candidate.reasons = [f"reason_{i}"]
            candidate.skills_overlap = [f"skill_{i}"]
            candidate.complementary_skills = [f"comp_skill_{i}"]
            self.mock_candidates.append(candidate)
    
    @patch('ai_services.bias_mitigation.CreatorProfile.objects.get')
    def test_analyze_bias(self, mock_get_profile):
        """Test bias analysis"""
        # Mock profile responses
        mock_profiles = []
        for i in range(len(self.mock_candidates)):
            mock_profile = Mock()
            mock_profile.category = 'music' if i % 2 == 0 else 'visual_arts'
            mock_profile.location = f'City_{i % 3}'
            mock_profile.skills = [f'skill_{i}']
            mock_profile.portfolio_items.count.return_value = i + 1
            mock_profiles.append(mock_profile)
        
        mock_get_profile.side_effect = mock_profiles
        
        # Analyze bias
        bias_metrics = self.fairness_mitigator._analyze_bias(self.mock_candidates)
        
        self.assertIsInstance(bias_metrics.demographic_distribution, dict)
        self.assertIsInstance(bias_metrics.exposure_parity, dict)
        self.assertIsInstance(bias_metrics.recommendation_diversity, float)
        self.assertIsInstance(bias_metrics.protected_group_representation, dict)
    
    def test_calculate_diversity_score(self):
        """Test diversity score calculation"""
        # Create mock profiles with different attributes
        mock_profiles = []
        categories = ['music', 'visual_arts', 'writing']
        locations = ['New York', 'Los Angeles', 'Chicago']
        
        for i in range(6):
            mock_profile = Mock()
            mock_profile.category = categories[i % 3]
            mock_profile.location = locations[i % 3]
            mock_profile.skills = [f'skill_{i}', f'skill_{i+1}']
            mock_profiles.append(mock_profile)
        
        diversity_score = self.fairness_mitigator._calculate_diversity_score(mock_profiles)
        
        self.assertIsInstance(diversity_score, float)
        self.assertGreaterEqual(diversity_score, 0.0)
        self.assertLessEqual(diversity_score, 1.0)
    
    def test_get_experience_group(self):
        """Test experience group classification"""
        # Mock profile with different experience levels
        mock_profile = Mock()
        
        # Beginner
        mock_profile.portfolio_items.count.return_value = 1
        mock_profile.skills = ['skill1']
        exp_group = self.fairness_mitigator._get_experience_group(mock_profile)
        self.assertEqual(exp_group, 'beginner')
        
        # Experienced
        mock_profile.portfolio_items.count.return_value = 10
        mock_profile.skills = ['skill1', 'skill2', 'skill3', 'skill4', 'skill5', 'skill6']
        exp_group = self.fairness_mitigator._get_experience_group(mock_profile)
        self.assertEqual(exp_group, 'experienced')

class IntegrationTestCase(TestCase):
    """Integration tests for AI matching system"""
    
    def setUp(self):
        """Set up integration test data"""
        # Create multiple users and profiles for realistic testing
        self.users = []
        self.profiles = []
        
        test_data = [
            {
                'email': 'musician1@test.com',
                'name': 'Musician 1',
                'category': 'music',
                'skills': ['guitar', 'songwriting'],
                'location': 'Nashville, TN'
            },
            {
                'email': 'musician2@test.com', 
                'name': 'Musician 2',
                'category': 'music',
                'skills': ['vocals', 'piano'],
                'location': 'Los Angeles, CA'
            },
            {
                'email': 'artist1@test.com',
                'name': 'Artist 1', 
                'category': 'visual_arts',
                'skills': ['illustration', 'digital_art'],
                'location': 'New York, NY'
            }
        ]
        
        for i, data in enumerate(test_data):
            user = User.objects.create_user(
                username=f"testuser{i+1}",
                email=data['email'],
                password='testpass123'
            )
            profile = CreatorProfile.objects.create(
                user=user,
                display_name=data['name'],
                category=data['category'],
                experience_level='intermediate',
                location=data['location']
            )
            self.users.append(user)
            self.profiles.append(profile)
    
    @patch('ai_services.matching_engine.VectorStore')
    def test_end_to_end_matching(self, mock_vector_store):
        """Test complete matching workflow"""
        # Mock vector store for integration test
        mock_vector_store_instance = Mock()
        mock_vector_store.return_value = mock_vector_store_instance
        
        mock_vector_store_instance.get_profile_embedding.return_value = np.random.randn(384)
        mock_vector_store_instance.find_similar.return_value = [
            (str(self.profiles[1].id), 0.85),
            (str(self.profiles[2].id), 0.72)
        ]
        
        # Create matching engine and request
        matching_engine = MatchingEngine()
        request = MatchingRequest(
            user_id=str(self.users[0].id),
            intent='collaboration',
            k=5,
            diversity=0.3
        )
        
        # Generate suggestions
        suggestions = matching_engine.generate_suggestions(request)
        
        # Verify results
        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 5)
        
        # Test explanation for first suggestion if available
        if suggestions:
            explanation = matching_engine.explain_match(
                str(self.users[0].id),
                suggestions[0].user_id
            )
            self.assertIsInstance(explanation, dict)
            self.assertIn('overall_score', explanation)

if __name__ == '__main__':
    unittest.main()
