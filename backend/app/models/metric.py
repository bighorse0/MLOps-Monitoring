from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid

from app.core.database import Base

class MetricType(str, enum.Enum):
    """Types of model metrics"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    DRIFT_SCORE = "drift_score"
    DATA_QUALITY = "data_quality"
    BUSINESS_IMPACT = "business_impact"

class DriftType(str, enum.Enum):
    """Types of data drift"""
    COVARIATE_DRIFT = "covariate_drift"
    LABEL_DRIFT = "label_drift"
    CONCEPT_DRIFT = "concept_drift"
    FEATURE_DRIFT = "feature_drift"

class ModelMetric(Base):
    """Time-series model performance metrics"""
    
    __tablename__ = "model_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False, index=True)
    
    # Metric information
    metric_type = Column(Enum(MetricType), nullable=False, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Additional context
    window_size = Column(Integer)  # Time window in seconds
    sample_size = Column(Integer)  # Number of samples used for calculation
    
    # Drift detection specific fields
    drift_type = Column(Enum(DriftType))
    drift_threshold = Column(Float)
    is_drift_detected = Column(String(10))  # "true", "false", "unknown"
    
    # Metadata and context
    metadata = Column(JSONB, default={})  # Additional context
    tags = Column(JSONB, default=[])  # Custom tags for filtering
    
    # Data quality metrics
    missing_values_pct = Column(Float)
    outlier_pct = Column(Float)
    data_freshness_hours = Column(Float)
    
    # Business impact metrics
    revenue_impact = Column(Float)  # Dollar amount
    customer_satisfaction = Column(Float)  # 0-1 scale
    business_kpi = Column(JSONB)  # Custom business KPIs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    model = relationship("Model", back_populates="metrics")
    
    def __repr__(self):
        return f"<ModelMetric(id={self.id}, model_id={self.model_id}, type={self.metric_type}, value={self.value})>"
    
    @property
    def is_alert_threshold_exceeded(self) -> bool:
        """Check if metric exceeds alert threshold"""
        if not self.model:
            return False
        
        config = self.model.get_monitoring_config()
        
        if self.metric_type == MetricType.ACCURACY:
            return self.value < config.get("accuracy_threshold", 0.8)
        elif self.metric_type == MetricType.LATENCY:
            return self.value > config.get("latency_threshold", 100.0)
        elif self.metric_type == MetricType.DRIFT_SCORE:
            return self.value > config.get("drift_threshold", 0.05)
        
        return False
    
    def to_dict(self) -> dict:
        """Convert metric to dictionary"""
        return {
            "id": str(self.id),
            "model_id": str(self.model_id),
            "metric_type": self.metric_type,
            "value": self.value,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "window_size": self.window_size,
            "sample_size": self.sample_size,
            "drift_type": self.drift_type,
            "drift_threshold": self.drift_threshold,
            "is_drift_detected": self.is_drift_detected,
            "metadata": self.metadata,
            "tags": self.tags,
            "missing_values_pct": self.missing_values_pct,
            "outlier_pct": self.outlier_pct,
            "data_freshness_hours": self.data_freshness_hours,
            "revenue_impact": self.revenue_impact,
            "customer_satisfaction": self.customer_satisfaction,
            "business_kpi": self.business_kpi,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ModelPrediction(Base):
    """Individual model predictions for detailed analysis"""
    
    __tablename__ = "model_predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False, index=True)
    
    # Prediction details
    input_data = Column(JSONB, nullable=False)  # Input features
    prediction = Column(JSONB, nullable=False)  # Model output
    ground_truth = Column(JSONB)  # Actual value (if available)
    
    # Performance metrics
    prediction_time = Column(Float)  # milliseconds
    confidence_score = Column(Float)  # Model confidence
    is_correct = Column(String(10))  # "true", "false", "unknown"
    
    # Context
    session_id = Column(String(255), index=True)  # User session
    request_id = Column(String(255), index=True)  # Unique request ID
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Metadata
    metadata = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ModelPrediction(id={self.id}, model_id={self.model_id}, timestamp={self.timestamp})>"
    
    def calculate_accuracy(self) -> float:
        """Calculate prediction accuracy"""
        if self.is_correct == "true":
            return 1.0
        elif self.is_correct == "false":
            return 0.0
        else:
            return None  # Unknown 