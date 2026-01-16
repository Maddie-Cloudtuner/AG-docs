# Phase 4 UI Planning: Kubernetes Cost Management Views

**Date**: 2025-10-13
**Status**: Planning Phase

---

## Executive Summary

This document outlines the UI/UX design for CloudTuner's Kubernetes cost management integration. Based on Kubecost API capabilities and CloudTuner's existing expense management flow, we propose **6 new views** plus enhancements to existing dashboards.

**Key Insight**: CloudTuner currently has a basic "K8s Rightsizing" view (CPU/RAM request sizing only). The new integration enables comprehensive cost visibility, optimization recommendations, and multi-cluster comparison.

---

## Kubecost API Capabilities Summary

### API 1: Allocation API (`/model/allocation`)
**Purpose**: Detailed cost allocation by various dimensions

**Aggregation Options**:
- `namespace` - Costs per namespace
- `pod` - Costs per pod
- `controller` - Costs per Deployment/StatefulSet/DaemonSet
- `service` - Costs per Kubernetes service
- `label:app` - Costs per application label
- `container` - Costs per container

**Available Metrics Per Entity**:
```json
{
  "cpuCost": 6.92,
  "ramCost": 3.00,
  "pvCost": 1.72,
  "networkCost": 0.25,
  "loadBalancerCost": 0.62,
  "totalCost": 12.51,

  "cpuEfficiency": 0.45,        // 45% CPU utilization
  "ramEfficiency": 0.32,        // 32% RAM utilization
  "totalEfficiency": 0.38,      // 38% overall efficiency

  "cpuCoreRequestAverage": 2.0,
  "cpuCoreUsageAverage": 0.9,
  "ramByteRequestAverage": 4294967296,  // 4GB
  "ramByteUsageAverage": 1374389535,    // 1.3GB

  "sharedCost": 1.2,            // Shared cluster overhead
  "externalCost": 0.0           // External cloud services
}
```

**Time Windows**: `1h`, `24h`, `7d`, `30d`, `today`, `yesterday`, `week`, `month`, custom

---

### API 2: Assets API (`/model/assets`)
**Purpose**: Infrastructure-level costs not tied to workloads

**Asset Types**:
- `ClusterManagement` - Control plane overhead (~$2.40/day)
- `Disk` - Local node storage costs
- `LoadBalancer` - LoadBalancer service costs
- `Network` - Network egress costs (internet, cross-region, cross-zone)
- `Node` - Individual node costs

**Metrics Per Asset**:
```json
{
  "type": "LoadBalancer",
  "totalCost": 0.6214,
  "minutes": 1440,
  "properties": {
    "category": "Network",
    "service": "Kubernetes"
  }
}
```

---

### API 3: Savings API (`/model/savings`)
**Purpose**: Cost optimization recommendations

**Recommendation Categories**:
```json
{
  "abandonedWorkload": {
    "state": "ready",
    "value": 9.69  // $9.69/week savings
  },
  "requestSizing": {
    "state": "ready",
    "value": 44.31  // $44.31/week from rightsizing
  },
  "clusterSizing": {
    "state": "ready",
    "value": 63.07  // $63.07/week from cluster downsizing
  },
  "pvSizing": {
    "state": "ready",
    "value": 14.02  // $14.02/week from PV optimization
  },
  "localDisks": {
    "state": "ready",
    "value": 52.14  // $52.14/week from removing unused disks
  },
  "unclaimedVolumes": {
    "state": "ready",
    "value": 0.00   // No unclaimed PVs
  }
}
```

**Total Potential Savings**: Sum of all categories (~$183/week in example cluster)

---

## Proposed UI Views

### View 1: **K8s Cost Dashboard** (Landing Page)
**Route**: `/expenses/kubernetes` or `/kubernetes/overview`

**Purpose**: High-level cost overview for all K8s clusters

**Layout**: Dashboard with cards and charts

**Sections**:

#### 1.1 Summary Cards (Top Row)
```
┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
│ Total K8s Costs      │ Active Clusters      │ Efficiency Score     │ Potential Savings    │
│ $432.50/week         │ 3 clusters           │ 38% ⚠️               │ $183.00/week 💰      │
│ ↑ 12% from last week │ 2 dev, 1 prod       │ Below 50% target     │ Click to optimize    │
└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘
```

