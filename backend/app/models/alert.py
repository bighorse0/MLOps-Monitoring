from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid

from app.core.database import Base

class AlertSeverity(str, enum.Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, enum.Enum):
    """Alert status"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"

class AlertType(str, enum.Enum):
    """Types of alerts"""
    DRIFT_DETECTED = "drift_detected"
    ACCURACY_DEGRADATION = "accuracy_degradation"
    LATENCY_INCREASE = "latency_increase"
    ERROR_RATE_SPIKE = "error_rate_spike"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    MODEL_FAILURE = "model_failure"
    INFRASTRUCTURE_ISSUE = "infrastructure_issue"
    COMPLIANCE_VIOLATION = "compliance_violation"

class Alert(Base):
    """Model alerts and notifications"""
    
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False, index=True)
    
    # Alert information
    alert_type = Column(Enum(AlertType), nullable=False, index=True)
    severity = Column(Enum(AlertSeverity), nullable=False, index=True)
    status = Column(Enum(AlertStatus), default=AlertStatus.OPEN, nullable=False, index=True)
    
    # Alert details
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    description = Column(Text)
    
    # Threshold and current values
    threshold_value = Column(String(100))
    current_value = Column(String(100))
    metric_value = Column(String(100))
    
    # Alert context
    triggered_at = Column(DateTime(timezone=True), nullable=False, index=True)
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    
    # Assignment and resolution
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Resolution details
    resolution_notes = Column(Text)
    resolution_action = Column(String(255))
    time_to_resolve = Column(Integer)  # minutes
    
    # Notification tracking
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(JSONB, default=[])  # Email, Slack, etc.
    notification_attempts = Column(Integer, default=0)
    
    # Metadata
    metadata = Column(JSONB, default={})
    tags = Column(JSONB, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    model = relationship("Model", back_populates="alerts")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    acknowledged_user = relationship("User", foreign_keys=[acknowledged_by])
    resolved_user = relationship("User", foreign_keys=[resolved_by])
    
    def __repr__(self):
        return f"<Alert(id={self.id}, model_id={self.model_id}, type={self.alert_type}, severity={self.severity})>"
    
    @property
    def is_open(self) -> bool:
        """Check if alert is open"""
        return self.status == AlertStatus.OPEN
    
    @property
    def is_acknowledged(self) -> bool:
        """Check if alert is acknowledged"""
        return self.status == AlertStatus.ACKNOWLEDGED
    
    @property
    def is_resolved(self) -> bool:
        """Check if alert is resolved"""
        return self.status == AlertStatus.RESOLVED
    
    @property
    def is_closed(self) -> bool:
        """Check if alert is closed"""
        return self.status == AlertStatus.CLOSED
    
    @property
    def time_since_triggered(self) -> int:
        """Get time since alert was triggered in minutes"""
        if not self.triggered_at:
            return 0
        
        from datetime import datetime
        now = datetime.utcnow()
        delta = now - self.triggered_at
        return int(delta.total_seconds() / 60)
    
    def acknowledge(self, user_id: uuid.UUID, notes: str = None):
        """Acknowledge the alert"""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_by = user_id
        self.acknowledged_at = func.now()
        if notes:
            self.resolution_notes = notes
    
    def resolve(self, user_id: uuid.UUID, action: str, notes: str = None):
        """Resolve the alert"""
        self.status = AlertStatus.RESOLVED
        self.resolved_by = user_id
        self.resolved_at = func.now()
        self.resolution_action = action
        if notes:
            self.resolution_notes = notes
        
        # Calculate time to resolve
        if self.triggered_at and self.resolved_at:
            delta = self.resolved_at - self.triggered_at
            self.time_to_resolve = int(delta.total_seconds() / 60)
    
    def close(self, user_id: uuid.UUID):
        """Close the alert"""
        self.status = AlertStatus.CLOSED
        self.closed_at = func.now()
    
    def to_dict(self) -> dict:
        """Convert alert to dictionary"""
        return {
            "id": str(self.id),
            "model_id": str(self.model_id),
            "alert_type": self.alert_type,
            "severity": self.severity,
            "status": self.status,
            "title": self.title,
            "message": self.message,
            "description": self.description,
            "threshold_value": self.threshold_value,
            "current_value": self.current_value,
            "metric_value": self.metric_value,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "assigned_to": str(self.assigned_to) if self.assigned_to else None,
            "acknowledged_by": str(self.acknowledged_by) if self.acknowledged_by else None,
            "resolved_by": str(self.resolved_by) if self.resolved_by else None,
            "resolution_notes": self.resolution_notes,
            "resolution_action": self.resolution_action,
            "time_to_resolve": self.time_to_resolve,
            "notification_sent": self.notification_sent,
            "notification_channels": self.notification_channels,
            "notification_attempts": self.notification_attempts,
            "metadata": self.metadata,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "time_since_triggered": self.time_since_triggered
        } 