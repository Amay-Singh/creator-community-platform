-- V0002: Add notifications and activity feed tables
-- Phase 2: Notifications + Activity Feed system

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}',
    read_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Foreign key constraint (assumes users table exists)
    CONSTRAINT fk_notifications_user_id 
        FOREIGN KEY (user_id) REFERENCES accounts_customuser(id) ON DELETE CASCADE
);

-- Create indexes for optimal query performance
CREATE INDEX IF NOT EXISTS idx_notifications_user_read 
    ON notifications (user_id, read_at);
    
CREATE INDEX IF NOT EXISTS idx_notifications_user_created 
    ON notifications (user_id, created_at DESC);

-- Create activity_feed table for personal feed events
CREATE TABLE IF NOT EXISTS activity_feed (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    actor_id UUID NULL,
    action_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50) NULL,
    target_id UUID NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Foreign key constraints
    CONSTRAINT fk_activity_feed_user_id 
        FOREIGN KEY (user_id) REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    CONSTRAINT fk_activity_feed_actor_id 
        FOREIGN KEY (actor_id) REFERENCES accounts_customuser(id) ON DELETE SET NULL
);

-- Create indexes for activity feed
CREATE INDEX IF NOT EXISTS idx_activity_feed_user_created 
    ON activity_feed (user_id, created_at DESC);
    
CREATE INDEX IF NOT EXISTS idx_activity_feed_actor_created 
    ON activity_feed (actor_id, created_at DESC);

-- Add notification types enum for validation (optional)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'notification_type') THEN
        CREATE TYPE notification_type AS ENUM (
            'user_signed_in',
            'profile_updated', 
            'message_received',
            'profile_followed',
            'collaboration_invite',
            'system_announcement'
        );
    END IF;
END $$;

-- Add activity types enum for validation (optional)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'activity_type') THEN
        CREATE TYPE activity_type AS ENUM (
            'profile_created',
            'profile_updated',
            'message_sent',
            'collaboration_joined',
            'content_generated',
            'profile_followed'
        );
    END IF;
END $$;