#### 1.2 Cost Breakdown (Pie Chart)
- CPU costs: 48%
- RAM costs: 28%
- Storage (PV): 10%
- Network: 8%
- Management: 6%

#### 1.3 Cost Trend (Line Chart)
- Last 30 days daily costs
- Overlay: Efficiency trend
- Annotations for significant events (deployments, scaling)

#### 1.4 Top Cost Drivers (Table)
| Cluster | Namespace | Cost (7d) | Trend | Efficiency | Actions |
|---------|-----------|-----------|-------|------------|---------|
| prod-k8s-01 | ml-training | $120.50 | ↑15% | 42% | [Optimize] |
| prod-k8s-01 | api-backend | $89.20 | ↓5% | 65% | [View] |
| dev-k8s | dev | $45.30 | →0% | 28% ⚠️ | [Rightsize] |

#### 1.5 Quick Actions
- 🔍 View all clusters
- 💰 View savings recommendations
- 📊 Download cost report
- ⚙️ Configure cost alerts

**API Integration**:
```python
# Metroculus endpoint (Phase 3)
GET /metroculus/v2/kubecost_cluster_costs?cloud_account_id=<id>&start_date=<ts>&end_date=<ts>

# Response includes full allocation + infrastructure costs
{
  "summary": {
    "total_cost": 432.50,
    "cpu_cost": 207.60,
    "ram_cost": 121.10,
    "pv_cost": 43.25,
    "network_cost": 34.60,
    "management_cost": 25.95
  },
  "efficiency": {
    "cpu_efficiency": 0.45,
    "ram_efficiency": 0.32,
    "total_efficiency": 0.38
  },
  "potential_savings": 183.00
}
```

---

### View 2: **Cluster Detail View**
**Route**: `/kubernetes/cluster/<cloud_account_id>`

**Purpose**: Deep-dive into single cluster costs

**Layout**: Multi-tab interface

#### Tab 2.1: Cost Overview
- **Total Cluster Cost**: $156.20/week
- **Cost by Resource Type** (Stacked bar chart over time):
  - CPU, RAM, Storage, Network, Management
- **Cost by Namespace** (Treemap):
  - Larger boxes = higher costs
  - Color: efficiency (green = high, red = low)

#### Tab 2.2: Workload Costs
**Table View** (sortable, filterable):
| Namespace | Workload | Type | CPU Cost | RAM Cost | Storage | Total | Efficiency | Trend (7d) |
|-----------|----------|------|----------|----------|---------|-------|------------|------------|
| production | api-server | Deployment | $12.50 | $8.30 | $2.10 | $22.90 | 65% ✅ | ↑5% |
| production | db-cluster | StatefulSet | $18.20 | $14.50 | $8.90 | $41.60 | 82% ✅ | →0% |
| ml-training | training-job | Job | $45.00 | $28.00 | $5.00 | $78.00 | 38% ⚠️ | ↓12% |

**Filters**:
- Namespace dropdown
- Workload type (Deployment, StatefulSet, DaemonSet, Job)
- Cost range slider
- Efficiency range
- Date range picker

**Actions Per Row**:
- 📊 View details
- 🔧 Rightsize recommendations
- 📉 Cost history

#### Tab 2.3: Infrastructure Costs
**Asset Breakdown**:
- Cluster Management: $16.80/week (fixed)
- Load Balancers: $17.36/week (4 LBs)
- Network Egress: $21.45/week
  - Internet: $18.50
  - Cross-region: $2.15
  - Cross-zone: $0.80
- Local Disks: $8.40/week
- Node Costs (if available)

#### Tab 2.4: Efficiency Analysis
- **CPU Efficiency Chart**: Request vs Usage over time
- **RAM Efficiency Chart**: Request vs Usage over time
- **Idle Resources**: Cost of unused allocated capacity
- **Peak Usage Patterns**: Identify over-provisioning

**API Integration**:
```python
# Namespace aggregation
GET /model/allocation?window=7d&aggregate=namespace

# Controller/workload details
GET /model/allocation?window=7d&aggregate=controller

# Infrastructure assets
GET /model/assets?window=7d&aggregate=type
```

