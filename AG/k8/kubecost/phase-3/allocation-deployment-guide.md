# Phase 3: Namespace/Pod/Node Level Cost Allocation - Deployment Guide

**Date**: 2025-10-31
**Status**: Ready for Deployment
**Version**: v1.5.0

---

## Executive Summary

This phase adds **granular K8s cost tracking** at the namespace, pod, and node levels. Users can now:
- View costs broken down by namespace
- Drill down to pod-level costs
- Analyze costs by node
- Filter expenses by K8s dimensions in the UI

### Key Changes
1. ✅ Added `k8s_namespace`, `k8s_node`, `k8s_service` columns to ClickHouse `expenses` table
2. ✅ Enhanced `kubecost_worker` to fetch allocation data from Kubecost API
3. ✅ Granular expense records written per namespace/pod/node (instead of cluster-level only)
4. ✅ REST API already supports filtering by these dimensions (expense.py:707-727)

---

## Architecture Overview

### Data Flow

```
┌─────────────────┐
│ Kubecost API    │
│ /model/         │
│  allocation     │
└────────┬────────┘
         │ HTTP GET (namespace, pod, node aggregations)
         ↓
┌─────────────────────────────────────────┐
│ kubecost_worker                         │
│ - allocation_processor.py (new)        │
│ - Queries Kubecost Allocation API      │
│ - Aggregates hourly data into daily    │
│ - Creates expense records per entity   │
└────────┬────────────────────────────────┘
         │ INSERT with k8s dimensions
         ↓
┌─────────────────────────────────────────┐
│ ClickHouse expenses table               │
│ - k8s_namespace (nullable)              │
│ - k8s_node (nullable)                   │
│ - k8s_service (nullable)                │
└────────┬────────────────────────────────┘
         │ SELECT with filters
         ↓
┌─────────────────────────────────────────┐
│ REST API                                │
│ - expense.py filters (already support  │
│   k8s_namespace, k8s_node, k8s_service) │
└────────┬────────────────────────────────┘
         │ JSON response
         ↓
┌─────────────────────────────────────────┐
│ NGUI (Frontend)                         │
│ - Display namespace/pod/node costs     │
│ - Enable filtering by K8s dimensions   │
└─────────────────────────────────────────┘
```

---

## Deployment Steps

### Step 1: Run ClickHouse Migration

The migration adds three new nullable columns to the `expenses` table.

```bash
# Navigate to diworker directory
cd /Users/balaji/source/code/cloudtuner/cloud-tuner/diworker

# Run migration via Python
python3 -c "
import clickhouse_connect
import sys
sys.path.insert(0, 'migrations')

# Import migration
from migrations.202510311400000_add_k8s_dimensions import upgrade

# Connect to ClickHouse
client = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password=''
)

# Run upgrade
upgrade(client)
print('Migration completed successfully')
"
```

**Verify Migration:**
```bash
curl -s 'http://localhost:8123/?query=DESCRIBE%20TABLE%20expenses' | grep k8s
```

Expected output:
```
k8s_namespace	Nullable(String)
k8s_node	Nullable(String)
k8s_service	Nullable(String)
```

---

### Step 2: Update Cloud Account Configuration

Add `kubecost_host` to the K8s cloud account config to enable direct API access.

**Via REST API:**
```bash
# Get cloud account ID
CLOUD_ACCOUNT_ID="<your-k8s-account-id>"

# Update config
curl -X PATCH "http://localhost:8999/restapi/v2/cloud_accounts/${CLOUD_ACCOUNT_ID}" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "kubecost_host": "http://kubecost-cost-analyzer.kubecost:9090"
    }
  }'
```

**Via MongoDB (if REST API not available):**
```javascript
// Connect to MongoDB
use restapi

// Update cloud account
db.cloudaccount.updateOne(
  { _id: "<your-k8s-account-id>" },
  { $set: {
    "config.kubecost_host": "http://kubecost-cost-analyzer.kubecost:9090"
  }}
)
```

