# Phase 3: Kubecost Allocation API Integration

**Date**: 2025-10-13
**Status**: Planning Complete, Ready for Implementation

---

## Overview

Phase 3 completes the Kubernetes cost integration by capturing CPU, RAM, and PV allocation costs from Kubecost's allocation API. This closes the ~$75/week gap identified in Phase 2.

**Current State** (Phase 2):
- Infrastructure costs only: $29.84/week
- Management: $10.40
- Load Balancer: $2.49
- Network: $16.95

**Target State** (Phase 3):
- Full allocation costs: ~$105/week
- CPU allocation: ~$50/week
- RAM allocation: ~$30/week
- PV allocation: ~$10/week
- Infrastructure: $29.84/week (unchanged)

---

## Kubecost Allocation API Analysis

### API Endpoint
```
GET http://kubecost-cost-analyzer:9090/model/allocation
```

### Query Parameters
| Parameter | Description | Example |
|-----------|-------------|---------|
| `window` | Time window | `7d`, `24h`, `30d`, `today`, `yesterday`, `week`, `month` |
| `aggregate` | Aggregation level | `namespace`, `pod`, `controller`, `service`, `label:app` |
| `filterNamespaces` | Namespace filter | `production,staging` |
| `filterLabels` | Label filter | `app=backend,env=prod` |

### Response Structure
```json
{
  "code": 200,
  "data": [
    {
      "namespace-name": {
        "name": "namespace-name",
        "properties": {
          "namespace": "namespace-name",
          "labels": { ... },
          "namespaceLabels": { ... }
        },
        "window": {
          "start": "2025-10-07T00:00:00Z",
          "end": "2025-10-08T00:00:00Z"
        },
        "minutes": 1440,

        // CPU metrics
        "cpuCores": 0.32482,
        "cpuCoreRequestAverage": 0.25,
        "cpuCoreUsageAverage": 0.18,
        "cpuCoreHours": 7.79564,
        "cpuCost": 6.91764,
        "cpuEfficiency": 0.72,  // 72% efficiency

        // RAM metrics
        "ramBytes": 3124873293,
        "ramByteRequestAverage": 2684354560,  // 2.5GB
        "ramByteUsageAverage": 1879048192,    // 1.75GB
        "ramByteHours": 74996959039,
        "ramCost": 3.0041,
        "ramEfficiency": 0.70,  // 70% efficiency

        // PV metrics
        "pvBytes": 10737418240,  // 10GB
        "pvByteHours": 257698037760,
        "pvCost": 1.72,
        "pvs": {
          "pvc-name": {
            "byteHours": 257698037760,
            "cost": 1.72,
            "providerID": "aws://...",
            "adjustment": 0
          }
        },

        // Network metrics
        "networkCost": 0.25,
        "networkTransferBytes": 1048576000,
        "networkReceiveBytes": 524288000,
        "networkCrossZoneCost": 0.05,
        "networkCrossRegionCost": 0.10,
        "networkInternetCost": 0.10,

        // Load balancer
        "loadBalancerCost": 0.62,

        // Aggregate
        "totalCost": 12.51,
        "totalEfficiency": 0.71,

        // Special allocations
        "sharedCost": 1.2,    // Shared cluster overhead
        "externalCost": 0.0   // External services
      },
      "__idle__": {
        "name": "__idle__",
        "cpuCost": 2.5,
        "ramCost": 1.8,
        "totalCost": 4.3,
        // ... idle capacity costs
      },
      "__unallocated__": {
        "name": "__unallocated__",
        "pvCost": 0.55,
        // ... unallocated PVs, orphaned resources
      }
    }
  ]
}
```

### Key Metrics Explained

#### CPU Metrics
- `cpuCores`: Average CPU cores allocated
- `cpuCoreRequestAverage`: Average requested CPU (from resource requests)
- `cpuCoreUsageAverage`: Average actual CPU usage
- `cpuCoreHours`: CPU core-hours (cores × hours)
- `cpuCost`: Total CPU cost ($)
- `cpuEfficiency`: Usage / Request (1.0 = perfect, <0.5 = over-provisioned)

