# Phase 2 Implementation Summary: REST API K8s Cost Integration

## Overview
Phase 2 integrates Kubernetes costs from Metroculus (Phase 1) into the REST API's `clean_expenses` endpoint. This allows K8s costs to appear alongside cloud provider costs in a unified expense view.

## Architecture Decision

### Approach Taken: REST API Integration (Phase 1 Reuse)
**Flow**: Prometheus remote_write → Thanos → Metroculus → REST API → Dashboard

**Why This Approach**:
- CloudTuner is a closed-source SaaS
- Customers deploy helm charts in their own clusters
- Metrics already flow via Prometheus remote_write (Phase 1)
- Multi-cluster compatible
- No new services required
- Minimal deployment friction

### Approach Discarded: Direct Kubecost Querying
**Flow**: kubecost_worker → Kubecost API → ClickHouse → REST API

**Why Discarded**:
- Only works in same-cluster deployment
- Breaks multi-tenant SaaS architecture
- Requires additional worker service deployment
- Not compatible with customer-deployed helm charts

## Implementation Details

### File Modified
**Path**: `/cloud-tuner/rest_api/rest_api_server/controllers/expense.py`

### Changes Made

#### 1. Import MetroculusClient (Line 23)
```python
from optscale_client.metroculus_client.client import Client as MetroculusClient
```

#### 2. Add metroculus_cl Property (Lines 831-836)
```python
@property
def metroculus_cl(self):
    if self._metroculus_cl is None:
        self._metroculus_cl = MetroculusClient(
            url=self._config.metroculus_url(),
            secret=self._config.cluster_secret())
    return self._metroculus_cl
```

#### 3. Create _get_k8s_costs Method (Lines 838-892)
```python
def _get_k8s_costs(self, cloud_account_ids):
    """
    Query K8s costs from Metroculus for kubernetes_cnr cloud accounts.

    Uses Phase 1 integration: kubecost metrics from Thanos via Metroculus.

    Args:
        cloud_account_ids: List of cloud account IDs to query

    Returns:
        Dict with k8s_total_cost and k8s_cost_breakdown
    """
    from rest_api.rest_api_server.models.enums import CloudTypes

    # Filter for K8s cloud accounts
    k8s_accounts = self.session.query(CloudAccount).filter(
        CloudAccount.id.in_(cloud_account_ids),
        CloudAccount.type == CloudTypes.KUBERNETES_CNR,
        CloudAccount.deleted.is_(False)
    ).all()

    if not k8s_accounts:
        return {'k8s_total_cost': 0, 'k8s_cost_breakdown': []}

    k8s_total_cost = 0
    k8s_cost_breakdown = []

    for k8s_account in k8s_accounts:
        try:
            # Query kubecost cluster costs from Metroculus (Phase 1 endpoint)
            status_code, cost_data = self.metroculus_cl.get_kubecost_cluster_costs(
                k8s_account.id,
                int(self.start_date),
                int(self.end_date)
            )

            if status_code == 200 and cost_data:
                cluster_cost = cost_data.get('summary', {}).get('total_cost', 0)
                k8s_total_cost += cluster_cost

                k8s_cost_breakdown.append({
                    'cloud_account_id': k8s_account.id,
                    'cloud_account_name': k8s_account.name,
                    'cost': cluster_cost,
                    'breakdown': cost_data.get('summary', {})
                })

        except Exception as e:
            LOG.warning(f"Failed to fetch K8s costs for account {k8s_account.id}: {e}")
            continue

    return {
        'k8s_total_cost': k8s_total_cost,
        'k8s_cost_breakdown': k8s_cost_breakdown
    }
```

#### 4. Update get() Method (Lines 1527-1531)
```python
# Add K8s costs from Metroculus (Phase 1 integration)
k8s_costs = self._get_k8s_costs(query_filters['cloud_account_id'])
if k8s_costs['k8s_total_cost'] > 0:
    result['total_cost'] += k8s_costs['k8s_total_cost']
    result['k8s_costs'] = k8s_costs

return result
```

## API Response Format

### Endpoint
```
GET /restapi/v2/clean_expenses
  ?organization_id={org_id}
  &start_date={timestamp}
  &end_date={timestamp}
```

### Response Structure
```json
{
  "start_date": 1234567890,
  "end_date": 1234567990,
  "total_count": 100,
  "total_cost": 250.50,
  "clean_expenses": [
    {
      "cloud_account_id": "aws-account-id",
      "cost": 145.50,
      ...
    }
  ],
  "k8s_costs": {
    "k8s_total_cost": 105.00,
    "k8s_cost_breakdown": [
      {
        "cloud_account_id": "k8s-cluster-1-id",
        "cloud_account_name": "Production K8s Cluster",
        "cost": 105.00,
        "breakdown": {
          "total_cost": 105.00,
          "management_cost": 3.20,
          "cpu_cost": 50.00,
          "ram_cost": 30.00,
          "pv_cost": 10.00,
          "network_cost": 5.00,
          "load_balancer_cost": 6.80
        }
      }
    ]
  }
}
```

**Note**: The `k8s_costs` field only appears if there are K8s cloud accounts with costs > 0.

## Phase 1 Dependencies

