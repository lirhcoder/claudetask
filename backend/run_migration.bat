@echo off
chcp 65001 > nul
echo ============================================
echo     ClaudeTask GitHub Style Migration Tool
echo ============================================
echo.
echo This script will migrate your system to GitHub-style architecture
echo.
echo Migration includes:
echo   - Projects to Repositories
echo   - Tasks to Branches  
echo   - Old API to New API (backward compatible)
echo.
echo Press any key to start migration, or Ctrl+C to cancel...
pause > nul

python migrate_to_github.py

echo.
echo Migration completed! Please restart the backend service.
pause