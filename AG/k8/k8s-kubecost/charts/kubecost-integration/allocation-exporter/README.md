# Kubecost Allocation Exporter for CloudTuner

## Overview

The Kubecost Allocation Exporter is an in-cluster service that queries the Kubecost Allocation API and exposes allocation costs as Prometheus metrics. These metrics are then scraped by Prometheus and sent to CloudTuner's Thanos via remote_write.

This approach enables CloudTuner to receive allocation cost data (CPU, RAM, PV costs and efficiency metrics) while maintaining the remote_write-only architecture required for multi-cluster SaaS deployments.

## Architecture

```
Customer Cluster:
  Kubecost API → Allocation Exporter → Prometheus → remote_write → CloudTuner Thanos
```

**Key Features:**
- Queries Kubecost `/model/allocation` API locally (cluster-internal)
- Exposes low-cardinality Prometheus metrics with `cloudtuner_kubecost_*` prefix
- Namespace-level aggregation by default (pod-level optional)
- Includes efficiency metrics (CPU, RAM, total)
- Configurable scrape interval and time window
- Multi-tenant labels for isolation

## Metrics Exposed

### Namespace-Level Metrics (Default)

- `cloudtuner_kubecost_namespace_total_cost{cluster, namespace, tenant_id, currency}`
- `cloudtuner_kubecost_namespace_cpu_cost{cluster, namespace, tenant_id, currency}`
- `cloudtuner_kubecost_namespace_ram_cost{cluster, namespace, tenant_id, currency}`
- `cloudtuner_kubecost_namespace_pv_cost{cluster, namespace, tenant_id, currency}`
- `cloudtuner_kubecost_namespace_network_cost{cluster, namespace, tenant_id, currency}`
- `cloudtuner_kubecost_namespace_lb_cost{cluster, namespace, tenant_id, currency}`
- `cloudtuner_kubecost_namespace_cpu_efficiency{cluster, namespace, tenant_id}`
- `cloudtuner_kubecost_namespace_ram_efficiency{cluster, namespace, tenant_id}`
- `cloudtuner_kubecost_namespace_total_efficiency{cluster, namespace, tenant_id}`

### Cluster-Level Metrics

- `cloudtuner_kubecost_cluster_total_cost{cluster, tenant_id, currency}`
- `cloudtuner_kubecost_cluster_cpu_cost{cluster, tenant_id, currency}`
- `cloudtuner_kubecost_cluster_ram_cost{cluster, tenant_id, currency}`
- `cloudtuner_kubecost_cluster_pv_cost{cluster, tenant_id, currency}`
- `cloudtuner_kubecost_cluster_network_cost{cluster, tenant_id, currency}`
- `cloudtuner_kubecost_cluster_lb_cost{cluster, tenant_id, currency}`
- `cloudtuner_kubecost_cluster_cpu_efficiency{cluster, tenant_id}`
- `cloudtuner_kubecost_cluster_ram_efficiency{cluster, tenant_id}`
- `cloudtuner_kubecost_cluster_total_efficiency{cluster, tenant_id}`

### Pod-Level Metrics (Optional, High Cardinality)

When `enablePodMetrics: true`:

- `cloudtuner_kubecost_pod_total_cost{cluster, namespace, pod, tenant_id, currency}`
- `cloudtuner_kubecost_pod_cpu_cost{cluster, namespace, pod, tenant_id, currency}`
- `cloudtuner_kubecost_pod_ram_cost{cluster, namespace, pod, tenant_id, currency}`

**Note:** Pod metrics are limited to top N pods by cost (default: 50) to control cardinality.

### Health Metrics

- `cloudtuner_kubecost_exporter_scrape_duration_seconds` - Duration of last scrape
- `cloudtuner_kubecost_exporter_scrape_success` - 1 if last scrape succeeded, 0 otherwise
- `cloudtuner_kubecost_exporter_scrape_errors_total` - Total number of scrape errors

## Building the Docker Image

```bash
cd /Users/balaji/source/code/cloudtuner/cloudtuner-dev-helm/k8s-kubecost/charts/kubecost-integration/allocation-exporter

# Build the image
docker build -t invincibledocker24/kubecost-allocation-exporter:v1.0.0 .

# Push to registry
docker push invincibledocker24/kubecost-allocation-exporter:v1.0.0
```

## Configuration

The exporter is configured via Helm values in `values.yaml`:

