# CloudTuner Kubernetes Stack Technical Brief

**Date**: 2025-11-19
**Status**: Phase 2 Complete, Phase 3 In Progress
**Reference Diagrams**: [Kubernetes-Stack-Diagrams.md](Kubernetes-Stack-Diagrams.md)

---

## 1. Project Overview

### Objective
The primary objective of the Kubernetes Stack integration is to provide CloudTuner users with unified cost visibility for their Kubernetes clusters alongside existing cloud infrastructure (AWS, Azure, GCP). This is achieved by integrating **Kubecost** (running in the customer's cluster) with **CloudTuner's SaaS platform**.

### Scope
- **Data Collection**: Ingesting cost metrics from customer Kubernetes clusters via Prometheus remote_write.
- **Data Processing**: Aggregating and transforming raw metrics into daily cost records.
- **Visualization**: Displaying Kubernetes costs in the CloudTuner dashboard (NGUI) with drill-down capabilities.
- **Multi-Tenancy**: Ensuring secure, isolated data handling for multiple customers using `Cloud-Account-Id`.

### Current Status
- **Phase 1 (Infrastructure Costs)**: ✅ Complete. Management, Load Balancer, and Network costs are flowing.
- **Phase 2 (Backend Processing)**: ✅ Complete. `kubecost_worker` successfully writes daily cluster costs to the ClickHouse `expenses` table.
- **Phase 3 (Frontend Integration)**: 🔄 In Progress. API endpoints are ready (`clean_expenses`, `breakdown_expenses`), but frontend components need to be built.
- **Phase 4 (Granular Allocation)**: 📅 Planned. Detailed pod/namespace-level cost breakdown is a future enhancement.

---

## 2. Technical Flow & Architecture

### High-Level Data Flow
The integration follows a pipeline from the customer's environment to the CloudTuner dashboard:

1.  **Collection**: Kubecost calculates costs in the customer's cluster. The `allocation-exporter` exposes these as Prometheus metrics.
2.  **Ingestion**: A local Prometheus server scrapes these metrics and forwards them to CloudTuner's `diproxy` via `remote_write` (HTTPS).
3.  **Storage**: Metrics are stored in **Thanos** (Object Storage) with `Cloud-Account-Id` tenant isolation.
4.  **Processing**: The `kubecost_worker` runs daily, querying **Metroculus** (which queries Thanos) to aggregate costs.
5.  **Persistence**: Aggregated daily costs are written to the **ClickHouse** `expenses` table.
6.  **Serving**: The **REST API** queries ClickHouse and serves unified cost data to the **NGUI** frontend.

*(See Diagram 1 & 2 in [Kubernetes-Stack-Diagrams.md](Kubernetes-Stack-Diagrams.md) for visual representation)*

### Key Components

| Component | Location | Role |
|-----------|----------|------|
| **Kubecost** | Customer Cluster | Cost calculation engine. |
| **Allocation Exporter** | Customer Cluster | Exposes Kubecost API data as Prometheus metrics. |
| **Prometheus** | Customer Cluster | Scrapes metrics and performs `remote_write`. |
| **Diproxy** | CloudTuner SaaS | Ingestion gateway, handles authentication. |
| **Thanos** | CloudTuner SaaS | Long-term metric storage. |
| **Metroculus** | CloudTuner SaaS | Internal service to query/aggregate Thanos data. |
| **Kubecost Worker** | CloudTuner SaaS | ETL job; writes to ClickHouse. |
| **ClickHouse** | CloudTuner SaaS | Primary data warehouse for cost data. |

---

## 3. Cloud Elements & Technology Stack

### Core Technologies
-   **Kubernetes**: The target platform for monitoring.
-   **Prometheus**: The standard for metric collection and transport.
-   **Thanos**: Provides global query view and long-term storage for Prometheus metrics.
-   **ClickHouse**: Columnar database used for high-performance cost reporting.
-   **MongoDB**: Stores resource metadata and configuration.

### Specific Implementations
-   **Virtual Cluster Resource**: A Kubernetes cluster is represented as a "virtual resource" in the `expenses` table, allowing it to coexist with EC2 instances and RDS databases.
-   **Tenant Isolation**: Achieved via the `Cloud-Account-Id` HTTP header in `remote_write` requests, which maps to the tenant ID in Thanos.
-   **Hybrid Cost Model**:
    -   *Infrastructure Costs* (Node, LB, Network) are derived directly from Prometheus metrics.
    -   *Allocation Costs* (Workload level) are currently aggregated at the cluster level due to metric export limitations (see Risks).

---

## 4. Strategic & Operational Steps

### Deployment Strategy
-   **Helm Charts**: Deployment is managed via standard Helm charts (`cloudtuner/kubecost-integration`).
-   **Versioning**: Strict version control on images (e.g., `v1.4.0`).
-   **Configuration**: Customers must provide their `Cloud-Account-Id` and `remote_write` credentials during installation.

### CI/CD & Operations
-   **Spot Instances**: For dev/test environments, a "Simple Spot Solution" is recommended to reduce costs (60-70% savings) using spot-only node groups and cross-zone storage for Thanos to prevent preemption issues.
-   **Monitoring**:
    -   Check `diproxy` logs for `POST /write` activity.
    -   Monitor `kubecost_cluster_info` metric availability in Thanos.
    -   Verify `kubecost_worker` success logs for ClickHouse writes.

### Project Health
-   **Integration Status**: Data collection is healthy (33+ metrics flowing).
-   **Backend**: Ready for cluster-level reporting.
-   **Frontend**: Needs development (Phase 3).

---

## 5. Decision Logic & Architecture Rationale

### Hybrid "Single Pane of Glass" Approach
**Decision**: Instead of building a separate "Kubernetes" tab, K8s costs are integrated into the existing `clean_expenses` API and views.
**Rationale**: This aligns with CloudTuner's philosophy of unified cloud management. A K8s cluster is treated as just another resource type, allowing users to see their total spend across all providers in one view.

### Remote Write vs. API Polling
**Decision**: Use Prometheus `remote_write` (Push) instead of polling the customer's Kubecost API (Pull).
**Rationale**:
-   **Security**: No need for CloudTuner to have inbound access to customer clusters (firewall friendly).
-   **Scalability**: SaaS platform doesn't need to manage thousands of API connections.
-   **Standardization**: Uses standard Prometheus protocols.

### Handling Allocation Data Gaps
**Decision**: Proceed with Phase 1/2 using Infrastructure Costs and Cluster-Level Aggregates.
**Rationale**: Detailed allocation metrics (pod-level) are not natively exposed by Kubecost for scraping. Rather than blocking the release, the team chose to ship cluster-level visibility first while investigating metric export solutions for Phase 4.

---

## 6. Recommendations & Next Steps

### Immediate Actions (Phase 3 - Frontend)
1.  **Build K8s Resource View**: Update NGUI to render "K8s Cluster" resources in the main expense table.
2.  **Implement Cost Breakdown**: Create the visualization for CPU/RAM/Storage/Network breakdown using the `k8s_costs` API field.
3.  **Fix API Bugs**: Deploy the fix for the `KeyError` in `breakdown_expenses` mentioned in the handover notes.

### Strategic Improvements (Phase 4)
1.  **Solve Allocation Data Gap**: Investigate enabling Kubecost's experimental metric exporter or deploying a sidecar to expose `kubecost_pod_*` metrics. This is critical for providing namespace/pod-level drill-down.
2.  **Enhance Virtual Resource**: Populate missing optional fields (Region, Owner) for the virtual cluster resource to improve filtering and reporting.
3.  **Alerting**: Implement budget alerts specifically for K8s clusters.

### Risks & Mitigations
-   **Risk**: **Missing Granular Data**. Users may expect pod-level costs immediately.
    -   *Mitigation*: Clearly label the current view as "Cluster Level" and add "Workload Breakdown" to the roadmap.
-   **Risk**: **Data Discrepancy**. Differences between Kubecost's local UI and CloudTuner's dashboard due to aggregation timing.
    -   *Mitigation*: Document the daily processing cycle and expected data freshness (24h latency for finalized costs).
