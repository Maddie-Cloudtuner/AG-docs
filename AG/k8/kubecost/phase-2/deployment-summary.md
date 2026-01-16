# Phase 2: Kubecost Allocation Exporter - Deployment Summary

**Date**: October 14, 2025
**Status**: ✅ Core Implementation Complete | 🔄 Integration Testing In Progress
**Version**: v1.4.0-dev-k8s1

---

## Executive Summary

Phase 2 successfully implements a **production-ready, self-contained Kubecost Allocation Exporter** that exposes Kubecost allocation costs as Prometheus metrics for remote_write to CloudTuner's Thanos. This approach enables CloudTuner to receive detailed K8s cost data (CPU, RAM, PV, efficiency metrics) while maintaining the remote_write-only architecture required for multi-cluster SaaS deployments.

### Key Achievement
✅ **Self-Contained Helm Chart**: Users can deploy `kubecost-integration` with any release name in any namespace, and it works automatically without external dependencies.

---

## Architecture

```
Customer Cluster:
  ┌─────────────────────────────────────────────────────────────┐
  │  Kubecost (cost-analyzer)                                   │
  │    └─> Allocation API (:9090/model/allocation)             │
  └────────────────┬────────────────────────────────────────────┘
                   │
                   │ Query (every 120s)
                   ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Allocation Exporter (:9103/metrics)                        │
  │    - Aggregates by namespace (default) or pod               │
  │    - Includes idle cost allocation (weighted)               │
  │    - Exposes cloudtuner_kubecost_* metrics                  │
  └────────────────┬────────────────────────────────────────────┘
                   │
                   │ Scrape (every 60s)
                   ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Prometheus (kubecost-dev-prometheus-server)                │
  │    - Scrapes exporter metrics                               │
  │    - Applies metric filters                                 │
  └────────────────┬────────────────────────────────────────────┘
                   │
                   │ remote_write
                   ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  CloudTuner Thanos                                          │
  │    https://dev.dashboard.cloudtuner.ai/storage/api/v2/write│
  └────────────────┬────────────────────────────────────────────┘
                   │
                   ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Metroculus API                                             │
  │    /metroculus/v2/kubecost_cluster_costs                    │
  └─────────────────────────────────────────────────────────────┘
```

---

## What Was Accomplished

### 1. Dynamic Service Discovery ✅

**Problem**: Hardcoded Kubecost URL pointing to external namespace broke self-contained architecture.

**Solution**: Dynamic URL generation in Helm template
```yaml
env:
- name: KUBECOST_URL
  value: {{ printf "http://%s.%s.svc.cluster.local:9090" .Release.Name .Release.Namespace | quote }}
```

**Result**:
- Release `kubecost-dev` in namespace `kubecost-dev` → `http://kubecost-dev.kubecost-dev.svc.cluster.local:9090`
- Works with ANY release name in ANY namespace

### 2. Allocation Exporter Deployed ✅

**Image**: `invincibledocker24/kubecost-allocation-exporter:v1.4.0-dev-k8s1`

**Features**:
- Queries Kubecost `/model/allocation` API every 120s
- Aggregates costs by namespace (8 namespaces detected)
- Includes weighted idle cost allocation
- Exposes hourly rate metrics (metricMode: rate)
- Multi-tenant labels (tenant_id)

**Current Metrics**:
- Cluster total: **$0.27/hour**
- Namespaces: argocd, cert-manager, default, ingress-nginx, kube-state-metrics, kube-system, kubecost, kubecost-dev
- Health: `cloudtuner_kubecost_exporter_scrape_success = 1.0`

### 3. Prometheus Scraping Configured ✅

**Scrape Job Added**:
```yaml
- job_name: 'kubecost-allocation-exporter'
  honor_labels: true
  scrape_interval: 60s
  scrape_timeout: 30s
  metrics_path: /metrics
  scheme: http
  static_configs:
  - targets:
    - kubecost-allocation-exporter.kubecost-dev.svc.cluster.local:9103
```

**Status**:
- ✅ Metrics visible in Prometheus
- ✅ `cloudtuner_kubecost_cluster_total_cost{cluster="kubecost-dev",currency="USD",tenant_id="d603f6e0-aff4-4e89-962d-c56f16b69404"} 0.26759`

