from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request
import structlog
import time
from typing import Dict, Any

from app.core.config import settings

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

MODEL_PREDICTIONS = Counter(
    'model_predictions_total',
    'Total model predictions',
    ['model_id', 'model_version', 'status']
)

MODEL_DRIFT_SCORE = Gauge(
    'model_drift_score',
    'Model drift detection score',
    ['model_id', 'drift_type']
)

ALERT_COUNT = Counter(
    'alerts_total',
    'Total alerts generated',
    ['model_id', 'alert_type', 'severity']
)

ACTIVE_MODELS = Gauge(
    'active_models',
    'Number of active models being monitored'
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections',
    'Number of active database connections'
)

def setup_monitoring():
    """Setup monitoring and metrics"""
    logger.info("Setting up monitoring and metrics collection")

def record_request_metrics(request: Request, response_time: float, status_code: int):
    """Record HTTP request metrics"""
    endpoint = request.url.path
    method = request.method
    
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(response_time)

def record_model_prediction(model_id: str, model_version: str, status: str):
    """Record model prediction metrics"""
    MODEL_PREDICTIONS.labels(
        model_id=model_id,
        model_version=model_version,
        status=status
    ).inc()

def record_drift_score(model_id: str, drift_type: str, score: float):
    """Record model drift detection score"""
    MODEL_DRIFT_SCORE.labels(
        model_id=model_id,
        drift_type=drift_type
    ).set(score)

def record_alert(model_id: str, alert_type: str, severity: str):
    """Record alert metrics"""
    ALERT_COUNT.labels(
        model_id=model_id,
        alert_type=alert_type,
        severity=severity
    ).inc()

def update_active_models(count: int):
    """Update active models count"""
    ACTIVE_MODELS.set(count)

def update_database_connections(count: int):
    """Update database connections count"""
    DATABASE_CONNECTIONS.set(count)

def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest()

def log_model_event(event_type: str, model_id: str, data: Dict[str, Any]):
    """Log model-related events with structured logging"""
    logger.info(
        f"Model {event_type}",
        model_id=model_id,
        event_type=event_type,
        **data
    )

def log_alert_event(alert_type: str, model_id: str, severity: str, message: str):
    """Log alert events"""
    logger.warning(
        "Model alert triggered",
        model_id=model_id,
        alert_type=alert_type,
        severity=severity,
        message=message
    )

def log_drift_detection(model_id: str, drift_type: str, score: float, threshold: float):
    """Log drift detection events"""
    logger.info(
        "Drift detected",
        model_id=model_id,
        drift_type=drift_type,
        score=score,
        threshold=threshold,
        is_alert=score > threshold
    )

def log_compliance_event(event_type: str, user_id: str, action: str, resource: str):
    """Log compliance and audit events"""
    logger.info(
        "Compliance event",
        event_type=event_type,
        user_id=user_id,
        action=action,
        resource=resource,
        timestamp=time.time()
    ) 