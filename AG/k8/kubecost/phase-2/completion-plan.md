# Phase 2: Completion Plan & Action Items

**Status**: 🟡 Core Complete | Integration Pending
**Target Completion**: End of Week
**Priority**: HIGH

---

## Current State

### ✅ What's Working
1. Allocation exporter deployed and collecting data ($0.27/hr, 8 namespaces)
2. Prometheus scraping exporter metrics successfully
3. Remote_write sending metrics to Thanos (28,346 samples)
4. Self-contained Helm chart with dynamic service discovery

### ⚠️ What's Pending
1. Verify metrics made it to Thanos storage
2. Update Metroculus API to use exporter metrics
3. Make Prometheus scrape config persistent in Helm
4. End-to-end testing and validation
5. Production deployment checklist

---

## Action Plan

## Task 1: Verify Thanos Ingestion 🔴 HIGH PRIORITY

**Goal**: Confirm cloudtuner_kubecost_* metrics are queryable in Thanos

### Steps

#### 1.1 Find Thanos Query Endpoint
```bash
# Check if Thanos is running in the cluster
kubectl get svc -A | grep thanos

# Or check CloudTuner deployment for Thanos service
kubectl get svc -n default | grep query
```

#### 1.2 Query Thanos for Exporter Metrics
```bash
# Port-forward to Thanos Query (adjust service name)
kubectl port-forward -n default svc/<thanos-query-service> 9091:9091

# Query for exporter metrics
curl -s 'http://localhost:9091/api/v1/query?query=cloudtuner_kubecost_cluster_total_cost{tenant_id="d603f6e0-aff4-4e89-962d-c56f16b69404"}' | python3 -m json.tool

# List all cloudtuner_kubecost metrics
curl -s 'http://localhost:9091/api/v1/label/__name__/values' | grep cloudtuner_kubecost
```

#### 1.3 Alternative: Query via Metroculus
```bash
# If Thanos is not directly accessible, check via storage API
kubectl port-forward -n default svc/metroculusapi 39069:80

# Query raw Thanos data
curl -s -H "Secret: <secret>" \
  "http://localhost:39069/metroculus/v2/prometheus_query?query=cloudtuner_kubecost_cluster_total_cost&tenant_id=d603f6e0-aff4-4e89-962d-c56f16b69404"
```

### Success Criteria
- [ ] Exporter metrics visible in Thanos with correct tenant_id
- [ ] Metrics have proper labels (cluster, namespace, currency)
- [ ] Data covers recent time range (last 1-2 hours)

### Risk Mitigation
- **If metrics not in Thanos**: Check remote_write filter includes cloudtuner_kubecost_*
- **If data incomplete**: Verify remote_write authentication and network connectivity

---

## Task 2: Update Metroculus API 🔴 HIGH PRIORITY

**Goal**: Switch from Phase 1 raw metric calculations to Phase 2 exporter metrics

### Background
Current Metroculus implementation (Phase 1) queries raw Prometheus metrics and calculates costs:
- Queries: `container_cpu_usage_seconds_total`, `kube_pod_resource_requests`, etc.
- Calculates: CPU cost, RAM cost from usage and requests
- **Problem**: Returns `CPU=$0.00, RAM=$0.00` because calculations are complex

Phase 2 approach: Query pre-aggregated cloudtuner_kubecost_* metrics directly.

### File to Modify
`/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py`

### Implementation Plan

#### 2.1 Add Phase 2 Query Function
```python
def _get_cluster_costs_from_exporter(self, cloud_account_id: str, start_date: int, end_date: int) -> dict:
    """
    Query cloudtuner_kubecost_* metrics from Thanos (Phase 2).

    Returns:
        {
            'total_cost': float,
            'cpu_cost': float,
            'ram_cost': float,
            'pv_cost': float,
            'network_cost': float,
            'load_balancer_cost': float,
            'cpu_efficiency': float,
            'ram_efficiency': float,
            'total_efficiency': float,
        }
    """
    # Query pattern
    queries = {
        'total_cost': f'cloudtuner_kubecost_cluster_total_cost{{tenant_id="{cloud_account_id}"}}',
        'cpu_cost': f'cloudtuner_kubecost_cluster_cpu_cost{{tenant_id="{cloud_account_id}"}}',
        'ram_cost': f'cloudtuner_kubecost_cluster_ram_cost{{tenant_id="{cloud_account_id}"}}',
        'pv_cost': f'cloudtuner_kubecost_cluster_pv_cost{{tenant_id="{cloud_account_id}"}}',
        'network_cost': f'cloudtuner_kubecost_cluster_network_cost{{tenant_id="{cloud_account_id}"}}',
        'lb_cost': f'cloudtuner_kubecost_cluster_lb_cost{{tenant_id="{cloud_account_id}"}}',
        'cpu_efficiency': f'cloudtuner_kubecost_cluster_cpu_efficiency{{tenant_id="{cloud_account_id}"}}',
        'ram_efficiency': f'cloudtuner_kubecost_cluster_ram_efficiency{{tenant_id="{cloud_account_id}"}}',
        'total_efficiency': f'cloudtuner_kubecost_cluster_total_efficiency{{tenant_id="{cloud_account_id}"}}',
    }

    results = {}
    for metric_name, query in queries.items():
        # Query Thanos via prometheus API
        result = self._query_thanos_range(query, start_date, end_date)

        if result and len(result) > 0:
            # Sum/average values over time range
            if 'efficiency' in metric_name:
                results[metric_name] = self._average_over_range(result)
            else:
                # For costs, sum hourly rates * duration
                duration_hours = (end_date - start_date) / 3600
                hourly_rate = self._average_over_range(result)
                results[metric_name] = hourly_rate * duration_hours
        else:
            results[metric_name] = 0.0

    return results
```

#### 2.2 Update get_cluster_costs() Method
```python
def get_cluster_costs(self, cloud_account_id: str, start_date: int, end_date: int) -> dict:
    """Get Kubecost cluster costs for a cloud account."""

    # Try Phase 2 first (exporter metrics)
    try:
        costs = self._get_cluster_costs_from_exporter(cloud_account_id, start_date, end_date)

        # Validate we got real data (not all zeros)
        if costs['total_cost'] > 0:
            LOG.info(f"Using Phase 2 exporter metrics for {cloud_account_id}")
            return {
                'total_cost': costs['total_cost'],
                'cpu_cost': costs['cpu_cost'],
                'ram_cost': costs['ram_cost'],
                'pv_cost': costs['pv_cost'],
                'network_cost': costs['network_cost'],
                'load_balancer_cost': costs['lb_cost'],
                'cpu_efficiency': costs['cpu_efficiency'],
                'ram_efficiency': costs['ram_efficiency'],
                'total_efficiency': costs['total_efficiency'],
            }
    except Exception as e:
        LOG.warning(f"Phase 2 query failed for {cloud_account_id}, falling back to Phase 1: {e}")

    # Fallback to Phase 1 (raw metric calculations)
    LOG.info(f"Using Phase 1 raw metrics for {cloud_account_id}")
    return self._get_cluster_costs_from_raw_metrics(cloud_account_id, start_date, end_date)
```

#### 2.3 Add Thanos Query Helper
```python
def _query_thanos_range(self, query: str, start_date: int, end_date: int) -> list:
    """
    Query Thanos for a metric over a time range.

    Returns list of (timestamp, value) tuples.
    """
    # Use existing thanos/prometheus client from config
    thanos_url = self._config.thanos_url()  # e.g., http://thanos-query.default.svc:9090

    params = {
        'query': query,
        'start': start_date,
        'end': end_date,
        'step': '3600s',  # 1 hour resolution
    }

    response = requests.get(
        f"{thanos_url}/api/v1/query_range",
        params=params,
        timeout=30
    )
    response.raise_for_status()

    data = response.json()
    if data['status'] != 'success':
        raise Exception(f"Thanos query failed: {data}")

    results = data['data']['result']
    if not results:
        return []

    # Extract time series values
    values = []
    for result in results:
        for timestamp, value in result['values']:
            values.append((timestamp, float(value)))

    return values

def _average_over_range(self, values: list) -> float:
    """Calculate average value from time series."""
    if not values:
        return 0.0
    return sum(v[1] for v in values) / len(values)
```

### Testing
```bash
# After implementing changes, rebuild and deploy
cd /Users/balaji/source/code/cloudtuner/cloud-tuner/metroculus
docker build -t invincibledocker24/metroculusapi:v1.5.0-phase2 .
docker push invincibledocker24/metroculusapi:v1.5.0-phase2

# Update deployment
kubectl set image deployment/metroculusapi -n default metroculusapi=invincibledocker24/metroculusapi:v1.5.0-phase2

# Test API
curl -s -H "Secret: <secret>" \
  "http://localhost:39069/metroculus/v2/kubecost_cluster_costs?cloud_account_id=d603f6e0-aff4-4e89-962d-c56f16b69404&start_date=$(date -u -v-1d +%s)&end_date=$(date -u +%s)" \
  | python3 -m json.tool
```

### Success Criteria
- [ ] API returns detailed cost breakdown (CPU, RAM, PV all > 0)
- [ ] Efficiency metrics populated (0-100%)
- [ ] Total cost matches exporter metrics
- [ ] Phase 1 fallback works if Phase 2 fails

---

## Task 3: Make Prometheus Config Persistent 🟡 MEDIUM PRIORITY

**Goal**: Add allocation exporter scrape job to Helm chart permanently

### Problem
Currently manually patched Prometheus ConfigMap. If Prometheus restarts or chart is upgraded, scrape config is lost.

### Solution Options

#### Option A: Override Kubecost Subchart Values (Recommended)
```yaml
# In kubecost-integration/values.yaml
kubecost:
  prometheus:
    server:
      extraScrapeConfigs: |
        - job_name: 'kubecost-allocation-exporter'
          honor_labels: true
          scrape_interval: 60s
          metrics_path: /metrics
          kubernetes_sd_configs:
          - role: service
            namespaces:
              names:
              - {{ .Release.Namespace }}
          relabel_configs:
          - source_labels: [__meta_kubernetes_service_name]
            action: keep
            regex: .*allocation-exporter.*
```

**Test**:
```bash
helm upgrade kubecost-dev ./kubecost-integration -n kubecost-dev \
  --set allocationExporter.config.tenantId="d603f6e0-aff4-4e89-962d-c56f16b69404"

# Verify config applied
kubectl get configmap -n kubecost-dev kubecost-dev-prometheus-server -o yaml | grep allocation-exporter
```

#### Option B: ConfigMap Patch Template
Create `templates/prometheus-configmap-patch.yaml`:
```yaml
{{- if .Values.allocationExporter.enabled }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-prometheus-server-extra-scrape-configs
  labels:
    {{- include "kubecost-integration.labels" . | nindent 4 }}
data:
  extra-scrape-configs.yaml: |
    - job_name: 'kubecost-allocation-exporter'
      honor_labels: true
      scrape_interval: 60s
      static_configs:
      - targets:
        - {{ .Values.allocationExporter.name }}.{{ .Release.Namespace }}.svc.cluster.local:{{ .Values.allocationExporter.port }}
{{- end }}
```

### Success Criteria
- [ ] Helm upgrade preserves scrape configuration
- [ ] Works across different release names/namespaces
- [ ] Prometheus automatically reloads on config change

---

## Task 4: End-to-End Testing 🟡 MEDIUM PRIORITY

**Goal**: Validate complete data flow from K8s to NGUI

### Test Scenarios

#### 4.1 Single Cluster Flow
```bash
# 1. Verify exporter metrics
kubectl port-forward -n kubecost-dev svc/kubecost-allocation-exporter 9103:9103
curl http://localhost:9103/metrics | grep cloudtuner_kubecost_cluster_total_cost

# 2. Verify Prometheus has metrics
kubectl port-forward -n kubecost-dev svc/kubecost-dev-prometheus-server 9090:80
curl -s 'http://localhost:9090/api/v1/query?query=cloudtuner_kubecost_cluster_total_cost'

# 3. Verify Metroculus API
kubectl port-forward -n default svc/metroculusapi 39069:80
curl -s -H "Secret: <secret>" \
  "http://localhost:39069/metroculus/v2/kubecost_cluster_costs?cloud_account_id=d603f6e0-aff4-4e89-962d-c56f16b69404&start_date=$(date -u -v-1d +%s)&end_date=$(date -u +%s)"

# 4. Verify REST API
kubectl port-forward -n default svc/restapi 8999:80
curl -s -H "Authorization: Bearer <token>" \
  "http://localhost:8999/restapi/v2/clean_expenses?organization_id=<org_id>&start_date=$(date -u -v-7d +%s)&end_date=$(date -u +%s)" \
  | jq '.k8s_costs'

# 5. Verify NGUI Dashboard
# Open http://localhost:3000 and check Expenses page for K8s costs
```

#### 4.2 Multi-Cluster Test
```bash
# Deploy in second namespace with different tenant_id
helm install kubecost-prod ./kubecost-integration \
  -n kubecost-prod \
  --create-namespace \
  --set allocationExporter.config.tenantId="<different-tenant-id>" \
  --set allocationExporter.config.clusterName="production"

# Verify metrics are isolated by tenant_id
curl -s 'http://localhost:9090/api/v1/query?query=cloudtuner_kubecost_cluster_total_cost' \
  | jq '.data.result[] | {cluster: .metric.cluster, tenant: .metric.tenant_id, cost: .value[1]}'
```

