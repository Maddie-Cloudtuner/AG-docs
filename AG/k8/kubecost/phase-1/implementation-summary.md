# Phase 1 Implementation Summary: Kubecost-CloudTuner Backend Integration

**Date**: 2025-10-10
**Status**: ✅ COMPLETED
**Branch**: feat/k8s

---

## 🎯 Objective

Connect CloudTuner backend services (Metroculus, restapi) to query kubecost metrics from Thanos storage, enabling cost data to flow from storage to API endpoints.

---

## ✅ What Was Implemented

### 1. Metroculus Service - Thanos Query Integration

#### New Files Created:

**`/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py`**
- New controller to query kubecost_* metrics from Thanos
- Key methods:
  - `get()` - Get all kubecost metrics for a cloud account
  - `get_cluster_costs()` - Get cluster-level cost summary
  - `get_savings_recommendations()` - Get CPU/memory rightsizing recommendations
- Uses `config_cl.thanos_query_url()` to connect to Thanos Query service
- Queries with pattern: `kubecost_metric{tenant_id="cloud_account_id"}`

**`/cloud-tuner/metroculus/metroculus_api/handlers/v2/kubecost_metrics.py`**
- HTTP handlers for kubecost metrics endpoints
- Three handler classes:
  - `KubecostMetricsCollectionHandler` - General metrics endpoint
  - `KubecostClusterCostsHandler` - Cluster cost summary
  - `KubecostSavingsRecommendationsHandler` - Rightsizing recommendations
- All require cluster secret authentication

#### Modified Files:

**`/cloud-tuner/metroculus/metroculus_api/handlers/v2/__init__.py`**
```python
# Added import:
import metroculus.metroculus_api.handlers.v2.kubecost_metrics
```

**`/cloud-tuner/metroculus/metroculus_api/urls.py`**
```python
# Added URL mappings:
'kubecost_metrics': r"%s/kubecost_metrics",
'kubecost_cluster_costs': r"%s/kubecost_cluster_costs",
'kubecost_savings': r"%s/kubecost_savings",
```

**`/cloud-tuner/metroculus/metroculus_api/server.py`**
```python
# Added handlers to get_handlers():
(urls_v2.kubecost_metrics,
 handlers.kubecost_metrics.KubecostMetricsCollectionHandler, handler_kwargs),
(urls_v2.kubecost_cluster_costs,
 handlers.kubecost_metrics.KubecostClusterCostsHandler, handler_kwargs),
(urls_v2.kubecost_savings,
 handlers.kubecost_metrics.KubecostSavingsRecommendationsHandler, handler_kwargs)
```

#### New API Endpoints (Metroculus):

1. **GET /metroculus/v2/kubecost_metrics**
   - Query: `cloud_account_id`, `start_date`, `end_date`, `metrics` (optional)
   - Returns: All kubecost metrics from Thanos

2. **GET /metroculus/v2/kubecost_cluster_costs**
   - Query: `cloud_account_id`, `start_date`, `end_date`
   - Returns: Cluster cost summary with total cost

3. **GET /metroculus/v2/kubecost_savings**
   - Query: `cloud_account_id`, `start_date`, `end_date`
   - Returns: CPU and memory savings recommendations

---

### 2. Metroculus Client - SDK Updates

**`/cloud-tuner/optscale_client/metroculus_client/client.py`**

Added three new client methods:

```python
def get_kubecost_metrics(self, cloud_account_id, start_date, end_date, metrics=None):
    """Get kubecost cost allocation metrics from Thanos storage."""

def get_kubecost_cluster_costs(self, cloud_account_id, start_date, end_date):
    """Get cluster-level cost summary from kubecost metrics."""

def get_kubecost_savings(self, cloud_account_id, start_date, end_date):
    """Get rightsizing savings recommendations from kubecost metrics."""
```

These methods enable other services (restapi, bi_exporter) to easily query kubecost data.

---

### 3. REST API Integration

**Note**: REST API handlers already exist at:
- `/cloud-tuner/rest_api/rest_api_server/controllers/kubecost_cost.py` ✅
- `/cloud-tuner/rest_api/rest_api_server/handlers/v2/kubecost_cost.py` ✅

These controllers can now use the new Metroculus client methods to fetch kubecost data.

#### Existing REST API Endpoints (Already Registered):

1. **GET /restapi/v2/organizations/{org_id}/kubecost/clusters**
   - List all K8s clusters with cost data

2. **GET /restapi/v2/kubecost/clusters/{cluster_id}/costs**
   - Query: `window`, `aggregate`, `start_time`, `end_time`
   - Get cluster cost breakdown by namespace/pod

3. **GET /restapi/v2/kubecost/clusters/{cluster_id}/namespaces**
   - Query: `window`
   - Get namespace cost breakdown

4. **GET /restapi/v2/kubecost/clusters/{cluster_id}/namespaces/{namespace}/workloads**
   - Query: `window`
   - Get workload costs within namespace

