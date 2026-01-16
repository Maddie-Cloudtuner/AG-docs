"""
Configuration module for ML Inference
Loads settings from environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

class Config:
    """Configuration settings"""
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'cloudtuner_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    EXCEL_FILE_PATH = Path(os.getenv('EXCEL_FILE_PATH', '../cloud_resource_tags_complete 1.xlsx'))
    SQL_OUTPUT_PATH = Path(os.getenv('SQL_OUTPUT_PATH', '../cloud_resource_tags_from_excel.sql'))
    
    # ML Settings
    ML_CONFIDENCE_AUTO_APPLY = float(os.getenv('ML_CONFIDENCE_AUTO_APPLY_THRESHOLD', 0.90))
    ML_CONFIDENCE_REVIEW = float(os.getenv('ML_CONFIDENCE_REVIEW_THRESHOLD', 0.70))
    ML_CACHE_ENABLED = os.getenv('ML_CACHE_ENABLED', 'true').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'ml_inference.log')
    
    @classmethod
    def get_db_connection_string(cls):
        """Get PostgreSQL connection string"""
        return f"host={cls.DB_HOST} port={cls.DB_PORT} dbname={cls.DB_NAME} user={cls.DB_USER} password={cls.DB_PASSWORD}"
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.DB_NAME:
            errors.append("DB_NAME is required")
        if not cls.DB_USER:
            errors.append("DB_USER is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True

# Validate on import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️  Configuration warning: {e}")
    print("Using default values. Create .env file for custom configuration.")
