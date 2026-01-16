# AI Cost Management - CloudTuner.ai

## 🎯 Overview

The **AI Cost Management** feature is a comprehensive solution for tracking, analyzing, and optimizing AI resource costs across multiple cloud providers (AWS, Azure, and GCP). This feature consolidates cost data from various sources, provides detailed insights through intuitive visualizations, and delivers intelligent, data-driven recommendations to reduce AI infrastructure spending.

### Key Features

- 📊 **Multi-Cloud Consolidation**: Unified view of AI costs from AWS, Azure, and GCP
- 💰 **Real-Time Cost Tracking**: Daily updates with cost trends and breakdowns
- 🎯 **Intelligent Recommendations**: AI-powered suggestions for cost optimization
- 📈 **Rich Visualizations**: Interactive charts and graphs for better insights
- 🔍 **Resource-Level Details**: Drill down into individual AI resources
- ⚡ **Performance Metrics**: Correlate costs with throughput and inference metrics
- 💡 **Actionable Insights**: Step-by-step implementation guides for recommendations

### Value Proposition

- **Visibility**: Complete transparency into AI spending across all cloud providers
- **Control**: Identify cost drivers and underutilized resources
- **Optimization**: Save 20-70% on AI costs through intelligent recommendations
- **Efficiency**: Automated data consolidation eliminates manual tracking

---

## 🏗️ Architecture

### System Architecture

```mermaid
graph TB
    subgraph "Cloud Providers"
        AWS[AWS - CUR Reports<br/>SageMaker, Bedrock]
        Azure[Azure - Cost Management<br/>ML Services, Cognitive Services]
        GCP[GCP - BigQuery Exports<br/>Vertex AI, Cloud AI]
    end
    
    subgraph "Data Ingestion Layer"
        ETL[ETL Pipelines<br/>AWS/Azure/GCP Processors]
    end
    
    subgraph "Core Backend Services"
        Consolidation[Cost Consolidation]
        Normalization[Data Normalization]
        Aggregation[Aggregation Engine]
    end
    
    subgraph "Intelligence Layer"
        Analyzer[Cost Analyzer]
        Recommendations[Recommendations Engine<br/>- Rightsizing<br/>- Pricing Models<br/>- Scheduling<br/>- Autoscaling]
        Metrics[Metrics Analyzer<br/>- Throughput<br/>- Inference<br/>- Utilization]
    end
    
    subgraph "Data Storage"
        DB[(PostgreSQL<br/>- ai_resources<br/>- ai_costs<br/>- ai_metrics<br/>- recommendations)]
    end
    
    subgraph "API Layer"
        REST[REST API<br/>FastAPI]
    end
    
    subgraph "Frontend"
        UI[React Dashboard<br/>- Cost Overview<br/>- Visualizations<br/>- Recommendations]
    end
    
    AWS --> ETL
    Azure --> ETL
    GCP --> ETL
    
    ETL --> Consolidation
    Consolidation --> Normalization
    Normalization --> DB
    Normalization --> Aggregation
    Aggregation --> DB
    
    DB --> Analyzer
    DB --> Metrics
    Analyzer --> Recommendations
    Metrics --> Recommendations
    Recommendations --> DB
    
    DB --> REST
    REST --> UI
    
    style AWS fill:#FF9900
    style Azure fill:#0078D4
    style GCP fill:#4285F4
    style Recommendations fill:#22c55e
    style UI fill:#3b82f6
```

### Data Flow

```mermaid
sequenceDiagram
    participant CP as Cloud Providers
    participant ETL as ETL Pipeline
    participant DB as Database
    participant RE as Recommendations Engine
    participant API as REST API
    participant UI as Frontend

    Note over CP,UI: Daily ETL Job (Scheduled)
    
    CP->>ETL: Export cost data
    ETL->>ETL: Fetch & normalize data
    ETL->>DB: Store normalized costs
    
    DB->>RE: Fetch resources & metrics
    RE->>RE: Analyze patterns
    RE->>RE: Generate recommendations
    RE->>DB: Store recommendations
    
    Note over CP,UI: User Interaction
    
    UI->>API: Request cost summary
    API->>DB: Query aggregated costs
    DB->>API: Return cost data
    API->>UI: Send response
    
    UI->>API: Request recommendations
    API->>DB: Query recommendations
    DB->>API: Return recommendations
    API->>UI: Display recommendations
    
    UI->>API: Accept recommendation
    API->>DB: Update status
    DB->>API: Confirmation
    API->>UI: Success message
```

---

## 💾 Data Sources

### AWS - Cost and Usage Reports (CUR)

**Services Tracked:**
- Amazon SageMaker (endpoints, training jobs, notebooks)
- Amazon Bedrock (foundation models)
- Amazon Rekognition
- Amazon Comprehend
- Amazon Transcribe / Polly / Lex

