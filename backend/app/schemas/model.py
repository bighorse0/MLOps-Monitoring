from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.models.model import ModelStatus, ModelFramework, ModelType

class ModelBase(BaseModel):
    """Base model schema"""
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    framework: ModelFramework
    model_type: ModelType
    status: ModelStatus = ModelStatus.DRAFT

class ModelCreate(ModelBase):
    """Schema for model creation"""
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    training_config: Optional[Dict[str, Any]] = None
    
    # Performance baseline
    baseline_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    baseline_latency: Optional[float] = Field(None, ge=0.0)  # milliseconds
    baseline_throughput: Optional[float] = Field(None, ge=0.0)  # predictions per second
    
    # Monitoring configuration
    drift_threshold: float = Field(0.05, ge=0.0, le=1.0)
    accuracy_threshold: float = Field(0.8, ge=0.0, le=1.0)
    latency_threshold: float = Field(100.0, ge=0.0)  # milliseconds
    
    # Alert configuration
    alert_channels: List[str] = []
    alert_cooldown: int = Field(900, ge=0)  # seconds
    
    # Compliance and governance
    compliance_tags: List[str] = []
    data_sources: List[str] = []
    model_card: Optional[Dict[str, Any]] = None
    
    # Deployment information
    deployment_environment: Optional[str] = None
    deployment_region: Optional[str] = None
    deployment_url: Optional[str] = None

class ModelUpdate(BaseModel):
    """Schema for model updates"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ModelStatus] = None
    
    # Monitoring configuration
    drift_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    accuracy_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    latency_threshold: Optional[float] = Field(None, ge=0.0)
    
    # Alert configuration
    alert_channels: Optional[List[str]] = None
    alert_cooldown: Optional[int] = Field(None, ge=0)
    
    # Compliance and governance
    compliance_tags: Optional[List[str]] = None
    model_card: Optional[Dict[str, Any]] = None
    
    # Deployment information
    deployment_environment: Optional[str] = None
    deployment_region: Optional[str] = None
    deployment_url: Optional[str] = None

class ModelInDB(ModelBase):
    """Schema for model in database"""
    id: uuid.UUID
    user_id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    
    # Model artifacts and storage
    artifact_path: Optional[str] = None
    artifact_size: Optional[int] = None
    artifact_checksum: Optional[str] = None
    
    # Model configuration
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    training_config: Optional[Dict[str, Any]] = None
    
    # Performance baseline
    baseline_accuracy: Optional[float] = None
    baseline_latency: Optional[float] = None
    baseline_throughput: Optional[float] = None
    
    # Monitoring configuration
    drift_threshold: float = 0.05
    accuracy_threshold: float = 0.8
    latency_threshold: float = 100.0
    
    # Alert configuration
    alert_channels: List[str] = []
    alert_cooldown: int = 900
    
    # Compliance and governance
    compliance_tags: List[str] = []
    data_sources: List[str] = []
    model_card: Optional[Dict[str, Any]] = None
    
    # Deployment information
    deployment_environment: Optional[str] = None
    deployment_region: Optional[str] = None
    deployment_url: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Model(ModelInDB):
    """Schema for model response"""
    pass

class ModelList(BaseModel):
    """Schema for model list response"""
    models: List[Model]
    total: int
    page: int
    size: int
    pages: int

class ModelDeploy(BaseModel):
    """Schema for model deployment"""
    environment: str = Field(..., min_length=1)
    region: Optional[str] = None
    deployment_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class ModelArtifact(BaseModel):
    """Schema for model artifact upload"""
    file_path: str
    file_size: int
    checksum: str
    metadata: Optional[Dict[str, Any]] = None

class ModelPrediction(BaseModel):
    """Schema for model prediction request"""
    input_data: Dict[str, Any]
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ModelPredictionResponse(BaseModel):
    """Schema for model prediction response"""
    prediction: Dict[str, Any]
    confidence_score: Optional[float] = None
    prediction_time: float  # milliseconds
    model_version: str
    request_id: str

class ModelMonitoringConfig(BaseModel):
    """Schema for model monitoring configuration"""
    drift_threshold: float = Field(0.05, ge=0.0, le=1.0)
    accuracy_threshold: float = Field(0.8, ge=0.0, le=1.0)
    latency_threshold: float = Field(100.0, ge=0.0)
    alert_channels: List[str] = []
    alert_cooldown: int = Field(900, ge=0)
    monitoring_enabled: bool = True
    data_quality_checks: bool = True
    business_impact_tracking: bool = False

class ModelCard(BaseModel):
    """Schema for model card information"""
    model_details: Dict[str, Any] = {}
    intended_use: Dict[str, Any] = {}
    factors: Dict[str, Any] = {}
    metrics: Dict[str, Any] = {}
    evaluation_data: Dict[str, Any] = {}
    training_data: Dict[str, Any] = {}
    quantitative_analyses: Dict[str, Any] = {}
    ethical_considerations: Dict[str, Any] = {}
    caveats_and_recommendations: Dict[str, Any] = {}

class ModelVersion(BaseModel):
    """Schema for model version information"""
    version: str
    created_at: datetime
    status: ModelStatus
    description: Optional[str] = None
    performance_metrics: Optional[Dict[str, float]] = None
    artifact_info: Optional[Dict[str, Any]] = None 