---

### View 3: **Namespace/Workload Detail View**
**Route**: `/kubernetes/cluster/<id>/namespace/<namespace>` or `/workload/<controller>`

**Purpose**: Granular cost analysis for specific namespace/workload

**Sections**:

#### 3.1 Workload Summary
```
┌────────────────────────────────────────────────────────────┐
│ Namespace: ml-training / Workload: training-job-v2         │
│ Type: Deployment | Replicas: 3 | Created: 2025-09-15      │
├────────────────────────────────────────────────────────────┤
│ Weekly Cost: $78.00                                        │
│ CPU: $45.00 | RAM: $28.00 | Storage: $5.00               │
│ Efficiency: 38% ⚠️ (Below 50% target)                     │
│ Savings Potential: $32.50/week from rightsizing          │
└────────────────────────────────────────────────────────────┘
```

#### 3.2 Pod-Level Breakdown (Table)
| Pod Name | CPU Cost | RAM Cost | PV Cost | Total | CPU Eff | RAM Eff | Status |
|----------|----------|----------|---------|-------|---------|---------|--------|
| training-job-v2-abc123 | $15.20 | $9.50 | $1.70 | $26.40 | 42% | 35% | Running |
| training-job-v2-def456 | $14.80 | $9.20 | $1.65 | $25.65 | 40% | 33% | Running |
| training-job-v2-ghi789 | $15.00 | $9.30 | $1.65 | $25.95 | 38% | 34% | Running |

#### 3.3 Resource Timeline
**Dual-axis chart**:
- Left Y-axis: Cost ($)
- Right Y-axis: Resource usage (CPU cores, GB RAM)
- X-axis: Time (hourly for 24h, daily for 7d/30d)
- Lines: CPU cost, RAM cost, CPU usage, RAM usage

#### 3.4 Rightsizing Recommendation Card
```
┌────────────────────────────────────────────────────────────┐
│ 💡 Rightsizing Recommendation                              │
├────────────────────────────────────────────────────────────┤
│ Current Resources:                                         │
│   CPU Request: 2 cores → Usage: 0.8 cores (40%)          │
│   RAM Request: 4 GB → Usage: 1.4 GB (35%)                │
│                                                            │
│ Recommended Resources:                                     │
│   CPU Request: 1 core (25% buffer)                        │
│   RAM Request: 2 GB (30% buffer)                          │
│                                                            │
│ Expected Savings: $32.50/week (41% reduction)             │
│                                                            │
│ [Apply Recommendation] [Customize] [Dismiss]              │
└────────────────────────────────────────────────────────────┘
```

#### 3.5 Cost Allocation by Container (if multi-container pod)
- Pie chart showing per-container costs
- Table with container-level metrics

**API Integration**:
```python
# Pod-level costs
GET /model/allocation?window=7d&aggregate=pod&filterNamespaces=<namespace>

# Container-level costs
GET /model/allocation?window=7d&aggregate=container&filterNamespaces=<namespace>

# Savings recommendations (specific to namespace)
GET /model/savings?namespace=<namespace>
```

---

### View 4: **Cost Optimization Center**
**Route**: `/kubernetes/optimization`

**Purpose**: Centralized view of all cost-saving opportunities

**Layout**: Prioritized list with impact metrics

#### 4.1 Savings Summary
```
┌──────────────────────────────────────────────────────────────┐
│ Total Potential Savings: $183.00/week                        │
│ Quick Wins (<1 hour effort): $68.50/week                     │
│ Medium Effort (1-4 hours): $92.00/week                      │
│ Long-term (project): $22.50/week                            │
└──────────────────────────────────────────────────────────────┘
```

#### 4.2 Recommendations (Grouped by Category)

**Category 1: Abandoned Workloads** 💀
```
┌────────────────────────────────────────────────────────────┐
│ 🗑️ Remove Unused Workloads                                 │
│ Potential Savings: $9.69/week                              │
├────────────────────────────────────────────────────────────┤
│ • dev/test-deployment-old (no traffic 14d) → $4.20/week   │
│ • staging/legacy-api (0 requests 30d) → $3.25/week        │
│ • prod/temp-debug-pod (created 45d ago) → $2.24/week      │
│                                                            │
│ [Review All] [Delete Selected]                             │
└────────────────────────────────────────────────────────────┘
```