#### RAM Metrics
- `ramBytes`: Average RAM allocated
- `ramByteRequestAverage`: Average requested RAM
- `ramByteUsageAverage`: Average actual RAM usage
- `ramByteHours`: RAM byte-hours
- `ramCost`: Total RAM cost ($)
- `ramEfficiency`: Usage / Request

#### Special Entities
- `__idle__`: Unused cluster capacity (cost waste)
- `__unallocated__`: Orphaned resources (PVs without pods, etc.)

---

## Implementation Plan

### Step 1: Add Kubecost API Client to Metroculus

**File**: `/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py`

**New Method**: `_query_kubecost_allocation_api()`

```python
def _query_kubecost_allocation_api(self, kubecost_url, window, aggregate='namespace'):
    """
    Query Kubecost allocation API.

    Args:
        kubecost_url: Kubecost API URL (from config)
        window: Time window (7d, 24h, etc.)
        aggregate: Aggregation level (namespace, pod, controller, etc.)

    Returns:
        dict: Allocation data
    """
    url = f"{kubecost_url}/model/allocation"
    params = {
        'window': window,
        'aggregate': aggregate
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get('code') != 200:
            LOG.error(f"Kubecost API returned code {data.get('code')}")
            return None

        return data.get('data', [])

    except Exception as e:
        LOG.error(f"Failed to query Kubecost allocation API: {e}")
        return None
```

---

### Step 2: Update `get_cluster_costs()` Method

**File**: `/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py`

**Enhanced Implementation**:

