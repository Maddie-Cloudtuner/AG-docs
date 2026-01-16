#!/bin/bash
# ============================================================================
# 🔥 👊 👤 Dataset Downloader - Linux/Mac Shell Script
# ============================================================================
# Easy one-click dataset download for Fire, Fight, and Face Detection
# 
# Usage: 
#   chmod +x download_datasets.sh
#   ./download_datasets.sh
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║   🔥 👊 👤 AUTOMATED DATASET DOWNLOADER FOR AI TRAINING 👤 👊 🔥   ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3.8+"
    echo "   Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "   Mac: brew install python3"
    exit 1
fi

# Navigate to script directory
cd "$(dirname "$0")"

# Install dependencies
echo ""
echo "📦 Installing required packages..."
pip3 install roboflow kaggle requests tqdm gdown --quiet

# Check for Roboflow API Key
if [ -z "$ROBOFLOW_API_KEY" ]; then
    echo ""
    echo "⚠️  ROBOFLOW_API_KEY not set!"
    echo "   Get your FREE API key from: https://app.roboflow.com/account/api"
    echo ""
    read -p "Enter your Roboflow API key (or press Enter to skip): " ROBOFLOW_API_KEY
fi

# Show menu
show_menu() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "                         SELECT DOWNLOAD OPTION"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "   [1] Download ALL datasets (Fire + Fight + Face)"
    echo "   [2] Download FIRE/SMOKE datasets only"
    echo "   [3] Download FIGHT/VIOLENCE datasets only"
    echo "   [4] Download FACE DETECTION datasets only"
    echo "   [5] List available datasets (no download)"
    echo "   [6] Exit"
    echo ""
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice (1-6): " choice
    
    case $choice in
        1)
            echo ""
            echo "📥 Downloading ALL datasets..."
            if [ -n "$ROBOFLOW_API_KEY" ]; then
                python3 download_datasets.py --all --roboflow-key "$ROBOFLOW_API_KEY"
            else
                python3 download_datasets.py --all --skip-roboflow
            fi
            ;;
        2)
            echo ""
            echo "🔥 Downloading FIRE/SMOKE datasets..."
            if [ -n "$ROBOFLOW_API_KEY" ]; then
                python3 download_datasets.py --fire --roboflow-key "$ROBOFLOW_API_KEY"
            else
                python3 download_datasets.py --fire --skip-roboflow
            fi
            ;;
        3)
            echo ""
            echo "👊 Downloading FIGHT/VIOLENCE datasets..."
            if [ -n "$ROBOFLOW_API_KEY" ]; then
                python3 download_datasets.py --fight --roboflow-key "$ROBOFLOW_API_KEY"
            else
                python3 download_datasets.py --fight --skip-roboflow
            fi
            ;;
        4)
            echo ""
            echo "👤 Downloading FACE DETECTION datasets..."
            if [ -n "$ROBOFLOW_API_KEY" ]; then
                python3 download_datasets.py --face --roboflow-key "$ROBOFLOW_API_KEY"
            else
                python3 download_datasets.py --face --skip-roboflow
            fi
            ;;
        5)
            echo ""
            python3 download_datasets.py --list
            read -p "Press Enter to continue..."
            ;;
        6)
            echo ""
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            ;;
    esac
    
    if [ "$choice" != "5" ] && [ "$choice" != "6" ]; then
        echo ""
        echo "════════════════════════════════════════════════════════════════════"
        echo "✅ DOWNLOAD COMPLETE!"
        echo "════════════════════════════════════════════════════════════════════"
        echo ""
        echo "📁 Datasets saved to: $(pwd)/datasets"
        echo "📄 Config file: $(pwd)/datasets/combined_dataset.yaml"
        echo ""
        echo "Next steps:"
        echo "   1. Review downloaded datasets"
        echo "   2. Train your model with: yolo train data=datasets/combined_dataset.yaml"
        echo ""
        read -p "Press Enter to continue..."
    fi
done
