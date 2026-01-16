# CloudTuner Virtual Tagging - Architecture Diagrams

This document contains all Mermaid architecture diagrams for the CloudTuner Virtual Tagging system.

---

## 1. High-Level System Architecture

This diagram shows the complete end-to-end architecture from cloud providers through all processing layers to the dashboard.

```mermaid
graph TB
    subgraph "Cloud Providers"
        AWS[AWS Resources]
        GCP[GCP Resources]
        AZURE[Azure Resources]
    end

    subgraph "Ingestion Layer"
        RD[Resource Discovery<br/>Service]
        MQ[Message Queue<br/>RabbitMQ]
    end

    subgraph "Virtual Tagging Microservices"
        VT[virtual_tagger<br/>REST API]
        VW[virtual_tagger_worker<br/>Async Processing]
        VS[virtual_tagger_scheduler<br/>CronJobs]
        VG[virtual_tagger_graphql<br/>Query API]
    end

    subgraph "Data Storage"
        PG[(PostgreSQL<br/>Tags & Rules)]
        ES[(Elasticsearch<br/>Search Index)]
        NEO[(Neo4j<br/>Graph Relations)]
    end

    subgraph "ML & Inference"
        ML[ML Models<br/>Tag Inference]
        IM[(Inference Models<br/>Storage)]
    end

    subgraph "Alerting"
        H[herald<br/>Alert Service]
    end

    subgraph "Frontend"
        UI[FinOps Dashboard<br/>Virtual Tags Only]
    end

    AWS --> RD
    GCP --> RD
    AZURE --> RD

    RD --> MQ
    MQ --> VW

    VW --> PG
    VW --> ES
    VW --> NEO
    VW --> ML
    VW --> H

    ML <--> IM

    VT --> PG
    VT --> ES
    VT --> NEO

    VG --> PG
    VG --> ES
    VG --> NEO

    VS --> MQ

    UI --> VT
    UI --> VG
```

---

## 2. ML Model Architecture

This diagram illustrates the machine learning pipeline for tag inference with feedback loop.

```mermaid
graph LR
    A[Resource Metadata] --> B[Feature Extraction]
    B --> C[ML Inference Models]
    C --> D[Tag Predictions]
    D --> E[Confidence Scoring]
    E --> F[Dashboard Display]
    F --> G[User Feedback Loop]
    G --> C
```

---

## 3. Component Deployment Architecture

This diagram shows the Kubernetes deployment with HPA-enabled API tier, queue-based worker scaling, and managed service integrations.

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "API Tier - HPA Enabled"
            REST1[REST API Pod 1]
            REST2[REST API Pod 2]
            REST3[REST API Pod N]
            
            GQL1[GraphQL API Pod 1]
            GQL2[GraphQL API Pod 2]
        end
        
        subgraph "Worker Tier - Queue-Based Scaling"
            WORKER1[Worker Pod 1]
            WORKER2[Worker Pod 2]
            WORKER3[Worker Pod N]
        end
        
        subgraph "Scheduler Tier - CronJobs"
            CRON1[Reingest CronJob]
            CRON2[Compliance CronJob]
            CRON3[ML Training CronJob]
        end
        
        subgraph "ML Tier"
            ML_SVC[ML Inference Service]
        end
    end
    
    subgraph "Managed Services"
        RDS[Amazon RDS PostgreSQL<br/>or Cloud SQL]
        ES_SVC[Elasticsearch Service<br/>AWS/Elastic Cloud]
        NEO_SVC[Neo4j Aura]
        REDIS_SVC[ElastiCache Redis<br/>or Memorystore]
        MQ_SVC[Amazon MQ RabbitMQ<br/>or Cloud Pub/Sub]
    end
    
    subgraph "Load Balancing"
        ALB[Application Load Balancer]
        INGRESS[Kubernetes Ingress]
    end
    
    ALB --> INGRESS
    INGRESS --> REST1
    INGRESS --> REST2
    INGRESS --> REST3
    INGRESS --> GQL1
    INGRESS --> GQL2
    
    REST1 --> RDS
    REST1 --> ES_SVC
    REST1 --> REDIS_SVC
    
    WORKER1 --> MQ_SVC
    WORKER2 --> MQ_SVC
    WORKER3 --> MQ_SVC
    
    WORKER1 --> RDS
    WORKER1 --> ES_SVC
    WORKER1 --> NEO_SVC
    
    ML_SVC --> REDIS_SVC
    
    CRON1 --> MQ_SVC
    CRON2 --> MQ_SVC
    CRON3 --> ML_SVC