**Note**: The `kubecost_host` should be the internal Kubernetes service URL if both CloudTuner and Kubecost are in the same cluster. Use `http://<external-ip>:9090` if Kubecost is external.

---

### Step 3: Rebuild and Deploy kubecost_worker

```bash
# Navigate to kubecost_worker directory
cd /Users/balaji/source/code/cloudtuner/cloud-tuner/kubecost_worker

# Build Docker image
docker build -t invincibledocker24/kubecost_worker:v1.5.0 .

# Push to registry
docker push invincibledocker24/kubecost_worker:v1.5.0

# Update Helm values
cd /Users/balaji/source/code/cloudtuner/cloudtuner-dev-helm

# Edit cloud-tuner-dev/values.yaml
# Update kubecost_worker.image.tag to v1.5.0

# Upgrade Helm release
helm upgrade cloud-tuner-dev ./cloud-tuner-dev -n default
```

---

### Step 4: Trigger kubecost_worker Execution

The worker runs on a schedule (default: hourly). To test immediately:

**Option A: Via Kubernetes Job (Recommended)**
```bash
# Create one-time job
kubectl create job kubecost-worker-manual-$(date +%s) \
  --from=cronjob/kubecost-scheduler \
  -n default

# Watch logs
kubectl logs -n default -l job-name=kubecost-worker-manual-<timestamp> -f
```

**Option B: Via Direct Execution (for testing)**
```bash
# Get cloud account ID
CLOUD_ACCOUNT_ID="<your-k8s-account-id>"

# Execute worker directly
kubectl exec -n default deploy/kubecost-worker -- \
  python -m kubecost_worker.main $CLOUD_ACCOUNT_ID
```

---

## Verification

### 1. Check ClickHouse Data

```sql
-- Check if namespace data exists
SELECT
    k8s_namespace,
    k8s_node,
    k8s_service,
    SUM(cost * sign) as total_cost,
    COUNT(*) as records
FROM expenses
WHERE cloud_account_id = '<your-k8s-account-id>'
  AND date >= today() - 7
GROUP BY k8s_namespace, k8s_node, k8s_service
ORDER BY total_cost DESC
LIMIT 20;
```

Expected output:
```
┌─k8s_namespace─┬─k8s_node────┬─k8s_service──────────┬─total_cost─┬─records─┐
│ default       │ ᴺᵁᴸᴸ        │ ᴺᵁᴸᴸ                 │     15.25  │      7  │
│ kubecost      │ ᴺᵁᴸᴸ        │ ᴺᵁᴸᴸ                 │     12.50  │      7  │
│ ᴺᵁᴸᴸ          │ node-1      │ ᴺᵁᴸᴸ                 │     45.00  │      7  │
│ default       │ ᴺᵁᴸᴸ        │ default/nginx-abc123 │      5.20  │      7  │
└───────────────┴─────────────┴──────────────────────┴────────────┴─────────┘
```

### 2. Test REST API Filtering

**Filter by namespace:**
```bash
curl -s "http://localhost:8999/restapi/v2/organizations/<org-id>/clean_expenses?start_date=<ts>&end_date=<ts>&k8s_namespace=default" \
  | jq '.clean_expenses[] | {resource_name, cost, k8s_namespace}'
```

**Filter by node:**
```bash
curl -s "http://localhost:8999/restapi/v2/organizations/<org-id>/clean_expenses?start_date=<ts>&end_date=<ts>&k8s_node=node-1" \
  | jq '.clean_expenses[] | {resource_name, cost, k8s_node}'
```

**Filter by pod/service:**
```bash
curl -s "http://localhost:8999/restapi/v2/organizations/<org-id>/clean_expenses?start_date=<ts>&end_date=<ts>&k8s_service=nginx" \
  | jq '.clean_expenses[] | {resource_name, cost, k8s_service}'
```

### 3. Check Worker Logs

```bash
# Check recent worker executions
kubectl logs -n default -l app=kubecost-worker --tail=100

# Look for these log messages:
# - "Direct Kubecost API access: True"
# - "Processing namespace allocation data"
# - "Got X expenses for namespace"
# - "Processing pod allocation data"
# - "Got X expenses for pod"
# - "Processing node allocation data"
# - "Got X expenses for node"
```

