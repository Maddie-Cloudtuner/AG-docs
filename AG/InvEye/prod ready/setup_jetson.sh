#!/bin/bash
# ============================================================
# InvEye Petrol Pump Analytics - One-Click Setup (Linux/Jetson)
# ============================================================
echo ""
echo "========================================"
echo " InvEye Petrol Pump - Quick Setup"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found! Install Python 3.8+ first."
    exit 1
fi

echo "[1/5] Creating directories..."
mkdir -p models face_database incidents logs

echo "[2/5] Installing dependencies..."
pip3 install -q ultralytics>=8.3.0 opencv-python numpy pyyaml

echo "[3/5] Installing face recognition (optional)..."
pip3 install -q insightface onnxruntime-gpu 2>/dev/null || pip3 install -q insightface onnxruntime

echo "[4/5] Downloading models..."
if [ ! -f "models/yolov11n-face.pt" ]; then
    echo "Downloading face detection model..."
    wget -q --show-progress -O models/yolov11n-face.pt \
        https://github.com/YapaLab/yolo-face/releases/download/v0.0.0/yolov11n-face.pt
fi

if [ ! -f "models/yolov11n.pt" ]; then
    echo "Downloading object detection model..."
    wget -q --show-progress -O models/yolov11n.pt \
        https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt
fi

echo "[5/5] Setup complete!"
echo ""
echo "========================================"
echo " Quick Test Commands:"
echo "========================================"
echo ""
echo "  Test with webcam:"
echo "    python3 petrol_pump_analytics.py --test"
echo ""
echo "  Register employee face:"
echo "    python3 petrol_pump_analytics.py --register 'John Doe' photo.jpg"
echo ""
echo "  Run with RTSP cameras:"
echo "    python3 petrol_pump_analytics.py --config petrol_pump_config.yaml"
echo ""
echo "  Output JSON will be saved to: analytics_output.json"
echo ""
echo "========================================"

# Jetson-specific optimization
if [ -f /etc/nv_tegra_release ]; then
    echo ""
    echo "[JETSON] Detected Jetson device!"
    echo "  For best performance, run:"
    echo "    sudo jetson_clocks"
    echo "    python3 jetson_deploy.py --convert-all"
fi