**Data Location:** S3 bucket with CUR exports  
**Update Frequency:** Daily  
**Coverage:** Line-item billing with resource tags

### Azure - Cost Management API

**Services Tracked:**
- Microsoft.MachineLearningServices (workspaces, endpoints)
- Microsoft.CognitiveServices (OpenAI, Vision, Speech)
- Microsoft.BotService

**Data Location:** Cost Management API  
**Update Frequency:** Daily  
**Coverage:** Resource-level costs with tags

### GCP - BigQuery Billing Exports

**Services Tracked:**
- Vertex AI (training, endpoints, pipelines)
- Cloud AI Platform
- Cloud Natural Language / Vision / Speech APIs

**Data Location:** BigQuery dataset  
**Update Frequency:** Daily  
**Coverage:** Detailed SKU-level billing with labels

---

## 🤖 Recommendations Engine

The recommendations engine analyzes cost and performance data to generate intelligent optimization suggestions.

### Recommendation Types

#### 1. **Rightsizing**
- **What**: Identifies over-provisioned resources
- **How**: Analyzes GPU/CPU/Memory utilization metrics
- **Example**: "Your SageMaker endpoint has 28% GPU utilization. Downsize from ml.g4dn.xlarge to ml.g4dn.large to save $1,280/month (40%)"

#### 2. **Pricing Model Optimization**
- **What**: Suggests better pricing models
- **How**: Analyzes usage consistency and cost variance
- **Example**: "Consistent usage detected. Switch to AWS Savings Plan to save $555/month (30%)"

#### 3. **Scheduling**
- **What**: Recommends auto-shutdown during off-hours
- **How**: Analyzes hourly usage patterns and throughput
- **Example**: "Low usage detected during 10 hours/day. Implement scheduling to save $1,000/month (42%)"

#### 4. **Autoscaling**
- **What**: Enables dynamic scaling based on demand
- **How**: Analyzes throughput variability
- **Example**: "High throughput variability (3x peak vs avg). Enable autoscaling to save $600/month (25%)"

#### 5. **Decommissioning**
- **What**: Identifies idle or unused resources
- **How**: Checks for near-zero activity over extended periods
- **Example**: "Virtually no usage in 7 days. Decommission to save $850/month (100%)"

### Recommendation Confidence & Priority

Each recommendation includes:
- **Confidence Score** (0.00 - 1.00): Based on data quality and analysis depth
- **Priority** (Critical/High/Medium/Low): Based on potential savings
- **Implementation Effort** (Low/Medium/High): Estimated complexity

### Supporting Data

Every recommendation provides:
- Current monthly cost
- Estimated monthly savings
- Savings percentage
- Detailed metrics (utilization, throughput, patterns)
- Step-by-step implementation guide

---

## 🎨 Frontend Dashboard

### Dashboard Sections

1. **Cost Summary Cards**
   - Total AI cost this month
   - Breakdown by cloud provider (AWS/Azure/GCP)
   - Potential savings from recommendations

2. **Cost Trend Chart**
   - Historical cost trends (daily/weekly/monthly)
   - Multi-cloud comparison
   - Category breakdown (compute, inference, storage, training)

3. **Cost Breakdown Visualizations**
   - Pie chart: Cost by provider
   - Bar chart: Cost by service
   - Stacked area: Cost by category over time

4. **Resources Table**
   - Searchable and filterable
   - Shows resource name, provider, service, region
   - Displays daily and monthly costs
   - Inline performance metrics

5. **Recommendations List**
   - Expandable cards with details
   - Priority badges (critical/high/medium/low)
   - One-click accept/reject actions
   - Implementation guides

### Filters

- **Date Range**: Custom date picker
- **Cloud Provider**: AWS, Azure, GCP (multi-select)
- **Service Type**: SageMaker, Bedrock, Vertex AI, etc.
- **Account/Subscription**: Filter by account ID
- **Cost Category**: Compute, inference, training, storage

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Cloud provider credentials (AWS, Azure, GCP)

### Backend Setup

1. **Install Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

2. **Configure Environment Variables**

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cloudtuner

# AWS
AWS_CUR_BUCKET=my-cur-bucket
AWS_CUR_PREFIX=cur-reports/
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Azure
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# GCP
GCP_PROJECT_ID=your-project-id
GCP_DATASET_ID=billing_export
GCP_TABLE_ID=gcp_billing_export
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

3. **Initialize Database**

```bash
# Run migrations
alembic upgrade head

# Or create tables manually
python scripts/init_db.py
```

4. **Run Backend Server**

```bash
uvicorn main:app --reload --port 8000
```

5. **Setup ETL Cron Job**

```bash
# Add to crontab for daily execution at 2 AM
0 2 * * * /usr/bin/python /path/to/backend/jobs/daily_etl.py
```