```python
def get_cluster_costs(self, **kwargs):
    """
    Get comprehensive cluster costs from:
    1. Prometheus metrics (management, LB, network) - Phase 2
    2. Kubecost allocation API (CPU, RAM, PV) - Phase 3

    Returns:
        dict: {
            'summary': { total_cost, cpu_cost, ram_cost, pv_cost, ... },
            'efficiency': { cpu_efficiency, ram_efficiency, total_efficiency },
            'potential_savings': float,
            'breakdown_by_namespace': [...],  # Optional, for UI drill-down
            'savings_recommendations': {...}   # Optional, for optimization
        }
    """
    cloud_account_id = kwargs.get('cloud_account_id')
    start_date = kwargs.get('start_date')
    end_date = kwargs.get('end_date')
    detail_level = kwargs.get('detail_level', 'summary')  # summary | namespace | workload

    thanos_url = self.config_cl.thanos_query_url()
    kubecost_url = self._get_kubecost_url(cloud_account_id)

    # ===== PHASE 2: Infrastructure costs (Prometheus metrics) =====
    cost_metrics = {
        'management_cost': 'kubecost_cluster_management_cost',
        'load_balancer_cost': 'kubecost_load_balancer_cost',
        'network_internet_cost': 'kubecost_network_internet_egress_cost',
        'network_region_cost': 'kubecost_network_region_egress_cost',
        'network_zone_cost': 'kubecost_network_zone_egress_cost',
    }

    cost_breakdown = {}
    for cost_key, metric_name in cost_metrics.items():
        metric_data = self._query_thanos_metric(
            thanos_url, cloud_account_id, metric_name,
            start_date, end_date
        )
        cost_breakdown[cost_key] = sum(p['value'] for p in metric_data) if metric_data else 0.0

    network_cost = (
        cost_breakdown['network_internet_cost'] +
        cost_breakdown['network_region_cost'] +
        cost_breakdown['network_zone_cost']
    )

    # ===== PHASE 3: Allocation costs (Kubecost API) =====
    window = self._calculate_window(start_date, end_date)  # e.g., "7d"

    # Query namespace-level allocation
    allocation_data = self._query_kubecost_allocation_api(
        kubecost_url,
        window=window,
        aggregate='namespace'
    )

    cpu_cost = 0.0
    ram_cost = 0.0
    pv_cost = 0.0
    total_cpu_efficiency = 0.0
    total_ram_efficiency = 0.0
    namespace_count = 0

    namespace_breakdown = []

    if allocation_data:
        for day_data in allocation_data:
            for namespace, metrics in day_data.items():
                # Skip special entities for aggregation
                if namespace.startswith('__'):
                    continue

                cpu_cost += metrics.get('cpuCost', 0.0)
                ram_cost += metrics.get('ramCost', 0.0)
                pv_cost += metrics.get('pvCost', 0.0)

                # Aggregate efficiency (weighted by cost)
                cpu_eff = metrics.get('cpuEfficiency', 0.0)
                ram_eff = metrics.get('ramEfficiency', 0.0)
                ns_cost = metrics.get('totalCost', 0.0)

                if ns_cost > 0:
                    total_cpu_efficiency += cpu_eff * ns_cost
                    total_ram_efficiency += ram_eff * ns_cost
                    namespace_count += 1

                # Store namespace breakdown (for UI drill-down)
                if detail_level in ['namespace', 'workload']:
                    namespace_breakdown.append({
                        'namespace': namespace,
                        'cpu_cost': metrics.get('cpuCost', 0.0),
                        'ram_cost': metrics.get('ramCost', 0.0),
                        'pv_cost': metrics.get('pvCost', 0.0),
                        'network_cost': metrics.get('networkCost', 0.0),
                        'total_cost': metrics.get('totalCost', 0.0),
                        'cpu_efficiency': cpu_eff,
                        'ram_efficiency': ram_eff,
                        'total_efficiency': metrics.get('totalEfficiency', 0.0)
                    })

    # Calculate weighted average efficiency
    total_workload_cost = cpu_cost + ram_cost + pv_cost
    avg_cpu_efficiency = total_cpu_efficiency / total_workload_cost if total_workload_cost > 0 else 0.0
    avg_ram_efficiency = total_ram_efficiency / total_workload_cost if total_workload_cost > 0 else 0.0
    total_efficiency = (avg_cpu_efficiency + avg_ram_efficiency) / 2

    # ===== PHASE 3: Savings recommendations (optional) =====
    potential_savings = 0.0
    savings_recommendations = None

    if detail_level in ['namespace', 'workload']:
        savings_data = self._query_kubecost_savings_api(kubecost_url)
        if savings_data:
            for category, recommendation in savings_data.items():
                if recommendation.get('state') == 'ready':
                    potential_savings += recommendation.get('value', 0.0)
            savings_recommendations = savings_data

    # ===== Aggregate total cost =====
    total_cost = (
        cost_breakdown['management_cost'] +
        cost_breakdown['load_balancer_cost'] +
        network_cost +
        cpu_cost +
        ram_cost +
        pv_cost
    )

    # ===== Build response =====
    summary = {
        'total_cost': total_cost,
        'cpu_cost': cpu_cost,
        'ram_cost': ram_cost,
        'pv_cost': pv_cost,
        'management_cost': cost_breakdown['management_cost'],
        'load_balancer_cost': cost_breakdown['load_balancer_cost'],
        'network_cost': network_cost,
    }

    efficiency = {
        'cpu_efficiency': avg_cpu_efficiency,
        'ram_efficiency': avg_ram_efficiency,
        'total_efficiency': total_efficiency
    }

    response = {
        'cloud_account_id': cloud_account_id,
        'start_date': start_date,
        'end_date': end_date,
        'summary': summary,
        'efficiency': efficiency,
        'potential_savings': potential_savings,
        'breakdown': cost_breakdown,
    }

    # Add namespace breakdown if requested
    if detail_level in ['namespace', 'workload'] and namespace_breakdown:
        response['breakdown_by_namespace'] = namespace_breakdown

    # Add savings recommendations if requested
    if savings_recommendations:
        response['savings_recommendations'] = savings_recommendations

    return response
```

---

### Step 3: Add Kubecost URL Configuration

**File**: `/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py`

```python
def _get_kubecost_url(self, cloud_account_id):
    """
    Get Kubecost API URL for a given cloud account.

    In multi-cluster SaaS setup, each K8s cloud account may have
    a different Kubecost endpoint. This could be:
    1. Stored in cloud_account metadata
    2. Derived from cluster naming convention
    3. Configured in Metroculus config

    For now, assume single Kubecost instance accessible via service:
    """
    # Option 1: From environment variable (single cluster dev/test)
    kubecost_url = os.getenv('KUBECOST_API_URL', 'http://kubecost-cost-analyzer.kubecost.svc.cluster.local:9090')

    # Option 2: From cloud account metadata (production multi-cluster)
    # cloud_account = self._get_cloud_account(cloud_account_id)
    # kubecost_url = cloud_account.get('kubecost_url')

    return kubecost_url
```