### Success Criteria
- [ ] Metrics flow from exporter → Prometheus → Thanos → Metroculus → REST API
- [ ] Costs appear in NGUI with correct breakdowns
- [ ] Multi-tenant isolation works (different tenant_ids don't mix)
- [ ] Historical data available (at least 24 hours)

---

## Task 5: Production Readiness 🟢 LOW PRIORITY

### 5.1 Create Production Deployment Checklist

#### Prerequisites
- [ ] Cloud Account created in CloudTuner (get tenant_id)
- [ ] Kubernetes cluster configured (kubectl access)
- [ ] Helm 3.x installed
- [ ] Registry access (or use public: invincibledocker24/kubecost-allocation-exporter:v1.4.0-dev-k8s1)

#### Deployment Steps
1. [ ] Create namespace: `kubectl create namespace <namespace>`
2. [ ] Set tenant_id and clusterName values
3. [ ] Install chart: `helm install <release> ./kubecost-integration -n <namespace> --set ...`
4. [ ] Verify exporter: `kubectl get pods -n <namespace> -l app.kubernetes.io/name=kubecost-allocation-exporter`
5. [ ] Check Prometheus scraping: Query cloudtuner_kubecost_exporter_scrape_success
6. [ ] Verify remote_write: Check prometheus_remote_storage_samples_total
7. [ ] Confirm data in CloudTuner UI: Check Expenses page

#### Post-Deployment
- [ ] Set up monitoring alerts (scrape failures, cost spikes)
- [ ] Document cluster-specific configuration
- [ ] Schedule regular cost reviews with customer
- [ ] Enable pod-level metrics if needed (high cardinality warning!)

### 5.2 Update Documentation

#### User-Facing Docs
- [ ] Deployment guide for customers
- [ ] Configuration reference
- [ ] Troubleshooting guide
- [ ] FAQ (common issues, performance tuning)

#### Internal Docs
- [ ] Architecture diagram (update with Phase 2)
- [ ] Runbook for support team
- [ ] Upgrade procedure from Phase 1 to Phase 2
- [ ] Disaster recovery (data loss, metric gaps)

---

## Risk Assessment

### High Risk 🔴
1. **Metrics not in Thanos**: Remote_write failing or filter not including exporter metrics
   - **Mitigation**: Verify filter, check authentication, test network connectivity

2. **Metroculus breaking change**: Updating API might break existing Phase 1 users
   - **Mitigation**: Implement with fallback, test both code paths, gradual rollout

### Medium Risk 🟡
3. **Prometheus config persistence**: Manual patch gets overwritten on upgrade
   - **Mitigation**: Implement permanent solution (Option A or B) before production

4. **Performance issues**: High cardinality if pod metrics enabled
   - **Mitigation**: Keep pod metrics disabled by default, document when to enable

### Low Risk 🟢
5. **Multi-cluster conflicts**: tenant_id mismatch or label conflicts
   - **Mitigation**: Clear documentation on tenant_id management

---

## Timeline

| Task | Priority | Estimated Time | Dependencies |
|------|----------|----------------|--------------|
| 1. Verify Thanos | HIGH | 1-2 hours | None |
| 2. Update Metroculus | HIGH | 4-6 hours | Task 1 |
| 3. Prometheus Config | MEDIUM | 2-3 hours | None |
| 4. End-to-End Testing | MEDIUM | 3-4 hours | Task 2 |
| 5. Production Docs | LOW | 2-3 hours | Task 4 |

**Total Estimated Time**: 12-18 hours (1.5-2 days)

---

## Success Metrics

### Technical Metrics
- [ ] 100% of cloudtuner_kubecost_* metrics successfully remote_written to Thanos
- [ ] Metroculus API returns complete breakdown (CPU, RAM, PV, efficiency)
- [ ] End-to-end latency < 5 minutes (metric export → visible in UI)
- [ ] Zero manual interventions needed after deployment

### Business Metrics
- [ ] Customers can deploy chart without CloudTuner support
- [ ] K8s costs visible in UI within 10 minutes of deployment
- [ ] Cost accuracy within 5% of Kubecost native UI
- [ ] Efficiency recommendations actionable and valuable

---

## Rollback Plan

If Phase 2 causes issues:

### Quick Rollback
```bash
# Disable allocation exporter
helm upgrade kubecost-dev ./kubecost-integration -n kubecost-dev \
  --set allocationExporter.enabled=false

# Revert Metroculus API
kubectl set image deployment/metroculusapi -n default \
  metroculusapi=invincibledocker24/metroculusapi:<previous-version>
```

### Full Rollback to Phase 1
1. Uninstall kubecost-integration chart
2. Reinstall Phase 1 (direct API queries, same-cluster only)
3. Re-enable kubecost_worker if implemented

---

## Contact & Support

- **Primary Contact**: CloudTuner Integration Team
- **Documentation**: `../phase-2/deployment-summary.md`
- **Issues**: Report via GitHub or Slack #cloudtuner-k8s

---

**Created**: October 14, 2025
**Last Updated**: October 14, 2025
**Version**: 1.0