```

---

## 4. Data Flow Sequence Diagram

This diagram illustrates the complete event-driven flow from cloud resource change to dashboard display.

```mermaid
sequenceDiagram
    participant Cloud as Cloud Provider
    participant RD as Resource Discovery
    participant MQ as Message Queue
    participant Worker as Tagging Worker
    participant ML as ML Engine
    participant DB as PostgreSQL
    participant ES as Elasticsearch
    participant Herald as Alert Service
    participant UI as Dashboard

    Cloud->>RD: Resource change event
    RD->>MQ: Publish ingestion event
    MQ->>Worker: Consume event
    
    Worker->>Worker: Normalize tags
    Worker->>ML: Request tag inference
    ML-->>Worker: Predicted tags + confidence
    
    Worker->>DB: Store virtual tags
    Worker->>ES: Index for search
    
    Worker->>Worker: Evaluate compliance
    
    alt Violation detected
        Worker->>Herald: Send alert event
        Herald->>Herald: Dispatch notifications
    end
    
    UI->>DB: Query virtual tags
    DB-->>UI: Return tag data
    UI->>ML: Request suggestions
    ML-->>UI: AI recommendations
    UI->>UI: Render dashboard
```

---

## 5. Detailed Multi-Cloud System Architecture

This diagram shows the comprehensive architecture including all cloud resources, processing layers, and monitoring.

```mermaid
graph TB
    subgraph "Multi-Cloud Resources"
        subgraph AWS
            EC2[EC2 Instances]
            S3[S3 Buckets]
            RDS[RDS Databases]
            Lambda[Lambda Functions]
        end
        
        subgraph GCP
            GCE[Compute Engine]
            GCS[Cloud Storage]
            BQ[BigQuery]
            GKE[GKE Clusters]
        end
        
        subgraph Azure
            VM[Virtual Machines]
            BLOB[Blob Storage]
            SQL[Azure SQL]
            AKS[AKS Clusters]
        end
    end

    subgraph "Ingestion & Processing Layer"
        API_GW[API Gateway<br/>Rate Limiting & Auth]
        
        subgraph "Resource Discovery"
            RD_AWS[AWS Collector]
            RD_GCP[GCP Collector]
            RD_AZURE[Azure Collector]
        end
        
        MQ[Message Queue<br/>RabbitMQ/SQS]
        
        subgraph "Processing Workers"
            W1[Ingestion Worker]
            W2[Normalization Worker]
            W3[Inference Worker]
            W4[Compliance Worker]
        end
    end

    subgraph "Virtual Tagging Platform"
        subgraph "API Services"
            REST[REST API<br/>virtual_tagger]
            GQL[GraphQL API<br/>virtual_tagger_graphql]
        end
        
        subgraph "Background Services"
            WORKER[Worker Service<br/>virtual_tagger_worker]
            SCHED[Scheduler Service<br/>virtual_tagger_scheduler]
        end
        
        subgraph "ML Services"
            ML_TRAIN[Training Pipeline]
            ML_INFERENCE[Inference Engine]
            ML_MODELS[(Model Registry)]
        end
    end

    subgraph "Data Layer"
        subgraph "Databases"
            PG[(PostgreSQL<br/>Primary Data)]
            ES[(Elasticsearch<br/>Search & Analytics)]
            NEO[(Neo4j<br/>Relationships)]
            REDIS[(Redis<br/>Cache)]
        end
        
        subgraph "Object Storage"
            S3_STORAGE[S3/GCS<br/>Model Artifacts & Logs]
        end
    end

    subgraph "Alerting & Notifications"
        HERALD[Herald Service<br/>Alert Manager]
        
        subgraph "Notification Channels"
            EMAIL[Email]
            SLACK[Slack]
            WEBHOOK[Webhooks]
        end
    end

    subgraph "Frontend"
        WEB[Web Dashboard<br/>React/Vue]
        MOBILE[Mobile App<br/>React Native]
    end

    subgraph "Monitoring & Observability"
        PROM[Prometheus<br/>Metrics]
        GRAFANA[Grafana<br/>Dashboards]
        ELK[ELK Stack<br/>Logs]
    end

    %% Connections
    EC2 --> RD_AWS
    S3 --> RD_AWS
    RDS --> RD_AWS
    Lambda --> RD_AWS
    
    GCE --> RD_GCP
    GCS --> RD_GCP
    BQ --> RD_GCP
    GKE --> RD_GCP
    
    VM --> RD_AZURE
    BLOB --> RD_AZURE
    SQL --> RD_AZURE
    AKS --> RD_AZURE
    
    RD_AWS --> MQ
    RD_GCP --> MQ
    RD_AZURE --> MQ
    
    MQ --> W1
    W1 --> W2
    W2 --> W3
    W3 --> W4
    
    W1 --> PG
    W2 --> PG
    W3 --> ML_INFERENCE
    W4 --> PG
    
    ML_INFERENCE --> ML_MODELS
    ML_TRAIN --> ML_MODELS
    
    PG --> ES
    PG --> NEO
    
    REST --> PG
    REST --> ES
    REST --> REDIS
    
    GQL --> PG
    GQL --> ES
    GQL --> NEO
    
    SCHED --> MQ
    
    W4 --> HERALD
    HERALD --> EMAIL
    HERALD --> SLACK
    HERALD --> WEBHOOK
    
    WEB --> API_GW
    MOBILE --> API_GW
    
    API_GW --> REST
    API_GW --> GQL
    
    REST --> PROM
    WORKER --> PROM
    SCHED --> PROM
    
    PROM --> GRAFANA
    
    REST --> ELK
    WORKER --> ELK
    SCHED --> ELK
