# CloudTuner-Kubecost Integration Development Chart

> **Note**: This is a development/testing Helm chart. For production customer deployments, use the main `optscale-k8s-cost` solution.

## Overview

This Helm chart provides a comprehensive development environment for testing CloudTuner-Kubecost integration features. It includes data extraction components, metrics processing, and cost aggregation services that work alongside the existing CloudTuner ecosystem.

## Prerequisites

- Kubernetes cluster 1.20+
- Helm 3.0+
- CloudTuner backend services running (restapi, diproxy, metroculus, influxdb, clickhouse)
- kubectl configured to access your cluster

## Quick Start

### 1. Install the Chart

```bash
# From the cloudtuner-dev-helm directory
cd k8s-kubecost
helm install kubecost-dev ./charts/kubecost-integration -n kubecost-dev --create-namespace
```

### 2. Verify Installation

```bash
# Check all pods are running
kubectl get pods -n kubecost-dev

# Check services
kubectl get svc -n kubecost-dev

# Check data flow (should see successful metrics ingestion)
kubectl logs -n default -l app=diproxy | grep "POST.*write"
```

## Configuration

### Basic Configuration

The chart uses sensible defaults but can be customized via `values.yaml`:

```yaml
# Enable/disable components
kubecost:
  enabled: true
  cloudtuner:
    enabled: true
    endpoint: "http://diproxy.default.svc.cluster.local"

extractor:
  enabled: true
  schedule:
    allocation: "0 */1 * * *"  # Every hour
    assets: "0 0 * * *"        # Daily

metricsProcessor:
  enabled: true
  
costAggregator:
  enabled: true
  schedule: "*/15 * * * *"     # Every 15 minutes
```

### Advanced Configuration

#### Custom CloudTuner Endpoints

```yaml
kubecost:
  cloudtuner:
    storage:
      influxdb: "http://influxdb.custom.svc.cluster.local"
      clickhouse: "http://clickhouse.custom.svc.cluster.local:8123"
    auth:
      username: "custom-user"
      password: "custom-password"
```

#### Resource Limits

```yaml
extractor:
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi

costAggregator:
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 2Gi
```

#### Custom Schedules

```yaml
extractor:
  schedule:
    allocation: "0 */30 * * *"  # Every 30 minutes
    assets: "0 2 * * *"         # Daily at 2 AM
    cleanup: "0 3 * * *"        # Daily cleanup at 3 AM

costAggregator:
  schedule: "*/10 * * * *"      # Every 10 minutes
```

## Installation Options

### Option 1: Default Installation

```bash
helm install kubecost-dev ./charts/kubecost-integration \
  -n kubecost-dev \
  --create-namespace
```

### Option 2: Custom Values

```bash
# Create custom values file
cat > custom-values.yaml <<EOF
kubecost:
  enabled: true
  cloudtuner:
    endpoint: "http://diproxy.cloudtuner.svc.cluster.local"

extractor:
  replicaCount: 2
  schedule:
    allocation: "0 */30 * * *"

monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    namespace: monitoring
EOF

# Install with custom values
helm install kubecost-dev ./charts/kubecost-integration \
  -f custom-values.yaml \
  -n kubecost-dev \
  --create-namespace
```

### Option 3: Development Mode

```bash
# Install with debug logging and frequent collection
helm install kubecost-dev ./charts/kubecost-integration \
  --set extractor.schedule.allocation="*/5 * * * *" \
  --set costAggregator.schedule="*/5 * * * *" \
  --set global.logLevel=DEBUG \
  -n kubecost-dev \
  --create-namespace
```

## Monitoring and Debugging

### Check Component Status

```bash
# Check all components
kubectl get all -n kubecost-dev

# Check specific deployments
kubectl get deployment -n kubecost-dev
kubectl get cronjob -n kubecost-dev

# Check pod logs
kubectl logs -n kubecost-dev deployment/kubecost-extractor
kubectl logs -n kubecost-dev deployment/cost-aggregator
```

### Monitor Data Flow

```bash
# Check metrics ingestion in diproxy
kubectl logs -n default -l app=diproxy --tail=50 | grep kubecost

# Check Kubecost API connectivity
kubectl exec -n kubecost-dev deployment/kubecost-extractor -- \
  curl -s http://kubecost-cost-analyzer.kubecost.svc.cluster.local:9090/model/allocation?window=1h
```

### Debug Data Extraction

```bash
# Run extraction job manually
kubectl create job -n kubecost-dev manual-extraction \
  --from=cronjob/kubecost-extractor-allocation

# Check job logs
kubectl logs -n kubecost-dev job/manual-extraction
```