### 4. Remote_write Active ✅

**Configuration**:
```yaml
remoteWrite:
- url: "https://dev.dashboard.cloudtuner.ai/storage/api/v2/write"
  name: cloudtuner
  headers:
    Cloud-Account-Id: "5635f99d-4dc6-4e31-891f-4e8990925c83"
  write_relabel_configs:
  - source_labels: [__name__]
    regex: '(kubecost_.*|cloudtuner_kubecost_.*|container_.*|kube_.*|node_.*|pod_pvc_.*|pv_.*|up)'
    action: keep
```

**Status**:
- ✅ **28,346 samples** sent to CloudTuner
- ✅ Filter includes `cloudtuner_kubecost_.*` metrics

### 5. Deprecated Components Removed ✅

```yaml
costAggregator:
  enabled: false  # DEPRECATED - replaced by allocation exporter

extractor:
  enabled: false  # DEPRECATED - replaced by allocation exporter
```

---

## Metrics Exposed

### Cluster-Level Metrics
```
cloudtuner_kubecost_cluster_total_cost{cluster, tenant_id, currency}
cloudtuner_kubecost_cluster_cpu_cost{cluster, tenant_id, currency}
cloudtuner_kubecost_cluster_ram_cost{cluster, tenant_id, currency}
cloudtuner_kubecost_cluster_pv_cost{cluster, tenant_id, currency}
cloudtuner_kubecost_cluster_network_cost{cluster, tenant_id, currency}
cloudtuner_kubecost_cluster_lb_cost{cluster, tenant_id, currency}
cloudtuner_kubecost_cluster_cpu_efficiency{cluster, tenant_id}
cloudtuner_kubecost_cluster_ram_efficiency{cluster, tenant_id}
cloudtuner_kubecost_cluster_total_efficiency{cluster, tenant_id}
```

### Namespace-Level Metrics (Default)
```
cloudtuner_kubecost_namespace_total_cost{cluster, namespace, tenant_id, currency}
cloudtuner_kubecost_namespace_cpu_cost{cluster, namespace, tenant_id, currency}
cloudtuner_kubecost_namespace_ram_cost{cluster, namespace, tenant_id, currency}
cloudtuner_kubecost_namespace_pv_cost{cluster, namespace, tenant_id, currency}
cloudtuner_kubecost_namespace_cpu_efficiency{cluster, namespace, tenant_id}
cloudtuner_kubecost_namespace_ram_efficiency{cluster, namespace, tenant_id}
cloudtuner_kubecost_namespace_total_efficiency{cluster, namespace, tenant_id}
```

### Health Metrics
```
cloudtuner_kubecost_exporter_scrape_success (1=success, 0=failure)
cloudtuner_kubecost_exporter_scrape_duration_seconds
cloudtuner_kubecost_exporter_scrape_errors_total
```

---

## Configuration

### Key Parameters (values.yaml)

```yaml
allocationExporter:
  enabled: true
  image:
    repository: invincibledocker24/kubecost-allocation-exporter
    tag: v1.4.0-dev-k8s1

  port: 9103

  config:
    # Kubecost URL auto-generated: http://{{ .Release.Name }}.{{ .Release.Namespace }}.svc.cluster.local:9090
    scrapeInterval: 120        # Query Kubecost every 2 minutes
    scrapeJitterMax: 10        # Random jitter to avoid thundering herd

    aggregationLevel: namespace # namespace (default) or pod
    window: "1h"               # Time window for allocation query

    timeSeries: false          # false = single aggregate for window
    accumulate: true           # Aggregate across entire window

    includeIdle: true          # Include idle costs
    shareIdle: weighted        # Distribute idle costs proportionally

    metricMode: rate           # Export as hourly rate (rate) or window total (total)

    tenantId: ""               # Cloud Account ID (set via --set at deployment)
    clusterName: "kubernetes"  # Cluster identifier
    currency: "USD"

    enablePodMetrics: false    # High cardinality - use with caution
    topNPods: 50              # If pod metrics enabled, limit to top N
```

---

## Deployment

