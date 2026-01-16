# Virtual Tags - Architecture Diagrams
## Visual Guide to CloudTuner Virtual Tagging System

**Purpose**: Comprehensive visual architecture reference  
**Audience**: Developers, Architects, Product Managers  
**Last Updated**: 2025-11-25

---

## 📐 Diagram Index

1. [System Overview](#1-system-overview)
2. [Component Architecture](#2-component-architecture)
3. [Data Flow Diagrams](#3-data-flow-diagrams)
4. [API Architecture](#4-api-architecture)
5. [Frontend Components](#5-frontend-components)
6. [Database Schema](#6-database-schema)
7. [Deployment Architecture](#7-deployment-architecture)

---

## 1. System Overview

### 1.1 High-Level Architecture

```mermaid
graph TB
    subgraph "Cloud Providers"
        AWS[AWS<br/>EC2, S3, RDS, etc.]
        GCP[GCP<br/>Compute, Storage, BigQuery]
        AZURE[Azure<br/>VMs, Blob, SQL]
    end
    
    subgraph "Ingestion Layer"
        DISCOVERY[Resource Discovery<br/>Service]
        QUEUE[Message Queue<br/>RabbitMQ]
    end
    
    subgraph "Virtual Tagging Platform"
        direction TB
        API[REST API<br/>virtual_tagger]
        GRAPHQL[GraphQL API<br/>virtual_tagger_graphql]
        WORKER[Worker Service<br/>virtual_tagger_worker]
        SCHEDULER[Scheduler<br/>virtual_tagger_scheduler]
    end
    
    subgraph "Processing Engines"
        NORM[Normalization<br/>Engine]
        ML[ML Inference<br/>Engine]
        COMP[Compliance<br/>Engine]
        RULE[Rule<br/>Engine]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Primary DB)]
        ES[(Elasticsearch<br/>Search Index)]
        NEO[(Neo4j<br/>Graph DB)]
        REDIS[(Redis<br/>Cache)]
    end
    
    subgraph "Presentation Layer"
        DASH[FinOps Dashboard<br/>React/Vue]
        MOBILE[Mobile App]
        CLI[CLI Tool]
    end
    
    subgraph "Alert & Notification"
        HERALD[Herald<br/>Alert Service]
        EMAIL[Email]
        SLACK[Slack]
        WEBHOOK[Webhooks]
    end
    
    AWS --> DISCOVERY
    GCP --> DISCOVERY
    AZURE --> DISCOVERY
    
    DISCOVERY --> QUEUE
    
    QUEUE --> WORKER
    
    WORKER --> NORM
    WORKER --> ML
    WORKER --> COMP
    WORKER --> RULE
    
    NORM --> PG
    ML --> PG
    COMP --> PG
    RULE --> PG
    
    API --> PG
    API --> ES
    API --> REDIS
    
    GRAPHQL --> PG
    GRAPHQL --> ES
    GRAPHQL --> NEO
    
    SCHEDULER --> QUEUE
    
    COMP --> HERALD
    HERALD --> EMAIL
    HERALD --> SLACK
    HERALD --> WEBHOOK
    
    DASH --> API
    DASH --> GRAPHQL
    MOBILE --> API
    CLI --> API
    
    style AWS fill:#FF9900
    style GCP fill:#4285F4
    style AZURE fill:#0078D4
    style ML fill:#9B59B6
    style DASH fill:#3498DB
    style HERALD fill:#E74C3C
```

### 1.2 Simplified 3-Tier Architecture

```mermaid
graph LR
    subgraph "Tier 1: Frontend"
        UI[Dashboard UI<br/>Components]
    end
    
    subgraph "Tier 2: API Layer"
        REST[REST APIs]
        GQL[GraphQL]
    end
    
    subgraph "Tier 3: Backend Services"
        SERVICES[Microservices<br/>Workers, ML, Rules]
        DATA[(Databases<br/>PostgreSQL, ES, Redis)]
    end
    
    UI --> REST
    UI --> GQL
    REST --> SERVICES
    GQL --> SERVICES
    SERVICES --> DATA
    
    style UI fill:#3498DB
    style REST fill:#2ECC71
    style GQL fill:#2ECC71
    style SERVICES fill:#E67E22
    style DATA fill:#95A5A6
```

---

## 2. Component Architecture

### 2.1 Microservices Breakdown

```mermaid
graph TB
    subgraph "virtual_tagger (REST API)"
        REST_TAGS[Tag CRUD<br/>Endpoints]
        REST_RULES[Rule Management<br/>Endpoints]
        REST_COMP[Compliance<br/>Endpoints]
        REST_AUDIT[Audit Trail<br/>Endpoints]
    end
    
    subgraph "virtual_tagger_worker (Background Jobs)"
        WORKER_ING[Ingestion<br/>Worker]
        WORKER_NORM[Normalization<br/>Worker]
        WORKER_INF[Inference<br/>Worker]
        WORKER_COMP[Compliance<br/>Worker]
    end
    
    subgraph "virtual_tagger_scheduler (Cron Jobs)"
        SCHED_REINGEST[Re-ingestion<br/>Every 6h]
        SCHED_COMP[Compliance Sweep<br/>Daily 2 AM]
        SCHED_ML[Model Retraining<br/>Weekly Monday]
        SCHED_CLEANUP[Audit Cleanup<br/>Monthly]
    end
    
    subgraph "virtual_tagger_graphql (Query API)"
        GQL_QUERY[Complex Queries]
        GQL_MUTATION[Mutations]
        GQL_SUB[Subscriptions]
    end
    
    QUEUE[Message Queue]
    
    REST_TAGS --> QUEUE
    REST_RULES --> QUEUE
    REST_COMP --> QUEUE
    
    QUEUE --> WORKER_ING
    QUEUE --> WORKER_NORM
    QUEUE --> WORKER_INF
    QUEUE --> WORKER_COMP
    
    SCHED_REINGEST --> QUEUE
    SCHED_COMP --> QUEUE
    SCHED_ML --> QUEUE
    SCHED_CLEANUP --> QUEUE
    
    style REST_TAGS fill:#3498DB
    style WORKER_ING fill:#2ECC71
    style SCHED_REINGEST fill:#F39C12
    style GQL_QUERY fill:#9B59B6
```

### 2.2 Service Dependencies

```mermaid
graph LR
    UI[Frontend Dashboard]
    
    subgraph "API Gateway"
        NGINX[NGINX<br/>Load Balancer]
    end
    
    subgraph "Services"
        VT[virtual_tagger]
        VG[virtual_tagger_graphql]
        VW[virtual_tagger_worker]
        VS[virtual_tagger_scheduler]
    end
    
    subgraph "External Services"
        AUTH[Auth Service<br/>JWT]
        HERALD[Herald Alerts]
        ML[ML Service]
    end
    
    subgraph "Data Stores"
        PG[(PostgreSQL)]
        ES[(Elasticsearch)]
        REDIS[(Redis)]
    end
    
    UI --> NGINX
    NGINX --> VT
    NGINX --> VG
    
    VT --> AUTH
    VT --> PG
    VT --> ES
    VT --> REDIS
    
    VG --> AUTH
    VG --> PG
    VG --> ES
    
    VW --> ML
    VW --> HERALD
    VW --> PG
    
    VS --> VW
    
    style UI fill:#3498DB
    style VT fill:#2ECC71
    style ML fill:#9B59B6
    style HERALD fill:#E74C3C
```

---

## 3. Data Flow Diagrams

### 3.1 Tag Creation Flow

```mermaid
sequenceDiagram
    actor User
    participant UI as Dashboard
    participant API as REST API
    participant Worker as Background Worker
    participant ML as ML Engine
    participant DB as PostgreSQL
    participant Cache as Redis

    User->>UI: Enter tag key/value
    UI->>UI: Validate input
    UI->>API: POST /virtual-tags/apply
    
    API->>DB: Check resource exists
    DB-->>API: Resource found
    
    API->>DB: Insert virtual_tag
    API->>Cache: Invalidate cache
    
    API->>Worker: Queue inference job
    API-->>UI: 201 Created
    UI-->>User: "Tag applied successfully"
    
    Worker->>ML: Get predictions for resource
    ML-->>Worker: New suggestions
    Worker->>DB: Save ml_inferences
    Worker->>DB: Create audit_log
    
    Worker->>UI: WebSocket: new_suggestions
    UI-->>User: Show AI suggestions
```

### 3.2 Rule-Based Tagging Flow

```mermaid
sequenceDiagram
    participant Scheduler
    participant Queue as Message Queue
    participant Worker
    participant RuleEngine
    participant DB as Database
    participant UI as Dashboard

    Scheduler->>Queue: Trigger rule execution
    Queue->>Worker: Consume job
    
    Worker->>RuleEngine: Execute all enabled rules
    RuleEngine->>DB: Fetch rules (ORDER BY priority)
    
    loop For each rule (by priority)
        RuleEngine->>DB: Fetch matching resources
        RuleEngine->>RuleEngine: Evaluate conditions
        
        alt Conditions match
            RuleEngine->>DB: Apply tags from actions
            RuleEngine->>DB: Log audit trail
        end
    end
    
    RuleEngine-->>Worker: Execution complete
    Worker->>DB: Update rule stats
    Worker->>UI: WebSocket: tags_updated
    UI->>UI: Refresh tag display
```

### 3.3 ML Inference Flow

```mermaid
flowchart TD
    START([New Resource Ingested])
    
    EXTRACT[Extract Features:<br/>- Name patterns<br/>- Resource type<br/>- Configuration<br/>- Cost data]
    
    MODELS{Select Models}
    
    ENV_MODEL[Environment Model<br/>Random Forest]
    TEAM_MODEL[Team Model<br/>Neural Network]
    COST_MODEL[Cost Center Model<br/>XGBoost]
    
    ENV_PRED[Predict: environment]
    TEAM_PRED[Predict: team]
    COST_PRED[Predict: cost-center]
    
    ENSEMBLE[Ensemble Scoring]
    
    CONFIDENCE{Confidence<br/>Score?}
    
    AUTO_APPLY[Auto-apply<br/>≥90%]
    SUGGEST[Suggest for review<br/>70-89%]
    RECOMMEND[Show as option<br/><70%]
    
    SAVE[Save to DB]
    
    NOTIFY[Notify UI]
    
    END([Complete])
    
    START --> EXTRACT
    EXTRACT --> MODELS
    
    MODELS --> ENV_MODEL
    MODELS --> TEAM_MODEL
    MODELS --> COST_MODEL
    
    ENV_MODEL --> ENV_PRED
    TEAM_MODEL --> TEAM_PRED
    COST_MODEL --> COST_PRED
    
    ENV_PRED --> ENSEMBLE
    TEAM_PRED --> ENSEMBLE
    COST_PRED --> ENSEMBLE
    
    ENSEMBLE --> CONFIDENCE
    
    CONFIDENCE -->|High| AUTO_APPLY
    CONFIDENCE -->|Medium| SUGGEST
    CONFIDENCE -->|Low| RECOMMEND
    
    AUTO_APPLY --> SAVE
    SUGGEST --> SAVE
    RECOMMEND --> SAVE
    
    SAVE --> NOTIFY
    NOTIFY --> END
    
    style START fill:#2ECC71
    style AUTO_APPLY fill:#2ECC71
    style SUGGEST fill:#F39C12
    style RECOMMEND fill:#E74C3C
    style END fill:#3498DB
```

### 3.4 Compliance Check Flow

```mermaid
flowchart TD
    START([Daily Compliance Sweep])
    
    FETCH_POLICIES[Fetch All Enabled<br/>Compliance Policies]
    
    LOOP_POLICIES{For Each<br/>Policy}
    
    FETCH_RESOURCES[Fetch Resources<br/>in Scope]
    
    LOOP_RESOURCES{For Each<br/>Resource}
    
    CHECK_TYPE{Policy<br/>Type?}
    
    REQ_TAGS[Check Required Tags]
    VAL_TAGS[Validate Tag Values]
    COND_REQ[Check Conditional Requirements]
    TAG_FORMAT[Validate Tag Format]
    TAG_COUNT[Check Tag Count]
    
    COMPLIANT{Is<br/>Compliant?}
    
    SAVE_OK[Save Compliant Status]
    SAVE_VIOLATION[Save Violation]
    
    SEVERITY{Severity?}
    
    ALERT[Send Alert<br/>via Herald]
    
    LOG[Log to Audit Trail]
    
    NEXT_RESOURCE[Next Resource]
    NEXT_POLICY[Next Policy]
    
    DONE([Complete])
    
    START --> FETCH_POLICIES
    FETCH_POLICIES --> LOOP_POLICIES
    
    LOOP_POLICIES -->|Yes| FETCH_RESOURCES
    LOOP_POLICIES -->|No| DONE
    
    FETCH_RESOURCES --> LOOP_RESOURCES
    
    LOOP_RESOURCES -->|Yes| CHECK_TYPE
    LOOP_RESOURCES -->|No| NEXT_POLICY
    
    CHECK_TYPE -->|REQUIRED_TAGS| REQ_TAGS
    CHECK_TYPE -->|VALUE_VALIDATION| VAL_TAGS
    CHECK_TYPE -->|CONDITIONAL_REQUIREMENT| COND_REQ
    CHECK_TYPE -->|TAG_FORMAT| TAG_FORMAT
    CHECK_TYPE -->|TAG_COUNT| TAG_COUNT
    
    REQ_TAGS --> COMPLIANT
    VAL_TAGS --> COMPLIANT
    COND_REQ --> COMPLIANT
    TAG_FORMAT --> COMPLIANT
    TAG_COUNT --> COMPLIANT
    
    COMPLIANT -->|Yes| SAVE_OK
    COMPLIANT -->|No| SAVE_VIOLATION
    
    SAVE_OK --> LOG
    SAVE_VIOLATION --> SEVERITY
    
    SEVERITY -->|CRITICAL/HIGH| ALERT
    SEVERITY -->|MEDIUM/LOW| LOG
    
    ALERT --> LOG
    LOG --> NEXT_RESOURCE
    NEXT_RESOURCE --> LOOP_RESOURCES
    
    NEXT_POLICY --> LOOP_POLICIES
    
    style START fill:#2ECC71
    style COMPLIANT fill:#F39C12
    style ALERT fill:#E74C3C
    style DONE fill:#3498DB
```

---

## 4. API Architecture

### 4.1 API Endpoint Map

```mermaid
graph TB
    subgraph "API Gateway"
        NGINX[NGINX<br/>Port 443]
    end
    
    subgraph "Virtual Tags API"
        GET_TAGS[GET /resources/{id}/virtual-tags]
        POST_TAGS[POST /virtual-tags/apply]
        PUT_TAGS[PUT /virtual-tags/{id}]
        DEL_TAGS[DELETE /virtual-tags/{id}]
        BULK_TAGS[POST /virtual-tags/bulk-apply]
    end
    
    subgraph "Tag Rules API"
        GET_RULES[GET /tag-rules]
        POST_RULES[POST /tag-rules]
        EXEC_RULE[POST /tag-rules/{id}/execute]
        TEST_RULE[POST /tag-rules/test]
    end
    
    subgraph "Compliance API"
        GET_STATUS[GET /compliance/status]
        GET_VIOL[GET /compliance/violations]
        POST_POLICY[POST /compliance/policies]
        RECHECK[POST /compliance/recheck]
    end
    
    subgraph "ML API"
        POST_INFER[POST /ml/infer]
        POST_FEEDBACK[POST /ml/feedback]
        GET_MODELS[GET /ml/models]
    end
    
    subgraph "Audit API"
        GET_TRAIL[GET /audit/trail]
        GET_REPORTS[GET /audit/reports]
    end
    
    NGINX --> GET_TAGS
    NGINX --> POST_TAGS
    NGINX --> GET_RULES
    NGINX --> POST_RULES
    NGINX --> GET_STATUS
    NGINX --> POST_INFER
    NGINX --> GET_TRAIL
    
    style NGINX fill:#2ECC71
    style GET_TAGS fill:#3498DB
    style POST_TAGS fill:#E67E22
    style GET_STATUS fill:#9B59B6
    style POST_INFER fill:#E74C3C
```

### 4.2 GraphQL Schema Structure

```mermaid
graph TB
    subgraph "Query Types"
        Q_RESOURCE[resource<br/>resources]
        Q_TAGS[virtualTag<br/>virtualTags]
        Q_RULES[tagRule<br/>tagRules]
        Q_COMP[complianceStatus<br/>compliancePolicies]
        Q_SCHEMA[tagSchema]
    end
    
    subgraph "Object Types"
        T_RESOURCE[Resource]
        T_TAG[VirtualTag]
        T_RULE[TagRule]
        T_COMP[ComplianceStatus]
        T_SUGG[TagSuggestion]
    end
    
    subgraph "Mutation Types"
        M_APPLY[applyVirtualTags]
        M_UPDATE[updateVirtualTag]
        M_CREATE_RULE[createTagRule]
        M_CREATE_POLICY[createCompliancePolicy]
        M_FEEDBACK[submitMLFeedback]
    end
    
    Q_RESOURCE --> T_RESOURCE
    Q_TAGS --> T_TAG
    Q_RULES --> T_RULE
    Q_COMP --> T_COMP
    
    T_RESOURCE --> T_TAG
    T_RESOURCE --> T_COMP
    T_RESOURCE --> T_SUGG
    
    M_APPLY --> T_RESOURCE
    M_UPDATE --> T_TAG
    M_CREATE_RULE --> T_RULE
    
    style Q_RESOURCE fill:#3498DB
    style T_RESOURCE fill:#2ECC71
    style M_APPLY fill:#E67E22
```

---

## 5. Frontend Components

### 5.1 Component Hierarchy

```mermaid
graph TB
    APP[App Root]
    
    subgraph "Pages"
        DASH_PAGE[Dashboard Page]
        RULES_PAGE[Rules Manager Page]
        COMP_PAGE[Compliance Page]
        AUDIT_PAGE[Audit Trail Page]
    end
    
    subgraph "Dashboard Components"
        RES_LIST[Resource List]
        RES_DETAIL[Resource Detail]
        TAG_PANEL[Tag Panel]
    end
    
    subgraph "Shared Components"
        TAG_BADGE[Tag Badge]
        TAG_INPUT[Tag Input]
        CONF_BADGE[Confidence Badge]
        SUGG_CARD[Suggestion Card]
        COMP_ALERT[Compliance Alert]
    end
    
    subgraph "Rule Components"
        RULE_LIST[Rule List]
        RULE_BUILDER[Rule Builder]
        COND_ROW[Condition Row]
        ACTION_ROW[Action Row]
    end
    
    subgraph "State Management"
        TAG_STORE[Tag Store]
        RULE_STORE[Rule Store]
        COMP_STORE[Compliance Store]
    end
    
    APP --> DASH_PAGE
    APP --> RULES_PAGE
    APP --> COMP_PAGE
    APP --> AUDIT_PAGE
    
    DASH_PAGE --> RES_LIST
    DASH_PAGE --> RES_DETAIL
    
    RES_DETAIL --> TAG_PANEL
    
    TAG_PANEL --> TAG_BADGE
    TAG_PANEL --> TAG_INPUT
    TAG_PANEL --> SUGG_CARD
    TAG_PANEL --> COMP_ALERT
    
    TAG_BADGE --> CONF_BADGE
    
    RULES_PAGE --> RULE_LIST
    RULES_PAGE --> RULE_BUILDER
    
    RULE_BUILDER --> COND_ROW
    RULE_BUILDER --> ACTION_ROW
    
    TAG_PANEL --> TAG_STORE
    RULE_BUILDER --> RULE_STORE
    COMP_ALERT --> COMP_STORE
    
    style APP fill:#3498DB
    style TAG_PANEL fill:#2ECC71
    style TAG_STORE fill:#E67E22
```

### 5.2 State Management Flow

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    Idle --> Loading: Fetch Tags
    Loading --> Success: Data Received
    Loading --> Error: API Error
    
    Success --> Idle: User Action
    Error --> Idle: Retry
    
    Success --> Updating: Apply Tag
    Updating --> Success: Tag Applied
    Updating --> Error: Apply Failed
    
    Success --> Suggesting: Request ML Suggestions
    Suggesting --> Success: Suggestions Received
    
    state Success {
        [*] --> DisplayTags
        DisplayTags --> ShowCompliance
        ShowCompliance --> ShowSuggestions
    }
```

---

## 6. Database Schema

### 6.1 Entity Relationship Diagram

```mermaid
erDiagram
    RESOURCES ||--o{ VIRTUAL_TAGS : has
    RESOURCES ||--o{ COMPLIANCE_STATUS : has
    RESOURCES ||--o{ ML_INFERENCES : has
    
    VIRTUAL_TAGS }o--|| TAG_SCHEMA : follows
    VIRTUAL_TAGS }o--o| VIRTUAL_TAG_RULES : applied_by
    
    COMPLIANCE_POLICIES ||--o{ COMPLIANCE_STATUS : evaluates
    
    VIRTUAL_TAG_RULES ||--o{ TAG_AUDIT : triggers
    VIRTUAL_TAGS ||--o{ TAG_AUDIT : logged_in
    
    RESOURCES {
        uuid id PK
        string provider
        string resource_id
        string resource_type
        string name
        jsonb metadata
    }
    
    VIRTUAL_TAGS {
        uuid id PK
        uuid resource_id FK
        string tag_key
        string tag_value
        string source
        float confidence
        uuid rule_id FK
    }
    
    VIRTUAL_TAG_RULES {
        uuid id PK
        string rule_name
        int priority
        jsonb conditions
        jsonb actions
    }
    
    TAG_SCHEMA {
        uuid id PK
        string tag_key UK
        string display_name
        string data_type
        array allowed_values
        boolean required
    }
    
    COMPLIANCE_POLICIES {
        uuid id PK
        string policy_name
        string policy_type
        string severity
        jsonb rules
    }
    
    COMPLIANCE_STATUS {
        uuid id PK
        uuid resource_id FK
        uuid policy_id FK
        boolean is_compliant
        jsonb violations
    }
    
    ML_INFERENCES {
        uuid id PK
        uuid resource_id FK
        string model_version
        jsonb predictions
    }
    
    TAG_AUDIT {
        uuid id PK
        uuid resource_id FK
        string action
        string tag_key
        string old_value
        string new_value
    }
```

### 6.2 Table Dependencies

```mermaid
graph TD
    RESOURCES[resources<br/>Primary table]
    
    VT[virtual_tags<br/>Tag assignments]
    RULES[virtual_tag_rules<br/>Automation rules]
    SCHEMA[tag_schema<br/>Tag definitions]
    
    POLICIES[compliance_policies<br/>Governance rules]
    STATUS[compliance_status<br/>Compliance state]
    
    ML[ml_inferences<br/>AI predictions]
    AUDIT[tag_audit<br/>Change history]
    
    RESOURCES --> VT
    RESOURCES --> STATUS
    RESOURCES --> ML
    RESOURCES --> AUDIT
    
    SCHEMA --> VT
    RULES --> VT
    RULES --> AUDIT
    
    POLICIES --> STATUS
    
    style RESOURCES fill:#3498DB
    style VT fill:#2ECC71
    style POLICIES fill:#E67E22
    style ML fill:#9B59B6
```

---

## 7. Deployment Architecture

### 7.1 Kubernetes Architecture

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Ingress"
            INGRESS[NGINX Ingress<br/>TLS Termination]
        end
        
        subgraph "API Pods"
            API1[virtual_tagger<br/>Pod 1]
            API2[virtual_tagger<br/>Pod 2]
            API3[virtual_tagger<br/>Pod 3]
        end
        
        subgraph "GraphQL Pods"
            GQL1[virtual_tagger_graphql<br/>Pod 1]
            GQL2[virtual_tagger_graphql<br/>Pod 2]
        end
        
        subgraph "Worker Pods"
            WORKER1[virtual_tagger_worker<br/>Pod 1]
            WORKER2[virtual_tagger_worker<br/>Pod 2]
            WORKER3[virtual_tagger_worker<br/>Pod 3]
        end
        
        subgraph "CronJobs"
            CRON1[Re-ingestion<br/>Every 6h]
            CRON2[Compliance<br/>Daily 2 AM]
            CRON3[ML Training<br/>Weekly]
        end
        
        subgraph "Services"
            SVC_API[API Service<br/>ClusterIP]
            SVC_GQL[GraphQL Service<br/>ClusterIP]
        end
    end
    
    subgraph "External Data Stores"
        PG[(RDS PostgreSQL<br/>Multi-AZ)]
        ES[(Elasticsearch<br/>Cluster)]
        REDIS[(ElastiCache<br/>Redis)]
        RABBIT[RabbitMQ<br/>Cluster]
    end
    
    INGRESS --> SVC_API
    INGRESS --> SVC_GQL
    
    SVC_API --> API1
    SVC_API --> API2
    SVC_API --> API3
    
    SVC_GQL --> GQL1
    SVC_GQL --> GQL2
    
    API1 --> PG
    API1 --> ES
    API1 --> REDIS
    
    WORKER1 --> RABBIT
    WORKER2 --> RABBIT
    WORKER3 --> RABBIT
    
    WORKER1 --> PG
    WORKER1 --> ES
    
    CRON1 --> RABBIT
    CRON2 --> RABBIT
    CRON3 --> RABBIT
    
    style INGRESS fill:#2ECC71
    style API1 fill:#3498DB
    style WORKER1 fill:#E67E22
    style PG fill:#95A5A6
```

### 7.2 Multi-Region Deployment

```mermaid
graph TB
    subgraph "Global"
        DNS[Route 53<br/>Global DNS]
        CDN[CloudFront<br/>CDN]
    end
    
    subgraph "Region: US-EAST-1"
        LB_US[ALB<br/>Load Balancer]
        K8S_US[EKS Cluster<br/>Virtual Tagger]
        PG_US[(RDS Primary<br/>US-EAST-1)]
        ES_US[(ES Domain<br/>US-EAST-1)]
    end
    
    subgraph "Region: EU-WEST-1"
        LB_EU[ALB<br/>Load Balancer]
        K8S_EU[EKS Cluster<br/>Virtual Tagger]
        PG_EU[(RDS Replica<br/>EU-WEST-1)]
        ES_EU[(ES Domain<br/>EU-WEST-1)]
    end
    
    DNS --> CDN
    CDN --> LB_US
    CDN --> LB_EU
    
    LB_US --> K8S_US
    LB_EU --> K8S_EU
    
    K8S_US --> PG_US
    K8S_US --> ES_US
    
    K8S_EU --> PG_EU
    K8S_EU --> ES_EU
    
    PG_US -.Replication.-> PG_EU
    
    style DNS fill:#2ECC71
    style K8S_US fill:#3498DB
    style K8S_EU fill:#3498DB
    style PG_US fill:#E67E22
```

### 7.3 Security Architecture

```mermaid
graph TB
    subgraph "Public Internet"
        USER[Users]
    end
    
    subgraph "DMZ"
        WAF[AWS WAF<br/>Web Application Firewall]
        ALB[Application<br/>Load Balancer]
    end
    
    subgraph "Application Tier (Private Subnet)"
        API[API Pods<br/>virtual_tagger]
        WORKER[Worker Pods]
    end
    
    subgraph "Data Tier (Private Subnet)"
        PG[(PostgreSQL<br/>Encrypted at Rest)]
        ES[(Elasticsearch<br/>Encrypted)]
        REDIS[(Redis<br/>In-memory)]
    end
    
    subgraph "Security Services"
        KMS[AWS KMS<br/>Key Management]
        SECRETS[Secrets Manager]
        IAM[IAM Roles<br/>RBAC]
    end
    
    USER --> WAF
    WAF --> ALB
    ALB --> API
    
    API --> IAM
    API --> SECRETS
    API --> PG
    API --> ES
    API --> REDIS
    
    WORKER --> IAM
    WORKER --> SECRETS
    WORKER --> PG
    
    PG --> KMS
    ES --> KMS
    
    style WAF fill:#E74C3C
    style KMS fill:#E67E22
    style IAM fill:#9B59B6
```

---

## 8. Integration Patterns

### 8.1 Event-Driven Architecture

```mermaid
graph LR
    subgraph "Event Sources"
        AWS_EVENT[AWS EventBridge]
        GCP_EVENT[GCP Pub/Sub]
        AZURE_EVENT[Azure Event Grid]
    end
    
    subgraph "Event Ingestion"
        LAMBDA[Lambda Function<br/>Event Processor]
    end
    
    subgraph "Message Queue"
        QUEUE[RabbitMQ<br/>virtual_tags.ingestion]
    end
    
    subgraph "Workers"
        WORKER1[Worker Pod 1]
        WORKER2[Worker Pod 2]
        WORKER3[Worker Pod 3]
    end
    
    subgraph "Processing"
        NORM[Normalization]
        ML[ML Inference]
        RULES[Rule Engine]
    end
    
    AWS_EVENT --> LAMBDA
    GCP_EVENT --> LAMBDA
    AZURE_EVENT --> LAMBDA
    
    LAMBDA --> QUEUE
    
    QUEUE --> WORKER1
    QUEUE --> WORKER2
    QUEUE --> WORKER3
    
    WORKER1 --> NORM
    WORKER1 --> ML
    WORKER1 --> RULES
    
    style AWS_EVENT fill:#FF9900
    style GCP_EVENT fill:#4285F4
    style AZURE_EVENT fill:#0078D4
    style QUEUE fill:#E67E22
```

---

## 9. Performance & Scalability

### 9.1 Caching Strategy

```mermaid
graph TB
    CLIENT[Client Request]
    
    CDN{CDN<br/>Cache?}
    REDIS{Redis<br/>Cache?}
    API[API Server]
    DB[(Database)]
    
    CDN_HIT[Return from CDN<br/>~10ms]
    REDIS_HIT[Return from Redis<br/>~50ms]
    DB_HIT[Return from DB<br/>~200ms]
    
    CLIENT --> CDN
    CDN -->|HIT| CDN_HIT
    CDN -->|MISS| REDIS
    
    REDIS -->|HIT| REDIS_HIT
    REDIS -->|MISS| API
    
    API --> DB
    DB --> DB_HIT
    
    DB_HIT -.Cache.-> REDIS
    REDIS_HIT -.Cache.-> CDN
    
    style CDN_HIT fill:#2ECC71
    style REDIS_HIT fill:#F39C12
    style DB_HIT fill:#E74C3C
```

### 9.2 Auto-Scaling Configuration

```mermaid
graph TB
    subgraph "Metrics"
        CPU[CPU Usage<br/>>70%]
        MEM[Memory Usage<br/>>80%]
        QUEUE[Queue Depth<br/>>1000]
        RPS[Requests/sec<br/>>500]
    end
    
    subgraph "HPA - Horizontal Pod Autoscaler"
        HPA[HPA Controller]
    end
    
    subgraph "Current Pods"
        POD1[Pod 1]
        POD2[Pod 2]
        POD3[Pod 3]
    end
    
    subgraph "Scale Events"
        SCALE_UP[Scale Up<br/>Add 2 Pods]
        SCALE_DOWN[Scale Down<br/>Remove 1 Pod]
    end
    
    CPU --> HPA
    MEM --> HPA
    QUEUE --> HPA
    RPS --> HPA
    
    HPA -.Monitor.-> POD1
    HPA -.Monitor.-> POD2
    HPA -.Monitor.-> POD3
    
    HPA -->|Threshold exceeded| SCALE_UP
    HPA -->|Under capacity| SCALE_DOWN
    
    style SCALE_UP fill:#2ECC71
    style SCALE_DOWN fill:#E74C3C
```

---

## 10. Monitoring & Observability

### 10.1 Monitoring Stack

```mermaid
graph TB
    subgraph "Applications"
        API[API Pods]
        WORKER[Worker Pods]
    end
    
    subgraph "Metrics Collection"
        PROM[Prometheus<br/>Metrics Scraper]
    end
    
    subgraph "Log Aggregation"
        FLUENT[Fluentd<br/>Log Collector]
        ES_LOG[(Elasticsearch<br/>Log Storage)]
    end
    
    subgraph "Tracing"
        JAEGER[Jaeger<br/>Distributed Tracing]
    end
    
    subgraph "Visualization"
        GRAFANA[Grafana<br/>Dashboards]
        KIBANA[Kibana<br/>Log Analysis]
    end
    
    subgraph "Alerting"
        ALERT[AlertManager]
        PAGER[PagerDuty]
    end
    
    API --> PROM
    API --> FLUENT
    API --> JAEGER
    
    WORKER --> PROM
    WORKER --> FLUENT
    WORKER --> JAEGER
    
    FLUENT --> ES_LOG
    ES_LOG --> KIBANA
    
    PROM --> GRAFANA
    PROM --> ALERT
    
    ALERT --> PAGER
    
    style PROM fill:#E67E22
    style GRAFANA fill:#F39C12
    style ALERT fill:#E74C3C
```

---

## 📚 Diagram Legend

### Colors
- 🟦 **Blue (#3498DB)**: Frontend/UI components
- 🟩 **Green (#2ECC71)**: API/Gateway services
- 🟧 **Orange (#E67E22)**: Backend/Worker services
- 🟪 **Purple (#9B59B6)**: ML/AI services
- 🟥 **Red (#E74C3C)**: Alerts/Security
- ⬜ **Gray (#95A5A6)**: Data stores

### Shapes
- 📦 **Rectangle**: Component/Service
- 🗄️ **Cylinder**: Database
- 💠 **Diamond**: Decision point
- 🔄 **Parallelogram**: Data/Message
- ⚫ **Circle**: Start/End state

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-25  
**Maintained By**: Architecture Team  
**Next Review**: After Phase 1 deployment