**Category 2: Request Rightsizing** 📏
```
┌────────────────────────────────────────────────────────────┐
│ 🔧 Rightsize Over-Provisioned Workloads                    │
│ Potential Savings: $44.31/week                             │
├────────────────────────────────────────────────────────────┤
│ • ml-training/training-job (38% eff) → $32.50/week        │
│ • api/backend-service (45% eff) → $8.20/week              │
│ • data/etl-processor (52% eff) → $3.61/week               │
│                                                            │
│ [Apply All] [Review Individually]                          │
└────────────────────────────────────────────────────────────┘
```

**Category 3: Cluster Sizing** 🏗️
```
┌────────────────────────────────────────────────────────────┐
│ ⚙️ Downsize Over-Provisioned Clusters                      │
│ Potential Savings: $63.07/week                             │
├────────────────────────────────────────────────────────────┤
│ • dev-k8s: 6 nodes → 4 nodes recommended                  │
│   Current: 6 × t3a.2xlarge ($18.20/node/week)            │
│   Recommended: 4 × t3a.2xlarge                            │
│   Savings: $36.40/week                                     │
│                                                            │
│ • staging-k8s: 4 nodes → 3 nodes recommended              │
│   Savings: $26.67/week                                     │
│                                                            │
│ [View Detailed Analysis] [Schedule Resize]                 │
└────────────────────────────────────────────────────────────┘
```

**Category 4: Storage Optimization** 💾
```
┌────────────────────────────────────────────────────────────┐
│ 💾 Optimize Storage Costs                                  │
│ Potential Savings: $14.02/week                             │
├────────────────────────────────────────────────────────────┤
│ • Unclaimed PVs: 0 volumes → $0.00/week                   │
│ • Oversized PVs: 8 volumes → $14.02/week                  │
│   - dev/logs-pv: 100GB → 30GB used (70GB waste)          │
│   - prod/cache-pv: 50GB → 15GB used (35GB waste)         │
│                                                            │
│ [Resize PVs] [View All Storage]                           │
└────────────────────────────────────────────────────────────┘
```

**Category 5: Local Disks** 💿
```
┌────────────────────────────────────────────────────────────┐
│ 💿 Remove Unused Node Local Storage                        │
│ Potential Savings: $52.14/week                             │
├────────────────────────────────────────────────────────────┤
│ • 18 nodes with local storage (93% idle)                  │
│ • Most workloads use remote PVs                           │
│ • Recommendation: Migrate to EBS/PD + remove local disks  │
│                                                            │
│ [View Migration Plan]                                      │
└────────────────────────────────────────────────────────────┘
```

#### 4.3 Implementation Timeline
**Gantt chart** showing:
- Quick wins (0-1 week)
- Medium-term optimizations (2-4 weeks)
- Strategic initiatives (1-3 months)

**API Integration**:
```python
# All savings recommendations
GET /model/savings

# Detailed recommendations per category
GET /model/savings/<category>?window=7d
```

---

### View 5: **Multi-Cluster Comparison**
**Route**: `/kubernetes/compare`

**Purpose**: Compare costs, efficiency, and optimization opportunities across clusters

**Layout**: Side-by-side comparison

#### 5.1 Cluster Selector
- Multi-select dropdown
- Default: All K8s cloud accounts
- Filter by: Environment (dev/staging/prod), Region, Labels

#### 5.2 Comparison Table
| Metric | prod-k8s-01 | prod-k8s-02 | dev-k8s | staging-k8s |
|--------|-------------|-------------|---------|-------------|
| **Total Cost/Week** | $156.20 | $142.50 | $78.30 | $55.50 |
| **Cost/Pod/Day** | $2.15 | $1.98 | $1.45 | $1.72 |
| **CPU Efficiency** | 65% ✅ | 58% ⚠️ | 28% ❌ | 45% ⚠️ |
| **RAM Efficiency** | 52% ⚠️ | 48% ⚠️ | 22% ❌ | 38% ⚠️ |
| **Nodes** | 8 | 6 | 6 | 4 |
| **Pods** | 124 | 98 | 74 | 45 |
| **Namespaces** | 12 | 10 | 8 | 6 |
| **Savings Potential** | $32.00 | $28.50 | $63.00 | $18.50 |
| **Top Cost Driver** | ml-training | api-backend | dev | staging-db |

#### 5.3 Cost Distribution (Stacked Bar Chart)
- X-axis: Clusters
- Y-axis: Cost ($)
- Stack segments: CPU, RAM, Storage, Network, Management

#### 5.4 Efficiency Comparison (Radar Chart)
- Axes: CPU eff, RAM eff, Storage eff, Cost per pod, Utilization
- One line per cluster
- Ideal target zone highlighted

#### 5.5 Recommendations
- **Best Practices from Top Performer**: Cluster `prod-k8s-01` has 65% CPU efficiency
  - Recommendation: Apply similar resource limits to other clusters
- **Consolidation Opportunities**: `staging-k8s` and `dev-k8s` have low utilization
  - Recommendation: Merge into shared dev/staging cluster → Save $45/week

**API Integration**:
```python
# Aggregate data for all K8s cloud accounts
for account in k8s_accounts:
    data = GET /metroculus/v2/kubecost_cluster_costs?cloud_account_id=<account>&...
    compare_data.append(data)
```

---

### View 6: **Cost Alerts & Budget Management**
**Route**: `/kubernetes/alerts`

**Purpose**: Proactive cost monitoring and anomaly detection

**Sections**:

#### 6.1 Active Alerts
```
┌────────────────────────────────────────────────────────────┐
│ 🔴 CRITICAL: dev-k8s exceeded budget                       │
│ Current: $89.20/week | Budget: $75.00/week (19% over)    │
│ Triggered: 2025-10-12 03:00 UTC                           │
│ [View Details] [Adjust Budget] [Mute 24h]                 │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ 🟡 WARNING: ml-training namespace cost spike               │
│ Current: $120.50/week | Baseline: $85.00/week (+42%)     │
│ Triggered: 2025-10-11 18:00 UTC                           │
│ [Investigate] [Acknowledge]                                │
└────────────────────────────────────────────────────────────┘
```

#### 6.2 Budget Configuration (Per Cluster/Namespace)
**Table**:
| Scope | Current Cost | Budget | Status | Alert Threshold |
|-------|--------------|--------|--------|----------------|
| prod-k8s-01 | $156.20/wk | $175.00/wk | ✅ 89% | 90% |
| dev-k8s | $89.20/wk | $75.00/wk | 🔴 119% | 100% |
| ml-training | $120.50/wk | $100.00/wk | 🟡 121% | 110% |

**Actions**:
- [Set New Budget]
- [Edit Alert Thresholds]
- [Configure Notification Channels]

#### 6.3 Anomaly Detection
**List of detected anomalies**:
- ⚠️ **Sudden cost increase**: `api-backend` (+58% in 24h)
  - Cause: Replica count increased from 3 → 8
  - Action: [View Change Log] [Rollback if unintended]

- ⚠️ **Efficiency drop**: `db-cluster` efficiency fell from 82% → 52%
  - Possible cause: Increased idle time
  - Action: [Investigate] [Rightsize]

#### 6.4 Cost Forecasting
**Chart**: Projected costs for next 30 days based on trends
- Baseline forecast
- Upper bound (if current growth continues)
- Lower bound (if optimizations applied)

**API Integration**:
```python
# CloudTuner existing alert infrastructure
# Extend to support K8s cost alerts

# Budget checks
if k8s_cost > budget * threshold:
    trigger_alert(type='budget_exceeded', ...)

# Anomaly detection
if k8s_cost > baseline * 1.5:
    trigger_alert(type='cost_spike', ...)
```

---

## Enhanced Existing View

### **Update: K8s Rightsizing View** (Existing)
**Current State**: Shows CPU/RAM request recommendations only

