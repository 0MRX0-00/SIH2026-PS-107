@echo off
TITLE e-BIS Sahayak — Remove Auto-Start
COLOR 0E

echo ==============================================================================
echo        e-BIS Sahayak — Remove Automatic Startup on Windows Boot
echo ==============================================================================
echo.

powershell -NoProfile -Command ^
  "$startupPath = [System.Environment]::GetFolderPath('Startup'); $shortcutPath = Join-Path $startupPath 'eBIS-Sahayak.lnk'; if (Test-Path $shortcutPath) { Remove-Item $shortcutPath -Force; Write-Host ' [SUCCESS] Auto-start shortcut removed successfully.' -ForegroundColor Green } else { Write-Host ' [INFO] Auto-start shortcut was not present in Startup folder.' -ForegroundColor Yellow }"

echo.
pause
