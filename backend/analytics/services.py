"""
Analytics data collection services
"""
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from .models import (
    UserEngagementMetric, PlatformMetric, MatchingAnalytics, 
    NotificationAnalytics, RealtimeAnalytics, AnalyticsEvent
)
from notifications.models import Notification
from ai_services.models import MatchingResult
from collaborations.models import NewCollaborationInvite
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class AnalyticsCollector:
    """Main service for collecting and aggregating analytics data"""
    
    @staticmethod
    def track_event(event_type, user=None, event_data=None, request=None, response_time=None):
        """Track an individual analytics event"""
        try:
            event_data = event_data or {}
            
            # Extract request context if available
            ip_address = None
            user_agent = ""
            session_id = ""
            
            if request:
                ip_address = request.META.get('REMOTE_ADDR')
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                session_id = request.session.session_key or ""
            
            AnalyticsEvent.objects.create(
                user=user,
                event_type=event_type,
                event_data=event_data,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                response_time=response_time
            )
            
            logger.debug(f"Tracked event: {event_type} for user {user}")
            
        except Exception as e:
            logger.error(f"Failed to track event {event_type}: {e}")
    
    @staticmethod
    def collect_daily_user_engagement(date=None):
        """Collect daily user engagement metrics"""
        if date is None:
            date = timezone.now().date()
        
        try:
            # Get all users who were active on this date
            active_users = AnalyticsEvent.objects.filter(
                timestamp__date=date,
                user__isnull=False
            ).values_list('user', flat=True).distinct()
            
            for user_id in active_users:
                user = User.objects.get(id=user_id)
                
                # Calculate engagement metrics for this user
                user_events = AnalyticsEvent.objects.filter(
                    user=user,
                    timestamp__date=date
                )
                
                # Session metrics (simplified - count login/logout pairs)
                sessions_count = user_events.filter(event_type='user_login').count()
                
                # Activity metrics
                pages_viewed = user_events.filter(event_type='page_view').count()
                actions_performed = user_events.exclude(event_type__in=['page_view', 'user_login', 'user_logout']).count()
                notifications_clicked = user_events.filter(event_type='notification_opened').count()
                
                # Feature usage
                matches_viewed = user_events.filter(event_type='match_request').count()
                collaborations_initiated = user_events.filter(event_type='collaboration_invite').count()
                messages_sent = user_events.filter(event_type='message_sent').count()
                
                # Create or update engagement metric
                engagement, created = UserEngagementMetric.objects.get_or_create(
                    user=user,
                    date=date,
                    defaults={
                        'sessions_count': sessions_count,
                        'pages_viewed': pages_viewed,
                        'actions_performed': actions_performed,
                        'notifications_clicked': notifications_clicked,
                        'matches_viewed': matches_viewed,
                        'collaborations_initiated': collaborations_initiated,
                        'messages_sent': messages_sent,
                    }
                )
                
                if not created:
                    engagement.sessions_count = sessions_count
                    engagement.pages_viewed = pages_viewed
                    engagement.actions_performed = actions_performed
                    engagement.notifications_clicked = notifications_clicked
                    engagement.matches_viewed = matches_viewed
                    engagement.collaborations_initiated = collaborations_initiated
                    engagement.messages_sent = messages_sent
                    engagement.save()
            
            logger.info(f"Collected user engagement metrics for {date}")
            
        except Exception as e:
            logger.error(f"Failed to collect user engagement metrics for {date}: {e}")
    
    @staticmethod
    def collect_daily_platform_metrics(date=None):
        """Collect daily platform-wide metrics"""
        if date is None:
            date = timezone.now().date()
        
        try:
            # User metrics
            total_users = User.objects.count()
            
            # Active users (different time periods)
            daily_active = AnalyticsEvent.objects.filter(
                timestamp__date=date,
                user__isnull=False
            ).values('user').distinct().count()
            
            weekly_start = date - timedelta(days=7)
            weekly_active = AnalyticsEvent.objects.filter(
                timestamp__date__gte=weekly_start,
                timestamp__date__lte=date,
                user__isnull=False
            ).values('user').distinct().count()
            
            monthly_start = date - timedelta(days=30)
            monthly_active = AnalyticsEvent.objects.filter(
                timestamp__date__gte=monthly_start,
                timestamp__date__lte=date,
                user__isnull=False
            ).values('user').distinct().count()
            
            new_registrations = User.objects.filter(date_joined__date=date).count()
            
            # Engagement metrics
            total_sessions = AnalyticsEvent.objects.filter(
                timestamp__date=date,
                event_type='user_login'
            ).count()
            
            total_page_views = AnalyticsEvent.objects.filter(
                timestamp__date=date,
                event_type='page_view'
            ).count()
            
            # Feature usage
            total_matches_generated = MatchingResult.objects.filter(created_at__date=date).count()
            successful_matches = MatchingResult.objects.filter(
                created_at__date=date,
                match_score__gte=0.7  # Consider matches with score >= 0.7 as successful
            ).count()
            
            collaboration_invites_sent = NewCollaborationInvite.objects.filter(created_at__date=date).count()
            collaboration_invites_accepted = NewCollaborationInvite.objects.filter(
                updated_at__date=date,
                status='accepted'
            ).count()
            
            messages_exchanged = AnalyticsEvent.objects.filter(
                timestamp__date=date,
                event_type='message_sent'
            ).count()
            
            # Performance metrics
            api_events = AnalyticsEvent.objects.filter(
                timestamp__date=date,
                event_type='api_request',
                response_time__isnull=False
            )
            avg_api_response_time = api_events.aggregate(Avg('response_time'))['response_time__avg'] or 0.0
            
            error_events = AnalyticsEvent.objects.filter(
                timestamp__date=date,
                event_type='error_occurred'
            ).count()
            total_events = AnalyticsEvent.objects.filter(timestamp__date=date).count()
            error_rate = (error_events / total_events * 100) if total_events > 0 else 0.0
            
            # Create or update platform metric
            platform_metric, created = PlatformMetric.objects.get_or_create(
                date=date,
                defaults={
                    'total_users': total_users,
                    'active_users_daily': daily_active,
                    'active_users_weekly': weekly_active,
                    'active_users_monthly': monthly_active,
                    'new_registrations': new_registrations,
                    'total_sessions': total_sessions,
                    'total_page_views': total_page_views,
                    'total_matches_generated': total_matches_generated,
                    'successful_matches': successful_matches,
                    'collaboration_invites_sent': collaboration_invites_sent,
                    'collaboration_invites_accepted': collaboration_invites_accepted,
                    'messages_exchanged': messages_exchanged,
                    'avg_api_response_time': avg_api_response_time,
                    'error_rate': error_rate,
                }
            )
            
            if not created:
                platform_metric.total_users = total_users
                platform_metric.active_users_daily = daily_active
                platform_metric.active_users_weekly = weekly_active
                platform_metric.active_users_monthly = monthly_active
                platform_metric.new_registrations = new_registrations
                platform_metric.total_sessions = total_sessions
                platform_metric.total_page_views = total_page_views
                platform_metric.total_matches_generated = total_matches_generated
                platform_metric.successful_matches = successful_matches
                platform_metric.collaboration_invites_sent = collaboration_invites_sent
                platform_metric.collaboration_invites_accepted = collaboration_invites_accepted
                platform_metric.messages_exchanged = messages_exchanged
                platform_metric.avg_api_response_time = avg_api_response_time
                platform_metric.error_rate = error_rate
                platform_metric.save()
            
            logger.info(f"Collected platform metrics for {date}")
            
        except Exception as e:
            logger.error(f"Failed to collect platform metrics for {date}: {e}")
    
    @staticmethod
    def collect_daily_matching_analytics(date=None):
        """Collect daily AI matching analytics"""
        if date is None:
            date = timezone.now().date()
        
        try:
            # Matching metrics
            total_match_requests = AnalyticsEvent.objects.filter(
                timestamp__date=date,
                event_type='match_request'
            ).count()
            
            matches_today = MatchingResult.objects.filter(created_at__date=date)
            successful_matches = matches_today.filter(match_score__gte=0.7).count()
            
            match_acceptance_rate = 0.0
            if total_match_requests > 0:
                accepted_matches = AnalyticsEvent.objects.filter(
                    timestamp__date=date,
                    event_type='match_acceptance'
                ).count()
                match_acceptance_rate = (accepted_matches / total_match_requests) * 100
            
            avg_match_score = matches_today.aggregate(Avg('match_score'))['match_score__avg'] or 0.0
            
            # Performance metrics (would need to be tracked in matching service)
            avg_matching_time = 0.5  # Placeholder - would come from actual timing
            cache_hit_rate = 75.0    # Placeholder - would come from cache metrics
            
            # Quality metrics (would need user feedback system)
            user_feedback_positive = 0  # Placeholder
            user_feedback_negative = 0  # Placeholder
            matches_leading_to_collaboration = NewCollaborationInvite.objects.filter(
                created_at__date=date
            ).count()  # Approximation
            
            # Create or update matching analytics
            matching_analytics, created = MatchingAnalytics.objects.get_or_create(
                date=date,
                defaults={
                    'total_match_requests': total_match_requests,
                    'successful_matches': successful_matches,
                    'match_acceptance_rate': match_acceptance_rate,
                    'avg_match_score': avg_match_score,
                    'avg_matching_time': avg_matching_time,
                    'cache_hit_rate': cache_hit_rate,
                    'user_feedback_positive': user_feedback_positive,
                    'user_feedback_negative': user_feedback_negative,
                    'matches_leading_to_collaboration': matches_leading_to_collaboration,
                }
            )
            
            if not created:
                matching_analytics.total_match_requests = total_match_requests
                matching_analytics.successful_matches = successful_matches
                matching_analytics.match_acceptance_rate = match_acceptance_rate
                matching_analytics.avg_match_score = avg_match_score
                matching_analytics.avg_matching_time = avg_matching_time
                matching_analytics.cache_hit_rate = cache_hit_rate
                matching_analytics.user_feedback_positive = user_feedback_positive
                matching_analytics.user_feedback_negative = user_feedback_negative
                matching_analytics.matches_leading_to_collaboration = matches_leading_to_collaboration
                matching_analytics.save()
            
            logger.info(f"Collected matching analytics for {date}")
            
        except Exception as e:
            logger.error(f"Failed to collect matching analytics for {date}: {e}")
    
    @staticmethod
    def collect_daily_notification_analytics(date=None):
        """Collect daily notification analytics"""
        if date is None:
            date = timezone.now().date()
        
        try:
            # Delivery metrics
            total_notifications_sent = Notification.objects.filter(created_at__date=date).count()
            push_notifications_sent = total_notifications_sent  # Assuming all are push for now
            email_notifications_sent = 0  # Would need email notification tracking
            
            # Engagement metrics
            notifications_opened = AnalyticsEvent.objects.filter(
                timestamp__date=date,
                event_type='notification_opened'
            ).count()
            
            notifications_clicked = notifications_opened  # Simplification
            
            open_rate = 0.0
            click_rate = 0.0
            if total_notifications_sent > 0:
                open_rate = (notifications_opened / total_notifications_sent) * 100
                click_rate = (notifications_clicked / total_notifications_sent) * 100
            
            # Performance metrics (placeholders - would need actual tracking)
            avg_delivery_time = 0.5  # seconds
            delivery_failure_rate = 2.0  # percentage
            
            # User preferences (would need preference tracking)
            users_opted_out = 0
            users_opted_in = 0
            
            # Create or update notification analytics
            notification_analytics, created = NotificationAnalytics.objects.get_or_create(
                date=date,
                defaults={
                    'total_notifications_sent': total_notifications_sent,
                    'push_notifications_sent': push_notifications_sent,
                    'email_notifications_sent': email_notifications_sent,
                    'notifications_opened': notifications_opened,
                    'notifications_clicked': notifications_clicked,
                    'open_rate': open_rate,
                    'click_rate': click_rate,
                    'avg_delivery_time': avg_delivery_time,
                    'delivery_failure_rate': delivery_failure_rate,
                    'users_opted_out': users_opted_out,
                    'users_opted_in': users_opted_in,
                }
            )
            
            if not created:
                notification_analytics.total_notifications_sent = total_notifications_sent
                notification_analytics.push_notifications_sent = push_notifications_sent
                notification_analytics.email_notifications_sent = email_notifications_sent
                notification_analytics.notifications_opened = notifications_opened
                notification_analytics.notifications_clicked = notifications_clicked
                notification_analytics.open_rate = open_rate
                notification_analytics.click_rate = click_rate
                notification_analytics.avg_delivery_time = avg_delivery_time
                notification_analytics.delivery_failure_rate = delivery_failure_rate
                notification_analytics.users_opted_out = users_opted_out
                notification_analytics.users_opted_in = users_opted_in
                notification_analytics.save()
            
            logger.info(f"Collected notification analytics for {date}")
            
        except Exception as e:
            logger.error(f"Failed to collect notification analytics for {date}: {e}")
    
    @staticmethod
    def collect_all_daily_metrics(date=None):
        """Collect all daily metrics in one call"""
        if date is None:
            date = timezone.now().date()
        
        logger.info(f"Starting daily analytics collection for {date}")
        
        AnalyticsCollector.collect_daily_user_engagement(date)
        AnalyticsCollector.collect_daily_platform_metrics(date)
        AnalyticsCollector.collect_daily_matching_analytics(date)
        AnalyticsCollector.collect_daily_notification_analytics(date)
        
        logger.info(f"Completed daily analytics collection for {date}")


