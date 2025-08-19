-- uat_seed.sql
-- Example seed data for UAT environment
INSERT INTO users (email, password_hash) VALUES
('demo1@example.com', 'hash1'),
('demo2@example.com', 'hash2')
ON CONFLICT DO NOTHING;

INSERT INTO profiles (user_id, display_name, bio)
SELECT id, 'Demo One', 'UAT demo account' FROM users WHERE email='demo1@example.com'
ON CONFLICT DO NOTHING;
