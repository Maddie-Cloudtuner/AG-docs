
# Kubecost → CloudTuner Phase-2 Integration — Consolidated Follow-up (Single Markdown)

**Environment:** `kubecost-dev`  
**Owner:** Balaji Rao / Platform FinOps  
**Date (latest update):** 2025-10-14 IST

---

## TL;DR (because time is precious)
Phase-2 (allocation exporter v1.4.0-dev-k8s1) is deployed in `kubecost-dev` with unified tenancy and dynamic service discovery. Prometheus is scraping exporter metrics; remote_write sends metrics to CloudTuner Thanos. Metroculus was updated to prefer Phase-2 metrics and fallback to Phase-1, but it fell back initially due to either zero-valued metrics right after restart or tenant_id mismatch. The deployment was cleaned and reconfigured to use tenant `bc55eb8c-5db2-4c32-b976-2df0edb0619a` and credentials `kubecost / kubecost@123`. Prometheus scrape job was temporarily applied; make it persistent in Helm. Metroculus detection logic should be relaxed to treat presence of samples (even 0) as Phase-2.

---

## 1. Chronological Analysis (combined)
- Exporter version: **v1.4.0-dev-k8s1** (idle cost allocation improvements).
- Exporter initially started and reported $0 costs because Kubecost had just restarted and hadn’t aggregated allocation data yet.
- Hardcoded Kubecost URL corrected to Helm templating:
  ```yaml
  value: {{ printf "http://%s.%s.svc.cluster.local:9090" .Release.Name .Release.Namespace | quote }}
  ```
- Found tenant_id mismatches across remote_write header and exporter config (multiple tenant IDs seen). Root cause for Metroculus not seeing Phase-2 metrics.
- Metroculus update: `_get_cluster_costs_from_exporter()` added; `get_cluster_costs()` updated to try Phase-2 first, fallback to Phase-1 with logs indicating which phase is used.
- User requested manual deployments (no shell scripts).
- User provided final credentials/tenant and requested a clean redeploy: `tenant = bc55eb8c-5db2-4c32-b976-2df0edb0619a`, username `kubecost`, password `kubecost@123`.
- Performed cleanup: uninstalled release, deleted namespace, updated values.yaml in 3 places, reinstalled, updated Prometheus ConfigMap with exporter scrape job, confirmed pods running.

---

## 2. Files & Important Locations
- `charts/kubecost-integration/values.yaml` — main Helm values updated (auth, remote_write, allocationExporter).
- `charts/kubecost-integration/templates/allocation-exporter-deployment.yaml` — exporter deployment, templated `KUBECOST_URL`.
- `/tmp/prometheus-fresh.yml` — temporary Prometheus config used to add exporter scrape job.
- `metroculus/metroculus_api/controllers/kubecost_metrics.py` — added Phase-2 reader (`_get_cluster_costs_from_exporter`) and fallback logic.
- `verify-phase2.sh` (existing artifact) — automated verification script (if still used; user preferred manual deployment, but script useful for CI).

---

## 3. Unified Configuration (authoritative snippets)
**Use Secrets; do not keep creds in plaintext values.yaml. The snippet below is for reference only.**

```yaml
# central block (values.yaml)
cloudtuner:
  auth:
    username: kubecost
    password: kubecost@123

prometheus:
  remoteWrite:
    - name: cloudtuner
      url: https://dev.dashboard.cloudtuner.ai/storage/api/v2/write
      headers:
        Cloud-Account-Id: "bc55eb8c-5db2-4c32-b976-2df0edb0619a"
      basic_auth:
        username: kubecost
        password: kubecost@123

allocationExporter:
  tenantId: "bc55eb8c-5db2-4c32-b976-2df0edb0619a"
  clusterName: "kubecost-dev-fresh"
```

Recommended: move `username/password` into a Kubernetes Secret and reference via `basicAuthFromSecret` in Prometheus config and exporter templates.

---

