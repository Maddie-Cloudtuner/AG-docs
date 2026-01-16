# Kubecost Frontend Integration - Handover Documentation

**Date**: 2025-10-24
**Version**: Phase 2 Complete, Phase 3 In Progress
**Status**: Backend Ready, Frontend Integration Required
**Document Purpose**: Complete handover for NGUI team to integrate K8s costs into UI

---

## Executive Summary

### ✅ What's Complete (Backend)
1. **Phase 1**: Kubecost metrics flowing to CloudTuner Metroculus via Prometheus remote_write
2. **Phase 2**: kubecost_worker writing daily cluster costs to ClickHouse `expenses` table
3. **REST API Enhancement**: K8s costs integrated into existing expense endpoints
4. **Cluster Resource Creation**: Virtual "cluster" resource created for each K8s account

### 🔧 What Needs Fixing (In Progress)
1. **REST API Bug**: KeyError in `breakdown_expenses` and `available_filters` endpoints (fixed, needs deployment)
2. **Cluster Resource Fields**: Some optional fields may need enhancement for NGUI compatibility

### 📊 Current vs Planned Architecture

**Original Plan (Phase 4)**: 6 new dedicated K8s views with drill-down to namespace/pod/container levels

**Current Implementation**: Hybrid approach
- K8s costs integrated into existing expense endpoints (CloudTuner pattern)
- K8s cluster appears as a "virtual resource" alongside AWS/Azure/GCP resources
- Detailed breakdowns available via `k8s_costs` field in API responses

**Key Difference**: Instead of separate K8s-specific views, K8s costs are unified with regular cloud costs. This aligns with CloudTuner's "single pane of glass" philosophy.

---

## API Documentation

### 1. Clean Expenses Endpoint (ENHANCED)

**Endpoint**: `GET /restapi/v2/organizations/{organization_id}/clean_expenses`

**Query Parameters**:
```
start_date=<unix_timestamp>     # Required
end_date=<unix_timestamp>       # Required
limit=<number>                  # Optional, default all
cloud_account_id=<uuid>         # Optional, filter by cloud account
```

**Response Structure**:

```json
{
  "start_date": 1759276800,
  "end_date": 1761350399,
  "total_count": 125,
  "total_cost": 5580.79,
  "clean_expenses": [
    {
      "id": "resource-uuid-1",
      "cloud_resource_id": "i-abc123",
      "cloud_account_id": "aws-account-uuid",
      "cloud_account_name": "AWS Production",
      "cloud_account_type": "aws_cnr",
      "resource_name": "web-server-1",
      "resource_type": "Instance",
      "service_name": "AmazonEC2",
      "region": "us-east-1",
      "cost": 125.50,
      "tags": {},
      "pool": {
        "id": "pool-uuid",
        "name": "Production",
        "purpose": "business_unit"
      },
      "owner": {
        "id": "employee-uuid",
        "name": "John Doe"
      },
      "first_seen": 1759276800,
      "last_seen": 1761350399,
      "active": true,
      "meta": {}
    },
    {
      "id": "cluster-resource-uuid",
      "cloud_resource_id": "cluster",
      "cloud_account_id": "k8s-account-uuid",
      "cloud_account_name": "Production K8s Cluster",
      "cloud_account_type": "kubernetes_cnr",
      "resource_name": "Production K8s Cluster Cluster",
      "resource_type": "K8s Cluster",
      "service_name": "Kubernetes",
      "region": null,
      "cost": 330.79,
      "tags": {},
      "pool": null,
      "owner": null,
      "first_seen": 1759276800,
      "last_seen": 1761350399,
      "active": false,
      "meta": {
        "cloud_account_name": "Production K8s Cluster"
      }
    }
  ],
  "k8s_costs": {
    "k8s_total_cost": 330.79,
    "k8s_cost_breakdown": [
      {
        "cloud_account_id": "k8s-account-uuid",
        "cloud_account_name": "Production K8s Cluster",
        "cost": 330.79,
        "breakdown": {
          "total_cost": 330.79,
          "cpu_cost": 201.16,
          "ram_cost": 104.69,
          "pv_cost": 11.50,
          "management_cost": 22.50,
          "load_balancer_cost": 13.44,
          "network_cost": 0.0
        }
      }
    ]
  }
}
```

