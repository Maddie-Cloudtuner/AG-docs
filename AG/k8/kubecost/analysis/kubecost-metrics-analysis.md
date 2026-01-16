# Kubecost Metrics Analysis for SaaS Multi-Cluster Cost Tracking

**Date**: 2025-10-14
**Status**: Phase 1 - Infrastructure Costs Working, Allocation Costs Missing
**Cloud Account**: d603f6e0-aff4-4e89-962d-c56f16b69404 (balaji/balaji@2025)

---

## Executive Summary

CloudTuner's Kubernetes cost tracking requires comprehensive cost data from Kubecost, but **allocation costs (CPU, RAM, PV) are currently $0.00** because Kubecost stores allocation data in its internal database, not as Prometheus metrics. Only infrastructure costs ($0.57/hour) are currently flowing through Prometheus remote_write to Thanos.

**Critical Gap**: Kubecost allocation data (CPU/RAM/PV costs per pod/namespace) is NOT exposed as scrapable Prometheus metrics.

---

## 1. Current Architecture

### Data Flow
```
Kubecost → Prometheus (scrape) → remote_write → CloudTuner Thanos → Metroculus API → Resource Discovery → MongoDB/ClickHouse → Frontend
```

### Multi-Cluster SaaS Constraints
- ✅ Prometheus remote_write works across networks (HTTPS to CloudTuner)
- ✅ Metrics flow with tenant isolation (cloud_account_id header)
- ❌ Kubecost API is cluster-local only (http://kubecost-dev.kubecost-dev.svc:9090)
- ❌ Cannot query Kubecost API from CloudTuner SaaS (different clusters)

**Implication**: Only metrics sent via Prometheus remote_write are available to CloudTuner.

---

## 2. Metrics Currently Available in Thanos

### 2.1 Infrastructure Costs (✅ WORKING)

| Metric | Source | Value (Last Hour) | Description |
|--------|--------|-------------------|-------------|
| `kubecost_cluster_management_cost` | Kubecost scrape | $0.20 | Cluster overhead (control plane) |
| `kubecost_load_balancer_cost` | Kubecost scrape | $0.05 | Load balancer costs |
| `kubecost_network_internet_egress_cost` | Kubecost scrape | $0.29 | Internet egress traffic |
| `kubecost_network_region_egress_cost` | Kubecost scrape | $0.02 | Cross-region traffic |
| `kubecost_network_zone_egress_cost` | Kubecost scrape | $0.02 | Cross-AZ traffic |
| **TOTAL INFRASTRUCTURE** | | **$0.57/hour** | ~$410/month |

**Prometheus Config**: Lines 139-149 in kubecost-prometheus-config.yaml
```yaml
- job_name: kubecost
  honor_labels: true
  scrape_interval: 1m
  metrics_path: /metrics
  scheme: http
  dns_sd_configs:
  - names:
    - kubecost-dev
    type: 'A'
    port: 9003
```

**Remote Write Filter**: Lines 22-26
```yaml
write_relabel_configs:
- action: keep
  regex: (kubecost_.*|container_.*|kube_.*|node_.*|up)
  source_labels:
  - __name__
```

### 2.2 Recording Rules (✅ SCRAPED, ❓ NOT COST DATA)

| Recording Rule | Type | Purpose | Available? |
|----------------|------|---------|------------|
| `kubecost_container_cpu_usage_irate` | Rate | CPU usage per container | ✅ |
| `kubecost_container_memory_working_set_bytes` | Gauge | Memory usage per container | ✅ |
| `kubecost_cluster_memory_working_set_bytes` | Gauge | Total cluster memory | ✅ |
| `kubecost_savings_cpu_allocation` | Gauge | CPU allocation (cores) | ✅ |
| `kubecost_savings_memory_allocation_bytes` | Gauge | Memory allocation (bytes) | ✅ |

**Problem**: These show **resource allocations**, NOT **costs**. Missing pricing data to convert to dollars.

**Source**: Recording rules in kubecost-prometheus-config.yaml lines 185-222

### 2.3 Metadata Metrics (✅ WORKING)

| Metric | Purpose | Example Labels |
|--------|---------|----------------|
| `kube_pod_info` | Pod metadata | pod, namespace, node, uid |
| `kube_node_info` | Node metadata | node, instance, provider_id |
| `kube_namespace_created` | Namespace list | namespace |
| `kubecost_cluster_info` | Cluster metadata | cluster_id, cluster_name |

---

## 3. Metrics MISSING from Thanos

### 3.1 Allocation Cost Metrics (❌ NOT EXPOSED BY KUBECOST)

These are **NOT available as Prometheus metrics**. Kubecost stores this data in its internal database and exposes it via REST API only.

| Missing Metric | What It Should Provide | Current Status |
|----------------|------------------------|----------------|
| `kubecost_pod_cpu_cost` | CPU cost per pod ($) | ❌ Not exposed |
| `kubecost_pod_memory_cost` | RAM cost per pod ($) | ❌ Not exposed |
| `kubecost_pod_pv_cost` | PV cost per pod ($) | ❌ Not exposed |
| `kubecost_namespace_cpu_cost` | CPU cost per namespace ($) | ❌ Not exposed |
| `kubecost_namespace_memory_cost` | RAM cost per namespace ($) | ❌ Not exposed |
| `kubecost_namespace_pv_cost` | PV cost per namespace ($) | ❌ Not exposed |

**Why Missing**: Kubecost computes these values by:
1. Querying allocation data from its internal DB (OpenCost ETL backend)
2. Applying pricing data (node costs, PV costs)
3. Returning results via `/model/allocation` API

These computed cost values are **NOT exported as scrapable Prometheus metrics**.

### 3.2 Pricing Metrics (❓ MAY BE AVAILABLE, NOT SCRAPED)

| Metric | Purpose | Scraped? | In remote_write filter? |
|--------|---------|----------|------------------------|
| `node_cpu_hourly_cost` | Cost per CPU core/hour | ❓ | ✅ Yes (node_.*) |
| `node_ram_hourly_cost` | Cost per GB RAM/hour | ❓ | ✅ Yes (node_.*) |
| `node_gpu_hourly_cost` | Cost per GPU/hour | ❓ | ✅ Yes (node_.*) |
| `pv_hourly_cost` | Cost per GB PV/hour | ❓ | ❌ No (pv_.*) |
| `node_total_hourly_cost` | Total node cost/hour | ❓ | ✅ Yes (node_.*) |

**Hypothesis**: These pricing metrics may be exposed by Kubecost's node-exporter or cost-model, but:
1. May not be in the scrape targets
2. `pv_hourly_cost` is filtered out by remote_write regex

### 3.3 Allocation Metrics (⚠️ PARTIALLY AVAILABLE)

| Metric | Purpose | Scraped? | In remote_write filter? |
|--------|---------|----------|------------------------|
| `container_cpu_allocation` | CPU requests per container | ✅ | ✅ Yes (container_.*) |
| `container_memory_allocation_bytes` | RAM requests per container | ✅ | ✅ Yes (container_.*) |
| `pod_pvc_allocation` | PV allocation per pod | ❓ | ❌ No (pod_.*) |
| `container_gpu_allocation` | GPU requests per container | ❓ | ✅ Yes (container_.*) |

**Problem**: Even if we have allocation + pricing, we'd need to compute costs ourselves. Kubecost already does this, but doesn't expose the results as metrics.

---

## 4. Kubecost API Data (❌ NOT ACCESSIBLE IN SAAS)

### 4.1 Allocation API

**Endpoint**: `http://kubecost-dev.kubecost-dev.svc:9090/model/allocation`

**What It Provides**:
```json
{
  "data": [
    {
      "default": {
        "name": "default",
        "cpuCost": 54.76,           // ✅ WHAT WE NEED
        "ramCost": 44.65,            // ✅ WHAT WE NEED
        "pvCost": 13.15,             // ✅ WHAT WE NEED
        "gpuCost": 0.0,
        "networkCost": 0.0,
        "loadBalancerCost": 0.0,
        "totalCost": 112.56,         // ✅ WHAT WE NEED
        "cpuEfficiency": 2.57,       // ✅ WHAT WE NEED
        "ramEfficiency": 2.23,       // ✅ WHAT WE NEED
        "totalEfficiency": 2.40      // ✅ WHAT WE NEED
      }
    }
  ]
}
```

**Why It's Perfect**:
- ✅ Pre-computed costs (no calculation needed)
- ✅ Includes efficiency metrics
- ✅ Supports aggregation (namespace, pod, controller, label)
- ✅ Time-windowed queries (7d, 30d, custom)

**Why It's Unusable in SaaS**:
- ❌ Cluster-local endpoint (http://kubecost-dev.kubecost-dev.svc:9090)
- ❌ No cross-cluster access
- ❌ Customer clusters cannot be directly queried from CloudTuner SaaS

### 4.2 Savings API

**Endpoint**: `http://kubecost-dev.kubecost-dev.svc:9090/model/savings`

**What It Provides**:
- Rightsizing recommendations
- Abandoned workloads
- Underutilized nodes
- Potential monthly savings ($)

**Status**: Same accessibility problem as allocation API

---

## 5. What We Tried (Current Implementation)

### Approach: Compute Allocation Costs from Thanos Metrics

**File**: `/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py`

**Method**: `_query_allocation_costs_from_thanos()` (lines 140-213)

**Logic**:
1. Query `container_cpu_allocation` → get total CPU cores
2. Query `node_cpu_hourly_cost` → get cost per core
3. Calculate: `cpu_cost = cpu_allocation * cpu_price * duration_hours`
4. Repeat for RAM and PV

**Result**: ❌ **All costs = $0.00**

**Why It Failed**:
1. ❓ `node_cpu_hourly_cost` may not be scraped
2. ❓ `node_ram_hourly_cost` may not be scraped
3. ❌ `pv_hourly_cost` definitely NOT scraped (filtered out by regex)
4. ❌ `pod_pvc_allocation` NOT scraped (filtered out by regex)
5. ⚠️ Even if available, this approach is a workaround - Kubecost already has accurate cost data

---

## 6. Gap Analysis

### What We Have ✅
1. Infrastructure costs: management, LB, network ($0.57/hour working)
2. Resource allocation metrics: CPU/RAM requests per container
3. Resource usage metrics: actual CPU/RAM usage
4. Metadata: pods, nodes, namespaces, cluster info

### What We're Missing ❌
1. **CPU allocation costs per pod/namespace** (in $)
2. **RAM allocation costs per pod/namespace** (in $)
3. **PV allocation costs per pod/namespace** (in $)
4. **Efficiency metrics** (usage vs allocation %)
5. **Savings recommendations** (rightsizing opportunities)

### Root Cause
**Kubecost does NOT expose allocation cost data as Prometheus metrics.**

Kubecost stores allocation costs in:
- Internal database (OpenCost backend)
- Exposed via REST API (`/model/allocation`)
- **NOT** exposed as Prometheus metrics for scraping

---

## 7. Proposed Solutions

### Solution 1: Infrastructure Costs Only (Phase 1 - DO THIS NOW)

**Status**: ✅ Already Working

**Cost Data Available**:
- Management cost: $0.20/hour
- Load balancer cost: $0.05/hour
- Network costs: $0.33/hour
- **Total**: $0.57/hour (~$410/month)

**What This Gives Us**:
- ✅ Cluster-level cost tracking
- ✅ Network egress visibility (important for cost control)
- ✅ Infrastructure overhead tracking
- ✅ Works in multi-cluster SaaS architecture
- ✅ No additional Kubecost configuration needed

**What It Doesn't Give**:
- ❌ CPU/RAM/PV allocation costs
- ❌ Per-namespace cost breakdown
- ❌ Efficiency metrics
- ❌ Rightsizing recommendations

**Recommendation**:
- **Proceed with Phase 1 using infrastructure costs**
- Get cluster discovery working end-to-end
- Show cluster-level costs on frontend
- Document limitation: "Allocation costs require Kubecost metrics export"

---

### Solution 2: Add Missing Metrics to Prometheus Scrape (Investigate)

**Step 1: Check if pricing metrics are available**

Test if Kubecost exposes these metrics at its `/metrics` endpoint:

```bash
kubectl port-forward -n kubecost-dev svc/kubecost-cost-analyzer 9090:9090
curl -s http://localhost:9090/metrics | grep -E "node_cpu_hourly_cost|node_ram_hourly_cost|pv_hourly_cost"
```

**Step 2: Update Prometheus remote_write filter**

If metrics exist, update regex to include PV metrics:

```yaml
write_relabel_configs:
- action: keep
  regex: (kubecost_.*|container_.*|kube_.*|node_.*|pod_pvc_.*|pv_.*|up)  # Added pod_pvc_.* and pv_.*
  source_labels:
  - __name__
```

**Step 3: Test cost calculation**

If pricing metrics flow to Thanos, retry `_query_allocation_costs_from_thanos()`.

**Risk**: Even if this works, it's a workaround. We're duplicating Kubecost's cost computation logic.

---

### Solution 3: Kubecost Metrics Export Enhancement (Long-term)

**Goal**: Get Kubecost to export allocation costs as Prometheus metrics.

**Approach**:
1. Check Kubecost documentation for metric export options
2. Look for configuration flags:
   - `exportMetrics: true`
   - Metrics exporter for allocation API
3. File feature request with Kubecost/OpenCost project

**Ideal Metrics to Export**:
```
kubecost_pod_cpu_cost{pod="nginx-123", namespace="default"} 0.05
kubecost_pod_memory_cost{pod="nginx-123", namespace="default"} 0.03
kubecost_pod_pv_cost{pod="nginx-123", namespace="default"} 0.01
kubecost_namespace_total_cost{namespace="default"} 112.56
kubecost_namespace_cpu_efficiency{namespace="default"} 2.57
```

**Benefits**:
- ✅ Accurate costs (Kubecost's calculation)
- ✅ Works in multi-cluster SaaS
- ✅ No API access needed
- ✅ Real-time metric updates

---

### Solution 4: Hybrid Mode (Dev Only)

**For Single-Cluster Development**:
- Keep Metroculus Thanos-only for production SaaS
- Add optional `KUBECOST_API_URL` env var for dev/testing
- Query Kubecost API when in same cluster

**Code Change**:
```python
# In _query_allocation_costs_from_thanos()
kubecost_url = os.getenv('KUBECOST_API_URL')
if kubecost_url:
    # Direct API access (dev mode)
    return self._query_kubecost_allocation_api(kubecost_url, ...)
else:
    # Thanos metrics only (production SaaS)
    return self._compute_from_thanos_metrics(...)
```

**Use Case**: Development and testing only, NOT for production SaaS.

---

## 8. Recommended Action Plan

### Phase 1: Infrastructure Costs (DO NOW)
1. ✅ Keep current implementation (infrastructure costs working)
2. ✅ Deploy resource-discovery with cluster discovery
3. ✅ Test end-to-end: discovery → MongoDB → ClickHouse → frontend
4. ✅ Verify $0.57/hour infrastructure costs appear on dashboard
5. ✅ Document known limitation in UI

**Timeline**: Immediate (code ready)

---

### Phase 2: Investigate Kubecost Metric Export (RESEARCH)
1. 🔍 Check Kubecost `/metrics` endpoint for pricing metrics
2. 🔍 Review Kubecost documentation for allocation cost export
3. 🔍 Test if updating remote_write filter helps
4. 📝 Document findings
5. 📝 File feature request with Kubecost if needed

**Timeline**: 1-2 days research

---

### Phase 3: Full Allocation Costs (FUTURE)
Depends on Phase 2 findings:
- **If metrics available**: Update Metroculus to use them
- **If not available**: Consider alternative approaches
  - Kubecost metrics exporter sidecar?
  - Periodic API scraper (if cluster access possible)?
  - Alternative cost calculation?

**Timeline**: TBD based on Phase 2 results

---

## 9. Testing Checklist

### Current State Verification
- [x] Infrastructure costs flowing to Thanos ($0.57/hour)
- [x] Metroculus API returning cost data
- [ ] Allocation costs in Metroculus (currently $0.00)
- [ ] Cluster resource discovery working
- [ ] Costs appearing in MongoDB
- [ ] Costs appearing in ClickHouse
- [ ] Costs appearing on frontend dashboard

### Metrics Investigation
- [ ] Port-forward to Kubecost and check `/metrics` endpoint
- [ ] Search for `node_cpu_hourly_cost` in Kubecost metrics
- [ ] Search for `node_ram_hourly_cost` in Kubecost metrics
- [ ] Search for `pv_hourly_cost` in Kubecost metrics
- [ ] Check if `pod_pvc_allocation` is scraped
- [ ] Verify Thanos has these metrics

### Configuration Testing
- [ ] Update remote_write regex to include `pv_.*` and `pod_pvc_.*`
- [ ] Restart Prometheus
- [ ] Verify new metrics flow to Thanos
- [ ] Test Metroculus allocation cost calculation
- [ ] Compare with Kubecost allocation API results

---

## 10. Open Questions

1. **Does Kubecost expose pricing metrics?**
   - Test: `kubectl port-forward` + `curl /metrics | grep hourly_cost`

2. **Can Kubecost export allocation costs as metrics?**
   - Check: Kubecost docs, OpenCost exporter options

3. **What's the correct label for tenant isolation in allocation metrics?**
   - Current: Using `cloud_account_id` for allocation queries
   - Infrastructure: Using `tenant_id` for kubecost_* metrics
   - Need to verify both are correct

4. **Should we add `pv_.*` and `pod_pvc_.*` to remote_write filter?**
   - Currently filtered out
   - May help with PV cost tracking

5. **Is there a Kubecost metrics exporter we're not using?**
   - OpenCost project has exporters
   - May need additional configuration

---

## 11. References

### Documentation to Review
- [ ] Kubecost Prometheus Metrics: https://docs.kubecost.com/apis/prometheus-metrics
- [ ] OpenCost Exporters: https://github.com/opencost/opencost
- [ ] Kubecost Allocation API: https://docs.kubecost.com/apis/apis-overview/allocation
- [ ] Thanos Remote Write: https://thanos.io/tip/components/receive.md/

### Current Implementation Files
- `/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py` (lines 140-365)
- `/cloud-tuner/tools/cloud_adapter/clouds/kubernetes.py` (lines 194-314)
- `/cloud-tuner/tools/cloud_adapter/model.py` (ClusterResource lines 294-347)
- `/kubecost-dev-helm/kubecost-prometheus-config.yaml` (Prometheus config)

### Test Endpoints
- Metroculus: `http://localhost:39069/metroculus/v2/kubecost_cluster_costs`
- Kubecost Allocation: `http://kubecost-dev.kubecost-dev.svc:9090/model/allocation`
- Kubecost Metrics: `http://kubecost-dev.kubecost-dev.svc:9090/metrics`

---

## 12. Conclusion

**Current Status**: Infrastructure costs ($0.57/hour) are working via Prometheus remote_write to Thanos. Allocation costs (CPU/RAM/PV) are $0.00 because Kubecost doesn't expose them as Prometheus metrics.

**Immediate Path Forward**: Deploy Phase 1 with infrastructure costs only. This provides valuable network egress and cluster overhead tracking while we investigate how to get allocation cost data.

**Long-term Solution**: Need to either:
1. Get Kubecost to export allocation costs as metrics
2. Find alternative approach for multi-cluster allocation tracking
3. Accept infrastructure-only costs for SaaS deployments

**Next Steps**:
1. ✅ Deploy cluster discovery with current implementation
2. 🔍 Investigate Kubecost metric export options
3. 📝 Document findings and update approach accordingly