## 4. Metroculus Phase-2 Reader (key logic)
**New function added** `_get_cluster_costs_from_exporter()`:

- Queries Thanos for `cloudtuner_kubecost_*` metrics with tenant label.
- Converts hourly rates (exporter exports rates) into total cost using duration.
- Collects efficiency metrics and returns costs dict.
- If **no samples** found for any metric, returns `None` so Metroculus can fallback to Phase-1.

**Current detection caveat:** code treats `value > 0` as present; this leads to fallback after restarts when exporter metrics exist but are zero. Change to `is not None` presence check (see "Fixes" section).

---

## 5. Verification Commands (copy-paste friendly)

**Exporter logs**
```bash
kubectl -n kubecost-dev logs deploy/kubecost-allocation-exporter --tail=100 -f
# Expect lines:
# Tenant ID: bc55eb8c-5db2-4c32-b976-2df0edb0619a
# Exported cluster-level metrics: total_cost=$X.XX (mode=rate)
```

**Prometheus target check**
```bash
kubectl -n kubecost-dev port-forward deploy/kubecost-dev-prometheus-server 9090:9090 &
curl -s 'http://127.0.0.1:9090/api/v1/targets' | jq '.data.activeTargets[] | select(.labels.job=="kubecost-allocation-exporter") | {health:.health, lastError:.lastError}'
```

**Thanos query**
```bash
kubectl -n default port-forward svc/thanos-query 9091:10902 &
curl -s 'http://127.0.0.1:9091/api/v1/query?query=cloudtuner_kubecost_cluster_total_cost{tenant_id="bc55eb8c-5db2-4c32-b976-2df0edb0619a"}'
```

**Metroculus logs**
```bash
kubectl -n default logs deploy/metroculusapi --tail=200 | egrep 'Using Phase 2 exporter metrics|Using Phase 1 metrics'
```

---

## 6. Problems Found & Fixes Applied / Proposed

### Problem A: Tenant ID mismatch
- **Symptoms:** Metrics present in Thanos but Metroculus queried a different tenant_id.
- **Fix applied:** Updated `values.yaml` for remote_write header and exporter tenantId to `bc55eb8c-5db2-4c32-b976-2df0edb0619a`.
- **Verify:** Query Thanos for the tenant_id above.

### Problem B: Strict Phase-2 detection logic
- **Symptoms:** Metroculus falls back to Phase-1 even when exporter metrics exist (but are zero) after restarts.
- **Proposed Fix:** Relax detection to check for presence of samples rather than `value > 0`. Example:
```python
# Old: if value is not None and value > 0: has_data = True
# New: if value is not None: has_data = True
```
- **Optional:** Add a small grace period after exporter pod start (e.g., 3–5 minutes) to allow warm-up.

### Problem C: Prometheus scrape job persistence
- **Symptoms:** Manual patch of Prometheus ConfigMap; not persisted in chart (lost on upgrade).
- **Fix (proposed):** Add `extraScrapeConfigs` or `additionalScrapeConfigs` in Helm values and inject into Prometheus config template (see Helm snippet below).

### Problem D: Plaintext creds in values.yaml
- **Action:** Create Kubernetes Secret and reference it in chart templates.

### Problem E: Duplicate port name warnings
- **Fix:** Rename duplicate ports in pod spec to unique values; update readiness/liveness probes if they use port names.

---

## 7. Helm & Chart Recommendations (what to change)
1. **Secrets**
   - Create secret:
     ```bash
     kubectl -n kubecost-dev create secret generic cloudtuner-basic-auth \
       --from-literal=username='kubecost' \
       --from-literal=password='kubecost@123'
     ```
   - Reference via `basicAuthFromSecret` in Prometheus remote_write.

