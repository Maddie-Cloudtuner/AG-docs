# Phase 2 Kubecost Integration: Comprehensive Completion Plan

**Status**: Partial Implementation - Frontend Not Showing Data
**Date**: 2025-10-14
**Objective**: Complete end-to-end Phase 2 integration with frontend visibility

---

## Executive Summary

**What's Working:**
- ✅ Allocation Exporter deployed and functioning (was showing $0.09/hour)
- ✅ Prometheus scraping exporter successfully
- ✅ kube-state-metrics integrated (141 pods)
- ✅ Kubecost API returning allocation data with costs
- ✅ Remote write configured with correct credentials
- ✅ Metroculus Phase 2 code deployed

**What's Broken:**
- ❌ **Hour Boundary Issue**: Exporter currently showing $0.00 (timing issue)
- ❌ **Remote Write Not Verified**: Metrics may not be reaching Thanos
- ❌ **Metroculus Falling Back to Phase 1**: Can't find Phase 2 metrics in Thanos
- ❌ **Frontend Not Showing Data**: No K8s costs visible in UI
- ❌ **Metroculus API Errors**: Returns "Error" instead of valid JSON

---

## Data Pipeline Architecture

```
┌─────────────┐     ┌───────────────────┐     ┌────────────┐
│   Kubecost  │────▶│ Allocation        │────▶│ Prometheus │
│   API       │     │ Exporter          │     │ (scrape)   │
│ :9090/model │     │ cloudtuner_       │     │            │
│ /allocation │     │ kubecost_*        │     │            │
└─────────────┘     │ metrics           │     └──────┬─────┘
                    │ :9103/metrics     │            │
                    └───────────────────┘            │
                                                     │ remote_write
                                                     ▼
┌─────────────┐     ┌───────────────────┐     ┌────────────┐
│   NGUI      │◀────│ REST API          │◀────│ Metroculus │
│  Frontend   │     │ /clean_expenses   │     │ Phase 2    │
│             │     │ + k8s_costs       │     │ Query      │
└─────────────┘     └───────────────────┘     └──────▲─────┘
                                                      │
                                                      │ PromQL
                                              ┌───────┴──────┐
                                              │    Thanos    │
                                              │    Query     │
                                              └──────────────┘
```

---

## Current Pipeline Status

### 1. Kubecost → Exporter ✅ (But Timing Issue)
**Status**: Working but caught at hour boundary

**Evidence**:
```
15:47 - Exported 8 namespaces, total_cost=$0.09
15:49 - Exported 8 namespaces, total_cost=$0.09
15:51 - Exported 8 namespaces, total_cost=$0.09
16:00 - Exported 0 namespaces, total_cost=$0.00  ← Hour boundary
```

**Issue**: Kubecost computes allocations in 1-hour windows. When crossing hour boundaries (15:00-16:00 → 16:00-17:00), new data needs 2-5 minutes to compute.

**Fix**: Wait for Kubecost to complete hourly ETL, or query previous hour's data.

---

### 2. Exporter → Prometheus ✅
**Status**: Scraping successfully

**Evidence**:
- Prometheus target `kubecost-allocation-exporter` shows as `up`
- Metrics visible: `cloudtuner_kubecost_cluster_total_cost{tenant_id="bc55eb8c-5db2-4c32-b976-2df0edb0619a"}`
- Currently showing $0 (due to hour boundary)

**Config**: `k8s-kubecost/charts/kubecost-integration/values.yaml:28-57`

---

### 3. Prometheus → Thanos ❌ (Unverified)
**Status**: Configured but not confirmed working

**Configuration**:
```yaml
remoteWrite:
  - url: "https://dev.dashboard.cloudtuner.ai/storage/api/v2/write"
    name: cloudtuner
    headers:
      Cloud-Account-Id: "bc55eb8c-5db2-4c32-b976-2df0edb0619a"
    basic_auth:
      username: kubecost
      password: kubecost@123
    write_relabel_configs:
    - source_labels: [__name__]
      regex: '(kubecost_.*|cloudtuner_kubecost_.*|...)'
      action: keep
```

**Issues**:
1. No remote_write logs visible in Prometheus
2. Cannot verify metrics in Thanos (connectivity issue during check)
3. Regex includes `cloudtuner_kubecost_*` ✓

**Verification Needed**:
```bash
# Check Prometheus is sending
kubectl logs -n kubecost-dev kubecost-dev-prometheus-server-XXX | grep remote_write

# Check Thanos has data
kubectl port-forward -n default svc/thanos-query 9091:10902
curl 'http://localhost:9091/api/v1/query?query=cloudtuner_kubecost_cluster_total_cost{tenant_id="bc55eb8c-5db2-4c32-b976-2df0edb0619a"}'
```

---

### 4. Thanos → Metroculus ❌ (Phase 2 Not Working)
**Status**: Metroculus can't find Phase 2 metrics, falling back to Phase 1

**Evidence**:
```
INFO: No Phase 2 exporter metrics found for bc55eb8c-5db2-4c32-b976-2df0edb0619a, will use Phase 1
INFO: Falling back to Phase 1 raw metric calculations
INFO: Cluster costs: Total=$1.15, CPU=$0.00, RAM=$0.00, PV=$0.00, Efficiency=0.00%
```

**Root Cause Options**:
1. Metrics never reached Thanos (remote_write issue)
2. Metrics in Thanos but wrong tenant_id label
3. Metrics in Thanos but Metroculus querying incorrectly
4. Metrics exist but all values are 0 (Phase 2 detection requires value > 0)

**Metroculus Phase 2 Detection Logic** (`/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py:254-311`):
```python
def _get_cluster_costs_from_exporter(self, thanos_url, cloud_account_id, start_date, end_date):
    # Queries: cloudtuner_kubecost_cluster_total_cost{tenant_id="..."}
    # Returns None if no data found
    # Phase 1 fallback if None returned
```

**Fix Required**:
1. Verify metrics in Thanos with correct tenant_id
2. Check Metroculus Thanos URL configuration
3. Ensure at least one cost metric > 0

---

### 5. Metroculus → REST API ❌ (Returns Error)
**Status**: Metroculus API endpoint returning "Error" instead of JSON

**Test**:
```bash
curl -H "Secret: fc83d31-461d-44c5-b4d5-41a32d6c36a1" \
  "http://localhost:39069/metroculus/v2/kubecost_cluster_costs?cloud_account_id=bc55eb8c-5db2-4c32-b976-2df0edb0619a&start_date=1760400000&end_date=1760486400"
# Returns: Error
```

**Expected Response**:
```json
{
  "total_cost": 1.15,
  "cpu_cost": 0.50,
  "ram_cost": 0.35,
  "pv_cost": 0.10,
  "network_cost": 0.05,
  "lb_cost": 0.15,
  "cpu_efficiency": 0.65,
  "ram_efficiency": 0.58,
  "total_efficiency": 0.62,
  "breakdown": {...}
}
```

