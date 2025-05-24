# TradeWise Deployment Guide

## 🚀 Quick Start (Development)

### Prerequisites
- Docker & Docker Compose
- Node.js 16+ (for frontend development)
- Python 3.11+ (for backend development)
- PostgreSQL 13+ (if running locally)

### 1. Clone Repository
```bash
git clone <repository-url>
cd freqtrade-saas
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### 3. Start with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access Application
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Environment Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/tradewise
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=tradewise

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO

# External Services (Optional)
REDIS_URL=redis://redis:6379/0
DATADOG_API_KEY=your-datadog-api-key
SENTRY_DSN=your-sentry-dsn
```

### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build: ./backend
    environment:
      DATABASE_URL: ${DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: ${DEBUG}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend/vue-app
    ports:
      - "8080:8080"
    depends_on:
      - backend
    volumes:
      - ./frontend/vue-app:/app
      - /app/node_modules
    command: npm run serve

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 🏗️ Production Deployment

### 1. Cloud Infrastructure

#### AWS Deployment
```bash
# Install AWS CLI and configure
aws configure

# Create ECS cluster
aws ecs create-cluster --cluster-name tradewise-cluster

# Deploy using CloudFormation
aws cloudformation deploy \
  --template-file infrastructure/aws/cloudformation.yaml \
  --stack-name tradewise-infrastructure \
  --parameter-overrides \
    Environment=production \
    DBInstanceClass=db.t3.medium
```

#### Azure Deployment
```bash
# Install Azure CLI
az login

# Create resource group
az group create --name tradewise-rg --location eastus

# Deploy using ARM template
az deployment group create \
  --resource-group tradewise-rg \
  --template-file infrastructure/azure/main.json \
  --parameters @infrastructure/azure/parameters.json
```

#### Google Cloud Deployment
```bash
# Install gcloud CLI
gcloud auth login

# Set project
gcloud config set project your-project-id

# Deploy using Cloud Run
gcloud run deploy tradewise-backend \
  --image gcr.io/your-project/tradewise-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 2. Database Setup

#### PostgreSQL Production Configuration
```sql
-- Create database
CREATE DATABASE tradewise;

-- Create application user
CREATE USER tradewise_app WITH PASSWORD 'secure_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE tradewise TO tradewise_app;
GRANT USAGE ON SCHEMA public TO tradewise_app;
GRANT CREATE ON SCHEMA public TO tradewise_app;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
```

#### Database Migration
```bash
# Run migrations
cd backend
python -m alembic upgrade head

# Verify tables
python -c "
from app.db.session import SessionLocal
from sqlalchemy import text
db = SessionLocal()
result = db.execute(text('SELECT tablename FROM pg_tables WHERE schemaname = \\'public\\''))
print([row[0] for row in result])
"
```

### 3. Container Images

#### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 4. Load Balancer Configuration

#### Nginx Configuration
```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    server_name api.tradewise.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.tradewise.com;
    
    ssl_certificate /etc/ssl/certs/tradewise.crt;
    ssl_certificate_key /etc/ssl/private/tradewise.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # API routes
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
}

server {
    listen 443 ssl http2;
    server_name app.tradewise.com;
    
    ssl_certificate /etc/ssl/certs/tradewise.crt;
    ssl_certificate_key /etc/ssl/private/tradewise.key;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 🔒 Security Configuration

### SSL/TLS Setup
```bash
# Generate SSL certificate with Let's Encrypt
certbot --nginx -d api.tradewise.com -d app.tradewise.com

# Auto-renewal cron job
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

### Firewall Configuration
```bash
# Allow only necessary ports
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw deny 5432/tcp  # Block direct database access
ufw enable
```

### Secret Management
```bash
# Using HashiCorp Vault
vault kv put secret/tradewise \
  database_password="secure_db_password" \
  jwt_secret="super-secret-jwt-key" \
  api_encryption_key="encryption-key-for-tokens"

# Using AWS Secrets Manager
aws secretsmanager create-secret \
  --name "tradewise/production" \
  --secret-string '{
    "database_password": "secure_db_password",
    "jwt_secret": "super-secret-jwt-key"
  }'
```

## 📊 Monitoring Setup

### Health Checks
```python
# app/api/endpoints/health.py
@router.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    try:
        # Check database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )
```

### Prometheus Metrics
```python
# app/middleware/metrics.py
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Log Aggregation
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  fluentd:
    image: fluent/fluentd:v1.16
    volumes:
      - ./fluentd/conf:/fluentd/etc
      - /var/log:/var/log
    ports:
      - "24224:24224"
    environment:
      DATADOG_API_KEY: ${DATADOG_API_KEY}

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy TradeWise

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
          cd backend
          pip install -r requirements.txt
          python -m pytest tests/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push images
        run: |
          docker build -t tradewise/backend:${{ github.sha }} ./backend
          docker build -t tradewise/frontend:${{ github.sha }} ./frontend
          docker push tradewise/backend:${{ github.sha }}
          docker push tradewise/frontend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/backend backend=tradewise/backend:${{ github.sha }}
          kubectl set image deployment/frontend frontend=tradewise/frontend:${{ github.sha }}
```

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
psql -h localhost -U postgres -d tradewise -c "SELECT version();"

# Check connection pool
python -c "
from app.db.session import engine
with engine.connect() as conn:
    print('Database connected successfully')
"
```

#### Memory Issues
```bash
# Monitor memory usage
docker stats

# Check Python memory usage
python -c "
import psutil
process = psutil.Process()
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

#### Performance Issues
```bash
# Check slow queries
psql -d tradewise -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"

# Check API response times
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8000/api/v1/bots/
```

### Log Analysis
```bash
# Search logs for errors
docker logs backend-container 2>&1 | grep -i error

# Monitor real-time logs
docker logs -f backend-container | jq '.'

# Search for specific events
docker logs backend-container | grep "bot_connection_test" | jq '.'
```

## 📋 Maintenance Tasks

### Regular Maintenance
```bash
# Database vacuum and analyze
psql -d tradewise -c "VACUUM ANALYZE;"

# Clean up old logs
find /var/log/tradewise -name "*.log" -mtime +30 -delete

# Update dependencies
cd backend && pip-audit --fix
cd frontend && npm audit fix
```

### Backup and Recovery
```bash
# Database backup
pg_dump -h postgres-host -U tradewise_app tradewise > backup-$(date +%Y%m%d).sql

# Restore from backup
psql -h postgres-host -U tradewise_app -d tradewise < backup-20240101.sql

# Test backup integrity
pg_restore --list backup-20240101.sql
```