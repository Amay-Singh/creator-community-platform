"""
AI-Powered Personality Analysis and Matching Services
Implements REQ-6: Personality-driven collaboration matching with OpenAI integration
"""
import openai
import json
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from django.utils import timezone
from django.db import models
from .personality_models import PersonalityProfile, PersonalityQuiz, PersonalityResponse, CollaborationMatch
from .models import CreatorProfile

class PersonalityAnalyzer:
    """
    AI-powered personality analysis using OpenAI GPT models
    """
    
    def __init__(self):
        self.client = None
    
    def _get_client(self):
        """Lazy initialization of OpenAI client"""
        if self.client is None:
            try:
                self.client = openai.OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', None))
            except Exception as e:
                # Fallback if OpenAI is not configured
                self.client = None
        return self.client
        
    def analyze_quiz_responses(self, responses: Dict, quiz_type: str) -> Dict[str, float]:
        """
        Analyze quiz responses using AI to extract personality traits
        
        Args:
            responses: Dictionary of question_id -> answer mappings
            quiz_type: Type of quiz (big_five, creative_style, etc.)
        
        Returns:
            Dictionary of personality trait scores (0-100 scale)
        """
        prompt = self._build_analysis_prompt(responses, quiz_type)
        
        client = self._get_client()
        if not client:
            return self._fallback_analysis(responses, quiz_type)
        
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional personality psychologist specializing in creative personality assessment. Analyze quiz responses and provide accurate personality trait scores."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse AI response to extract scores
            analysis_text = response.choices[0].message.content
            scores = self._parse_personality_scores(analysis_text)
            
            return scores
            
        except Exception as e:
            # Fallback to rule-based analysis
            return self._fallback_analysis(responses, quiz_type)
    
    def _build_analysis_prompt(self, responses: Dict, quiz_type: str) -> str:
        """Build prompt for AI personality analysis"""
        
        base_prompt = f"""
        Analyze the following {quiz_type} quiz responses and provide personality trait scores on a 0-100 scale.
        
        Quiz Responses:
        {json.dumps(responses, indent=2)}
        
        Please provide scores for these traits:
        - Openness (0-100): Openness to experience and new ideas
        - Conscientiousness (0-100): Organization and dependability  
        - Extraversion (0-100): Social energy and assertiveness
        - Agreeableness (0-100): Cooperation and trust
        - Neuroticism (0-100): Emotional instability (higher = more neurotic)
        - Creativity Index (0-100): Overall creativity and innovation
        - Risk Tolerance (0-100): Willingness to take creative risks
        
        Also determine:
        - Collaboration Style: leader, collaborator, supporter, or independent
        - Communication Preference: direct, diplomatic, casual, or formal
        - Work Pace: fast, moderate, or deliberate
        - Feedback Style: frequent, milestone, or minimal
        
        Format your response as JSON:
        {{
            "openness": score,
            "conscientiousness": score,
            "extraversion": score,
            "agreeableness": score,
            "neuroticism": score,
            "creativity_index": score,
            "risk_tolerance": score,
            "collaboration_style": "style",
            "communication_preference": "preference",
            "work_pace": "pace",
            "feedback_style": "style",
            "confidence_score": 0.0-1.0,
            "analysis_summary": "Brief explanation of the personality profile"
        }}
        """
        
        return base_prompt
    
    def _parse_personality_scores(self, analysis_text: str) -> Dict[str, float]:
        """Parse AI response to extract personality scores"""
        try:
            # Try to extract JSON from the response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = analysis_text[start_idx:end_idx]
                scores = json.loads(json_str)
                return scores
            else:
                raise ValueError("No JSON found in response")
                
        except (json.JSONDecodeError, ValueError):
            # Fallback parsing using text analysis
            return self._extract_scores_from_text(analysis_text)
    
    def _extract_scores_from_text(self, text: str) -> Dict[str, float]:
        """Fallback method to extract scores from text response"""
        scores = {
            'openness': 50.0,
            'conscientiousness': 50.0,
            'extraversion': 50.0,
            'agreeableness': 50.0,
            'neuroticism': 50.0,
            'creativity_index': 50.0,
            'risk_tolerance': 50.0,
            'collaboration_style': 'collaborator',
            'communication_preference': 'casual',
            'work_pace': 'moderate',
            'feedback_style': 'milestone',
            'confidence_score': 0.5
        }
        
        # Simple keyword-based extraction
        trait_keywords = {
            'openness': ['open', 'creative', 'imaginative', 'curious'],
            'conscientiousness': ['organized', 'reliable', 'disciplined', 'thorough'],
            'extraversion': ['outgoing', 'social', 'energetic', 'assertive'],
            'agreeableness': ['cooperative', 'trusting', 'helpful', 'sympathetic'],
            'neuroticism': ['anxious', 'stressed', 'emotional', 'worried']
        }
        
        text_lower = text.lower()
        for trait, keywords in trait_keywords.items():
            keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
            # Adjust score based on keyword presence
            if keyword_count > 0:
                scores[trait] = min(100.0, 50.0 + (keyword_count * 10))
        
        return scores
    
    def _fallback_analysis(self, responses: Dict, quiz_type: str) -> Dict[str, float]:
        """Rule-based fallback analysis when AI is unavailable"""
        
        # Default scores
        scores = {
            'openness': 50.0,
            'conscientiousness': 50.0,
            'extraversion': 50.0,
            'agreeableness': 50.0,
            'neuroticism': 50.0,
            'creativity_index': 60.0,  # Assume creators are above average
            'risk_tolerance': 55.0,
            'collaboration_style': 'collaborator',
            'communication_preference': 'casual',
            'work_pace': 'moderate',
            'feedback_style': 'milestone',
            'confidence_score': 0.6
        }
        
        # Simple rule-based scoring based on response patterns
        if responses:
            total_responses = len(responses)
            positive_responses = sum(1 for answer in responses.values() 
                                   if isinstance(answer, (int, float)) and answer > 3)
            
            # Adjust extraversion based on positive response ratio
            if total_responses > 0:
                positivity_ratio = positive_responses / total_responses
                scores['extraversion'] = 30.0 + (positivity_ratio * 40.0)
                scores['agreeableness'] = 40.0 + (positivity_ratio * 30.0)
        
        return scores

