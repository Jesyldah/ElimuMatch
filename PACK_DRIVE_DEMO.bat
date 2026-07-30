@echo off
REM Build a Google Drive–friendly demo zip (HTML + docs + local server bits).
cd /d "%~dp0"
set OUT=ElimuMatch_Capstone_Demo
if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%OUT%"
mkdir "%OUT%\03_Demos"
mkdir "%OUT%\01_Docs"

copy /Y START_HERE.txt "%OUT%\00_START_HERE.txt" >nul
copy /Y START_HERE.md "%OUT%\00_START_HERE.md" >nul
copy /Y README.md "%OUT%\00_README.md" >nul
copy /Y CONCEPT_EXPLORATION_ANSWERS.md "%OUT%\01_Docs\" >nul
copy /Y Concept_Exploration_Answers_ElimuMatch.docx "%OUT%\01_Docs\" >nul
copy /Y DATA_AND_LIMITATIONS.md "%OUT%\01_Docs\" >nul
copy /Y COST_BENEFIT_ANALYSIS.md "%OUT%\01_Docs\" >nul

copy /Y index.html "%OUT%\03_Demos\" >nul
copy /Y dashboard.html "%OUT%\03_Demos\" >nul
copy /Y ops_dashboard.html "%OUT%\03_Demos\" >nul
copy /Y sponsor_portal.html "%OUT%\03_Demos\" >nul
copy /Y modeling_gallery.html "%OUT%\03_Demos\" >nul
copy /Y OPEN_DEMO.bat "%OUT%\03_Demos\" >nul

xcopy /E /I /Y db "%OUT%\03_Demos\db" >nul
if exist "%OUT%\03_Demos\db\__pycache__" rmdir /s /q "%OUT%\03_Demos\db\__pycache__"

echo.
echo ============================================================
echo Folder ready: %OUT%
echo.
echo Reviewers should open FIRST:
echo   %OUT%\00_START_HERE.txt
echo Then open:
echo   %OUT%\03_Demos\index.html
echo ============================================================
echo Zip that folder and upload to Google Drive.
pause
