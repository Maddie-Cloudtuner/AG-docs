# Getting Started: Jetson Orin Nano Setup

This guide will walk you through setting up your NVIDIA Jetson Orin Nano from scratch to run the Roboi Edge Service.

## 1. Hardware & Jetson Linux Installation

Before starting, ensure you have flashed your Jetson Orin Nano with the latest Jetson Linux (JetPack 6.x).

- [Jetson Orin Nano Developer Kit Get Started Guide](https://developer.nvidia.com/embedded/learn/get-started-jetson-orin-nano-devkit)

## 2. Install DeepStream 7.1

DeepStream is the core framework used for accelerated video analytics.

- [DeepStream 7.1 Installation Guide](https://docs.nvidia.com/metropolis/deepstream/7.1/text/DS_Installation.html)

## 3. Machine Learning Setup (Ultralytics & ONNX)

Install the necessary libraries for YOLO inference and GPU acceleration.

- [Ultralytics Jetson Guide & ONNX Runtime GPU Installation](https://docs.ultralytics.com/guides/nvidia-jetson/#install-onnxruntime-gpu)

## 4. DeepStream Configuration for YOLO 11

Follow the official Ultralytics guide to prepare YOLO 11 for DeepStream.

- [YOLO11 DeepStream Configuration](https://docs.ultralytics.com/guides/deepstream-nvidia-jetson/#deepstream-configuration-for-yolo11)
  - **Note:** Follow from **Step 2** onwards.

## 5. Python Environment Setup

Ensure your Python environment is correctly configured to avoid compatibility issues.

### Install DeepStream Python Bindings

Download and install the v1.2.0 Python bindings for DeepStream.

- [DeepStream Python Apps v1.2.0 Releases](https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/releases/tag/v1.2.0)

### Install Project Dependencies

1. Clone this repository:
   ```bash
   git clone <repo-url>
   cd roboi-edge-service
   ```
2. **Crucial:** Ensure `numpy` version is 1.x (DeepStream and other libraries on Jetson may experience issues with numpy 2.x).
   ```bash
   pip install "numpy<2.0.0"
   ```

## 6. Running the Service

Once everything is installed, you can start the service using the provided runner script.

```bash
chmod +x scripts/run_orin.sh
./scripts/run_orin.sh
```

> [!NOTE]
> The `run_orin.sh` script monitors device temperature and automatically manages the service and logging pipeline (Vector).