### Frontend Setup

1. **Install Dependencies**

```bash
cd frontend
npm install
```

2. **Configure Environment**

Create `.env` file:

```env
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_USE_MOCK=false
```

3. **Run Development Server**

```bash
npm start
```

4. **Build for Production**

```bash
npm run build
```

### Testing with Mock Data

For development and testing without backend:

```env
REACT_APP_USE_MOCK=true
```

This will use the mock data defined in `src/mockData/aiCostData.ts`.

---

## 📊 Usage Guide

### Viewing Costs

1. **Navigate to AI Cost Management** dashboard
2. **Select date range** (default: last 30 days)
3. **Apply filters** (optional):
   - Cloud provider
   - Service type
   - Account ID
4. **Review summary cards** for high-level insights
5. **Analyze trends** in the line chart
6. **Drill down** into specific resources in the table

### Acting on Recommendations

1. **Review recommendations** in the bottom section
2. **Click on a recommendation** to expand details
3. **Review supporting data** and implementation steps
4. **Accept** to mark for implementation, or **Reject** to dismiss
5. **Follow implementation guide** step-by-step
6. **Monitor savings** in subsequent billing cycles

### Exporting Data

```typescript
// Export cost summary as CSV
const exportCostData = async () => {
  const response = await fetch(`${API_BASE_URL}/ai-costs/export?format=csv`);
  const blob = await response.blob();
  // Download file
};
```

---

## 🔗 API Reference

### Cost Endpoints

#### `GET /api/v1/ai-costs/summary`

Get aggregated cost summary.

**Query Parameters:**
- `start_date` (required): YYYY-MM-DD
- `end_date` (required): YYYY-MM-DD
- `cloud_provider` (optional): AWS, Azure, GCP
- `service_type` (optional): Service filter
- `account_id` (optional): Account filter

**Response:**
```json
{
  "total_cost": 12450.00,
  "currency": "USD",
  "period_start": "2024-11-01",
  "period_end": "2024-11-28",
  "breakdown_by_provider": {
    "AWS": 6200.00,
    "Azure": 3100.00,
    "GCP": 3150.00
  },
  "breakdown_by_service": { ... },
  "breakdown_by_category": { ... }
}
```

#### `GET /api/v1/ai-costs/trends`

Get cost trends over time.

**Query Parameters:**
- `start_date` (required)
- `end_date` (required)
- `granularity` (required): daily, weekly, monthly
- `cloud_provider` (optional)

**Response:**
```json
[
  {
    "date": "2024-11-01",
    "cost": 420.50,
    "provider": "AWS"
  },
  ...
]
```

### Recommendation Endpoints

#### `GET /api/v1/recommendations`

Get cost optimization recommendations.

**Query Parameters:**
- `cloud_provider` (optional)
- `recommendation_type` (optional)
- `priority` (optional): critical, high, medium, low
- `min_savings` (optional): Minimum monthly savings
- `status` (default: pending): pending, accepted, rejected

**Response:**
```json
[
  {
    "id": "rec-1",
    "resource_id": "...",
    "recommendation_type": "rightsizing",
    "title": "Downsize Inference Endpoint",
    "description": "...",
    "current_monthly_cost": 3200.00,
    "estimated_monthly_savings": 1280.00,
    "savings_percent": 40.0,
    "confidence_score": 0.85,
    "priority": "high",
    "implementation_effort": "medium",
    "recommended_action": { ... },
    "supporting_data": { ... },
    "created_at": "2024-11-28T06:00:00Z"
  },
  ...
]
```

#### `POST /api/v1/recommendations/{id}/accept`

Accept a recommendation.

**Response:**
```json
{
  "status": "success",
  "message": "Recommendation accepted"
}
```

#### `POST /api/v1/recommendations/{id}/reject`

Reject a recommendation.

**Request Body:**
```json
{
  "reason": "Already using a different optimization strategy"
}
```

---

## 📸 Screenshots & Demo

### Cost Overview Dashboard

