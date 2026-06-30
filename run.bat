@echo off
REM Next Gen Agent — one-click session launcher.
REM Sets up the venv on first run (or after dependency changes), then starts the agent.

setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [run.bat] No venv found - creating one and installing dependencies...
    python -m venv .venv
    if errorlevel 1 (
        echo [run.bat] ERROR: failed to create venv. Is Python installed and on PATH?
        pause
        exit /b 1
    )
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [run.bat] ERROR: dependency installation failed.
        pause
        exit /b 1
    )
)

if not exist ".env" (
    echo [run.bat] WARNING: .env not found - the agent will run with stub subagents
    echo [run.bat]          ^(no DEEPSEEK_API_KEY^). Create .env with DEEPSEEK_API_KEY=... for real LLM calls.
)

echo [run.bat] Starting Next Gen Agent...
".venv\Scripts\python.exe" -m src.main

set EXITCODE=%ERRORLEVEL%
echo.
echo [run.bat] Agent exited with code %EXITCODE%.
pause
exit /b %EXITCODE%
