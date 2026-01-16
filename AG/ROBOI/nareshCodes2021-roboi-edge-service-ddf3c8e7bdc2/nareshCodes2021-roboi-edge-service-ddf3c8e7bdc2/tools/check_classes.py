
from ultralytics import YOLO
import sys

try:
    model = YOLO("models/exports/yolo8n_fight.pt")
    print("Class Names:", model.names)
except Exception as e:
    print(e)