**Configuration Options**:

1. **Environment Variable** (Simple, single-cluster):
   ```yaml
   # values.yaml
   metroculus:
     env:
       - name: KUBECOST_API_URL
         value: "http://kubecost-cost-analyzer.kubecost.svc.cluster.local:9090"
   ```

2. **Cloud Account Metadata** (Multi-cluster SaaS):
   ```sql
   -- Add kubecost_url to cloud_accounts table
   ALTER TABLE cloud_accounts ADD COLUMN kubecost_url VARCHAR(255);

   -- Store Kubecost URL per cluster
   UPDATE cloud_accounts
   SET kubecost_url = 'http://kubecost-prod-01.example.com:9090'
   WHERE id = 'prod-k8s-01-id';
   ```

3. **Service Discovery** (Advanced):
   ```python
   # Use Kubernetes service discovery
   kubecost_url = f"http://kubecost-cost-analyzer.{namespace}.svc.cluster.local:9090"
   ```

**Recommendation**: Start with **Option 1** (env variable) for Phase 3. Migrate to **Option 2** for production multi-cluster.

---

### Step 4: Add Helper Methods

**File**: `/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py`

```python
def _calculate_window(self, start_date, end_date):
    """
    Convert start/end timestamps to Kubecost window format.

    Args:
        start_date: Unix timestamp
        end_date: Unix timestamp

    Returns:
        str: Kubecost window (e.g., "7d", "24h", "30d")
    """
    duration_seconds = end_date - start_date
    duration_days = duration_seconds / 86400

    if duration_days <= 1:
        return "24h"
    elif duration_days <= 7:
        return "7d"
    elif duration_days <= 30:
        return "30d"
    else:
        return f"{int(duration_days)}d"


def _query_kubecost_savings_api(self, kubecost_url):
    """
    Query Kubecost savings recommendations API.

    Args:
        kubecost_url: Kubecost API URL

    Returns:
        dict: Savings recommendations by category
    """
    url = f"{kubecost_url}/model/savings"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Kubecost savings API returns per-cluster recommendations
        # Extract first cluster (or aggregate if multiple)
        if isinstance(data, dict):
            first_cluster = next(iter(data.values())) if data else {}
            return first_cluster

        return None

    except Exception as e:
        LOG.error(f"Failed to query Kubecost savings API: {e}")
        return None
```

---

### Step 5: Update REST API (No Changes Required!)

**File**: `/cloud-tuner/rest_api/rest_api_server/controllers/expense.py`

**Good News**: REST API `_get_k8s_costs()` already reads `summary` object, so **no changes needed**!

The Phase 2 implementation already handles the structure:
```python
summary = cost_data.get('summary', {})
if summary:
    cluster_cost = summary.get('total_cost', 0)  # ✅ Works with Phase 3
    breakdown = summary                           # ✅ Includes all cost fields
```

REST API will automatically include:
- `cpu_cost`, `ram_cost`, `pv_cost` (Phase 3 additions)
- `efficiency` object (Phase 3 addition)
- `potential_savings` (Phase 3 addition)

---

## Testing Plan

### Test 1: Verify Kubecost API Access
```bash
kubectl port-forward -n kubecost svc/kubecost-cost-analyzer 39090:9090

# Test allocation API
curl "http://localhost:39090/model/allocation?window=7d&aggregate=namespace" | jq '.data[0] | keys'

# Expected: namespace names as keys
```

### Test 2: Verify Metroculus Integration
```bash
# Deploy updated Metroculus image
docker build -t invincibledocker24/metroculus_api:v1.4.0-phase3 .
docker push invincibledocker24/metroculus_api:v1.4.0-phase3

# Update Helm
helm upgrade cloud-tuner-dev ./cloud-tuner-dev -n default

# Test endpoint
CLUSTER_SECRET=$(kubectl get secret cluster-secret -n default -o jsonpath='{.data.cluster_secret}' | base64 -d)

curl -H "Secret: $CLUSTER_SECRET" \
  "http://localhost:39069/metroculus/v2/kubecost_cluster_costs?cloud_account_id=5635f99d-4dc6-4e31-891f-4e8990925c83&start_date=$(date -u -d '7 days ago' +%s)&end_date=$(date +%s)" \
  | jq '.summary'

# Expected:
# {
#   "total_cost": 105.50,  # Should be ~$100-110/week
#   "cpu_cost": 52.30,     # Should be ~$45-55/week
#   "ram_cost": 31.20,     # Should be ~$25-35/week
#   "pv_cost": 9.50,       # Should be ~$5-15/week
#   "management_cost": 10.40,
#   "load_balancer_cost": 2.49,
#   "network_cost": 16.95
# }
```