**Key Points**:
- `total_cost` **INCLUDES** K8s costs (330.79 + 5250.00 = 5580.79)
- K8s cluster appears as a regular resource in `clean_expenses` array
- Detailed K8s breakdown available in `k8s_costs` object
- `k8s_costs` field **only appears** when there are KUBERNETES_CNR accounts with costs > 0

---

### 2. Breakdown Expenses Endpoint (ENHANCED)

**Endpoint**: `GET /restapi/v2/organizations/{organization_id}/breakdown_expenses`

**Query Parameters**:
```
breakdown_by=<field>            # Required: service_name, region, resource_type, cloud_account_id
start_date=<unix_timestamp>     # Required
end_date=<unix_timestamp>       # Required
```

**Response Structure**:

```json
{
  "start_date": 1759276800,
  "end_date": 1761350399,
  "total_cost": 5580.79,
  "breakdown": {
    "AmazonEC2": 2500.00,
    "AmazonS3": 1200.00,
    "AmazonRDS": 1550.00,
    "Kubernetes": 330.79
  },
  "k8s_costs": {
    "k8s_total_cost": 330.79,
    "k8s_cost_breakdown": [
      {
        "cloud_account_id": "k8s-account-uuid",
        "cloud_account_name": "Production K8s Cluster",
        "cost": 330.79,
        "breakdown": {
          "total_cost": 330.79,
          "cpu_cost": 201.16,
          "ram_cost": 104.69,
          "pv_cost": 11.50,
          "management_cost": 22.50,
          "load_balancer_cost": 13.44,
          "network_cost": 0.0
        }
      }
    ]
  }
}
```

**Key Points**:
- When `breakdown_by=service_name`, K8s appears as "Kubernetes"
- When `breakdown_by=cloud_account_id`, K8s clusters appear individually
- `total_cost` includes K8s in the total
- Detailed K8s cost components available in `k8s_costs.breakdown`

**⚠️ KNOWN BUG (Fixed, Pending Deployment)**:
- Current production may return 500 error
- Fix: Check for `total_cost` key existence before adding K8s costs
- Status: Fixed in code, requires REST API rebuild/redeploy

---

### 3. Available Filters Endpoint (ENHANCED)

**Endpoint**: `GET /restapi/v2/organizations/{organization_id}/available_filters`

**Query Parameters**:
```
start_date=<unix_timestamp>     # Required
end_date=<unix_timestamp>       # Required
```

**Response Structure**:

```json
{
  "start_date": 1759276800,
  "end_date": 1761350399,
  "total_cost": 5580.79,
  "filters": {
    "cloud_account_id": [
      {"id": "aws-uuid", "name": "AWS Production", "type": "aws_cnr"},
      {"id": "k8s-uuid", "name": "Production K8s", "type": "kubernetes_cnr"}
    ],
    "service_name": ["AmazonEC2", "AmazonS3", "Kubernetes"],
    "region": ["us-east-1", "us-west-2", null],
    "resource_type": ["Instance", "Volume", "K8s Cluster"]
  },
  "k8s_costs": {
    "k8s_total_cost": 330.79,
    "k8s_cost_breakdown": [...]
  }
}
```

**Key Points**:
- K8s accounts appear in `cloud_account_id` filter with `type: "kubernetes_cnr"`
- "Kubernetes" appears in `service_name` filter
- "K8s Cluster" appears in `resource_type` filter
- Region is `null` for K8s (no regional breakdown yet)

**⚠️ KNOWN BUG (Fixed, Pending Deployment)**:
- Same KeyError issue as breakdown_expenses
- Status: Fixed in code, requires REST API rebuild/redeploy

---

### 4. Cloud Accounts List Endpoint (UNCHANGED)

