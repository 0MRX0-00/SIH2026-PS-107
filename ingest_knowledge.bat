@echo off
TITLE e-BIS Sahayak — Knowledge Base Ingestion
COLOR 0E

echo ==============================================================================
echo                 e-BIS Sahayak — Knowledge Base Ingestion
echo ==============================================================================
echo.

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%backend"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo Ingesting Indian Standards, QCO orders, and registry documents into Qdrant...
python -m app.rag.ingestion
echo.

echo ==============================================================================
echo [COMPLETED] Ingestion process finished.
echo ==============================================================================
pause
