# NAYARA FUEL STATION - SYSTEM ARCHITECTURE DIAGRAMS

**Technical Architecture for AI-Powered Petroleum Retail Monitoring**

---

## 📋 Table of Contents

1. [High-Level System Overview](#high-level-system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow Architecture](#data-flow-architecture)
4. [Severity-Based Alert Routing](#severity-based-alert-routing)
5. [Integration Architecture](#integration-architecture)
6. [Network Topology](#network-topology)
7. [Database Schema](#database-schema)
8. [Deployment Architecture](#deployment-architecture)

---

## High-Level System Overview

```mermaid
graph TB
    subgraph "FUEL STATION (On-Premise)"
        A[CCTV Cameras 14-30] --> B[Video Management System]
        B --> C[NVIDIA Jetson Edge Device 1]
        B --> D[NVIDIA Jetson Edge Device 2]
        
        E[ATG System] --> F[Local Data Hub]
        G[POS System] --> F
        H[DU Control Units] --> F
        I[Biometric System] --> F
        
        C --> J[maigic.ai AI Engine]
        D --> J
        F --> J
        
        J --> K[Edge Gateway]
    end
    
    subgraph "CLOUD PLATFORM (cloudtuner.ai)"
        L[Load Balancer] --> M[API Gateway]
        M --> N[Authentication Service]
        M --> O[Analytics Service]
        M --> P[Alert Service]
        M --> Q[Integration Service]
        M --> R[Video Streaming Service]
        
        O --> S[(PostgreSQL)]
        O --> T[(TimescaleDB)]
        P --> U[(Redis Cache)]
        R --> V[S3 Video Archive]
    end
    
    subgraph "USER INTERFACES"
        W[Web Dashboard]
        X[Mobile App - iOS]
        Y[Mobile App - Android]
    end
    
    K -->|HTTPS/WSS| L
    
    M --> W
    M --> X
    M --> Y
    
    P --> Z[SMS Gateway]
    P --> AA[Push Notification Service]
    
    style J fill:#FFE0B2
    style M fill:#C8E6C9
    style P fill:#FFCDD2
    style W fill:#E1BEE7
```

**Key Components**:
- **Edge Layer**: CCTV + AI processing at fuel station
- **Cloud Layer**: Analytics, storage, dashboards
- **Integration Layer**: Connect to existing fuel station systems
- **User Layer**: Web + mobile interfaces

---

## Component Architecture

### Edge Processing Layer (maigic.ai)

```mermaid
graph LR
    subgraph "NVIDIA Jetson Edge Device"
        A[Video Decoder] --> B[Frame Buffer]
        B --> C[AI Inference Engine]
        
        C --> D[Person Detection]
        C --> E[PPE Detection]
        C --> F[Smoking Detection]
        C --> G[Vehicle Detection]
        C --> H[Activity Recognition]
        C --> I[Anomaly Detection]
        
        D --> J[Event Processor]
        E --> J
        F --> J
        G --> J
        H --> J
        I --> J
        
        J --> K[KPI Classifier]
        K --> L[Alert Generator]
        L --> M[Cloud Uplink Queue]
    end
    
    subgraph "AI Models"
        N[YOLOv8 - Object Detection]
        O[Custom PPE Model]
        P[Smoking Classifier]
        Q[DeepSort Tracker]
        R[Action Recognition CNN]
    end
    
    C -.-> N
    C -.-> O
    C -.-> P
    C -.-> Q
    C -.-> R
    
    style C fill:#FFE0B2
    style K fill:#FFCCBC
    style L fill:#FFCDD2
```

**Processing Pipeline**:
1. **Video Decode**: RTSP streams → H.264/H.265 decode (GPU-accelerated)
2. **Frame Extraction**: 30 FPS → downsample to 5-10 FPS for AI
3. **AI Inference**: Run detection models on each frame
4. **Event Generation**: Convert detections to KPI events
5. **Classification**: Assign severity (RED/ORANGE/YELLOW)
6. **Cloud Sync**: Send events to cloudtuner.ai

**Hardware Spec**:
- **NVIDIA Jetson Orin Nano** (8GB): Small stations (≤ 16 cameras)
- **NVIDIA Jetson AGX Orin** (32GB): Large stations (≥ 24 cameras)
- **Storage**: 256GB NVMe SSD (local video buffer)

---

### Cloud Analytics Service

```mermaid
graph TB
    A[API Gateway] --> B[Event Ingestion Service]
    
    B --> C{Event Type?}
    C -->|KPI Violation| D[KPI Processor]
    C -->|ATG Data| E[Fuel Quality Analyzer]
    C -->|POS Data| F[Transaction Analyzer]
    C -->|Video Metadata| G[Video Annotation Service]
    
    D --> H[Compliance Calculator]
    E --> H
    F --> H
    
    H --> I[(PostgreSQL - Structured Data)]
    D --> J[(TimescaleDB - Time Series)]
    
    I --> K[Report Generator]
    J --> K
    
    K --> L[PDF Reports]
    K --> M[Excel Exports]
    K --> N[Regulatory Filings]
    
    D --> O[Alert Decision Engine]
    O --> P{Severity?}
    P -->|RED| Q[Immediate Alert Queue]
    P -->|ORANGE| R[Urgent Alert Queue]
    P -->|YELLOW| S[Daily Summary Queue]
    
    style O fill:#FFCCBC
    style Q fill:#FFCDD2
    style R fill:#FFE0B2
```

---

## Data Flow Architecture

### Real-Time KPI Monitoring Flow

```mermaid
sequenceDiagram
    participant CAM as CCTV Camera
    participant EDGE as Edge Device
    participant AI as AI Models
    participant CLOUD as Cloud Service
    participant ATG as ATG System
    participant DB as Database
    participant DASH as Dashboard
    participant MGR as Station Manager

    CAM->>EDGE: RTSP Stream (30 FPS)
    EDGE->>AI: Extract frames (10 FPS)
    AI->>AI: Run PPE detection
    
    alt PPE Violation Detected
        AI->>EDGE: Event: PPE Missing
        EDGE->>CLOUD: KPI Violation Event (RED)
        CLOUD->>DB: Store incident
        CLOUD->>DASH: WebSocket push
        CLOUD->>MGR: SMS + App Push
        Note over CLOUD,MGR: Response time < 30 seconds
    end
    
    loop Every 5 seconds
        ATG->>CLOUD: Fuel level, density data
        CLOUD->>CLOUD: Check density tolerance
        
        alt Density Mismatch
            CLOUD->>DB: Store fuel quality alert
            CLOUD->>MGR: RED Alert
        end
    end
    
    loop Every 5 minutes
        CLOUD->>DB: Calculate aggregated KPIs
        DB->>DASH: Update KPI cards
    end
    
    MGR->>DASH: Acknowledge alert
    DASH->>CLOUD: Log response
    CLOUD->>DB: Update compliance record
```

---

### Tanker Unloading SOP Verification Flow

```mermaid
flowchart TD
    A[Tanker Enters Station] --> B[Camera 5: LPR Detection]
    B --> C{Authorized Tanker?}
    C -->|No| D[🔴 Alert: Unauthorized Tanker]
    C -->|Yes| E[Tanker Parks at Bay]
    
    E --> F[Camera 6: Monitor Unloading Zone]
    F --> G{Grounding Cable Connected?}
    G -->|No| H[🔴 Alert: Static Discharge Violation]
    G -->|Yes| I{Supervisor Present?}
    I -->|No| J[🔴 Alert: No Supervisor]
    I -->|Yes| K[Monitor Valve Opening]
    
    K --> L{Correct Sequence?}
    L -->|No| M[🔴 Alert: SOP Violation]
    L -->|Yes| N[ATG: Start Density Monitoring]
    
    N --> O{Density in Range?}
    O -->|No| P[🔴 Alert: Fuel Quality Issue]
    O -->|Yes| Q[Unloading In Progress]
    
    Q --> R[Completion Detected]
    R --> S[Auto-Generate Delivery Report]
    S --> T[Update Inventory]
    T --> U[✅ Compliance Log Updated]
    
    style D fill:#FFCDD2
    style H fill:#FFCDD2
    style J fill:#FFCDD2
    style M fill:#FFCDD2
    style P fill:#FFCDD2
    style U fill:#C8E6C9
```

---

## Severity-Based Alert Routing

```mermaid
graph TB
    A[KPI Violation Event] --> B[Alert Decision Engine]
    
    B --> C{Severity Classification}
    
    C -->|RED - VERY CRITICAL| D[Priority 1 Queue]
    C -->|ORANGE - CRITICAL| E[Priority 2 Queue]
    C -->|YELLOW - MODERATE| F[Priority 3 Queue]
    
    D --> G[Multi-Channel Dispatcher]
    G --> H[SMS Gateway]
    G --> I[App Push - FCM/APNS]
    G --> J[WebSocket to Dashboard]
    G --> K[Email Service]
    
    H --> L[Station Manager]
    H --> M[Regional Manager]
    H --> N[Safety Team]
    
    I --> L
    I --> M
    
    J --> O[Dashboard Audio Alarm]
    J --> P[Popup Notification]
    
    D --> Q{Check Time}
    Q -->|After Hours?| R[Also Alert Corporate HQ]
    
    E --> S[App + Dashboard Only]
    S --> L
    
    F --> T[Daily Summary Service]
    T --> U[Batch at 11:59 PM]
    U --> V[Email Report]
    
    L --> W[Acknowledge Alert]
    W --> X[Update Alert Status]
    X --> Y[(Alert History DB)]
    
    style D fill:#FFCDD2
    style E fill:#FFE0B2
    style F fill:#FFF9C4
    style G fill:#E1BEE7
```

### Alert Persistence & Tracking

```mermaid
erDiagram
    ALERT ||--o{ ALERT_LOG : generates
    ALERT ||--|| KPI : references
    ALERT_LOG ||--o| USER : acknowledged_by
    
    ALERT {
        int id PK
        string kpi_code
        string severity
        timestamp detected_at
        string location
        string camera_id
        string snapshot_url
        string status
    }
    
    ALERT_LOG {
        int id PK
        int alert_id FK
        timestamp action_at
        string action_type
        int user_id FK
        string notes
    }
    
    KPI {
        string code PK
        string name
        string category
        string severity
        string detection_method
    }
    
    USER {
        int id PK
        string name
        string role
        string phone
        string email
    }
```

---

## Integration Architecture

### External System Connections

```mermaid
graph TB
    subgraph "InvEye Integration Hub"
        A[API Gateway]
        B[Authentication Module]
        C[Data Transformer]
        D[Sync Scheduler]
    end
    
    subgraph "Fuel Station Systems"
        E[ATG - Veeder Root]
        F[POS - Petro Soft]
        G[DU - Gilbarco/Wayne]
        H[Certificate Management]
        I[Biometric - ZKTeco]
    end
    
    A --> B
    B --> C
    
    C <-->|REST API| E
    C <-->|REST API| F
    C <-->|Modbus TCP| G
    C <-->|SQL Sync| H
    C <-->|REST API| I
    
    C --> J[Data Warehouse]
    D --> J
    
    J --> K[Analytics Engine]
    K --> L[Dashboard API]
    
    style C fill:#E1BEE7
    style J fill:#B2DFDB
```

### API Specifications

#### ATG Integration (Automatic Tank Gauge)

**Endpoint**: `GET /api/atg/tank-status`

**Request**:
```json
{
  "station_id": "NAY-SEC12",
  "tank_ids": ["TANK-MS-1", "TANK-HSD-1"]
}
```

**Response**:
```json
{
  "timestamp": "2024-12-08T14:32:00Z",
  "tanks": [
    {
      "tank_id": "TANK-MS-1",
      "product": "MS (Petrol)",
      "volume_liters": 12485,
      "density_kg_m3": 738.2,
      "temperature_celsius": 28.5,
      "water_level_mm": 5,
      "status": "NORMAL"
    },
    {
      "tank_id": "TANK-HSD-1",
      "product": "HSD (Diesel)",
      "volume_liters": 8920,
      "density_kg_m3": 834.1,
      "temperature_celsius": 29.1,
      "water_level_mm": 3,
      "status": "NORMAL"
    }
  ]
}
```

**Alert Triggers**:
- Density variance > ±0.5 kg/m³ → 🔴 RED Alert
- Water level > 10mm → 🔴 RED Alert
- Temperature out of range → ⚠️ ORANGE Alert

---

#### POS Integration

**Webhook**: `POST /api/pos/transaction` (Pushed by POS on each sale)

**Payload**:
```json
{
  "transaction_id": "TXN-20241208-1432-042",
  "timestamp": "2024-12-08T14:32:15Z",
  "du_id": "DU-03",
  "product": "MS",
  "quantity_liters": 45.5,
  "amount_inr": 5005.50,
  "payment_method": "UPI",
  "customer_vehicle": "MH-12-AB-1234"
}
```

**Validation**:
- Cross-check quantity with DU meter reading
- Verify amount = quantity × price
- Flag if variance > 2%

---

## Network Topology

### Fuel Station Network Architecture

```mermaid
graph TB
    subgraph "Internet"
        A[cloudtuner.ai Cloud]
    end
    
    subgraph "Station Perimeter"
        B[Firewall / Router]
        
        subgraph "CCTV VLAN (192.168.10.0/24)"
            C[CCTV Cameras x 16]
            D[DVR/NVR]
            E[PoE Switch 24-port]
        end
        
        subgraph "Edge AI VLAN (192.168.20.0/24)"
            F[Jetson Device 1]
            G[Jetson Device 2]
            H[Edge Gateway]
        end
        
        subgraph "Fuel Systems VLAN (192.168.30.0/24)"
            I[ATG Controller]
            J[POS Terminal]
            K[DU Controllers x 4]
            L[Biometric System]
        end
        
        subgraph "Office VLAN (192.168.40.0/24)"
            M[Manager PC]
            N[WiFi AP]
        end
    end
    
    C --> E
    E --> D
    E --> F
    E --> G
    
    D --> B
    F --> H
    G --> H
    H --> B
    
    I --> B
    J --> B
    K --> B
    L --> B
    
    M --> N
    N --> B
    
    B <-->|HTTPS/WSS| A
    
    style F fill:#FFE0B2
    style G fill:#FFE0B2
    style H fill:#FFCCBC
    style A fill:#C8E6C9
```

**Network Configuration**:
- **CCTV VLAN**: Isolated for video traffic (highest priority QoS)
- **Edge AI VLAN**: Jetson devices + gateway (medium priority)
- **Fuel Systems VLAN**: ATG, POS, DU (secure, no internet access)
- **Office VLAN**: Manager devices (standard priority)

**Security**:
- Firewall rules: Only Edge Gateway can access internet
- VPN tunnel: Station → Cloud (encrypted)
- Certificate-based authentication
- No direct camera internet exposure

---

## Database Schema

### Core Tables

```mermaid
erDiagram
    STATION ||--o{ ALERT : generates
    STATION ||--o{ KPI_EVENT : logs
    STATION ||--o{ FUEL_DELIVERY : receives
    STATION ||--o{ DAILY_REPORT : produces
    
    ALERT ||--o{ ALERT_LOG : tracks
    ALERT ||--|| KPI : references
    
    KPI_EVENT ||--|| KPI : categorized_by
    
    USER ||--o{ ALERT_LOG : acknowledges
    
    STATION {
        string id PK
        string name
        string location
        string regional_manager
        timestamp created_at
    }
    
    ALERT {
        int id PK
        string station_id FK
        string kpi_code FK
        string severity
        timestamp detected_at
        string camera_id
        string snapshot_url
        string status
        timestamp resolved_at
        int resolved_by FK
    }
    
    KPI {
        string code PK
        string name
        string category
        string severity
        string detection_method
        string response_sla
    }
    
    KPI_EVENT {
        int id PK
        string station_id FK
        string kpi_code FK
        timestamp event_at
        float value
        string status
        json metadata
    }
    
    FUEL_DELIVERY {
        int id PK
        string station_id FK
        timestamp delivery_at
        string product
        float quantity_liters
        float density_kg_m3
        string tanker_id
        string supervisor_id
        bool sop_compliant
    }
    
    ALERT_LOG {
        int id PK
        int alert_id FK
        int user_id FK
        timestamp action_at
        string action_type
        string notes
    }
    
    USER {
        int id PK
        string name
        string role
        string phone
        string email
        string station_id FK
    }
    
    DAILY_REPORT {
        int id PK
        string station_id FK
        date report_date
        int red_alerts
        int orange_alerts
        int yellow_alerts
        float compliance_score
        json summary
    }
```

### Time-Series Data (TimescaleDB)

**Table**: `kpi_timeseries`

| Column | Type | Description |
|:-------|:-----|:------------|
| `time` | TIMESTAMPTZ | Event timestamp (indexed) |
| `station_id` | VARCHAR | Station identifier |
| `kpi_code` | VARCHAR | KPI code |
| `value` | FLOAT | Measured value |
| `status` | VARCHAR | OK / WARNING / CRITICAL |
| `metadata` | JSONB | Additional context |

**Hypertable Config**:
- Partition by: `time` (1 day chunks)
- Retention policy: 90 days (auto-delete older data)
- Compression: After 7 days

**Sample Queries**:

```sql
-- Hourly compliance score for last 24 hours
SELECT 
  time_bucket('1 hour', time) AS hour,
  AVG(CASE WHEN status = 'OK' THEN 100 ELSE 0 END) AS compliance_pct
FROM kpi_timeseries
WHERE station_id = 'NAY-SEC12'
  AND time > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;

-- Top 5 violated KPIs this week
SELECT 
  kpi_code,
  COUNT(*) AS violation_count
FROM kpi_timeseries
WHERE status IN ('WARNING', 'CRITICAL')
  AND time > NOW() - INTERVAL '7 days'
GROUP BY kpi_code
ORDER BY violation_count DESC
LIMIT 5;
```

---

## Deployment Architecture

### Cloud Infrastructure (AWS)

```mermaid
graph TB
    subgraph "AWS Cloud (ap-south-1 - Mumbai)"
        A[Route 53 DNS]
        B[CloudFront CDN]
        C[ALB - Load Balancer]
        
        subgraph "ECS Cluster"
            D[API Service x3]
            E[Analytics Service x2]
            F[Alert Service x2]
            G[WebSocket Service x2]
        end
        
        subgraph "Database Layer"
            H[(RDS PostgreSQL)]
            I[(RDS TimescaleDB)]
            J[(ElastiCache Redis)]
        end
        
        subgraph "Storage"
            K[S3 - Video Archive]
            L[S3 - Reports]
        end
        
        M[SES - Email]
        N[SNS - SMS/Push]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
    C --> G
    
    D --> H
    E --> I
    F --> J
    
    F --> M
    F --> N
    
    G --> K
    
    style C fill:#FFE0B2
    style H fill:#B2DFDB
    style I fill:#B2DFDB
```

**Resource Specifications**:

| Service | Instance Type | Count | Purpose |
|:--------|:--------------|:------|:--------|
| **API Service** | ECS Fargate (2 vCPU, 4GB) | 3 | REST API endpoints |
| **Analytics** | ECS Fargate (4 vCPU, 8GB) | 2 | Heavy computation |
| **Alert Service** | ECS Fargate (1 vCPU, 2GB) | 2 | Notification dispatch |
| **WebSocket** | ECS Fargate (2 vCPU, 4GB) | 2 | Real-time updates |
| **PostgreSQL** | RDS db.r6g.xlarge | 1 (Multi-AZ) | Primary database |
| **TimescaleDB** | RDS db.r6g.large | 1 | Time-series data |
| **Redis** | ElastiCache r6g.large | 1 (Cluster mode) | Alert queue |

**Autoscaling**:
- API Service: Scale out when CPU > 70%
- Analytics: Scale out when queue depth > 1000 events

---

### Multi-Region Deployment (Future)

```mermaid
graph TB
    A[Global Route 53]
    
    subgraph "Primary Region: Mumbai (ap-south-1)"
        B[ALB Mumbai]
        C[ECS Cluster Mumbai]
        D[(RDS Primary)]
    end
    
    subgraph "DR Region: Singapore (ap-southeast-1)"
        E[ALB Singapore]
        F[ECS Cluster Singapore]
        G[(RDS Read Replica)]
    end
    
    A -->|Geolocation Routing| B
    A -->|Failover| E
    
    D -.->|Async Replication| G
    
    style B fill:#C8E6C9
    style E fill:#FFE0B2
```

---

## Security Architecture

### Authentication & Access Control

```mermaid
graph LR
    A[User Login] --> B[Auth0 / Cognito]
    B --> C{Role?}
    
    C -->|Station Manager| D[Station-Level Access]
    C -->|Regional Manager| E[Multi-Station Access]
    C -->|Corporate Admin| F[Global Access]
    
    D --> G[JWT Token]
    E --> G
    F --> G
    
    G --> H[API Gateway]
    H --> I{Validate Token}
    I -->|Valid| J[Allow Request]
    I -->|Invalid| K[401 Unauthorized]
    
    J --> L{Check Permissions}
    L -->|Authorized| M[Execute API Call]
    L -->|Forbidden| N[403 Forbidden]
    
    style B fill:#E1BEE7
    style G fill:#FFE0B2
```

**Role-Based Access Control (RBAC)**:

| Role | Dashboard | Alerts | CCTV | Reports | Config |
|:-----|:----------|:-------|:-----|:--------|:-------|
| **Station Manager** | Own station | Acknowledge | Own station | View only | No |
| **Regional Manager** | All assigned | View all | All stations | Generate | Limited |
| **Corporate Admin** | Global | Manage | Global | Full access | Yes |
| **Auditor** | Read-only | View | No | Full access | No |

---

## Scalability Considerations

### Horizontal Scaling

**Current Capacity** (Single Station):
- **CCTV Streams**: 16 cameras × 4 Mbps = 64 Mbps
- **Edge Processing**: 2 Jetson devices (8 cameras each)
- **Cloud Events**: ~500 events/hour
- **Dashboard Users**: 5-10 concurrent

**Scaling to 100 Stations**:
- **Cloud Events**: 50,000 events/hour
- **Database**: PostgreSQL with read replicas
- **Cache Layer**: Redis cluster (5 nodes)
- **API Service**: Autoscale to 10-20 instances
- **Storage**: S3 with lifecycle policies (30 days archive → Glacier)

---

## Next Steps

### Architecture Review Checklist
- [ ] Validate camera placement strategy with field operations
- [ ] Confirm ATG/POS API availability and documentation
- [ ] Review network security requirements with IT team
- [ ] Estimate cloud infrastructure costs for 10/50/100 stations
- [ ] Finalize edge device procurement (Jetson models)

### Documentation References
- [NAYARA_KPI_SEVERITY_CLASSIFICATION.md](file:///c:/Users/LENOVO/Desktop/my_docs/AG/InvEye/nayasa/NAYARA_KPI_SEVERITY_CLASSIFICATION.md)
- [NAYARA_WORKFLOW.md](file:///c:/Users/LENOVO/Desktop/my_docs/AG/InvEye/nayasa/NAYARA_WORKFLOW.md)

---

**Document Version**: 1.0  
**Last Updated**: December 8, 2024  
**System**: InvEye (Nayara Edition)  
**Edge Processing**: maigic.ai  
**Dashboard**: cloudtuner.ai  
**Infrastructure**: AWS (ap-south-1)
