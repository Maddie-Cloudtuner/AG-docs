# Kubernetes Cost Schema Design

## Overview
Design for storing Kubecost data in CloudTuner following the existing data flow pattern.

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: Metrics Ingestion                    │
│  Kubecost → Prometheus → Remote Write → Thanos (with tenant_id) │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                   PHASE 2: Resource Discovery                    │
│              k8s_collector Worker (NEW COMPONENT)                │
│                                                                   │
│  1. Query Kubecost Allocation API (/model/allocation)           │
│  2. Discover resources: Cluster, Nodes, Namespaces, Pods        │
│  3. Write to MongoDB resources collection                        │
│  4. Write to ClickHouse expenses table                           │
│  5. Update discovery_info table                                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 3: Query & Display                      │
│           REST API → GraphQL → Frontend Dashboard                │
│                                                                   │
│  • /cloudaccounts?details=true shows costs                       │
│  • /clean_expenses shows hierarchical breakdown                  │
│  • Drill-down: Cluster → Namespace → Pod → Container            │
└─────────────────────────────────────────────────────────────────┘
```

---

## MongoDB Schema (resources collection)

### 1. Cluster-Level Resource (Virtual Resource)
```javascript
{
  _id: "k8s-cluster-<cloud_account_id>",
  organization_id: "<org_id>",
  cloud_account_id: "<k8s_cloud_account_id>",

  // Resource identification
  cloud_resource_id: "cluster:<cluster_name>",
  resource_type: "K8s Cluster",
  name: "<cluster_name>",

  // K8s specific fields
  k8s_cluster_id: "<cluster_id>",

  // Timestamps
  first_seen: 1234567890,
  last_seen: 1234567890,
  created_at: 1234567890,
  deleted_at: 0,
  active: true,

  // Date fields for querying
  _first_seen_date: ISODate("2025-01-01"),
  _last_seen_date: ISODate("2025-01-14"),

  // Cost tracking
  total_cost: 110.60,

  // Metadata
  meta: {
    cluster_version: "1.28",
    node_count: 3,
    namespace_count: 12,
    pod_count: 45,
    cloud_console_link: null
  },
  tags: {},

  // Ownership
  employee_id: null,
  pool_id: "<default_pool_id>",

  // Recommendations (future)
  recommendations: {},
  saving: 0,
  constraint_violated: false
}
```

### 2. Node-Level Resource
```javascript
{
  _id: "<uuid>",
  organization_id: "<org_id>",
  cloud_account_id: "<k8s_cloud_account_id>",

  // Resource identification
  cloud_resource_id: "node:<node_name>",
  resource_type: "K8s Node",
  name: "<node_name>",
  region: "<zone>",  // e.g., "us-central1-a"

  // K8s specific fields
  k8s_cluster_id: "<cluster_id>",
  k8s_node: "<node_name>",

  // Node metadata
  meta: {
    instance_type: "n2-standard-4",
    cpu_cores: 4,
    memory_gb: 16,
    is_spot: false,
    node_labels: {
      "node.kubernetes.io/instance-type": "n2-standard-4",
      "topology.kubernetes.io/zone": "us-central1-a"
    },
    allocatable_cpu: "3.92",
    allocatable_memory": "14.5Gi",
    cloud_console_link": null
  },

  // Timestamps
  first_seen: 1234567890,
  last_seen: 1234567890,
  created_at: 1234567890,
  deleted_at: 0,
  active: true,

  _first_seen_date: ISODate("2025-01-01"),
  _last_seen_date: ISODate("2025-01-14"),

  // Cost
  total_cost: 36.87,  // Node infrastructure cost

  // Ownership
  employee_id: null,
  pool_id: "<default_pool_id>",
  tags: {}
}
```

### 3. Namespace-Level Resource
```javascript
{
  _id: "<uuid>",
  organization_id: "<org_id>",
  cloud_account_id: "<k8s_cloud_account_id>",

  // Resource identification
  cloud_resource_id: "namespace:<namespace_name>",
  resource_type: "K8s Namespace",
  name: "<namespace_name>",

  // K8s hierarchy
  k8s_cluster_id: "<cluster_id>",
  k8s_namespace: "<namespace_name>",

  // Namespace metadata
  meta: {
    pod_count: 12,
    deployment_count: 5,
    service_count: 8,
    labels: {
      "team": "backend",
      "environment": "production"
    },
    cloud_console_link: null
  },

  // Timestamps
  first_seen: 1234567890,
  last_seen: 1234567890,
  created_at: 1234567890,
  deleted_at: 0,
  active: true,

  _first_seen_date: ISODate("2025-01-01"),
  _last_seen_date: ISODate("2025-01-14"),

  // Cost (sum of all pods in namespace)
  total_cost: 45.20,

  // Ownership (can be tagged to teams via pool_id)
  employee_id: null,
  pool_id: "<team_pool_id>",
  tags: {
    "team": "backend",
    "environment": "production"
  }
}
```

### 4. Pod-Level Resource
```javascript
{
  _id: "<uuid>",
  organization_id: "<org_id>",
  cloud_account_id: "<k8s_cloud_account_id>",

  // Resource identification
  cloud_resource_id: "pod:<namespace>/<pod_name>",
  resource_type: "K8s Pod",
  name: "<pod_name>",

  // K8s hierarchy
  k8s_cluster_id: "<cluster_id>",
  k8s_namespace: "<namespace_name>",
  k8s_node: "<node_name>",
  k8s_service: "<service_name>",  // e.g., "api-server"

  // Pod metadata
  meta: {
    controller_kind: "Deployment",
    controller_name: "api-server",
    container_count: 2,
    containers: [
      {
        name: "app",
        image: "myapp:v1.2.3",
        cpu_request: "500m",
        cpu_limit: "1000m",
        memory_request: "512Mi",
        memory_limit: "1Gi"
      },
      {
        name: "sidecar",
        image: "envoy:v1.20",
        cpu_request: "100m",
        memory_request: "128Mi"
      }
    ],
    labels: {
      "app": "api-server",
      "version": "v1.2.3",
      "team": "backend"
    },
    annotations: {},
    phase: "Running",
    restarts: 0,
    cloud_console_link: null
  },

  // Timestamps
  first_seen: 1234567890,
  last_seen: 1234567890,
  created_at: 1234567890,
  deleted_at: 0,
  active: true,

  _first_seen_date: ISODate("2025-01-01"),
  _last_seen_date: ISODate("2025-01-14"),

  // Cost (from Kubecost allocation)
  total_cost: 3.50,  // CPU + RAM + PV allocation cost

  // Cost breakdown
  cpu_cost: 1.80,
  ram_cost: 1.20,
  pv_cost: 0.50,

  // Efficiency metrics
  cpu_efficiency: 0.65,  // 65% utilization
  ram_efficiency: 0.80,  // 80% utilization

  // Ownership
  employee_id: null,
  pool_id: "<team_pool_id>",
  tags: {
    "app": "api-server",
    "version": "v1.2.3",
    "team": "backend"
  },

  // Recommendations (future)
  recommendations: {
    run_timestamp: 1234567890,
    modules: [
      {
        type": "rightsizing",
        saving": 1.20,
        recommended_cpu: "300m",
        recommended_memory: "384Mi"
      }
    ]
  },
  saving: 1.20
}
```

---

## ClickHouse Schema (expenses table)

### Existing Schema (No changes needed!)
```sql
CREATE TABLE expenses (
    cloud_account_id String,
    resource_id String,
    date Date,
    cost Float64,
    sign Int8,  -- For updates: 1 for insert, -1 for delete

    -- Already indexed for fast queries
    INDEX cloud_account_id_idx cloud_account_id TYPE bloom_filter GRANULARITY 1,
    INDEX resource_id_idx resource_id TYPE bloom_filter GRANULARITY 1
) ENGINE = CollapsingMergeTree(sign)
PARTITION BY toYYYYMM(date)
ORDER BY (cloud_account_id, resource_id, date);
```

### How K8s Data Maps to Expenses

**Example entries:**

```sql
-- Cluster-level cost (aggregated)
INSERT INTO expenses VALUES (
    'd603f6e0-aff4-4e89-962d-c56f16b69404',  -- cloud_account_id
    'k8s-cluster-d603f6e0-aff4-4e89-962d-c56f16b69404',  -- resource_id
    '2025-01-14',  -- date
    110.60,  -- cost
    1  -- sign
);

