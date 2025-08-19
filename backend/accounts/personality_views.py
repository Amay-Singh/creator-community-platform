"""
API Views for Personality Quiz and Matching System
Implements REQ-6: Personality-driven collaboration matching
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from .personality_models import PersonalityQuiz, PersonalityResponse, PersonalityProfile, CollaborationMatch
from .personality_serializers import (
    PersonalityQuizSerializer, PersonalityResponseSerializer, PersonalityProfileSerializer,
    CollaborationMatchSerializer, QuizSubmissionSerializer, MatchActionSerializer,
    PersonalityInsightsSerializer, MatchingPreferencesSerializer
)
from .personality_services import personality_analyzer, collaboration_matcher
from .models import CreatorProfile

class PersonalityQuizListView(generics.ListAPIView):
    """List available personality quizzes"""
    
    queryset = PersonalityQuiz.objects.filter(is_active=True)
    serializer_class = PersonalityQuizSerializer
    permission_classes = [permissions.IsAuthenticated]

class PersonalityQuizDetailView(generics.RetrieveAPIView):
    """Get detailed quiz information"""
    
    queryset = PersonalityQuiz.objects.filter(is_active=True)
    serializer_class = PersonalityQuizSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_quiz_response(request):
    """Submit personality quiz response and get analysis"""
    
    try:
        profile = request.user.creator_profile
    except CreatorProfile.DoesNotExist:
        return Response(
            {'error': 'Creator profile required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = QuizSubmissionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    quiz_id = serializer.validated_data['quiz_id']
    answers = serializer.validated_data['answers']
    completion_time = serializer.validated_data.get('completion_time_seconds')
    
    try:
        quiz = PersonalityQuiz.objects.get(id=quiz_id, is_active=True)
        
        with transaction.atomic():
            # Save quiz response
            response_obj, created = PersonalityResponse.objects.update_or_create(
                profile=profile,
                quiz=quiz,
                defaults={
                    'answers': answers,
                    'completion_time_seconds': completion_time,
                }
            )
            
            # Analyze responses using AI
            analysis_results = personality_analyzer.analyze_quiz_responses(
                answers, quiz.quiz_type
            )
            
            # Update or create personality profile
            personality_profile, created = PersonalityProfile.objects.update_or_create(
                profile=profile,
                defaults={
                    'openness': analysis_results.get('openness', 50.0),
                    'conscientiousness': analysis_results.get('conscientiousness', 50.0),
                    'extraversion': analysis_results.get('extraversion', 50.0),
                    'agreeableness': analysis_results.get('agreeableness', 50.0),
                    'neuroticism': analysis_results.get('neuroticism', 50.0),
                    'creativity_index': analysis_results.get('creativity_index', 60.0),
                    'risk_tolerance': analysis_results.get('risk_tolerance', 50.0),
                    'collaboration_style': analysis_results.get('collaboration_style', 'collaborator'),
                    'communication_preference': analysis_results.get('communication_preference', 'casual'),
                    'work_pace': analysis_results.get('work_pace', 'moderate'),
                    'feedback_style': analysis_results.get('feedback_style', 'milestone'),
                    'confidence_score': analysis_results.get('confidence_score', 0.6),
                }
            )
            
            # Generate new matches after personality update
            new_matches = collaboration_matcher.generate_matches_for_profile(profile, limit=5)
            
            return Response({
                'message': 'Quiz submitted successfully',
                'personality_profile': PersonalityProfileSerializer(personality_profile).data,
                'new_matches_count': len(new_matches),
                'analysis_summary': analysis_results.get('analysis_summary', 'Personality profile updated')
            }, status=status.HTTP_201_CREATED)
            
    except PersonalityQuiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Analysis failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class PersonalityProfileView(generics.RetrieveUpdateAPIView):
    """Get or update personality profile"""
    
    serializer_class = PersonalityProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        try:
            profile = self.request.user.creator_profile
            personality_profile, created = PersonalityProfile.objects.get_or_create(
                profile=profile,
                defaults={
                    'creativity_index': 60.0,
                    'confidence_score': 0.5
                }
            )
            return personality_profile
        except CreatorProfile.DoesNotExist:
            return None
    
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj is None:
            return Response(
                {'error': 'Creator profile required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().get(request, *args, **kwargs)

class MatchPagination(PageNumberPagination):
    """Custom pagination for matches"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class CollaborationMatchListView(generics.ListAPIView):
    """List collaboration matches for current user"""
    
    serializer_class = CollaborationMatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MatchPagination
    
    def get_queryset(self):
        try:
            profile = self.request.user.creator_profile
            
            # Get matches where user is either profile_a or profile_b
            matches = CollaborationMatch.objects.filter(
                Q(profile_a=profile) | Q(profile_b=profile)
            ).select_related('profile_a', 'profile_b').order_by('-created_at')
            
            # Filter by status if provided
            status_filter = self.request.query_params.get('status')
            if status_filter:
                matches = matches.filter(
                    Q(profile_a=profile, status_a=status_filter) |
                    Q(profile_b=profile, status_b=status_filter)
                )
            
            return matches
            
        except CreatorProfile.DoesNotExist:
            return CollaborationMatch.objects.none()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_new_matches(request):
    """Generate new collaboration matches for current user"""
    
    try:
        profile = request.user.creator_profile
    except CreatorProfile.DoesNotExist:
        return Response(
            {'error': 'Creator profile required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get preferences from request
    preferences_serializer = MatchingPreferencesSerializer(data=request.data)
    if not preferences_serializer.is_valid():
        return Response(preferences_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    preferences = preferences_serializer.validated_data
    limit = preferences.get('max_matches_per_day', 10)
    
    try:
        # Generate matches
        new_matches = collaboration_matcher.generate_matches_for_profile(profile, limit=limit)
        
        return Response({
            'message': f'Generated {len(new_matches)} new matches',
            'matches': CollaborationMatchSerializer(new_matches, many=True).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Match generation failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def match_action(request):
    """Handle match actions (like/pass)"""
    
    try:
        profile = request.user.creator_profile
    except CreatorProfile.DoesNotExist:
        return Response(
            {'error': 'Creator profile required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = MatchActionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    match_id = serializer.validated_data['match_id']
    action = serializer.validated_data['action']
    
    try:
        match = CollaborationMatch.objects.get(id=match_id)
        
        # Determine which profile is taking action
        if match.profile_a == profile:
            status_field = 'status_a'
            viewed_field = 'viewed_at_a'
        elif match.profile_b == profile:
            status_field = 'status_b'
            viewed_field = 'viewed_at_b'
        else:
            return Response(
                {'error': 'Not authorized for this match'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update match status
        new_status = 'liked' if action == 'like' else 'passed'
        setattr(match, status_field, new_status)
        
        # Mark as viewed if not already
        if not getattr(match, viewed_field):
            setattr(match, viewed_field, timezone.now())
        
        match.save()
        
        # Check for mutual match
        is_mutual = match.update_match_status()
        
        response_data = {
            'message': f'Match {action}d successfully',
            'match': CollaborationMatchSerializer(match).data,
            'is_mutual_match': is_mutual
        }
        
        if is_mutual:
            response_data['message'] = 'Congratulations! You have a mutual match!'
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except CollaborationMatch.DoesNotExist:
        return Response(
            {'error': 'Match not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def personality_insights(request):
    """Get AI-generated personality insights and recommendations"""
    
    try:
        profile = request.user.creator_profile
        personality_profile = profile.personality_profile
    except (CreatorProfile.DoesNotExist, PersonalityProfile.DoesNotExist):
        return Response(
            {'error': 'Personality profile not found. Please complete a personality quiz first.'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Generate insights based on personality profile
    insights = {
        'personality_summary': _generate_personality_summary(personality_profile),
        'strengths': _identify_strengths(personality_profile),
        'collaboration_tips': _generate_collaboration_tips(personality_profile),
        'recommended_partners': _recommend_partner_types(personality_profile),
        'growth_areas': _identify_growth_areas(personality_profile)
    }
    
    serializer = PersonalityInsightsSerializer(insights)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def match_statistics(request):
    """Get matching statistics for current user"""
    
    try:
        profile = request.user.creator_profile
    except CreatorProfile.DoesNotExist:
        return Response(
            {'error': 'Creator profile required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Calculate statistics
    total_matches = CollaborationMatch.objects.filter(
        Q(profile_a=profile) | Q(profile_b=profile)
    ).count()
    
    mutual_matches = CollaborationMatch.objects.filter(
        Q(profile_a=profile, status_a='matched') | Q(profile_b=profile, status_b='matched')
    ).count()
    
    pending_matches = CollaborationMatch.objects.filter(
        Q(profile_a=profile, status_a='pending') | Q(profile_b=profile, status_b='pending')
    ).count()
    
    liked_matches = CollaborationMatch.objects.filter(
        Q(profile_a=profile, status_a='liked') | Q(profile_b=profile, status_b='liked')
    ).count()
    
    stats = {
        'total_matches': total_matches,
        'mutual_matches': mutual_matches,
        'pending_matches': pending_matches,
        'liked_matches': liked_matches,
        'match_rate': (mutual_matches / max(total_matches, 1)) * 100,
        'response_rate': ((liked_matches + mutual_matches) / max(total_matches, 1)) * 100
    }
    
    return Response(stats, status=status.HTTP_200_OK)

# Helper functions for personality insights

def _generate_personality_summary(personality_profile):
    """Generate a summary of personality traits"""
    
    traits = []
    
    if personality_profile.openness > 70:
        traits.append("highly creative and open to new experiences")
    elif personality_profile.openness > 50:
        traits.append("moderately open to new ideas")
    
    if personality_profile.extraversion > 70:
        traits.append("outgoing and energetic")
    elif personality_profile.extraversion < 30:
        traits.append("more introverted and reflective")
    
    if personality_profile.agreeableness > 70:
        traits.append("collaborative and trusting")
    
    if personality_profile.conscientiousness > 70:
        traits.append("organized and reliable")
    
    if personality_profile.creativity_index > 80:
        traits.append("exceptionally creative")
    
    summary = f"You are {', '.join(traits[:3])}."
    if len(traits) > 3:
        summary += f" You also tend to be {', '.join(traits[3:])}."
    
    return summary

def _identify_strengths(personality_profile):
    """Identify key strengths based on personality"""
    
    strengths = []
    
    if personality_profile.creativity_index > 70:
        strengths.append("Strong creative vision and innovation")
    
    if personality_profile.agreeableness > 70:
        strengths.append("Excellent collaboration and teamwork skills")
    
    if personality_profile.conscientiousness > 70:
        strengths.append("Reliable project management and organization")
    
    if personality_profile.openness > 70:
        strengths.append("Adaptability and willingness to experiment")
    
    if personality_profile.extraversion > 70:
        strengths.append("Strong communication and networking abilities")
    
    if personality_profile.risk_tolerance > 70:
        strengths.append("Courage to take creative risks and try new approaches")
    
    return strengths[:4]  # Return top 4 strengths

def _generate_collaboration_tips(personality_profile):
    """Generate collaboration tips based on personality"""
    
    tips = []
    
    if personality_profile.communication_preference == 'direct':
        tips.append("Be clear and straightforward in your communications")
    elif personality_profile.communication_preference == 'diplomatic':
        tips.append("Use tactful communication to build consensus")
    
    if personality_profile.work_pace == 'fast':
        tips.append("Set clear deadlines and maintain momentum in projects")
    elif personality_profile.work_pace == 'deliberate':
        tips.append("Allow time for thoughtful planning and iteration")
    
    if personality_profile.collaboration_style == 'leader':
        tips.append("Take initiative in organizing and directing collaborative efforts")
    elif personality_profile.collaboration_style == 'supporter':
        tips.append("Focus on supporting others' visions while contributing your expertise")
    
    if personality_profile.feedback_style == 'frequent':
        tips.append("Schedule regular check-ins and feedback sessions")
    
    return tips

def _recommend_partner_types(personality_profile):
    """Recommend compatible partner types"""
    
    recommendations = []
    
    if personality_profile.collaboration_style == 'leader':
        recommendations.append("Supportive partners who appreciate clear direction")
    elif personality_profile.collaboration_style == 'supporter':
        recommendations.append("Natural leaders who can guide the creative vision")
    else:
        recommendations.append("Equal collaborators who share decision-making")
    
    if personality_profile.extraversion > 70:
        recommendations.append("Partners who enjoy brainstorming and active discussion")
    elif personality_profile.extraversion < 30:
        recommendations.append("Partners who work well independently and communicate thoughtfully")
    
    if personality_profile.creativity_index > 80:
        recommendations.append("Partners who can execute and refine creative ideas")
    
    return recommendations

def _identify_growth_areas(personality_profile):
    """Identify areas for potential growth"""
    
    growth_areas = []
    
    if personality_profile.conscientiousness < 40:
        growth_areas.append("Developing stronger project management and organizational skills")
    
    if personality_profile.agreeableness < 40:
        growth_areas.append("Building more collaborative and diplomatic communication")
    
    if personality_profile.openness < 40:
        growth_areas.append("Becoming more open to new ideas and creative approaches")
    
    if personality_profile.confidence_score < 0.5:
        growth_areas.append("Building confidence in your creative abilities and decisions")
    
    return growth_areas[:3]  # Return top 3 growth areas