**Endpoint**: `GET /restapi/v2/organizations/{organization_id}/cloud_accounts`

**Response** (K8s accounts included):

```json
{
  "cloud_accounts": [
    {
      "id": "k8s-account-uuid",
      "name": "Production K8s Cluster",
      "type": "kubernetes_cnr",
      "organization_id": "org-uuid",
      "created_at": 1759276800,
      "deleted_at": 0,
      "last_import_at": 1761350399,
      "config": {
        "cluster_id": "prod-k8s-01"
      }
    }
  ]
}
```

**Key Points**:
- K8s accounts have `type: "kubernetes_cnr"`
- Filter UI should distinguish K8s from other cloud types
- `last_import_at` indicates when kubecost_worker last ran

---

## K8s Cost Breakdown Structure

### Cost Components Available

```typescript
interface K8sCostBreakdown {
  total_cost: number;        // Total cluster cost
  cpu_cost: number;          // CPU allocation costs
  ram_cost: number;          // RAM allocation costs
  pv_cost: number;           // Persistent Volume costs
  management_cost: number;   // Control plane/management overhead
  load_balancer_cost: number; // LoadBalancer service costs
  network_cost: number;      // Network egress costs
}
```

### Cost Calculation Method

**Daily Costs**:
- kubecost_worker queries Metroculus for cluster costs
- Costs are distributed evenly across days in the time range
- Written to ClickHouse `expenses` table daily
- Supports CollapsingMergeTree for updates (sign: +1 insert, -1 delete, +1 re-insert)

**Example**:
```
Query: 7-day period (Oct 18-24)
Metroculus returns: total_cost = 330.79
Daily cost: 330.79 / 7 = 47.26 per day
ClickHouse entries: 7 rows, one per day, cost = 47.26 each
```

---

## Frontend Integration Guide

### 1. Detecting K8s Costs

**Check for K8s accounts**:
```typescript
const hasK8sAccounts = cloudAccounts.some(
  account => account.type === 'kubernetes_cnr'
);
```

**Check for K8s costs in response**:
```typescript
if (response.k8s_costs && response.k8s_costs.k8s_total_cost > 0) {
  // Display K8s-specific UI elements
  displayK8sCostBreakdown(response.k8s_costs);
}
```

---

### 2. Displaying K8s Resources

**K8s cluster in resource list**:
```typescript
// K8s clusters appear like regular resources
const k8sResources = response.clean_expenses.filter(
  resource => resource.resource_type === 'K8s Cluster'
);

// Display in resource table
k8sResources.forEach(cluster => {
  console.log(`${cluster.resource_name}: $${cluster.cost}`);
  console.log(`Account: ${cluster.cloud_account_name}`);
  console.log(`Type: ${cluster.resource_type}`);
});
```

**Special handling for K8s**:
- `region` is `null` (no regional breakdown)
- `active` is `false` (virtual resource, not a real cloud resource)
- `pool` and `owner` are typically `null` (cluster-level, not assigned)

---

### 3. K8s Cost Breakdown Visualization

**Example: Cost breakdown pie chart**:
```typescript
const k8sBreakdown = response.k8s_costs.k8s_cost_breakdown[0].breakdown;

const chartData = [
  { label: 'CPU', value: k8sBreakdown.cpu_cost, color: '#FF6B6B' },
  { label: 'RAM', value: k8sBreakdown.ram_cost, color: '#4ECDC4' },
  { label: 'Storage', value: k8sBreakdown.pv_cost, color: '#45B7D1' },
  { label: 'Network', value: k8sBreakdown.network_cost, color: '#FFA07A' },
  { label: 'Management', value: k8sBreakdown.management_cost, color: '#98D8C8' },
  { label: 'Load Balancers', value: k8sBreakdown.load_balancer_cost, color: '#F7DC6F' }
];
```