**Enhancements**:
1. **Add Cost Impact**: Show $ savings from rightsizing
2. **Add Current Efficiency**: Display current vs ideal efficiency
3. **Add Bulk Actions**: Apply recommendations to multiple workloads
4. **Add Priority Sorting**: Sort by savings potential
5. **Add Before/After Cost Preview**:
   ```
   Current Monthly Cost: $432.00
   After Rightsizing: $285.00
   Savings: $147.00/month (34%)
   ```

---

## Data Flow: API → Backend → Frontend

### Phase 3 Backend (Metroculus)
```python
# /cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py

def get_cluster_costs(self, **kwargs):
    """
    Aggregates:
    1. Infrastructure costs (from Prometheus metrics) ← PHASE 2 COMPLETE
    2. Allocation costs (from Kubecost allocation API) ← PHASE 3 NEW
    3. Savings recommendations (from Kubecost savings API) ← PHASE 3 NEW
    """

    # Phase 2: Infrastructure metrics (DONE)
    mgmt_cost = query_prometheus('kubecost_cluster_management_cost')
    lb_cost = query_prometheus('kubecost_load_balancer_cost')
    net_cost = query_prometheus('kubecost_network_*_cost')

    # Phase 3: Allocation API (NEW)
    allocation_data = query_kubecost_api(
        '/model/allocation',
        window='7d',
        aggregate='namespace'
    )

    cpu_cost = sum(ns['cpuCost'] for ns in allocation_data)
    ram_cost = sum(ns['ramCost'] for ns in allocation_data)
    pv_cost = sum(ns['pvCost'] for ns in allocation_data)

    # Phase 3: Savings API (NEW)
    savings_data = query_kubecost_api('/model/savings')
    potential_savings = sum(rec['value'] for rec in savings_data.values())

    # Phase 3: Efficiency metrics (NEW)
    total_efficiency = calculate_weighted_efficiency(allocation_data)

    return {
        'summary': {
            'total_cost': mgmt_cost + lb_cost + net_cost + cpu_cost + ram_cost + pv_cost,
            'cpu_cost': cpu_cost,
            'ram_cost': ram_cost,
            'pv_cost': pv_cost,
            'management_cost': mgmt_cost,
            'load_balancer_cost': lb_cost,
            'network_cost': net_cost,
        },
        'efficiency': {
            'cpu_efficiency': avg_cpu_eff,
            'ram_efficiency': avg_ram_eff,
            'total_efficiency': total_efficiency
        },
        'potential_savings': potential_savings,
        'breakdown_by_namespace': allocation_data,  # For drill-down
        'savings_recommendations': savings_data      # For optimization view
    }
```

### Phase 4 Frontend (NGUI)
```typescript
// /cloud-tuner/ngui/ui/src/api/kubernetes.ts

export interface K8sClusterCost {
  cloud_account_id: string;
  cloud_account_name: string;
  summary: {
    total_cost: number;
    cpu_cost: number;
    ram_cost: number;
    pv_cost: number;
    management_cost: number;
    load_balancer_cost: number;
    network_cost: number;
  };
  efficiency: {
    cpu_efficiency: number;
    ram_efficiency: number;
    total_efficiency: number;
  };
  potential_savings: number;
  breakdown_by_namespace?: NamespaceCost[];
  savings_recommendations?: SavingsRecommendation[];
}

export interface NamespaceCost {
  namespace: string;
  cpu_cost: number;
  ram_cost: number;
  pv_cost: number;
  total_cost: number;
  cpu_efficiency: number;
  ram_efficiency: number;
  workloads: WorkloadCost[];
}

// API client
export const getK8sCosts = async (params: {
  organization_id: string;
  cloud_account_id?: string;
  start_date: number;
  end_date: number;
}): Promise<K8sClusterCost[]> => {
  const response = await api.get('/v2/kubernetes/costs', { params });
  return response.data;
};

export const getSavingsRecommendations = async (
  cloud_account_id: string
): Promise<SavingsRecommendation[]> => {
  const response = await api.get(`/v2/kubernetes/${cloud_account_id}/savings`);
  return response.data;
};
```

---

## UI Component Hierarchy