-- Node-level cost
INSERT INTO expenses VALUES (
    'd603f6e0-aff4-4e89-962d-c56f16b69404',
    '<node_resource_uuid>',
    '2025-01-14',
    36.87,
    1
);

-- Namespace-level cost (sum of pods)
INSERT INTO expenses VALUES (
    'd603f6e0-aff4-4e89-962d-c56f16b69404',
    '<namespace_resource_uuid>',
    '2025-01-14',
    45.20,
    1
);

-- Pod-level cost
INSERT INTO expenses VALUES (
    'd603f6e0-aff4-4e89-962d-c56f16b69404',
    '<pod_resource_uuid>',
    '2025-01-14',
    3.50,
    1
);
```

---

## MySQL Schema (discovery_info table)

### Existing Table Structure
```sql
CREATE TABLE discovery_info (
    id VARCHAR(36) PRIMARY KEY,
    cloud_account_id VARCHAR(36) NOT NULL,
    resource_type ENUM('instance', 'volume', 'snapshot', 'bucket', 'k8s_pod', ...) NOT NULL,
    created_at DATETIME NOT NULL,
    last_discovery_at INT NOT NULL,
    last_error_at INT DEFAULT 0,
    last_error VARCHAR(2048),
    enabled BOOLEAN DEFAULT TRUE,
    deleted_at INT DEFAULT 0,

    FOREIGN KEY (cloud_account_id) REFERENCES cloud_account(id)
);
```

### K8s Discovery Info Entries

```sql
-- Cluster discovery
INSERT INTO discovery_info VALUES (
    UUID(),
    'd603f6e0-aff4-4e89-962d-c56f16b69404',
    'k8s_cluster',
    NOW(),
    UNIX_TIMESTAMP(),
    0,
    NULL,
    TRUE,
    0
);

