import os
import time
import json
import logging
import datetime
from logging.handlers import RotatingFileHandler

# --- PATHS ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "data", "logs")
DETECTION_LOG_FILE = os.path.join(LOG_DIR, "detection_log.json")
APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

class JSONLogger:
    """Handles appending detection events and metrics to a newline-delimited JSON file with rotation."""
    
    _logger = None

    @classmethod
    def _get_logger(cls):
        if cls._logger is None:
            cls._logger = logging.getLogger("detection-json")
            cls._logger.setLevel(logging.INFO)
            cls._logger.propagate = False # Don't send to root logger
            
            # Rotating File Handler for JSON logs
            # 10MB limit, keep 5 backups
            handler = RotatingFileHandler(DETECTION_LOG_FILE, maxBytes=10*1024*1024, backupCount=5)
            # Use a formatter that just outputs the message (which will be JSON)
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            cls._logger.addHandler(handler)
        return cls._logger

    @staticmethod
    def write_log(data):
        try:
            logger = JSONLogger._get_logger()
            # Convert data to compact JSON string without newlines within the object
            json_line = json.dumps(data, separators=(',', ':'))
            logger.info(json_line)
        except Exception as e:
            get_app_logger().error(f"Failed to write JSON log: {e}")

def get_app_logger(name="roboi-edge"):
    """Returns a standard Python logger that writes to console and file."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console Handler
        c_handler = logging.StreamHandler()
        c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_format.converter = time.gmtime # Use UTC
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)
        
        # File Handler (Rotating)
        f_handler = RotatingFileHandler(APP_LOG_FILE, maxBytes=10*1024*1024, backupCount=5)
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_format.converter = time.gmtime # Use UTC
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)
        
    return logger
