# Kubecost-CloudTuner Integration Status & Implementation Plan

**Date**: 2025-10-10
**Namespace**: `kubecost-dev`
**Cloud Account ID**: `5635f99d-4dc6-4e31-891f-4e8990925c83`
**Kubernetes ID**: `0f9e62cf-1b5d-4f22-af26-21e48974ea90`

---

## 🎯 Executive Summary

**Current Status**: DATA COLLECTION ✅ | BACKEND PROCESSING ❌

**Key Finding**: All 33 kubecost_* metrics are successfully flowing from kubecost-dev namespace to Thanos storage, but CloudTuner backend services (risp/bi, restapi, ngui) don't know how to query and display them.

**Data Flow (Verified)**:
```
Kubecost → Prometheus → diproxy → Thanos → S3 Storage ✅
                                      ↓
                                 Thanos Query (33 metrics available) ✅
                                      ↓
                                     ??? ❌ <- THIS IS THE GAP
                                      ↓
                              risp/bi → restapi → ngui ❌
```

**Next Steps**: Build CloudTuner services to query Thanos and expose kubecost cost data via REST API and dashboard.

---

## Current Status Details

### What's Working

#### 1. Kubecost Deployment (kubecost-dev namespace)
- **Status**: ✅ All 4 pods running healthy
- **Pods**:
  - `kubecost-dev` (cost-analyzer) - 4/4 containers
  - `kubecost-dev-prometheus-server` - 1/1
  - `kubecost-dev-forecasting` - 1/1
  - `kubecost-dev-grafana` - 2/2

#### 2. Metrics Collection
- **Status**: ✅ Prometheus scraping 33 kubecost_* metrics
- **Key Metrics Being Scraped**:
  ```
  kubecost_cluster_info
  kubecost_cluster_management_cost
  kubecost_node_is_spot
  kubecost_load_balancer_cost
  kubecost_network_internet_egress_cost
  kubecost_network_region_egress_cost
  kubecost_network_zone_egress_cost
  kubecost_savings_cpu_allocation
  kubecost_savings_memory_allocation_bytes
  kubecost_allocation_data_status
  kubecost_asset_data_status
  + 22 more kubecost_* metrics
  + container_*, kube_*, node_* metrics
  ```

#### 3. Prometheus Remote Write
- **Status**: ✅ Successfully sending to CloudTuner
- **Metrics**:
  - Total samples sent: **13,076,378**
  - Failed samples: **0**
  - Last sent: **60 seconds ago** (actively sending)
  - Pending in queue: **1,767** (normal)
- **Endpoint**: `https://dev.dashboard.cloudtuner.ai/storage/api/v2/write`
- **Auth**: Basic auth (luffy/luffy01)
- **Headers**: `Cloud-Account-Id: 5635f99d-4dc6-4e31-891f-4e8990925c83`

### What's NOT Working

#### 1. CloudTuner Backend Processing
- **Status**: ❌ Metrics arriving but not processed/displayed
- **Symptom**: Dashboard shows no updates after removing `cloudtuner-k8s` namespace
- **Root Cause**: CloudTuner backend services not configured to process kubecost_* metrics

#### 2. Missing Backend Components
The following CloudTuner services need updates to process Kubecost metrics:

1. **diproxy** (storage/api/v2/write endpoint) ✅
   - **VERIFIED**: Successfully receiving and forwarding 13M+ samples to Thanos
   - Metrics stored under tenant_id = Cloud-Account-Id
   - No changes needed here

2. **risp/bi** (Reporting/Analytics services) ❌
   - No logic to query Thanos for kubecost_* metrics
   - Missing cost allocation queries
   - No rightsizing recommendation processing
   - **ACTION NEEDED**: Add Thanos Query client and kubecost metric queries

3. **restapi** (REST API endpoints) ❌
   - Missing K8s-specific endpoints for kubecost data
   - No integration with existing cloud account structure
   - **ACTION NEEDED**: Create K8s cost endpoints that call risp/bi

4. **ngui** (Frontend Dashboard) ❌
   - Not displaying kubecost cost allocation data
   - Missing K8s workload views
   - **ACTION NEEDED**: Add dashboard components for K8s costs

---

## Architecture Overview

### Data Flow (ACTUAL - Verified)
```
Kubecost → Prometheus → remote_write → diproxy → Thanos Receive → S3/Object Storage
  (✅)       (✅)           (✅)          (✅)         (✅)                (✅)
                                                         ↓
                                                   Thanos Query (33 kubecost_* metrics available)
                                                         ↓
                                                        ???
                                                         ↓
                                                   risp/bi → restapi → ngui
                                                    (❌)      (❌)      (❌)
```

**KEY FINDING**: All 33 kubecost metrics ARE successfully stored in Thanos under tenant_id `5635f99d-4dc6-4e31-891f-4e8990925c83`!

---

## Implementation Roadmap

### Phase 1: Verify Backend Data Storage ✅ COMPLETED

**Objective**: Confirm kubecost_* metrics are being stored

**Results**:
- ✅ diproxy receiving metrics (all 200 OK responses)
- ✅ Metrics forwarded to **Thanos Receive**
- ✅ **33 kubecost_* metrics** stored in Thanos under tenant_id `5635f99d-4dc6-4e31-891f-4e8990925c83`
- ✅ Thanos Query endpoint: `thanos-query:10902`
- ✅ Data queryable via Prometheus API

