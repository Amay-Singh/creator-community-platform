# Generated for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_initial'),
    ]

    operations = [
        # Add database indexes for performance optimization
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user_created_at ON notifications_notification(user_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_notifications_user_created_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user_read_at ON notifications_notification(user_id, read_at) WHERE read_at IS NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_notifications_user_read_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_type_created_at ON notifications_notification(notification_type, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_notifications_type_created_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_match_notifications_user_created_at ON notifications_matchnotification(user_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_match_notifications_user_created_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_subscription_user_endpoint ON notifications_notificationsubscription(user_id, endpoint);",
            reverse_sql="DROP INDEX IF EXISTS idx_subscription_user_endpoint;"
        ),
    ]