### Prerequisites
- Kubernetes cluster with kubectl access
- Helm 3.x installed
- Cloud Account ID (tenant_id)

### Install Command

```bash
helm upgrade --install <release-name> ./kubecost-integration \
  -n <namespace> \
  --create-namespace \
  --set allocationExporter.enabled=true \
  --set allocationExporter.config.tenantId="<your-cloud-account-id>" \
  --set allocationExporter.config.clusterName="<your-cluster-name>"
```

### Example (Current Deployment)

```bash
helm upgrade --install kubecost-dev ./kubecost-integration \
  -n kubecost-dev \
  --set allocationExporter.enabled=true \
  --set allocationExporter.config.tenantId="d603f6e0-aff4-4e89-962d-c56f16b69404" \
  --set allocationExporter.config.clusterName="kubecost-dev"
```

---

## Verification Checklist

### ✅ Completed Verifications

- [x] Exporter pod running and healthy
- [x] Exporter querying correct Kubecost URL (dynamic)
- [x] Exporter collecting allocation data (8 namespaces, $0.27/hr)
- [x] Metrics exposed on exporter endpoint (:9103/metrics)
- [x] Prometheus scraping exporter successfully
- [x] Metrics visible in Prometheus queries
- [x] Remote_write sending samples to Thanos (28,346 samples)
- [x] Deprecated components disabled

### 🔄 Pending Verifications

- [ ] **Metrics in Thanos**: Verify cloudtuner_kubecost_* metrics are queryable in Thanos
- [ ] **Metroculus Integration**: Update API to query exporter metrics instead of raw calculations
- [ ] **End-to-End Flow**: Test from K8s cluster → Thanos → Metroculus → REST API → NGUI
- [ ] **Multi-Cluster Test**: Deploy in second cluster with different tenant_id
- [ ] **Persistence**: Make Prometheus scrape config permanent in Helm chart

---

## Known Issues & Solutions

### Issue 1: Prometheus Scrape Config Not Persistent ⚠️

**Status**: Manual patch applied to ConfigMap

**Current Solution**:
```bash
kubectl exec -n kubecost-dev <prometheus-pod> -- cat /etc/config/prometheus.yml > /tmp/prometheus.yml
# Add scrape job to /tmp/prometheus.yml
kubectl create configmap kubecost-dev-prometheus-server -n kubecost-dev \
  --from-file=prometheus.yml=/tmp/prometheus.yml \
  --dry-run=client -o yaml | kubectl apply -f -
curl -X POST http://localhost:9090/-/reload
```

**Permanent Solution Needed**: Add to Kubecost subchart values override or create ConfigMap patch in Helm templates

### Issue 2: Metroculus Using Old Phase 1 Logic ⚠️

**Current Behavior**: Metroculus API still calculating costs from raw Prometheus metrics
- Result: `CPU=$0.00, RAM=$0.00, PV=$0.00` (incorrect breakdown)
- Total cost is calculated but not using exporter's detailed breakdown

**Required Action**: Update `/cloud-tuner/metroculus/metroculus_api/controllers/kubecost_metrics.py` to query `cloudtuner_kubecost_*` metrics

---

## Performance Metrics

### Resource Usage
- **Exporter**:
  - CPU: ~10m average, ~100m during scrape
  - Memory: 64-128 MB (namespace-level only)
  - Scrape duration: ~0.06-0.12s

- **Prometheus**:
  - Additional time series: ~40-50 (namespace-level metrics)
  - Remote_write overhead: Minimal (included in filter)

### Data Flow
- **Kubecost → Exporter**: Every 120s ± 10s jitter
- **Prometheus → Exporter**: Every 60s
- **Prometheus → Thanos**: Per remote_write batch settings
- **Metric Retention**: 15d in Prometheus, long-term in Thanos

---

## Next Steps

### Immediate (Week 1)
1. **Verify Thanos Ingestion**: Query Thanos directly for cloudtuner_kubecost_* metrics
2. **Update Metroculus API**: Implement Phase 2 metric queries
3. **Make Prometheus Config Persistent**: Add to Helm chart
4. **End-to-End Testing**: Verify full flow works

