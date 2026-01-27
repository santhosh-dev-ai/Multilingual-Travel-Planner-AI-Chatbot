@echo off
echo Starting TravelGenie Backend API Server...
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo.
    echo Please create a .env file with your API keys.
    echo Example .env content:
    echo   GROQ_API_KEY=your_groq_api_key_here
    echo   WEATHER_API_KEY=your_weather_api_key_here
    echo.
    pause
    exit /b 1
)

REM Check if Python dependencies are installed
python -c "import fastapi, uvicorn, httpx, pydantic" 2>nul
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo Starting FastAPI server on port 8000...
echo.
echo Backend API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload