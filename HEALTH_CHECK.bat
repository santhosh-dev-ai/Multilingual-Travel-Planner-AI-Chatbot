@echo off
title TravelGenie - Health Check
color 0B

echo ===============================================
echo    TravelGenie - System Health Check
echo ===============================================
echo.

echo Checking system requirements...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python is not installed or not in PATH
    echo        Please install Python 3.8+ from https://python.org
) else (
    echo [OK] Python is installed
    python --version
)

echo.

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Node.js is not installed or not in PATH
    echo        Please install Node.js 18+ from https://nodejs.org
) else (
    echo [OK] Node.js is installed
    node --version
)

echo.
echo ===============================================
echo Checking configuration files...
echo ===============================================
echo.

REM Check backend .env
if exist "backend\.env" (
    echo [OK] Backend .env file exists
    findstr /C:"GROQ_API_KEY" backend\.env >nul
    if errorlevel 1 (
        echo [WARN] GROQ_API_KEY not found in backend\.env
    ) else (
        echo [OK] GROQ_API_KEY configured
    )
) else (
    echo [FAIL] Backend .env file missing
    echo        Please create backend\.env with your API keys
)

echo.

REM Check frontend .env.local
if exist "frontend\.env.local" (
    echo [OK] Frontend .env.local file exists
) else (
    echo [WARN] Frontend .env.local file missing (will use defaults)
)

echo.
echo ===============================================
echo Checking services...
echo ===============================================
echo.

REM Check if ports are available
netstat -an | findstr :8000 >nul
if not errorlevel 1 (
    echo [INFO] Port 8000 is in use (Backend API might be running)
) else (
    echo [INFO] Port 8000 is available
)

netstat -an | findstr :8001 >nul
if not errorlevel 1 (
    echo [INFO] Port 8001 is in use (Database API might be running)
) else (
    echo [INFO] Port 8001 is available
)

netstat -an | findstr :3000 >nul
if not errorlevel 1 (
    echo [INFO] Port 3000 is in use (Frontend might be running)
) else (
    echo [INFO] Port 3000 is available
)

echo.
echo ===============================================
echo Testing API endpoints (if services are running)...
echo ===============================================
echo.

REM Test backend health
curl -s http://localhost:8000/health >nul 2>&1
if not errorlevel 1 (
    echo [OK] Backend API is responding
) else (
    echo [INFO] Backend API is not running or not responding
)

REM Test database API health
curl -s http://localhost:8001/health >nul 2>&1
if not errorlevel 1 (
    echo [OK] Database API is responding
) else (
    echo [INFO] Database API is not running or not responding
)

echo.
echo ===============================================
echo Health Check Complete
echo ===============================================
echo.
echo If you see any [FAIL] messages above, please fix them before starting the chatbot.
echo.
echo To start the chatbot, run: START_CHATBOT.bat
echo.
pause