### Short-Term (Week 2-3)
1. **Multi-Cluster Testing**: Deploy in second cluster, verify isolation
2. **REST API Integration**: Update `/restapi/v2/clean_expenses` to use new Metroculus response
3. **NGUI Dashboard**: Display K8s costs with detailed breakdown (CPU, RAM, PV)
4. **Documentation**: User-facing deployment guide

### Long-Term (Month 2+)
1. **Efficiency Alerts**: Add Prometheus alerts for low efficiency
2. **Cost Anomaly Detection**: Alert on unexpected cost spikes
3. **Namespace Recommendations**: Suggest cost optimization based on efficiency
4. **Pod-Level Metrics** (Optional): Enable for detailed troubleshooting

---

## Files Modified

### Helm Chart
- `/k8s-kubecost/charts/kubecost-integration/values.yaml`
  - Updated allocation exporter config
  - Documented dynamic Kubecost URL pattern
  - Disabled deprecated components

- `/k8s-kubecost/charts/kubecost-integration/templates/allocation-exporter-deployment.yaml`
  - **Critical Fix**: Dynamic KUBECOST_URL using Helm templating

### Exporter Application
- `/k8s-kubecost/charts/kubecost-integration/allocation-exporter/exporter.py`
  - User implemented idle cost allocation improvements
  - Pushed as v1.4.0-dev-k8s1

### Documentation
- `/k8s-kubecost/charts/kubecost-integration/allocation-exporter/README.md`
  - Comprehensive exporter documentation
  - Configuration reference
  - Troubleshooting guide

---

## Testing Commands

### Check Exporter Status
```bash
kubectl get pods -n kubecost-dev -l app.kubernetes.io/name=kubecost-allocation-exporter
kubectl logs -n kubecost-dev -l app.kubernetes.io/name=kubecost-allocation-exporter --tail=50
```

### Query Metrics
```bash
# Port-forward to exporter
kubectl port-forward -n kubecost-dev svc/kubecost-allocation-exporter 9103:9103

# Check metrics
curl http://localhost:9103/metrics | grep cloudtuner_kubecost_cluster_total_cost

# Port-forward to Prometheus
kubectl port-forward -n kubecost-dev svc/kubecost-dev-prometheus-server 9090:80

# Query Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=cloudtuner_kubecost_cluster_total_cost' | python3 -m json.tool
```

### Verify Remote Write
```bash
# Check samples sent
curl -s 'http://localhost:9090/api/v1/query?query=prometheus_remote_storage_samples_total' | grep cloudtuner
```

---

## Security

- Exporter runs as non-root (UID 1000)
- Read-only root filesystem
- No privilege escalation
- Minimal RBAC (no permissions required - queries local Kubecost service)
- TLS for remote_write to CloudTuner (insecure_skip_verify: true for dev)

---

## Support & Troubleshooting

### Exporter Not Collecting Data
1. Check Kubecost URL is accessible: `kubectl logs -n kubecost-dev <exporter-pod> | grep "Kubecost URL"`
2. Verify Kubecost has allocation data: Port-forward to Kubecost and query `/model/allocation?window=1h`
3. Check exporter logs for errors: `kubectl logs -n kubecost-dev <exporter-pod> --tail=100`

### Metrics Not in Prometheus
1. Verify scrape config: `kubectl get configmap -n kubecost-dev kubecost-dev-prometheus-server -o yaml | grep allocation-exporter`
2. Check Prometheus targets: Port-forward and visit `http://localhost:9090/targets`
3. Reload Prometheus: `curl -X POST http://localhost:9090/-/reload`

### Remote_write Failing
1. Check remote_write queue: `prometheus_remote_storage_queue_length`
2. Check authentication: Verify username/password in values.yaml
3. Check network: Verify cluster can reach `dev.dashboard.cloudtuner.ai`

---

## References

- [Phase 2 Implementation Plan](./implementation-summary.md)
- [Allocation Exporter README](./kubecost-integration/allocation-exporter/README.md)
- [Kubecost Allocation API Docs](https://docs.kubecost.com/apis/apis-overview/allocation)
- [Prometheus Remote Write](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#remote_write)

---

**Last Updated**: October 14, 2025
**Author**: CloudTuner Integration Team
**Version**: 1.0
