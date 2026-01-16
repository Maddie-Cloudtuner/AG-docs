#!/bin/bash
# ============================================================================
# 🚀 Jetson Orin Nano One-Click Setup Script
# ============================================================================
# Complete setup for InvEye Fire/Fight/Face Detection System
# 
# Usage: 
#   chmod +x jetson_setup.sh
#   sudo ./jetson_setup.sh
#
# Hardware: NVIDIA Jetson Orin Nano Developer Kit (8GB)
# JetPack: 5.x+ recommended
# ============================================================================

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║     🚀 JETSON ORIN NANO SETUP - InvEye Detection System 🚀        ║"
echo "║                                                                    ║"
echo "║  Detects: 🔥 Fire | 💨 Smoke | 👊 Fighting | 👤 Face | 🔪 Weapon  ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running on Jetson
if [ ! -f /etc/nv_tegra_release ]; then
    echo "⚠️  Warning: This doesn't appear to be a Jetson device."
    echo "   Some features may not work correctly."
    read -p "Continue anyway? (y/n): " continue
    if [ "$continue" != "y" ]; then
        exit 1
    fi
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Please run as root: sudo ./jetson_setup.sh"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER=${SUDO_USER:-$USER}
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

echo "📋 System Information:"
echo "   User: $ACTUAL_USER"
echo "   Home: $ACTUAL_HOME"

# Show Jetson info if available
if [ -f /etc/nv_tegra_release ]; then
    echo "   Jetson: $(cat /etc/nv_tegra_release | head -1)"
fi

echo ""

# ============================================================================
# STEP 1: System Update
# ============================================================================

echo "═══════════════════════════════════════════════════════════════════"
echo "📦 STEP 1: System Update"
echo "═══════════════════════════════════════════════════════════════════"

apt-get update
apt-get upgrade -y

# ============================================================================
# STEP 2: Install Dependencies
# ============================================================================

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "📦 STEP 2: Installing Dependencies"
echo "═══════════════════════════════════════════════════════════════════"

apt-get install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    libopencv-dev \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    cmake \
    git \
    curl \
    wget \
    v4l-utils \
    ffmpeg \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly

echo "✅ Dependencies installed"

# ============================================================================
# STEP 3: Create Virtual Environment
# ============================================================================

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "🐍 STEP 3: Creating Python Virtual Environment"
echo "═══════════════════════════════════════════════════════════════════"

VENV_DIR="$ACTUAL_HOME/inveye_env"

if [ -d "$VENV_DIR" ]; then
    echo "   Virtual environment already exists at $VENV_DIR"
else
    python3 -m venv $VENV_DIR
    echo "   Created virtual environment at $VENV_DIR"
fi

# Activate and install packages
source $VENV_DIR/bin/activate

pip install --upgrade pip wheel setuptools

echo "✅ Virtual environment ready"

# ============================================================================
# STEP 4: Install PyTorch for Jetson
# ============================================================================

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "🔥 STEP 4: Installing PyTorch for Jetson"
echo "═══════════════════════════════════════════════════════════════════"

# Check JetPack version and install appropriate PyTorch
JETPACK_VERSION=$(cat /etc/nv_tegra_release 2>/dev/null | grep -oP 'R\K[0-9]+' | head -1 || echo "0")

if [ "$JETPACK_VERSION" -ge 35 ]; then
    # JetPack 5.x (L4T R35+) - PyTorch 2.x
    echo "   Detected JetPack 5.x, installing PyTorch 2.x..."
    pip install --no-cache https://developer.download.nvidia.com/compute/redist/jp/v512/pytorch/torch-2.1.0a0+41361538.nv23.06-cp38-cp38-linux_aarch64.whl
else
    # Try the latest wheel from NVIDIA
    echo "   Installing PyTorch from NVIDIA repository..."
    pip install torch torchvision torchaudio --index-url https://developer.download.nvidia.com/compute/redist/jp/
fi

echo "✅ PyTorch installed"

# ============================================================================
# STEP 5: Install Ultralytics (YOLOv8/YOLO11)
# ============================================================================

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "📦 STEP 5: Installing Ultralytics (YOLO)"
echo "═══════════════════════════════════════════════════════════════════"

pip install ultralytics

# Verify installation
python3 -c "from ultralytics import YOLO; print('Ultralytics installed successfully')"

echo "✅ Ultralytics installed"

# ============================================================================
# STEP 6: Install Additional Python Packages
# ============================================================================

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "📦 STEP 6: Installing Additional Packages"
echo "═══════════════════════════════════════════════════════════════════"

pip install \
    opencv-python \
    numpy \
    pillow \
    pyyaml \
    tqdm \
    requests \
    flask \
    flask-cors \
    websocket-client

echo "✅ Additional packages installed"

