# MLOps Monitoring Platform - Setup Guide

This guide will help you set up the MLOps Model Monitoring Platform for development and production use.

## 🚀 Quick Start (Development)

### Prerequisites

- **Docker & Docker Compose** (v20.10+)
- **Python 3.9+**
- **Node.js 18+**
- **Git**

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd mlops-monitoring

# Create environment file
cp .env.example .env
```

### 2. Environment Configuration

Edit `.env` file with your configuration:

```bash
# Database Configuration
DATABASE_URL=postgresql://mlops_user:mlops_password@localhost:5432/mlops_monitoring
REDIS_URL=redis://localhost:6379
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-influxdb-token
INFLUXDB_ORG=mlops
INFLUXDB_BUCKET=model_metrics

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_PREDICTIONS=model_predictions
KAFKA_TOPIC_METRICS=model_metrics
KAFKA_TOPIC_ALERTS=model_alerts

# Billing (Stripe)
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Cloud Providers (Optional)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1

GCP_PROJECT_ID=your_gcp_project
GCP_CREDENTIALS_FILE=path/to/credentials.json

AZURE_STORAGE_CONNECTION_STRING=your_azure_connection_string
```

### 3. Start Infrastructure Services

```bash
# Start databases and message queues
docker-compose up -d postgres redis influxdb kafka prometheus grafana

# Wait for services to be healthy
docker-compose ps
```

### 4. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Frontend Setup

```bash
# Open new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 6. Verify Setup

```bash
# Run the test script
python test_setup.py

# Check services
curl http://localhost:8000/health
curl http://localhost:3000
```

## 🏗️ Production Deployment

### Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n mlops-monitoring
kubectl get services -n mlops-monitoring
```

## 📊 Monitoring Setup

### Prometheus Configuration

1. Access Prometheus: http://localhost:9090
2. Verify targets are healthy
3. Check metrics collection

### Grafana Setup

1. Access Grafana: http://localhost:3001
   - Username: `admin`
   - Password: `admin`
2. Add Prometheus data source
3. Import dashboard templates from `monitoring/grafana/dashboards/`

## 🔐 Security Configuration

### SSL/TLS Setup

```bash
# Generate SSL certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/private.key \
  -out nginx/ssl/certificate.crt

# Update nginx configuration
cp nginx/nginx.conf.example nginx/nginx.conf
```

### Environment Variables

```bash
# Production environment variables
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="postgresql://user:pass@prod-db:5432/mlops"
export REDIS_URL="redis://prod-redis:6379"
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run with coverage
pytest --cov=app tests/ -v
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run E2E tests
npm run test:e2e

# Run with coverage
npm run test:coverage
```

### Load Testing

```bash
# Install k6
curl -L https://github.com/grafana/k6/releases/download/v0.43.1/k6-v0.43.1-linux-amd64.tar.gz | tar xz

# Run load test
k6 run load-tests/model-monitoring.js
```

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Issues

```bash
# Check PostgreSQL status
docker-compose logs postgres

# Test connection
psql -h localhost -U mlops_user -d mlops_monitoring
```

#### Redis Connection Issues

```bash
# Check Redis status
docker-compose logs redis

# Test connection
redis-cli -h localhost ping
```

#### Frontend Build Issues

```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run type-check
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

## 📈 Performance Tuning

### Database Optimization

```sql
-- PostgreSQL optimization
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

### Redis Optimization

```bash
# Redis configuration
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Application Tuning

```python
# Backend optimization
WORKERS = 4
WORKER_CONNECTIONS = 1000
MAX_REQUESTS = 1000
MAX_REQUESTS_JITTER = 100
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend && pytest
          cd frontend && npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          docker-compose -f docker-compose.prod.yml up -d
```

## 📚 API Documentation

Once the backend is running, access the API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🆘 Support

For issues and support:

1. Check the troubleshooting section above
2. Review logs for error messages
3. Create an issue in the repository
4. Contact support at support@mlops-monitoring.com

## 📝 License

This project is proprietary software. All rights reserved. 