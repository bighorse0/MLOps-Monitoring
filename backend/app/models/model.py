from sqlalchemy import Column, String, Boolean, DateTime, Text, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid

from app.core.database import Base

class ModelStatus(str, enum.Enum):
    """Model deployment status"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class ModelFramework(str, enum.Enum):
    """Supported ML frameworks"""
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    SCIKIT_LEARN = "scikit-learn"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    CUSTOM = "custom"

class ModelType(str, enum.Enum):
    """Model types"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    RECOMMENDATION = "recommendation"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"

class Model(Base):
    """ML Model metadata and configuration"""
    
    __tablename__ = "models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    
    # Model metadata
    framework = Column(Enum(ModelFramework), nullable=False)
    model_type = Column(Enum(ModelType), nullable=False)
    status = Column(Enum(ModelStatus), default=ModelStatus.DRAFT, nullable=False)
    
    # Ownership and organization
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), index=True)
    
    # Model artifacts and storage
    artifact_path = Column(String(500))  # Path to model file
    artifact_size = Column(Integer)  # Size in bytes
    artifact_checksum = Column(String(64))  # SHA256 checksum
    
    # Model configuration
    input_schema = Column(JSONB)  # Input feature schema
    output_schema = Column(JSONB)  # Output schema
    hyperparameters = Column(JSONB)  # Model hyperparameters
    training_config = Column(JSONB)  # Training configuration
    
    # Performance baseline
    baseline_accuracy = Column(Float)
    baseline_latency = Column(Float)  # milliseconds
    baseline_throughput = Column(Float)  # predictions per second
    
    # Monitoring configuration
    drift_threshold = Column(Float, default=0.05)
    accuracy_threshold = Column(Float, default=0.8)
    latency_threshold = Column(Float, default=100.0)  # milliseconds
    
    # Alert configuration
    alert_channels = Column(JSONB, default=[])  # Email, Slack, webhook URLs
    alert_cooldown = Column(Integer, default=900)  # seconds
    
    # Compliance and governance
    compliance_tags = Column(JSONB, default=[])  # GDPR, SOX, FDA, etc.
    data_sources = Column(JSONB, default=[])  # Training data sources
    model_card = Column(JSONB)  # Model card information
    
    # Deployment information
    deployment_environment = Column(String(100))  # prod, staging, dev
    deployment_region = Column(String(100))
    deployment_url = Column(String(500))  # Model serving endpoint
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deployed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="models")
    metrics = relationship("ModelMetric", back_populates="model")
    alerts = relationship("Alert", back_populates="model")
    
    def __repr__(self):
        return f"<Model(id={self.id}, name={self.name}, version={self.version})>"
    
    @property
    def is_active(self) -> bool:
        """Check if model is active"""
        return self.status == ModelStatus.ACTIVE
    
    @property
    def full_name(self) -> str:
        """Get full model name with version"""
        return f"{self.name}:{self.version}"
    
    def get_monitoring_config(self) -> dict:
        """Get monitoring configuration"""
        return {
            "drift_threshold": self.drift_threshold,
            "accuracy_threshold": self.accuracy_threshold,
            "latency_threshold": self.latency_threshold,
            "alert_channels": self.alert_channels,
            "alert_cooldown": self.alert_cooldown
        }
    
    def update_status(self, new_status: ModelStatus):
        """Update model status"""
        self.status = new_status
        if new_status == ModelStatus.ACTIVE:
            self.deployed_at = func.now()
    
    def validate_input_schema(self, input_data: dict) -> bool:
        """Validate input data against schema"""
        if not self.input_schema:
            return True
        
        # Basic schema validation
        for field, field_config in self.input_schema.items():
            if field not in input_data:
                if field_config.get("required", False):
                    return False
            else:
                # Type validation
                expected_type = field_config.get("type")
                if expected_type and not isinstance(input_data[field], eval(expected_type)):
                    return False
        
        return True 