**Sample Query**:
```bash
kubectl exec -n default thanos-query-54cd97dcb7-xjlhl -- \
  wget -qO- 'http://localhost:10902/api/v1/query?query=kubecost_cluster_info'
```

---

### Phase 2: Build Backend Services (Priority: CRITICAL - Next Step)

**Objective**: Build services to query and process kubecost metrics

**Tasks**:

1. **Service: risp/bi (Analytics Engine)**
   - Location: `/Users/balaji/source/code/cloudtuner/cloud-tuner/risp` or `/bi`
   - Create queries for:
     - `kubecost_cluster_management_cost` → cluster-level costs
     - `kubecost_node_is_spot` → spot vs on-demand node tracking
     - `kubecost_savings_cpu_allocation` → rightsizing recommendations
     - `kubecost_allocation_data_status` → cost allocation by namespace/pod
   - Map to CloudTuner's existing cost structures

2. **Service: restapi (API Layer)**
   - Location: `/Users/balaji/source/code/cloudtuner/cloud-tuner/restapi`
   - Add endpoints:
     ```
     GET /restapi/v2/cloud_accounts/<id>/k8s/cost_allocation
     GET /restapi/v2/cloud_accounts/<id>/k8s/rightsizing
     GET /restapi/v2/cloud_accounts/<id>/k8s/efficiency
     GET /restapi/v2/cloud_accounts/<id>/k8s/clusters
     ```
   - Return data queried from risp/bi

3. **Service: ngui (Frontend)**
   - Location: `/Users/balaji/source/code/cloudtuner/cloud-tuner/ngui`
   - Add K8s cost views:
     - Cluster cost overview
     - Namespace cost breakdown
     - Pod/workload costs
     - Rightsizing recommendations

**Expected Outcome**: Backend services can query and return kubecost cost data

---

### Phase 3: Test End-to-End Flow (Priority: HIGH)

**Objective**: Verify complete data flow from Kubecost to Dashboard

**Tasks**:
1. Trigger test workloads in kubecost-dev namespace
2. Query restapi endpoints for cost data
3. Verify dashboard displays costs correctly
4. Compare with Kubecost's own UI (port-forward to kubecost-dev:9090)

**Expected Outcome**: Dashboard shows accurate K8s workload costs

---

### Phase 4: Production Hardening (Priority: MEDIUM)

**Objective**: Make integration production-ready

**Tasks**:
1. Add authentication/authorization for Cloud-Account-Id mapping
2. Implement metric retention policies
3. Add alerting for metric ingestion failures
4. Document deployment process
5. Create Helm chart updates for easy customer deployment

---

## Quick Wins for Development

### Option 1: Manual Data Verification (Fastest - 15 mins)
**Goal**: Prove metrics are in storage
1. Check ClickHouse tables for kubecost metrics
2. Run manual queries to extract cost data
3. Display raw data in terminal

### Option 2: Simple REST Endpoint (Medium - 2 hours)
**Goal**: Create one working endpoint
1. Pick simplest metric (e.g., `kubecost_cluster_management_cost`)
2. Create `/restapi/v2/cloud_accounts/<id>/k8s/cluster_cost` endpoint
3. Query from storage and return JSON
4. Test with curl

### Option 3: Full Integration (Long - 1-2 weeks)
**Goal**: Complete CloudTuner-Kubecost integration
1. Follow Phase 1-4 roadmap above
2. Build all backend services
3. Create dashboard views
4. Test with real workloads

---

## Key Decisions Needed

1. **Storage Backend**: Which system stores kubecost metrics?
   - ClickHouse (likely for time-series)
   - InfluxDB (if configured for metrics)
   - Both?

2. **Data Transformation**: How to map kubecost metrics to CloudTuner models?
   - Direct passthrough (fast, less control)
   - Transform to CloudTuner schema (slower, more control)

3. **API Design**: New endpoints or extend existing?
   - New K8s-specific endpoints (cleaner separation)
   - Extend existing cloud account endpoints (unified view)

4. **Dashboard Integration**: Separate K8s section or unified cost view?
   - Separate K8s tab (easier to build)
   - Unified cloud + K8s view (better UX)

---

## Next Immediate Steps

### Step 1: Verify Storage (< 5 minutes)
```bash
# Check if diproxy is receiving metrics
kubectl logs -n default -l app=diproxy --tail=50 | grep "POST.*write"

# Check ClickHouse for kubecost metrics
kubectl exec -n default deployment/clickhouse -- clickhouse-client -q \
  "SELECT DISTINCT(__name__) FROM metrics WHERE __name__ LIKE 'kubecost%' LIMIT 10"
```

### Step 2: Understand Current Backend (< 30 minutes)
```bash
# Find which services handle metrics
cd /Users/balaji/source/code/cloudtuner/cloud-tuner
grep -r "storage/api/v2/write" --include="*.py"
grep -r "prometheus" --include="*.py" | grep -i "metric"
```

### Step 3: Create Proof of Concept (< 2 hours)
- Pick one simple metric to expose
- Create minimal REST endpoint
- Test data retrieval
- Validate against Kubecost UI

