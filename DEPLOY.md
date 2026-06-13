# TITAN — Deployment Guide

> **Production deployment checklist for TITAN governance platform**

---

## 📋 Table of Contents

1. [Quick Start (Docker Compose)](#quick-start-docker-compose)
2. [Production Deployment](#production-deployment)
3. [Environment Variables](#environment-variables)
4. [Database Setup](#database-setup)
5. [Monitoring & Observability](#monitoring--observability)
6. [Cost Management](#cost-management)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start (Docker Compose)

### Prerequisites

- Docker & Docker Compose
- 4GB RAM minimum
- PostgreSQL 13+ (or use the docker-compose Postgres service)

### Steps

1. **Clone and navigate to project:**
```bash
git clone <repo>
cd TITAN
```

2. **Create environment file:**
```bash
cp apps/api/.env.example apps/api/.env
```

3. **Set required variables:**
```bash
# apps/api/.env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql+asyncpg://titan:titanpass@postgres:5432/titan_db
ENVIRONMENT=development
```

4. **Start services:**
```bash
docker-compose -f docker/docker-compose.yml up
```

5. **Initialize database:**
```bash
# Run in another terminal
docker-compose -f docker/docker-compose.yml exec api alembic upgrade head
```

6. **Access the application:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🏢 Production Deployment

### Architecture

```
┌─────────────────────────────────────────────┐
│            Load Balancer (Nginx/ALB)        │
└────────────────┬────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
    ┌───▼────┐        ┌───▼────┐
    │ API-1  │        │ API-2  │  (Horizontal scaling)
    └───┬────┘        └───┬────┘
        │                 │
        └────────┬────────┘
                 │
        ┌────────▼───────────┐
        │   PostgreSQL 16+   │  (RDS/CloudSQL)
        │   (Primary + Read) │
        └────────────────────┘
        
        ┌────────────────────┐
        │  Redis Cache       │  (Optional)
        │  (Session + Cache) │
        └────────────────────┘
```

### Kubernetes Deployment Example

```yaml
# deploy/titan-api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: titan-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: titan-api
  template:
    metadata:
      labels:
        app: titan-api
    spec:
      containers:
      - name: api
        image: titan-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: titan-secrets
              key: database-url
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: titan-secrets
              key: gemini-api-key
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: titan-api
spec:
  selector:
    app: titan-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Cloud Deployment Options

#### Google Cloud Run

```bash
# Build image
docker build -f docker/Dockerfile.api -t gcr.io/PROJECT_ID/titan-api:latest .
docker push gcr.io/PROJECT_ID/titan-api:latest

# Deploy
gcloud run deploy titan-api \
  --image gcr.io/PROJECT_ID/titan-api:latest \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY,DATABASE_URL=$DATABASE_URL \
  --allow-unauthenticated
```

#### AWS ECS

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URI
docker build -f docker/Dockerfile.api -t $ECR_URI/titan-api:latest .
docker push $ECR_URI/titan-api:latest

# Update ECS task definition and service
```

---

## 🔧 Environment Variables

### Backend (API)

```bash
# ─── Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false  # Set to false in production
ENVIRONMENT=production
API_VERSION=1.0.0

# ─── Database
DATABASE_URL=postgresql+asyncpg://user:password@hostname:5432/titan_db
DATABASE_ECHO=false  # Set to false in production
DATABASE_POOL_SIZE=20  # Adjust for concurrency
DATABASE_MAX_OVERFLOW=10

# ─── Gemini AI
GEMINI_API_KEY=your_api_key_here
GEMINI_FLASH_MODEL=gemini-1.5-flash
GEMINI_PRO_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_OUTPUT_TOKENS=4096

# ─── Agent Settings
DEBATE_ROUNDS=2
MAX_SIMULATION_OPTIONS=3
AGENT_TIMEOUT_SECONDS=120
SESSION_TIMEOUT_SECONDS=1800

# ─── CORS
ALLOWED_ORIGINS=https://app.titan-governance.com,https://www.titan-governance.com
ALLOWED_METHODS=GET,POST,OPTIONS
ALLOWED_HEADERS=Content-Type,Authorization

# ─── Security
JWT_SECRET_KEY=your_secure_random_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# ─── Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_SESSIONS_PER_HOUR=100

# ─── Monitoring
SENTRY_DSN=https://your_sentry_dsn
LOG_LEVEL=INFO
```

### Frontend (Next.js)

```bash
# .env.local
NEXT_PUBLIC_API_URL=https://api.titan-governance.com
NEXT_PUBLIC_ENVIRONMENT=production
```

### Database Configuration

```bash
# Connection string format:
postgresql://username:password@hostname:5432/database_name

# With SSL (recommended for production):
postgresql+asyncpg://username:password@hostname:5432/database_name?ssl=require
```

---

## 🗄️ Database Setup

### 1. Create Database

```sql
CREATE DATABASE titan_db;
CREATE USER titan_user WITH PASSWORD 'secure_password_here';
ALTER ROLE titan_user SET client_encoding TO 'utf8';
ALTER ROLE titan_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE titan_user SET default_transaction_dereference TO ON;
GRANT ALL PRIVILEGES ON DATABASE titan_db TO titan_user;
```

### 2. Run Migrations

```bash
cd apps/api
alembic upgrade head
```

### 3. Verify Tables

```bash
psql titan_db -U titan_user -c "\dt"

# Output should show:
# public | projects     | table | titan_user
# public | agents       | table | titan_user
# public | debates      | table | titan_user
# public | votes        | table | titan_user
# public | simulations  | table | titan_user
# public | final_reports| table | titan_user
```

### 4. Create Indexes

Indexes are auto-created by SQLAlchemy models, but verify:

```bash
alembic current
```

### 5. Backup Strategy

```bash
# Daily backup to S3
0 2 * * * pg_dump -h localhost -U titan_user titan_db | gzip | \
  aws s3 cp - s3://titan-backups/db_$(date +\%Y\%m\%d).sql.gz
```

---

## 📊 Monitoring & Observability

### 1. Application Metrics

```python
# apps/api/main.py — add Prometheus middleware
from prometheus_client import Counter, Histogram
from prometheus_client.asgi import make_wsgi_app

# Request metrics
request_count = Counter(
    'titan_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'titan_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

# LLM metrics
llm_tokens_used = Counter(
    'titan_llm_tokens_total',
    'Total tokens used',
    ['model', 'agent', 'phase']
)

llm_cost_usd = Counter(
    'titan_llm_cost_usd_total',
    'Total LLM cost in USD',
    ['model']
)
```

### 2. Centralized Logging

#### Using CloudLogging (GCP)

```python
# apps/api/app/core/logging.py
import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
```

#### Using CloudWatch (AWS)

```python
import watchtower
import logging

cloudwatch_handler = watchtower.CloudWatchLogHandler(
    log_group='titan-api',
    stream_name='api-logs'
)
logging.getLogger().addHandler(cloudwatch_handler)
```

### 3. Distributed Tracing

```python
# OpenTelemetry setup
from opentelemetry import trace
from opentelemetry.exporter.gcp_trace import CloudTraceExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

trace.set_tracer_provider(TracerProvider())
CloudTraceExporter().setup_tracing()

tracer = trace.get_tracer(__name__)

# Use in nodes:
@trace.tracer.start_as_current_span("minister_analysis")
async def node_minister_analysis(payload):
    ...
```

### 4. Health Checks

```bash
# Add health endpoint
GET /api/v1/health

# Response:
{
  "status": "healthy",
  "database": "connected",
  "gemini_api": "reachable",
  "timestamp": "2026-06-13T12:00:00Z"
}
```

---

## 💰 Cost Management

### LLM Budget Alerts

```python
# In session service
from app.core.cost_tracking import get_cost_tracker

cost_tracker = get_cost_tracker(session_id)
cost_tracker.log_usage(input_tokens=1500, output_tokens=800, 
                      model="gemini-1.5-flash", 
                      agent_role="economic_minister",
                      phase="analyzing")

# Check budget
if cost_tracker.cost_exceeds_budget(budget_usd=10.0):
    logger.warning("Session exceeding budget")
    # Optionally halt session
```

### Cost Tracking Dashboard

```bash
# Query cost by date
SELECT 
    DATE(created_at) as date,
    COUNT(*) as sessions,
    SUM(total_tokens) as tokens,
    SUM(estimated_cost_usd) as total_cost
FROM sessions_metadata
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## 🔐 Security Considerations

### 1. API Key Management

```bash
# Rotate Gemini API keys regularly
# Store in secrets manager, never in code

# AWS Secrets Manager
aws secretsmanager create-secret \
    --name titan/gemini-api-key \
    --secret-string "your_api_key"

# Reference in code
import boto3
secrets = boto3.client('secretsmanager')
response = secrets.get_secret_value(SecretId='titan/gemini-api-key')
api_key = response['SecretString']
```

### 2. Input Sanitization

- All problem statements are sanitized (see `app/core/validation.py`)
- Use Pydantic validators for all user input
- Regularly update attack detection patterns

### 3. Authentication

```python
# Add JWT middleware
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

@app.get("/api/v1/sessions")
async def get_sessions(credentials: HTTPAuthCredentials = Depends(security)):
    # Verify JWT token
    # Return only user's own sessions
```

### 4. Rate Limiting

```python
# Add slowapi middleware
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/sessions")
@limiter.limit("10/minute")
async def create_session(req: Request):
    ...
```

### 5. HTTPS/TLS

- Use valid SSL certificate (Let's Encrypt)
- Enforce HTTPS redirects
- Set HSTS headers

```python
# In main.py
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
app.add_middleware(HTTPSRedirectMiddleware)
```

---

## 🐛 Troubleshooting

### Issue: LLM API Timeout

```
Error: asyncio.TimeoutError in node_minister_analysis
```

**Solution:**
1. Check network connectivity to Gemini API
2. Increase `AGENT_TIMEOUT_SECONDS` in .env
3. Implement retry logic (see `app/core/error_recovery.py`)

### Issue: Database Connection Pool Exhausted

```
Error: QueuePool limit of 20 reached
```

**Solution:**
```bash
# Increase pool size
DATABASE_POOL_SIZE=40
DATABASE_MAX_OVERFLOW=20

# Monitor connection usage
SELECT count(*) FROM pg_stat_activity WHERE datname = 'titan_db';
```

### Issue: Out of Memory (OOM)

```
Error: Worker killed due to memory limit exceeded
```

**Solution:**
1. Increase memory allocation
2. Reduce `MAX_SIMULATION_OPTIONS`
3. Implement pagination for large sessions

### Issue: LLM API Rate Limited

```
Error: 429 Too Many Requests
```

**Solution:**
1. Implement exponential backoff (included in `error_recovery.py`)
2. Reduce concurrent sessions
3. Add request queuing

```python
# Use queue to limit concurrent LLM calls
from asyncio import Semaphore

llm_semaphore = Semaphore(10)  # Max 10 concurrent LLM calls

async with llm_semaphore:
    result = await minister.analyze(problem, context)
```

### Issue: SSE Connection Drops

```
Error: Client disconnected from event stream
```

**Solution:**
1. Implement heartbeat pings every 30 seconds
2. Add reconnection logic on frontend
3. Store session state server-side for resumption

---

## ✅ Pre-Production Checklist

- [ ] Environment variables configured (no defaults in production)
- [ ] Database backups scheduled (daily minimum)
- [ ] SSL/TLS certificate installed
- [ ] API rate limiting configured
- [ ] Authentication middleware enabled
- [ ] Monitoring/logging centralized
- [ ] Cost tracking dashboard set up
- [ ] Load balancer health checks passing
- [ ] Database connection pooling tuned
- [ ] LLM API key stored in secrets manager
- [ ] CORS origins restricted to production domains
- [ ] API documentation deployed (/docs hidden in production)
- [ ] Error pages customized (no stack traces in 500 responses)
- [ ] Audit logging enabled
- [ ] Incident response plan documented
- [ ] Load testing completed (target: 100 concurrent sessions)
- [ ] Security audit completed
- [ ] Rollback procedure tested

---

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs -f api`
2. Review troubleshooting section above
3. File issue on GitHub with:
   - Full error message
   - Environment config (no secrets)
   - Relevant log excerpts
   - Steps to reproduce

---

**Last Updated:** 2026-06-13  
**Version:** 1.0.0
