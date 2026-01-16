@echo off
echo ================================
echo InvEye Dashboard Launcher
echo ================================
echo.
echo Starting dashboard on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
echo Opening browser in 3 seconds...
echo.

timeout /t 3 /nobreak > nul

REM Try Python 3 first
python --version > nul 2>&1
if %errorlevel% equ 0 (
    echo Using Python HTTP Server...
    start http://localhost:8000
    python -m http.server 8000
    goto :end
)

REM Try Node.js http-server
where http-server > nul 2>&1
if %errorlevel% equ 0 (
    echo Using Node.js HTTP Server...
    start http://localhost:8000
    http-server -p 8000
    goto :end
)

REM Fallback: Just open the HTML file
echo No server found. Opening index.html directly...
start index.html

:end