-- Node discovery
INSERT INTO discovery_info VALUES (
    UUID(),
    'd603f6e0-aff4-4e89-962d-c56f16b69404',
    'k8s_node',
    NOW(),
    UNIX_TIMESTAMP(),
    0,
    NULL,
    TRUE,
    0
);

-- Namespace discovery
INSERT INTO discovery_info VALUES (
    UUID(),
    'd603f6e0-aff4-4e89-962d-c56f16b69404',
    'k8s_namespace',
    NOW(),
    UNIX_TIMESTAMP(),
    0,
    NULL,
    TRUE,
    0
);

-- Pod discovery
INSERT INTO discovery_info VALUES (
    UUID(),
    'd603f6e0-aff4-4e89-962d-c56f16b69404',
    'k8s_pod',
    NOW(),
    UNIX_TIMESTAMP(),
    0,
    NULL,
    TRUE,
    0
);
```

---

## Query Patterns

### 1. Get Cluster Total Cost
```javascript
db.resources.aggregate([
  {
    $match: {
      cloud_account_id: "d603f6e0-aff4-4e89-962d-c56f16b69404",
      resource_type: "K8s Cluster",
      deleted_at: 0
    }
  },
  {
    $project: {
      name: 1,
      total_cost: 1,
      meta: 1
    }
  }
]);
```

### 2. Get Namespace Breakdown
```javascript
db.resources.aggregate([
  {
    $match: {
      cloud_account_id: "d603f6e0-aff4-4e89-962d-c56f16b69404",
      resource_type: "K8s Namespace",
      deleted_at: 0
    }
  },
  {
    $sort: { total_cost: -1 }
  },
  {
    $project: {
      name: 1,
      k8s_namespace: 1,
      total_cost: 1,
      "meta.pod_count": 1,
      tags: 1
    }
  }
]);
```

### 3. Get Pods in Namespace with Costs
```javascript
db.resources.aggregate([
  {
    $match: {
      cloud_account_id: "d603f6e0-aff4-4e89-962d-c56f16b69404",
      resource_type: "K8s Pod",
      k8s_namespace: "production",
      deleted_at: 0
    }
  },
  {
    $sort: { total_cost: -1 }
  },
  {
    $project: {
      name: 1,
      k8s_node: 1,
      k8s_service: 1,
      total_cost: 1,
      cpu_cost: 1,
      ram_cost: 1,
      cpu_efficiency: 1,
      ram_efficiency: 1,
      saving: 1,
      "meta.controller_name": 1
    }
  }
]);
```

### 4. Get Cost Trend from ClickHouse
```sql
SELECT
    date,
    resource_id,
    SUM(cost * sign) AS daily_cost
