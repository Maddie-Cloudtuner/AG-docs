# 🏗️ Virtual Tagging System - Complete Architecture Guide

**Full-Stack Cloud Resource Auto-Tagging Platform**

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Code Structure](#code-structure)
4. [End-to-End Workflow](#end-to-end-workflow)
5. [Database Schema](#database-schema)
6. [Deployment Guide](#deployment-guide)
7. [Development Server Setup](#development-server-setup)

---

## 🏛️ System Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React SPA<br/>Vite + Axios]
    end
    
    subgraph "API Layer"
        API[Tornado REST API<br/>Python Async]
        CORS[CORS Handler]
    end
    
    subgraph "Business Logic Layer"
        AT[Auto-Tagger<br/>Service]
        ML[ML Inference<br/>Service]
        RD[Resource Discovery<br/>Service]
        SCH[APScheduler<br/>Cron Jobs]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL<br/>Database)]
        ORM[SQLAlchemy<br/>Async ORM]
    end
    
    subgraph "External Systems"
        AWS[AWS API]
        GCP[GCP API]
        AZURE[Azure API]
    end
    
    UI -->|HTTP/JSON| API
    API -->|CORS| CORS
    API --> AT
    API --> ML
    API --> RD
    AT --> ORM
    ML --> ORM
    RD --> ORM
    SCH --> AT
    SCH --> RD
    ORM --> DB
    RD -.->|Future| AWS
    RD -.->|Future| GCP
    RD -.->|Future| AZURE
    
    style UI fill:#61dafb,stroke:#000,stroke-width:2px
    style API fill:#90ee90,stroke:#000,stroke-width:2px
    style DB fill:#336791,stroke:#000,stroke-width:2px,color:#fff
```

### Request Flow Architecture

```mermaid
sequenceDiagram
    participant U as User Browser
    participant F as React Frontend
    participant A as Tornado API
    participant AT as Auto-Tagger
    participant ML as ML Service
    participant DB as PostgreSQL
    
    U->>F: Visit Dashboard
    F->>A: GET /api/resources
    A->>DB: Query Resources + Tags
    DB-->>A: Return Data
    A-->>F: JSON Response
    F-->>U: Render UI
    
    Note over AT,ML: Background Cron Job (Every 2 min)
    AT->>DB: Find Untagged Resources
    DB-->>AT: Resource List
    AT->>ML: Infer Tags
    ML-->>AT: Predictions
    AT->>DB: Store Tags (if conf >= 90%)
    AT->>DB: Store Suggestions (if conf >= 70%)
```

---

## 🛠️ Technology Stack

### Backend
```yaml
Framework: Tornado (Python Async Web Framework)
ORM: SQLAlchemy 2.0 (Async)
Migrations: Alembic (Database version control)
Database: PostgreSQL 15
Scheduler: APScheduler
ML: Custom Rule-Based + Pattern Matching
Python Version: 3.11+
```

### Frontend (NGUI Production Stack)

**Core Framework**
```yaml
React: 18.2.0 (UI Library)
TypeScript: 5.3.3 (Type-safe JavaScript)
Build Tool: Vite 5.4.14 (HMR + Fast Refresh)
Package Manager: pnpm 9.15.0
```

**UI Framework & Styling**
```yaml
Material-UI: 5.15.0 (@mui/material, @mui/icons-material)
Emotion: CSS-in-JS (@emotion/react, @emotion/styled)
tss-react: 4.5.2 (Type-safe MUI styling)
```

**State Management**
```yaml
Redux: 4.2.0 (Global state)
React-Redux: 8.0.5 (React bindings)
Redux Persist: 6.0.0 (State persistence)
Reselect: 4.1.7 (Memoized selectors)
```

**Data Fetching**
```yaml
Apollo Client: 3.12.6 (GraphQL client)
GraphQL: 16.10.0 + GraphQL-WS 5.16.0
Axios: 1.7.4 (REST APIs)
```

**Routing & Forms**
```yaml
React Router: 6.6.2 (Client-side routing)
React Hook Form: 7.51.3 (Form management)
Zod: 4.1.12 (Schema validation)
```

**Data Visualization**
```yaml
Nivo: 0.87.0 (Charts)
Recharts: 2.8.0 (React charts)
Plotly.js: 2.6.0 (Advanced plots)
Deck.gl: 8.8.22 (WebGL visualization)
TanStack Table: 8.7.6 (Tables)
```

**Backend for Frontend (BFF)**
```yaml
Node.js: Express 4.21.2
Apollo Server: 4.11.3 (GraphQL server)
TypeScript: 5.7.2
http-proxy-middleware: 2.0.7 (REST proxy)
```

**Development & Testing**
```yaml
Vitest: 0.34.6 (Unit testing)
Storybook: 7.6.20 (Component dev)
ESLint: 9.17.0 + Prettier 3.3.3
```

### Infrastructure
```yaml
Containerization: Docker + Docker Compose
Database: PostgreSQL 15 in Docker
Backend: Python 3.11 in Docker
Frontend: Node.js 18+ Development Server
GraphQL BFF: Node.js TypeScript Server
```

---

## 📁 Code Structure

### Backend Structure

```
python/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Tornado app entry point
│   ├── config.py                  # Settings & environment vars
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy 2.0 models
│   │   └── database.py            # Async database connection
│   │
│   ├── handlers/                  # API endpoints (Tornado)
│   │   ├── health.py              # Base handler + health check
│   │   ├── resources.py           # GET/POST resources (PAGINATED)
│   │   ├── virtual_tags.py        # Tag CRUD operations
│   │   ├── rules.py               # Tagging rules management
│   │   ├── ml.py                  # ML inference endpoints
│   │   ├── scheduler.py           # Scheduler controls
│   │   ├── approvals.py           # Tag approvals workflow
│   │   └── csv_upload.py          # Bulk CSV import/export
│   │
│   ├── services/                  # Business logic layer
│   │   ├── auto_tagger.py         # Orchestrates auto-tagging
│   │   ├── ml_inference.py        # ML tag prediction
│   │   └── resource_discovery.py  # Resource discovery service
│   │
│   └── scheduler/
│       └── jobs.py                # APScheduler cron jobs
│
├── alembic/                       # Database migrations
│   ├── versions/                  # Migration scripts
│   │   └── 001_initial_schema.py
│   ├── env.py                     # Alembic environment
│   ├── script.py.mako             # Migration template
│   └── alembic.ini                # Alembic configuration
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── alembic.ini                    # Alembic config (root)
```

### Frontend Structure (TypeScript + Material-UI)

```
client/
├── src/
│   ├── App.tsx                    # Main app component
│   ├── main.tsx                   # Entry point
│   ├── vite-env.d.ts             # Vite type definitions
│   │
│   ├── components/                # Reusable UI components
│   │   ├── common/               # Shared components
│   │   │   ├── Navbar.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── resources/
│   │   │   ├── ResourceCard.tsx
│   │   │   ├── ResourceTable.tsx
│   │   │   └── AddResourceModal.tsx
│   │   └── tags/
│   │       ├── TagChip.tsx
│   │       └── TagApprovalCard.tsx
│   │
│   ├── pages/                     # Route components
│   │   ├── Dashboard.tsx
│   │   ├── ResourcesPage.tsx
│   │   ├── RulesPage.tsx
│   │   ├── AutomationDashboard.tsx
│   │   ├── ApprovalsPage.tsx
│   │   └── CSVImportPage.tsx
│   │
│   ├── store/                     # Redux state management
│   │   ├── index.ts              # Store configuration
│   │   ├── slices/
│   │   │   ├── resourcesSlice.ts
│   │   │   ├── tagsSlice.ts
│   │   │   └── authSlice.ts
│   │   └── selectors/
│   │       └── resourceSelectors.ts
│   │
│   ├── api/                       # API clients
│   │   ├── graphql/              # Apollo GraphQL
│   │   │   ├── client.ts
│   │   │   ├── queries.ts
│   │   │   └── mutations.ts
│   │   └── rest/                 # Axios REST
│   │       └── apiClient.ts
│   │
│   ├── hooks/                     # Custom React hooks
│   │   ├── useResources.ts
│   │   ├── useTags.ts
│   │   └── useAuth.ts
│   │
│   ├── types/                     # TypeScript types
│   │   ├── Resource.ts
│   │   ├── Tag.ts
│   │   └── api.ts
│   │
│   ├── theme/                     # MUI theme configuration
│   │   ├── index.ts
│   │   └── palette.ts
│   │
│   └── utils/                     # Utility functions
│       ├── validators.ts
│       └── formatters.ts
│
├── bff/                           # Backend for Frontend (GraphQL)
│   ├── src/
│   │   ├── server.ts             # Express + Apollo Server
│   │   ├── schema/               # GraphQL schema
│   │   │   ├── typeDefs.ts
│   │   │   └── resolvers.ts
│   │   ├── datasources/          # REST API proxies
│   │   │   └── tornadoAPI.ts
│   │   └── generated/            # GraphQL Code Generator output
│   │       └── types.ts
│   ├── package.json
│   └── tsconfig.json
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .storybook/                    # Storybook configuration
```

---

## 🔄 End-to-End Workflow

### 1. Resource Discovery & Ingestion

```mermaid
flowchart TD
    A[Cron Job Triggers<br/>Every 2 minutes] --> B[Resource Discovery Service]
    B --> C{Resource Source}
    C -->|Simulated| D[Generate 20 Random Resources]
    C -->|Future: Real| E[Query AWS/GCP/Azure APIs]
    D --> F[Create Resource Records]
    E --> F
    F --> G[(PostgreSQL<br/>resources table)]
    G --> H[Trigger Auto-Tagger]
```

### 2. Auto-Tagging Pipeline

```mermaid
flowchart LR
    A[Untagged Resource] --> B[ML Inference Service]
    B --> C{Check Native Tags}
    C -->|Has Tags| D[Extract & Normalize<br/>98% confidence]
    C -->|No Tags| E[Pattern Matching<br/>on Name]
    E --> F[Resource Type<br/>Inference]
    F --> G[Apply Rules]
    G --> H{Merge Tags}
    D --> H
    H --> I{Confidence?}
    I -->|>= 90%| J[Auto-Apply as PENDING]
    I -->|70-89%| K[Store as Suggestion]
    I -->|< 70%| L[Discard]
    J --> M[Approval Workflow]
    K --> N[Manual Review]
```

### 3. Tag Approval Workflow

```mermaid
stateDiagram-v2
    [*] --> PENDING: Auto-Tagged
    PENDING --> APPROVED: User Approves
    PENDING --> DENIED: User Denies
    APPROVED --> [*]
    DENIED --> [*]
    
    note right of PENDING
        Tags with >= 90% confidence
        Queue for manual review
    end note
```

### 4. User Interaction Flow

```mermaid
graph TD
    A[User Opens Dashboard] --> B{Action?}
    B -->|View Resources| C[Resources Page]
    B -->|Review Rules| D[Rules Page]
    B -->|Check Automation| E[Automation Dashboard]
    B -->|Approve Tags| F[Approvals Page]
    B -->|Bulk Import| G[CSV Import]
    
    C --> H[View Resource Details<br/>+ Virtual Tags]
    D --> I[Create/Edit/Delete Rules]
    E --> J[View Jobs<br/>Trigger Manual Run]
    F --> K[Approve/Deny<br/>Single or Bulk]
    G --> L[Upload CSV<br/>Download Template]
```

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    RESOURCES ||--o{ VIRTUAL_TAGS : has
    RESOURCES ||--o{ ML_INFERENCES : has
    RESOURCES ||--o{ TAG_AUDIT : has
    RULES ||--o{ VIRTUAL_TAGS : creates
    
    RESOURCES {
        int id PK
        varchar resource_id UK
        varchar name
        varchar cloud
        varchar account_id
        varchar resource_type
        json native_tags
        timestamp created_at
    }
    
    VIRTUAL_TAGS {
        int id PK
        varchar resource_id FK
        varchar tag_key
        varchar tag_value
        varchar source
        float confidence
        boolean auto_applied
        varchar approval_status
        int rule_id FK
        timestamp created_at
    }
    
    RULES {
        int id PK
        varchar rule_name
        varchar condition
        varchar tag_key
        varchar tag_value
        int priority
    }
    
    ML_INFERENCES {
        int id PK
        varchar resource_id FK
        varchar model_version
        json predictions
        timestamp predicted_at
    }
    
    TAG_AUDIT {
        int id PK
        varchar resource_id FK
        varchar action
        varchar tag_key
        varchar old_value
        varchar new_value
        timestamp timestamp
    }
```

### Key Tables

**resources**: Stores cloud resources  
**virtual_tags**: Applied tags (approved/pending)  
**rules**: User-defined tagging rules  
**ml_inferences**: ML prediction history  
**tag_audit**: Complete audit trail  
**scheduler_jobs**: Cron job execution history

---

## 🚀 Deployment Guide

### Local Development (Current Setup)

```bash
# Backend (Docker)
cd python
docker-compose up -d

# Frontend (Local)
cd client
npm install
npm run dev

# Access
Frontend: http://localhost:5173
Backend API: http://localhost:8000
Database: localhost:5432
```

### Production Deployment Options

#### Option 1: Full Docker Deployment

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build: ./python
    environment:
      - DATABASE_URL=postgresql://user:pass@prod-db:5432/vt
      - ENV=production
    ports:
      - "8000:8000"
    restart: always
  
  frontend:
    build: ./client
    ports:
      - "80:80"
    restart: always
  
  postgres:
    image: postgres:15-alpine
    volumes:
      - prod-data:/var/lib/postgresql/data
    restart: always
```

#### Option 2: Cloud Deployment

**Backend → AWS ECS / GCP Cloud Run**
- Container: `python-backend:latest`
- Environment: Production database URL
- Auto-scaling: 2-10 instances

**Frontend → AWS S3 + CloudFront / Vercel**
- Build: `npm run build`
- Deploy: Static files to CDN

**Database → AWS RDS / GCP Cloud SQL**
- PostgreSQL 15
- Multi-AZ deployment
- Automated backups

---

## 🔧 Development Server Setup

### Connect to Dev Server & Database

#### Method 1: Direct Database Connection

**Update backend config:**

```python
# python/app/config.py
class Settings(BaseSettings):
    # Replace with your dev database
    database_url: str = "postgresql://dev_user:dev_pass@dev.yourcompany.com:5432/virtual_tagging"
    
    # Or use environment variable
    database_url: str = Field(..., env='DEV_DATABASE_URL')
```

**Set environment variable:**

```bash
# .env file
DEV_DATABASE_URL=postgresql://user:pass@dev-server.com:5432/vt_db
```

#### Method 2: SSH Tunnel to Dev DB

```bash
# Create SSH tunnel
ssh -L 5432:localhost:5432 user@dev-server.com

# Backend connects to localhost:5432 (tunneled to dev)
DATABASE_URL=postgresql://user:pass@localhost:5432/vt_db
```

#### Method 3: Cloud SQL Proxy (for GCP)

```bash
# Download cloud_sql_proxy
./cloud_sql_proxy -instances=project:region:instance=tcp:5432

# Backend connects to localhost:5432
DATABASE_URL=postgresql://user:pass@localhost:5432/vt_db
```

### Backend Configuration for Dev Server

```python
# python/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # ML Settings
    ml_model_version: str = "v1.0"
    auto_apply_threshold: float = 0.90
    manual_review_threshold: float = 0.70
    
    # Environment-specific
    environment: str = "development"  # or "production"
    debug: bool = True
    
    # Scheduler
    enable_scheduler: bool = True
    discovery_interval: str = "*/2"  # Every 2 minutes
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

**Create `.env` file:**

```bash
# Development
DATABASE_URL=postgresql://dev_user:dev_pass@dev-server:5432/vt_db
ENVIRONMENT=development
DEBUG=true
ENABLE_SCHEDULER=true

# Production
# DATABASE_URL=postgresql://prod_user:prod_pass@prod-db:5432/vt_db
# ENVIRONMENT=production
# DEBUG=false
```

### Frontend Configuration for Dev Server

```javascript
// client/src/services/api.js
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**Create `.env` file:**

```bash
# Development (local backend)
VITE_API_URL=http://localhost:8000/api

# Development (remote backend)
VITE_API_URL=https://api-dev.yourcompany.com/api

# Production
# VITE_API_URL=https://api.yourcompany.com/api
```

---

## 📊 Complete Deployment Checklist

### Development Environment

- [ ] Install Docker & Docker Compose
- [ ] Clone repository
- [ ] Create `.env` files for backend and frontend
- [ ] Run `docker-compose up -d` for backend
- [ ] Run `npm install && npm run dev` for frontend
- [ ] Access http://localhost:5173

### Production Environment

- [ ] Set up production database (PostgreSQL 15+)
- [ ] Configure environment variables
- [ ] Build Docker images
- [ ] Deploy backend container with auto-scaling
- [ ] Build and deploy frontend static files
- [ ] Configure CDN and SSL certificates
- [ ] Set up monitoring and logging
- [ ] Configure automated backups
- [ ] Test end-to-end functionality

---

## 🔐 Security Considerations

### API Security
- Add JWT authentication for production
- Implement rate limiting
- Enable HTTPS only
- Validate all inputs
- Use parameterized queries (already implemented via SQLAlchemy)

### Database Security
- Use connection pooling
- Enable SSL for database connections
- Rotate credentials regularly
- Implement row-level security
- Regular automated backups

### Frontend Security
- Enable Content Security Policy (CSP)
- Implement CSRF protection
- Sanitize user inputs
- Use HTTPS
- Regular dependency updates

---

## 📈 Performance Optimization

### Backend
- **Pagination**: All list endpoints use limit/offset (✅ Implemented)
- **Caching**: Add Redis for frequently accessed data
- **Connection Pooling**: SQLAlchemy async pool
- **Batch Operations**: Bulk tag operations

### Frontend
- **Code Splitting**: Dynamic imports for routes
- **Lazy Loading**: Load components on demand
- **Memoization**: React.memo for expensive components
- **Virtual Scrolling**: For large lists

### Database
- **Indexes**: On resource_id, tag_key, approval_status
- **Partitioning**: For large audit tables
- **Vacuuming**: Regular maintenance
- **Query Optimization**: EXPLAIN ANALYZE for slow queries

---

## 🎯 Next Steps

1. **Add Real Cloud Integration**
   - AWS boto3 SDK
   - GCP google-cloud SDK
   - Azure SDK

2. **Enhance ML Model**
   - Train on historical data
   - Add multi-class classification
   - Implement feedback loop

3. **Add Authentication**
   - JWT tokens
   - User roles (admin, viewer, approver)
   - RBAC for tag approvals

4. **Monitoring & Alerts**
   - Prometheus metrics
   - Grafana dashboards
   - PagerDuty integration

5. **API Documentation**
   - OpenAPI/Swagger spec
   - Interactive API docs
   - Client SDKs

---

## 📞 Support & Resources

**Documentation**: `/DEVELOPER_DOCUMENTATION.md`  
**Automation Guide**: `/AUTOMATION_GUIDE.md`  
**Deployment**: `/DEPLOYMENT_GUIDE.md`  
**Tag Sources**: `/TAG_SOURCES_EXPLAINED.md`

**Database Access**:
```bash
# Local
docker-compose exec postgres psql -U postgres -d virtual_tagging

# Dev Server
psql -h dev-server.com -U dev_user -d virtual_tagging
```

**Logs**:
```bash
# Backend logs
docker-compose logs -f backend

# Scheduler logs
docker-compose logs backend | grep SCHEDULER
```

---

**Built with ❤️ using Python Tornado, React, and PostgreSQL**