```yaml
allocationExporter:
  enabled: true
  name: kubecost-allocation-exporter
  replicaCount: 1

  image:
    repository: invincibledocker24/kubecost-allocation-exporter
    tag: v1.0.0

  port: 9103

  config:
    # Kubecost URL (cluster-local service)
    kubecostUrl: "http://kubecost-cost-analyzer.kubecost.svc.cluster.local:9090"

    # Scrape interval in seconds (how often to query Kubecost)
    scrapeInterval: 120
    # Max random jitter added to scrape interval (seconds)
    scrapeJitterMax: 10

    # Aggregation level: namespace or pod
    aggregationLevel: namespace

    # Time window for allocation query (1h, 24h, 7d, etc.)
    window: "1h"

    # Control shape of data from Kubecost
    timeSeries: false        # false = single aggregate for window
    step: "1h"              # only used if timeSeries=true
    accumulate: true         # true = aggregate across entire window

    # Idle handling
    includeIdle: true
    shareIdle: weighted      # none|even|weighted

    # Metric output semantics
    # - rate: exporter converts window totals to hourly rate (recommended)
    # - total: exporter emits window totals as-is
    metricMode: rate

    # Tenant ID (Cloud Account ID for multi-tenancy)
    tenantId: ""

    # Cluster name (used in metric labels)
    clusterName: "kubernetes"

    # Currency for cost metrics
    currency: "USD"

    # Enable pod-level metrics (use with caution - high cardinality)
    enablePodMetrics: false

    # If pod metrics enabled, limit to top N pods by cost
    topNPods: 50
```

## Deployment

The exporter is deployed automatically when the `kubecost-integration` Helm chart is installed with `allocationExporter.enabled: true`.

```bash
# Install or upgrade the chart
helm upgrade --install kubecost-integration ./k8s-kubecost/charts/kubecost-integration \
  --set allocationExporter.enabled=true \
  --set allocationExporter.config.tenantId="<your-cloud-account-id>" \
  --set allocationExporter.config.clusterName="<your-cluster-name>"
```

## Verification

### 1. Check Exporter Pod Status

```bash
kubectl get pods -l app.kubernetes.io/name=kubecost-allocation-exporter
```

### 2. Check Exporter Logs

```bash
kubectl logs -l app.kubernetes.io/name=kubecost-allocation-exporter --tail=50
```

### 3. Check Metrics Endpoint

```bash
kubectl port-forward svc/kubecost-allocation-exporter 9103:9103
curl http://localhost:9103/metrics | grep cloudtuner_kubecost

## Semantics

- By default (`metricMode: rate`), costs are exported as hourly gauges derived from the selected `window`.
- If you need exact window totals, set `metricMode: total`.
- `includeIdle` and `shareIdle` control whether/how idle cost is distributed across groups to keep cluster and namespace totals aligned.
```

### 4. Verify Prometheus Scraping

```bash
# Check Prometheus targets
kubectl port-forward -n kubecost svc/kubecost-prometheus-server 9090:80
# Open http://localhost:9090/targets
# Look for kubecost-allocation-exporter target
```

### 5. Verify Metrics in Thanos

```bash
# Query Thanos for exporter metrics
curl "http://thanos-query.default.svc:9090/api/v1/label/__name__/values" | grep cloudtuner_kubecost
```

## Troubleshooting

### Exporter Pod Not Starting

Check pod events:
```bash
kubectl describe pod -l app.kubernetes.io/name=kubecost-allocation-exporter
```

### No Metrics Exposed

1. Check exporter logs for errors
2. Verify Kubecost URL is accessible from the exporter pod:
   ```bash
   kubectl exec -it <exporter-pod> -- wget -O- http://kubecost-cost-analyzer.kubecost.svc.cluster.local:9090/model/allocation?window=1h
   ```

### Metrics Not Appearing in Thanos

1. Check Prometheus is scraping the exporter (see verification step 4)
2. Verify remote_write filter includes `cloudtuner_kubecost_.*` in regex
3. Check Prometheus remote_write queue metrics:
   ```bash
   # On Prometheus
   prometheus_remote_storage_samples_total{url=~".*cloudtuner.*"}
   ```

### High Memory Usage

If pod metrics are enabled and memory usage is high:
1. Reduce `topNPods` value
2. Consider disabling pod metrics: `enablePodMetrics: false`
3. Increase scrape interval: `scrapeInterval: 300` (5 minutes)

## Dependencies

- Python 3.9+
- prometheus-client==0.19.0
- requests==2.31.0

## Security Considerations

- The exporter runs as non-root user (UID 1000)
- Read-only root filesystem
- No privilege escalation
- Only requires network access to Kubecost service (no RBAC permissions needed)

## Performance

- Default scrape interval: 120 seconds (2 minutes)
- Typical memory usage: 64-128 MB (namespace-level only)
- Memory with pod metrics: 128-256 MB (depends on pod count)
- CPU usage: ~10m average, ~100m during scrape

## References

- [Kubecost Allocation API Documentation](https://docs.kubecost.com/apis/apis-overview/allocation)
- [CloudTuner Kubecost Integration Plan](../../../../docs/kubecost/analysis/metrics-analysis-notes.md)
- [Phase 2 Implementation Summary](../../../../docs/kubecost/phase-2/implementation-summary.md)
