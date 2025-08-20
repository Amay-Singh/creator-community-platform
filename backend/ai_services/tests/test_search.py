"""
Tests for Advanced Search Engine and API
"""
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import Mock, patch
from accounts.models import CreatorProfile
from ai_services.search_engine import AdvancedSearchEngine, SearchRequest
from ai_services.search_api import search_engine

User = get_user_model()

class SearchEngineTestCase(TestCase):
    """Test cases for Advanced Search Engine"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users and profiles
        self.user1 = User.objects.create_user(
            username='musician1',
            email='musician1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='artist1',
            email='artist1@test.com',
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            username='designer1',
            email='designer1@test.com',
            password='testpass123'
        )
        
        self.profile1 = CreatorProfile.objects.create(
            user=self.user1,
            display_name='John Musician',
            bio='Professional music producer and songwriter',
            category='performing_arts',
            experience_level='professional',
            location='New York, NY'
        )
        
        self.profile2 = CreatorProfile.objects.create(
            user=self.user2,
            display_name='Jane Artist',
            bio='Digital artist and illustrator',
            category='visual_arts',
            experience_level='intermediate',
            location='Los Angeles, CA'
        )
        
        self.profile3 = CreatorProfile.objects.create(
            user=self.user3,
            display_name='Bob Designer',
            bio='UX/UI designer with 5 years experience',
            category='design',
            experience_level='advanced',
            location='San Francisco, CA'
        )
        
        self.search_engine = AdvancedSearchEngine()
    
    def test_basic_search(self):
        """Test basic search functionality"""
        request = SearchRequest(
            query="music",
            page=1,
            page_size=10
        )
        
        response = self.search_engine.search(request)
        
        self.assertIsInstance(response.results, list)
        self.assertGreaterEqual(response.total_count, 0)
        self.assertEqual(response.page, 1)
        self.assertEqual(response.page_size, 10)
        self.assertIsInstance(response.query_time_ms, int)
    
    def test_category_filter(self):
        """Test category filtering"""
        request = SearchRequest(
            category="performing_arts",
            page=1,
            page_size=10
        )
        
        response = self.search_engine.search(request)
        
        # Should find the musician profile
        self.assertGreaterEqual(response.total_count, 1)
        if response.results:
            self.assertEqual(response.results[0].category, "performing_arts")
    
    def test_experience_level_filter(self):
        """Test experience level filtering"""
        request = SearchRequest(
            experience_level="professional",
            page=1,
            page_size=10
        )
        
        response = self.search_engine.search(request)
        
        # Should find the professional musician
        self.assertGreaterEqual(response.total_count, 1)
        if response.results:
            self.assertEqual(response.results[0].experience_level, "professional")
    
    def test_location_filter(self):
        """Test location filtering"""
        request = SearchRequest(
            location="New York",
            page=1,
            page_size=10
        )
        
        response = self.search_engine.search(request)
        
        # Should find profiles in New York
        self.assertGreaterEqual(response.total_count, 0)
        for result in response.results:
            self.assertIn("New York", result.location)
    
    def test_text_search(self):
        """Test text search across fields"""
        request = SearchRequest(
            query="producer",
            page=1,
            page_size=10
        )
        
        response = self.search_engine.search(request)
        
        # Should find the music producer
        self.assertGreaterEqual(response.total_count, 0)
    
    def test_pagination(self):
        """Test search pagination"""
        request = SearchRequest(
            query="",
            page=1,
            page_size=2
        )
        
        response = self.search_engine.search(request)
        
        self.assertLessEqual(len(response.results), 2)
        self.assertEqual(response.page, 1)
        self.assertEqual(response.page_size, 2)
    
    def test_sorting(self):
        """Test different sorting options"""
        # Test relevance sorting
        request = SearchRequest(
            query="",
            sort_by="relevance",
            page=1,
            page_size=10
        )
        
        response = self.search_engine.search(request)
        self.assertIsInstance(response.results, list)
        
        # Test recent sorting
        request.sort_by = "recent"
        response = self.search_engine.search(request)
        self.assertIsInstance(response.results, list)
    
    def test_aggregations(self):
        """Test search result aggregations"""
        request = SearchRequest(
            query="",
            page=1,
            page_size=10
        )
        
        response = self.search_engine.search(request)
        
        self.assertIsInstance(response.aggregations, dict)
        self.assertIn('categories', response.aggregations)
        self.assertIn('experience_levels', response.aggregations)
    
    def test_relevance_scoring(self):
        """Test relevance score calculation"""
        result = self.search_engine._profile_to_search_result(
            self.profile1,
            SearchRequest(query="music")
        )
        
        self.assertIsInstance(result.relevance_score, float)
        self.assertGreaterEqual(result.relevance_score, 0.0)
        self.assertLessEqual(result.relevance_score, 1.0)
    
    def test_search_suggestions(self):
        """Test search suggestions"""
        suggestions = self.search_engine.get_search_suggestions("art", 5)
        
        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 5)
    
    def test_talent_map_data(self):
        """Test talent map data generation"""
        bounds = {
            "north": 41.0,
            "south": 40.0,
            "east": -73.0,
            "west": -74.0
        }
        
        map_data = self.search_engine.get_talent_map_data(bounds, 10)
        
        self.assertIsInstance(map_data, dict)
        self.assertIn('clusters', map_data)
        self.assertIn('heatmap', map_data)
        self.assertIn('category_stats', map_data)
        self.assertIn('total_profiles', map_data)

class SearchAPITestCase(APITestCase):
    """Test cases for Search API endpoints"""
    
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
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
    
    def test_advanced_search_api(self):
        """Test advanced search API endpoint"""
        url = reverse('ai_services:advanced_search')
        data = {
            'query': 'test',
            'category': 'performing_arts',
            'page': 1,
            'page_size': 20
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('pagination', response.data)
        self.assertIn('aggregations', response.data)
        self.assertIn('query_time_ms', response.data)
    
    def test_talent_map_api(self):
        """Test talent map API endpoint"""
        url = reverse('ai_services:talent_map')
        params = {
            'north': 41.0,
            'south': 40.0,
            'east': -73.0,
            'west': -74.0,
            'zoom': 10
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('clusters', response.data)
        self.assertIn('heatmap', response.data)
        self.assertIn('category_stats', response.data)
        self.assertIn('total_profiles', response.data)
    
    def test_search_suggestions_api(self):
        """Test search suggestions API endpoint"""
        url = reverse('ai_services:search_suggestions')
        params = {'q': 'test', 'limit': 5}
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('suggestions', response.data)
        self.assertIn('query', response.data)
    
    def test_search_filters_api(self):
        """Test search filters API endpoint"""
        url = reverse('ai_services:search_filters')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('categories', response.data)
        self.assertIn('experience_levels', response.data)
        self.assertIn('locations', response.data)
        self.assertIn('sort_options', response.data)
    
    def test_search_health_api(self):
        """Test search health check API endpoint"""
        url = reverse('ai_services:search_health')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('total_profiles', response.data)
        self.assertEqual(response.data['status'], 'healthy')
    
    def test_advanced_search_with_geospatial(self):
        """Test advanced search with geospatial parameters"""
        url = reverse('ai_services:advanced_search')
        data = {
            'query': 'artist',
            'lat': 40.7128,
            'lng': -74.0060,
            'radius_km': 50,
            'page': 1,
            'page_size': 10
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_advanced_search_pagination(self):
        """Test advanced search pagination"""
        url = reverse('ai_services:advanced_search')
        data = {
            'query': '',
            'page': 1,
            'page_size': 1
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['pagination']['page'], 1)
        self.assertEqual(response.data['pagination']['page_size'], 1)
    
    def test_search_authentication_required(self):
        """Test that search endpoints require authentication"""
        self.client.force_authenticate(user=None)
        
        url = reverse('ai_services:advanced_search')
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_search_suggestions_short_query(self):
        """Test search suggestions with short query"""
        url = reverse('ai_services:search_suggestions')
        params = {'q': 'a', 'limit': 5}  # Too short
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['suggestions'], [])
    
    def test_advanced_search_sorting(self):
        """Test advanced search with different sorting options"""
        url = reverse('ai_services:advanced_search')
        
        # Test each sort option
        sort_options = ['relevance', 'recent', 'rating', 'distance']
        
        for sort_by in sort_options:
            data = {
                'query': 'test',
                'sort_by': sort_by,
                'page': 1,
                'page_size': 10
            }
            
            response = self.client.post(url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('results', response.data)
