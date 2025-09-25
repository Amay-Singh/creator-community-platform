"""
AI-powered Recommendation Engine
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
from datetime import timedelta
from .models import CreatorProfile, MatchingResult, SearchQuery
from collaborations.models import NewCollaborationInvite
from notifications.models import Notification
from analytics.services import AnalyticsCollector

User = get_user_model()
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    AI-powered recommendation engine for projects, collaborators, and content
    """
    
    def __init__(self):
        self.tfidf_vectorizer = None
        self.svd_model = None
        self.user_clusters = None
        self.project_categories = [
            'web_development', 'mobile_app', 'data_science', 'machine_learning',
            'design', 'marketing', 'content_creation', 'e_commerce', 'gaming',
            'blockchain', 'iot', 'ai_research', 'social_media', 'education'
        ]
        
    def initialize_models(self):
        """Initialize recommendation models"""
        try:
            # Initialize TF-IDF for content-based recommendations
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Initialize SVD for collaborative filtering
            self.svd_model = TruncatedSVD(n_components=50, random_state=42)
            
            # Build user clusters for demographic filtering
            self._build_user_clusters()
            
            logger.info("Recommendation engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing recommendation engine: {e}")
    
    def get_project_recommendations(self, user, limit=10):
        """Get personalized project recommendations for a user"""
        try:
            cache_key = f"project_recommendations:{user.id}"
            cached_recommendations = cache.get(cache_key)
            
            if cached_recommendations:
                return cached_recommendations
            
            # Get user profile and preferences
            user_profile = self._get_user_profile_data(user)
            
            # Generate recommendations using multiple approaches
            content_based = self._content_based_project_recommendations(user, user_profile, limit)
            collaborative = self._collaborative_project_recommendations(user, limit)
            trending = self._trending_project_recommendations(user, limit)
            
            # Combine and rank recommendations
            recommendations = self._combine_project_recommendations(
                content_based, collaborative, trending, limit
            )
            
            # Cache recommendations
            cache.set(cache_key, recommendations, 3600)  # 1 hour
            
            # Track analytics
            AnalyticsCollector.track_event(
                'project_recommendations_generated',
                user=user,
                event_data={
                    'recommendations_count': len(recommendations),
                    'methods_used': ['content_based', 'collaborative', 'trending']
                }
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating project recommendations for user {user.id}: {e}")
            return []
    
    def get_collaborator_recommendations(self, user, project_context=None, limit=10):
        """Get personalized collaborator recommendations"""
        try:
            cache_key = f"collaborator_recommendations:{user.id}:{hash(str(project_context))}"
            cached_recommendations = cache.get(cache_key)
            
            if cached_recommendations:
                return cached_recommendations
            
            # Get user's collaboration history and preferences
            user_history = self._get_collaboration_history(user)
            
            # Generate recommendations
            if project_context:
                recommendations = self._project_specific_collaborator_recommendations(
                    user, project_context, limit
                )
            else:
                recommendations = self._general_collaborator_recommendations(user, limit)
            
            # Apply diversity and freshness filters
            recommendations = self._apply_recommendation_filters(recommendations, user_history)
            
            # Cache recommendations
            cache.set(cache_key, recommendations, 1800)  # 30 minutes
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error generating collaborator recommendations for user {user.id}: {e}")
            return []
    
    def get_skill_recommendations(self, user, limit=5):
        """Recommend skills for user to learn based on market trends and profile"""
        try:
            cache_key = f"skill_recommendations:{user.id}"
            cached_skills = cache.get(cache_key)
            
            if cached_skills:
                return cached_skills
            
            # Get user's current skills
            user_profile = self._get_user_profile_data(user)
            current_skills = set(user_profile.get('skills', []))
            
            # Analyze market trends and skill gaps
            trending_skills = self._get_trending_skills()
            complementary_skills = self._get_complementary_skills(current_skills)
            high_demand_skills = self._get_high_demand_skills()
            
            # Score and rank skills
            skill_scores = {}
            
            for skill in trending_skills:
                if skill not in current_skills:
                    skill_scores[skill] = skill_scores.get(skill, 0) + 0.4
            
            for skill in complementary_skills:
                if skill not in current_skills:
                    skill_scores[skill] = skill_scores.get(skill, 0) + 0.3
            
            for skill in high_demand_skills:
                if skill not in current_skills:
                    skill_scores[skill] = skill_scores.get(skill, 0) + 0.3
            
            # Sort by score and return top recommendations
            recommended_skills = sorted(
                skill_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:limit]
            
            recommendations = [
                {
                    'skill': skill,
                    'score': score,
                    'reason': self._get_skill_recommendation_reason(skill, user_profile)
                }
                for skill, score in recommended_skills
            ]
            
            # Cache recommendations
            cache.set(cache_key, recommendations, 7200)  # 2 hours
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating skill recommendations for user {user.id}: {e}")
            return []
    
    def get_content_recommendations(self, user, content_type='all', limit=10):
        """Recommend content (articles, tutorials, resources) based on user interests"""
        try:
            cache_key = f"content_recommendations:{user.id}:{content_type}"
            cached_content = cache.get(cache_key)
            
            if cached_content:
                return cached_content
            
            user_profile = self._get_user_profile_data(user)
            user_interests = self._extract_user_interests(user_profile)
            
            # Generate content recommendations based on interests
            recommendations = []
            
            if content_type in ['all', 'tutorials']:
                tutorials = self._recommend_tutorials(user_interests, limit // 3)
                recommendations.extend(tutorials)
            
            if content_type in ['all', 'articles']:
                articles = self._recommend_articles(user_interests, limit // 3)
                recommendations.extend(articles)
            
            if content_type in ['all', 'tools']:
                tools = self._recommend_tools(user_interests, limit // 3)
                recommendations.extend(tools)
            
            # Shuffle and limit
            import random
            random.shuffle(recommendations)
            recommendations = recommendations[:limit]
            
            # Cache recommendations
            cache.set(cache_key, recommendations, 3600)  # 1 hour
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating content recommendations for user {user.id}: {e}")
            return []
    
    def _get_user_profile_data(self, user):
        """Extract comprehensive user profile data"""
        try:
            profile = CreatorProfile.objects.get(user=user)
            
            return {
                'skills': getattr(profile, 'skills', []),
                'bio': getattr(profile, 'bio', ''),
                'location': getattr(profile, 'location', ''),
                'experience_level': getattr(profile, 'experience_level', 'beginner'),
                'interests': getattr(profile, 'interests', []),
                'portfolio_tags': getattr(profile, 'portfolio_tags', [])
            }
            
        except CreatorProfile.DoesNotExist:
            return {
                'skills': [],
                'bio': '',
                'location': '',
                'experience_level': 'beginner',
                'interests': [],
                'portfolio_tags': []
            }
    
    def _content_based_project_recommendations(self, user, user_profile, limit):
        """Generate content-based project recommendations"""
        recommendations = []
        
        try:
            user_skills = set(user_profile.get('skills', []))
            user_interests = set(user_profile.get('interests', []))
            
            # Recommend projects based on skill matches
            for category in self.project_categories:
                if any(skill.lower() in category.lower() for skill in user_skills):
                    recommendations.append({
                        'type': 'project_idea',
                        'category': category,
                        'title': self._generate_project_title(category, user_skills),
                        'description': self._generate_project_description(category, user_skills),
                        'skills_required': list(user_skills)[:3],
                        'difficulty': self._estimate_project_difficulty(user_profile),
                        'score': 0.8
                    })
            
            # Add trending project ideas
            trending_categories = ['ai_research', 'blockchain', 'web_development']
            for category in trending_categories:
                if category not in [r['category'] for r in recommendations]:
                    recommendations.append({
                        'type': 'project_idea',
                        'category': category,
                        'title': self._generate_project_title(category, user_skills),
                        'description': self._generate_project_description(category, user_skills),
                        'skills_required': self._get_category_skills(category),
                        'difficulty': 'intermediate',
                        'score': 0.6
                    })
            
        except Exception as e:
            logger.error(f"Error in content-based recommendations: {e}")
        
        return recommendations[:limit]
    
    def _collaborative_project_recommendations(self, user, limit):
        """Generate collaborative filtering project recommendations"""
        recommendations = []
        
        try:
            # Find similar users based on past collaborations
            similar_users = self._find_similar_users(user)
            
            # Get projects that similar users have worked on
            for similar_user in similar_users[:5]:
                # Get their recent collaboration invites or projects
                recent_invites = NewCollaborationInvite.objects.filter(
                    sender=similar_user,
                    created_at__gte=timezone.now() - timedelta(days=30)
                ).values_list('project_title', 'project_description')[:2]
                
                for title, description in recent_invites:
                    recommendations.append({
                        'type': 'similar_user_project',
                        'title': title or 'Collaborative Project',
                        'description': description or 'Project based on similar user activity',
                        'similar_user': similar_user.username,
                        'score': 0.7
                    })
            
        except Exception as e:
            logger.error(f"Error in collaborative recommendations: {e}")
        
        return recommendations[:limit]
    
    def _trending_project_recommendations(self, user, limit):
        """Generate trending project recommendations"""
        recommendations = []
        
        try:
            # Analyze recent platform activity to identify trends
            recent_searches = SearchQuery.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).values_list('query_text', flat=True)
            
            # Count search term frequency
            search_terms = {}
            for query in recent_searches:
                words = query.lower().split()
                for word in words:
                    if len(word) > 3:  # Filter short words
                        search_terms[word] = search_terms.get(word, 0) + 1
            
            # Get top trending terms
            trending_terms = sorted(search_terms.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for term, count in trending_terms:
                recommendations.append({
                    'type': 'trending_project',
                    'title': f"{term.title()} Project Opportunity",
                    'description': f"Trending project idea based on recent platform activity around {term}",
                    'trend_score': count,
                    'score': 0.5
                })
            
        except Exception as e:
            logger.error(f"Error in trending recommendations: {e}")
        
        return recommendations[:limit]
    
    def _combine_project_recommendations(self, content_based, collaborative, trending, limit):
        """Combine and rank different types of recommendations"""
        all_recommendations = []
        
        # Add recommendations with source weighting
        for rec in content_based:
            rec['source'] = 'content_based'
            rec['final_score'] = rec['score'] * 0.5  # 50% weight
            all_recommendations.append(rec)
        
        for rec in collaborative:
            rec['source'] = 'collaborative'
            rec['final_score'] = rec['score'] * 0.3  # 30% weight
            all_recommendations.append(rec)
        
        for rec in trending:
            rec['source'] = 'trending'
            rec['final_score'] = rec['score'] * 0.2  # 20% weight
            all_recommendations.append(rec)
        
        # Sort by final score and return top recommendations
        all_recommendations.sort(key=lambda x: x['final_score'], reverse=True)
        return all_recommendations[:limit]
    
    def _build_user_clusters(self):
        """Build user clusters for demographic filtering"""
        try:
            # Get all user profiles
            profiles = CreatorProfile.objects.select_related('user').all()
            
            if profiles.count() < 10:
                logger.warning("Insufficient users for clustering")
                return
            
            # Extract features for clustering
            features = []
            user_ids = []
            
            for profile in profiles:
                feature_vector = [
                    len(getattr(profile, 'skills', [])),
                    hash(getattr(profile, 'location', '')) % 1000,  # Simple location encoding
                    {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}.get(
                        getattr(profile, 'experience_level', 'beginner'), 1
                    )
                ]
                features.append(feature_vector)
                user_ids.append(profile.user.id)
            
            # Perform clustering
            if len(features) >= 5:
                kmeans = KMeans(n_clusters=min(5, len(features)), random_state=42)
                clusters = kmeans.fit_predict(features)
                
                # Store cluster assignments
                self.user_clusters = dict(zip(user_ids, clusters))
                
                logger.info(f"Built user clusters with {len(set(clusters))} clusters")
            
        except Exception as e:
            logger.error(f"Error building user clusters: {e}")
    
    def _find_similar_users(self, user):
        """Find users similar to the given user"""
        try:
            if not self.user_clusters or user.id not in self.user_clusters:
                # Fallback to simple similarity
                return User.objects.exclude(id=user.id).filter(
                    creatorprofile__isnull=False
                )[:5]
            
            user_cluster = self.user_clusters[user.id]
            similar_user_ids = [
                uid for uid, cluster in self.user_clusters.items() 
                if cluster == user_cluster and uid != user.id
            ]
            
            return User.objects.filter(id__in=similar_user_ids)[:5]
            
        except Exception as e:
            logger.error(f"Error finding similar users: {e}")
            return []
    
    def _get_collaboration_history(self, user):
        """Get user's collaboration history"""
        try:
            sent_invites = NewCollaborationInvite.objects.filter(sender=user)
            received_invites = NewCollaborationInvite.objects.filter(recipient=user)
            
            return {
                'sent_count': sent_invites.count(),
                'received_count': received_invites.count(),
                'accepted_count': received_invites.filter(status='accepted').count(),
                'recent_collaborators': list(
                    sent_invites.values_list('recipient__username', flat=True)[:5]
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting collaboration history: {e}")
            return {}
    
    def _get_trending_skills(self):
        """Get currently trending skills based on platform activity"""
        # This would typically analyze job postings, project requirements, etc.
        # For now, return a static list of trending skills
        return [
            'Python', 'React', 'Machine Learning', 'AWS', 'Docker',
            'Kubernetes', 'TypeScript', 'GraphQL', 'Blockchain', 'AI/ML'
        ]
    
    def _get_complementary_skills(self, current_skills):
        """Get skills that complement the user's current skills"""
        skill_complements = {
            'Python': ['Django', 'Flask', 'FastAPI', 'Data Science'],
            'JavaScript': ['React', 'Node.js', 'TypeScript', 'Vue.js'],
            'React': ['Redux', 'Next.js', 'TypeScript', 'Testing'],
            'Design': ['Figma', 'Sketch', 'Adobe Creative Suite', 'Prototyping'],
            'Marketing': ['SEO', 'Content Marketing', 'Social Media', 'Analytics']
        }
        
        complements = []
        for skill in current_skills:
            if skill in skill_complements:
                complements.extend(skill_complements[skill])
        
        return list(set(complements))
    
    def _get_high_demand_skills(self):
        """Get skills that are in high demand"""
        # This would typically analyze job market data
        return [
            'Cloud Computing', 'DevOps', 'Cybersecurity', 'Data Analysis',
            'Mobile Development', 'UI/UX Design', 'Project Management'
        ]
    
    def _generate_project_title(self, category, user_skills):
        """Generate a project title based on category and skills"""
        titles = {
            'web_development': f"Modern Web App with {', '.join(list(user_skills)[:2])}",
            'mobile_app': f"Mobile Application for {category.replace('_', ' ').title()}",
            'data_science': "Data Analysis and Visualization Project",
            'machine_learning': "ML Model Development Project",
            'design': "Creative Design Portfolio Project"
        }
        return titles.get(category, f"{category.replace('_', ' ').title()} Project")
    
    def _generate_project_description(self, category, user_skills):
        """Generate a project description"""
        return f"A {category.replace('_', ' ')} project that leverages your skills in {', '.join(list(user_skills)[:3])}. This project would help you build your portfolio and collaborate with other creators."
    
    def _estimate_project_difficulty(self, user_profile):
        """Estimate appropriate project difficulty for user"""
        experience_level = user_profile.get('experience_level', 'beginner')
        skill_count = len(user_profile.get('skills', []))
        
        if experience_level == 'expert' or skill_count > 10:
            return 'advanced'
        elif experience_level in ['advanced', 'intermediate'] or skill_count > 5:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _get_category_skills(self, category):
        """Get typical skills for a project category"""
        category_skills = {
            'web_development': ['HTML', 'CSS', 'JavaScript', 'React'],
            'mobile_app': ['React Native', 'Flutter', 'Swift', 'Kotlin'],
            'data_science': ['Python', 'Pandas', 'NumPy', 'Matplotlib'],
            'machine_learning': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn'],
            'design': ['Figma', 'Adobe Creative Suite', 'Sketch', 'Prototyping']
        }
        return category_skills.get(category, [])
    
    def _get_skill_recommendation_reason(self, skill, user_profile):
        """Get reason for recommending a specific skill"""
        current_skills = user_profile.get('skills', [])
        
        if any(related in current_skills for related in ['Python', 'JavaScript', 'React']):
            return f"Complements your existing {', '.join(current_skills[:2])} skills"
        else:
            return "High demand skill in the current market"
    
    def _extract_user_interests(self, user_profile):
        """Extract user interests from profile data"""
        interests = set()
        
        # Add explicit interests
        interests.update(user_profile.get('interests', []))
        
        # Infer interests from skills
        skill_to_interest = {
            'Python': 'programming',
            'JavaScript': 'web_development',
            'Design': 'creative_design',
            'Marketing': 'digital_marketing',
            'Data Science': 'analytics'
        }
        
        for skill in user_profile.get('skills', []):
            if skill in skill_to_interest:
                interests.add(skill_to_interest[skill])
        
        return list(interests)
    
    def _recommend_tutorials(self, interests, limit):
        """Recommend tutorials based on interests"""
        # This would typically integrate with tutorial platforms
        tutorial_suggestions = [
            {
                'type': 'tutorial',
                'title': f"Advanced {interest.title()} Techniques",
                'description': f"Learn advanced concepts in {interest}",
                'url': f"https://example.com/tutorials/{interest}",
                'difficulty': 'intermediate'
            }
            for interest in interests[:limit]
        ]
        return tutorial_suggestions
    
    def _recommend_articles(self, interests, limit):
        """Recommend articles based on interests"""
        # This would typically integrate with content platforms
        article_suggestions = [
            {
                'type': 'article',
                'title': f"Latest Trends in {interest.title()}",
                'description': f"Stay updated with the latest in {interest}",
                'url': f"https://example.com/articles/{interest}",
                'read_time': '5 min'
            }
            for interest in interests[:limit]
        ]
        return article_suggestions
    
    def _recommend_tools(self, interests, limit):
        """Recommend tools based on interests"""
        # This would typically integrate with tool databases
        tool_suggestions = [
            {
                'type': 'tool',
                'title': f"Best Tools for {interest.title()}",
                'description': f"Essential tools for {interest} professionals",
                'url': f"https://example.com/tools/{interest}",
                'category': interest
            }
            for interest in interests[:limit]
        ]
        return tool_suggestions
    
    def _project_specific_collaborator_recommendations(self, user, project_context, limit):
        """Recommend collaborators for a specific project"""
        # This would analyze project requirements and find matching skills
        return self._general_collaborator_recommendations(user, limit)
    
    def _general_collaborator_recommendations(self, user, limit):
        """General collaborator recommendations"""
        try:
            # Get users with complementary skills
            user_profile = self._get_user_profile_data(user)
            user_skills = set(user_profile.get('skills', []))
            
            # Find users with different but complementary skills
            potential_collaborators = User.objects.exclude(id=user.id).filter(
                creatorprofile__isnull=False
            )[:limit * 2]
            
            recommendations = []
            for collaborator in potential_collaborators:
                collab_profile = self._get_user_profile_data(collaborator)
                collab_skills = set(collab_profile.get('skills', []))
                
                # Calculate complementarity score
                skill_overlap = len(user_skills & collab_skills)
                skill_complement = len(collab_skills - user_skills)
                
                if skill_complement > skill_overlap:  # More complementary than overlapping
                    recommendations.append({
                        'user': collaborator,
                        'score': skill_complement / (skill_overlap + 1),
                        'complementary_skills': list(collab_skills - user_skills)[:3]
                    })
            
            # Sort by score
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error in general collaborator recommendations: {e}")
            return []
    
    def _apply_recommendation_filters(self, recommendations, user_history):
        """Apply diversity and freshness filters to recommendations"""
        try:
            # Filter out recent collaborators to promote diversity
            recent_collaborators = set(user_history.get('recent_collaborators', []))
            
            filtered_recommendations = [
                rec for rec in recommendations
                if rec.get('user', {}).get('username') not in recent_collaborators
            ]
            
            return filtered_recommendations
            
        except Exception as e:
            logger.error(f"Error applying recommendation filters: {e}")
            return recommendations


# Global instance
recommendation_engine = RecommendationEngine()
