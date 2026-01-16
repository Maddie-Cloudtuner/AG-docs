# Kubecost-CloudTuner Integration: Complete Architecture and Implementation Guide

## Executive Summary

This document captures the complete architecture, implementation phases, and critical decisions for integrating Kubecost cost allocation with CloudTuner's multi-tenant SaaS platform. The integration enables CloudTuner customers to gain granular Kubernetes cost visibility (cluster, namespace, pod, node level) while maintaining CloudTuner's SaaS-first architecture where customer Helm charts run in their own clusters.

**Key Architectural Principle**: Data flows via Prometheus remote_write from customer clusters → CloudTuner's centralized Thanos → Metroculus API → CloudTuner backend services. Direct API-to-API communication between customer clusters and CloudTuner SaaS is avoided to maintain security boundaries and multi-cluster compatibility.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Integration Phases](#integration-phases)
3. [Data Flow](#data-flow)
4. [Component Responsibilities](#component-responsibilities)
5. [Implementation Details](#implementation-details)
6. [Critical Architectural Decisions](#critical-architectural-decisions)
7. [Deployment Guide](#deployment-guide)
8. [Verification and Testing](#verification-and-testing)
9. [Troubleshooting](#troubleshooting)
10. [Production Considerations](#production-considerations)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Customer Kubernetes Cluster (Multi-tenant)                   │
│                                                               │
│  ┌──────────────┐         ┌────────────────────┐            │
│  │ Kubecost     │         │ allocation-exporter│            │
│  │ cost-analyzer│─────────▶ (gauge metrics)    │            │
│  │              │  API    │                    │            │
│  └──────────────┘         └─────────┬──────────┘            │
│                                      │                        │
│                           ┌──────────▼──────────┐            │
│                           │ Prometheus          │            │
│                           │ (scrapes exporters) │            │
│                           └──────────┬──────────┘            │
│                                      │ remote_write          │
└──────────────────────────────────────┼────────────────────────┘
                                       │
                                       │ HTTPS + Auth Headers
                                       │ (Cloud-Account-Id)
                                       ▼
┌─────────────────────────────────────────────────────────────┐
│ CloudTuner SaaS Platform (Centralized)                       │
│                                                               │
│  ┌──────────┐    ┌─────────┐    ┌──────────────┐           │
│  │ diproxy  │───▶│ Thanos  │───▶│ Metroculus   │           │
│  │ (ingress)│    │ (TSDB)  │    │ (API layer)  │           │
│  └──────────┘    └─────────┘    └──────┬───────┘           │
│                                         │                    │
│                                         ▼                    │
│                           ┌─────────────────────┐           │
│                           │ kubecost_worker     │           │
│                           │ (data processor)    │           │
│                           └──────┬──────┬───────┘           │
│                                  │      │                    │
│                    ┌─────────────┘      └────────────┐      │
│                    ▼                                  ▼      │
│           ┌────────────────┐                 ┌──────────┐   │
│           │ MongoDB        │                 │ ClickHouse│  │
│           │ (resources)    │                 │ (expenses)│  │
│           └────────┬───────┘                 └─────┬────┘   │
│                    │                               │         │
│                    └───────────┬───────────────────┘         │
│                                ▼                             │
│                    ┌───────────────────────┐                │
│                    │ REST API              │                │
│                    │ (clean_expenses, etc) │                │
│                    └───────────┬───────────┘                │
│                                │                             │
│                                ▼                             │
│                    ┌───────────────────────┐                │
│                    │ NGUI (Frontend)       │                │
│                    │ (cost dashboards)     │                │
│                    └───────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Location | Purpose | Data Format |
|-----------|----------|---------|-------------|
| **Kubecost** | Customer cluster | Native K8s cost calculation engine | Internal state + API |
| **allocation-exporter** | Customer cluster | Exports Kubecost data as Prometheus metrics | Gauge metrics (hourly rates) |
| **Prometheus** | Customer cluster | Scrapes exporters, forwards via remote_write | Time-series data |
| **diproxy** | CloudTuner SaaS | Ingress endpoint for remote_write | HTTP proxy |
| **Thanos** | CloudTuner SaaS | Long-term TSDB storage | PromQL-queryable |
| **Metroculus** | CloudTuner SaaS | Metrics API layer wrapping Thanos | REST API (JSON) |
| **kubecost_worker** | CloudTuner SaaS | Data processor and transformer | Python worker |
| **MongoDB** | CloudTuner SaaS | Resource metadata storage | Document store |
| **ClickHouse** | CloudTuner SaaS | Expense data storage | Columnar DB |
| **REST API** | CloudTuner SaaS | Business logic + aggregation | REST endpoints |
| **NGUI** | CloudTuner SaaS | User interface | React frontend |

---

## Integration Phases

### Phase 1: Cluster-Level Costs (COMPLETED)

**Goal**: Aggregate total cluster cost via Prometheus remote_write.

**Implementation**:
- Kubecost metrics forwarded via Prometheus remote_write
- Metroculus API endpoint: `GET /metroculus/v2/kubecost_cluster_costs`
- REST API integration: Added `k8s_costs` field to `clean_expenses` response
- Data storage: ClickHouse only (no granular breakdown)

**Result**: Total K8s cluster cost displayed alongside cloud provider costs.

**Files Modified**:
- `rest_api/rest_api_server/controllers/expense.py` (lines 831-892, 1527-1531)
- `metroculus/metroculus_api/controllers/kubecost_metrics.py`

### Phase 2: Allocation-Level Costs (IN PROGRESS)

**Goal**: Namespace, pod, and node-level cost attribution following CloudTuner's resource + expense pattern.

**Implementation**:
- **allocation-exporter**: New deployment that queries Kubecost allocation API every 60s, exposes gauge metrics
- Metrics: `cloudtuner_kubecost_namespace_total_cost`, `cloudtuner_kubecost_pod_total_cost`, etc.
- **kubecost_worker**: Polls Metroculus for allocation metrics, creates:
  - MongoDB `cloud_resource` records (for UI filters)
  - ClickHouse `expenses` records (with k8s_namespace, k8s_node, k8s_service columns)
- **Metroculus API**: Queries instant values (gauges) from Thanos, synthesizes time ranges

**Critical Architectural Fix**:
Initially attempted to write only to ClickHouse, breaking CloudTuner's standard pattern. **Corrected to follow AWS/Azure/GCP pattern**: MongoDB for resource metadata + ClickHouse for expenses.

**Files Modified**:
- `kubecost_worker/kubecost_worker/metroculus_allocation_processor.py`
- `kubecost_worker/kubecost_worker/main.py`
- `metroculus/metroculus_api/controllers/kubecost_metrics.py` (allocation metric queries)
- REST API `available_filters.py` (already had k8s filter support)

### Phase 3: Real-Time Metrics Dashboard (PLANNED)

**Goal**: Live Prometheus-style dashboards for K8s resource utilization.

**Scope**:
- Grafana integration or NGUI live metrics view
- Direct Thanos queries for container_cpu_usage, node_memory, etc.
- No batch processing, pure time-series visualization

### Phase 4: Optimization Recommendations (PLANNED)

**Goal**: ML-driven rightsizing and cost optimization suggestions.

**Scope**:
- Analyze usage patterns from ClickHouse expense history
- Generate recommendations (resize pods, bin packing, spot instances)
- Integration with CloudTuner's existing optimization engine

---

## Data Flow

### 1. Metric Collection (Customer Cluster)

```
┌──────────────────────────────────────────────────────────────┐
│ Step 1: Kubecost computes allocation costs                    │
│ - Queries K8s API (pods, nodes, PVs)                         │
│ - Applies pricing data from cloud provider APIs              │
│ - Maintains allocation state in cost-model service           │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 2: allocation-exporter polls Kubecost API               │
│ - Every 60s: GET /allocation?window=1h&aggregate=namespace   │
│ - Converts JSON response to Prometheus gauge metrics         │
│ - Exposes on :19090/metrics                                  │
│                                                               │
│ Example metrics:                                              │
│   cloudtuner_kubecost_namespace_total_cost{                  │
│     tenant_id="bc55eb8c-...",                                │
│     namespace="default",                                      │
│     cluster="minikube"                                        │
│   } 0.2573                                                    │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 3: Prometheus scrapes allocation-exporter               │
│ - scrape_interval: 60s                                        │
│ - Stores locally in TSDB                                      │
│ - Applies relabeling rules (add Cloud-Account-Id label)      │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 4: Prometheus remote_write forwards to CloudTuner       │
│ - Endpoint: https://dashboard.cloudtuner.ai/storage/...      │
│ - Headers: Cloud-Account-Id (for multi-tenancy)              │
│ - Basic auth: kubecost / kubecost@123                         │
│ - Metric filter: Only kubecost_*, cloudtuner_kubecost_*      │
└───────────────────────────────────────────────────────────────┘
```

### 2. Data Ingestion (CloudTuner SaaS)

```
┌──────────────────────────────────────────────────────────────┐
│ Step 5: diproxy receives remote_write POST                   │
│ - Parses Cloud-Account-Id header → tenant isolation          │
│ - Forwards to Thanos Receiver                                 │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 6: Thanos stores time-series data                        │
│ - TSDB blocks written to object storage                      │
│ - Queryable via PromQL at /api/v1/query                      │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 7: kubecost_worker polls Metroculus API (5min cadence)  │
│ - GET /metroculus/v2/kubecost_metrics?metrics=...            │
│ - Metroculus queries Thanos instant API (gauges!)            │
│ - Returns JSON with metric values                            │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────���───────────────────────────────────┐
│ Step 8: kubecost_worker processes data                       │
│ A. Parse allocation metrics by namespace/pod                 │
│ B. Create cloud_resource records in MongoDB                  │
│    - resource_type: "K8s Namespace"                          │
│    - k8s_namespace: "default"                                │
│    - cloud_resource_id: "k8s-ns-{hash}"                      │
│ C. Create expense records in ClickHouse                      │
│    - cloud_account_id, date, cost, k8s_namespace             │
│    - CollapsingMergeTree pattern (sign: 1/-1)                │
└───────────────────────────────────────────────────────────────┘
```

### 3. Data Retrieval (User Queries)

```
┌──────────────────────────────────────────────────────────────┐
│ Step 9: User opens NGUI cost dashboard                       │
│ - Frontend calls GET /restapi/v2/available_filters           │
│ - REST API queries MongoDB resources collection              │
│ - Returns: {k8s_namespace: ["default", "kube-system", ...]}  │
│ - UI populates filter dropdowns                              │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 10: User applies filters and requests expense data      │
│ - Frontend calls GET /restapi/v2/clean_expenses?             │
│   organization_id=...&start_date=...&k8s_namespace=default   │
│ - REST API queries ClickHouse expenses table                 │
│ - Aggregates by date, namespace, service, etc.               │
│ - Returns: {total_cost: 250.50, k8s_costs: {...}, ...}       │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 11: NGUI renders cost breakdown charts                  │
│ - Namespace cost trends over time                            │
│ - Pod-level cost attribution                                 │
│ - Cost comparison across clusters                            │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Responsibilities

### allocation-exporter (Customer Cluster)

**Image**: `invincibledocker24/kubecost-allocation-exporter:v1.3.0`
**Deployment**: `k8s-kubecost/charts/kubecost-integration/templates/allocation-exporter.yaml`

**Responsibilities**:
1. Query Kubecost allocation API every 60s
2. Parse allocation JSON responses (namespace, pod, node aggregations)
3. Convert to Prometheus gauge metrics with labels (tenant_id, namespace, cluster)
4. Expose metrics endpoint at :19090/metrics for Prometheus scraping

**Configuration**:
```yaml
env:
  - name: KUBECOST_URL
    value: "http://kubecost-cost-analyzer.kubecost-dev:9090"
  - name: TENANT_ID
    value: "bc55eb8c-5db2-4c32-b976-2df0edb0619a"  # K8s cloud account ID
  - name: CLUSTER_NAME
    value: "minikube"
  - name: SCRAPE_INTERVAL
    value: "60"
```

**Exported Metrics**:
- `cloudtuner_kubecost_namespace_total_cost` (gauge, hourly rate)
- `cloudtuner_kubecost_namespace_cpu_cost`
- `cloudtuner_kubecost_namespace_ram_cost`
- `cloudtuner_kubecost_namespace_pv_cost`
- `cloudtuner_kubecost_pod_total_cost`
- `cloudtuner_kubecost_pod_cpu_cost`
- `cloudtuner_kubecost_pod_ram_cost`

**Why Gauges?**: Allocation costs are point-in-time snapshots of hourly rates, not cumulative counters. Kubecost recalculates the "last 1h" cost on each API call.

### Metroculus (CloudTuner SaaS)

**Service**: `metroculus`
**File**: `metroculus/metroculus_api/controllers/kubecost_metrics.py`

**Responsibilities**:
1. Provide REST API wrapper around Thanos PromQL queries
2. Handle instant queries for gauge metrics vs range queries for counters
3. Synthesize time ranges for allocation metrics (which only exist as instant values)
4. Support multi-tenancy via tenant_id label filtering

**Key Endpoints**:

#### `GET /metroculus/v2/kubecost_cluster_costs`
**Purpose**: Phase 1 cluster-level cost aggregation
**Query**: Sums all Kubecost metrics for total cluster cost
**Returns**:
```json
{
  "cloud_account_id": "bc55eb8c-...",
  "start_date": 1730419200,
  "end_date": 1730505600,
  "total_cost": 105.50,
  "breakdown": {
    "management_cost": 3.20,
    "cpu_cost": 50.00,
    "ram_cost": 30.00,
    "pv_cost": 10.00,
    "network_cost": 5.00,
    "load_balancer_cost": 6.80
  }
}
```

#### `GET /metroculus/v2/kubecost_metrics`
**Purpose**: Phase 2 allocation-level metrics
**Query Parameters**:
- `cloud_account_id` (required)
- `metrics` (comma-separated list)
- `start_date`, `end_date` (Unix timestamps)

**Returns**:
```json
{
  "cloud_account_id": "bc55eb8c-...",
  "start_date": 1730419200,
  "end_date": 1730505600,
  "metrics": {
    "cloudtuner_kubecost_namespace_total_cost": {
      "status": "success",
      "data": {
        "resultType": "vector",
        "result": [
          {
            "metric": {
              "tenant_id": "bc55eb8c-...",
              "namespace": "default",
              "cluster": "minikube"
            },
            "value": [1730419200, "0.2573"]
          },
          {
            "metric": {
              "tenant_id": "bc55eb8c-...",
              "namespace": "kube-system",
              "cluster": "minikube"
            },
            "value": [1730419200, "0.1741"]
          }
        ]
      }
    }
  }
}
```

**Critical Implementation Detail**:
```python
def _query_allocation_metric(self, thanos_url, cloud_account_id, metric_name,
                              start_date, end_date):
    """
    Query allocation metric (gauge showing hourly rate) from Thanos.

    CRITICAL: These are gauge metrics that only exist at CURRENT time.
    We query the instant value and create a synthetic time series for
    the requested range, since historical gauge values don't exist in TSDB.
    """
    query = f'{metric_name}{{tenant_id="{cloud_account_id}"}}'

    # Query at current time (NOT end_date which may be in the past)
    params = {'query': query}  # No 'time' parameter = current time

    response = requests.get(f"{thanos_url}/api/v1/query", params=params)
    # ... convert instant results to synthetic range format
```

### kubecost_worker (CloudTuner SaaS)

**Image**: `invincibledocker24/kubecost_worker:v1.4.1-dev`
**Deployment**: `cloud-tuner-dev/templates/kubecost-worker.yaml`

**Responsibilities**:
1. Poll Metroculus API every 5 minutes for allocation metrics
2. Parse namespace and pod cost data
3. **Create cloud_resource records in MongoDB** (for UI filters)
4. **Create expense records in ClickHouse** (for cost analysis)
5. Handle CollapsingMergeTree upsert pattern (sign: -1 then +1)

**Key Code Sections**:

#### MongoDB Resource Creation
**File**: `metroculus_allocation_processor.py` (lines 150-220)

```python
def create_cloud_resources_for_namespaces(self, allocation_data):
    """
    Create cloud_resource records in MongoDB for namespaces.

    This ensures namespaces appear in available_filters and UI dropdowns.
    Follows the same pattern as AWS/Azure/GCP resources.
    """
    if not allocation_data or 'metrics' not in allocation_data:
        return

    now_ts = int(datetime.now(timezone.utc).timestamp())
    resources_to_create = []

    metrics = allocation_data.get('metrics', {})
    namespace_metric = metrics.get('cloudtuner_kubecost_namespace_total_cost', {})

    if namespace_metric and 'data' in namespace_metric:
        for result in namespace_metric.get('data', {}).get('result', []):
            metric_labels = result.get('metric', {})
            namespace = metric_labels.get('namespace')

            if not namespace:
                continue

            # Generate stable resource ID
            import hashlib
            resource_hash = hashlib.md5(f"namespace-{namespace}".encode()).hexdigest()[:16]
            cloud_resource_id = f"k8s-ns-{resource_hash}"

            resource = {
                'cloud_resource_id': cloud_resource_id,
                'name': f"Namespace: {namespace}",
                'resource_type': 'K8s Namespace',
                'region': None,
                'service_name': 'Kubernetes',
                'tags': {},
                'first_seen': now_ts,
                'last_seen': now_ts,
                'meta': {
                    'namespace': namespace
                },
                'k8s_namespace': namespace,  # Critical for filtering
                'k8s_node': None,
                'k8s_service': None
            }
            resources_to_create.append(resource)

    if resources_to_create:
        try:
            LOG.info(f"Creating {len(resources_to_create)} namespace cloud_resource records")
            self.rest_cl.cloud_resource_create_bulk(
                self.cloud_account_id,
                {'resources': resources_to_create},
                behavior='skip_existing',
                return_resources=False
            )
        except Exception as e:
            LOG.warning(f"Failed to create cloud_resource records: {e}")
```

#### ClickHouse Expense Creation
**File**: `metroculus_allocation_processor.py` (lines 75-148)

```python
def parse_namespace_metrics(self, allocation_data, start_date, end_date):
    """
    Parse namespace-level cost metrics from Metroculus response.

    Creates expense records with k8s_namespace populated for filtering.
    """
    expenses = []

    metrics = allocation_data.get('metrics', {})
    namespace_metric = metrics.get('cloudtuner_kubecost_namespace_total_cost', {})

    if not namespace_metric or 'data' not in namespace_metric:
        LOG.warning("No namespace metrics data found")
        return []

    for result in namespace_metric.get('data', {}).get('result', []):
        metric_labels = result.get('metric', {})
        namespace = metric_labels.get('namespace')
        value = result.get('value')

        if not namespace or not value:
            continue

        # value is [timestamp, "cost_string"]
        cost = float(value[1])
        date = datetime.fromtimestamp(start_date, tz=timezone.utc)

        # Generate stable resource ID
        import hashlib
        resource_hash = hashlib.md5(f"namespace-{namespace}".encode()).hexdigest()[:16]
        resource_id = f"k8s-ns-{resource_hash}"

        expense = {
            'cloud_account_id': self.cloud_account_id,
            'resource_id': resource_id,
            'date': date,
            'cost': cost,
            'sign': 1,
            'k8s_namespace': namespace,  # Enables filtering
            'k8s_node': None,
            'k8s_service': None
        }
        expenses.append(expense)

    return expenses
```

#### Main Processing Loop
**File**: `main.py` (lines 150-220)

```python
def process_cluster(self):
    """
    Main processing loop: fetch metrics, create resources, write expenses.
    """
    now = datetime.now(timezone.utc)
    start_date = int((now - timedelta(days=1)).timestamp())
    end_date = int(now.timestamp())

    # Create processor with ALL required clients
    processor = MetroculusAllocationProcessor(
        cloud_account_id=self.cloud_account_id,
        metroculus_cl=self.metroculus_cl,
        clickhouse_cl=self.clickhouse_cl,
        rest_cl=self.rest_cl  # Critical for MongoDB resource creation
    )

    # Step 1: Fetch cluster-level costs
    cluster_expenses = processor.process_cost_data(cost_data, start_date, end_date)

    # Step 2: Fetch allocation data and create MongoDB resources
    allocation_expenses = processor.process_allocation_data(start_date, end_date)

    # Step 3: Write to ClickHouse separately (different column counts)
    if cluster_expenses:
        self.write_expenses_to_clickhouse(
            cluster_expenses,
            include_k8s_dimensions=False  # 5 columns
        )

    if allocation_expenses:
        self.write_expenses_to_clickhouse(
            allocation_expenses,
            include_k8s_dimensions=True  # 8 columns (+ k8s_namespace, k8s_node, k8s_service)
        )
```

### REST API (CloudTuner SaaS)

**Service**: `restapi`
**File**: `rest_api_server/controllers/expense.py`

**Modifications for K8s**:

#### Phase 1: Cluster-level cost aggregation
**Lines**: 831-892, 1527-1531

```python
@property
def metroculus_cl(self):
    if self._metroculus_cl is None:
        self._metroculus_cl = MetroculusClient(
            url=self._config.metroculus_url(),
            secret=self._config.cluster_secret())
    return self._metroculus_cl

def _get_k8s_costs(self, cloud_account_ids, start_date, end_date):
    """
    Fetch Kubernetes costs for KUBERNETES_CNR accounts via Metroculus.
    """
    k8s_accounts = [acc for acc in cloud_account_ids
                    if acc['type'] == CloudTypes.KUBERNETES_CNR]

    if not k8s_accounts:
        return None

    k8s_total_cost = 0
    k8s_cost_breakdown = []

    for account in k8s_accounts:
        try:
            cost_data = self.metroculus_cl.get_kubecost_cluster_costs(
                account['id'], start_date, end_date
            )
            account_cost = cost_data.get('total_cost', 0)
            k8s_total_cost += account_cost

            k8s_cost_breakdown.append({
                'cloud_account_id': account['id'],
                'cloud_account_name': account['name'],
                'cost': account_cost,
                'breakdown': cost_data.get('breakdown', {})
            })
        except Exception as e:
            LOG.warning(f"Failed to fetch K8s costs for {account['id']}: {e}")

    return {
        'k8s_total_cost': k8s_total_cost,
        'k8s_cost_breakdown': k8s_cost_breakdown
    }

def get(self, organization_id, **kwargs):
    """
    GET /restapi/v2/clean_expenses
    """
    # ... existing expense processing

    # Add K8s costs if applicable
    k8s_costs = self._get_k8s_costs(cloud_account_ids, start_date, end_date)
    if k8s_costs:
        result['k8s_costs'] = k8s_costs
        result['total_cost'] += k8s_costs['k8s_total_cost']

    return result
```

#### Phase 2: Namespace/pod filtering support
**File**: `available_filters.py` (lines 79-80, 201-202)

**No changes required** - endpoint already supports k8s dimensions:

```python
# Line 79-80
for field in ['service_name', 'region', 'k8s_node',
              'k8s_service', 'k8s_namespace']:

# Line 201-202
collected_filters = [
    'service_name', 'pool_id', 'employee_id', 'k8s_node', 'region',
    'resource_type', 'k8s_namespace', 'k8s_service', 'cloud_account_id'
]
```

The endpoint queries MongoDB resources collection. When kubecost_worker creates resources with `k8s_namespace` field, they automatically appear in filter results.

### Frontend (NGUI)

**No code changes required** - filters already implemented:
```bash
curl -X POST http://localhost:3000/restapi/v2/expenses_async \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "start_date": 1730419200,
    "end_date": 1730505600,
    "filter": {
      "k8s_namespace": "default"
    }
  }'
```

---

## Implementation Details

### Database Schema Changes

#### ClickHouse: expenses table
```sql
CREATE TABLE expenses (
    cloud_account_id     String,
    resource_id          String,
    date                 DateTime,
    cost                 Float64,
    sign                 Int8,
    k8s_namespace        Nullable(String),  -- Added for Phase 2
    k8s_node             Nullable(String),  -- Added for Phase 2
    k8s_service          Nullable(String)   -- Added for Phase 2
) ENGINE = CollapsingMergeTree(sign)
ORDER BY (cloud_account_id, resource_id, date);
```

**Migration**: `diworker/migrations/202511081530000_k8s_dimensions.py`

**Verification**:
```bash
kubectl exec -n default clickhouse-0 -- \
  clickhouse-client -q "
    SELECT k8s_namespace, k8s_node, k8s_service, date, cost, sign
    FROM expenses
    WHERE k8s_namespace IS NOT NULL
    ORDER BY date DESC
    LIMIT 10;
  "
```

#### MongoDB: cloud_resources collection

**Existing schema** (no changes required):
```javascript
{
  _id: ObjectId("..."),
  cloud_resource_id: "k8s-ns-abc123",
  cloud_account_id: "bc55eb8c-...",
  name: "Namespace: default",
  resource_type: "K8s Namespace",
  service_name: "Kubernetes",
  region: null,
  k8s_namespace: "default",  // Filter field
  k8s_node: null,
  k8s_service: null,
  tags: {},
  first_seen: 1730419200,
  last_seen: 1730505600,
  meta: {
    namespace: "default"
  }
}
```

**Verification**:
```bash
kubectl exec -n default mongo-0 -- mongo restapi \
  --eval "db.cloud_resource.find({k8s_namespace: {\$ne: null}}).pretty()"
```

### Metric Definitions

#### Cluster-Level Metrics (Phase 1)
| Metric | Type | Description | Unit |
|--------|------|-------------|------|
| `kubecost_cluster_management_cost` | Gauge | Control plane overhead | USD/hour |
| `kubecost_cluster_cpu_cost` | Gauge | Total CPU cost | USD/hour |
| `kubecost_cluster_memory_cost` | Gauge | Total RAM cost | USD/hour |
| `kubecost_cluster_storage_cost` | Gauge | PV/PVC cost | USD/hour |
| `kubecost_cluster_network_cost` | Gauge | Network egress | USD/hour |
| `kubecost_cluster_load_balancer_cost` | Gauge | LB cost | USD/hour |

#### Allocation-Level Metrics (Phase 2)
| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `cloudtuner_kubecost_namespace_total_cost` | Gauge | tenant_id, namespace, cluster | Total namespace cost rate |
| `cloudtuner_kubecost_namespace_cpu_cost` | Gauge | tenant_id, namespace, cluster | Namespace CPU cost rate |
| `cloudtuner_kubecost_namespace_ram_cost` | Gauge | tenant_id, namespace, cluster | Namespace RAM cost rate |
| `cloudtuner_kubecost_namespace_pv_cost` | Gauge | tenant_id, namespace, cluster | Namespace PV cost rate |
| `cloudtuner_kubecost_pod_total_cost` | Gauge | tenant_id, namespace, pod, cluster | Pod cost rate |
| `cloudtuner_kubecost_pod_cpu_cost` | Gauge | tenant_id, namespace, pod, cluster | Pod CPU cost rate |
| `cloudtuner_kubecost_pod_ram_cost` | Gauge | tenant_id, namespace, pod, cluster | Pod RAM cost rate |

**Why Gauges vs Counters**:
- **Gauge**: Instantaneous value that can go up or down (cost per hour)
- **Counter**: Monotonically increasing value (total cost accumulated)

Kubecost allocation API returns "last 1 hour cost rate", not cumulative totals. Each query recalculates based on current resource state. Therefore, gauges are correct.

---

## Critical Architectural Decisions

### Decision 1: No Direct Customer → CloudTuner API Calls

**Context**: Initial Phase 2 design proposed kubecost_worker directly querying customer Kubecost APIs.

**Problem**:
- Breaks multi-tenant SaaS model
- Requires network connectivity from CloudTuner SaaS to every customer cluster
- Security nightmare (credentials, firewall rules, VPN tunnels)
- Single-cluster deployments only (no multi-cluster aggregation)

**Solution**:
Use existing Prometheus remote_write path that already handles:
- Authentication (basic auth, headers)
- Multi-tenancy (Cloud-Account-Id header → tenant isolation)
- Data aggregation (Thanos stores all clusters' metrics)
- Security boundaries (customer initiates connection, no inbound to cluster)

**Files Affected**:
- DISCARDED: `kubecost_worker/kubecost_worker/allocation_processor.py` (direct API approach)
- KEPT: `kubecost_worker/kubecost_worker/metroculus_allocation_processor.py` (remote_write approach)

### Decision 2: MongoDB Resources + ClickHouse Expenses Pattern

**Context**: Initial implementation wrote only to ClickHouse expenses table.

**Problem**:
- UI `available_filters` endpoint queries MongoDB resources, not ClickHouse
- No namespace/pod options appeared in filter dropdowns
- Diverged from CloudTuner's standard AWS/Azure/GCP pattern

**User Feedback**:
> "so we messed up writing all data to clickhouse isnt it ? it should be similar structure like the rest of the stack , details in maria mongo and clickhouse"

**Solution**:
Follow CloudTuner's established pattern:
- **MongoDB `cloud_resources`**: Resource metadata, tags, k8s dimensions → powers filters
- **ClickHouse `expenses`**: Cost data, time-series → powers analytics

**Implementation**:
```python
# Step 1: Create MongoDB resources (for UI filters)
processor.create_cloud_resources_for_namespaces(allocation_data)

# Step 2: Create ClickHouse expenses (for cost analysis)
processor.parse_namespace_metrics(allocation_data)
processor.parse_pod_metrics(allocation_data)
```

**Files Modified**:
- `kubecost_worker/kubecost_worker/metroculus_allocation_processor.py` (added `create_cloud_resources_for_namespaces()`)
- `kubecost_worker/kubecost_worker/main.py` (pass `rest_cl` to processor)

### Decision 3: Instant Queries for Gauge Metrics

**Context**: Metroculus was querying allocation metrics with `query_range` at historical timestamps.

**Problem**:
- Allocation metrics are gauges showing "current hourly rate"
- Historical gauge values don't exist in Thanos (only current instant value)
- Queries at `end_date` in the past returned empty results

**Solution**:
Query gauges as instant queries at current time, synthesize time range:

```python
def _query_allocation_metric(self, thanos_url, cloud_account_id, metric_name,
                              start_date, end_date):
    # Query at current time (not end_date which is in the past)
    params = {'query': query}  # No 'time' parameter = current time

    response = requests.get(f"{thanos_url}/api/v1/query", params=params)

    # Convert instant results to synthetic range format
    # Each namespace gets its instant cost value for the entire range
```

**Tradeoff**: Loses historical cost variation within the time range, but accurately represents current allocation state.

**Files Modified**:
- `metroculus/metroculus_api/controllers/kubecost_metrics.py` (lines 150-200)

### Decision 4: Separate Writes for Cluster vs Allocation Expenses

**Context**: ClickHouse write failed with "column count mismatch" error.

**Problem**:
- Cluster expenses: 5 columns (cloud_account_id, resource_id, date, cost, sign)
- Allocation expenses: 8 columns (+ k8s_namespace, k8s_node, k8s_service)
- Cannot write both in single bulk insert

**Solution**:
Split into two separate writes with different column specs:

```python
if cluster_expenses:
    self.write_expenses_to_clickhouse(
        cluster_expenses,
        include_k8s_dimensions=False  # 5 columns
    )

if allocation_expenses:
    self.write_expenses_to_clickhouse(
        allocation_expenses,
        include_k8s_dimensions=True  # 8 columns
    )
```

**Files Modified**:
- `kubecost_worker/kubecost_worker/main.py` (lines 180-195)

---

## Deployment Guide

### Prerequisites

| Requirement | Verification | Notes |
|-------------|--------------|-------|
| Kubernetes cluster | `kubectl version` | v1.20+ required |
| CloudTuner stack | `kubectl get pods -n default | grep -E "restapi\|metroculus\|diproxy"` | Must be running |
| Helm 3 | `helm version` | Helm 2 not supported |
| Cloud Account ID | Query MongoDB or create via UI | K8s account type: `kubernetes_cnr` |
| Cluster secret | From CloudTuner config | Used for Metroculus auth |

### Step 1: Deploy CloudTuner Backend Components

#### 1.1 Build and Push Images

```bash
# Build Metroculus (if modified)
cd /Users/balaji/source/code/cloudtuner/cloud-tuner/metroculus
docker build -t invincibledocker24/metroculus:v1.4.0-k8s .
docker push invincibledocker24/metroculus:v1.4.0-k8s

# Build kubecost_worker
cd /Users/balaji/source/code/cloudtuner/cloud-tuner/kubecost_worker
docker build -t invincibledocker24/kubecost_worker:v1.4.1-dev .
docker push invincibledocker24/kubecost_worker:v1.4.1-dev

# Build REST API (if modified)
cd /Users/balaji/source/code/cloudtuner/cloud-tuner/rest_api
docker build -t invincibledocker24/rest_api:v1.4.0-k8s .
docker push invincibledocker24/rest_api:v1.4.0-k8s
```

#### 1.2 Update Helm Values

Edit `/Users/balaji/source/code/cloudtuner/cloudtuner-dev-helm/cloud-tuner-dev/values.yaml`:

```yaml
metroculus:
  image:
    repository: invincibledocker24/metroculus
    tag: v1.4.0-k8s

kubecost_worker:
  image:
    repository: invincibledocker24/kubecost_worker
    tag: v1.4.1-dev
  enabled: true
  schedule: "*/5 * * * *"  # Every 5 minutes

restapi:
  image:
    repository: invincibledocker24/rest_api
    tag: v1.4.0-k8s
```

#### 1.3 Deploy CloudTuner Stack

```bash
cd /Users/balaji/source/code/cloudtuner/cloudtuner-dev-helm

helm upgrade --install cloud-tuner-dev ./cloud-tuner-dev \
  -n default \
  --wait --timeout 10m

# Verify deployments
kubectl get pods -n default | grep -E "metroculus|kubecost-worker|restapi"
```

### Step 2: Deploy Kubecost Integration (Customer Cluster)

#### 2.1 Obtain Configuration Values

```bash
# Get Cloud Account ID
CLOUD_ACCOUNT_ID="bc55eb8c-5db2-4c32-b976-2df0edb0619a"

# Get Cluster Secret
CLUSTER_SECRET="fc83d31-461d-44c5-b4d5-41a32d6c36a1"

# Verify CloudTuner diproxy endpoint
kubectl get svc -n default diproxy
```

#### 2.2 Install Kubecost Integration Chart

```bash
cd /Users/balaji/source/code/cloudtuner/cloudtuner-dev-helm/k8s-kubecost

helm upgrade --install kubecost-dev ./charts/kubecost-integration \
  -n kubecost-dev \
  --create-namespace \
  --set global.imageTag="v1.3.0" \
  --set kubecost.prometheus.server.remoteWrite[0].url="http://diproxy.default.svc.cluster.local/storage/api/v2/write" \
  --set kubecost.prometheus.server.remoteWrite[0].headers.Cloud-Account-Id="$CLOUD_ACCOUNT_ID" \
  --set allocationExporter.enabled=true \
  --wait --timeout 10m
```

#### 2.3 Verify Deployment

```bash
# Check pods
kubectl get pods -n kubecost-dev

# Expected output:
# kubecost-cost-analyzer-xxx           Running
# kubecost-prometheus-server-xxx       Running
# kubecost-allocation-exporter-xxx     Running

# Check allocation-exporter metrics
kubectl port-forward -n kubecost-dev svc/kubecost-allocation-exporter 19090:19090
curl http://localhost:19090/metrics | grep cloudtuner_kubecost_namespace_total_cost

# Check remote_write flow
kubectl logs -n default -l app=diproxy --tail=100 | grep -E "POST.*write"
```

---

## Verification and Testing

### Test 1: Metric Export from Customer Cluster

```bash
# Port-forward to allocation-exporter
kubectl port-forward -n kubecost-dev svc/kubecost-allocation-exporter 19090:19090

# Verify metrics are exported
curl -s http://localhost:19090/metrics | grep cloudtuner_kubecost

# Expected output:
# cloudtuner_kubecost_namespace_total_cost{tenant_id="bc55eb8c-...",namespace="default",cluster="minikube"} 0.2573
# cloudtuner_kubecost_namespace_total_cost{tenant_id="bc55eb8c-...",namespace="kube-system",cluster="minikube"} 0.1741
# cloudtuner_kubecost_pod_total_cost{tenant_id="bc55eb8c-...",namespace="default",pod="nginx-xxx",cluster="minikube"} 0.05
```

### Test 2: Remote Write to Thanos

```bash
# Check diproxy logs for incoming writes
kubectl logs -n default -l app=diproxy --tail=50 | grep -E "POST.*write.*200"

# Expected: 200 OK responses for remote_write POSTs

# Query Thanos directly
kubectl port-forward -n default svc/thanos-query 9090:9090
curl -s 'http://localhost:9090/api/v1/query?query=cloudtuner_kubecost_namespace_total_cost' | jq .
```

### Test 3: Metroculus API Query

```bash
# Port-forward to Metroculus
kubectl port-forward -n default svc/metroculus 8969:80

# Query allocation metrics
curl -s -H "Secret: $CLUSTER_SECRET" \
  "http://localhost:8969/metroculus/v2/kubecost_metrics?cloud_account_id=$CLOUD_ACCOUNT_ID&metrics=cloudtuner_kubecost_namespace_total_cost&start_date=1730419200&end_date=1730505600" \
  | jq .

# Expected output:
# {
#   "cloud_account_id": "bc55eb8c-...",
#   "metrics": {
#     "cloudtuner_kubecost_namespace_total_cost": {
#       "status": "success",
#       "data": {
#         "result": [
#           {"metric": {"namespace": "default"}, "value": [1730419200, "0.2573"]},
#           {"metric": {"namespace": "kube-system"}, "value": [1730419200, "0.1741"]}
#         ]
#       }
#     }
#   }
# }
```

### Test 4: kubecost_worker Processing

```bash
# Trigger manual run (or wait for CronJob)
kubectl create job --from=cronjob/kubecost-worker kubecost-worker-manual -n default

# Check logs
kubectl logs -n default job/kubecost-worker-manual -f

# Expected log messages:
# INFO - Querying allocation metrics from Metroculus...
# INFO - Creating 5 namespace cloud_resource records
# INFO - Successfully created 5 namespace resources
# INFO - Parsed 5 namespace expenses, 12 pod expenses
# INFO - Wrote 5 expenses to ClickHouse (allocation with k8s dimensions)
```

### Test 5: MongoDB Resources Created

```bash
# Query MongoDB for K8s resources
kubectl exec -n default mongo-0 -- mongo restapi --eval "
  db.cloud_resource.find({
    k8s_namespace: {\$ne: null}
  }).pretty()
"

# Expected output:
# {
#   "_id": ObjectId("..."),
#   "cloud_resource_id": "k8s-ns-abc123",
#   "name": "Namespace: default",
#   "resource_type": "K8s Namespace",
#   "k8s_namespace": "default",
#   "cloud_account_id": "bc55eb8c-..."
# }
```

### Test 6: ClickHouse Expenses Written

```bash
# Query ClickHouse for K8s expenses
kubectl exec -n default clickhouse-0 -- clickhouse-client -q "
  SELECT
    k8s_namespace,
    k8s_node,
    k8s_service,
    date,
    SUM(cost * sign) as total_cost,
    COUNT() as records
  FROM expenses
  WHERE cloud_account_id = '$CLOUD_ACCOUNT_ID'
    AND k8s_namespace IS NOT NULL
  GROUP BY k8s_namespace, k8s_node, k8s_service, date
  ORDER BY date DESC, total_cost DESC
  LIMIT 20;
"

# Expected output:
# k8s_namespace    k8s_node  k8s_service  date         total_cost  records
# default          NULL      NULL         2025-11-01   0.2573      1
# kube-system      NULL      NULL         2025-11-01   0.1741      1
# kubecost-dev     NULL      NULL         2025-11-01   0.0652      1
```

### Test 7: REST API available_filters

```bash
# Port-forward to REST API
kubectl port-forward -n default svc/restapi 8999:80

# Get auth token (login via UI or use existing token)
TOKEN="eyJhbGc..."

# Query available filters
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8999/restapi/v2/available_filters?organization_id=$ORG_ID" \
  | jq .k8s_namespace

# Expected output:
# ["default", "kube-system", "kubecost-dev", "kubecost", "ingress-nginx"]
```

### Test 8: REST API clean_expenses with K8s Filter

```bash
# Query expenses with namespace filter
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8999/restapi/v2/clean_expenses?organization_id=$ORG_ID&start_date=1730419200&end_date=1730505600&k8s_namespace=default" \
  | jq .

# Expected output:
# {
#   "start_date": 1730419200,
#   "end_date": 1730505600,
#   "total_cost": 0.2573,
#   "clean_expenses": [
#     {
#       "cloud_account_id": "bc55eb8c-...",
#       "date": "2025-11-01",
#       "cost": 0.2573,
#       "k8s_namespace": "default"
#     }
#   ],
#   "k8s_costs": {
#     "k8s_total_cost": 0.2573,
#     "k8s_cost_breakdown": [...]
#   }
# }
```

### Test 9: Frontend Filter UI

1. Open NGUI: `http://localhost:3000`
2. Navigate to Cost Dashboard
3. Verify filter dropdowns populate:
   - K8s Namespace: `default`, `kube-system`, `kubecost-dev`, ...
   - K8s Node: (if node-level metrics enabled)
   - K8s Service: (if service-level metrics enabled)
4. Apply `k8s_namespace=default` filter
5. Verify charts update with namespace-specific costs

---

## Troubleshooting

### Issue 1: Allocation Metrics Not Exported

**Symptoms**:
```bash
curl http://localhost:19090/metrics | grep cloudtuner_kubecost
# No output
```

**Diagnosis**:
```bash
kubectl logs -n kubecost-dev -l app=kubecost-allocation-exporter --tail=100

# Look for errors:
# ERROR - Failed to query Kubecost allocation API: Connection refused
# ERROR - Kubecost API returned 500: Internal Server Error
```

**Fixes**:

1. **Kubecost not reachable**:
   ```bash
   # Verify Kubecost service
   kubectl get svc -n kubecost-dev kubecost-cost-analyzer

   # Test connection from allocation-exporter pod
   kubectl exec -n kubecost-dev deployment/kubecost-allocation-exporter -- \
     curl -s http://kubecost-cost-analyzer:9090/allocation?window=1h
   ```

2. **Kubecost API errors**:
   ```bash
   # Check Kubecost logs
   kubectl logs -n kubecost-dev -l app=kubecost-cost-analyzer --tail=100

   # Common issues:
   # - Insufficient RBAC permissions
   # - Prometheus not scraping
   # - Pricing data not configured
   ```

3. **Exporter configuration**:
   ```bash
   # Verify environment variables
   kubectl get deployment -n kubecost-dev kubecost-allocation-exporter -o yaml | grep -A20 "env:"

   # Should see:
   # - KUBECOST_URL: http://kubecost-cost-analyzer:9090
   # - TENANT_ID: bc55eb8c-...
   # - CLUSTER_NAME: minikube
   ```

### Issue 2: Remote Write Not Reaching CloudTuner

**Symptoms**:
```bash
kubectl logs -n default -l app=diproxy --tail=50 | grep write
# No log entries
```

**Diagnosis**:
```bash
# Check Prometheus remote_write config
kubectl get configmap -n kubecost-dev kubecost-prometheus-server -o yaml | grep -A30 remote_write

# Check Prometheus logs
kubectl logs -n kubecost-dev -l app=kubecost-prometheus-server --tail=100 | grep remote

# Look for errors:
# level=warn component=remote msg="Failed to send batch, retrying"
# level=error component=remote msg="non-recoverable error" err="401 Unauthorized"
```

**Fixes**:

1. **Network connectivity**:
   ```bash
   # Test from Prometheus pod
   kubectl exec -n kubecost-dev deployment/kubecost-prometheus-server -- \
     curl -v http://diproxy.default.svc.cluster.local/storage/api/v2/write

   # Should get 400 (expected, means endpoint is reachable)
   ```

2. **Authentication headers**:
   ```bash
   # Verify Cloud-Account-Id header in remote_write config
   kubectl get configmap -n kubecost-dev kubecost-prometheus-server -o yaml | grep Cloud-Account-Id

   # Must match K8s cloud account ID in CloudTuner
   ```

3. **Metric filtering**:
   ```bash
   # Check write_relabel_configs
   kubectl get configmap -n kubecost-dev kubecost-prometheus-server -o yaml | grep -A10 write_relabel_configs

   # Regex must include cloudtuner_kubecost_* metrics
   ```

### Issue 3: Metroculus Returns Empty Metrics

**Symptoms**:
```bash
curl "http://localhost:8969/metroculus/v2/kubecost_metrics?cloud_account_id=$CLOUD_ACCOUNT_ID&metrics=cloudtuner_kubecost_namespace_total_cost"
# {"metrics": {"cloudtuner_kubecost_namespace_total_cost": {"data": {"result": []}}}}
```

**Diagnosis**:
```bash
# Check Metroculus logs
kubectl logs -n default -l app=metroculus --tail=100

# Look for:
# WARNING - Thanos query returned empty result
# ERROR - Failed to query Thanos: connection refused
```

**Fixes**:

1. **Thanos not receiving data**:
   ```bash
   # Query Thanos directly
   kubectl port-forward -n default svc/thanos-query 9090:9090
   curl -s 'http://localhost:9090/api/v1/query?query=cloudtuner_kubecost_namespace_total_cost' | jq .

   # If empty, remote_write is not working (see Issue 2)
   ```

2. **Tenant ID mismatch**:
   ```bash
   # Verify tenant_id label in Thanos
   curl -s 'http://localhost:9090/api/v1/query?query=cloudtuner_kubecost_namespace_total_cost' | jq '.data.result[].metric.tenant_id'

   # Must match cloud_account_id query parameter
   ```

3. **Query time range issues**:
   ```bash
   # For gauges, query at current time (no time parameter)
   curl -s 'http://localhost:9090/api/v1/query?query=cloudtuner_kubecost_namespace_total_cost'

   # NOT query_range with historical timestamps
   ```

### Issue 4: kubecost_worker Not Processing Data

**Symptoms**:
```bash
kubectl logs -n default -l app=kubecost-worker --tail=50
# INFO - No allocation data returned from Metroculus
```

**Diagnosis**:
```bash
# Check CronJob status
kubectl get cronjob -n default kubecost-worker

# Check Job status
kubectl get jobs -n default -l app=kubecost-worker --sort-by=.metadata.creationTimestamp

# Check worker logs for errors
kubectl logs -n default job/kubecost-worker-xxx
```

**Fixes**:

1. **Metroculus API errors**:
   ```bash
   # Verify cluster secret
   kubectl get secret -n default cluster-secret -o jsonpath='{.data.cluster_secret}' | base64 -d

   # Test Metroculus API manually
   kubectl exec -n default deployment/kubecost-worker -- \
     curl -H "Secret: $CLUSTER_SECRET" \
     "http://metroculus.default.svc.cluster.local/metroculus/v2/kubecost_metrics?cloud_account_id=$CLOUD_ACCOUNT_ID&metrics=cloudtuner_kubecost_namespace_total_cost"
   ```

2. **Cloud account not found**:
   ```bash
   # Verify K8s cloud account exists
   kubectl exec -n default mongo-0 -- mongo restapi --eval "
     db.cloud_account.find({
       _id: '$CLOUD_ACCOUNT_ID',
       type: 'kubernetes_cnr',
       deleted_at: 0
     }).pretty()
   "
   ```

3. **Parser errors**:
   ```bash
   # Check worker logs for parse errors
   kubectl logs -n default job/kubecost-worker-xxx | grep -E "ERROR|Failed"

   # Common issues:
   # - Unexpected Metroculus response structure
   # - Missing metric labels (namespace, pod)
   # - Invalid cost values (null, negative)
   ```

### Issue 5: Namespaces Not Appearing in UI Filters

**Symptoms**:
```bash
curl "http://localhost:8999/restapi/v2/available_filters?organization_id=$ORG_ID" | jq .k8s_namespace
# null or []
```

**Root Cause**: MongoDB resources not created (see Critical Decision #2).

**Fixes**:

1. **Verify kubecost_worker created resources**:
   ```bash
   kubectl logs -n default job/kubecost-worker-xxx | grep "cloud_resource"

   # Should see:
   # INFO - Creating 5 namespace cloud_resource records
   # INFO - Successfully created 5 namespace resources
   ```

2. **Check MongoDB directly**:
   ```bash
   kubectl exec -n default mongo-0 -- mongo restapi --eval "
     db.cloud_resource.find({
       cloud_account_id: '$CLOUD_ACCOUNT_ID',
       k8s_namespace: {\$ne: null}
     }).count()
   "

   # Should return > 0
   ```

3. **Verify rest_cl passed to processor**:
   ```bash
   # Check main.py instantiation
   grep -A5 "MetroculusAllocationProcessor" /Users/balaji/source/code/cloudtuner/cloud-tuner/kubecost_worker/kubecost_worker/main.py

   # Must include: rest_cl=self.rest_cl
   ```

4. **Re-run kubecost_worker**:
   ```bash
   # Trigger manual job
   kubectl create job --from=cronjob/kubecost-worker kubecost-worker-fix -n default

   # Watch logs
   kubectl logs -n default job/kubecost-worker-fix -f
   ```

### Issue 6: ClickHouse Column Count Mismatch

**Symptoms**:
```bash
kubectl logs -n default job/kubecost-worker-xxx | grep -A5 "ERROR"
# ERROR - Insert data column count does not match column names
```

**Root Cause**: Mixing cluster expenses (5 columns) with allocation expenses (8 columns) in single write.

**Fix**: Ensure separate writes (see Critical Decision #4):

```python
# Correct pattern in main.py
if cluster_expenses:
    self.write_expenses_to_clickhouse(cluster_expenses, include_k8s_dimensions=False)

if allocation_expenses:
    self.write_expenses_to_clickhouse(allocation_expenses, include_k8s_dimensions=True)
```

Rebuild and redeploy kubecost_worker if fix needed.

---

## Production Considerations

### Multi-Cluster Deployment

**Architecture**:
```
Customer Cluster 1 (US-East)    Customer Cluster 2 (EU-West)
│                               │
├─ Kubecost (tenant_id: aaa)    ├─ Kubecost (tenant_id: bbb)
├─ allocation-exporter          ├─ allocation-exporter
├─ Prometheus                   ├─ Prometheus
│  └─ remote_write              │  └─ remote_write
│     (Cloud-Account-Id: aaa)   │     (Cloud-Account-Id: bbb)
└─────────┬─────────────────────┴─────────┬──────────────
          │                               │
          └───────────▼───────────────────┘
                  CloudTuner SaaS
                  (Thanos aggregates both)
```

**Configuration**:
- Each cluster gets unique Cloud-Account-Id in remote_write headers
- Thanos stores all clusters' data with tenant_id label
- kubecost_worker runs once per cloud_account_id
- REST API aggregates costs across all K8s accounts in organization

**Helm values**:
```yaml
# Cluster 1
kubecost:
  prometheus:
    server:
      remoteWrite:
        - headers:
            Cloud-Account-Id: "aaa-111-..."

# Cluster 2
kubecost:
  prometheus:
    server:
      remoteWrite:
        - headers:
            Cloud-Account-Id: "bbb-222-..."
```

### Security Considerations

1. **Authentication**:
   - Remote write basic auth (rotate credentials periodically)
   - Metroculus API requires cluster secret
   - REST API uses JWT tokens

2. **Encryption**:
   - HTTPS for remote_write in production
   - TLS certificates for ingress endpoints
   - Encrypt secrets at rest (Kubernetes secrets encryption)

3. **Multi-tenancy Isolation**:
   - Cloud-Account-Id header enforces tenant isolation
   - Thanos queries filter by tenant_id label
   - MongoDB resources scoped by cloud_account_id

4. **Network Policies**:
   ```yaml
   # Customer cluster: Allow egress to CloudTuner diproxy only
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: prometheus-egress
   spec:
     podSelector:
       matchLabels:
         app: kubecost-prometheus-server
     policyTypes:
     - Egress
     egress:
     - to:
       - podSelector: {}  # DNS
       ports:
       - protocol: TCP
         port: 53
     - to:
       - ipBlock:
           cidr: 0.0.0.0/0  # CloudTuner SaaS endpoint
       ports:
       - protocol: TCP
         port: 443
   ```

### Scaling Considerations

1. **Metrics Volume**:
   - 100 namespaces × 10 metrics = 1,000 time series per cluster
   - 1,000 clusters = 1M time series
   - Thanos handles billions of series, but configure retention policies

2. **kubecost_worker CronJob**:
   - Current: 5-minute cadence (12 runs/hour)
   - Production: Consider 15-minute cadence (4 runs/hour)
   - Use Kubernetes Job parallelism for large deployments

3. **ClickHouse Optimization**:
   ```sql
   -- Add materialized view for common queries
   CREATE MATERIALIZED VIEW expenses_namespace_daily
   ENGINE = SummingMergeTree
   ORDER BY (cloud_account_id, date, k8s_namespace)
   AS SELECT
       cloud_account_id,
       date,
       k8s_namespace,
       SUM(cost * sign) as total_cost
   FROM expenses
   WHERE k8s_namespace IS NOT NULL
   GROUP BY cloud_account_id, date, k8s_namespace;
   ```

4. **MongoDB Indexing**:
   ```javascript
   db.cloud_resource.createIndex({
     cloud_account_id: 1,
     k8s_namespace: 1,
     deleted_at: 1
   });

   db.cloud_resource.createIndex({
     k8s_namespace: 1,
     last_seen: -1
   });
   ```

### Monitoring and Alerting

1. **Metrics to Monitor**:
   ```promql
   # Remote write lag (Prometheus)
   prometheus_remote_storage_highest_timestamp_in_seconds - time()

   # kubecost_worker success rate
   kube_job_status_succeeded{job_name=~"kubecost-worker-.*"} /
   kube_job_status_start_time{job_name=~"kubecost-worker-.*"}

   # ClickHouse write errors
   rate(clickhouse_write_errors_total[5m])

   # Metroculus API errors
   rate(metroculus_api_errors_total[5m])
   ```

2. **Alerts**:
   ```yaml
   - alert: KubecostRemoteWriteFailing
     expr: rate(prometheus_remote_storage_failed_samples_total[5m]) > 0
     for: 10m
     annotations:
       summary: "Kubecost metrics not reaching CloudTuner"

   - alert: KubecostWorkerFailing
     expr: kube_job_status_failed{job_name=~"kubecost-worker-.*"} > 0
     for: 5m
     annotations:
       summary: "kubecost_worker CronJob failing"

   - alert: K8sExpensesStale
     expr: time() - max(expenses_last_insert_time{cloud_account_type="kubernetes_cnr"}) > 3600
     for: 30m
     annotations:
       summary: "No K8s expense data written in last hour"
   ```

### Cost Optimization

1. **Storage Retention**:
   - Thanos: 90 days for high-resolution metrics
   - ClickHouse: 2 years for expense data
   - MongoDB: Keep resources indefinitely (small footprint)

2. **Resource Requests/Limits**:
   ```yaml
   allocation-exporter:
     resources:
       requests:
         cpu: 100m
         memory: 256Mi
       limits:
         cpu: 500m
         memory: 512Mi

   kubecost_worker:
     resources:
       requests:
         cpu: 200m
         memory: 512Mi
       limits:
         cpu: 1000m
         memory: 2Gi
   ```

3. **Prometheus Metric Filtering**:
   ```yaml
   # Only forward essential metrics
   write_relabel_configs:
     - source_labels: [__name__]
       regex: 'cloudtuner_kubecost_.*|kubecost_cluster_.*'
       action: keep
   ```

---

## Summary

This integration successfully extends CloudTuner's multi-cloud cost management to Kubernetes environments using a SaaS-compatible architecture. Key achievements:

✅ **Phase 1 Complete**: Cluster-level cost aggregation via Prometheus remote_write
✅ **Phase 2 In Progress**: Namespace/pod-level cost attribution following CloudTuner's MongoDB + ClickHouse pattern
✅ **Multi-tenant**: Supports unlimited customer clusters via tenant isolation
✅ **Secure**: No direct customer → SaaS API calls, customer initiates all connections
✅ **Scalable**: Leverages existing Thanos infrastructure for time-series storage

**Next Steps**:
1. Complete Phase 2 deployment and UI verification
2. Implement Phase 3 real-time metrics dashboards
3. Develop Phase 4 optimization recommendations

For questions or issues, contact the CloudTuner backend team or file an issue in the cloudtuner-dev-helm repository.
