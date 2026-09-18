@echo off
TITLE e-BIS Sahayak — Test Suite & Benchmark Runner
COLOR 0A

echo ==============================================================================
echo                 e-BIS Sahayak — Automated Test Suite Runner
echo ==============================================================================
echo.

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%backend"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo [1/2] Running 87 Backend Unit & Integration Tests...
python -m pytest -v
echo.

echo [2/2] Running RAG Evaluation Benchmark Runner...
python -m app.evaluation.run
echo.

echo ==============================================================================
echo [COMPLETED] Test execution finished.
echo ==============================================================================
pause
