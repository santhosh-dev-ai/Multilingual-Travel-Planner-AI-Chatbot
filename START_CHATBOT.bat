@echo off
title TravelGenie - AI Travel Chatbot
color 0A

echo ===============================================
echo    TravelGenie - AI Travel Chatbot Setup
echo ===============================================
echo.

echo This script will start all required services:
echo   1. Backend API Server (Port 8000)
echo   2. Database API Server (Port 8001) 
echo   3. Frontend Web App (Port 3000)
echo.

echo IMPORTANT: Make sure you have:
echo   - Python 3.8+ installed
echo   - Node.js 18+ installed  
echo   - Valid API keys in backend/.env
echo.

pause

echo.
echo ===============================================
echo Starting Backend API Server...
echo ===============================================
cd backend
start "Backend API" cmd /k "start_server.bat"
cd ..

echo.
echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo ===============================================
echo Starting Database API Server...
echo ===============================================
cd database
start "Database API" cmd /k "start_server.bat"
cd ..

echo.
echo Waiting 5 seconds for database API to initialize...
timeout /t 5 /nobreak >nul

echo.
echo ===============================================
echo Starting Frontend Web App...
echo ===============================================
cd frontend
start "Frontend" cmd /k "start_frontend.bat"
cd ..

echo.
echo ===============================================
echo All services are starting up!
echo ===============================================
echo.
echo Please wait a moment for all services to fully load.
echo.
echo Once ready, open your browser and go to:
echo   http://localhost:3000
echo.
echo API Documentation available at:
echo   http://localhost:8000/docs
echo.
echo Press any key to exit this window...
pause >nul