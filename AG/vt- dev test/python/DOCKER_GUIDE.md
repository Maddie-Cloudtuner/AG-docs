# 🐳 Docker Deployment Guide - Virtual Tagging Backend

## ✅ Is it Feasible? YES! Highly Recommended!

Docker is the **BEST way** to deploy this application because:
- ✅ **Consistent environment** - Works same everywhere
- ✅ **Easy setup** - Single command to run everything
- ✅ **PostgreSQL included** - No manual database setup
- ✅ **Production-ready** - Proper isolation and networking
- ✅ **Scalable** - Easy to deploy to cloud (AWS ECS, GKE, Azure Container Apps)

---

## 🚀 Quick Start with Docker

### Prerequisites
- Docker Desktop for Windows
- Download from: https://www.docker.com/products/docker-desktop/

### 1. Build and Start Everything

```cmd
cd C:\Users\LENOVO\Desktop\my_docs\AG\virtual-tagging-prototype\python

REM Build and start all containers
docker-compose up --build
```

**That's it!** This single command will:
- Build the Python Tornado backend image
- Pull PostgreSQL image
- Create a network  
- Start both containers
- Connect them together

### 2. Seed Database (First Time Only)

**Open a new Command Prompt**:
```cmd
cd C:\Users\LENOVO\Desktop\my_docs\AG\virtual-tagging-prototype\python

REM Run seeder inside the container
docker-compose exec backend python seed_database.py
```

This creates 1000 resources in the database.

### 3. Access the API

- **Health Check**: http://localhost:8000/api/health
- **Resources**: http://localhost:8000/api/resources
- **ML Stats**: http://localhost:8000/api/ml/stats
- **Scheduler Status**: http://localhost:8000/api/scheduler/status

---

## 📦 What Docker Compose Creates

```
┌─────────────────────────────────────┐
│  Docker Network: vt-network         │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │  PostgreSQL  │  │   Tornado   │ │
│  │   Database   │◄─┤   Backend   │ │
│  │  Port 5432   │  │  Port 8000  │ │
│  └──────────────┘  └─────────────┘ │
│         │                  │        │
│    [Volume]           [Exposed]     │
│  postgres_data        localhost     │
└─────────────────────────────────────┘
```

---

## 🎯 Common Docker Commands

### Start Services
```cmd
REM Start in foreground (see logs)
docker-compose up

REM Start in background (detached)
docker-compose up -d

REM Rebuild and start
docker-compose up --build
```

### Stop Services
```cmd
REM Stop containers
docker-compose down

REM Stop and remove volumes (deletes database!)
docker-compose down -v
```

### View Logs
```cmd
REM All logs
docker-compose logs

REM Follow logs (live)
docker-compose logs -f

REM Backend logs only
docker-compose logs -f backend

REM Database logs only
docker-compose logs -f postgres
```

### Execute Commands in Container
```cmd
REM Seed database
docker-compose exec backend python seed_database.py

REM Open Python shell
docker-compose exec backend python

REM Open bash in container
docker-compose exec backend bash

REM Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d virtual_tagging
```

### Check Status
```cmd
REM List running containers
docker-compose ps

REM View resource usage
docker stats
```

---

## 🔧 Configuration

### Environment Variables

Edit `docker-compose.yml` to change settings:

```yaml
environment:
  DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/virtual_tagging
  ENABLE_AUTO_TAGGING: "True"
  DISCOVERY_INTERVAL_MINUTES: 1
  AUTO_APPLY_THRESHOLD: 0.90
  # Add more as needed
```

### Change Ports

```yaml
services:
  backend:
    ports:
      - "9000:8000"  # Access at localhost:9000
  
  postgres:
    ports:
      - "5433:5432"  # Use different PostgreSQL port
```

---

## 🌐 Production Deployment

### AWS ECS (Elastic Container Service)