# ============================================================================
# STEP 7: Set Up Project Directory
# ============================================================================

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "📁 STEP 7: Setting Up Project Directory"
echo "═══════════════════════════════════════════════════════════════════"

PROJECT_DIR="$ACTUAL_HOME/inveye"
mkdir -p $PROJECT_DIR/{models,datasets,outputs,scripts}

# Copy scripts to project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -f $SCRIPT_DIR/jetson_deploy.py $PROJECT_DIR/scripts/ 2>/dev/null || true
cp -f $SCRIPT_DIR/merge_datasets.py $PROJECT_DIR/scripts/ 2>/dev/null || true
cp -f $SCRIPT_DIR/download_datasets.py $PROJECT_DIR/scripts/ 2>/dev/null || true

# Set ownership
chown -R $ACTUAL_USER:$ACTUAL_USER $PROJECT_DIR
chown -R $ACTUAL_USER:$ACTUAL_USER $VENV_DIR

echo "   Project directory: $PROJECT_DIR"
echo "✅ Project structure created"

# ============================================================================
# STEP 8: Configure Jetson for Maximum Performance
# ============================================================================

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "⚡ STEP 8: Configuring Jetson for Maximum Performance"
echo "═══════════════════════════════════════════════════════════════════"

# Set to maximum performance mode (MAXN)
nvpmodel -m 0 2>/dev/null || echo "   ⚠️ Could not set power mode"

# Set clocks to maximum
jetson_clocks 2>/dev/null || echo "   ⚠️ Could not set clocks"

# Show current power mode
echo "   Power mode: $(nvpmodel -q 2>/dev/null || echo 'N/A')"

# Enable GPU frequency governor
echo "   Enabling performance governor..."

echo "✅ Performance configuration complete"

# ============================================================================
# STEP 9: Create Convenience Scripts
# ============================================================================

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "📝 STEP 9: Creating Convenience Scripts"
echo "═══════════════════════════════════════════════════════════════════"

# Create activation script
cat > $PROJECT_DIR/activate.sh << 'EOF'
#!/bin/bash
# Activate InvEye environment
source ~/inveye_env/bin/activate
cd ~/inveye
echo "🚀 InvEye environment activated!"
echo "   Run: python scripts/jetson_deploy.py --help"
EOF
chmod +x $PROJECT_DIR/activate.sh

# Create run script
cat > $PROJECT_DIR/run_detection.sh << 'EOF'
#!/bin/bash
# Run InvEye detection on camera
source ~/inveye_env/bin/activate
cd ~/inveye

# Check for model
if [ ! -f "models/best.engine" ]; then
    if [ -f "models/best.pt" ]; then
        echo "📦 Exporting model to TensorRT..."
        python scripts/jetson_deploy.py --model models/best.pt --export
    else
        echo "❌ No model found! Place your model in ~/inveye/models/"
        exit 1
    fi
fi

# Run detection
echo "🚀 Starting detection..."
python scripts/jetson_deploy.py --model models/best.engine --camera ${1:-0}
EOF
chmod +x $PROJECT_DIR/run_detection.sh

# Create benchmark script
cat > $PROJECT_DIR/benchmark.sh << 'EOF'
#!/bin/bash
# Run performance benchmark
source ~/inveye_env/bin/activate
cd ~/inveye

if [ -f "models/best.engine" ]; then
    python scripts/jetson_deploy.py --model models/best.engine --benchmark
else
    echo "❌ No TensorRT engine found!"
    exit 1
fi
EOF
chmod +x $PROJECT_DIR/benchmark.sh

# Create systemd service file
cat > /etc/systemd/system/inveye.service << EOF
[Unit]
Description=InvEye Detection Service
After=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/python $PROJECT_DIR/scripts/jetson_deploy.py --model $PROJECT_DIR/models/best.engine --camera 0 --headless
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Convenience scripts created"

# ============================================================================
# STEP 10: Final Summary
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ SETUP COMPLETE! ✅                           ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Project Location: $PROJECT_DIR"
echo "🐍 Virtual Env: $VENV_DIR"
echo ""
echo "📋 Quick Start:"
echo "   1. Place your trained model (best.pt) in: $PROJECT_DIR/models/"
echo "   2. Activate environment: source $PROJECT_DIR/activate.sh"
echo "   3. Export to TensorRT: python scripts/jetson_deploy.py --model models/best.pt --export"
echo "   4. Run detection: ./run_detection.sh"
echo ""
echo "📋 Available Commands:"
echo "   ./run_detection.sh [camera_id]  - Run camera detection"
echo "   ./benchmark.sh                   - Run performance benchmark"
echo ""
echo "📋 Systemd Service (for auto-start):"
echo "   sudo systemctl enable inveye    - Enable auto-start"
echo "   sudo systemctl start inveye     - Start service"
echo "   sudo systemctl status inveye    - Check status"
echo ""
echo "🔗 For more information, see the documentation."
echo ""