class AnalyticsReporter:
    """Service for generating analytics reports"""
    
    @staticmethod
    def get_platform_overview(days=30):
        """Get platform overview for the last N days"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        metrics = PlatformMetric.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        if not metrics.exists():
            return None
        
        latest = metrics.last()
        
        return {
            'total_users': latest.total_users,
            'active_users_daily': latest.active_users_daily,
            'active_users_weekly': latest.active_users_weekly,
            'active_users_monthly': latest.active_users_monthly,
            'avg_api_response_time': latest.avg_api_response_time,
            'error_rate': latest.error_rate,
            'daily_metrics': [
                {
                    'date': metric.date.isoformat(),
                    'active_users': metric.active_users_daily,
                    'sessions': metric.total_sessions,
                    'page_views': metric.total_page_views,
                    'new_registrations': metric.new_registrations,
                }
                for metric in metrics
            ]
        }
    
    @staticmethod
    def get_matching_performance(days=30):
        """Get AI matching performance for the last N days"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        analytics = MatchingAnalytics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        if not analytics.exists():
            return None
        
        latest = analytics.last()
        
        return {
            'match_acceptance_rate': latest.match_acceptance_rate,
            'avg_match_score': latest.avg_match_score,
            'avg_matching_time': latest.avg_matching_time,
            'daily_metrics': [
                {
                    'date': analytic.date.isoformat(),
                    'total_requests': analytic.total_match_requests,
                    'successful_matches': analytic.successful_matches,
                    'acceptance_rate': analytic.match_acceptance_rate,
                    'avg_score': analytic.avg_match_score,
                }
                for analytic in analytics
            ]
        }
    
    @staticmethod
    def get_notification_performance(days=30):
        """Get notification performance for the last N days"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        analytics = NotificationAnalytics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        if not analytics.exists():
            return None
        
        latest = analytics.last()
        
        return {
            'open_rate': latest.open_rate,
            'click_rate': latest.click_rate,
            'avg_delivery_time': latest.avg_delivery_time,
            'daily_metrics': [
                {
                    'date': analytic.date.isoformat(),
                    'sent': analytic.total_notifications_sent,
                    'opened': analytic.notifications_opened,
                    'clicked': analytic.notifications_clicked,
                    'open_rate': analytic.open_rate,
                    'click_rate': analytic.click_rate,
                }
                for analytic in analytics
            ]
        }
