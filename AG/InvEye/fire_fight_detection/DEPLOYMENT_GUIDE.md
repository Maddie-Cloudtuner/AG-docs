# 🚀 InvEye Deployment Guide
## Jetson Orin Nano Setup After Training

---

## Step 1: Copy Model to Jetson

### From your PC/Mac:
```bash
# Replace <JETSON_IP> with your Jetson's IP address
# Find IP on Jetson with: hostname -I

scp best.pt nvidia@<JETSON_IP>:~/inveye/

# Example:
scp best.pt nvidia@192.168.1.50:~/inveye/
```

### From Google Drive on Jetson:
```bash
# Install gdown
pip3 install gdown

# Copy shareable link from Google Drive and download
gdown "https://drive.google.com/uc?id=YOUR_FILE_ID"
```

### If you're on same network:
```bash
# On Jetson, get IP
hostname -I
# Output: 192.168.1.50

# On your PC
scp /path/to/inveye_yolo11_best.pt nvidia@192.168.1.50:~/inveye/
# Password: nvidia (default)
```

---

## Step 2: SSH into Jetson

```bash
# From your computer
ssh nvidia@<JETSON_IP>

# Default password: nvidia
# Example:
ssh nvidia@192.168.1.50
```

---

## Step 3: Prepare Jetson Environment

```bash
# Navigate to InvEye folder
cd ~/inveye

# Verify model is there
ls -la *.pt

# Install dependencies (if not already done)
pip3 install ultralytics pyyaml requests

# Clone DeepStream-YOLO (if not done)
cd ~
git clone https://github.com/marcoslucianops/DeepStream-Yolo.git
```

---

## Step 4: Export Model to TensorRT

```bash
cd ~/inveye

# Run the export script
python3 export_to_deepstream.py --model best.pt

# OR manually export:
python3 -c "
from ultralytics import YOLO
model = YOLO('best.pt')
model.export(format='engine', half=True, device=0)
"

# This creates: best.engine
```

### Expected Output:
```
🔄 Exporting model...
   Format: TensorRT
   Image Size: 640
   Half Precision: True

✅ Export complete!
   Engine: best.engine
```

---

## Step 5: Configure Cameras

```bash
# Edit camera configuration
nano cameras.yaml
```

### Update with your camera RTSP URLs:
```yaml
cameras:
  - id: cam_entrance
    name: Entrance Camera
    rtsp_url: rtsp://admin:password@192.168.1.101:554/stream1
    
  - id: cam_office1
    name: Office Area 1
    rtsp_url: rtsp://admin:password@192.168.1.102:554/stream1
    
  - id: cam_office2
    name: Office Area 2
    rtsp_url: rtsp://admin:password@192.168.1.103:554/stream1
    
  - id: cam_parking
    name: Parking Area
    rtsp_url: rtsp://admin:password@192.168.1.104:554/stream1
```

### Find your camera RTSP URL:
```bash
# Common RTSP URL formats:
# Hikvision: rtsp://admin:password@IP:554/Streaming/Channels/101
# Dahua: rtsp://admin:password@IP:554/cam/realmonitor?channel=1&subtype=0
# Generic: rtsp://admin:password@IP:554/stream1
```

---

## Step 6: Run Multi-Camera Detection

```bash
cd ~/inveye

# Start detection
python3 inveye_multi_camera.py --config cameras.yaml
```

### Expected Output:
```
╔══════════════════════════════════════════════════════════════╗
║   🔥 InvEye Fire & Fight Detection                          ║
║   DeepStream + YOLO11 Multi-Camera Pipeline                  ║
╚══════════════════════════════════════════════════════════════╝

[InvEye] Initializing with 4 cameras
[InvEye] Creating pipeline...
[InvEye] Pipeline created successfully
[InvEye] Starting pipeline...
[InvEye] Pipeline running. Press Ctrl+C to stop.

🚨 ALERT [FIRE] Camera 2 - Confidence: 0.87
🚨 ALERT [FIGHTING] Camera 0 - Confidence: 0.73
```

---

## Step 7: Run as Background Service (Optional)

```bash
# Create systemd service
sudo nano /etc/systemd/system/inveye.service
```

### Add this content:
```ini
[Unit]
Description=InvEye Multi-Camera Detection
After=network.target

[Service]
Type=simple
User=nvidia
WorkingDirectory=/home/nvidia/inveye
ExecStart=/usr/bin/python3 inveye_multi_camera.py --config cameras.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and start:
```bash
sudo systemctl enable inveye
sudo systemctl start inveye

# Check status
sudo systemctl status inveye

# View logs
journalctl -u inveye -f
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Cannot SSH** | Check Jetson IP: `hostname -I` on Jetson |
| **Model export fails** | Ensure CUDA is working: `nvidia-smi` |
| **Camera not connecting** | Test RTSP in VLC first |
| **Low FPS** | Use smaller model (yolo11n), reduce imgsz |
| **Out of memory** | Reduce batch_size to 2 |
| **No display** | Add `DISPLAY=:0` before command |

---

## Quick Reference Commands

```bash
# Check GPU status
nvidia-smi

# Test single camera
python3 -c "
from ultralytics import YOLO
model = YOLO('best.engine')
results = model('rtsp://admin:pass@192.168.1.101:554/stream1', show=True)
"

# Monitor Jetson performance
sudo tegrastats

# Kill running detection
pkill -f inveye_multi_camera
```

---

*InvEye - AI Eyes That Never Blink*
