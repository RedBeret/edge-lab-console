@echo off
REM EdgeLab Console — Windows dev launcher
REM Starts the FastAPI backend and Vite frontend in separate windows.

echo Starting EdgeLab Console...
echo.

REM Check for Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Install Python 3.12+ and add it to PATH.
    pause
    exit /b 1
)

REM Check for Node
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js not found. Install Node.js 22+ and add it to PATH.
    pause
    exit /b 1
)

echo [1/2] Starting FastAPI backend on http://localhost:8000
start "EdgeLab Backend" cmd /k "cd backend && python -m venv .venv && .venv\Scripts\pip install -r requirements.txt && .venv\Scripts\uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Vite frontend on http://localhost:5173
start "EdgeLab Frontend" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo Both services are starting. Open http://localhost:5173 in your browser.
echo Close the two terminal windows to stop the servers.