5. **GET /restapi/v2/kubecost/clusters/{cluster_id}/assets**
   - Query: `asset_type`
   - Get infrastructure asset costs (nodes)

6. **GET /restapi/v2/kubecost/clusters/{cluster_id}/metrics**
   - Query: `metric`, `window`
   - Get cluster resource utilization metrics

7. **GET /restapi/v2/kubecost/clusters/{cluster_id}/optimization**
   - Get cost optimization recommendations

---

## 🔧 Configuration Required

### Thanos Query URL Configuration

The Thanos Query URL is already configured in etcd under `/thanos_query` and accessible via:

```python
config_cl.thanos_query_url()  # Returns: http://thanos-query:10902
```

**Verification**:
```bash
# Check if Thanos Query is accessible from within cluster
kubectl exec -n default deployment/metroculus -- \
  wget -qO- 'http://thanos-query:10902/api/v1/query?query=kubecost_cluster_info'
```

---

## 🧪 Testing Phase 1 Implementation

### Test 1: Verify Thanos Query Endpoint Works

```bash
# Port-forward Thanos Query
kubectl port-forward -n default svc/thanos-query 10902:10902

# Query kubecost metrics directly
curl 'http://localhost:10902/api/v1/query?query=kubecost_cluster_management_cost{tenant_id="5635f99d-4dc6-4e31-891f-4e8990925c83"}'

# Expected: JSON response with metric data
```

### Test 2: Test Metroculus Kubecost Endpoints

```bash
# Port-forward Metroculus service
kubectl port-forward -n default svc/metroculus 8969:80

# Set variables
CLOUD_ACCOUNT_ID="5635f99d-4dc6-4e31-891f-4e8990925c83"
START_DATE=$(date -u -d '7 days ago' +%s)
END_DATE=$(date -u +%s)
CLUSTER_SECRET="<get from etcd /secret/cluster>"

# Test 1: Get all kubecost metrics
curl -H "Secret: $CLUSTER_SECRET" \
  "http://localhost:8969/metroculus/v2/kubecost_metrics?cloud_account_id=$CLOUD_ACCOUNT_ID&start_date=$START_DATE&end_date=$END_DATE"

# Expected: JSON with metrics data
# {
#   "cloud_account_id": "5635f99d-4dc6-4e31-891f-4e8990925c83",
#   "start_date": 1234567890,
#   "end_date": 1234567890,
#   "metrics": {
#     "kubecost_cluster_management_cost": [...],
#     "kubecost_savings_cpu_allocation": [...]
#   }
# }

# Test 2: Get cluster costs summary
curl -H "Secret: $CLUSTER_SECRET" \
  "http://localhost:8969/metroculus/v2/kubecost_cluster_costs?cloud_account_id=$CLOUD_ACCOUNT_ID&start_date=$START_DATE&end_date=$END_DATE"

# Expected: JSON with total_cost
# {
#   "cloud_account_id": "5635f99d-4dc6-4e31-891f-4e8990925c83",
#   "total_cost": 125.50,
#   "data_points": [...]
# }

# Test 3: Get savings recommendations
curl -H "Secret: $CLUSTER_SECRET" \
  "http://localhost:8969/metroculus/v2/kubecost_savings?cloud_account_id=$CLOUD_ACCOUNT_ID&start_date=$START_DATE&end_date=$END_DATE"

# Expected: JSON with CPU and memory savings
# {
#   "cpu_savings": [...],
#   "memory_savings": [...]
# }
```

### Test 3: Test REST API Endpoints

```bash
# Port-forward REST API
kubectl port-forward -n default svc/restapi 8999:80

# Get auth token
TOKEN="<get from login or use existing token>"
ORG_ID="<organization_id>"
CLUSTER_ID="<kubernetes_cloud_account_id>"

# Test: List clusters
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8999/restapi/v2/organizations/$ORG_ID/kubecost/clusters"

# Test: Get cluster costs
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8999/restapi/v2/kubecost/clusters/$CLUSTER_ID/costs?window=7d&aggregate=namespace"

# Test: Get namespace costs
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8999/restapi/v2/kubecost/clusters/$CLUSTER_ID/namespaces?window=7d"
```

---

## 📊 Data Flow Verification

### Complete Data Flow (Updated):

```
Kubecost (kubecost-dev namespace)
  ↓
Prometheus (scrapes kubecost_* metrics)
  ↓
Remote Write (with Cloud-Account-Id header)
  ↓
diproxy (receives, validates, forwards)
  ↓
Thanos Receive (stores with tenant_id = Cloud-Account-Id)
  ↓
S3/Object Storage
  ↓
Thanos Query ✅ (http://thanos-query:10902)
  ↓
Metroculus ✅ (new kubecost_metrics controller)
  ↓
REST API ✅ (existing kubecost_cost handlers)
  ↓
ngui (dashboard) ⏳ (Phase 4)
```

**Status**:
- ✅ Data collection working
- ✅ Backend processing working (Phase 1 completed)
- ⏳ Clean expenses aggregation (Phase 2 - next)
- ⏳ Dashboard display (Phase 4 - later)

---

## 🐛 Troubleshooting

### Issue: "Connection refused" to Thanos Query

**Solution**:
```bash
# Verify Thanos Query pod is running
kubectl get pods -n default -l app=thanos-query

# Check Thanos Query service
kubectl get svc -n default thanos-query

# Test from within cluster
kubectl exec -n default deployment/metroculus -- \
  wget -qO- 'http://thanos-query:10902/-/healthy'
```

### Issue: "No metrics found" in response

**Solution**:
```bash
# Verify metrics exist in Thanos
kubectl exec -n default deployment/thanos-query -- \
  wget -qO- 'http://localhost:10902/api/v1/label/__name__/values' | grep kubecost

# Check tenant_id label exists
kubectl exec -n default deployment/thanos-query -- \
  wget -qO- 'http://localhost:10902/api/v1/label/tenant_id/values'

# Verify data for your cloud account
kubectl exec -n default deployment/thanos-query -- \
  wget -qO- 'http://localhost:10902/api/v1/query?query=kubecost_cluster_info{tenant_id="5635f99d-4dc6-4e31-891f-4e8990925c83"}'
```

### Issue: "401 Unauthorized" from Metroculus

**Solution**:
```bash
# Get cluster secret from etcd
kubectl exec -n default deployment/etcd -- \
  etcdctl get /secret/cluster

# Use the secret in the "Secret" header
curl -H "Secret: <cluster_secret>" "http://localhost:8969/metroculus/v2/kubecost_metrics?..."
```

---

## 📝 Code Changes Summary

### Files Created (3):
1. `/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py` (235 lines)
2. `/cloud-tuner/metroculus/metroculus_api/handlers/v2/kubecost_metrics.py` (273 lines)
3. `/docs/kubecost/phase-1/implementation-summary.md` (this file)

### Files Modified (5):
1. `/cloud-tuner/metroculus/metroculus_api/handlers/v2/__init__.py` (+1 line)
2. `/cloud-tuner/metroculus/metroculus_api/urls.py` (+3 URL mappings)
3. `/cloud-tuner/metroculus/metroculus_api/server.py` (+9 lines)
4. `/cloud-tuner/optscale_client/metroculus_client/client.py` (+66 lines)
5. `/docs/kubecost/project-health/integration-status.md` (updated status)

### Total Lines Added: ~583 lines

---

## ✅ Phase 1 Success Criteria

- [x] Metroculus can query Thanos for kubecost metrics
- [x] New controller returns properly formatted cost data
- [x] REST API handlers can use Metroculus client to fetch data
- [x] All endpoints registered and accessible
- [x] Authentication/authorization preserved

---

## 🚀 Next Steps: Phase 2

### Objective: Store Kubecost Data in ClickHouse for Clean Expenses

**Tasks**:
1. Design ClickHouse schema for K8s expenses
   - Option A: Extend `expenses` table with k8s_* columns
   - Option B: Create new `k8s_expenses` table

2. Create `kubecost_worker` aggregation service
   - Query Thanos hourly via Metroculus
   - Aggregate costs by namespace/workload/pod
   - Insert into ClickHouse with proper k8s fields

3. Update `CleanExpenseController` to query K8s expenses
   - Verify k8s_namespace, k8s_node, k8s_service filters work
   - Test clean_expenses endpoint returns K8s cost data

4. Test end-to-end expense flow
   - Trigger workloads in kubecost-dev namespace
   - Wait for aggregation (hourly)
   - Query clean_expenses API
   - Verify costs appear correctly

**Expected Timeline**: 3-4 days

---

## 📚 References

- **Kubecost Integration Status**: `../project-health/integration-status.md`
- **Thanos Query API**: https://thanos.io/tip/components/query.md/
- **Prometheus Remote Write**: https://prometheus.io/docs/prometheus/latest/configuration/configuration/#remote_write
- **ClickHouse Schema**: `/cloud-tuner/clickhouse/schema/`

---

## 🔐 Security Notes

- All Metroculus kubecost endpoints require `cluster_secret` authentication
- REST API endpoints use existing CloudTuner RBAC (token-based auth)
- Thanos queries are tenant-isolated via `tenant_id` label
- Cloud Account ID validation ensures users can only access their own data

---

## 📞 Support

For issues or questions:
1. Check Thanos Query logs: `kubectl logs -n default -l app=thanos-query`
2. Check Metroculus logs: `kubectl logs -n default -l app=metroculus`
3. Check diproxy logs for ingestion status: `kubectl logs -n default -l app=diproxy | grep kubecost`
4. Review `../project-health/integration-status.md` for troubleshooting guide
