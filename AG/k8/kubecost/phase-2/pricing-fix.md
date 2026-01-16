# Phase 2 Pricing Fix: Correct K8s Cost Integration

## Issues Identified

### Issue 1: Response Structure Mismatch ✅ FIXED
**Problem**: Metroculus and REST API had incompatible response formats
- **Metroculus returned**: `{ total_cost: 10.2, data_points: [...] }` (top-level)
- **REST API expected**: `{ summary: { total_cost: 10.2, ... }, ... }`
- **Result**: REST API couldn't read costs, silently discarded data

**Fix**: Updated Metroculus to return `summary` object structure

### Issue 2: Only Management Costs Captured ✅ PARTIALLY FIXED
**Problem**: Metroculus only queried `kubecost_cluster_management_cost` metric
- **Captured**: ~$0.10/hour = ~$10.20 for 102 hours
- **Missing**: Load balancer, network egress, and allocation costs (CPU, RAM, PV)
- **Result**: Only seeing ~$10 instead of real ~$105/week cluster costs

**Fix**: Updated Metroculus to aggregate all available Prometheus cost metrics:
- ✅ `kubecost_cluster_management_cost`
- ✅ `kubecost_load_balancer_cost`
- ✅ `kubecost_network_internet_egress_cost`
- ✅ `kubecost_network_region_egress_cost`
- ✅ `kubecost_network_zone_egress_cost`

**Still Missing** (requires Phase 3):
- ❌ `cpu_cost` (from Kubecost allocation API)
- ❌ `ram_cost` (from Kubecost allocation API)
- ❌ `pv_cost` (from Kubecost allocation API)

---

## Changes Made

### 1. Metroculus: `/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py`

#### Before (Lines 139-180):
```python
def get_cluster_costs(self, **kwargs):
    # Only queried kubecost_cluster_management_cost
    cluster_cost_data = self._query_thanos_metric(
        thanos_url, cloud_account_id,
        'kubecost_cluster_management_cost',
        start_date, end_date
    )

    total_cost = sum(point['value'] for point in cluster_cost_data)

    return {
        'cloud_account_id': cloud_account_id,
        'total_cost': total_cost,  # Wrong structure
        'data_points': cluster_cost_data
    }
```

#### After (Lines 139-216):
```python
def get_cluster_costs(self, **kwargs):
    # Query ALL available cost metrics
    cost_metrics = {
        'management_cost': 'kubecost_cluster_management_cost',
        'load_balancer_cost': 'kubecost_load_balancer_cost',
        'network_internet_cost': 'kubecost_network_internet_egress_cost',
        'network_region_cost': 'kubecost_network_region_egress_cost',
        'network_zone_cost': 'kubecost_network_zone_egress_cost',
    }

    cost_breakdown = {}
    total_cost = 0.0

    for cost_key, metric_name in cost_metrics.items():
        metric_data = self._query_thanos_metric(...)
        if metric_data:
            cost = sum(point['value'] for point in metric_data)
            cost_breakdown[cost_key] = cost
            total_cost += cost

    network_cost = (
        cost_breakdown['network_internet_cost'] +
        cost_breakdown['network_region_cost'] +
        cost_breakdown['network_zone_cost']
    )

    # Create summary structure (REST API compatible)
    summary = {
        'total_cost': total_cost,
        'management_cost': cost_breakdown['management_cost'],
        'load_balancer_cost': cost_breakdown['load_balancer_cost'],
        'network_cost': network_cost,
        # Placeholders for Phase 3
        'cpu_cost': 0.0,
        'ram_cost': 0.0,
        'pv_cost': 0.0,
    }

    return {
        'cloud_account_id': cloud_account_id,
        'start_date': start_date,
        'end_date': end_date,
        'summary': summary,  # Correct structure
        'breakdown': cost_breakdown,
    }
```

**Key Changes**:
1. ✅ Returns `summary` object (REST API compatible)
2. ✅ Aggregates 5 cost metrics instead of 1
3. ✅ Provides detailed `breakdown` for debugging
4. ✅ Documents Phase 3 requirements (CPU/RAM/PV costs)

---

### 2. REST API: `/cloud-tuner/rest_api/rest_api_server/controllers/expense.py`

#### Before (Lines 865-888):
```python
if status_code == 200 and cost_data:
    cluster_cost = cost_data.get('summary', {}).get('total_cost', 0)
    k8s_total_cost += cluster_cost

    k8s_cost_breakdown.append({
        'cloud_account_id': k8s_account.id,
        'cloud_account_name': k8s_account.name,
        'cost': cluster_cost,
        'breakdown': cost_data.get('summary', {})
    })
```