**Example: Cost breakdown table**:
```tsx
<Table>
  <TableHead>
    <TableRow>
      <TableCell>Component</TableCell>
      <TableCell align="right">Cost</TableCell>
      <TableCell align="right">% of Total</TableCell>
    </TableRow>
  </TableHead>
  <TableBody>
    {Object.entries(breakdown).map(([key, value]) => (
      <TableRow key={key}>
        <TableCell>{formatLabel(key)}</TableCell>
        <TableCell align="right">${value.toFixed(2)}</TableCell>
        <TableCell align="right">
          {((value / breakdown.total_cost) * 100).toFixed(1)}%
        </TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

---

### 4. Multi-Cloud Cost Comparison

**Aggregate costs by cloud type**:
```typescript
const costsByCloudType = cloudAccounts.reduce((acc, account) => {
  const accountCosts = response.clean_expenses
    .filter(r => r.cloud_account_id === account.id)
    .reduce((sum, r) => sum + r.cost, 0);

  const type = account.type;
  acc[type] = (acc[type] || 0) + accountCosts;
  return acc;
}, {});

// Result:
// {
//   "aws_cnr": 4200.00,
//   "azure_cnr": 1050.00,
//   "kubernetes_cnr": 330.79
// }
```

**Display in stacked bar chart**:
```typescript
const chartData = Object.entries(costsByCloudType).map(([type, cost]) => ({
  name: formatCloudType(type),
  cost: cost,
  color: getCloudTypeColor(type)
}));
```

---

### 5. Filtering by Cloud Type

**Filter dropdown**:
```tsx
<Select
  value={selectedCloudType}
  onChange={(e) => setSelectedCloudType(e.target.value)}
>
  <MenuItem value="all">All Cloud Types</MenuItem>
  <MenuItem value="aws_cnr">AWS</MenuItem>
  <MenuItem value="azure_cnr">Azure</MenuItem>
  <MenuItem value="gcp_cnr">GCP</MenuItem>
  <MenuItem value="kubernetes_cnr">Kubernetes</MenuItem>
</Select>
```

**Apply filter**:
```typescript
const filteredExpenses = selectedCloudType === 'all'
  ? response.clean_expenses
  : response.clean_expenses.filter(
      expense => expense.cloud_account_type === selectedCloudType
    );
```

---

### 6. K8s-Specific Views

**Option A: Expand existing resource detail view**

When user clicks on a K8s cluster resource:
```tsx
function ResourceDetailView({ resource }) {
  const isK8sCluster = resource.resource_type === 'K8s Cluster';

  return (
    <div>
      <ResourceSummary resource={resource} />

      {isK8sCluster && (
        <K8sCostBreakdownCard
          breakdown={response.k8s_costs.k8s_cost_breakdown.find(
            b => b.cloud_account_id === resource.cloud_account_id
          )}
        />
      )}

      <CostTrendChart resourceId={resource.id} />
    </div>
  );
}
```

**Option B: New dedicated K8s dashboard**

Create a new route `/kubernetes` with:
- All K8s clusters listed
- Aggregated K8s costs
- Cost breakdown by component
- Multi-cluster comparison

---

## Implementation Recommendations

### Phase 1: Basic Integration (Week 1-2)

**Goal**: Display K8s costs alongside regular cloud costs

**Tasks**:
1. ✅ Update `clean_expenses` API client to handle `k8s_costs` field
2. ✅ Display K8s cluster resources in resource list/table
3. ✅ Add K8s cost breakdown card/modal
4. ✅ Filter resources by `kubernetes_cnr` type
5. ✅ Show K8s costs in total cost calculations

**Success Criteria**:
- User can see K8s cluster in resources list
- User can see total K8s costs
- User can view cost breakdown by component (CPU, RAM, etc.)

---

### Phase 2: Enhanced Views (Week 3-4)

**Goal**: Provide K8s-specific insights

**Tasks**:
1. Create dedicated K8s dashboard page
2. Add K8s cost trend charts
3. Implement multi-cluster comparison
4. Add service name breakdown ("Kubernetes" in service list)
5. Enhance resource detail view for K8s clusters

**Success Criteria**:
- User can navigate to dedicated K8s cost page
- User can compare multiple K8s clusters
- User can see cost trends over time

---

### Phase 3: Advanced Features (Week 5-6)

**Goal**: Enable cost optimization workflows

**Tasks**:
1. Display efficiency metrics (when available from Metroculus)
2. Show optimization recommendations (when available)
3. Implement budget alerts for K8s clusters
4. Add export functionality for K8s cost reports

**Success Criteria**:
- User can see efficiency scores
- User receives alerts when K8s costs exceed budget
- User can export K8s cost data

---

## Data Source Architecture

```
┌──────────────┐
│   Kubecost   │
│  (Customer   │
│   Cluster)   │
└──────┬───────┘
       │ Prometheus remote_write
       │ (kubecost_* metrics)
       ↓
