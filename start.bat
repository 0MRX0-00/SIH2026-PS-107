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

echo [1/4] Checking and clearing any lingering port conflicts (8000, 3000)...
powershell -NoProfile -Command ^
  "$ports = @(8000, 3000); foreach ($p in $ports) { $conns = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue; foreach ($c in $conns) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } }"
echo       Port verification complete.
echo.

echo [2/4] Running Pre-Flight Diagnostics Check...
set PYTHONPATH=%ROOT_DIR%backend
cd /d "%ROOT_DIR%backend"
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" -m app.preflight
) else (
    python -m app.preflight
)
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARNING] Pre-flight check reported warnings or errors. Continuing startup...
)
cd /d "%ROOT_DIR%"
echo.

echo [3/4] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "e-BIS Sahayak - Backend API" cmd /k "cd /d ""%ROOT_DIR%backend"" && set PYTHONPATH=. && (if exist ""venv\Scripts\activate.bat"" call venv\Scripts\activate.bat) && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [4/4] Starting Next.js Frontend on http://localhost:3000 ...
start "e-BIS Sahayak - Frontend Portal" cmd /k "cd /d ""%ROOT_DIR%frontend"" && npm run dev"

echo.
echo Waiting for backend API to initialize...
powershell -NoProfile -Command ^
  "$maxAttempts = 20; $attempt = 0; $ready = $false; while ($attempt -lt $maxAttempts -and -not $ready) { Start-Sleep -Seconds 1; $attempt++; try { $resp = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop; if ($resp.StatusCode -eq 200) { $ready = $true } } catch {} }; if ($ready) { Write-Host ' [SUCCESS] Backend API is live and responding!' -ForegroundColor Green } else { Write-Host ' [INFO] Backend is still launching in background window.' -ForegroundColor Yellow }"

echo.
echo ==============================================================================
echo [SUCCESS] e-BIS Sahayak is ready!
echo.
echo   - Web Portal UI : http://localhost:3000
echo   - Backend API   : http://localhost:8000/api/v1
echo   - Swagger Docs  : http://localhost:8000/docs
echo   - Admin Console : http://localhost:3000/admin
echo.
echo ==============================================================================
echo Opening web portal in default browser...
start http://localhost:3000