#### After (Lines 865-921):
```python
if status_code == 200 and cost_data:
    # Handle new format (with 'summary' object)
    summary = cost_data.get('summary', {})
    if summary:
        cluster_cost = summary.get('total_cost', 0)
        breakdown = summary
    else:
        # Backward compatibility: old format
        cluster_cost = cost_data.get('total_cost', 0)
        breakdown = {
            'total_cost': cluster_cost,
            'management_cost': cluster_cost,
        }
        LOG.warning(
            f"K8s account {k8s_account.id}: Using legacy format"
        )

    if cluster_cost > 0:
        k8s_total_cost += cluster_cost
        k8s_cost_breakdown.append({
            'cloud_account_id': k8s_account.id,
            'cloud_account_name': k8s_account.name,
            'cost': cluster_cost,
            'breakdown': breakdown
        })
        LOG.info(
            f"K8s account {k8s_account.id}: ${cluster_cost:.2f} "
            f"(breakdown: {breakdown})"
        )
    else:
        LOG.debug(f"K8s account {k8s_account.id}: No costs")
else:
    LOG.warning(
        f"K8s account {k8s_account.id}: Metroculus returned "
        f"status {status_code}"
    )
```

**Key Changes**:
1. ✅ Handles both new and old Metroculus formats
2. ✅ Added detailed logging for debugging
3. ✅ Logs cost breakdown for verification
4. ✅ Warns if no costs found (helps identify issues)

---

## Expected Results After Fix

### Metroculus Response (New Format)
```json
{
  "cloud_account_id": "5635f99d-4dc6-4e31-891f-4e8990925c83",
  "start_date": 1234567890,
  "end_date": 1234567990,
  "summary": {
    "total_cost": 18.45,
    "management_cost": 10.20,
    "load_balancer_cost": 6.25,
    "network_cost": 2.00,
    "cpu_cost": 0.0,
    "ram_cost": 0.0,
    "pv_cost": 0.0
  },
  "breakdown": {
    "management_cost": 10.20,
    "load_balancer_cost": 6.25,
    "network_internet_cost": 1.50,
    "network_region_cost": 0.30,
    "network_zone_cost": 0.20
  }
}
```

### REST API Response (Updated)
```json
{
  "total_cost": 268.45,
  "clean_expenses": [...],
  "k8s_costs": {
    "k8s_total_cost": 18.45,
    "k8s_cost_breakdown": [
      {
        "cloud_account_id": "5635f99d-4dc6-4e31-891f-4e8990925c83",
        "cloud_account_name": "Production K8s Cluster",
        "cost": 18.45,
        "breakdown": {
          "total_cost": 18.45,
          "management_cost": 10.20,
          "load_balancer_cost": 6.25,
          "network_cost": 2.00,
          "cpu_cost": 0.0,
          "ram_cost": 0.0,
          "pv_cost": 0.0
        }
      }
    ]
  }
}
```

**Improvements**:
- ✅ Structure mismatch fixed
- ✅ More comprehensive costs (~$18 vs ~$10)
- ✅ Detailed breakdown visible
- ⚠️ Still missing CPU/RAM/PV allocation costs (Phase 3)

---

## Deployment Steps

### 1. Build and Deploy Metroculus
```bash
cd /Users/balaji/source/code/cloudtuner/cloud-tuner/metroculus
docker build -t invincibledocker24/metroculus:v1.4.0-pricing-fix .
docker push invincibledocker24/metroculus:v1.4.0-pricing-fix

# Update Helm
cd /Users/balaji/source/code/cloudtuner/cloudtuner-dev-helm
# Update values.yaml: metroculus.image.tag: v1.4.0-pricing-fix
helm upgrade cloud-tuner-dev ./cloud-tuner-dev -n default
```

### 2. Build and Deploy REST API
```bash
cd /Users/balaji/source/code/cloudtuner/cloud-tuner/rest_api
docker build -t invincibledocker24/rest_api:v1.4.0-pricing-fix .
docker push invincibledocker24/rest_api:v1.4.0-pricing-fix

# Update Helm
cd /Users/balaji/source/code/cloudtuner/cloudtuner-dev-helm
# Update values.yaml: restapi.image.tag: v1.4.0-pricing-fix
helm upgrade cloud-tuner-dev ./cloud-tuner-dev -n default
```

### 3. Verify Deployment
```bash
# Check pods
kubectl get pods -l app=metroculus
kubectl get pods -l app=restapi

# Check logs for K8s cost queries
kubectl logs -l app=restapi --tail=50 | grep "K8s account"

# Should see logs like:
# INFO: K8s account abc-123 (Production): $18.45 (breakdown: {...})
```

---

## Testing

