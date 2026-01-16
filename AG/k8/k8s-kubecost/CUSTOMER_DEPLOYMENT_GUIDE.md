# CloudTuner Kubernetes Cost Monitoring - Customer Deployment Guide

## Overview

This Helm chart enables seamless integration between your Kubernetes cluster and CloudTuner's SaaS cost management platform. Once deployed, your Kubernetes cost data (namespace, pod, and node-level) will automatically flow to CloudTuner's dashboard, providing unified visibility across all your cloud infrastructure.

**What This Chart Does**:
- Deploys Kubecost for native Kubernetes cost allocation
- Exposes cost metrics via Prometheus
- Forwards metrics to CloudTuner SaaS via secure remote_write
- Enables granular cost visibility in CloudTuner dashboard

**Architecture**:
```
Your Kubernetes Cluster              CloudTuner SaaS Platform
┌─────────────────────────┐         ┌──────────────────────┐
│ Kubecost                │         │ Thanos (TSDB)        │
│   ↓                     │         │   ↓                  │
│ allocation-exporter     │         │ Cost Analytics       │
│   ↓                     │         │   ↓                  │
│ Prometheus              │────────▶│ CloudTuner Dashboard │
│   (remote_write)        │  HTTPS  │                      │
└─────────────────────────┘         └──────────────────────┘
```

