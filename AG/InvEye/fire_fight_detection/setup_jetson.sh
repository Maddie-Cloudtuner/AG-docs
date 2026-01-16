#!/bin/bash
# ============================================================
# InvEye Jetson Orin Nano Setup Script
# DeepStream + YOLO11 for Fire & Fight Detection
# ============================================================

set -e

echo "============================================================"
echo "  InvEye Setup for Jetson Orin Nano"
echo "  DeepStream + YOLO11 Multi-Camera Detection"
echo "============================================================"

# Check if running on Jetson
if [ ! -f /etc/nv_tegra_release ]; then
    echo "⚠️  Warning: This script is designed for NVIDIA Jetson devices"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "📦 Step 1: System Update"
echo "------------------------------------------------------------"
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo "📦 Step 2: Install Dependencies"
echo "------------------------------------------------------------"
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    gstreamer1.0-rtsp \
    libgirepository1.0-dev \
    gir1.2-gst-rtsp-server-1.0

echo ""
echo "📦 Step 3: Install Python Packages"
echo "------------------------------------------------------------"
pip3 install --upgrade pip
pip3 install \
    ultralytics \
    pyyaml \
    requests \
    numpy \
    opencv-python \
    PyGObject

echo ""
echo "📦 Step 4: Clone DeepStream-YOLO"
echo "------------------------------------------------------------"
cd ~
if [ ! -d "DeepStream-Yolo" ]; then
    git clone https://github.com/marcoslucianops/DeepStream-Yolo.git
    echo "✅ DeepStream-YOLO cloned"
else
    echo "✓ DeepStream-YOLO already exists"
    cd DeepStream-Yolo && git pull && cd ~
fi

echo ""
echo "📦 Step 5: Setup Ultralytics Export"
echo "------------------------------------------------------------"
cd ~
if [ ! -d "ultralytics" ]; then
    git clone https://github.com/ultralytics/ultralytics.git
fi

# Copy export script
cp ~/DeepStream-Yolo/utils/export_yolo11.py ~/ultralytics/
echo "✅ Export script copied"

echo ""
echo "📦 Step 6: Download YOLO11s Base Model"
echo "------------------------------------------------------------"
cd ~/ultralytics
if [ ! -f "yolo11s.pt" ]; then
    wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11s.pt
    echo "✅ YOLO11s model downloaded"
else
    echo "✓ YOLO11s model already exists"
fi

echo ""
echo "📦 Step 7: Setup InvEye Project"
echo "------------------------------------------------------------"
mkdir -p ~/inveye
cd ~/inveye

# Copy files if source exists
if [ -d "/path/to/fire_fight_detection" ]; then
    cp -r /path/to/fire_fight_detection/* ~/inveye/
fi

echo ""
echo "============================================================"
echo "✅ SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "Next Steps:"
echo ""
echo "1. Fine-tune YOLO11 with fire/fight data (on PC with GPU):"
echo "   python scripts/train.py --model yolo11s.pt --epochs 100"
echo ""
echo "2. Export model to TensorRT (on Jetson):"
echo "   cd ~/ultralytics"
echo "   python export_yolo11.py -w yolo11s_fire_fight.pt --dynamic"
echo ""
echo "3. Copy engine file to InvEye folder:"
echo "   cp yolo11s_fire_fight.engine ~/inveye/"
echo ""
echo "4. Edit camera configuration:"
echo "   nano ~/inveye/cameras.yaml"
echo ""
echo "5. Run InvEye:"
echo "   cd ~/inveye"
echo "   python3 inveye_multi_camera.py --config cameras.yaml"
echo ""
echo "============================================================"
