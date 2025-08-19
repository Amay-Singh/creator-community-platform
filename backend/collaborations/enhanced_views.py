"""
Enhanced Collaboration Views with AI Match Explanations
Implements REQ-8: Collaboration invites with match explanations
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from django.utils import timezone
import openai
from django.conf import settings

from .models import CollaborationInvite
from .enhanced_serializers import CollaborationInviteSerializer, CollaborationInviteCreateSerializer
from rest_framework.exceptions import ValidationError
from django.db import models
from accounts.models import CreatorProfile
from accounts.personality_services import personality_service

class EnhancedCollaborationInviteView(generics.CreateAPIView):
    """
    Create collaboration invite with AI-generated match explanation (REQ-8)
    """
    serializer_class = CollaborationInviteCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        sender_profile = getattr(self.request.user, 'profile', None)
        if not sender_profile:
            raise ValidationError("Sender profile not found")
        
        recipient_id = serializer.validated_data['recipient_id']
        try:
            recipient_profile = CreatorProfile.objects.get(id=recipient_id)
        except CreatorProfile.DoesNotExist:
            raise ValidationError("Recipient profile not found")
        
        # Generate AI match explanation
        match_explanation = self._generate_match_explanation(sender_profile, recipient_profile)
        
        # Calculate compatibility score
        compatibility_score = self._calculate_compatibility_score(sender_profile, recipient_profile)
        
        serializer.save(
            sender=sender_profile,
            recipient=recipient_profile,
            match_explanation=match_explanation,
            compatibility_score=compatibility_score
        )
    
    def _generate_match_explanation(self, sender: CreatorProfile, recipient: CreatorProfile) -> str:
        """Generate AI-powered match explanation"""
        
        try:
            client = openai.OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', None))
            
            prompt = f"""
            Generate a compelling collaboration match explanation for why {sender.display_name} ({sender.get_category_display()}, {sender.get_experience_level_display()}) 
            should collaborate with {recipient.display_name} ({recipient.get_category_display()}, {recipient.get_experience_level_display()}).
            
            Sender Bio: {sender.bio[:200] if sender.bio else 'No bio provided'}
            Recipient Bio: {recipient.bio[:200] if recipient.bio else 'No bio provided'}
            
            Focus on:
            1. Creative synergy potential
            2. Complementary skills
            3. Mutual learning opportunities
            4. Project possibilities
            
            Keep it engaging, personalized, and under 150 words.
            """
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative collaboration expert who helps artists and creators find meaningful partnerships. Write engaging, personalized match explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            # Fallback explanation
            return self._generate_fallback_explanation(sender, recipient)
    
    def _generate_fallback_explanation(self, sender: CreatorProfile, recipient: CreatorProfile) -> str:
        """Generate fallback explanation without AI"""
        
        if sender.category != recipient.category:
            return f"Great cross-disciplinary opportunity! {sender.display_name}'s {sender.get_category_display()} expertise could perfectly complement {recipient.display_name}'s {recipient.get_category_display()} skills, creating innovative collaborative projects that blend both creative worlds."
        else:
            return f"Strong collaboration potential! Both {sender.display_name} and {recipient.display_name} share a passion for {sender.get_category_display()}, offering opportunities for skill sharing, creative inspiration, and joint projects that could elevate both artists' work."
    
    def _calculate_compatibility_score(self, sender: CreatorProfile, recipient: CreatorProfile) -> float:
        """Calculate compatibility score between profiles"""
        
        score = 0.0
        
        # Category complementarity (30%)
        if sender.category != recipient.category:
            score += 0.3
        elif sender.category == recipient.category:
            score += 0.2  # Same category still has value
        
        # Experience level compatibility (25%)
        experience_levels = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'professional': 4}
        sender_level = experience_levels.get(sender.experience_level, 2)
        recipient_level = experience_levels.get(recipient.experience_level, 2)
        
        level_diff = abs(sender_level - recipient_level)
        if level_diff <= 1:
            score += 0.25
        elif level_diff == 2:
            score += 0.15
        
        # Portfolio quality (20%)
        if recipient.portfolio_items.filter(is_ai_validated=True).exists():
            score += 0.2
        
        # Activity level (15%)
        if recipient.user.last_login and recipient.user.last_login >= timezone.now() - timezone.timedelta(days=7):
            score += 0.15
        
        # Feedback score (10%)
        avg_feedback = recipient.feedback_received.aggregate(
            avg_rating=models.Avg('rating')
        )['avg_rating']
        
        if avg_feedback and avg_feedback >= 4.0:
            score += 0.1
        
        return min(1.0, score)

class CollaborationInviteListView(generics.ListAPIView):
    """List collaboration invites for authenticated user"""
    serializer_class = CollaborationInviteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
            return CollaborationInvite.objects.none()
        
        invite_type = self.request.query_params.get('type', 'received')
        
        if invite_type == 'sent':
            return CollaborationInvite.objects.filter(sender=profile).order_by('-created_at')
        else:
            return CollaborationInvite.objects.filter(recipient=profile).order_by('-created_at')

class CollaborationInviteDetailView(generics.RetrieveUpdateAPIView):
    """View and update collaboration invite"""
    serializer_class = CollaborationInviteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
            return CollaborationInvite.objects.none()
        
        return CollaborationInvite.objects.filter(
            Q(sender=profile) | Q(recipient=profile)
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        profile = getattr(request.user, 'profile', None)
        
        # Only recipient can accept/decline invites
        if instance.recipient != profile:
            return Response(
                {'error': 'Only the recipient can update invite status'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status in ['accepted', 'declined']:
            instance.status = new_status
            instance.responded_at = timezone.now()
            instance.save()
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Invalid status. Use "accepted" or "declined"'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_collaboration_suggestions(request):
    """Generate AI-powered collaboration suggestions"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get potential collaborators
    suggestions = []
    
    # Exclude already invited profiles
    invited_profiles = CollaborationInvite.objects.filter(
        sender=profile
    ).values_list('recipient_id', flat=True)
    
    # Find complementary profiles
    potential_collaborators = CreatorProfile.objects.filter(
        is_validated=True,
        user__is_active=True
    ).exclude(
        id__in=list(invited_profiles) + [profile.id]
    )[:20]
    
    for candidate in potential_collaborators:
        compatibility_score = EnhancedCollaborationInviteView()._calculate_compatibility_score(profile, candidate)
        
        if compatibility_score > 0.6:  # Only suggest high compatibility matches
            suggestions.append({
                'profile': {
                    'id': str(candidate.id),
                    'display_name': candidate.display_name,
                    'category': candidate.get_category_display(),
                    'experience_level': candidate.get_experience_level_display(),
                    'bio': candidate.bio[:150] + '...' if len(candidate.bio) > 150 else candidate.bio,
                    'avatar_url': candidate.avatar.url if candidate.avatar else None,
                    'portfolio_count': candidate.portfolio_items.count()
                },
                'compatibility_score': compatibility_score,
                'suggestion_reason': _get_suggestion_reason(profile, candidate, compatibility_score)
            })
    
    # Sort by compatibility score
    suggestions.sort(key=lambda x: x['compatibility_score'], reverse=True)
    
    return Response({
        'suggestions': suggestions[:10],  # Top 10 suggestions
        'total_count': len(suggestions)
    })

def _get_suggestion_reason(profile: CreatorProfile, candidate: CreatorProfile, score: float) -> str:
    """Generate suggestion reason"""
    
    if profile.category != candidate.category:
        return f"Cross-disciplinary collaboration potential between {profile.get_category_display()} and {candidate.get_category_display()}"
    elif score > 0.8:
        return f"High compatibility match with shared {profile.get_category_display()} expertise"
    elif candidate.experience_level != profile.experience_level:
        return f"Great learning opportunity with {candidate.get_experience_level_display()} level expertise"
    else:
        return f"Strong collaboration potential in {profile.get_category_display()}"
