# Kubecost Metrics Remote‑Write Integration Plan

Date: 2025-10-14
Status: Planning ready for implementation
Scope: Multi‑cluster SaaS, remote_write‑only ingestion into CloudTuner

---

## Executive Summary

- Constraint: Client clusters send metrics to CloudTuner exclusively via Prometheus remote_write. No SaaS→cluster API calls are allowed.
- Today: Infra metrics from Kubecost flow (management, LB, network). Allocation costs (CPU/RAM/PV per namespace/pod) do not, because Kubecost computes them via its internal API rather than Prometheus.
- Plan: Keep infra metrics as-is (Phase 1). Add an in-cluster Allocation Exporter that calls Kubecost locally and exposes low-cardinality Prometheus metrics for allocation and efficiencies, which are then remote_written to CloudTuner (Phase 2). Provide a PromQL fallback for partial coverage if needed.

Outcomes
- Phase 1: Cluster-level infra costs and visibility are live and accurate.
- Phase 2: Allocation costs/efficiencies are available via metrics only, respecting remote_write-only architecture and multi-tenant labeling.

---

## Current Architecture & Constraints

Data flow (target):
Kubecost → Prometheus (scrape) → remote_write → CloudTuner Thanos → Metroculus → Storage/FE

Constraints
- Single egress path: Prometheus remote_write from customer clusters.
- No cross-cluster HTTP calls from CloudTuner SaaS to Kubecost.
- Multi-tenant isolation required (tenant label on every series).

Notes
- Dev has an Ingress for Kubecost; production SaaS must not rely on it.
- Existing helm chart `k8s-kubecost` provides integration points (remote_write filters, additional jobs).

---

## Metrics Inventory (What We Have vs Need)

Working via remote_write
- Infra costs: `kubecost_cluster_management_cost`, `kubecost_load_balancer_cost`, network egress variants.
- Resource/metadata: `container_*`, `kube_*`, `kubecost_cluster_info`.

Partially available or uncertain
- Pricing: `node_cpu_hourly_cost`, `node_ram_hourly_cost`, `node_total_hourly_cost` (often present); `pv_hourly_cost` and `pod_pvc_*` frequently filtered out.

Missing for planning purposes (root cause)
- Allocation costs in dollars (CPU/RAM/PV by namespace/pod) are computed by Kubecost’s internal allocation engine and returned via `/model/allocation`, not emitted as standard Prometheus metrics.

Implication
- Deriving full allocation $ purely from raw metrics is error-prone and incomplete. We need a metricized bridge to Kubecost allocation results while staying remote_write-only.

---

## Proposed Approach

Phase 1 — Keep Infra Costs (Already Working)
- Continue scraping Kubecost `/metrics` and remote_write to CloudTuner.
- Show cluster-level infra costs and network egress in UI; this is valuable on its own.

Phase 2 — Add Allocation Exporter (Remote‑Write Friendly)
- Deploy an in-cluster “Kubecost Allocation Exporter” alongside Kubecost.
  - Queries Kubecost locally: `http://kubecost-cost-analyzer.<ns>.svc:9090/model/allocation`
  - Exposes low-cardinality Prometheus gauges which Prometheus scrapes and remote_writes.
  - Adds tenancy label via the same mechanism used today (external_labels or relabel_configs).

Exporter metric design
- Prefix: `cloudtuner_kubecost_` to distinguish from native Kubecost series.
- Levels (configurable; default namespace):
  - Namespace totals: `cloudtuner_kubecost_namespace_total_cost{cluster, namespace, currency}`
  - Optional breakdowns: `..._cpu_cost`, `..._ram_cost`, `..._pv_cost`, `..._network_cost`, `..._lb_cost`
  - Efficiencies: `cloudtuner_kubecost_namespace_cpu_efficiency`, `..._ram_efficiency`, `..._total_efficiency`
  - Cluster totals: `cloudtuner_kubecost_cluster_total_cost{cluster, currency}`
  - Pod totals (guarded by flag; high cardinality): `cloudtuner_kubecost_pod_total_cost{cluster, namespace, pod, currency}`
- Sampling: scrape every 60–300s; exporter may cache for ~120s to reduce Kubecost load.
- Semantics: export “current hourly rate” as gauges (Prometheus provides time series history).
- Labels: include `tenant_id`/`cloud_account_id` consistently with existing series.

Prometheus configuration deltas
- Add scrape for exporter Service (via annotations or static job).
- Expand remote_write filter to include exporter and PV metrics:
  - From `(kubecost_.*|container_.*|kube_.*|node_.*|up)`
  - To `(kubecost_.*|cloudtuner_kubecost_.*|container_.*|kube_.*|node_.*|pod_pvc_.*|pv_.*|up)`
- Ensure tenancy labels applied uniformly (prefer `external_labels`; otherwise mirror relabel rules on the exporter job).