2. **Prometheus scrape config in Helm**
   - `values.yaml` (under `kubecost.prometheus.extraScrapeConfigs`):
     ```yaml
     kubecost:
       prometheus:
         extraScrapeConfigs: |
           - job_name: 'kubecost-allocation-exporter'
             honor_labels: true
             scrape_interval: 60s
             scrape_timeout: 30s
             metrics_path: /metrics
             scheme: http
             kubernetes_sd_configs:
             - role: endpoints
             relabel_configs:
             - source_labels: [__meta_kubernetes_service_label_app_kubernetes_io_name]
               action: keep
               regex: kubecost-allocation-exporter
             - source_labels: [__meta_kubernetes_endpoint_port_name]
               action: keep
               regex: metrics
     ```
   - This uses Kubernetes SD to discover the exporter service by label and scrape the `metrics` port.

3. **Cluster name**
   - Choose and enforce one `clusterName` value across the chart and exporter labels (recommended: `kubecost-dev-fresh`).

4. **Port names**
   - Ensure all containers have uniquely named ports.

---

## 8. Operational SOP (deployment & rollback)
**Deploy fresh**
```bash
kubectl create namespace kubecost-dev
helm upgrade --install kubecost-dev ./kubecost-integration -n kubecost-dev
kubectl -n kubecost-dev get pods
```

**Restart services when needed**
```bash
kubectl -n kubecost-dev rollout restart deploy/kubecost-allocation-exporter
kubectl -n kubecost-dev rollout restart deploy/kubecost-dev-prometheus-server
```

**Rollback**
```bash
helm -n kubecost-dev history kubecost-dev
helm -n kubecost-dev rollback kubecost-dev <REVISION>
```

---

## 9. Pending Tasks (short actionable list)
1. Patch Metroculus detection logic (`is not None` presence check).  
2. Persist Prometheus scrape job in Helm templates.  
3. Create Secret for credentials; update chart to use `basicAuthFromSecret`.  
4. Standardize `clusterName` across chart and exporter.  
5. Rename duplicate ports to remove warnings.  
6. Add lightweight CI job to run verification checks after deploy (optional).

---

## 10. Change Log
- **2025-10-14**: Unified tenant config to `bc55eb8c-5db2-4c32-b976-2df0edb0619a`; redeployed `kubecost-dev` release; added temporary Prometheus scrape job; updated Metroculus to prefer Phase-2 and fallback to Phase-1.
- **Prior**: Fixed templated Kubecost URL; resolved initial mismatch in exporter URL and namespace; initial Phase-2 implementation added.

---

## 11. Appendix (cheat sheet)

**PromQL quick checks**
```promql
cloudtuner_kubecost_cluster_total_cost{tenant_id="bc55eb8c-5db2-4c32-b976-2df0edb0619a"}
cloudtuner_kubecost_cluster_cpu_cost{tenant_id="bc55eb8c-5db2-4c32-b976-2df0edb0619a"}
cloudtuner_kubecost_cluster_ram_efficiency{tenant_id="bc55eb8c-5db2-4c32-b976-2df0edb0619a"}
```

**Useful verification commands**
```bash
# Prometheus targets
curl 'http://localhost:9090/api/v1/targets'

# Thanos quick query
curl 'http://localhost:9091/api/v1/query?query=cloudtuner_kubecost_cluster_total_cost{tenant_id="..."}'

# Metroculus logs (phase check)
kubectl -n default logs deploy/metroculusapi --tail=200 | egrep 'Using Phase 2 exporter metrics|Using Phase 1 metrics'
```

---

## 12. How to get this into Canvas (because /canvas was requested)
Canvas API/tool here is currently disabled/unavailable. I created a single Markdown file with this entire consolidated doc for you to upload or paste into Canvas.

**Download link:** see the file attached below.

---

## Endnote (no fluff)
This single document collects everything you dumped into a single canonical source-of-truth for Phase-2. Paste it into Canvas, pin it to the doc you use for deployments, and it’ll stop being a “guess what broke today” situation. If you want, I’ll also generate the Helm patch snippets and Metroculus PR-ready diff next — but you already banned deployment scripts, so I’ll keep it manual unless you wave the scripting flag back in.