**Possible Issues**:
1. Authentication/secret mismatch
2. Invalid cloud_account_id (doesn't exist in database)
3. Metroculus code error (check logs)
4. Port forward to wrong service/port

**Fix Required**:
1. Verify cloud_account_id exists in CloudTuner database
2. Check Metroculus logs for actual error
3. Test with correct authentication

---

### 6. REST API → Frontend ❓ (Integration Unknown)
**Status**: REST API code exists but frontend integration unclear

**REST API Code** (`/cloud-tuner/rest_api/rest_api_server/controllers/expense.py:838-892`):
```python
def _get_k8s_costs(self, org_id, start_date, end_date):
    # Gets KUBERNETES_CNR accounts
    # Calls metroculus_cl.get_kubecost_cluster_costs()
    # Returns k8s_costs dict
```

**Used in** (`expense.py:1527-1531`):
```python
def get(self, ...):
    # ... compute other expenses ...

    k8s_costs = self._get_k8s_costs(org_id, start_date, end_date)
    if k8s_costs and k8s_costs.get('k8s_total_cost', 0) > 0:
        result['k8s_costs'] = k8s_costs
        result['total_cost'] += k8s_costs['k8s_total_cost']
```

**Expected REST API Response**:
```json
{
  "start_date": 1234567890,
  "end_date": 1234567990,
  "total_count": 100,
  "total_cost": 250.50,
  "clean_expenses": [...],
  "k8s_costs": {
    "k8s_total_cost": 105.00,
    "k8s_cost_breakdown": [...]
  }
}
```

**Frontend Requirements** (Unknown):
- Does NGUI look for `k8s_costs` field?
- Does it display K8s costs separately from cloud costs?
- Is there a dedicated K8s dashboard/section?

**Fix Required**:
1. Test REST API endpoint with valid org_id
2. Check if k8s_costs appears in response
3. Identify NGUI code that should display this data
4. Update NGUI if needed to show K8s costs

---

## Priority Action Plan

### PHASE A: Fix Data Collection (Priority 1)

#### A1. Resolve Hour Boundary Issue
**Goal**: Get exporter showing non-zero costs consistently

**Option 1: Wait Strategy** (Simplest)
```bash
# Wait 5-10 minutes after hour boundary
# Verify exporter logs show costs again
kubectl logs -n kubecost-dev kubecost-allocation-exporter-XXX --tail=5
```

**Option 2: Query Previous Hour** (Faster)
Update exporter to query `window=2h` or explicitly use previous hour's completed window.

**Option 3: Use lastN Windows** (Most Robust)
Modify exporter to use Kubecost's accumulate mode with offset to get most recent complete window.

**Timeline**: 10-60 minutes depending on approach

---

#### A2. Verify Remote Write to Thanos
**Goal**: Confirm metrics reaching Thanos with correct tenant_id

**Steps**:
1. Check Prometheus remote_write queue status:
```bash
kubectl exec -n kubecost-dev kubecost-dev-prometheus-server-XXX -- \
  wget -qO- 'http://localhost:9090/api/v1/query?query=prometheus_remote_storage_samples_total'
```

2. Check for send errors:
```bash
kubectl logs -n kubecost-dev kubecost-dev-prometheus-server-XXX | grep -i "remote_write\|error"
```

3. Verify metrics in Thanos:
```bash
kubectl port-forward -n default svc/thanos-query 9091:10902
curl 'http://localhost:9091/api/v1/query?query=cloudtuner_kubecost_cluster_total_cost{tenant_id="bc55eb8c-5db2-4c32-b976-2df0edb0619a"}'
```

4. If metrics not in Thanos:
   - Check diproxy logs (CloudTuner's Thanos receiver)
   - Verify credentials (username: kubecost, password: kubecost@123)
   - Check Cloud-Account-Id header matches tenant_id

**Timeline**: 1-2 hours (including waiting for metrics to propagate)

---

#### A3. Fix Metroculus API Error
**Goal**: Metroculus returns valid JSON instead of "Error"

**Steps**:
1. Check if cloud_account_id exists:
```sql
SELECT id, name, type FROM cloud_accounts
WHERE id = 'bc55eb8c-5db2-4c32-b976-2df0edb0619a'
AND type = 'kubernetes_cnr'
AND deleted_at IS NULL;
```

2. If not exists, create K8s cloud account in CloudTuner:
   - Via UI: Add new cloud account, type "Kubernetes"
   - Via API: POST /cloud_accounts with KUBERNETES_CNR type
   - Use the provided ID: bc55eb8c-5db2-4c32-b976-2df0edb0619a

3. Check Metroculus logs for actual error:
```bash
kubectl logs -n default metroculusapi-XXX | grep -A 5 "bc55eb8c"
```

4. Test Metroculus endpoint again

**Timeline**: 30 minutes - 2 hours

---

### PHASE B: Enable Phase 2 Detection (Priority 2)

#### B1. Verify Metrics in Thanos
**Goal**: Confirm cloudtuner_kubecost_* metrics exist in Thanos

**Required Metrics**:
- `cloudtuner_kubecost_cluster_total_cost`
- `cloudtuner_kubecost_cluster_cpu_cost`
- `cloudtuner_kubecost_cluster_ram_cost`
- `cloudtuner_kubecost_cluster_cpu_efficiency`
- `cloudtuner_kubecost_cluster_ram_efficiency`

**With Labels**:
- `tenant_id="bc55eb8c-5db2-4c32-b976-2df0edb0619a"`
- `cluster="k8s-kubecost"`

**Values**: At least one metric must have value > 0 for Phase 2 detection

---

#### B2. Test Metroculus Phase 2 Logic
**Goal**: Verify Metroculus switches to Phase 2 when metrics available

**Manual Test**:
```python
# In Metroculus pod
from metroculus_api.controllers.kubecost_metrics import KubecostMetricsController
controller = KubecostMetricsController()
costs = controller._get_cluster_costs_from_exporter(
    thanos_url="http://thanos-query.default.svc.cluster.local:10902",
    cloud_account_id="bc55eb8c-5db2-4c32-b976-2df0edb0619a",
    start_date=1760400000,
    end_date=1760486400
)
print(costs)  # Should not be None if Phase 2 working
```

**Expected Logs**:
```
INFO: Using Phase 2 exporter metrics for bc55eb8c-5db2-4c32-b976-2df0edb0619a
INFO: Cluster costs: Total=$0.09, CPU=$0.05, RAM=$0.03, Efficiency=62.5%
```

**Timeline**: 1 hour

---

### PHASE C: Frontend Integration (Priority 3)

#### C1. Verify REST API Returns k8s_costs
**Goal**: Confirm /clean_expenses endpoint includes K8s costs

**Test**:
```bash
curl -X GET "http://localhost:8999/restapi/v2/clean_expenses?organization_id=ORG_ID&start_date=1760400000&end_date=1760486400" \
  -H "Authorization: Bearer TOKEN"
```

**Expected Response**:
```json
{
  "total_cost": 250.50,
  "k8s_costs": {
    "k8s_total_cost": 105.00,
    "k8s_cost_breakdown": [...]
  }
}
```

**If Missing**:
- Check if KUBERNETES_CNR cloud account linked to organization
- Verify REST API code was deployed (version check)
- Check REST API logs for errors in _get_k8s_costs()

**Timeline**: 30 minutes

---

#### C2. Frontend Display Integration
**Goal**: NGUI shows K8s costs to user

**Requirements**:
1. Identify NGUI component that displays expenses
2. Check if it reads `k8s_costs` field from API
3. Update component to display K8s costs separately or add to total
4. Add visualization (charts, breakdown by cluster/namespace)

**Possible Locations** (to investigate):
- `/cloud-tuner/ngui_service/ui/src/components/Expenses`
- `/cloud-tuner/ngui_service/ui/src/containers/ExpensesContainer`
- `/cloud-tuner/ngui_service/ui/src/api/restapi`

**Frontend Update Required**:
```javascript
// In expense display component
const {clean_expenses, k8s_costs, total_cost} = response.data;

if (k8s_costs) {
  displayK8sCosts(k8s_costs);
  // Show breakdown by cluster
  k8s_costs.k8s_cost_breakdown.forEach(cluster => {
    renderClusterCosts(cluster);
  });
}
```

**Timeline**: 2-4 hours (investigation + development)

---

## Verification Checklist

### End-to-End Verification

- [ ] **Exporter Health**
  ```bash
  kubectl logs -n kubecost-dev kubecost-allocation-exporter-XXX --tail=5
  # Should show: total_cost > $0.00
  ```

- [ ] **Prometheus Scrape**
  ```bash
  kubectl exec -n kubecost-dev prometheus-XXX -- \
    wget -qO- 'http://localhost:9090/api/v1/query?query=cloudtuner_kubecost_cluster_total_cost'
  # Should return: value > 0
  ```

- [ ] **Thanos Storage**
  ```bash
  curl 'http://localhost:9091/api/v1/query?query=cloudtuner_kubecost_cluster_total_cost{tenant_id="bc55eb8c-5db2-4c32-b976-2df0edb0619a"}'
  # Should return: metrics with correct tenant_id
  ```

- [ ] **Metroculus Phase 2**
  ```bash
  kubectl logs -n default metroculusapi-XXX | grep "Phase 2"
  # Should show: "Using Phase 2 exporter metrics"
  ```

- [ ] **Metroculus API**
  ```bash
  curl -H "Secret: XXX" "http://localhost:39069/metroculus/v2/kubecost_cluster_costs?..."
  # Should return: Valid JSON with costs
  ```

- [ ] **REST API**
  ```bash
  curl "http://localhost:8999/restapi/v2/clean_expenses?..." -H "Authorization: Bearer XXX"
  # Should contain: "k8s_costs" field
  ```

- [ ] **Frontend**
  - Open CloudTuner NGUI
  - Navigate to Expenses page
  - Verify K8s costs visible
  - Check breakdown by cluster/namespace

---

## Timeline Estimates

| Phase | Task | Time | Dependencies |
|-------|------|------|--------------|
| A1 | Fix hour boundary | 10-60 min | None |
| A2 | Verify remote_write | 1-2 hours | A1 |
| A3 | Fix Metroculus API error | 30 min - 2 hours | None (parallel) |
| B1 | Verify Thanos metrics | 30 min | A2 |
| B2 | Test Phase 2 detection | 1 hour | B1 |
| C1 | Test REST API | 30 min | A3, B2 |
| C2 | Frontend integration | 2-4 hours | C1 |

**Total Estimated Time**: 6-10 hours (with parallelization)

---

## Risk Mitigation

### Risk 1: Remote Write Failing
**Impact**: High - Blocks entire Phase 2
**Mitigation**:
- Test with curl to diproxy endpoint directly
- Verify diproxy logs for incoming writes
- Check if credentials are correct
- Fallback to Phase 1 if unresolvable

### Risk 2: Cloud Account Not Created
**Impact**: Medium - Blocks Metroculus and REST API
**Mitigation**:
- Create KUBERNETES_CNR cloud account in CloudTuner
- Link to appropriate organization
- Use exact ID: bc55eb8c-5db2-4c32-b976-2df0edb0619a

### Risk 3: Frontend Changes Required
**Impact**: Medium - Delays user visibility
**Mitigation**:
- Document REST API response format
- Create separate task for frontend team
- Provide API examples and mock data

### Risk 4: Hour Boundary Timing
**Impact**: Low - Temporary, self-resolving
**Mitigation**:
- Use window=2h or offset queries
- Implement retry logic in exporter
- Add alerting for extended $0 periods

---

## Success Criteria

**Phase 2 Complete When**:
1. ✅ Allocation exporter consistently reports costs > $0
2. ✅ Prometheus stores cloudtuner_kubecost_* metrics
3. ✅ Thanos contains metrics with correct tenant_id
4. ✅ Metroculus logs show "Using Phase 2 exporter metrics"
5. ✅ Metroculus API returns valid JSON with cost breakdown
6. ✅ REST API /clean_expenses includes k8s_costs field
7. ✅ Frontend displays K8s costs to end users

**Performance Metrics**:
- Metric lag: < 2 minutes from Kubecost to Thanos
- Phase 2 detection: 100% when metrics available
- API response time: < 500ms for k8s_costs
- Data accuracy: ±5% vs Kubecost UI

---

## Next Immediate Steps

1. **Wait for Exporter to Show Costs** (5-10 min)
   ```bash
   watch -n 30 'kubectl logs -n kubecost-dev kubecost-allocation-exporter-XXX --tail=1'
   ```

2. **Verify Cloud Account Exists** (5 min)
   ```bash
   kubectl exec -n default clickhouse-0 -- clickhouse-client -q \
     "SELECT id, name, type FROM cloud_accounts WHERE id='bc55eb8c-5db2-4c32-b976-2df0edb0619a'"
   ```

3. **Check Metroculus Logs** (5 min)
   ```bash
   kubectl logs -n default metroculusapi-XXX --tail=100 | grep -i "error\|exception"
   ```

4. **Test Thanos Connectivity** (10 min)
   ```bash
   kubectl port-forward -n default svc/thanos-query 9091:10902
   curl 'http://localhost:9091/api/v1/query?query=up'
   ```

**Once these pass, proceed with Priority A2 (Verify Remote Write)**

---

## Document Updates

This plan supersedes/supplements:
- `../phase-2/deployment-summary.md` - Technical architecture
- `../phase-2/completion-plan.md` - Original completion steps
- `../phase-2/executive-summary.md` - High-level overview
- `../phase-2/phase-2-end-to-end-documentation.md` - Configuration reference

**Status**: Living document - update as issues resolved