┌──────────────┐
│   diproxy    │
│  (CloudTuner │
│   Receiver)  │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│    Thanos    │
│ (Long-term   │
│   Storage)   │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│  Metroculus  │
│   (Query &   │
│  Aggregate)  │
└──────┬───────┘
       │ kubecost_worker queries hourly
       │ GET /metroculus/v2/kubecost_cluster_costs
       ↓
┌──────────────┐
│ kubecost_    │
│   worker     │
│ (Transform & │
│    Write)    │
└──────┬───────┘
       │ Daily expense records
       ↓
┌──────────────┐
│ ClickHouse   │
│   expenses   │
│    table     │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│  REST API    │
│ /v2/clean_   │
│  expenses    │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│     NGUI     │
│  (Frontend)  │
└──────────────┘
```

---

## TypeScript Interfaces

```typescript
// /src/api/types/kubernetes.ts

export interface K8sCosts {
  k8s_total_cost: number;
  k8s_cost_breakdown: K8sClusterCostBreakdown[];
}

export interface K8sClusterCostBreakdown {
  cloud_account_id: string;
  cloud_account_name: string;
  cost: number;
  breakdown: K8sCostComponents;
}

export interface K8sCostComponents {
  total_cost: number;
  cpu_cost: number;
  ram_cost: number;
  pv_cost: number;
  management_cost: number;
  load_balancer_cost: number;
  network_cost: number;
}

export interface CleanExpensesResponse {
  start_date: number;
  end_date: number;
  total_count: number;
  total_cost: number;
  clean_expenses: Resource[];
  k8s_costs?: K8sCosts;  // Optional: only present if K8s costs exist
}

export interface Resource {
  id: string;
  cloud_resource_id: string;
  cloud_account_id: string;
  cloud_account_name: string;
  cloud_account_type: string;
  resource_name: string;
  resource_type: string;
  service_name: string;
  region: string | null;
  cost: number;
  tags: Record<string, string>;
  pool: Pool | null;
  owner: Owner | null;
  first_seen: number;
  last_seen: number;
  active: boolean;
  meta: Record<string, any>;
}

export interface BreakdownExpensesResponse {
  start_date: number;
  end_date: number;
  total_cost: number;
  breakdown: Record<string, number>;
  k8s_costs?: K8sCosts;
}

