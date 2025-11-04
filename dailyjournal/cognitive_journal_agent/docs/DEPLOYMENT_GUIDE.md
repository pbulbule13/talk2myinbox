# Deployment Guide - Cognitive Journal Agent

**Version**: 1.0.0
**Last Updated**: 2025-11-03

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Development Deployment](#local-development-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment (AWS)](#cloud-deployment-aws)
6. [Cloud Deployment (Google Cloud)](#cloud-deployment-google-cloud)
7. [Kubernetes Deployment](#kubernetes-deployment)
8. [Configuration Management](#configuration-management)
9. [Monitoring & Logging](#monitoring--logging)
10. [Backup & Recovery](#backup--recovery)
11. [Troubleshooting](#troubleshooting)

---

## 1. Overview

This guide provides step-by-step instructions for deploying the Cognitive Journal Agent in various environments:

- **Local Development**: For development and testing
- **Docker**: Containerized deployment
- **AWS**: Cloud deployment with auto-scaling
- **Google Cloud**: GCP with Firestore integration
- **Kubernetes**: Production-grade orchestration

---

## 2. Prerequisites

### General Requirements

```bash
# Software Requirements
- Python 3.9+ (for local deployment)
- Docker 20+ (for container deployment)
- kubectl (for Kubernetes deployment)
- Git

# Optional
- Tesseract OCR (for image processing)
- FFmpeg (for audio processing)
```

### API Keys Required

```bash
# LLM Providers (choose one)
- OpenAI API Key (recommended)
  OR
- Anthropic API Key

# Text-to-Speech (optional)
- ElevenLabs API Key

# Cloud Storage (optional)
- Google Cloud credentials (for Firestore)

# Email Integration (optional)
- SMTP credentials (Gmail App Password recommended)
```

---

## 3. Local Development Deployment

### 3.1 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/cognitive_journal_agent.git
cd cognitive_journal_agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3.2 Configuration

```bash
# Create environment file
python config.py  # Generates .env.template

# Copy and edit
cp .env.template .env

# Edit .env with your API keys
# Minimal configuration for local development:
nano .env
```

**Minimal `.env` for Development**:
```bash
# LLM Configuration (Optional - will use fallback if not set)
USE_LLM_PROCESSING=false
USE_LLM_REPORTING=false

# Storage (Local)
STORAGE_BACKEND=json
STORAGE_DIR=./data

# TTS (Local)
TTS_BACKEND=local
TTS_ENABLED=false

# API Server
API_HOST=127.0.0.1
API_PORT=8000
```

### 3.3 Running Locally

```bash
# CLI Mode
python main.py cli

# API Server Mode
python main.py api

# Demo Mode
python main.py demo

# Single Command
python main.py -c "Had a productive meeting today"
```

### 3.4 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_integration.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

---

## 4. Docker Deployment

### 4.1 Build Docker Image

```dockerfile
# Dockerfile (already provided)
# Build image
docker build -t cja:latest .

# Verify build
docker images | grep cja
```

### 4.2 Run Docker Container

```bash
# Simple run
docker run -d \
  --name cja-app \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/audio_output:/app/audio_output \
  --env-file .env \
  cja:latest

# Verify container
docker ps | grep cja-app

# View logs
docker logs -f cja-app

# Stop container
docker stop cja-app

# Remove container
docker rm cja-app
```

### 4.3 Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up -d --build
```

**Custom `docker-compose.yml`**:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=${LLM_PROVIDER}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - STORAGE_BACKEND=sqlite
      - TTS_ENABLED=true
    volumes:
      - app_data:/app/data
      - audio_output:/app/audio_output
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  app_data:
  audio_output:
```

---

## 5. Cloud Deployment (AWS)

### 5.1 AWS ECS (Elastic Container Service)

#### Prerequisites
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure
```

#### Step 1: Push Image to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name cja

# Get login credentials
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag cja:latest \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cja:latest

# Push image
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cja:latest
```

#### Step 2: Create ECS Task Definition

```json
{
  "family": "cja-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "cja-container",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cja:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "STORAGE_BACKEND",
          "value": "firestore"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:cja/openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/cja",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Step 3: Create ECS Service

```bash
# Create cluster
aws ecs create-cluster --cluster-name cja-cluster

# Create service
aws ecs create-service \
  --cluster cja-cluster \
  --service-name cja-service \
  --task-definition cja-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=cja-container,containerPort=8000"
```

### 5.2 AWS Lambda (Serverless)

#### Create Lambda Function

```python
# lambda_function.py
import json
from cognitive_journal_agent.graph.agent_graph import run_agent

def lambda_handler(event, context):
    """
    AWS Lambda handler for CJA.
    """
    body = json.loads(event['body'])
    user_input = body.get('user_input', '')

    # Run agent
    result = run_agent(user_input)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'result': str(result)
        })
    }
```

#### Deploy with SAM

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  CJAFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: cja-function
      Runtime: python3.11
      Handler: lambda_function.lambda_handler
      CodeUri: ./
      MemorySize: 512
      Timeout: 30
      Environment:
        Variables:
          STORAGE_BACKEND: firestore
          USE_LLM_PROCESSING: true
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /journal
            Method: post
```

```bash
# Deploy
sam build
sam deploy --guided
```

---

## 6. Cloud Deployment (Google Cloud)

### 6.1 Google Cloud Run

#### Prerequisites
```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

#### Deploy to Cloud Run

```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/cja

# Deploy to Cloud Run
gcloud run deploy cja-service \
  --image gcr.io/YOUR_PROJECT_ID/cja \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars STORAGE_BACKEND=firestore \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID

# Get service URL
gcloud run services describe cja-service \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

### 6.2 Firestore Setup

```bash
# Enable Firestore
gcloud firestore databases create --region=us-central

# Create service account
gcloud iam service-accounts create cja-sa \
  --display-name="CJA Service Account"

# Grant Firestore permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:cja-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

# Create key
gcloud iam service-accounts keys create cja-key.json \
  --iam-account=cja-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/cja-key.json"
```

---

## 7. Kubernetes Deployment

### 7.1 Create Kubernetes Resources

#### Namespace
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: cja
```

#### ConfigMap
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cja-config
  namespace: cja
data:
  STORAGE_BACKEND: "firestore"
  USE_LLM_PROCESSING: "true"
  TTS_ENABLED: "true"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
```

#### Secret
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: cja-secrets
  namespace: cja
type: Opaque
stringData:
  OPENAI_API_KEY: "your-openai-key-here"
  ELEVENLABS_API_KEY: "your-elevenlabs-key-here"
```

#### Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cja-deployment
  namespace: cja
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cja
  template:
    metadata:
      labels:
        app: cja
    spec:
      containers:
      - name: cja
        image: gcr.io/YOUR_PROJECT_ID/cja:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        envFrom:
        - configMapRef:
            name: cja-config
        - secretRef:
            name: cja-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Service
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: cja-service
  namespace: cja
spec:
  selector:
    app: cja
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  type: LoadBalancer
```

#### Ingress (Optional)
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cja-ingress
  namespace: cja
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - cja.yourdomain.com
    secretName: cja-tls
  rules:
  - host: cja.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: cja-service
            port:
              number: 80
```

### 7.2 Deploy to Kubernetes

```bash
# Apply resources
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml  # Optional

# Verify deployment
kubectl get pods -n cja
kubectl get svc -n cja

# View logs
kubectl logs -f deployment/cja-deployment -n cja

# Scale deployment
kubectl scale deployment cja-deployment --replicas=5 -n cja

# Update image
kubectl set image deployment/cja-deployment \
  cja=gcr.io/YOUR_PROJECT_ID/cja:v2 -n cja

# Rollback
kubectl rollout undo deployment/cja-deployment -n cja
```

---

## 8. Configuration Management

### 8.1 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_PROVIDER` | No | `openai` | LLM provider (openai/anthropic) |
| `OPENAI_API_KEY` | No* | - | OpenAI API key |
| `ANTHROPIC_API_KEY` | No* | - | Anthropic API key |
| `USE_LLM_PROCESSING` | No | `true` | Use LLM for processing |
| `USE_LLM_REPORTING` | No | `true` | Use LLM for reports |
| `STORAGE_BACKEND` | No | `json` | Storage backend (json/sqlite/firestore) |
| `STORAGE_DIR` | No | `./data` | Local storage directory |
| `TTS_BACKEND` | No | `elevenlabs` | TTS backend (elevenlabs/local/none) |
| `TTS_ENABLED` | No | `true` | Enable TTS output |
| `ELEVENLABS_API_KEY` | No | - | ElevenLabs API key |
| `SMTP_HOST` | No | `smtp.gmail.com` | SMTP server |
| `SMTP_USERNAME` | No | - | SMTP username |
| `SMTP_PASSWORD` | No | - | SMTP password |

*At least one LLM API key required if `USE_LLM_PROCESSING=true`

### 8.2 Secrets Management

#### AWS Secrets Manager
```bash
# Create secret
aws secretsmanager create-secret \
  --name cja/openai-key \
  --secret-string "sk-..."

# Retrieve secret
aws secretsmanager get-secret-value \
  --secret-id cja/openai-key \
  --query SecretString \
  --output text
```

#### Google Secret Manager
```bash
# Create secret
echo -n "sk-..." | gcloud secrets create openai-key \
  --data-file=-

# Access secret
gcloud secrets versions access latest --secret="openai-key"
```

#### Kubernetes Secrets
```bash
# Create from literal
kubectl create secret generic cja-secrets \
  --from-literal=OPENAI_API_KEY=sk-... \
  -n cja

# Create from file
kubectl create secret generic cja-secrets \
  --from-env-file=.env \
  -n cja
```

---

## 9. Monitoring & Logging

### 9.1 Application Metrics

```python
# Add Prometheus metrics (future enhancement)
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
journal_entries_total = Counter(
    'cja_journal_entries_total',
    'Total number of journal entries created'
)

processing_duration = Histogram(
    'cja_processing_duration_seconds',
    'Time spent processing entries'
)

active_users = Gauge(
    'cja_active_users',
    'Number of active users'
)
```

### 9.2 Logging Configuration

```python
# logging_config.py
import logging
import sys

def setup_logging(level=logging.INFO):
    """Configure application logging."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('cja.log')
        ]
    )
```

### 9.3 Health Checks

```python
# GET /health endpoint
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "storage_backend": "firestore",
  "llm_provider": "openai",
  "checks": {
    "database": "ok",
    "llm_api": "ok",
    "tts_api": "ok"
  }
}
```

---

## 10. Backup & Recovery

### 10.1 Data Backup

#### JSON Storage
```bash
# Backup
tar -czf cja-backup-$(date +%Y%m%d).tar.gz data/

# Restore
tar -xzf cja-backup-20240115.tar.gz
```

#### SQLite
```bash
# Backup
sqlite3 data/journal.db ".backup 'backup/journal-$(date +%Y%m%d).db'"

# Restore
sqlite3 data/journal.db ".restore 'backup/journal-20240115.db'"
```

#### Firestore
```bash
# Export
gcloud firestore export gs://YOUR_BUCKET/backups/$(date +%Y%m%d)

# Import
gcloud firestore import gs://YOUR_BUCKET/backups/20240115
```

### 10.2 Automated Backups

```bash
# Cron job for daily backups
0 2 * * * /path/to/backup.sh

# backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf /backups/cja-$DATE.tar.gz /app/data/
find /backups -name "cja-*.tar.gz" -mtime +30 -delete
```

---

## 11. Troubleshooting

### 11.1 Common Issues

#### Issue: Container fails to start
```bash
# Check logs
docker logs cja-app

# Common causes:
# - Missing environment variables
# - Port already in use
# - Volume mount issues

# Solution:
docker run -it --rm cja:latest /bin/bash
# Test configuration inside container
```

#### Issue: LLM API errors
```bash
# Verify API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check rate limits
# Review API usage dashboard

# Solution:
# - Verify API key is correct
# - Check account credits
# - Enable fallback: USE_LLM_PROCESSING=false
```

#### Issue: Database connection errors
```bash
# For Firestore:
# - Verify GOOGLE_APPLICATION_CREDENTIALS path
# - Check service account permissions

# For SQLite:
# - Verify file permissions
# - Check disk space

# Solution:
chmod 600 cja-key.json
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/cja-key.json"
```

### 11.2 Performance Issues

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py api

# Profile application
python -m cProfile -o profile.stats main.py

# Analyze profile
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"

# Common optimizations:
# - Increase worker processes
# - Enable caching
# - Use smaller LLM models
# - Batch processing
```

### 11.3 Debug Mode

```bash
# Run with debug logging
LOG_LEVEL=DEBUG python main.py cli

# Interactive debugging
python -m pdb main.py

# API request debugging
curl -v http://localhost:8000/journal \
  -H "Content-Type: application/json" \
  -d '{"user_input": "test"}'
```

---

## Appendix: Quick Reference

### Development
```bash
# Start dev environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py cli
```

### Docker
```bash
# Build and run
docker build -t cja .
docker run -d -p 8000:8000 --env-file .env cja
```

### Kubernetes
```bash
# Deploy
kubectl apply -f k8s/
kubectl get pods -n cja
kubectl logs -f deployment/cja-deployment -n cja
```

### AWS ECS
```bash
# Update service
aws ecs update-service \
  --cluster cja-cluster \
  --service cja-service \
  --force-new-deployment
```

### Google Cloud Run
```bash
# Deploy
gcloud run deploy cja-service \
  --image gcr.io/PROJECT_ID/cja \
  --platform managed
```

---

**Support**: For deployment issues, please open an issue on GitHub or contact support.
