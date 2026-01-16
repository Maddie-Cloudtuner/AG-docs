"""
Production-ready configuration with environment variable support
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # ===========================
    # DATABASE
    # ===========================
    database_url: str = "postgresql://postgres:postgres@postgres:5432/virtual_tagging"
    
    # ===========================
    # API
    # ===========================
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # ===========================
    # ENVIRONMENT
    # ===========================
    environment: str = "development"  # development, staging, production
    debug: bool = True
    
    # ===========================
    # ML & AUTO-TAGGING
    # ===========================
    ml_model_version: str = "v1.0"
    auto_apply_threshold: float = 0.90
    manual_review_threshold: float = 0.70
    
    # Tag normalization patterns
    environment_patterns: dict = {
        "production": ["prod", "prd", "production"],
        "development": ["dev", "develop", "development"],
        "staging": ["stg", "stage", "staging"],
        "test": ["test", "testing", "qa"]
    }
    
    team_patterns: dict = {
        "frontend": ["frontend", "fe", "ui", "web"],
        "backend": ["backend", "be", "api", "server"],
        "devops": ["devops", "ops", "infra", "platform"],
        "ml": ["ml", "ai", "data-science", "analytics"]
    }
    
    # ===========================
    # SCHEDULER
    # ===========================
    enable_scheduler: bool = True
    discovery_interval: str = "*/2"  # Cron format: every 2 minutes
    reevaluation_interval: str = "0"  # Every hour at minute 0
    
    # ===========================
    # CORS
    # ===========================
    cors_origins: str = "*"  # Comma-separated list or "*" for all
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into list"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # ===========================
    # LOGGING
    # ===========================
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # ===========================
    # CLOUD PROVIDERS (Future)
    # ===========================
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    
    gcp_project_id: str = ""
    google_application_credentials: str = ""
    
    azure_subscription_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""
    azure_tenant_id: str = ""
    
    # ===========================
    # SECURITY (Future)
    # ===========================
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
