@echo off
echo Starting TravelGenie Frontend...
echo.

REM Check if node_modules exists
if not exist node_modules (
    echo Installing Node.js dependencies...
    npm install
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo Starting Next.js development server...
echo.
echo Frontend will be available at: http://localhost:3000
echo.

npm run dev