PromQL fallback (optional bridge)
- If exporter is unavailable, you can approximate $ using pricing + allocations:
  - CPU (namespace hourly): `sum by (namespace) ((container_cpu_allocation) * on (pod, namespace) group_left(node) (kube_pod_info) * on (node) group_left (node_cpu_hourly_cost))`
  - RAM (namespace hourly, GiB): `sum by (namespace) ((container_memory_allocation_bytes/1024/1024/1024) * on (pod, namespace) group_left(node) (kube_pod_info) * on (node) group_left (node_ram_hourly_cost))`
  - PV (rough; needs `pv_hourly_cost` and PVC mapping): `sum by (namespace) (kube_persistentvolumeclaim_resource_requests_storage_bytes/1024/1024/1024 * on (storageclass) group_left (pv_hourly_cost))`
- Caveats: correctness depends on label alignment and availability of `pv_*`; not a full substitute for Kubecost’s allocation engine.

---

## Security and Multi‑Tenancy

- No SaaS→cluster calls. Exporter talks only to in-cluster Kubecost.
- Restrict exporter RBAC to what’s necessary (ideally none beyond network access to Kubecost Service).
- Ensure every exported series includes `tenant_id`/`cloud_account_id` for isolation in Thanos and downstream.
- Consider rate limits/backoff in exporter to avoid load spikes on Kubecost.

---

## Validation Plan

Pre-flight
- Confirm Prometheus sees exporter target as `UP`.
- Verify remote_write regex includes `cloudtuner_kubecost_.*` and PV patterns.

Thanos checks
- List metrics: `.../label/__name__/values` includes `cloudtuner_kubecost_*`.
- Spot queries (add your `tenant_id`):
  - `cloudtuner_kubecost_cluster_total_cost{tenant_id="..."}`
  - `cloudtuner_kubecost_namespace_total_cost{tenant_id="..."}`
- Cross-check: Compare namespace totals vs Kubecost UI for the same window.

Metroculus integration
- Switch to reading allocation from `cloudtuner_kubecost_*` series when present; otherwise use current infra-only path.
- Return consistent shapes to the frontend (document `idle`/`shareIdle` handling and window alignment).

---

## Rollout Plan

1) Phase 1 (Now)
- Keep infra-only metrics. Ensure UI shows cluster-level infra cost and network egress.

2) Phase 2 (Short term)
- Ship Allocation Exporter with helm integration (behind `enabled` flag, default on for supported clusters).
- Update Prometheus scrape + remote_write filter.
- Validate in dev, then promote.

3) Phase 3 (Refinements)
- Enable namespace-level by default; gate pod-level behind value flag to control cardinality.
- Add budget/alerts on `cloudtuner_kubecost_*` series as needed.

---

## Helm Integration Checklist

Values (suggested)
- `kubecostExporter.enabled: true|false`
- `kubecostExporter.image.repository: ghcr.io/cloudtuner/kubecost-allocation-exporter`
- `kubecostExporter.image.tag: <version>`
- `kubecostExporter.port: 9103`
- `kubecostExporter.kubecostUrl: http://kubecost-cost-analyzer.kubecost.svc.cluster.local:9090`
- `kubecostExporter.level: namespace|pod` (default `namespace`)
- `kubecostExporter.scrape.annotations: {prometheus.io/scrape: "true", prometheus.io/port: "9103"}`
- `kubecostExporter.intervalSeconds: 120`
- `kubecostExporter.extraLabels: {}` (e.g., tenant labels if not using external_labels)

Prometheus remote_write filter update
- Expand allowlist to include exporter + PV metrics.
- Reference (existing regex location): `k8s-kubecost/charts/kubecost-integration/values.yaml:39`

---

## Acceptance Criteria

- Thanos lists `cloudtuner_kubecost_*` metrics with correct tenant labels.
- Namespace total cost time series align (±5%) with Kubecost UI for the same window.
- Cluster total cost = sum(namespace totals) ± idle/share as configured.
- Metroculus surfaces allocation costs and efficiencies without SaaS→cluster calls.
- No excessive series cardinality or scrape errors.

---

## Open Questions / Decisions

- Idle handling: include `idle` and `shareIdle` semantics? If so, encode in exporter and document in labels, e.g., `idle="true"`, `share="weighted|even"`.
- Currency normalization: fix to USD or export `currency` label and convert downstream?
- Pod-level export policy: default off; optionally top-N pods by cost to control cardinality.
- Pricing metric parity: do we still want PromQL fallbacks enabled in parallel?

---

## References

- Existing analysis: `analysis/kubecost-metrics-analysis.md`
- Helm integration repo: k8s-kubecost (regex at k8s-kubecost/charts/kubecost-integration/values.yaml:39)
- Test scripts: `test_phase1.sh`, `phase-1/api-testing-guide.md`