```
╔═══════════════════════════════════════════════════════════════╗
║  AI Cost Management                    [🔍 Filters] [📤 Export] ║
╠═══════════════════════════════════════════════════════════════╣
║                                                                ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        ║
║  │ 💰 Total     │  │ ☁️  Multi-   │  │ 🎯 Potential │        ║
║  │    Cost      │  │    Cloud      │  │    Savings   │        ║
║  │              │  │               │  │              │        ║
║  │  $12,450/mo  │  │ AWS: $6,200   │  │  $3,430/mo   │        ║
║  │              │  │ Azure: $3,100 │  │              │        ║
║  │              │  │ GCP: $3,150   │  │  From 4 Recs │        ║
║  └──────────────┘  └──────────────┘  └──────────────┘        ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 📈 Cost Trends                                          │  ║
║  │                                                          │  ║
║  │    $700 ┤                      ╭─╮                      │  ║
║  │         │          ╭──╮      ╭─╯ ╰╮    ╭───╮            │  ║
║  │    $500 ┤    ╭──╮ │  ╰╮  ╭──╯     ╰─╮ ╭╯   ╰─╮          │  ║
║  │         │ ╭──╯  ╰─╯   ╰──╯          ╰─╯      ╰──        │  ║
║  │    $300 ┴─────────────────────────────────────────────  │  ║
║  │         Nov 1    Nov 7    Nov 14    Nov 21    Nov 28    │  ║
║  │                                                          │  ║
║  │  Legend: ─── AWS   ─── Azure   ─── GCP   ─ ─ Total     │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  🎯 Cost Optimization Recommendations (4 recommendations)     ║
║  Potential savings: $3,430/month                              ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 📏 Downsize Inference Endpoint              🔴 HIGH     │  ║
║  │ ml-inference-prod • AWS                                 │  ║
║  │                                                          │  ║
║  │ GPU utilization is only 28.3%. Consider using a         │  ║
║  │ smaller instance type to reduce costs.                  │  ║
║  │                                                          │  ║
║  │ 💰 $1,280/mo savings (40%)     🎯 85% confidence        │  ║
║  │ 📊 Medium effort                                        │  ║
║  │                                                          │  ║
║  │ [✓ Accept & Implement]  [✗ Dismiss]                     │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 💳 Switch to Savings Plan                   🔴 HIGH     │  ║
║  │ claude-api-integration • AWS                            │  ║
║  │                                                          │  ║
║  │ Consistent usage detected. A 1-year Savings Plan        │  ║
║  │ could reduce costs by ~35%.                             │  ║
║  │                                                          │  ║
║  │ 💰 $555/mo savings (30%)       🎯 90% confidence        │  ║
║  │ 📊 Low effort                                           │  ║
║  └────────────────────────────────────────────────────────┘  ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 🎯 Showcasing the Feature

### For Executive Presentation

**Key Talking Points:**
1. **Unified Visibility**: "Single pane of glass for all AI costs across AWS, Azure, and GCP"
2. **Immediate Value**: "Identified $3,430/month in potential savings on day one"
3. **Data-Driven**: "Recommendations backed by 30 days of utilization metrics with 85%+ confidence"
4. **ROI**: "20-70% cost reduction with minimal implementation effort"

### For Client Demo

**Demo Flow:**
1. Show the dashboard with real/mock data
2. Walk through cost summary cards
3. Highlight cost trends and anomalies
4. Dive into a specific high-priority recommendation
5. Show implementation steps
6. Demonstrate accept/reject workflow
7. Project annual savings

### For Development Team

**Technical Highlights:**
- Modular ETL architecture supporting any cloud provider
- Pluggable recommendations engine
- Type-safe React components with TypeScript
- Environment-based mock/real API switching
- Comprehensive test coverage (unit + integration)

---

## 🔮 Future Enhancements

### Phase 2
- **Budget Alerts**: Set budgets and receive notifications
- **Forecasting**: ML-based cost predictions
- **Custom Rules**: User-defined optimization rules
- **Anomaly Detection**: Automated unusual spend detection

### Phase 3
- **Multi-Tenancy**: Support for multiple organizations
- **Role-Based Access**: Granular permissions
- **Audit Logs**: Track all recommendation actions
- **Integration**: Slack/Teams notifications

### Phase 4
- **Auto-Remediation**: Automatically implement low-risk recommendations
- **What-If Analysis**: Simulate cost changes
- **Carbon Footprint**: CO2 emissions tracking for AI workloads
- **Kubernetes**: Support for self-managed AI on K8s

---

## 📚 Related Documentation

- [Backend Implementation Guide](./BACKEND_GUIDE.md) - Detailed backend architecture and code
- [Frontend Implementation Guide](./FRONTEND_GUIDE.md) - React components and integration
- CloudTuner API Documentation - Full API reference
- Cloud Provider Cost APIs:
  - [AWS Cost and Usage Reports](https://docs.aws.amazon.com/cur/)
  - [Azure Cost Management API](https://docs.microsoft.com/en-us/azure/cost-management-billing/)
  - [GCP BigQuery Billing Export](https://cloud.google.com/billing/docs/how-to/export-data-bigquery)

---

## 🤝 Support

For questions or issues:
- **Documentation**: See `BACKEND_GUIDE.md` and `FRONTEND_GUIDE.md`
- **API Issues**: Check logs in `/var/log/cloudtuner/`
- **Frontend Issues**: Check browser console
- **Feature Requests**: Submit via CloudTuner portal

---

## 📄 License

Copyright © 2024 CloudTuner.ai. All rights reserved.