```cmd
REM Build and push to ECR
docker build -t virtual-tagging-backend .
docker tag virtual-tagging-backend:latest YOUR_ECR_URL/virtual-tagging-backend:latest
docker push YOUR_ECR_URL/virtual-tagging-backend:latest

REM Use RDS for PostgreSQL instead of container
```

### Google Cloud Run

```cmd
REM Build and push to GCR
docker build -t virtual-tagging-backend .
docker tag virtual-tagging-backend gcr.io/YOUR_PROJECT/virtual-tagging-backend
docker push gcr.io/YOUR_PROJECT/virtual-tagging-backend

REM Deploy
gcloud run deploy virtual-tagging --image gcr.io/YOUR_PROJECT/virtual-tagging-backend
```

### Azure Container Apps

```cmd
REM Build and push to ACR
docker build -t virtual-tagging-backend .
docker tag virtual-tagging-backend YOUR_ACR.azurecr.io/virtual-tagging-backend
docker push YOUR_ACR.azurecr.io/virtual-tagging-backend

REM Deploy to Container Apps
az containerapp create --name virtual-tagging --resource-group YOUR_RG --image YOUR_ACR.azurecr.io/virtual-tagging-backend
```

---

## 🐛 Troubleshooting

### Container won't start
```cmd
REM Check logs
docker-compose logs backend

REM Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Database connection error
```cmd
REM Wait for PostgreSQL to be ready
docker-compose exec postgres pg_isready -U postgres

REM Check if containers are on same network
docker network inspect python_vt-network
```

### Port already in use
```cmd
REM Find what's using port 8000
netstat -ano | findstr :8000

REM Kill the process or change port in docker-compose.yml
```

### Database data lost
```cmd
REM Check if volume exists
docker volume ls

REM Backup database
docker-compose exec postgres pg_dump -U postgres virtual_tagging > backup.sql

REM Restore database
docker-compose exec -T postgres psql -U postgres virtual_tagging < backup.sql
```

---

## 📊 Monitoring with Docker

### Health Checks

Backend has automatic health check every 30s:
```cmd
docker-compose ps
# Shows "healthy" or "unhealthy"
```

### Resource Usage

```cmd
REM Monitor CPU/Memory
docker stats

REM Limit resources (in docker-compose.yml):
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

---

## 🔄 Development Workflow

### Local Development with Hot Reload

Create `docker-compose.dev.yml`:
```yaml
version: '3.8'
services:
  backend:
    build: .
    volumes:
      - ./app:/app/app  # Mount source code
    environment:
      DEBUG: "True"
```

Run with:
```cmd
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

## ✨ Benefits of Docker Deployment

| Aspect | Without Docker | With Docker |
|--------|---------------|-------------|
| **Setup Time** | 30+ minutes | 2 minutes |
| **Dependencies** | Manual install | Auto-included |
| **Database** | Separate setup | Included |
| **Consistency** | May vary | Always same |
| **Deployment** | Complex | Single command |
| **Scaling** | Manual | Orchestration |
| **Rollback** | Difficult | Change image tag |

---

## 🎉 Summary

**Docker is 100% feasible and RECOMMENDED!**

**Advantages**:
- ✅ **Zero local setup** - No Python, PostgreSQL installation needed
- ✅ **One command deployment** - `docker-compose up`
- ✅ **Production-ready** - Same environment dev to prod
- ✅ **Easy scaling** - Deploy to any cloud platform
- ✅ **Team friendly** - Everyone runs identical environment

**To run locally**:
```cmd
cd python
docker-compose up --build
# Wait 30 seconds
docker-compose exec backend python seed_database.py
# Visit http://localhost:8000/api/health
```

**Perfect for**:
- ✅ Local development
- ✅ CI/CD pipelines
- ✅ Cloud deployment (AWS/GCP/Azure)
- ✅ Team collaboration
- ✅ Production hosting

You can now deploy this to **any cloud platform** that supports Docker! 🚀
