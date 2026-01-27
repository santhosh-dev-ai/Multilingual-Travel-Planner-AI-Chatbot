# TravelGenie Chatbot - Troubleshooting Guide

## Quick Start
1. Double-click `START_CHATBOT.bat` to start all services
2. Wait for all services to load (about 30 seconds)
3. Open http://localhost:3000 in your browser

## Common Issues & Solutions

### 1. Chatbot Not Responding / API Errors

**Symptoms:**
- Chat interface loads but bot doesn't respond
- Error messages about API keys
- "Network error" or "Request failed" messages

**Solutions:**
1. **Check API Key Configuration:**
   - Open `backend/.env` file
   - Ensure GROQ_API_KEY is set correctly
   - Get your API key from: https://console.groq.com/keys
   
2. **Verify Backend Server:**
   - Check if backend is running on port 8000
   - Visit http://localhost:8000/health
   - Should return: `{"status": "healthy"}`

3. **Test API Connection:**
   - Visit http://localhost:8000/docs
   - Try the `/api/chat/message` endpoint

### 2. Frontend Not Loading

**Symptoms:**
- Browser shows "This site can't be reached"
- Page doesn't load at localhost:3000

**Solutions:**
1. **Check Node.js Installation:**
   ```cmd
   node --version
   npm --version
   ```
   
2. **Install Dependencies:**
   ```cmd
   cd frontend
   npm install
   npm run dev
   ```

3. **Check Port Availability:**
   - Ensure port 3000 is not used by another app
   - Try: `netstat -an | findstr :3000`

### 3. Backend Server Issues

**Symptoms:**
- Backend fails to start
- Import errors
- Port already in use

**Solutions:**
1. **Install Python Dependencies:**
   ```cmd
   cd backend
   pip install -r requirements.txt
   ```

2. **Check Python Version:**
   ```cmd
   python --version
   ```
   (Requires Python 3.8+)

3. **Kill Existing Processes:**
   ```cmd
   taskkill /f /im python.exe
   ```

### 4. Database API Issues

**Symptoms:**
- Wishlist/Itinerary features not working
- Database connection errors

**Solutions:**
1. **Check Database Server:**
   - Ensure database API runs on port 8001
   - Visit http://localhost:8001/health

2. **Configure Supabase (if using):**
   - Check `database/.env` file
   - Ensure Supabase credentials are correct

### 5. CORS Errors

**Symptoms:**
- Browser console shows CORS errors
- API calls blocked by browser

**Solutions:**
1. **Check Backend CORS Settings:**
   - File: `backend/app/core/config.py`
   - Ensure localhost:3000 is in CORS_ORIGINS

2. **Use Correct API URLs:**
   - Frontend should call localhost:8000/api
   - Check `frontend/.env.local`

## Port Configuration

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000 |
| Database API | 8001 | http://localhost:8001 |

## Environment Files

### backend/.env
```
GROQ_API_KEY=your_groq_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
```

### frontend/.env.local
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_DATABASE_URL=http://localhost:8001/api
```

## Manual Startup (if batch files don't work)

### 1. Start Backend:
```cmd
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Database API:
```cmd
cd database
pip install -r requirements.txt
python api.py
```

### 3. Start Frontend:
```cmd
cd frontend
npm install
npm run dev
```

## Getting Help

1. **Check Console Logs:**
   - Browser Developer Tools (F12)
   - Backend terminal output
   - Frontend terminal output

2. **Test Individual Components:**
   - Backend: http://localhost:8000/docs
   - Database: http://localhost:8001/docs (if available)
   - Frontend: Check browser console

3. **Common Error Messages:**
   - "API key not configured" → Check backend/.env
   - "Network error" → Check if backend is running
   - "CORS error" → Check CORS configuration
   - "Port already in use" → Kill existing processes

## System Requirements

- **Python:** 3.8 or higher
- **Node.js:** 18.0 or higher
- **RAM:** 4GB minimum
- **Disk Space:** 1GB free space
- **Internet:** Required for API calls

## API Key Setup

### Groq API Key:
1. Visit https://console.groq.com/keys
2. Create account and generate API key
3. Add to `backend/.env` as `GROQ_API_KEY=your_key_here`

### Weather API Key (Optional):
1. Visit https://openweathermap.org/api
2. Sign up and get free API key
3. Add to `backend/.env` as `WEATHER_API_KEY=your_key_here`