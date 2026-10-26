@echo off
REM build_exe.bat – Build Code Agent into a single Windows .exe
REM Requires: pip install pyinstaller openai
REM Run this from the code-agent/ directory.

echo =========================================
echo  Building Code Agent .exe with PyInstaller
echo =========================================

cd /d "%~dp0"

REM Install dependencies first
pip install -r requirements.txt

REM Build single-file windowed executable
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "CodeAgent" ^
    --distpath dist ^
    --workpath build ^
    --specpath build ^
    --add-data "samples;samples" ^
    main.py

echo.
if exist "dist\CodeAgent.exe" (
    echo =========================================
    echo  SUCCESS: dist\CodeAgent.exe is ready!
    echo  Double-click to run - no Python required.
    echo =========================================
) else (
    echo =========================================
    echo  BUILD FAILED - check output above.
    echo =========================================
    exit /b 1
)
