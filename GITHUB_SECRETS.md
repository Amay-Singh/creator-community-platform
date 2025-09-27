# GitHub Secrets Configuration

## Required Secrets for UAT Environment

To fix the GitHub UAT deployment errors, add these secrets in your GitHub repository:

**Go to:** `Settings > Secrets and variables > Actions > Repository secrets`

### Database Secrets
```
UAT_DB_URL=your-neon-postgres-connection-string
```

### External Service Secrets (Optional - will gracefully degrade if missing)
```
SENDGRID_API_KEY=your-sendgrid-api-key-starting-with-SG
GA4_MEASUREMENT_ID=your-google-analytics-measurement-id
AGORA_APP_ID=your-agora-app-id
GEMINI_API_KEY=your-google-gemini-api-key
REDIS_URL=your-redis-cloud-connection-string
```

### Security Secrets
```
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,creator-platform-demo.vercel.app
```

## How to Add Secrets

1. Go to your GitHub repository
2. Click `Settings` tab
3. Click `Secrets and variables` > `Actions`
4. Click `New repository secret`
5. Add each secret with the name and value above

## Current Status

The application is configured to work without these secrets (graceful degradation), but adding them will enable full functionality in UAT environment.

**Priority Secrets (add these first):**
1. `UAT_DB_URL` - Required for database connection
2. `SECRET_KEY` - Required for Django security

**Optional Secrets (enhance functionality):**
- All external service keys enable full production features
- Missing secrets will show in logs but won't break the application