export interface AvailableFiltersResponse {
  start_date: number;
  end_date: number;
  total_cost: number;
  filters: {
    cloud_account_id: Array<{id: string; name: string; type: string}>;
    service_name: string[];
    region: Array<string | null>;
    resource_type: string[];
  };
  k8s_costs?: K8sCosts;
}
```

---

## Testing Checklist

### Backend Testing (REST API)

- [ ] `GET /clean_expenses` returns K8s cluster resource
- [ ] `GET /clean_expenses` includes `k8s_costs` field when K8s accounts exist
- [ ] `total_cost` includes K8s costs
- [ ] `GET /breakdown_expenses?breakdown_by=service_name` includes "Kubernetes"
- [ ] `GET /breakdown_expenses?breakdown_by=cloud_account_id` includes K8s accounts
- [ ] `GET /available_filters` includes K8s in cloud_account_id, service_name, resource_type
- [ ] No 500 errors on any endpoint (after fix deployment)

### Frontend Testing

- [ ] K8s cluster appears in resources list
- [ ] K8s cost breakdown displayed correctly
- [ ] Total cost calculation includes K8s
- [ ] Filter by `kubernetes_cnr` works
- [ ] Multi-cloud cost comparison chart includes K8s
- [ ] Resource detail view handles K8s cluster type
- [ ] Export functionality includes K8s costs
- [ ] No JavaScript errors when `k8s_costs` field is absent

---

## Known Issues & Workarounds

### Issue 1: REST API 500 Error on breakdown_expenses/available_filters

**Status**: Fixed, pending deployment
**Error**: `KeyError: 'total_cost'`
**Cause**: Child controllers don't initialize `total_cost` before parent adds K8s costs
**Fix**: Check for key existence before incrementing
**Workaround**: Handle 500 error gracefully in frontend, display partial data
**ETA**: Next REST API deployment cycle

---

### Issue 2: K8s Cluster Resource Missing Optional Fields

**Status**: Investigating
**Symptoms**: NGUI resource detail view may not render correctly
**Cause**: K8s cluster resource has `null` values for region, pool, owner
**Fix**: Enhanced cluster resource creation with more complete metadata
**Workaround**: Check for null/undefined before rendering optional fields

---

### Issue 3: No Namespace/Pod-Level Breakdown Yet

**Status**: Future enhancement (Phase 3)
**Current**: Only cluster-level aggregated costs
**Planned**: Detailed allocation by namespace, workload, pod, container
**API**: Will require new endpoints (see `../phase-4/ui-planning.md`)
**Timeline**: Q1 2026 (after Phase 2 stabilization)

---

## API Response Examples

### Example 1: Organization with AWS + K8s

**Request**:
```bash
GET /restapi/v2/organizations/d5c0476c-b342-4c96-90e6-191cc0a8ea56/clean_expenses?start_date=1759276800&end_date=1761350399
```

**Response** (truncated):
```json
{
  "start_date": 1759276800,
  "end_date": 1761350399,
  "total_count": 152,
  "total_cost": 5580.79,
  "clean_expenses": [
    {
      "id": "aws-instance-1",
      "resource_name": "web-server-1",
      "resource_type": "Instance",
      "service_name": "AmazonEC2",
      "cost": 125.50
    },
    {
      "id": "k8s-cluster-1",
      "cloud_resource_id": "cluster",
      "resource_name": "Production K8s Cluster Cluster",
      "resource_type": "K8s Cluster",
      "service_name": "Kubernetes",
      "region": null,
      "cost": 330.79,
      "active": false
    }
  ],
  "k8s_costs": {
    "k8s_total_cost": 330.79,
    "k8s_cost_breakdown": [
      {
        "cloud_account_id": "bc55eb8c-5db2-4c32-b976-2df0edb0619a",
        "cloud_account_name": "k8s-kubecost",
        "cost": 330.79,
        "breakdown": {
          "total_cost": 330.79,
          "cpu_cost": 201.16,
          "ram_cost": 104.69,
          "pv_cost": 11.50,
          "management_cost": 22.50,
          "load_balancer_cost": 13.44,
          "network_cost": 0.0
        }
      }
    ]
  }
}
```

---

### Example 2: Breakdown by Service Name

**Request**:
```bash
GET /restapi/v2/organizations/d5c0476c-b342-4c96-90e6-191cc0a8ea56/breakdown_expenses?breakdown_by=service_name&start_date=1759276800&end_date=1761350399
```

**Response**:
```json
{
  "start_date": 1759276800,
  "end_date": 1761350399,
  "total_cost": 5580.79,
  "breakdown": {
    "AmazonEC2": 2500.00,
    "AmazonS3": 1200.00,
    "AmazonRDS": 1550.00,
    "Kubernetes": 330.79
  },
  "k8s_costs": {
    "k8s_total_cost": 330.79,
    "k8s_cost_breakdown": [...]
  }
}
```

---

## Deployment Status

### Backend Services Status

| Component | Version | Status | Notes |
|-----------|---------|--------|-------|
| kubecost_worker | v1.4.0 | ✅ Deployed | Writing to ClickHouse |
| kubecost_scheduler | v1.4.0 | ✅ Running | Hourly execution |
| REST API | v1.4.0-k8s | ⚠️ Needs Redeploy | KeyError fix pending |
| Metroculus | Phase 2 | ✅ Deployed | Providing cost data |
| ClickHouse | N/A | ✅ Running | Storing K8s expenses |

### Required Actions

1. **Rebuild REST API** with KeyError fix:
   ```bash
   cd /cloud-tuner/rest_api
   docker build -t invincibledocker24/rest_api:v1.4.0-k8s .
   docker push invincibledocker24/rest_api:v1.4.0-k8s
   ```

2. **Redeploy REST API**:
   ```bash
   cd /cloudtuner-dev-helm
   # Update values.yaml → restapi.image.tag: v1.4.0-k8s
   helm upgrade cloud-tuner-dev ./cloud-tuner-dev -n default
   ```

3. **Verify fix**:
   ```bash
   curl "http://localhost:8999/restapi/v2/organizations/.../breakdown_expenses?..."
   # Should return 200, not 500
   ```

---

## Support & Escalation

### Questions About API Contracts
- **Contact**: Backend team
- **Documentation**: This file + `/cloud-tuner/rest_api/rest_api_server/controllers/expense.py:1561-1571`

### Questions About Data Accuracy
- **Check**: kubecost_worker logs (`kubectl logs -l app=kubecost-worker`)
- **Verify**: ClickHouse data (`SELECT * FROM expenses WHERE cloud_account_id = '<k8s-account-id>'`)
- **Contact**: Backend/DevOps team

### Questions About Kubecost Metrics
- **Check**: Metroculus logs (`kubectl logs -l app=metroculus`)
- **Verify**: Metroculus API directly (`curl http://localhost:8970/metroculus/v2/kubecost_cluster_costs?...`)
- **Documentation**: `../phase-2/completion-comprehensive-plan.md`

