@echo off
TITLE e-BIS Sahayak — Auto-Start on Windows Boot Setup
COLOR 0A

echo ==============================================================================
echo        e-BIS Sahayak — Configure Automatic Startup on Windows Boot
echo ==============================================================================
echo.

set ROOT_DIR=%~dp0
set TARGET_SCRIPT=%ROOT_DIR%start.bat

powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; $startupPath = [System.Environment]::GetFolderPath('Startup'); $shortcutPath = Join-Path $startupPath 'eBIS-Sahayak.lnk'; $shortcut = $ws.CreateShortcut($shortcutPath); $shortcut.TargetPath = '%TARGET_SCRIPT%'; $shortcut.WorkingDirectory = '%ROOT_DIR%'; $shortcut.Description = 'e-BIS Sahayak Automated Startup'; $shortcut.Save(); Write-Host ' [SUCCESS] Auto-start shortcut installed to Windows Startup folder:' -ForegroundColor Green; Write-Host \"           $shortcutPath\" -ForegroundColor Cyan"

echo.
echo e-BIS Sahayak will now automatically start every time you turn on or restart your laptop!
echo.
echo To remove auto-start at any time, run 'remove_autostart.bat'.
echo.
pause
