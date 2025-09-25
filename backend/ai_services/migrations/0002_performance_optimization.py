# Generated for AI services performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_services', '0001_initial'),
    ]

    operations = [
        # Add database indexes for AI services performance
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_creator_profiles_user_skills ON ai_services_creatorprofile(user_id, skills);",
            reverse_sql="DROP INDEX IF EXISTS idx_creator_profiles_user_skills;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_creator_profiles_location ON ai_services_creatorprofile USING GIN(location);",
            reverse_sql="DROP INDEX IF EXISTS idx_creator_profiles_location;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matching_results_user_score ON ai_services_matchingresult(user_id, match_score DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_matching_results_user_score;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matching_results_created_at ON ai_services_matchingresult(created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_matching_results_created_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_search_queries_user_created_at ON ai_services_searchquery(user_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_search_queries_user_created_at;"
        ),
    ]
