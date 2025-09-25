# Generated for Phase 5 Guardian Performance Optimization

from django.db import migrations, models
import django.contrib.postgres.indexes


class Migration(migrations.Migration):

    dependencies = [
        ('ai_services', '0004_matchresult_matchhistory_matchfeedback_and_more'),
    ]

    operations = [
        # Add database indexes for vector similarity searches
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS ai_services_creatorprofile_embedding_idx ON ai_services_creatorprofile USING gin(embedding);",
            reverse_sql="DROP INDEX IF EXISTS ai_services_creatorprofile_embedding_idx;"
        ),
        
        # Add composite indexes for common query patterns
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS ai_services_creatorprofile_available_active_idx ON ai_services_creatorprofile(is_available, user_id) WHERE is_available = true;",
            reverse_sql="DROP INDEX IF EXISTS ai_services_creatorprofile_available_active_idx;"
        ),
        
        # Index for matching results queries
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS ai_services_matchresult_user_score_idx ON ai_services_matchresult(user_id, similarity_score DESC, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS ai_services_matchresult_user_score_idx;"
        ),
        
        # Index for search queries
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS ai_services_searchquery_user_created_idx ON ai_services_searchquery(user_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS ai_services_searchquery_user_created_idx;"
        ),
        
        # Partial index for active content generation requests
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS ai_services_contentgen_active_idx ON ai_services_contentgenerationrequest(user_id, created_at DESC) WHERE status = 'processing';",
            reverse_sql="DROP INDEX IF EXISTS ai_services_contentgen_active_idx;"
        ),
        
        # Add foreign key indexes that might be missing
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS ai_services_matchfeedback_result_idx ON ai_services_matchfeedback(match_result_id);",
            reverse_sql="DROP INDEX IF EXISTS ai_services_matchfeedback_result_idx;"
        ),
        
        # Index for collaboration invites (cross-app optimization)
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS collaborations_invite_sender_recipient_idx ON collaborations_newcollaborationinvite(sender_id, recipient_id, status);",
            reverse_sql="DROP INDEX IF EXISTS collaborations_invite_sender_recipient_idx;"
        ),
    ]
