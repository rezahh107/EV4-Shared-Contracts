@echo off
setlocal
cd /d "%~dp0"
title EV4 Project Gate Launcher

echo ==========================================
echo       EV4 Project Gate - Local UI
echo ==========================================
echo.

where uv >nul 2>nul
if errorlevel 1 (
    echo [ERROR] uv was not found on PATH.
    echo Install it with:
    echo winget install --id=astral-sh.uv -e
    echo Then close and reopen the terminal.
    pause
    exit /b 1
)

if not exist "pyproject.toml" (
    echo [ERROR] pyproject.toml was not found.
    echo Keep this file in the repository root.
    pause
    exit /b 1
)

echo [1/2] Checking project dependencies...
uv sync --locked --extra dev --extra ui
if errorlevel 1 (
    echo [ERROR] Dependency setup failed.
    pause
    exit /b 1
)

echo.
echo [2/2] Starting EV4 Project Gate...
echo Open the local URL shown below in your browser.
echo Keep this window open. Press Ctrl+C to stop the app.
echo.

uv run --locked python -m ev4_transition.ui.app

set "APP_EXIT=%ERRORLEVEL%"
echo.
if not "%APP_EXIT%"=="0" echo [ERROR] The app stopped with exit code %APP_EXIT%.
if "%APP_EXIT%"=="0" echo EV4 Project Gate has stopped.
pause
exit /b %APP_EXIT%
