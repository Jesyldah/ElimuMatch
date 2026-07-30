@echo off
REM One-click ElimuMatch demo launcher for presentations.
cd /d "%~dp0"
echo Starting ElimuMatch demo server...
echo Keep this window open while you present.
echo.
python db\portal_server.py --open
if errorlevel 1 (
  echo.
  echo If Python failed, try: py db\portal_server.py --open
  pause
)
