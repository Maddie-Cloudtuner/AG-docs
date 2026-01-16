# Kubernetes Stack Architecture Diagrams

## 1. High-Level Integration Architecture

This diagram illustrates how the customer's Kubernetes cluster integrates with the CloudTuner SaaS platform.

```mermaid
graph TB
    subgraph "Customer Environment"
        K8s[Kubernetes Cluster]
        subgraph "CloudTuner Integration"
            KC[Kubecost Cost Analyzer]
            AE[Allocation Exporter]
            Prom[Prometheus Server]
        end
    end

    subgraph "CloudTuner SaaS Platform"
        subgraph "Ingestion Layer"
            DP[Diproxy]
            ThanosR[Thanos Receive]
            S3[Object Storage]
        end

        subgraph "Processing Layer"
            ThanosQ[Thanos Query]
            Metro[Metroculus Service]
            Worker[Kubecost Worker]
        end

        subgraph "Data Storage"
            CH[(ClickHouse)]
            Mongo[(MongoDB)]
        end

        subgraph "Presentation Layer"
            API[REST API]
            NGUI[Frontend Dashboard]
        end
    end

    %% Data Flow
    K8s --> KC
    KC -- "Cost Data" --> AE
    AE -- "Metrics" --> Prom
    Prom -- "Remote Write (HTTPS)" --> DP
    DP --> ThanosR
    ThanosR --> S3
    
    %% Processing Flow
    Worker -- "1. Query Costs" --> Metro
    Metro -- "2. Query Metrics" --> ThanosQ
    ThanosQ -- "3. Read Data" --> S3
    Worker -- "4. Write Daily Expenses" --> CH
    
    %% Frontend Flow
    NGUI -- "5. Get Expenses" --> API
    API -- "6. Read Data" --> CH
    CH -- "7. Return Rows" --> API
    API -- "8. Unified Response" --> NGUI
```

## 2. Detailed Data Flow & Processing Pipeline

This diagram details the specific components and data transformations from metric collection to API response.

```mermaid
sequenceDiagram
    participant KC as Kubecost (Customer)
    participant Prom as Prometheus (Customer)
    participant DP as Diproxy (SaaS)
    participant Thanos as Thanos Store
    participant Metro as Metroculus
    participant Worker as Kubecost Worker
    participant CH as ClickHouse
    participant API as REST API
    participant UI as NGUI (Frontend)

    Note over KC, Prom: Phase 1: Data Collection
    KC->>KC: Calculate Cluster Costs
    KC->>Prom: Expose Metrics (allocation-exporter)
    Prom->>DP: Remote Write (kubecost_*)
    DP->>Thanos: Store Metrics (Tenant Isolated)

    Note over Metro, CH: Phase 2: Backend Processing
    loop Daily Processing
        Worker->>Metro: Fetch Daily Cluster Costs
        Metro->>Thanos: Query Aggregated Metrics
        Thanos-->>Metro: Return Cost Data
        Metro-->>Worker: Return JSON Cost Summary
        Worker->>CH: Insert into 'expenses' table
    end

    Note over API, UI: Phase 3: Frontend Integration
    UI->>API: GET /clean_expenses
    API->>CH: Query Expenses (SQL)
    CH-->>API: Return Rows
    API->>API: Merge K8s Costs with Cloud Costs
    API-->>UI: JSON Response (Unified View)
```

## 3. Data Source Architecture (Handover)

Based on the ASCII diagram from the frontend handover documentation.

```mermaid
graph TD
    subgraph "Customer Cluster"
        KC[Kubecost]
        Prom[Prometheus remote_write]
    end

    subgraph "CloudTuner SaaS"
        DP[diproxy<br>(Receiver)]
        Thanos[Thanos<br>(Long-term Storage)]
        Metro[Metroculus<br>(Query & Aggregate)]
        Worker[kubecost_worker<br>(Transform & Write)]
        CH[(ClickHouse<br>expenses table)]
        API[REST API<br>/v2/clean_expenses]
        UI[NGUI<br>Frontend]
    end

    KC -->|kubecost_* metrics| Prom
    Prom --> DP
    DP --> Thanos
    Thanos --> Metro
    Metro -->|Cost Data| Worker
    Worker -->|Daily expense records| CH
    CH --> API
    API --> UI
```

## 4. Entity Relationship Diagram (Schema)

Illustrating how Kubernetes entities map to CloudTuner's data model.

```mermaid
erDiagram
    ORGANIZATION ||--o{ CLOUD_ACCOUNT : "owns"
    CLOUD_ACCOUNT ||--o{ RESOURCE : "contains"
    
    CLOUD_ACCOUNT {
        string id PK
        string type "kubernetes_cnr"
        string name
        json config
    }

    RESOURCE {
        string id PK
        string resource_type "K8s Cluster"
        string service_name "Kubernetes"
        float cost
        json k8s_costs "Detailed Breakdown"
    }

    K8S_COST_BREAKDOWN {
        float cpu_cost
        float ram_cost
        float pv_cost
        float management_cost
        float load_balancer_cost
        float network_cost
    }

    RESOURCE ||--|| K8S_COST_BREAKDOWN : "has_details"
```
