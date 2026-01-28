@echo off
echo Starting TravelGenie Database API Server...
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo.
    echo Please create a .env file with your Supabase credentials.
    echo You can copy .env.example to .env and fill in your values:
    echo   copy .env.example .env
    echo.
    echo Then edit .env with your Supabase credentials from:
    echo   https://supabase.com/dashboard → Settings → API
    echo.
    pause
    exit /b 1
)

REM Check if Python dependencies are installed
python -c "import supabase, fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo Starting server on port 8001...
echo.
python api.py