FROM expenses
WHERE
    cloud_account_id = 'd603f6e0-aff4-4e89-962d-c56f16b69404'
    AND date >= '2025-01-01'
    AND date <= '2025-01-14'
GROUP BY date, resource_id
HAVING SUM(sign) > 0
ORDER BY date, daily_cost DESC;
```

---

## Hierarchical Drill-Down Queries

### Frontend View: Cluster → Namespace → Pod

**Level 1: Cluster Overview**
```
GET /cloudaccounts/d603f6e0-aff4-4e89-962d-c56f16b69404
→ Shows cluster total: $110.60
→ Discovered resources: 3 nodes, 12 namespaces, 45 pods
```

**Level 2: Namespace Breakdown**
```
GET /clean_expenses?cloud_account_id=d603f6e0-aff4-4e89-962d-c56f16b69404
     &resource_type=K8s Namespace
→ Shows namespaces ranked by cost
→ production: $45.20 (12 pods)
→ staging: $25.30 (8 pods)
→ monitoring: $15.10 (6 pods)
```

**Level 3: Pod Breakdown**
```
GET /clean_expenses?cloud_account_id=d603f6e0-aff4-4e89-962d-c56f16b69404
     &k8s_namespace=production
     &resource_type=K8s Pod
→ Shows pods in production namespace
→ api-server-abc123: $8.50 (high CPU)
→ database-xyz789: $12.30 (high memory)
→ cache-redis-456: $4.20
```

---

## Implementation Priority

### Phase 1: Quick Patch (THIS WEEK)
1. ✅ Create cluster-level virtual resource
2. ✅ Write aggregated cost to ClickHouse
3. ✅ Update discovery_info
4. ✅ Frontend shows total cost + discovered status

### Phase 2: Node Discovery (NEXT WEEK)
1. Discover nodes from Kubecost
2. Create node resources in MongoDB
3. Write node costs to ClickHouse
4. Frontend shows node breakdown

### Phase 3: Namespace Discovery (WEEK 3)
1. Discover namespaces from Kubecost allocation API
2. Create namespace resources
3. Support namespace-level cost filtering
4. Tag namespaces to pools for chargeback

### Phase 4: Pod-Level Discovery (WEEK 4)
1. Discover pods from Kubecost
2. Full hierarchical drill-down
3. Pod-level recommendations (rightsizing)
4. Container-level cost breakdown

---

## Key Design Decisions

1. **Reuse Existing Tables**: No schema changes to ClickHouse or MySQL
2. **MongoDB Flexibility**: Use existing `meta` field for K8s-specific data
3. **Hierarchical References**: Use `k8s_cluster_id`, `k8s_namespace`, `k8s_node` fields
4. **Cost Allocation**: Follow Kubecost's allocation model (CPU + RAM + PV)
5. **Query Performance**: Leverage existing indexes on `cloud_account_id` and `resource_type`

---

## Next Steps

1. ✅ Document schema (this file)
2. Create `k8s_collector` worker
3. Implement Phase 1: Cluster-level discovery
4. Deploy and test with kubecost-dev
5. Verify frontend shows costs
6. Iterate on Phases 2-4
