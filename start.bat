@echo off
echo Starting World Cup 2026 Predictor...
start "Backend" cmd /k "cd /d %~dp0backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt -q && uvicorn app.main:app --reload --port 8000"
timeout /t 5 /nobreak >nul
start "Frontend" cmd /k "cd /d %~dp0frontend && npm install && npm run dev"
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause
