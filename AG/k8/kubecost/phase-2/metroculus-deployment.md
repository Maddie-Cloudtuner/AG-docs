# Phase 2: Metroculus API Deployment Guide

**Status**: ✅ Code Complete | 🔄 Deployment & Testing Pending
**Updated**: October 14, 2025

---

## Summary of Changes

Updated Metroculus API to use **Phase 2 allocation exporter metrics** from Thanos with automatic fallback to Phase 1 raw metric calculations.

### What Was Changed

**File**: `/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py`

1. **Added `_get_cluster_costs_from_exporter()` method** (lines 254-311)
   - Queries `cloudtuner_kubecost_*` metrics from Thanos
   - Returns detailed cost breakdown with efficiency
   - Returns `None` if metrics not available (triggers fallback)

2. **Updated `get_cluster_costs()` method** (lines 313-461)
   - **Phase 2 First**: Tries allocation exporter metrics
   - **Phase 1 Fallback**: Uses raw metric calculations if Phase 2 unavailable
   - Proper logging to show which phase is used
   - Converts hourly rates to total costs based on time range

### Key Features

✅ **Automatic Fallback**: Works with both Phase 2 (new) and Phase 1 (legacy) clusters
✅ **Accurate Costs**: Uses pre-aggregated exporter metrics with idle cost allocation
✅ **Efficiency Metrics**: CPU, RAM, and total efficiency from exporter
✅ **Backward Compatible**: No breaking changes to API response format

---

## Deployment Steps

### Option 1: Using Existing Metroculus Pod (Quick Test)

If Metroculus is already deployed, you can copy the updated file:

```bash
# 1. Copy updated controller to Metroculus pod
kubectl cp /Users/balaji/source/code/cloudtuner/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py \
  default/metroculusapi-<pod-id>:/metroculus/metroculus_api/controllers/kubecost_metrics.py

# 2. Restart Metroculus to load new code
kubectl rollout restart deployment/metroculusapi -n default

# 3. Wait for pod to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=metroculusapi -n default --timeout=60s
```

### Option 2: Build and Deploy New Image (Production)

For production deployment with proper image versioning:

```bash
# 1. Navigate to metroculus directory
cd /Users/balaji/source/code/cloudtuner/cloud-tuner/metroculus

# 2. Build Docker image
docker build -t invincibledocker24/metroculusapi:v1.5.0-phase2 .

# 3. Push to registry
docker push invincibledocker24/metroculusapi:v1.5.0-phase2

# 4. Update deployment
kubectl set image deployment/metroculusapi -n default \
  metroculusapi=invincibledocker24/metroculusapi:v1.5.0-phase2

# 5. Verify deployment
kubectl rollout status deployment/metroculusapi -n default
```

### Option 3: Update Helm Values (Recommended for Production)

If using Helm to deploy CloudTuner:

```bash
# 1. Update Helm values
# In cloud-tuner-dev/values.yaml:
#   metroculusapi:
#     image:
#       tag: v1.5.0-phase2

# 2. Upgrade release
helm upgrade cloud-tuner-dev ./cloud-tuner-dev -n default

# 3. Verify
kubectl get pods -n default -l app.kubernetes.io/name=metroculusapi
```

---

## Testing

### 1. Check Metroculus Logs

```bash
# Watch logs for Phase 2 usage
kubectl logs -n default -l app.kubernetes.io/name=metroculusapi --tail=50 -f | grep -E "Phase|cluster costs"
```

**Expected Output**:
```
INFO:metroculus.metroculus_api.controllers.kubecost_metrics:Using Phase 2 exporter metrics for d603f6e0-aff4-4e89-962d-c56f16b69404
INFO:metroculus.metroculus_api.controllers.kubecost_metrics:Cluster costs for d603f6e0-aff4-4e89-962d-c56f16b69404: Total=$12.72, CPU=$5.20, RAM=$3.80, PV=$2.12, Efficiency=45.50%
```

**If Phase 2 not available** (fallback to Phase 1):
```
INFO:metroculus.metroculus_api.controllers.kubecost_metrics:No Phase 2 exporter metrics found for d603f6e0-aff4-4e89-962d-c56f16b69404, will use Phase 1
INFO:metroculus.metroculus_api.controllers.kubecost_metrics:Falling back to Phase 1 raw metric calculations for d603f6e0-aff4-4e89-962d-c56f16b69404
```

### 2. Test API Endpoint

```bash
# Port-forward to Metroculus
kubectl port-forward -n default svc/metroculusapi 39069:80

# Query cluster costs
curl -s -H "Secret: fc83d31-461d-44c5-b4d5-41a32d6c36a1" \
  "http://localhost:39069/metroculus/v2/kubecost_cluster_costs?cloud_account_id=d603f6e0-aff4-4e89-962d-c56f16b69404&start_date=$(date -u -v-1d +%s)&end_date=$(date -u +%s)" \
  | python3 -m json.tool
```

**Expected Response** (Phase 2):
```json
{
    "cloud_account_id": "d603f6e0-aff4-4e89-962d-c56f16b69404",
    "start_date": 1760350000,
    "end_date": 1760436400,
    "summary": {
        "total_cost": 12.72,
        "cpu_cost": 5.20,
        "ram_cost": 3.80,
        "pv_cost": 2.12,
        "management_cost": 0.60,
        "load_balancer_cost": 0.50,
        "network_cost": 0.50
    },
    "efficiency": {
        "cpu_efficiency": 42.5,
        "ram_efficiency": 48.3,
        "total_efficiency": 45.4
    },
    "potential_savings": 0.0,
    "breakdown": {
        "management_cost": 0.60,
        "load_balancer_cost": 0.50,
        "network_internet_cost": 0.50,
        "network_region_cost": 0.0,
        "network_zone_cost": 0.0
    }
}
```

### 3. Verify Phase 2 Metrics Used

Key indicators that Phase 2 is working:

✅ **CPU Cost > 0**: Phase 1 often returns $0 due to missing pricing data
✅ **RAM Cost > 0**: Phase 1 often returns $0
✅ **PV Cost > 0**: Storage costs properly calculated
✅ **Efficiency Values**: Real percentages (not 0%)
✅ **Logs show**: "Using Phase 2 exporter metrics"

### 4. Compare with Thanos Direct Query

Verify Metroculus returns same values as Thanos:

```bash
# Port-forward to Thanos
kubectl port-forward -n default svc/thanos-query 9091:10902

# Query total cost from Thanos
curl -s 'http://localhost:9091/api/v1/query?query=cloudtuner_kubecost_cluster_total_cost' \
  | python3 -c "import sys,json; r=json.load(sys.stdin)['data']['result'][0]; print(f\"Hourly: ${r['value'][1]}/hr\")"

# This hourly rate * 24 hours should match Metroculus 1-day total
```

---

## Troubleshooting

### Issue 1: Metroculus Still Returns $0 Costs

**Symptoms**:
- API returns `cpu_cost: 0`, `ram_cost: 0`
- Logs show "Falling back to Phase 1"

**Diagnosis**:
```bash
# Check if exporter metrics exist in Thanos
kubectl port-forward -n default svc/thanos-query 9091:10902
curl -s 'http://localhost:9091/api/v1/query?query=cloudtuner_kubecost_cluster_total_cost' | python3 -m json.tool

# If empty result: exporter metrics not in Thanos
# If has data: Check tenant_id matches cloud_account_id
```

**Solution**:
- Verify remote_write is working: Check Prometheus remote_write metrics
- Verify filter includes `cloudtuner_kubecost_.*`: Check values.yaml
- Check tenant_id/cloud_account_id: Must match between exporter and Metroculus query

### Issue 2: Tenant ID Mismatch

**Symptoms**:
- Thanos has metrics but Metroculus can't find them
- Different tenant_id in logs vs expected

**Diagnosis**:
```bash
# Check what tenant_id is in Thanos
curl -s 'http://localhost:9091/api/v1/query?query=cloudtuner_kubecost_cluster_total_cost' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['result'][0]['metric']['tenant_id'])"

# Compare with cloud_account_id in Metroculus query
```

**Solution**:
The `tenant_id` in Thanos comes from the `Cloud-Account-Id` header in remote_write config, NOT from the exporter's tenantId setting. They must match.

**Fix in values.yaml**:
```yaml
kubecost:
  prometheus:
    server:
      remoteWrite:
      - headers:
          Cloud-Account-Id: "<must-match-cloud-account-id>"

allocationExporter:
  config:
    tenantId: "<same-value-as-above>"
```

### Issue 3: Metroculus Pod Crash Loop

**Symptoms**:
- Pod in CrashLoopBackOff
- Logs show Python import errors

**Diagnosis**:
```bash
kubectl logs -n default -l app.kubernetes.io/name=metroculusapi --tail=100
```

**Solution**:
- Syntax error in kubecost_metrics.py: Review changes
- Missing dependencies: Rebuild image with proper base
- File permissions: Check file was copied correctly

---

## Validation Checklist

Before considering deployment complete:

- [ ] Metroculus pod running and healthy
- [ ] API responds to kubecost_cluster_costs queries
- [ ] Logs show "Using Phase 2 exporter metrics" (or Phase 1 fallback)
- [ ] CPU, RAM, PV costs all > 0 (if exporter has data)
- [ ] Efficiency metrics populated (not 0%)
- [ ] Total cost matches Thanos query (hourly rate * duration)
- [ ] Phase 1 fallback works (disable exporter and test)

---

## Rollback Procedure

If Phase 2 causes issues:

### Quick Rollback
```bash
# Revert to previous Metroculus image
kubectl set image deployment/metroculusapi -n default \
  metroculusapi=invincibledocker24/metroculusapi:<previous-version>
```

### Full Rollback
```bash
# Restore original kubecost_metrics.py from git
git checkout HEAD -- metroculus/metroculus_api/controllers/kubecost_metrics.py

# Rebuild and redeploy
docker build -t invincibledocker24/metroculusapi:rollback .
docker push invincibledocker24/metroculusapi:rollback
kubectl set image deployment/metroculusapi -n default metroculusapi=invincibledocker24/metroculusapi:rollback
```

---

## Next Steps

After successful deployment:

1. **Monitor for 24 hours**: Watch logs for errors, check costs are accurate
2. **Compare with Phase 1**: If you have Phase 1 data, verify Phase 2 costs are similar
3. **Update REST API**: Ensure `/restapi/v2/clean_expenses` displays k8s_costs properly
4. **NGUI Dashboard**: Verify costs appear in UI with detailed breakdown
5. **Customer Pilot**: Deploy to 2-3 customers, gather feedback

---

## Metrics Being Used

### Phase 2 (Exporter Metrics)

| Metric | Purpose |
|--------|---------|
| `cloudtuner_kubecost_cluster_total_cost` | Total cluster cost ($/hr) |
| `cloudtuner_kubecost_cluster_cpu_cost` | CPU allocation cost ($/hr) |
| `cloudtuner_kubecost_cluster_ram_cost` | RAM allocation cost ($/hr) |
| `cloudtuner_kubecost_cluster_pv_cost` | PV cost ($/hr) |
| `cloudtuner_kubecost_cluster_network_cost` | Network egress cost ($/hr) |
| `cloudtuner_kubecost_cluster_lb_cost` | Load balancer cost ($/hr) |
| `cloudtuner_kubecost_cluster_cpu_efficiency` | CPU efficiency (%) |
| `cloudtuner_kubecost_cluster_ram_efficiency` | RAM efficiency (%) |
| `cloudtuner_kubecost_cluster_total_efficiency` | Overall efficiency (%) |

### Phase 1 (Raw Metrics - Fallback)

| Metric | Purpose |
|--------|---------|
| `container_cpu_allocation` | CPU cores allocated |
| `container_memory_allocation_bytes` | RAM bytes allocated |
| `pod_pvc_allocation` | PV size allocated |
| `node_cpu_hourly_cost` | CPU price ($/core/hr) |
| `node_ram_hourly_cost` | RAM price ($/GB/hr) |
| `pv_hourly_cost` | PV price ($/GB/hr) |

---

## Reference

- **Phase 2 Summary**: `../phase-2/deployment-summary.md`
- **Completion Plan**: `../phase-2/completion-plan.md`
- **Verification Script**: `/k8s-kubecost/verify-phase2.sh`
- **Original Implementation**: See git history for Phase 1 implementation

---

**Last Updated**: October 14, 2025
**Version**: v1.5.0-phase2
**Status**: ✅ Ready for Deployment
