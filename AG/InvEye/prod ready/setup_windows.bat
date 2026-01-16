@echo off
REM ============================================================
REM InvEye Petrol Pump Analytics - One-Click Setup (Windows)
REM ============================================================
echo.
echo ========================================
echo  InvEye Petrol Pump - Quick Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Install Python 3.8+ first.
    pause
    exit /b 1
)

echo [1/5] Creating directories...
if not exist "models" mkdir models
if not exist "face_database" mkdir face_database
if not exist "incidents" mkdir incidents
if not exist "logs" mkdir logs

echo [2/5] Installing dependencies...
pip install -q ultralytics>=8.3.0 opencv-python numpy pyyaml

echo [3/5] Installing face recognition (optional)...
pip install -q insightface onnxruntime-gpu 2>nul || pip install -q insightface onnxruntime

echo [4/5] Downloading models...
if not exist "models\yolov11n-face.pt" (
    echo Downloading face detection model...
    curl -L -o models/yolov11n-face.pt https://github.com/YapaLab/yolo-face/releases/download/v0.0.0/yolov11n-face.pt
)

if not exist "models\yolov11n.pt" (
    echo Downloading object detection model...
    curl -L -o models/yolov11n.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt
)

echo [5/5] Setup complete!
echo.
echo ========================================
echo  Quick Test Commands:
echo ========================================
echo.
echo   Test with webcam:
echo     python petrol_pump_analytics.py --test
echo.
echo   Register employee face:
echo     python petrol_pump_analytics.py --register "John Doe" photo.jpg
echo.
echo   Run with RTSP cameras:
echo     python petrol_pump_analytics.py --config petrol_pump_config.yaml
echo.
echo   Output JSON will be saved to: analytics_output.json
echo.
echo ========================================

pause