class CollaborationMatcher:
    """
    AI-powered collaboration matching service
    """
    
    def __init__(self):
        self.analyzer = PersonalityAnalyzer()
        
    def generate_matches_for_profile(self, profile: CreatorProfile, limit: int = 10) -> List[CollaborationMatch]:
        """
        Generate collaboration matches for a given profile
        
        Args:
            profile: CreatorProfile to find matches for
            limit: Maximum number of matches to generate
        
        Returns:
            List of CollaborationMatch objects
        """
        # Get or create personality profile
        personality_profile = self._get_or_create_personality_profile(profile)
        
        # Find potential matches
        potential_matches = self._find_potential_matches(profile, personality_profile)
        
        # Score and rank matches
        scored_matches = []
        for candidate in potential_matches[:limit * 2]:  # Get more candidates to filter
            match_score = self._calculate_match_score(personality_profile, candidate)
            if match_score['compatibility_score'] > 0.3:  # Minimum threshold
                scored_matches.append((candidate, match_score))
        
        # Sort by compatibility score and take top matches
        scored_matches.sort(key=lambda x: x[1]['compatibility_score'], reverse=True)
        top_matches = scored_matches[:limit]
        
        # Create CollaborationMatch objects
        matches = []
        for candidate_profile, scores in top_matches:
            match = self._create_collaboration_match(profile, candidate_profile, scores)
            matches.append(match)
        
        return matches
    
    def _get_or_create_personality_profile(self, profile: CreatorProfile) -> PersonalityProfile:
        """Get existing personality profile or create default one"""
        try:
            return profile.personality_profile
        except PersonalityProfile.DoesNotExist:
            # Create default personality profile
            return PersonalityProfile.objects.create(
                profile=profile,
                openness=60.0,  # Creators tend to be open
                conscientiousness=55.0,
                extraversion=50.0,
                agreeableness=60.0,  # Important for collaboration
                neuroticism=45.0,
                creativity_index=70.0,  # High for creators
                risk_tolerance=60.0,
                confidence_score=0.5
            )
    
    def _find_potential_matches(self, profile: CreatorProfile, personality_profile: PersonalityProfile) -> List[CreatorProfile]:
        """Find potential collaboration candidates"""
        
        # Exclude profiles that already have matches
        existing_match_ids = set()
        existing_matches = CollaborationMatch.objects.filter(
            models.Q(profile_a=profile) | models.Q(profile_b=profile)
        ).values_list('profile_a_id', 'profile_b_id')
        
        for match in existing_matches:
            existing_match_ids.update(match)
        
        # Find candidates with different but complementary categories
        complementary_categories = self._get_complementary_categories(profile.category)
        
        candidates = CreatorProfile.objects.filter(
            is_validated=True,
            user__is_verified=True
        ).exclude(
            id__in=existing_match_ids
        ).exclude(
            id=profile.id
        )
        
        # Prioritize complementary categories
        priority_candidates = candidates.filter(category__in=complementary_categories)
        other_candidates = candidates.exclude(category__in=complementary_categories)
        
        # Combine and limit results
        all_candidates = list(priority_candidates[:20]) + list(other_candidates[:10])
        
        return all_candidates
    
    def _get_complementary_categories(self, category: str) -> List[str]:
        """Get categories that complement the given category"""
        
        complementary_map = {
            'visual_arts': ['performing_arts', 'media_arts', 'literary_arts'],
            'performing_arts': ['visual_arts', 'media_arts', 'digital_arts'],
            'literary_arts': ['visual_arts', 'media_arts', 'performing_arts'],
            'design': ['digital_arts', 'visual_arts', 'media_arts'],
            'digital_arts': ['design', 'visual_arts', 'performing_arts'],
            'crafts': ['design', 'visual_arts', 'media_arts'],
            'media_arts': ['visual_arts', 'performing_arts', 'digital_arts'],
            'culinary_arts': ['media_arts', 'visual_arts', 'design'],
            'architecture': ['design', 'visual_arts', 'digital_arts'],
        }
        
        return complementary_map.get(category, ['visual_arts', 'performing_arts', 'media_arts'])
    
    def _calculate_match_score(self, profile_a: PersonalityProfile, candidate: CreatorProfile) -> Dict[str, float]:
        """Calculate comprehensive match score between two profiles"""
        
        candidate_personality = self._get_or_create_personality_profile(candidate)
        
        # Personality compatibility
        personality_score = profile_a.get_compatibility_score(candidate_personality)
        
        # Skill complementarity
        skill_score = self._calculate_skill_complementarity(profile_a.profile, candidate)
        
        # Experience level compatibility
        experience_score = self._calculate_experience_compatibility(profile_a.profile, candidate)
        
        # Overall compatibility (weighted average)
        compatibility_score = (
            personality_score * 0.5 +
            skill_score * 0.3 +
            experience_score * 0.2
        )
        
        return {
            'compatibility_score': compatibility_score,
            'personality_score': personality_score,
            'skill_complementarity_score': skill_score,
            'experience_compatibility': experience_score
        }
    
    def _calculate_skill_complementarity(self, profile_a: CreatorProfile, profile_b: CreatorProfile) -> float:
        """Calculate how well skills complement each other"""
        
        # Category complementarity
        category_bonus = 0.2 if profile_a.category != profile_b.category else 0.0
        
        # Experience level complementarity
        exp_levels = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'professional': 4}
        exp_a = exp_levels.get(profile_a.experience_level, 2)
        exp_b = exp_levels.get(profile_b.experience_level, 2)
        
        # Similar experience levels are good for collaboration
        exp_diff = abs(exp_a - exp_b)
        exp_score = max(0, 1.0 - (exp_diff * 0.2))
        
        return min(1.0, category_bonus + exp_score)
    
    def _calculate_experience_compatibility(self, profile_a: CreatorProfile, profile_b: CreatorProfile) -> float:
        """Calculate experience level compatibility"""
        
        exp_levels = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'professional': 4}
        exp_a = exp_levels.get(profile_a.experience_level, 2)
        exp_b = exp_levels.get(profile_b.experience_level, 2)
        
        # Calculate compatibility based on experience difference
        exp_diff = abs(exp_a - exp_b)
        
        if exp_diff == 0:
            return 1.0  # Same level is perfect
        elif exp_diff == 1:
            return 0.8  # Adjacent levels are good
        elif exp_diff == 2:
            return 0.5  # Two levels apart is okay
        else:
            return 0.2  # Too far apart
    
    def _create_collaboration_match(self, profile_a: CreatorProfile, profile_b: CreatorProfile, scores: Dict) -> CollaborationMatch:
        """Create a CollaborationMatch object"""
        
        # Generate AI explanation for the match
        match_reason = self._generate_match_explanation(profile_a, profile_b, scores)
        
        # Suggest collaboration types
        collaboration_types = self._suggest_collaboration_types(profile_a, profile_b)
        
        match = CollaborationMatch.objects.create(
            profile_a=profile_a,
            profile_b=profile_b,
            compatibility_score=scores['compatibility_score'],
            personality_score=scores['personality_score'],
            skill_complementarity_score=scores['skill_complementarity_score'],
            match_reason=match_reason,
            suggested_collaboration_types=collaboration_types
        )
        
        return match
    
    def _generate_match_explanation(self, profile_a: CreatorProfile, profile_b: CreatorProfile, scores: Dict) -> str:
        """Generate AI explanation for why profiles match"""
        
        explanations = []
        
        # Personality compatibility
        if scores['personality_score'] > 0.7:
            explanations.append("Strong personality compatibility for smooth collaboration")
        elif scores['personality_score'] > 0.5:
            explanations.append("Good personality balance with complementary traits")
        
        # Skill complementarity
        if scores['skill_complementarity_score'] > 0.6:
            if profile_a.category != profile_b.category:
                explanations.append(f"Excellent cross-disciplinary potential between {profile_a.get_category_display()} and {profile_b.get_category_display()}")
            else:
                explanations.append("Strong skill alignment for focused collaboration")
        
        # Experience levels
        exp_a = profile_a.experience_level
        exp_b = profile_b.experience_level
        if exp_a == exp_b:
            explanations.append(f"Both at {exp_a} level for balanced partnership")
        else:
            explanations.append(f"Complementary experience levels ({exp_a} + {exp_b}) for mutual learning")
        
        if not explanations:
            explanations.append("Potential for creative collaboration based on profile analysis")
        
        return ". ".join(explanations) + "."
    
    def _suggest_collaboration_types(self, profile_a: CreatorProfile, profile_b: CreatorProfile) -> List[str]:
        """Suggest types of collaborations based on profiles"""
        
        suggestions = []
        
        # Category-based suggestions
        category_combos = {
            ('visual_arts', 'performing_arts'): ['music_video', 'album_artwork', 'concert_visuals'],
            ('visual_arts', 'literary_arts'): ['book_illustration', 'graphic_novel', 'poetry_art'],
            ('performing_arts', 'media_arts'): ['music_video', 'podcast', 'live_stream'],
            ('digital_arts', 'visual_arts'): ['digital_gallery', 'nft_collection', 'app_design'],
            ('media_arts', 'literary_arts'): ['documentary', 'storytelling_video', 'blog_content'],
        }
        
        key = (profile_a.category, profile_b.category)
        reverse_key = (profile_b.category, profile_a.category)
        
        suggestions.extend(category_combos.get(key, category_combos.get(reverse_key, [])))
        
        # General collaboration types
        general_types = ['creative_project', 'skill_exchange', 'portfolio_collaboration', 'brand_partnership']
        suggestions.extend(general_types)
        
        return list(set(suggestions))  # Remove duplicates

# Service instances
personality_analyzer = PersonalityAnalyzer()
collaboration_matcher = CollaborationMatcher()
