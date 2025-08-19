-- uat_seed.sql
-- Example seed data for UAT environment
INSERT INTO accounts_customuser (email, password, username, first_name, last_name) VALUES
('demo1@example.com', 'pbkdf2_sha256$600000$demo1hash', 'demo1', 'Demo', 'User'),
('demo2@example.com', 'pbkdf2_sha256$600000$demo2hash', 'demo2', 'Test', 'Creator')
ON CONFLICT (email) DO NOTHING;

-- Insert demo notifications
INSERT INTO notifications (user_id, type, payload, read_at, created_at)
SELECT 
    u.id,
    'message_received',
    '{"sender_name": "Test Creator", "message_preview": "Hey! Love your latest work!", "chat_id": "demo-chat-1"}',
    NULL,
    NOW() - INTERVAL '2 hours'
FROM accounts_customuser u WHERE u.email = 'demo1@example.com'
ON CONFLICT DO NOTHING;

INSERT INTO notifications (user_id, type, payload, read_at, created_at)
SELECT 
    u.id,
    'profile_updated',
    '{"field": "bio", "old_value": "Old bio", "new_value": "Updated bio with new projects"}',
    NOW() - INTERVAL '30 minutes',
    NOW() - INTERVAL '1 hour'
FROM accounts_customuser u WHERE u.email = 'demo1@example.com'
ON CONFLICT DO NOTHING;

INSERT INTO notifications (user_id, type, payload, read_at, created_at)
SELECT 
    u.id,
    'user_signed_in',
    '{"device": "Chrome on MacOS", "location": "San Francisco, CA"}',
    NULL,
    NOW() - INTERVAL '10 minutes'
FROM accounts_customuser u WHERE u.email = 'demo2@example.com'
ON CONFLICT DO NOTHING;

-- Insert demo activity feed entries
INSERT INTO activity_feed (user_id, actor_id, action_type, target_type, target_id, metadata, created_at)
SELECT 
    u1.id,
    u2.id,
    'message_sent',
    'chat_thread',
    gen_random_uuid(),
    '{"message_preview": "Thanks for the collaboration invite!", "thread_name": "Project Discussion"}',
    NOW() - INTERVAL '3 hours'
FROM accounts_customuser u1, accounts_customuser u2 
WHERE u1.email = 'demo1@example.com' AND u2.email = 'demo2@example.com'
ON CONFLICT DO NOTHING;

INSERT INTO activity_feed (user_id, actor_id, action_type, target_type, target_id, metadata, created_at)
SELECT 
    u.id,
    u.id,
    'profile_updated',
    'user_profile',
    u.id,
    '{"fields_updated": ["bio", "portfolio"], "portfolio_items_added": 2}',
    NOW() - INTERVAL '1 hour'
FROM accounts_customuser u WHERE u.email = 'demo1@example.com'
ON CONFLICT DO NOTHING;