```
src/pages/kubernetes/
├── KubernetesDashboard.tsx          # View 1: Landing page
│   ├── CostSummaryCards.tsx
│   ├── CostBreakdownChart.tsx
│   ├── CostTrendChart.tsx
│   └── TopCostDriversTable.tsx
│
├── ClusterDetailView.tsx            # View 2: Single cluster
│   ├── CostOverviewTab.tsx
│   ├── WorkloadCostsTab.tsx
│   ├── InfrastructureCostsTab.tsx
│   └── EfficiencyAnalysisTab.tsx
│
├── NamespaceDetailView.tsx          # View 3: Namespace/Workload
│   ├── WorkloadSummary.tsx
│   ├── PodLevelBreakdown.tsx
│   ├── ResourceTimeline.tsx
│   └── RightsizingRecommendationCard.tsx
│
├── OptimizationCenter.tsx           # View 4: Cost optimization
│   ├── SavingsSummary.tsx
│   ├── AbandonedWorkloadsCard.tsx
│   ├── RightsizingRecommendationsCard.tsx
│   ├── ClusterSizingCard.tsx
│   └── StorageOptimizationCard.tsx
│
├── MultiClusterComparison.tsx       # View 5: Multi-cluster compare
│   ├── ClusterSelector.tsx
│   ├── ComparisonTable.tsx
│   ├── CostDistributionChart.tsx
│   └── EfficiencyRadarChart.tsx
│
├── AlertsAndBudgets.tsx             # View 6: Alerts & budgets
│   ├── ActiveAlertsList.tsx
│   ├── BudgetConfigurationTable.tsx
│   ├── AnomalyDetectionList.tsx
│   └── CostForecastingChart.tsx
│
└── components/                       # Shared components
    ├── CostMetricCard.tsx
    ├── EfficiencyBadge.tsx
    ├── CostTrendIndicator.tsx
    ├── ResourceUsageChart.tsx
    └── SavingsRecommendationCard.tsx
```

---

## Implementation Priorities

### Priority 1: Core Views (MVP)
**Timeline**: 2-3 weeks

1. **View 1: K8s Cost Dashboard** - Essential landing page
2. **View 2: Cluster Detail View** (Cost Overview + Workload Costs tabs only)
3. **Enhanced REST API Integration** - Ensure k8s_costs field works

**Success Criteria**:
- User can see total K8s costs on main dashboard
- User can drill down to cluster-level costs
- User can see namespace/workload breakdown

---

### Priority 2: Optimization Features
**Timeline**: 2-3 weeks after Priority 1

4. **View 4: Optimization Center** - High business value
5. **View 3: Namespace Detail View** - Enables granular analysis
6. **Update existing K8s Rightsizing view** - Leverage existing UI

**Success Criteria**:
- User can identify cost-saving opportunities
- User can see $ impact of recommendations
- User can apply rightsizing recommendations

---

### Priority 3: Advanced Features
**Timeline**: 3-4 weeks after Priority 2

7. **View 5: Multi-Cluster Comparison** - For multi-cluster customers
8. **View 6: Alerts & Budget Management** - Proactive monitoring
9. **Advanced efficiency analysis** - Idle costs, peak patterns

**Success Criteria**:
- User can compare multiple clusters
- User receives alerts for budget overruns
- User can forecast future costs

---

## REST API Extensions Needed

### New Endpoints

#### 1. Get K8s Cost Details
```
GET /v2/kubernetes/costs?organization_id=<id>&cloud_account_id=<id>&start_date=<ts>&end_date=<ts>&detail_level=<level>

Query Parameters:
- organization_id (required)
- cloud_account_id (optional, all if omitted)
- start_date (required, unix timestamp)
- end_date (required, unix timestamp)
- detail_level (optional): summary | namespace | workload | pod
  - summary: Only summary metrics (default)
  - namespace: Include namespace breakdown
  - workload: Include workload/controller breakdown
  - pod: Include pod-level breakdown

Response:
{
  "clusters": [
    {
      "cloud_account_id": "...",
      "cloud_account_name": "prod-k8s-01",
      "summary": { ... },
      "efficiency": { ... },
      "potential_savings": 183.00,
      "namespaces": [  # Only if detail_level >= namespace
        {
          "namespace": "production",
          "costs": { ... },
          "workloads": [ ... ]  # Only if detail_level >= workload
        }
      ]
    }
  ]
}
```

#### 2. Get Savings Recommendations
```
GET /v2/kubernetes/<cloud_account_id>/savings

Response:
{
  "cloud_account_id": "...",
  "total_potential_savings": 183.00,
  "recommendations": {
    "abandoned_workloads": {
      "savings": 9.69,
      "workloads": [
        {
          "namespace": "dev",
          "name": "test-deployment-old",
          "type": "Deployment",
          "reason": "No traffic for 14 days",
          "savings": 4.20
        }
      ]
    },
    "request_sizing": {
      "savings": 44.31,
      "workloads": [ ... ]
    },
    "cluster_sizing": { ... },
    "pv_sizing": { ... },
    "local_disks": { ... }
  }
}
```

#### 3. Get Namespace/Workload Detail
```
GET /v2/kubernetes/<cloud_account_id>/namespace/<namespace>?window=7d

Response:
{
  "namespace": "production",
  "summary": { ... },
  "workloads": [
    {
      "name": "api-server",
      "type": "Deployment",
      "replicas": 3,
      "costs": { ... },
      "efficiency": { ... },
      "pods": [ ... ],
      "rightsizing_recommendation": {
        "current": { cpu: "2", memory: "4Gi" },
        "recommended": { cpu: "1", memory: "2Gi" },
        "savings": 32.50
      }
    }
  ]
}
```

#### 4. Update Budget/Alert Configuration
```
POST /v2/kubernetes/<cloud_account_id>/budget
{
  "budget_period": "weekly",  # or monthly
  "budget_amount": 175.00,
  "alert_threshold": 0.90,  # Alert at 90%
  "notification_channels": ["email", "slack"]
}
```

---

## Key Design Principles

### 1. Progressive Disclosure
- Start with high-level overview (View 1)
- Allow drill-down to detailed views (Views 2, 3)
- Hide complexity until needed

### 2. Action-Oriented
- Every cost insight should have actionable recommendations
- One-click apply for safe optimizations
- Clear cost impact ($) for every action

### 3. Context-Aware Efficiency Targets
- Different targets for prod (60%+) vs dev (40%+)
- Consider workload type (batch jobs vs services)
- Historical baseline for anomaly detection

### 4. Multi-Cluster First
- All views support multiple clusters by default
- Easy comparison and consolidation recommendations
- Organization-level aggregation

### 5. Integration with Existing CloudTuner UX
- Use existing expense management patterns
- Reuse existing chart/table components
- Consistent alert/notification system

---

## Visual Design References

### Cost Cards
Use existing CloudTuner expense card design:
- Large metric (cost)
- Trend indicator (↑↓→)
- Contextual color (green = good, yellow = warning, red = critical)

### Efficiency Badges
```
65% ✅  Good       (>60%)
45% ⚠️  Warning    (40-60%)
28% ❌  Critical   (<40%)
```

### Cost Trend Indicators
```
↑ 15%  Increased
↓ 5%   Decreased
→ 0%   Stable
```

---

## Success Metrics

### User Adoption
- % of users with K8s accounts who visit K8s dashboard
- Average time spent on K8s cost views
- Click-through rate from dashboard to detail views

### Cost Optimization
- $ savings achieved per month (tracked via applied recommendations)
- % of recommendations accepted vs rejected
- Time to implement recommendations

### System Performance
- Page load time <2s for dashboard
- API response time <500ms for summary, <2s for detailed views
- Support for 100+ clusters per organization

---

## Next Steps for Implementation

1. **Review this plan** with product/design team
2. **Prioritize views** based on customer feedback
3. **Create wireframes/mockups** for Priority 1 views
4. **Implement Phase 3 backend** (Kubecost allocation API integration)
5. **Build REST API extensions** (new endpoints above)
6. **Develop Priority 1 frontend views** (Views 1, 2)
7. **User testing** with beta customers
8. **Iterate** based on feedback
9. **Roll out Priority 2 & 3** incrementally

---

**Conclusion**: This UI plan transforms Kubecost's raw cost data into actionable insights within CloudTuner's existing UX. By providing 6 specialized views plus enhanced existing functionality, users gain comprehensive visibility into K8s costs, identify optimization opportunities, and track savings over time.
