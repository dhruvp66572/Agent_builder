# Deployment Guide

This guide covers various deployment strategies for the Agent Builder platform, from development to production environments.

## Table of Contents
- [Development Deployment](#development-deployment)
- [Staging Deployment](#staging-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Monitoring & Logging](#monitoring--logging)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Development Deployment

### Local Development Setup

1. **Clone and Setup**
```bash
git clone <repository-url>
cd agent-builder
```

2. **Automated Setup (Recommended)**
```bash
# Windows
setup.bat

# Linux/MacOS
chmod +x setup.sh
./setup.sh
```

3. **Manual Setup**
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python -m alembic upgrade head
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local
npm start
```

### Development Environment Variables

**Backend (.env)**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/agent_builder_dev
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_API_KEY=your-google-ai-key
SERPAPI_KEY=your-serpapi-key
CHROMA_DB_PATH=./chroma_db
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

**Frontend (.env.local)**
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
REACT_APP_DEBUG=true
```

## Staging Deployment

### Staging Environment Setup

Staging should closely mirror production while allowing for testing and validation.

1. **Infrastructure Setup**
```bash
# Create staging database
createdb agent_builder_staging

# Setup environment
export ENVIRONMENT=staging
export DATABASE_URL=postgresql://user:pass@staging-db:5432/agent_builder_staging
```

2. **Backend Deployment**
```bash
cd backend
pip install -r requirements.txt
python -m alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

3. **Frontend Build**
```bash
cd frontend
npm ci
npm run build
# Serve with nginx or similar
```

### Staging Environment Variables

**Backend (.env.staging)**
```env
DATABASE_URL=postgresql://user:pass@staging-db:5432/agent_builder_staging
OPENAI_API_KEY=sk-staging-openai-key
GOOGLE_API_KEY=staging-google-ai-key
SERPAPI_KEY=staging-serpapi-key
CHROMA_DB_PATH=/app/chroma_db
SECRET_KEY=staging-secret-key-32-characters-long
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_HOSTS=staging.yourapp.com,localhost
CORS_ORIGINS=https://staging.yourapp.com
```

**Frontend (.env.production)**
```env
REACT_APP_API_URL=https://api-staging.yourapp.com
REACT_APP_ENVIRONMENT=staging
REACT_APP_DEBUG=false
```

## Production Deployment

### Server Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 50GB SSD
- OS: Ubuntu 20.04 LTS or similar

**Recommended for Production:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 100GB SSD
- Load Balancer
- CDN for static assets

### Production Setup

1. **System Dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3-pip nodejs npm postgresql postgresql-contrib nginx certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash agentapp
sudo usermod -aG sudo agentapp
```

2. **Database Setup**
```bash
sudo -u postgres createuser agentapp
sudo -u postgres createdb agent_builder_prod -O agentapp
sudo -u postgres psql -c "ALTER USER agentapp PASSWORD 'secure-password';"
```

3. **Application Deployment**
```bash
# Clone application
cd /opt
sudo git clone <repository-url> agent-builder
sudo chown -R agentapp:agentapp agent-builder
cd agent-builder

# Backend setup
sudo -u agentapp python3.9 -m venv venv
sudo -u agentapp venv/bin/pip install -r backend/requirements.txt
sudo -u agentapp venv/bin/python backend/alembic upgrade head

# Frontend build
sudo -u agentapp npm ci --prefix frontend
sudo -u agentapp npm run build --prefix frontend
```

4. **Systemd Service Setup**

**Backend Service (/etc/systemd/system/agentbuilder-api.service)**
```ini
[Unit]
Description=Agent Builder API
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=exec
User=agentapp
Group=agentapp
WorkingDirectory=/opt/agent-builder/backend
Environment=PATH=/opt/agent-builder/venv/bin
EnvironmentFile=/opt/agent-builder/backend/.env.production
ExecStart=/opt/agent-builder/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Enable and start services**
```bash
sudo systemctl daemon-reload
sudo systemctl enable agentbuilder-api
sudo systemctl start agentbuilder-api
sudo systemctl status agentbuilder-api
```

5. **Nginx Configuration**

**/etc/nginx/sites-available/agentbuilder**
```nginx
server {
    listen 80;
    server_name yourapp.com www.yourapp.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourapp.com www.yourapp.com;

    ssl_certificate /etc/letsencrypt/live/yourapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourapp.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Frontend
    location / {
        root /opt/agent-builder/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # API docs (optional - disable in production)
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable site**
```bash
sudo ln -s /etc/nginx/sites-available/agentbuilder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

6. **SSL Certificate**
```bash
sudo certbot --nginx -d yourapp.com -d www.yourapp.com
sudo systemctl reload nginx
```

### Production Environment Variables

**Backend (.env.production)**
```env
DATABASE_URL=postgresql://agentapp:secure-password@localhost:5432/agent_builder_prod
OPENAI_API_KEY=sk-production-openai-key
GOOGLE_API_KEY=production-google-ai-key
SERPAPI_KEY=production-serpapi-key
CHROMA_DB_PATH=/opt/agent-builder/data/chroma_db
SECRET_KEY=super-secure-production-secret-key-32-chars
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_HOSTS=yourapp.com,www.yourapp.com
CORS_ORIGINS=https://yourapp.com,https://www.yourapp.com
MAX_UPLOAD_SIZE=50000000
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

## Docker Deployment

### Docker Setup

1. **Backend Dockerfile**
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Frontend Dockerfile**
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy build files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

3. **Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: agent_builder
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 5

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/agent_builder
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - SERPAPI_KEY=${SERPAPI_KEY}
    volumes:
      - chroma_data:/app/chroma_db
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 5

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  chroma_data:
```

4. **Environment File (.env)**
```env
DB_PASSWORD=secure_database_password
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
SERPAPI_KEY=your_serpapi_key
```

5. **Deploy with Docker Compose**
```bash
docker-compose up -d
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS with Fargate

1. **Create ECR repositories**
```bash
aws ecr create-repository --repository-name agentbuilder/backend
aws ecr create-repository --repository-name agentbuilder/frontend
```

2. **Build and push images**
```bash
# Get login token
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com

# Build and push backend
docker build -t agentbuilder-backend ./backend
docker tag agentbuilder-backend:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/agentbuilder/backend:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/agentbuilder/backend:latest

# Build and push frontend
docker build -t agentbuilder-frontend ./frontend
docker tag agentbuilder-frontend:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/agentbuilder/frontend:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/agentbuilder/frontend:latest
```

3. **Create ECS task definition and service** (use AWS Console or CloudFormation)

#### Using AWS Lambda + API Gateway (Serverless)

For the backend API, you can use AWS Lambda with Mangum:

```python
# lambda_handler.py
from mangum import Mangum
from app.main import app

handler = Mangum(app)
```

### Google Cloud Platform

#### Using Cloud Run

1. **Build and deploy backend**
```bash
gcloud run deploy agentbuilder-api \
    --source ./backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars DATABASE_URL=$DATABASE_URL,OPENAI_API_KEY=$OPENAI_API_KEY
```

2. **Deploy frontend to Cloud Storage + Cloud CDN**
```bash
# Build frontend
cd frontend && npm run build

# Upload to Cloud Storage
gsutil -m cp -r build/* gs://your-frontend-bucket/

# Configure bucket for website hosting
gsutil web set -m index.html -e 404.html gs://your-frontend-bucket
```

### Heroku Deployment

#### Backend on Heroku

1. **Prepare for Heroku**
```bash
# Create Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > backend/Procfile

# Create runtime.txt
echo "python-3.9.16" > backend/runtime.txt
```

2. **Deploy to Heroku**
```bash
cd backend
heroku create agentbuilder-api
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set OPENAI_API_KEY=your_key
heroku config:set GOOGLE_API_KEY=your_key
heroku config:set SERPAPI_KEY=your_key
git push heroku main
```

#### Frontend on Netlify/Vercel

**Netlify:**
1. Connect GitHub repository
2. Set build command: `npm run build`
3. Set publish directory: `build`
4. Set environment variables in Netlify dashboard

**Vercel:**
1. Import project from GitHub
2. Framework preset: Create React App
3. Set environment variables in Vercel dashboard

## Environment Configuration

### Environment-Specific Settings

#### Development
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600
```

#### Staging
```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://staging.yourapp.com
RATE_LIMIT_REQUESTS=500
RATE_LIMIT_WINDOW=3600
```

#### Production
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourapp.com
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

## Database Setup

### PostgreSQL Configuration

#### Production Database Setup
```sql
-- Create database and user
CREATE DATABASE agent_builder_prod;
CREATE USER agentapp WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE agent_builder_prod TO agentapp;

-- Additional security
ALTER USER agentapp CREATEDB;
```

#### Database Migrations
```bash
# Run migrations
python -m alembic upgrade head

# Create new migration
python -m alembic revision --autogenerate -m "Add new feature"

# Rollback migration
python -m alembic downgrade -1
```

#### Database Backup and Restore
```bash
# Backup
pg_dump -h localhost -U agentapp agent_builder_prod > backup.sql

# Restore
psql -h localhost -U agentapp -d agent_builder_prod < backup.sql
```

## Monitoring & Logging

### Application Monitoring

#### Health Checks
```python
# Add to app/main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": "connected",  # Check DB connection
        "services": {
            "openai": "connected",
            "chromadb": "connected"
        }
    }
```

#### Logging Configuration
```python
# app/config.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
```

### External Monitoring Tools

#### Prometheus + Grafana
```python
# Install prometheus client
pip install prometheus-client

# Add metrics to FastAPI
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')

@app.middleware("http")
async def add_prometheus_metrics(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(time.time() - start_time)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest())
```

#### Sentry Error Tracking
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

## Security Considerations

### API Security

#### Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/protected")
@limiter.limit("5/minute")
async def protected_route(request: Request):
    return {"message": "Protected content"}
```

#### Authentication & Authorization
```python
# JWT implementation example
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### HTTPS & Security Headers
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Force HTTPS in production
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["yourapp.com", "www.yourapp.com"]
)
```

### Database Security

#### Connection Security
```env
# Use SSL connections
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Connection pooling limits
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
```

#### Input Validation
```python
from pydantic import BaseModel, validator

class WorkflowCreate(BaseModel):
    name: str
    description: str
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v
```

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check database connectivity
psql -h localhost -U agentapp -d agent_builder_prod -c "SELECT 1;"

# Check database URL format
echo $DATABASE_URL
```

#### API Key Issues
```bash
# Verify environment variables
printenv | grep API_KEY

# Test API connections
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

#### Memory Issues
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Monitor application memory
htop
```

#### Performance Issues
```bash
# Check application logs
journalctl -u agentbuilder-api -f

# Monitor database queries
sudo -u postgres psql agent_builder_prod -c "SELECT query, state, query_start FROM pg_stat_activity;"

# Check disk usage
df -h
du -sh /opt/agent-builder/*
```

### Log Analysis

#### Application Logs
```bash
# View systemd logs
journalctl -u agentbuilder-api -f

# View nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Application-specific logs
tail -f /opt/agent-builder/logs/app.log
```

#### Database Logs
```bash
# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log

# Slow query log
sudo -u postgres psql -c "ALTER SYSTEM SET log_min_duration_statement = 1000;"
sudo systemctl reload postgresql
```

### Performance Optimization

#### Backend Optimization
```python
# Connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300
)
```

#### Frontend Optimization
```bash
# Build optimization
npm run build -- --analyze

# Bundle size analysis
npm install -g webpack-bundle-analyzer
npx webpack-bundle-analyzer build/static/js/*.js
```

#### Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_documents_created_at ON documents(created_at);
CREATE INDEX idx_workflows_user_id ON workflows(user_id);

-- Analyze table statistics
ANALYZE documents;
ANALYZE workflows;
```

### Rollback Procedures

#### Application Rollback
```bash
# Git rollback
git checkout previous-stable-tag
sudo systemctl restart agentbuilder-api

# Database rollback
python -m alembic downgrade -1
```

#### Blue-Green Deployment
```bash
# Deploy to green environment
docker-compose -f docker-compose.green.yml up -d

# Test green environment
# ...

# Switch traffic to green
# Update load balancer configuration

# Stop blue environment
docker-compose -f docker-compose.blue.yml down
```

This deployment guide provides comprehensive coverage for deploying Agent Builder in various environments, from development to production, with emphasis on security, monitoring, and maintainability.