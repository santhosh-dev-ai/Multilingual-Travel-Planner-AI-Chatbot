# 🚀 Vercel Deployment Guide

## Frontend Deployment (Vercel)

### 1. Prepare Frontend
```bash
cd frontend
npm install
npm run build
```

### 2. Deploy to Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Login: `vercel login`
3. Deploy: `vercel --prod`

### 3. Environment Variables
Set these in Vercel dashboard:
- `NEXT_PUBLIC_API_URL` - Your backend API URL
- `NEXT_PUBLIC_DATABASE_URL` - Your database API URL

## Backend Deployment Options

### Option 1: Railway
1. Connect GitHub repo
2. Deploy backend folder
3. Add environment variables

### Option 2: Render
1. Connect GitHub repo
2. Deploy as web service
3. Add environment variables

### Option 3: Heroku
1. Create Heroku app
2. Deploy backend folder
3. Add environment variables

## Database Deployment

### Option 1: Supabase (Recommended)
1. Create Supabase project
2. Run schema.sql in SQL editor
3. Get connection URL

### Option 2: Railway PostgreSQL
1. Add PostgreSQL service
2. Run schema.sql
3. Get connection URL

## Required Environment Variables

### Backend (.env)
```
GROQ_API_KEY=your_groq_api_key
WEATHER_API_KEY=your_weather_api_key
DATABASE_URL=your_database_url
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://your-backend.com/api
NEXT_PUBLIC_DATABASE_URL=https://your-database.com/api
```

## Quick Deploy Commands

```bash
# Frontend only (Vercel)
cd frontend && vercel --prod

# Full stack (if using Vercel for all)
vercel --prod
```