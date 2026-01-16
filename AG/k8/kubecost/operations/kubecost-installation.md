# k8s-kubecost Helm Installation (Development Environment)

This guide walks through installing the Kubecost integration chart that lives in `k8s-kubecost/charts/kubecost-integration/`. It assumes you are running against a dev/test CloudTuner stack and want to exercise the Kubecost allocation exporter plus remote-write path.

---

## 1. Before You Begin

| Requirement | Command | Notes |
| --- | --- | --- |
| Kubernetes ≥ 1.20 | `kubectl version --short` | Confirm you are pointing at the right cluster/context. |
| Helm ≥ 3.0 | `helm version --short` | Helm 2 is not supported. |
| CloudTuner backplane | `kubectl get pods -n default | grep -E "(restapi|metroculus|diproxy)"` | REST API, Metroculus, InfluxDB, ClickHouse should already exist. |
| Kubecost secret material | N/A | Collect Cloud Account ID, cluster secret, remote-write credentials. |
| Storage endpoints | `kubectl get svc -n default influxdb clickhouse` | Values file ships with defaults (`influxdb.default`, `clickhouse.default`). Adjust if your stack differs. |

> Tip: run `kubectl config current-context` and `kubectl get ns kubecost-dev || true` before touching Helm so you don’t deploy in the wrong cluster/namespace.

---

## 2. TL;DR Installation

```bash
cd /Users/balaji/source/code/cloudtuner/cloudtuner-dev-helm/k8s-kubecost

helm upgrade --install kubecost-dev ./charts/kubecost-integration \
  -n kubecost-dev \
  --create-namespace \
  --set global.imageTag="v1.3.0" \
  --set kubecost.prometheus.server.remoteWrite[0].headers.Cloud-Account-Id="bc55eb8c-5db2-4c32-b976-2df0edb0619a" \
  --wait --timeout 10m
```

Use the detailed steps below if you need linting, dry runs, or custom overrides.

---

## 3. Detailed Installation Steps

1. **Navigate to the chart**
   ```bash
   cd /Users/balaji/source/code/cloudtuner/cloudtuner-dev-helm/k8s-kubecost
   ```

2. **Lint & dry-run**
   ```bash
   helm lint ./charts/kubecost-integration

   helm upgrade --install kubecost-dev ./charts/kubecost-integration \
     -n kubecost-dev \
     --create-namespace \
     --dry-run --debug
   ```

3. **Install / upgrade**
   ```bash
   helm upgrade --install kubecost-dev ./charts/kubecost-integration \
     -n kubecost-dev \
     --create-namespace \
     --wait --timeout 10m
   ```

4. **Verify core pods**
   ```bash
   kubectl get pods -n kubecost-dev
   kubectl get svc -n kubecost-dev
   kubectl get cronjob -n kubecost-dev
   ```

5. **Confirm metrics flow**
   ```bash
   kubectl logs -n default -l app=diproxy --tail=50 | grep -E "POST.+/write"
   ```

---

## 4. Custom Configuration Snippets

### 4.1 Local `values` file

```bash
cat > /tmp/kubecost-values.yaml <<'EOF'
global:
  imageTag: v1.4.0-dev

kubecost:
  prometheus:
    server:
      remoteWrite:
        - url: "https://dev.dashboard.cloudtuner.ai/storage/api/v2/write"
          name: cloudtuner
          headers:
            Cloud-Account-Id: "REPLACE_WITH_ACCOUNT_ID"
          basic_auth:
            username: kubecost
            password: kubecost@123
          tls_config:
            insecure_skip_verify: true

allocationExporter:
  enabled: true
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
EOF

helm upgrade --install kubecost-dev ./charts/kubecost-integration \
  -n kubecost-dev \
  -f /tmp/kubecost-values.yaml \
  --create-namespace
```

### 4.2 Rapid iteration flags

```bash
helm upgrade --install kubecost-dev ./charts/kubecost-integration \
  -n kubecost-dev \
  --set extractor.schedule.allocation="*/5 * * * *" \
  --set costAggregator.schedule="*/5 * * * *" \
  --set global.imageTag="latest" \
  --create-namespace
```

---

## 5. Post-Install Validation

| Check | Command | Expectation |
| --- | --- | --- |
| Pods healthy | `kubectl get pods -n kubecost-dev` | `Ready` column should be `1/1`. |
| Allocation exporter scraping | `kubectl logs -n kubecost-dev -l app=kubecost-allocation-exporter --tail=50` | Look for `Successfully scraped allocation window`. |
| Remote write | `kubectl logs -n default -l app=diproxy --tail=50 | grep cloudtuner_kubecost` | 2xx responses. |
| REST API data | `curl -H "Secret: $CLUSTER_SECRET" http://localhost:8969/metroculus/v2/kubecost_cluster_costs?...` | Returns JSON with cost summary. |

Optional ClickHouse verification:
```bash
kubectl exec -n default clickhouse-0 -- \
  clickhouse-client -q "SELECT count() FROM expenses WHERE k8s_namespace IS NOT NULL;"
```

---

## 6. Troubleshooting

### ImagePullBackOff
```bash
kubectl describe pod -n kubecost-dev <pod-name> | grep -A5 "Events"
# Fix image registry / tag in values, then run helm upgrade.
```

### RBAC / Forbidden errors
```bash
kubectl auth can-i get pods \
  --as=system:serviceaccount:kubecost-dev:kubecost-integration
kubectl get clusterrolebinding kubecost-integration-reader
```

### Prometheus not scraping exporter
```bash
kubectl get pod -n kubecost-dev -l app.kubernetes.io/name=kubecost-allocation-exporter -o jsonpath='{.items[*].status.podIP}'
kubectl -n kubecost-dev port-forward svc/kubecost-allocation-exporter 19090:19090
curl http://localhost:19090/metrics | head
```

### Remote write filtered out
The regex at `kubecost.prometheus.server.remoteWrite[].write_relabel_configs[0].regex` keeps only `kubecost_*`/`cloudtuner_kubecost_*`/`container_*`/`node_*` series. Broaden it if you need more metrics.

---

## 7. Day-2 Operations

### Upgrade
```bash
helm upgrade kubecost-dev ./charts/kubecost-integration -n kubecost-dev
helm status kubecost-dev -n kubecost-dev
```

### Uninstall / Cleanup
```bash
helm uninstall kubecost-dev -n kubecost-dev
kubectl delete namespace kubecost-dev
kubectl delete clusterrolebinding kubecost-integration-reader
```

### Quick Reference

| Component | Purpose | Default cadence |
| --- | --- | --- |
| allocation-exporter | Pulls Kubecost allocation API and exposes metrics | 60s scrape |
| extractor (legacy) | Batch export to ClickHouse | Disabled by default |
| cost-aggregator (legacy) | Rollups for ClickHouse | Disabled by default |
| metrics-processor | Kubecost cost-model | Continuous |

| Path | Description |
| --- | --- |
| `charts/kubecost-integration/values.yaml` | All override-able values. |
| `charts/kubecost-integration/templates/` | Deployments, CronJobs, RBAC. |
| `docs/kubecost/phase-2/metroculus-deployment.md` | How this ties into Metroculus/REST. |

---

Remember: this chart is for **development and testing**. Production customers consume the supported `optscale-k8s-cost` chart once the Phase 3/4 work is promoted. Keep your overrides checked into a secure location so teammates can recreate your environment quickly.