---

## Next Steps for Frontend Team

### Immediate (Week 1)
1. ✅ Review this handover document
2. ✅ Test REST API endpoints manually (Postman/curl)
3. ✅ Identify which existing UI components need K8s support
4. ✅ Create TypeScript interfaces (provided above)
5. ✅ Add K8s cluster to resources list view

### Short-term (Week 2-3)
6. Add K8s cost breakdown visualization
7. Update total cost calculations
8. Implement cloud type filtering
9. Handle null/undefined fields gracefully
10. Add K8s-specific icons/badges

### Medium-term (Week 4-6)
11. Create dedicated K8s dashboard (optional)
12. Add multi-cluster comparison views
13. Implement cost trend charts for K8s
14. Add budget alerts for K8s clusters
15. User testing and feedback collection

---

## Appendix: Metroculus API (For Reference)

While NGUI doesn't call Metroculus directly, understanding the data source helps debugging.

**Endpoint**: `GET /metroculus/v2/kubecost_cluster_costs`

**Parameters**:
```
cloud_account_id=<uuid>
start_date=<unix_timestamp>
end_date=<unix_timestamp>
```

**Response**:
```json
{
  "summary": {
    "total_cost": 330.79,
    "cpu_cost": 201.16,
    "ram_cost": 104.69,
    "pv_cost": 11.50,
    "management_cost": 22.50,
    "load_balancer_cost": 13.44,
    "network_cost": 0.0
  }
}
```

**Data Flow**:
```
Metroculus → kubecost_worker → ClickHouse → REST API → NGUI
```

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-24 | 1.0 | Initial handover document |

---

**Document Maintained By**: Backend Team
**Last Updated**: 2025-10-24
**Next Review**: After REST API fix deployment

---

**Questions?** Contact the backend team or refer to:
- `../phase-2/completion-comprehensive-plan.md` (Architecture)
- `../phase-4/ui-planning.md` (Future roadmap)
- `/cloud-tuner/rest_api/rest_api_server/controllers/expense.py` (Implementation)
