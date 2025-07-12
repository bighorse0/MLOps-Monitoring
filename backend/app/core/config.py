from typing import List, Optional
from pydantic import BaseSettings, validator
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "MLOps Model Monitoring Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/mlops_monitoring"
    REDIS_URL: str = "redis://localhost:6379"
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = "your-influxdb-token"
    INFLUXDB_ORG: str = "mlops"
    INFLUXDB_BUCKET: str = "model_metrics"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_PREDICTIONS: str = "model_predictions"
    KAFKA_TOPIC_METRICS: str = "model_metrics"
    KAFKA_TOPIC_ALERTS: str = "model_alerts"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Monitoring
    PROMETHEUS_PORT: int = 9090
    GRAFANA_PORT: int = 3001
    
    # Billing
    STRIPE_SECRET_KEY: str = "sk_test_your_stripe_key"
    STRIPE_WEBHOOK_SECRET: str = "whsec_your_webhook_secret"
    
    # Cloud Providers
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    GCP_PROJECT_ID: Optional[str] = None
    GCP_CREDENTIALS_FILE: Optional[str] = None
    
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    
    # Model Monitoring
    DRIFT_DETECTION_THRESHOLD: float = 0.05
    ALERT_COOLDOWN_MINUTES: int = 15
    METRICS_RETENTION_DAYS: int = 90
    
    # Compliance
    GDPR_ENABLED: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('DB_USER', 'user')}:{values.get('DB_PASSWORD', 'password')}@{values.get('DB_HOST', 'localhost')}:{values.get('DB_PORT', '5432')}/{values.get('DB_NAME', 'mlops_monitoring')}"
    
    @validator("REDIS_URL", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"redis://{values.get('REDIS_HOST', 'localhost')}:{values.get('REDIS_PORT', '6379')}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings() 