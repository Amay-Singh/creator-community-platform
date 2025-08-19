# Online Database Setup Guide

## Quick Setup Options

### Option 1: Supabase (Recommended - Free Tier)
1. Go to [supabase.com](https://supabase.com)
2. Create account and new project
3. Get connection string from Settings > Database
4. Format: `postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres`

### Option 2: Railway (Simple Setup)
1. Go to [railway.app](https://railway.app)
2. Create project and add PostgreSQL service
3. Get DATABASE_URL from Variables tab
4. Format: `postgresql://postgres:[password]@[host]:5432/railway`

### Option 3: Neon (Serverless PostgreSQL)
1. Go to [neon.tech](https://neon.tech)
2. Create database
3. Copy connection string
4. Format: `postgresql://[user]:[password]@[endpoint]/[dbname]`

## Setup Steps

1. **Choose a provider** and create database
2. **Copy the DATABASE_URL** connection string
3. **Create .env file** in backend directory:
   ```
   DATABASE_URL=your_connection_string_here
   SECRET_KEY=your-secret-key
   DEBUG=True
   ```
4. **Run migrations**:
   ```bash
   cd /Users/amays/Desktop/Work/Colab/creator-platform/backend
   python manage.py migrate
   ```
5. **Restart Django server**:
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

## Current Status
- ✅ Django configured for online databases
- ✅ PostgreSQL adapter installed
- ✅ Database URL parsing enabled
- ⏳ Waiting for your DATABASE_URL configuration

## Test Registration
Once configured, your user registrations will be stored in the cloud database instead of local SQLite.