### Verify CloudTuner Integration

```bash
# Check if data is reaching CloudTuner
kubectl port-forward -n default svc/restapi 8999:80

# Test new API endpoints (in another terminal)
curl "http://localhost:8999/restapi/v2/organizations/{org_id}/kubecost/clusters"
```

## Troubleshooting

### Common Issues

#### 1. Extractor Pod Failing
```bash
# Check logs
kubectl logs -n kubecost-dev deployment/kubecost-extractor

# Common causes:
# - Kubecost service not accessible
# - CloudTuner endpoints not reachable
# - Authentication issues
```

#### 2. No Data in CloudTuner
```bash
# Verify diproxy is receiving data
kubectl logs -n default -l app=diproxy | grep "200 POST"

# Check CronJob execution
kubectl get cronjobs -n kubecost-dev
kubectl describe cronjob -n kubecost-dev kubecost-extractor-allocation
```

#### 3. Permission Errors
```bash
# Check RBAC
kubectl auth can-i get pods --as=system:serviceaccount:kubecost-dev:kubecost-integration
kubectl describe clusterrolebinding kubecost-integration-reader
```

### Resource Issues

#### High Resource Usage
```yaml
# Reduce resource consumption
extractor:
  replicaCount: 1
  schedule:
    allocation: "0 */2 * * *"  # Less frequent collection
  config:
    batchSize: 500  # Smaller batches

costAggregator:
  schedule: "*/30 * * * *"  # Less frequent aggregation
```

#### Out of Memory
```yaml
# Increase memory limits
extractor:
  resources:
    limits:
      memory: 2Gi

costAggregator:
  resources:
    limits:
      memory: 4Gi
```

## Integration with CloudTuner Backend

### Required Backend Components

Ensure these CloudTuner services are running:

- **diproxy**: Receives metrics from Kubecost Prometheus
- **metroculus**: Queries stored metrics
- **influxdb**: Time-series storage
- **clickhouse**: Aggregated data storage
- **restapi**: New Kubecost API endpoints

### API Endpoints Available

Once installed, these endpoints become available in CloudTuner REST API:

```bash
# List clusters
GET /restapi/v2/organizations/{org_id}/kubecost/clusters

# Cluster costs
GET /restapi/v2/kubecost/clusters/{cluster_id}/costs?window=1d&aggregate=namespace

# Namespace breakdown
GET /restapi/v2/kubecost/clusters/{cluster_id}/namespaces?window=1d

# Workload costs
GET /restapi/v2/kubecost/clusters/{cluster_id}/namespaces/{ns}/workloads

# Infrastructure assets
GET /restapi/v2/kubecost/clusters/{cluster_id}/assets

# Resource metrics
GET /restapi/v2/kubecost/clusters/{cluster_id}/metrics?metric=cpu&window=1h
```

## Uninstallation

### Remove Chart

```bash
# Remove the Helm release
helm uninstall kubecost-dev -n kubecost-dev

# Remove namespace (optional)
kubectl delete namespace kubecost-dev
```

### Clean Up CRDs (if any)

```bash
# Remove any remaining custom resources
kubectl get crd | grep kubecost | awk '{print $1}' | xargs kubectl delete crd
```

## Development Workflow

### Testing New Features

1. **Modify Chart**: Update templates or values
2. **Lint**: `helm lint ./charts/kubecost-integration`
3. **Dry Run**: `helm install test-release ./charts/kubecost-integration --dry-run`
4. **Install**: `helm install kubecost-dev ./charts/kubecost-integration -n kubecost-dev`
5. **Test**: Verify functionality and data flow
6. **Iterate**: Update and upgrade as needed

### Upgrading

```bash
# Upgrade with new values
helm upgrade kubecost-dev ./charts/kubecost-integration \
  -f updated-values.yaml \
  -n kubecost-dev

# Check upgrade status
helm status kubecost-dev -n kubecost-dev
```

## Production Migration

When ready to move features to production:

1. **Test Thoroughly**: Validate all functionality in development
2. **Document Changes**: Record configuration and lessons learned
3. **Merge Features**: Integrate successful components into `optscale-k8s-cost`
4. **Customer Rollout**: Deploy updated production chart to customers

## Support

For issues with this development chart:

1. Check the troubleshooting section above
2. Verify CloudTuner backend connectivity
3. Review component logs for specific error messages
4. Ensure all prerequisites are met

Remember: This is for development/testing only. Production deployments should use the main `optscale-k8s-cost` solution.