```

---

## 6. User Flow: View Resource Tags

```mermaid
graph LR
    A[User opens dashboard] --> B[View resources list]
    B --> C[Filter by compliance status]
    C --> D[Click resource]
    D --> E[View virtual tags only]
    E --> F{Tags complete?}
    F -->|Yes| G[Review cost allocation]
    F -->|No| H[View AI suggestions]
    H --> I[Apply suggested tags]
    I --> J[Confirm application]
    J --> K[Tags updated]
```

---

## 7. User Flow: Bulk Tag Application

```mermaid
graph LR
    A[Select multiple resources] --> B[Choose bulk action]
    B --> C[Define tag key/value]
    C --> D[Preview changes]
    D --> E{Confirm?}
    E -->|Yes| F[Apply to all selected]
    E -->|No| G[Cancel operation]
    F --> H[Background job queued]
    H --> I[Progress notification]
    I --> J[Completion confirmation]
```

---

## 8. User Flow: Compliance Remediation

```mermaid
graph LR
    A[Compliance alert received] --> B[Open violations dashboard]
    B --> C[View affected resources]
    C --> D[Select auto-remediation]
    D --> E{AI suggestions available?}
    E -->|Yes| F[Review AI recommendations]
    E -->|No| G[Manual tag input]
    F --> H[Accept suggestions]
    G --> H
    H --> I[Apply tags]
    I --> J[Re-evaluate compliance]
    J --> K[Mark as resolved]
```

---

## Usage Notes

### Rendering Mermaid Diagrams

These diagrams can be rendered in:
- **GitHub/GitLab**: Automatically renders Mermaid in markdown
- **VS Code**: Install "Markdown Preview Mermaid Support" extension
- **Confluence**: Use Mermaid macro
- **Documentation sites**: MkDocs, Docusaurus, GitBook support Mermaid
- **Online**: [mermaid.live](https://mermaid.live) for editing and export

### Exporting to Images

To export diagrams as PNG/SVG:
1. Use [mermaid-cli](https://github.com/mermaid-js/mermaid-cli)
2. Use online editor at mermaid.live
3. Use VS Code extension "Markdown PDF"
4. Use draw.io with Mermaid plugin

### Diagram Descriptions

| Diagram | Purpose | Complexity |
|---------|---------|------------|
| High-Level Architecture | Overview of all system components | Medium |
| ML Model Architecture | Machine learning pipeline flow | Low |
| Component Deployment | Kubernetes infrastructure details | High |
| Data Flow Sequence | Event processing timeline | Medium |
| Multi-Cloud System | Complete detailed architecture | Very High |
| User Flows (3) | User interaction patterns | Low |

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-19  
**Related Document**: [CloudTuner-Virtual-Tagging-Complete-Technical-Documentation.md](file:///c:/Users/LENOVO/Desktop/my_docs/vt/CloudTuner-Virtual-Tagging-Complete-Technical-Documentation.md)
