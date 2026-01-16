@echo off
REM InvEye Retail Dashboard - Quick Start Script
REM This script starts a local web server for the dashboard

echo ========================================
echo InvEye Retail Analytics Dashboard
echo ========================================
echo.
echo Starting local web server...
echo.

REM Try Python 3 first
where python >nul 2>&1
if %errorlevel% == 0 (
    echo Using Python HTTP Server
    echo Dashboard will be available at: http://localhost:8000
    echo.
    echo Press Ctrl+C to stop the server
    echo.
    python -m http.server 8000
    goto :end
)

REM Try Node.js http-server
where http-server >nul 2>&1
if %errorlevel% == 0 (
    echo Using Node.js HTTP Server
    echo Dashboard will be available at: http://localhost:8000
    echo.
    echo Press Ctrl+C to stop the server
    echo.
    http-server -p 8000
    goto :end
)

REM If neither is available, show error
echo ERROR: No web server found!
echo.
echo Please install either Python or Node.js:
echo - Python: https://www.python.org/downloads/
echo - Node.js: https://nodejs.org/
echo.
echo Alternatively, just open index.html directly in your browser.
echo.
pause
goto :end

:end
