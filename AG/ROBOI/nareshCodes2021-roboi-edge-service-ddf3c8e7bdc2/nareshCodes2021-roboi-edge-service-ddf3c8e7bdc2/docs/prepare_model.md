1. python export_yolo11.py \
  -w Fire_best.pt \
  --batch 4 \
  --size 1088 1920 \
  --opset 17

2. /usr/src/tensorrt/bin/trtexec \
  --onnx=/home/invieye/roboi-edge-service/models/exports/roboi_base_14012026.pt.onnx \
  --saveEngine=/home/invieye/roboi-edge-service/models/engines/roboi_base_b4_1080p_fp16.engine \
  --fp16 \
  --shapes=input:4x3x1088x1920 \
  --memPoolSize=workspace:4096 \
  --timingCacheFile=/home/invieye/roboi-edge-service/models/engines/roboi_base.cache
