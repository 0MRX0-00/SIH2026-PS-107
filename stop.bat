@echo off
TITLE e-BIS Sahayak — Stop Services
COLOR 0C

echo ==============================================================================
echo                 e-BIS Sahayak — Clean Shutdown Utility
echo ==============================================================================
echo.
echo Stopping services running on ports 8000 (Backend) and 3000 (Frontend)...

powershell -NoProfile -Command ^
  "$ports = @(8000, 3000); foreach ($p in $ports) { $conns = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue; foreach ($c in $conns) { Write-Host \"Stopping process on port $p (PID $($c.OwningProcess))...\"; Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } }"

echo.
echo [DONE] All backend and frontend processes have been stopped cleanly.
echo.
pause