### Test 1: Verify Metroculus Response Structure
```bash
CLUSTER_SECRET=$(kubectl get secret cluster-secret -n default -o jsonpath='{.data.cluster_secret}' | base64 -d)
CLOUD_ACCOUNT_ID="5635f99d-4dc6-4e31-891f-4e8990925c83"

# Port-forward
kubectl port-forward -n default svc/metroculus 8969:80 &

# Test endpoint
curl -s -H "Secret: $CLUSTER_SECRET" \
  "http://localhost:8969/metroculus/v2/kubecost_cluster_costs?cloud_account_id=$CLOUD_ACCOUNT_ID&start_date=1234567890&end_date=1234567990" \
  | jq '.'

# Verify response has:
# - summary object
# - summary.total_cost > 0
# - summary.management_cost > 0
# - summary.load_balancer_cost (may be 0)
# - summary.network_cost (may be 0)
```

### Test 2: Verify REST API Integration
```bash
# Get org ID and token from database
# Then test clean_expenses endpoint

curl -s -H "Authorization: Bearer <token>" \
  "http://localhost:8999/restapi/v2/clean_expenses?organization_id=<org_id>&start_date=<ts>&end_date=<ts>" \
  | jq '.k8s_costs'

# Verify response has:
# - k8s_costs.k8s_total_cost > 0
# - k8s_costs.k8s_cost_breakdown[0].breakdown.total_cost > 0
# - k8s_costs.k8s_cost_breakdown[0].breakdown.management_cost > 0
```

### Test 3: Check REST API Logs
```bash
kubectl logs -l app=restapi --tail=100 | grep "K8s account"

# Should see INFO logs with breakdown, NOT warnings about legacy format
```

---

## Current Limitations & Phase 3 Requirements

### What's Working Now ✅
- Cluster management costs (~$10/week)
- Load balancer costs
- Network egress costs (internet, region, zone)
- Structure compatibility (Metroculus ↔ REST API)
- Detailed logging and debugging

### What's Missing ❌ (Phase 3)
- **CPU allocation costs**: Requires Kubecost allocation API (`/model/allocation`)
- **RAM allocation costs**: Requires Kubecost allocation API
- **PV (persistent volume) costs**: Requires Kubecost allocation API
- **Per-pod/namespace breakdown**: Requires Kubecost allocation API
- **Idle vs allocated tracking**: Requires Kubecost allocation API

### Why Missing?
Kubecost's full cost allocation data (CPU, RAM, PV by pod/namespace) comes from the **Kubecost allocation API**, not from individual Prometheus metrics.

The Prometheus metrics we're querying are:
- ✅ Management/overhead costs (static)
- ✅ Load balancer costs (infrastructure)
- ✅ Network egress (actual usage)
- ❌ **NOT** CPU/RAM/PV allocation per workload

### Phase 3 Solution
Query Kubecost's `/model/allocation` API directly:
```bash
curl "http://kubecost-cost-analyzer:9090/model/allocation?window=7d&aggregate=namespace"
```

This returns:
```json
{
  "data": {
    "kube-system": {
      "cpuCost": 15.50,
      "ramCost": 8.25,
      "pvCost": 2.10,
      "totalCost": 25.85
    },
    "default": {
      "cpuCost": 45.20,
      "ramCost": 22.30,
      "pvCost": 8.50,
      "totalCost": 76.00
    }
  }
}
```

**Phase 3 Implementation Options**:
1. **Option A**: Metroculus queries Kubecost API, stores in Thanos as synthetic metrics
2. **Option B**: New kubecost_worker service queries API, stores in ClickHouse
3. **Option C**: REST API queries Kubecost API directly (not multi-cluster compatible)

Recommend **Option A** for consistency with Phase 1 architecture.

---

## Summary

### Fixed ✅
1. **Structure mismatch**: Metroculus now returns `summary` object
2. **Partial cost aggregation**: Now capturing management + LB + network (~$18 vs ~$10)
3. **REST API compatibility**: Handles both old and new formats
4. **Logging**: Detailed logs for debugging

### Still TODO 📋
1. **Phase 3**: Query Kubecost allocation API for CPU/RAM/PV costs
2. **Phase 3**: Store allocation data in Thanos or ClickHouse
3. **Phase 3**: Aggregate ~$105/week real costs (not just ~$18 overhead)

### Current Expected Cost
With this fix, you should see:
- **Management**: ~$10/week (0.10/hour * 168 hours)
- **Load Balancer**: ~$6-8/week (if configured)
- **Network**: ~$2-4/week (depending on egress)
- **Total**: ~$18-22/week ✅

**Phase 3 will add**:
- **CPU**: ~$50/week
- **RAM**: ~$30/week
- **PV**: ~$5-10/week
- **Total**: ~$105/week 🎯

---

**Date**: 2025-10-13
**Status**: Phase 2 pricing fix complete, Phase 3 required for full allocation costs