**Data Flow**:
1. Kubecost calculates K8s resource costs
2. allocation-exporter exposes costs as Prometheus metrics
3. Prometheus scrapes metrics and forwards via remote_write
4. CloudTuner SaaS receives, stores, and visualizes costs

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)
6. [Upgrades and Maintenance](#upgrades-and-maintenance)
7. [Uninstallation](#uninstallation)
8. [Security Considerations](#security-considerations)
9. [FAQ](#faq)

---

## Prerequisites

### Required

| Requirement | Version | Verification Command |
|-------------|---------|---------------------|
| Kubernetes | 1.20+ | `kubectl version --short` |
| Helm | 3.0+ | `helm version --short` |
| kubectl access | Admin | `kubectl auth can-i create clusterrolebinding` |
| CloudTuner Account | Active | Login at https://dashboard.cloudtuner.ai |

### Required Information from CloudTuner

Before installation, obtain these values from your CloudTuner account:

1. **Cloud Account ID**: Your Kubernetes cluster's unique identifier in CloudTuner
   - Navigate to: CloudTuner Dashboard → Cloud Accounts → Add Kubernetes Cluster
   - Copy the generated `Cloud Account ID` (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

2. **Remote Write Credentials**: Authentication for sending metrics
   - Provided during cluster registration
   - Username: `kubecost` (default)
   - Password: Provided by CloudTuner support

### Resource Requirements

**Minimum Cluster Resources**:
- 2 CPU cores available
- 4 GB RAM available
- 20 GB storage (for Prometheus retention)

**Deployed Components**:
| Component | CPU Request | Memory Request | Storage |
|-----------|-------------|----------------|---------|
| Kubecost cost-analyzer | 200m | 512Mi | - |
| Prometheus server | 500m | 2Gi | 15Gi |
| allocation-exporter | 100m | 128Mi | - |
| **Total** | **~800m** | **~2.6Gi** | **15Gi** |

---

## Installation

### Step 1: Add CloudTuner Helm Repository

```bash
# Add the CloudTuner Helm repository
helm repo add cloudtuner https://charts.cloudtuner.ai

# Update repository index
helm repo update

# Verify chart is available
helm search repo cloudtuner/kubecost-integration
```

> **Development/Testing**: If using the local development chart, skip this step and use the local path in installation commands.

### Step 2: Create Configuration File

Create a `cloudtuner-values.yaml` file with your cluster-specific configuration:

```yaml
# cloudtuner-values.yaml

# CRITICAL: Replace with your actual Cloud Account ID from CloudTuner
global:
  imageTag: v1.4.0

kubecost:
  enabled: true

  # CloudTuner integration settings
  cloudtuner:
    enabled: true
    # PRODUCTION: Use https://dashboard.cloudtuner.ai
    # DEVELOPMENT: Use https://dev.dashboard.cloudtuner.ai
    endpoint: "https://dashboard.cloudtuner.ai"

  # Prometheus remote write configuration
  prometheus:
    server:
      enabled: true
      retention: "15d"
      remoteWrite:
        - url: "https://dashboard.cloudtuner.ai/storage/api/v2/write"
          name: cloudtuner
          headers:
            # REPLACE THIS with your actual Cloud Account ID
            Cloud-Account-Id: "REPLACE_WITH_YOUR_CLOUD_ACCOUNT_ID"
          basic_auth:
            username: kubecost
            # REPLACE THIS with credentials from CloudTuner support
            password: "REPLACE_WITH_YOUR_PASSWORD"
          tls_config:
            # For production, set to false and ensure TLS certs are valid
            insecure_skip_verify: false
          write_relabel_configs:
          - source_labels: [__name__]
            regex: '(kubecost_.*|cloudtuner_kubecost_.*|container_.*|kube_.*|node_.*|pod_pvc_.*|pv_.*|up)'
            action: keep

  # Pricing configuration
  kubecostModel:
    customPricesEnabled: true
    defaultModelPricing:
      enabled: true
      CPU: "28.0"           # Monthly cost per CPU core (USD)
      spotCPU: "4.86"       # Monthly cost per spot CPU core
      RAM: "3.09"           # Monthly cost per GB of RAM
      spotRAM: "0.65"       # Monthly cost per GB of spot RAM
      storage: "0.04"       # Monthly cost per GB of storage
      zoneNetworkEgress: "0.01"
      regionNetworkEgress: "0.01"
      internetNetworkEgress: "0.12"

# Allocation Exporter - exposes cost metrics
allocationExporter:
  enabled: true
  replicaCount: 1

  config:
    scrapeInterval: 120  # Scrape Kubecost API every 120 seconds
    window: "24h"        # Query last 24h of allocation data
    aggregationLevel: namespace  # Options: namespace, pod

    # CRITICAL: Must match Cloud-Account-Id in remote_write headers
    tenantId: "REPLACE_WITH_YOUR_CLOUD_ACCOUNT_ID"

    # Set to your cluster's display name
    clusterName: "production-k8s-cluster"

    # Enable pod-level metrics (high cardinality)
    enablePodMetrics: false  # Set true for pod-level costs
    topNPods: 50             # If enablePodMetrics=true, limit to top 50

# RBAC and security
rbac:
  create: true

serviceAccount:
  create: true

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000

securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
    - ALL
```

### Step 3: Install the Chart

```bash
# Install in dedicated namespace (recommended)
helm install cloudtuner-k8s cloudtuner/kubecost-integration \
  -f cloudtuner-values.yaml \
  -n cloudtuner-system \
  --create-namespace \
  --wait \
  --timeout 10m
```

**Alternative: Development/Local Installation**
```bash
# If using local development chart
cd k8s-kubecost
helm install cloudtuner-k8s ./charts/kubecost-integration \
  -f cloudtuner-values.yaml \
  -n cloudtuner-system \
  --create-namespace \
  --wait \
  --timeout 10m
```

### Step 4: Verify Installation

```bash
# Check all pods are running
kubectl get pods -n cloudtuner-system

# Expected output (all Running):
# NAME                                              READY   STATUS    RESTARTS   AGE
# cloudtuner-k8s-cost-analyzer-xxx                  4/4     Running   0          5m
# cloudtuner-k8s-prometheus-server-xxx              1/1     Running   0          5m
# kubecost-allocation-exporter-xxx                  1/1     Running   0          5m

# Check services
kubectl get svc -n cloudtuner-system

# Check Prometheus remote_write config
kubectl get configmap -n cloudtuner-system cloudtuner-k8s-prometheus-server -o yaml | grep -A5 remote_write
```

---

## Configuration

### Required Configuration Parameters

These parameters **must** be set for proper operation:

#### 1. Cloud Account ID
```yaml
kubecost:
  prometheus:
    server:
      remoteWrite:
        - headers:
            Cloud-Account-Id: "YOUR_CLOUD_ACCOUNT_ID"  # From CloudTuner dashboard

allocationExporter:
  config:
    tenantId: "YOUR_CLOUD_ACCOUNT_ID"  # Must match above
```

**Critical**: Both values must be identical and match your CloudTuner Cloud Account ID.

#### 2. CloudTuner Endpoint
```yaml
kubecost:
  cloudtuner:
    endpoint: "https://dashboard.cloudtuner.ai"  # Production
    # OR
    endpoint: "https://dev.dashboard.cloudtuner.ai"  # Development

  prometheus:
    server:
      remoteWrite:
        - url: "https://dashboard.cloudtuner.ai/storage/api/v2/write"  # Must match endpoint
```

**For Production**: Remove `dev.` subdomain from URLs.

#### 3. Authentication Credentials
```yaml
kubecost:
  prometheus:
    server:
      remoteWrite:
        - basic_auth:
            username: kubecost
            password: "YOUR_PASSWORD_FROM_CLOUDTUNER"
```

### Optional Configuration Parameters

#### Cluster Identification
```yaml
allocationExporter:
  config:
    clusterName: "prod-us-east-1"  # Display name in CloudTuner dashboard
```

#### Cost Granularity
```yaml
allocationExporter:
  config:
    aggregationLevel: namespace  # Options: namespace, pod
    enablePodMetrics: true       # Enable pod-level cost tracking
    topNPods: 100                # Limit pod metrics to top 100 by cost
```

**Warning**: Pod-level metrics increase cardinality significantly. Only enable if needed.

#### Data Collection Frequency
```yaml
allocationExporter:
  config:
    scrapeInterval: 120  # Seconds between Kubecost API queries
    window: "24h"        # Allocation time window to query
```

**Recommendations**:
- Production: `scrapeInterval: 300` (5 minutes)
- Development: `scrapeInterval: 120` (2 minutes)

#### Prometheus Retention
```yaml
kubecost:
  prometheus:
    server:
      retention: "15d"  # How long Prometheus stores metrics locally
```

**Tradeoff**: Longer retention requires more storage but provides better local visibility.

#### Resource Limits
```yaml
allocationExporter:
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

kubecost:
  prometheus:
    server:
      resources:
        requests:
          cpu: 500m
          memory: 2Gi
        limits:
          cpu: 2000m
          memory: 4Gi
```

#### Custom Pricing

If your cluster uses custom pricing (not AWS/GCP/Azure):

```yaml
kubecost:
  kubecostModel:
    customPricesEnabled: true
    defaultModelPricing:
      CPU: "30.0"        # Your monthly cost per CPU core
      RAM: "4.0"         # Your monthly cost per GB RAM
      storage: "0.05"    # Your monthly cost per GB storage
      # ... additional pricing parameters
```

### Configuration Examples

#### Example 1: Production Multi-Cluster Setup

```yaml
# production-cluster-1.yaml
global:
  imageTag: v1.4.0

kubecost:
  cloudtuner:
    endpoint: "https://dashboard.cloudtuner.ai"
  prometheus:
    server:
      retention: "15d"
      remoteWrite:
        - url: "https://dashboard.cloudtuner.ai/storage/api/v2/write"
          headers:
            Cloud-Account-Id: "aaaaaaaa-1111-1111-1111-aaaaaaaaaaaa"
          basic_auth:
            username: kubecost
            password: "prod-secret-123"

allocationExporter:
  config:
    scrapeInterval: 300
    tenantId: "aaaaaaaa-1111-1111-1111-aaaaaaaaaaaa"
    clusterName: "prod-us-east-1"
    aggregationLevel: namespace
    enablePodMetrics: false
```

#### Example 2: Development/Testing Setup

```yaml
# development-cluster.yaml
global:
  imageTag: v1.4.0-dev

kubecost:
  cloudtuner:
    endpoint: "https://dev.dashboard.cloudtuner.ai"
  prometheus:
    server:
      retention: "7d"
      remoteWrite:
        - url: "https://dev.dashboard.cloudtuner.ai/storage/api/v2/write"
          headers:
            Cloud-Account-Id: "bbbbbbbb-2222-2222-2222-bbbbbbbbbbbb"
          basic_auth:
            username: kubecost
            password: "dev-secret-456"
          tls_config:
            insecure_skip_verify: true

allocationExporter:
  config:
    scrapeInterval: 120
    tenantId: "bbbbbbbb-2222-2222-2222-bbbbbbbbbbbb"
    clusterName: "dev-minikube"
    aggregationLevel: pod
    enablePodMetrics: true
    topNPods: 20
```

#### Example 3: High-Scale Production

```yaml
# large-production-cluster.yaml
global:
  imageTag: v1.4.0

kubecost:
  prometheus:
    server:
      retention: "30d"
      resources:
        requests:
          cpu: 2000m
          memory: 8Gi
        limits:
          cpu: 4000m
          memory: 16Gi
      remoteWrite:
        - url: "https://dashboard.cloudtuner.ai/storage/api/v2/write"
          headers:
            Cloud-Account-Id: "cccccccc-3333-3333-3333-cccccccccccc"
          queue_config:
            capacity: 50000
            max_shards: 20
            min_shards: 4
            max_samples_per_send: 10000

allocationExporter:
  replicaCount: 2  # High availability
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 2Gi
  config:
    tenantId: "cccccccc-3333-3333-3333-cccccccccccc"
    clusterName: "prod-us-west-2-main"
    scrapeInterval: 600  # 10 minutes (reduce load)
```

---

## Verification

### Step 1: Verify Pod Health

```bash
# All pods should be Running
kubectl get pods -n cloudtuner-system

# Check pod logs for errors
kubectl logs -n cloudtuner-system -l app.kubernetes.io/name=kubecost-allocation-exporter
kubectl logs -n cloudtuner-system -l app=prometheus
```

**Expected allocation-exporter logs**:
```
INFO - Starting allocation exporter...
INFO - Kubecost URL: http://cloudtuner-k8s.cloudtuner-system.svc.cluster.local:9090
INFO - Tenant ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
INFO - Successfully scraped allocation data: 15 namespaces
INFO - Exported 45 metrics
```

### Step 2: Verify Metrics Export

```bash
# Port-forward to allocation-exporter
kubectl port-forward -n cloudtuner-system svc/kubecost-allocation-exporter 9103:9103

# In another terminal, check metrics are exposed
curl -s http://localhost:9103/metrics | grep cloudtuner_kubecost_namespace_total_cost

# Expected output (example):
# cloudtuner_kubecost_namespace_total_cost{tenant_id="xxx",namespace="default",cluster="prod"} 0.245
# cloudtuner_kubecost_namespace_total_cost{tenant_id="xxx",namespace="kube-system",cluster="prod"} 0.189
```

### Step 3: Verify Prometheus Scraping

```bash
# Port-forward to Prometheus
kubectl port-forward -n cloudtuner-system svc/cloudtuner-k8s-prometheus-server 9090:80

# Open browser: http://localhost:9090
# Navigate to: Status → Targets
# Verify: kubecost-allocation-exporter target is UP

# Query metrics in Prometheus
# Navigate to: Graph
# Query: cloudtuner_kubecost_namespace_total_cost
# Should see namespace cost data
```

### Step 4: Verify Remote Write to CloudTuner

```bash
# Check Prometheus logs for remote_write activity
kubectl logs -n cloudtuner-system -l app=prometheus | grep -i "remote"

# Expected logs (no errors):
# level=info component=remote msg="Done replaying WAL" queue=cloudtuner
# level=info component=remote msg="Starting WAL watcher" queue=cloudtuner

# Check for errors:
kubectl logs -n cloudtuner-system -l app=prometheus | grep -i "error\|failed"

# Should see NO errors related to remote_write
```

### Step 5: Verify Data in CloudTuner Dashboard

1. **Login to CloudTuner**: https://dashboard.cloudtuner.ai
2. **Navigate to**: Cloud Accounts → Your Kubernetes Cluster
3. **Check Status**: Cluster should show as "Connected" or "Receiving Data"
4. **View Costs**: Navigate to Cost Explorer → Filter by Kubernetes
5. **Verify Filters**: Namespace filter dropdown should populate with your namespaces

**Timeline**: Data may take 5-10 minutes to appear in dashboard after installation.

### Verification Checklist

- [ ] All pods in `cloudtuner-system` namespace are Running
- [ ] allocation-exporter logs show successful Kubecost scraping
- [ ] Metrics endpoint (port 9103) exposes `cloudtuner_kubecost_*` metrics
- [ ] Prometheus targets show allocation-exporter as UP
- [ ] Prometheus logs show successful remote_write (no errors)
- [ ] CloudTuner dashboard shows cluster as Connected
- [ ] Cost data appears in CloudTuner Cost Explorer
- [ ] Namespace filters populate in CloudTuner UI

---

## Troubleshooting

### Issue 1: Pods Not Starting

**Symptoms**:
```bash
kubectl get pods -n cloudtuner-system
# NAME                               READY   STATUS             RESTARTS   AGE
# allocation-exporter-xxx            0/1     ImagePullBackOff   0          2m
```

**Diagnosis**:
```bash
kubectl describe pod -n cloudtuner-system <pod-name>
# Look for Events section
```

**Common Causes & Fixes**:

1. **ImagePullBackOff**
   ```bash
   # Error: Failed to pull image "invincibledocker24/kubecost-allocation-exporter:v1.4.0"
   # Fix: Verify image tag in values.yaml
   global:
     imageTag: v1.4.0  # Check this matches available image
   ```

2. **CrashLoopBackOff**
   ```bash
   # Check logs for startup errors
   kubectl logs -n cloudtuner-system <pod-name>

   # Common: Missing required env vars
   # Fix: Ensure tenantId is set correctly in values.yaml
   ```

3. **Insufficient Resources**
   ```bash
   # Error: 0/3 nodes are available: insufficient cpu
   # Fix: Increase cluster resources or reduce requests
   allocationExporter:
     resources:
       requests:
         cpu: 50m  # Reduce from 100m
   ```

### Issue 2: No Metrics Exported

**Symptoms**:
```bash
curl http://localhost:9103/metrics | grep cloudtuner_kubecost
# Empty output or only metadata
```

**Diagnosis**:
```bash
kubectl logs -n cloudtuner-system -l app.kubernetes.io/name=kubecost-allocation-exporter --tail=100
```

**Common Causes & Fixes**:

1. **Cannot Reach Kubecost API**
   ```
   ERROR - Failed to query Kubecost: connection refused

   # Fix: Verify Kubecost service exists
   kubectl get svc -n cloudtuner-system | grep cost-analyzer

   # Verify exporter can reach it
   kubectl exec -n cloudtuner-system deployment/kubecost-allocation-exporter -- \
     wget -O- http://cloudtuner-k8s.cloudtuner-system.svc.cluster.local:9090/allocation?window=1h
   ```

2. **Kubecost API Returns Errors**
   ```
   ERROR - Kubecost API returned 500: Internal Server Error

   # Check Kubecost logs
   kubectl logs -n cloudtuner-system -l app.kubernetes.io/name=cost-analyzer

   # Common: Pricing data not configured
   # Fix: Verify kubecostModel.customPricesEnabled=true in values.yaml
   ```

3. **No Allocation Data Available**
   ```
   WARN - Kubecost allocation query returned empty data

   # Kubecost needs time to collect data (15-30 minutes after installation)
   # Fix: Wait and check again, or verify Kubecost is scraping Prometheus
   ```

### Issue 3: Prometheus Not Scraping Exporter

**Symptoms**:
```
# Prometheus targets show allocation-exporter as DOWN
```

**Diagnosis**:
```bash
# Check Prometheus service discovery
kubectl logs -n cloudtuner-system -l app=prometheus | grep allocation-exporter

# Check service and endpoint
kubectl get svc,endpoints -n cloudtuner-system | grep allocation-exporter
```

**Fixes**:

1. **Service Discovery Not Working**
   ```bash
   # Verify service labels match Prometheus scrape config
   kubectl get svc -n cloudtuner-system kubecost-allocation-exporter -o yaml

   # Should have:
   # labels:
   #   app.kubernetes.io/name: kubecost-allocation-exporter
   ```

2. **Port Mismatch**
   ```yaml
   # Verify service port matches exporter port
   allocationExporter:
     port: 9103  # Must match service targetPort
   ```

### Issue 4: Remote Write Failing

**Symptoms**:
```bash
kubectl logs -n cloudtuner-system -l app=prometheus | grep -i "error.*remote"
# level=error component=remote msg="non-recoverable error" err="401 Unauthorized"
```

**Diagnosis**:
```bash
# Check remote_write configuration
kubectl get configmap -n cloudtuner-system cloudtuner-k8s-prometheus-server -o yaml | grep -A50 remote_write
```

**Common Causes & Fixes**:

1. **401 Unauthorized**
   ```yaml
   # Fix: Verify credentials in values.yaml
   kubecost:
     prometheus:
       server:
         remoteWrite:
           - basic_auth:
               username: kubecost
               password: "CORRECT_PASSWORD_FROM_CLOUDTUNER"
   ```

2. **400 Bad Request**
   ```
   # Often caused by missing or incorrect Cloud-Account-Id header
   # Fix:
   kubecost:
     prometheus:
       server:
         remoteWrite:
           - headers:
               Cloud-Account-Id: "VALID_CLOUD_ACCOUNT_ID"
   ```

3. **Connection Refused / Timeout**
   ```bash
   # Test connectivity from Prometheus pod
   kubectl exec -n cloudtuner-system -l app=prometheus -- \
     wget --spider https://dashboard.cloudtuner.ai/storage/api/v2/write

   # If fails, check:
   # - Firewall rules
   # - Network policies
   # - DNS resolution
   ```

### Issue 5: Data Not Appearing in CloudTuner Dashboard

**Symptoms**:
- Prometheus remote_write shows no errors
- Metrics are exported from allocation-exporter
- But no data in CloudTuner dashboard

**Diagnosis**:
```bash
# Verify Cloud-Account-Id matches between exporter and remote_write
kubectl get configmap -n cloudtuner-system cloudtuner-k8s-prometheus-server -o yaml | grep Cloud-Account-Id
kubectl get deployment -n cloudtuner-system kubecost-allocation-exporter -o yaml | grep TENANT_ID

# Both should be identical
```

**Fixes**:

1. **Mismatched Cloud Account ID**
   ```yaml
   # CRITICAL: These must match exactly
   kubecost:
     prometheus:
       server:
         remoteWrite:
           - headers:
               Cloud-Account-Id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

   allocationExporter:
     config:
       tenantId: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # Same value!
   ```

2. **Wrong CloudTuner Endpoint**
   ```yaml
   # Verify you're using the correct endpoint
   # Production:
   endpoint: "https://dashboard.cloudtuner.ai"
   # NOT:
   endpoint: "https://dev.dashboard.cloudtuner.ai"  # Development only
   ```

3. **Cloud Account Not Registered**
   - Login to CloudTuner dashboard
   - Navigate to: Cloud Accounts → Add Cloud Account
   - Select: Kubernetes
   - Verify account exists with matching Cloud Account ID

### Issue 6: High Resource Usage

**Symptoms**:
```bash
kubectl top pods -n cloudtuner-system
# NAME                               CPU    MEMORY
# prometheus-server-xxx              1500m  6000Mi  # High!
```

**Fixes**:

1. **Reduce Prometheus Retention**
   ```yaml
   kubecost:
     prometheus:
       server:
         retention: "7d"  # Reduce from 15d
   ```

2. **Reduce Metric Cardinality**
   ```yaml
   allocationExporter:
     config:
       enablePodMetrics: false  # Disable pod-level metrics
       aggregationLevel: namespace  # Use namespace only
   ```

3. **Increase Scrape Interval**
   ```yaml
   allocationExporter:
     config:
       scrapeInterval: 300  # 5 minutes instead of 2 minutes
   ```

4. **Add Resource Limits**
   ```yaml
   kubecost:
     prometheus:
       server:
         resources:
           limits:
             cpu: 2000m
             memory: 4Gi
   ```

---

## Upgrades and Maintenance

### Upgrading the Chart

```bash
# Update Helm repository
helm repo update cloudtuner

# Check available versions
helm search repo cloudtuner/kubecost-integration --versions

# Upgrade to latest version
helm upgrade cloudtuner-k8s cloudtuner/kubecost-integration \
  -f cloudtuner-values.yaml \
  -n cloudtuner-system \
  --wait

# Verify upgrade
helm status cloudtuner-k8s -n cloudtuner-system
kubectl get pods -n cloudtuner-system
```

### Updating Configuration

```bash
# Modify cloudtuner-values.yaml with desired changes

# Apply configuration changes
helm upgrade cloudtuner-k8s cloudtuner/kubecost-integration \
  -f cloudtuner-values.yaml \
  -n cloudtuner-system

# Restart pods if config doesn't hot-reload
kubectl rollout restart deployment -n cloudtuner-system
```

### Maintenance Tasks

#### Check Prometheus Storage Usage

```bash
# Get PVC size
kubectl get pvc -n cloudtuner-system

# Check disk usage inside Prometheus pod
kubectl exec -n cloudtuner-system -l app=prometheus -- df -h /data
```

#### Rotate Remote Write Credentials

```bash
# Update password in values.yaml
# Then upgrade release
helm upgrade cloudtuner-k8s cloudtuner/kubecost-integration \
  -f cloudtuner-values.yaml \
  -n cloudtuner-system

# Verify remote_write reconnects
kubectl logs -n cloudtuner-system -l app=prometheus | grep -i remote
```

#### Scale Components

```bash
# Temporarily scale down (maintenance window)
kubectl scale deployment -n cloudtuner-system kubecost-allocation-exporter --replicas=0

# Scale back up
kubectl scale deployment -n cloudtuner-system kubecost-allocation-exporter --replicas=1
```

---

## Uninstallation

### Step 1: Uninstall Helm Release

```bash
# Uninstall the chart
helm uninstall cloudtuner-k8s -n cloudtuner-system

# Verify resources are removed
kubectl get all -n cloudtuner-system
```

### Step 2: Clean Up Persistent Data

```bash
# List PVCs (Prometheus data)
kubectl get pvc -n cloudtuner-system

# Delete PVCs if you want to remove all historical data
kubectl delete pvc -n cloudtuner-system --all
```

### Step 3: Remove Namespace

```bash
# Delete namespace (removes all remaining resources)
kubectl delete namespace cloudtuner-system
```

### Step 4: Clean Up Cluster-Level Resources

```bash
# Remove ClusterRoleBinding (if created)
kubectl delete clusterrolebinding cloudtuner-k8s-integration-reader

# Verify cleanup
kubectl get clusterrolebinding | grep cloudtuner
```

### Step 5: Deregister from CloudTuner

1. Login to CloudTuner dashboard
2. Navigate to: Cloud Accounts
3. Find your Kubernetes cluster
4. Click: Delete or Disconnect

**Warning**: After uninstallation, cost data will no longer flow to CloudTuner. Historical data in CloudTuner will be retained based on your account's retention policy.

---

## Security Considerations

### Data Security

**What Data is Sent?**
- Kubernetes cost metrics (resource usage, costs)
- Namespace, pod, node names (metadata)
- Resource labels and annotations (if configured)

**What is NOT Sent?**
- Application logs
- Secret values
- ConfigMap contents
- Pod command/args
- Container images contents

### Authentication

**Credentials Storage**:
- Remote write credentials stored in Helm values
- Consider using Kubernetes Secrets for sensitive values:

```bash
# Create secret for remote_write password
kubectl create secret generic cloudtuner-remote-write \
  --from-literal=password='YOUR_PASSWORD' \
  -n cloudtuner-system

# Reference in values.yaml
kubecost:
  prometheus:
    server:
      remoteWrite:
        - basic_auth:
            username: kubecost
            password_file: /etc/prometheus/secrets/cloudtuner-remote-write/password
```

### Network Security

**Outbound Traffic**:
- Prometheus → `dashboard.cloudtuner.ai:443` (HTTPS)
- Only outbound connections initiated from your cluster
- No inbound connections required

**Firewall Rules**:
```
ALLOW outbound TCP 443 to dashboard.cloudtuner.ai
```

**Network Policies** (Optional):
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: prometheus-egress
  namespace: cloudtuner-system
spec:
  podSelector:
    matchLabels:
      app: prometheus
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53  # DNS
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: UDP
      port: 53  # DNS
  - ports:
    - protocol: TCP
      port: 443  # HTTPS to CloudTuner
```

### RBAC Permissions

The chart creates minimal RBAC permissions:

```yaml
# ClusterRole: Read-only access to pods, nodes, namespaces
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cloudtuner-k8s-integration-reader
rules:
- apiGroups: [""]
  resources:
  - nodes
  - nodes/metrics
  - pods
  - namespaces
  - persistentvolumes
  - persistentvolumeclaims
  verbs: ["get", "list"]
```

**No Write Permissions**: Chart components only read cluster data, never modify.

### TLS Configuration

**Production**: Use valid TLS certificates
```yaml
kubecost:
  prometheus:
    server:
      remoteWrite:
        - tls_config:
            insecure_skip_verify: false  # Verify CloudTuner's TLS cert
```

**Development/Testing Only**: Skip TLS verification
```yaml
kubecost:
  prometheus:
    server:
      remoteWrite:
        - tls_config:
            insecure_skip_verify: true  # WARNING: Not for production
```

---

## FAQ

### General Questions

**Q: How long does it take to see data in CloudTuner?**
A: Typically 5-10 minutes after installation. Kubecost needs 15-30 minutes to gather initial allocation data, then metrics flow within 2-5 minutes.

**Q: Will this affect my cluster performance?**
A: Minimal impact. Total overhead: ~800m CPU, ~2.6Gi RAM. Comparable to running a small application.

**Q: Can I deploy this in multiple clusters?**
A: Yes! Deploy the chart in each cluster with a unique Cloud-Account-Id. CloudTuner will aggregate costs across all clusters.

**Q: What happens if CloudTuner is unreachable?**
A: Prometheus will buffer metrics locally (up to retention period) and retry sending automatically. No data loss during temporary outages.

**Q: Is internet connectivity required?**
A: Yes, for sending metrics to CloudTuner SaaS. For air-gapped environments, contact CloudTuner support for on-premises deployment options.

### Cost and Pricing

**Q: How are costs calculated?**
A: Kubecost queries your cloud provider APIs (AWS/GCP/Azure) for pricing. For custom environments, use `customPricesEnabled` to set manual pricing.

**Q: Are network egress costs included?**
A: Yes, if network cost metrics are available from your cloud provider or configured in custom pricing.

**Q: Can I see costs by team/project?**
A: Yes! Use Kubernetes labels on namespaces/pods. CloudTuner's dashboard supports filtering and grouping by labels.

### Technical Questions

**Q: What Kubernetes versions are supported?**
A: Kubernetes 1.20+ (tested up to 1.28)

**Q: Can I use my existing Prometheus?**
A: Yes, but requires manual configuration. The chart includes Prometheus for simplicity. Contact support for integration guide.

**Q: Do you support OpenShift?**
A: Yes, with minor values.yaml adjustments for security contexts. Contact support for OpenShift-specific documentation.

**Q: Can I customize which metrics are sent?**
A: Yes, modify `write_relabel_configs` in values.yaml to filter metrics. See Prometheus documentation for relabeling rules.

**Q: What if I have multiple Prometheus instances?**
A: Add remote_write configuration to each Prometheus with the same Cloud-Account-Id. CloudTuner will aggregate data.

### Troubleshooting

**Q: I see 401 errors in Prometheus logs**
A: Verify `basic_auth` username/password match credentials provided by CloudTuner support. Check for typos in values.yaml.

**Q: Metrics are exported but not in CloudTuner dashboard**
A: Verify `Cloud-Account-Id` header matches `tenantId` exactly. Check CloudTuner dashboard that the cloud account is registered.

**Q: High memory usage on Prometheus**
A: Reduce `retention` period, disable pod-level metrics, or increase scrape intervals. See [High Resource Usage](#issue-6-high-resource-usage).

**Q: Can't connect to Kubecost API from allocation-exporter**
A: Verify service name matches release name. Default: `http://{{ .Release.Name }}.{{ .Release.Namespace }}.svc.cluster.local:9090`

---

## Support

### Documentation

- **Full Integration Guide**: [KUBECOST_CLOUDTUNER_INTEGRATION.md](../docs/kubecost/KUBECOST_CLOUDTUNER_INTEGRATION.md)
- **CloudTuner Docs**: https://docs.cloudtuner.ai
- **Kubecost Docs**: https://docs.kubecost.com

### Contact Support

- **Email**: support@cloudtuner.ai
- **Slack**: [CloudTuner Community](https://cloudtuner.slack.com)
- **Issues**: https://github.com/cloudtuner/k8s-cost-integration/issues

### Providing Diagnostic Information

When contacting support, please include:

```bash
# Collect diagnostic bundle
kubectl get all -n cloudtuner-system > diagnostics.txt
kubectl describe pods -n cloudtuner-system >> diagnostics.txt
kubectl logs -n cloudtuner-system -l app=prometheus --tail=100 >> diagnostics.txt
kubectl logs -n cloudtuner-system -l app.kubernetes.io/name=kubecost-allocation-exporter --tail=100 >> diagnostics.txt
helm get values cloudtuner-k8s -n cloudtuner-system >> diagnostics.txt

# Send diagnostics.txt to support
```

---

## Changelog

### v1.4.0 (2025-01-15)
- Added allocation-exporter for namespace/pod-level costs
- Improved Prometheus remote_write configuration
- Enhanced RBAC security
- Updated Kubecost to 2.8.0

### v1.3.0 (2024-12-01)
- Initial production release
- Cluster-level cost aggregation
- Basic Prometheus remote_write support

---

## License

Copyright © 2025 CloudTuner Inc. All rights reserved.

This Helm chart is licensed to CloudTuner customers for use with the CloudTuner platform. Redistribution or use outside of CloudTuner deployments is prohibited.