### Test 3: Verify REST API Integration
```bash
# Get auth token
kubectl exec -n default mariadb-0 -- mysql -u root -proot restapi -sN \
  -e "SELECT token FROM auth LIMIT 1;"

# Test clean_expenses endpoint
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8999/restapi/v2/clean_expenses?organization_id=<org_id>&start_date=<ts>&end_date=<ts>" \
  | jq '.k8s_costs.k8s_cost_breakdown[0].breakdown'

# Expected:
# {
#   "total_cost": 105.50,
#   "cpu_cost": 52.30,      # NEW in Phase 3
#   "ram_cost": 31.20,      # NEW in Phase 3
#   "pv_cost": 9.50,        # NEW in Phase 3
#   "management_cost": 10.40,
#   "load_balancer_cost": 2.49,
#   "network_cost": 16.95
# }
```

### Test 4: Verify Efficiency Metrics
```bash
curl -H "Secret: $CLUSTER_SECRET" \
  "http://localhost:39069/metroculus/v2/kubecost_cluster_costs?cloud_account_id=...&detail_level=namespace" \
  | jq '.efficiency'

# Expected:
# {
#   "cpu_efficiency": 0.45,  # 45%
#   "ram_efficiency": 0.38,  # 38%
#   "total_efficiency": 0.41 # 41%
# }
```

---

## Expected Results After Phase 3

### Cost Comparison
```
Phase 2 (Infrastructure Only):    $29.84/week  ████░░░░░░░░░░░░░░░░  28%
Phase 3 (Full Allocation):       $105.50/week  ████████████████████ 100%
─────────────────────────────────────────────────────────────────────
Improvement:                       $75.66/week  (254% increase)
```

### Cost Breakdown
```
CPU allocation:         $52.30/week  ██████████████░░░░░░  49%
RAM allocation:         $31.20/week  ████████░░░░░░░░░░░░  30%
Management overhead:    $10.40/week  ███░░░░░░░░░░░░░░░░░  10%
PV storage:             $9.50/week   ██░░░░░░░░░░░░░░░░░░   9%
Network egress:         $16.95/week  ████░░░░░░░░░░░░░░░░  16%
Load balancer:          $2.49/week   █░░░░░░░░░░░░░░░░░░░   2%
─────────────────────────────────────────────────────────────
Total:                 $105.50/week  ████████████████████ 100%
```

---

## Next Steps After Implementation

### 1. Validate Cost Accuracy
- Compare Kubecost UI costs vs Metroculus API costs
- Ensure totals match within 5% margin

### 2. Add Namespace/Workload Drill-Down (Phase 4)
- Implement `detail_level=namespace` in REST API
- Implement `detail_level=workload` for pod-level costs

### 3. Add Savings Recommendations (Phase 4)
- Expose savings API data to REST API
- Build optimization center UI

### 4. Performance Optimization
- Cache Kubecost API responses (15-minute TTL)
- Implement pagination for large clusters (100+ namespaces)

### 5. Multi-Cluster Support
- Add cloud_account metadata for Kubecost URLs
- Implement parallel querying for multiple clusters

---

## Summary

Phase 3 implementation requires:

1. ✅ **Kubecost API client** in Metroculus
2. ✅ **Enhanced `get_cluster_costs()`** to aggregate allocation costs
3. ✅ **Kubecost URL configuration** (env variable or metadata)
4. ✅ **Helper methods** for window calculation and savings API
5. ✅ **No REST API changes** (already compatible!)

**Estimated Effort**: 3-5 days development + 2 days testing

**Expected Outcome**: Accurate K8s cost tracking (~$105/week vs ~$30/week), enabling Phase 4 UI and optimization features.
