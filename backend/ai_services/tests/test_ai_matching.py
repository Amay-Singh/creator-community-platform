"""
Comprehensive tests for P5-001 AI-Powered Creator Matching Backend Service
Tests models, services, and API endpoints for AI matching functionality
"""
import json
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime, timedelta

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import CreatorProfile
from ai_services.models import (
    CreatorEmbedding, MatchResult, MatchFeedback, MatchHistory
)
from ai_services.matching_service import matching_service

User = get_user_model()


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
)
class AIMatchingModelsTestCase(TestCase):
    """Test AI matching models"""
    
    def setUp(self):
        # Create test users and profiles
        self.user1 = User.objects.create_user(
            username='creator1',
            email='creator1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='creator2',
            email='creator2@test.com',
            password='testpass123'
        )
        
        self.profile1 = CreatorProfile.objects.create(
            user=self.user1,
            display_name='Creator One',
            bio='Music producer and songwriter',
            location='Los Angeles, CA'
        )
        self.profile2 = CreatorProfile.objects.create(
            user=self.user2,
            display_name='Creator Two',
            bio='Video editor and motion graphics artist',
            location='New York, NY'
        )
    
    def test_creator_embedding_model(self):
        """Test CreatorEmbedding model creation and properties"""
        embedding = CreatorEmbedding.objects.create(
            creator=self.profile1,
            embedding_vector=[0.1, 0.2, 0.3, 0.4, 0.5],
            embedding_version='v1.0',
            skills_hash='abc123',
            bio_hash='def456',
            interests_hash='ghi789'
        )
        
        self.assertEqual(str(embedding), f"Embedding for {self.profile1.display_name}")
        self.assertTrue(embedding.needs_update)  # No last_profile_update set
        
        # Set last_profile_update to current time
        embedding.last_profile_update = timezone.now()
        embedding.save()
        self.assertFalse(embedding.needs_update)
    
    def test_match_result_model(self):
        """Test MatchResult model creation"""
        match = MatchResult.objects.create(
            requester=self.profile1,
            matched_creator=self.profile2,
            similarity_score=0.85,
            compatibility_score=78.5,
            match_reasons=['High profile similarity', 'Complementary skills'],
            shared_skills=['music', 'creativity'],
            complementary_skills=['production ↔ editing'],
            match_type='collaboration',
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        expected_str = f"Match: {self.profile1.display_name} → {self.profile2.display_name} (78.5%)"
        self.assertEqual(str(match), expected_str)
        self.assertEqual(match.status, 'pending')
        self.assertIsNotNone(match.created_at)
    
    def test_match_feedback_model(self):
        """Test MatchFeedback model creation"""
        match = MatchResult.objects.create(
            requester=self.profile1,
            matched_creator=self.profile2,
            similarity_score=0.75,
            compatibility_score=65.0
        )
        
        feedback = MatchFeedback.objects.create(
            match_result=match,
            user=self.profile1,
            rating=4,
            feedback_type='quality',
            comment='Great match, very relevant',
            contacted_match=True,
            collaboration_started=False,
            would_recommend=True
        )
        
        self.assertEqual(str(feedback), f"Feedback: {match} - 4/5")
        self.assertEqual(feedback.rating, 4)
        self.assertTrue(feedback.contacted_match)
    
    def test_match_history_model(self):
        """Test MatchHistory model creation"""
        history = MatchHistory.objects.create(
            user=self.profile1,
            request_type='find_matches',
            filters_used={'location': 'Los Angeles'},
            results_count=5,
            processing_time_ms=250,
            embedding_version='v1.0',
            top_similarity_score=0.89,
            average_compatibility=72.4
        )
        
        expected_str = f"Match History: {self.profile1.display_name} - find_matches (5 results)"
        self.assertEqual(str(history), expected_str)
        self.assertEqual(history.processing_time_ms, 250)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
)
class AIMatchingServiceTestCase(TestCase):
    """Test AI matching service functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testpass123'
        )
        self.profile = CreatorProfile.objects.create(
            user=self.user,
            display_name='Test Creator',
            bio='A creative professional with diverse skills',
            location='San Francisco, CA'
        )
    
    def test_extract_profile_text(self):
        """Test profile text extraction for embedding generation"""
        profile_text = matching_service._extract_profile_text(self.profile)
        
        self.assertIn('Bio: A creative professional', profile_text)
        self.assertIn('Location: San Francisco, CA', profile_text)
    
    def test_cosine_similarity_calculation(self):
        """Test cosine similarity calculation"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        vec3 = [1.0, 0.0, 0.0]
        
        # Orthogonal vectors should have similarity 0
        similarity1 = matching_service._cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity1, 0.0, places=5)
        
        # Identical vectors should have similarity 1
        similarity2 = matching_service._cosine_similarity(vec1, vec3)
        self.assertAlmostEqual(similarity2, 1.0, places=5)
    
    def test_compatibility_score_calculation(self):
        """Test compatibility score calculation"""
        similarity = 0.8
        shared_skills = ['music', 'video']
        complementary_skills = ['production ↔ editing']
        
        score = matching_service._calculate_compatibility_score(
            similarity, shared_skills, complementary_skills
        )
        
        # Base score (0.8 * 60) + shared bonus (2 * 3) + complementary bonus (1 * 2)
        expected_score = 48.0 + 6.0 + 2.0  # = 56.0
        self.assertEqual(score, expected_score)
    
    def test_skills_compatibility_analysis(self):
        """Test skills compatibility analysis"""
        # Create profiles with specific skills
        profile1 = CreatorProfile.objects.create(
            user=User.objects.create_user(username='user1', email='user1@test.com', password='pass'),
            display_name='Producer',
            bio='Music producer'
        )
        profile2 = CreatorProfile.objects.create(
            user=User.objects.create_user(username='user2', email='user2@test.com', password='pass'),
            display_name='Vocalist',
            bio='Singer and songwriter'
        )
        
        # Mock skills attributes
        profile1.skills = ['music_production', 'mixing']
        profile2.skills = ['vocals', 'songwriting']
        
        shared, complementary = matching_service._analyze_skills_compatibility(profile1, profile2)
        
        self.assertEqual(shared, [])  # No shared skills
        self.assertIn('music_production ↔ vocals', complementary)
    
    @patch('ai_services.matching_service.matching_service._get_openai_client')
    def test_embedding_generation_mock(self, mock_client):
        """Test embedding generation with mocked OpenAI client"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        mock_client.return_value.embeddings.create.return_value = mock_response
        
        embedding = matching_service.generate_embedding(self.profile)
        
        self.assertIsNotNone(embedding)
        self.assertEqual(len(embedding), 5)
        self.assertEqual(embedding[0], 0.1)
    
    def test_match_reasons_generation(self):
        """Test match reasons generation"""
        reasons = matching_service._generate_match_reasons(
            self.profile, self.profile,  # Same profile for testing
            similarity=0.9,
            shared_skills=['music', 'video'],
            complementary_skills=['production ↔ editing']
        )
        
        self.assertIn('Very high profile similarity', reasons)
        self.assertTrue(any('Shared skills' in reason for reason in reasons))
        self.assertTrue(any('Complementary skills' in reason for reason in reasons))


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
)
class AIMatchingAPITestCase(APITestCase):
    """Test AI matching API endpoints"""
    
    def setUp(self):
        # Create test users and profiles
        self.user1 = User.objects.create_user(
            username='creator1',
            email='creator1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='creator2',
            email='creator2@test.com',
            password='testpass123'
        )
        
        self.profile1 = CreatorProfile.objects.create(
            user=self.user1,
            display_name='Creator One',
            bio='Music producer and songwriter',
            location='Los Angeles, CA'
        )
        self.profile2 = CreatorProfile.objects.create(
            user=self.user2,
            display_name='Creator Two',
            bio='Video editor and motion graphics artist',
            location='New York, NY'
        )
        
        # Establish the reverse relationship for user.creatorprofile
        self.user1.creatorprofile = self.profile1
        self.user2.creatorprofile = self.profile2
        
        # Create embedding for profile1
        self.embedding1 = CreatorEmbedding.objects.create(
            creator=self.profile1,
            embedding_vector=[0.1, 0.2, 0.3, 0.4, 0.5],
            embedding_version='v1.0'
        )
    
    def test_creator_embedding_list_authenticated(self):
        """Test creator embedding list endpoint with authentication"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('ai_services:embeddings-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['creator_name'], 'Creator One')
    
    def test_creator_embedding_list_unauthenticated(self):
        """Test creator embedding list endpoint without authentication"""
        url = reverse('ai_services:embeddings-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('ai_services.matching_service.matching_service.update_creator_embedding')
    def test_update_embedding_endpoint(self, mock_update):
        """Test embedding update endpoint"""
        mock_update.return_value = True
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('ai_services:embeddings-update-embedding')
        response = self.client.post(url, {'force_update': True})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        mock_update.assert_called_once()
    
    def test_match_results_list(self):
        """Test match results list endpoint"""
        # Create a match result
        match = MatchResult.objects.create(
            requester=self.profile1,
            matched_creator=self.profile2,
            similarity_score=0.85,
            compatibility_score=78.5
        )
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('ai_services:matches-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['compatibility_score'], 78.5)
    
    @patch('ai_services.matching_service.matching_service.find_matches')
    def test_find_matches_endpoint(self, mock_find_matches):
        """Test find matches endpoint"""
        # Mock the find_matches method
        mock_match = MatchResult(
            requester=self.profile1,
            matched_creator=self.profile2,
            similarity_score=0.85,
            compatibility_score=78.5,
            match_reasons=['High similarity'],
            shared_skills=['music'],
            complementary_skills=[]
        )
        mock_find_matches.return_value = [mock_match]
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('ai_services:matches-find-matches')
        data = {
            'limit': 5,
            'location': 'Los Angeles'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIn('matches', response.data)
        mock_find_matches.assert_called_once()
    
    def test_match_feedback_creation(self):
        """Test match feedback creation"""
        # Create a match result
        match = MatchResult.objects.create(
            requester=self.profile1,
            matched_creator=self.profile2,
            similarity_score=0.85,
            compatibility_score=78.5
        )
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('ai_services:match-feedback-list')
        data = {
            'match_result': match.id,  # Use integer ID instead of string
            'rating': 4,
            'feedback_type': 'quality',
            'comment': 'Great match!',
            'contacted_match': True
        }
        response = self.client.post(url, data, format='json')
        
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 4)
        
        # Verify feedback was created
        feedback = MatchFeedback.objects.get(match_result=match, user=self.profile1)
        self.assertEqual(feedback.rating, 4)
        self.assertEqual(feedback.comment, 'Great match!')
    
    def test_match_statistics_endpoint(self):
        """Test match statistics endpoint"""
        # Create some test data
        MatchResult.objects.create(
            requester=self.profile1,
            matched_creator=self.profile2,
            similarity_score=0.85,
            compatibility_score=78.5,
            status='viewed'
        )
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('ai_services:match_statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_matches', response.data)
        self.assertIn('matches_viewed', response.data)
        self.assertEqual(response.data['total_matches'], 1)
    
    def test_batch_match_endpoint(self):
        """Test batch matching endpoint"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('ai_services:batch_match')
        data = {
            'creator_ids': [self.profile1.id, self.profile2.id],
            'limit_per_creator': 3
        }
        
        with patch('ai_services.matching_service.matching_service.find_matches') as mock_find:
            mock_find.return_value = []
            response = self.client.post(url, data, format='json')
            
            if response.status_code != status.HTTP_200_OK:
                print(f"Batch match error: {response.data}")
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('results', response.data)
            self.assertEqual(response.data['total_creators'], 2)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
)
class AIMatchingIntegrationTestCase(TestCase):
    """Integration tests for AI matching system"""
    
    def setUp(self):
        # Create multiple test users and profiles
        self.users = []
        self.profiles = []
        
        for i in range(3):
            user = User.objects.create_user(
                username=f'creator{i}',
                email=f'creator{i}@test.com',
                password='testpass123'
            )
            profile = CreatorProfile.objects.create(
                user=user,
                display_name=f'Creator {i}',
                bio=f'Creative professional {i}',
                location='Test City'
            )
            self.users.append(user)
            self.profiles.append(profile)
    
    def test_full_matching_workflow(self):
        """Test complete matching workflow from embedding to feedback"""
        # Step 1: Create embeddings for all profiles
        for i, profile in enumerate(self.profiles):
            CreatorEmbedding.objects.create(
                creator=profile,
                embedding_vector=[0.1 * (i + 1), 0.2 * (i + 1), 0.3 * (i + 1)],
                embedding_version='v1.0'
            )
        
        # Step 2: Create match results
        match = MatchResult.objects.create(
            requester=self.profiles[0],
            matched_creator=self.profiles[1],
            similarity_score=0.85,
            compatibility_score=78.5,
            match_reasons=['High similarity', 'Complementary skills'],
            shared_skills=['creativity'],
            complementary_skills=['music ↔ video']
        )
        
        # Step 3: User views the match
        match.status = 'viewed'
        match.viewed_at = timezone.now()
        match.save()
        
        # Step 4: User provides feedback
        feedback = MatchFeedback.objects.create(
            match_result=match,
            user=self.profiles[0],
            rating=4,
            feedback_type='quality',
            comment='Excellent match, led to collaboration',
            contacted_match=True,
            collaboration_started=True
        )
        
        # Step 5: Record match history
        history = MatchHistory.objects.create(
            user=self.profiles[0],
            request_type='find_matches',
            results_count=1,
            processing_time_ms=150,
            top_similarity_score=0.85,
            average_compatibility=78.5
        )
        
        # Verify the complete workflow
        self.assertEqual(match.status, 'viewed')
        self.assertIsNotNone(match.viewed_at)
        self.assertEqual(feedback.rating, 4)
        self.assertTrue(feedback.collaboration_started)
        self.assertEqual(history.results_count, 1)
        
        # Test statistics calculation
        stats = matching_service.get_match_statistics(self.profiles[0])
        self.assertEqual(stats['total_matches'], 1)
        self.assertEqual(stats['matches_viewed'], 1)
        self.assertEqual(stats['feedback_given'], 1)