### 4. Verify Data Completeness

```sql
-- Compare cluster total vs sum of namespace costs
SELECT
    'Cluster Total' as level,
    SUM(cost * sign) as total_cost
FROM expenses
WHERE cloud_account_id = '<your-k8s-account-id>'
  AND date >= today() - 1
  AND k8s_namespace IS NULL
  AND k8s_node IS NULL
  AND k8s_service IS NULL

UNION ALL

SELECT
    'Namespace Sum' as level,
    SUM(cost * sign) as total_cost
FROM expenses
WHERE cloud_account_id = '<your-k8s-account-id>'
  AND date >= today() - 1
  AND k8s_namespace IS NOT NULL;
```

The namespace sum should be close to (but not necessarily equal to) the cluster total, as some costs (like cluster management, idle resources) may not be allocated to namespaces.

---

## Troubleshooting

### Issue 1: No Granular Data in ClickHouse

**Symptoms**: Only cluster-level costs, no namespace/pod/node data

**Diagnosis**:
```bash
# Check if kubecost_host is configured
curl -s "http://localhost:8999/restapi/v2/cloud_accounts/<account-id>" \
  | jq '.config.kubecost_host'
```

**Solution**:
- Ensure `kubecost_host` is set in cloud account config (see Step 2)
- Verify Kubecost is accessible from kubecost_worker pod:
  ```bash
  kubectl exec -n default deploy/kubecost-worker -- \
    curl -s http://kubecost-cost-analyzer.kubecost:9090/model/allocation?window=1d
  ```

---

### Issue 2: Worker Fails with "Failed to query Kubecost Allocation API"

**Symptoms**: Worker logs show connection errors

**Diagnosis**:
```bash
# Check Kubecost service
kubectl get svc -n kubecost kubecost-cost-analyzer

# Test connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl -v http://kubecost-cost-analyzer.kubecost:9090/model/allocation?window=1h
```

**Solution**:
- Verify Kubecost service is running
- Check network policies allowing kubecost_worker → kubecost communication
- Ensure kubecost_host URL matches the actual service name/namespace

---

### Issue 3: Duplicate Costs (Cluster + Namespace Sum > Expected)

**Symptoms**: Total costs are roughly 2x expected

**Cause**: Both cluster-level and namespace-level expenses are being counted

**Solution**: This is by design. The UI should either:
1. Show cluster-level costs when k8s dimensions are NOT filtered
2. Show namespace/pod/node costs when k8s dimensions ARE filtered
3. Never sum both together

The REST API `k8s_costs` field provides the breakdown for display purposes.

---

### Issue 4: Migration Fails with "Column already exists"

**Symptoms**: Migration script errors

**Solution**:
```sql
-- Check if columns already exist
DESCRIBE TABLE expenses;

-- If columns exist, migration was already run
-- No action needed
```

---

## Frontend Integration (Next Steps)

The REST API now supports filtering by K8s dimensions, but the **NGUI needs updates** to display this data effectively.

### Recommended UI Changes

1. **Add K8s Filter Dropdowns**
   - Namespace dropdown (populated from `available_filters` endpoint)
   - Node dropdown
   - Pod/Service dropdown

2. **Update Resource Detail View**
   - Show k8s_namespace, k8s_node, k8s_service fields when present
   - Add "Kubernetes" section to resource details

3. **Create Dedicated K8s Cost Dashboard**
   - Namespace cost breakdown (pie chart)
   - Top pods by cost (table)
   - Node utilization vs cost (comparison chart)

4. **Enhance Expense Table**
   - Add K8s columns to expense list
   - Enable sorting/filtering by K8s dimensions

See `../phase-4/ui-planning.md` for detailed UI mockups and implementation guide.

---

## API Response Examples

### Clean Expenses (with namespace filter)

**Request**:
```
GET /restapi/v2/organizations/<org-id>/clean_expenses?start_date=1730336400&end_date=1730422799&k8s_namespace=default
```

