@echo off
TITLE e-BIS Sahayak — SIH 2026 Launcher
COLOR 0B

echo ==============================================================================
echo                 e-BIS Sahayak (SIH 2026 - SIH26107)
echo   AI-Powered Intelligent Assistant for Indian Standards ^& BIS Services
echo ==============================================================================
echo.

REM Determine script root directory
set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

echo [1/3] Running Pre-Flight Diagnostics Check...
if exist "%ROOT_DIR%backend\venv\Scripts\python.exe" (
    "%ROOT_DIR%backend\venv\Scripts\python.exe" -m app.demo.check
) else (
    python -m app.demo.check
)
echo.

echo [2/3] Starting FastAPI Backend on http://localhost:8000 ...
start "e-BIS Sahayak - Backend API" cmd /k "cd /d ""%ROOT_DIR%backend"" && if exist ""venv\Scripts\activate.bat"" (call venv\Scripts\activate.bat) && python -m uvicorn app.main:app --reload --port 8000"

echo [3/3] Starting Next.js Frontend on http://localhost:3000 ...
start "e-BIS Sahayak - Frontend Portal" cmd /k "cd /d ""%ROOT_DIR%frontend"" && npm run dev"

echo.
echo ==============================================================================
echo [SUCCESS] e-BIS Sahayak is launching!
echo.
echo   - Web Portal UI : http://localhost:3000
echo   - Backend API   : http://localhost:8000/api/v1
echo   - Swagger Docs  : http://localhost:8000/docs
echo   - Admin Console : http://localhost:3000/admin
echo.
echo Press any key to open the web portal in your default browser...
echo ==============================================================================
pause >nul

start http://localhost:3000
