from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, models, metrics, alerts, monitoring, compliance, billing

api_router = APIRouter()

# Authentication and user management
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Model management
api_router.include_router(models.router, prefix="/models", tags=["models"])

# Monitoring and metrics
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])

# Alerts and notifications
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])

# Compliance and reporting
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])

# Billing and subscriptions
api_router.include_router(billing.router, prefix="/billing", tags=["billing"]) 