### Metroculus Endpoint Used
```python
metroculus_cl.get_kubecost_cluster_costs(
    cloud_account_id,
    start_date,
    end_date
)
```

**Endpoint**: `GET /metroculus/v2/kubecost_cluster_costs`

**Returns**:
```json
{
  "cloud_account_id": "xxx",
  "start_date": 1234567890,
  "end_date": 1234567990,
  "summary": {
    "total_cost": 105.00,
    "management_cost": 3.20,
    "cpu_cost": 50.00,
    "ram_cost": 30.00,
    "pv_cost": 10.00,
    "network_cost": 5.00,
    "load_balancer_cost": 6.80
  },
  "metrics": [...]
}
```

## Deployment

### Image Built
```bash
cd /Users/balaji/source/code/cloudtuner/cloud-tuner/rest_api
docker build -t invincibledocker24/rest_api:v1.4.0-k8s .
docker push invincibledocker24/rest_api:v1.4.0-k8s
```

### Helm Values Updated
```yaml
restapi:
  image:
    tag: v1.4.0-k8s
```

### Deployment Command
```bash
cd /Users/balaji/source/code/cloudtuner/cloudtuner-dev-helm
helm upgrade cloud-tuner-dev ./cloud-tuner-dev -n default
```

## Verification Steps

### 1. Check REST API Pod
```bash
kubectl get pods -l app=restapi
kubectl describe pod -l app=restapi | grep "Image:"
# Should show: invincibledocker24/rest_api:v1.4.0-k8s
```

### 2. Check K8s Cloud Accounts
```bash
kubectl exec -n default deployment/mariadb -- \
  mysql -u root -proot restapi -e \
  "SELECT id, name, type FROM cloud_account WHERE type='kubernetes_cnr' AND deleted_at IS NULL;"
```

### 3. Test Metroculus Endpoint (Phase 1)
```bash
CLUSTER_SECRET=$(kubectl get secret cluster-secret -n default -o jsonpath='{.data.cluster_secret}' | base64 -d)
CLOUD_ACCOUNT_ID="<k8s-account-id>"
START_DATE=$(date -v-7d +%s)
END_DATE=$(date +%s)

curl -H "Secret: $CLUSTER_SECRET" \
  "http://localhost:8969/metroculus/v2/kubecost_cluster_costs?cloud_account_id=$CLOUD_ACCOUNT_ID&start_date=$START_DATE&end_date=$END_DATE"
```

### 4. Test REST API Endpoint (Phase 2)
```bash
# Get auth token
kubectl exec -n default deployment/mariadb -- \
  mysql -u root -proot restapi -e \
  "SELECT token FROM auth LIMIT 1;" -sN

# Test endpoint
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8999/restapi/v2/clean_expenses?organization_id=<org_id>&start_date=<ts>&end_date=<ts>"

# Look for k8s_costs field in response
```

## Next Steps

### 1. Dashboard Integration (NGUI)
- Update expense dashboard to show K8s costs section
- Add K8s cost breakdown visualization
- Show per-cluster K8s costs
- Display cost breakdown by category (CPU, RAM, PV, etc.)

### 2. API Documentation
- Document new `k8s_costs` field in API docs
- Add examples with K8s cost data
- Update OpenAPI/Swagger specs

### 3. Monitoring
- Add metrics for K8s cost queries
- Monitor Metroculus response times
- Track K8s cost data availability

## Files Modified

### Core Implementation
- `/cloud-tuner/rest_api/rest_api_server/controllers/expense.py` (55 lines added)

### Documentation
- `/docs/kubecost/phase-2/implementation-summary.md` (this file)
- `/docs/kubecost/phase-1/implementation-summary.md` (Phase 1 reference)

## Files Discarded (Not Deployed)

### Phase 2 Alternative Approach (Same-Cluster Only)
- `/cloud-tuner/diworker/diworker/migrations/202510131139000_k8s_expenses_table.py` (76 lines)
- `/cloud-tuner/kubecost_worker/` (628 lines total)
  - kubecost_client.py
  - processor.py
  - main.py
  - kubecost_scheduler/main.py
  - Dockerfile
  - requirements.txt

**Reason**: These components implement direct Kubecost API querying which only works in same-cluster deployments. CloudTuner's multi-cluster SaaS architecture requires the remote_write approach (Phase 1).

## Benefits

✅ **Multi-Cluster Compatible**: Works with customer-deployed helm charts
✅ **No New Services**: Reuses Phase 1 Metroculus infrastructure
✅ **Unified Expense View**: K8s costs alongside cloud provider costs
✅ **Minimal Deployment**: Only REST API image needs updating
✅ **Scalable**: Handles multiple K8s clusters via cloud account IDs
✅ **Cost Breakdown**: Detailed breakdown by category (CPU, RAM, PV, LB, Network)

## Summary

Phase 2 successfully integrates Kubernetes costs into CloudTuner's expense tracking system using the Phase 1 Metroculus infrastructure. The integration adds K8s costs to the `clean_expenses` endpoint, providing a unified view of all infrastructure costs (cloud + K8s) in a single API response.

**Total Code Changed**: 55 lines added to expense.py
**Services Required**: 0 new services (reuses Metroculus)
**Deployment**: REST API image update only
**Status**: Implemented and deployed, pending verification