**Response**:
```json
{
  "start_date": 1730336400,
  "end_date": 1730422799,
  "total_count": 42,
  "total_cost": 125.50,
  "clean_expenses": [
    {
      "id": "k8s-namespace-abc123",
      "cloud_resource_id": "k8s-namespace-abc123",
      "cloud_account_id": "<k8s-account-id>",
      "cloud_account_name": "Production K8s",
      "cloud_account_type": "kubernetes_cnr",
      "resource_name": "default namespace",
      "resource_type": "K8s Namespace",
      "service_name": "Kubernetes",
      "region": null,
      "cost": 15.25,
      "tags": {},
      "pool": null,
      "owner": null,
      "first_seen": 1730336400,
      "last_seen": 1730422799,
      "active": false,
      "meta": {
        "k8s_namespace": "default"
      }
    },
    ...
  ],
  "k8s_costs": {
    "k8s_total_cost": 330.79,
    "k8s_cost_breakdown": [...]
  }
}
```

---

## Performance Considerations

### ClickHouse Query Performance

The new nullable columns are indexed automatically by ClickHouse. However, for optimal performance:

1. **Use filters judiciously**: Filtering by k8s_namespace is fast. Filtering by k8s_service (which contains pod names) may be slower.

2. **Limit date ranges**: Always specify reasonable date ranges (7-30 days max for granular queries).

3. **Consider materialized views** (future optimization):
   ```sql
   CREATE MATERIALIZED VIEW expenses_by_namespace_mv
   ENGINE = SummingMergeTree()
   ORDER BY (cloud_account_id, k8s_namespace, date)
   AS SELECT
       cloud_account_id,
       k8s_namespace,
       toDate(date) as date,
       sum(cost * sign) as total_cost
   FROM expenses
   WHERE k8s_namespace IS NOT NULL
   GROUP BY cloud_account_id, k8s_namespace, date;
   ```

### Worker Execution Time

- **Cluster-level only**: ~5-10 seconds per account
- **With allocation data**: ~30-60 seconds per account (fetches 3 aggregation levels)

For large clusters (100+ namespaces, 1000+ pods), consider:
- Running worker less frequently (every 6 hours instead of hourly)
- Implementing pagination in Kubecost API queries (future enhancement)

---

## Rollback Procedure

If issues arise, roll back to cluster-level only:

1. **Remove kubecost_host from cloud account config**:
   ```bash
   # This disables allocation API queries
   db.cloudaccount.updateOne(
     { _id: "<account-id>" },
     { $unset: { "config.kubecost_host": "" }}
   )
   ```

2. **Redeploy previous kubecost_worker version**:
   ```bash
   helm upgrade cloud-tuner-dev ./cloud-tuner-dev \
     --set kubecost_worker.image.tag=v1.4.0 \
     -n default
   ```

3. **Optional: Remove new columns** (not recommended, as they don't hurt):
   ```sql
   ALTER TABLE expenses DROP COLUMN k8s_namespace;
   ALTER TABLE expenses DROP COLUMN k8s_node;
   ALTER TABLE expenses DROP COLUMN k8s_service;
   ```

---

## Timeline Summary

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Kubecost metrics → Thanos → Metroculus (cluster-level) |
| Phase 2 | ✅ Complete | kubecost_worker → ClickHouse (cluster-level expenses) |
| Phase 3 | ✅ Ready | Allocation API → ClickHouse (namespace/pod/node expenses) |
| Phase 4 | 📋 Planned | NGUI enhancements for K8s cost visualization |

---

## Support

For issues or questions:
1. Check worker logs: `kubectl logs -n default -l app=kubecost-worker`
2. Verify ClickHouse data: See "Verification" section above
3. Review architecture diagrams in `../phase-2/completion-comprehensive-plan.md`
4. Consult API documentation in `../handover/frontend-integration-handover.md`

---

**Last Updated**: 2025-10-31
**Document Version**: 1.0
**Next Review**: After Phase 3 deployment
