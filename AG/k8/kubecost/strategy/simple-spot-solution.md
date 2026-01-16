# Simple Spot Node Solution for Dev Environment

## Problem
- Thanos storegateway stuck because PVC is bound to terminated spot node in ap-south-1a
- Need simple solution to prevent volume preemption issues

## Simple Solution

### 1. Fix Current Issue (Immediate)
```bash
# Option 1: Delete PVC and recreate (DATA LOSS acceptable for dev)
kubectl scale statefulset thanos-storegateway --replicas=0
kubectl delete pvc thanos-storegateway-claim
kubectl scale statefulset thanos-storegateway --replicas=1

# Option 2: Force node in ap-south-1a
aws eks update-nodegroup-config \
  --cluster-name your-cluster \
  --nodegroup-name cloudtuner-general-amd \
  --scaling-config minSize=1,maxSize=5,desiredSize=3
```

### 2. Prevent Future Issues
The updated `thanos_storegateway.yaml` now uses:
- **Immediate volume binding** (cross-zone capable)
- **Encrypted storage** 
- **Retain policy** (prevents accidental deletion)
- **Simple configuration** (no complex affinity rules)

### 3. Spot-Only Node Group (Cost Savings)
```bash
# Create spot-only node group for dev
aws eks create-nodegroup \
  --cluster-name your-cluster \
  --nodegroup-name dev-spot-nodes \
  --capacity-type SPOT \
  --instance-types t3a.large t3a.xlarge m5.large m5.xlarge \
  --scaling-config minSize=1,maxSize=8,desiredSize=3 \
  --subnets subnet-ap-south-1a subnet-ap-south-1b subnet-ap-south-1c
```

## Files to Use

### Keep These:
- `pod-disruption-budgets.yaml` - Prevents all pods from being evicted at once
- Updated `thanos_storegateway.yaml` - Simple cross-zone storage
- Basic AWS Node Termination Handler (existing)

### Ignore These Complex Files:
- `spot-monitoring-alerting.yaml` - Too complex for dev
- `volume-management-solution.yaml` - Overkill for dev
- `eks-node-group-optimization.md` - Too detailed

## Deploy Steps

1. **Apply PDBs** (prevents service disruption):
```bash
kubectl apply -f pod-disruption-budgets.yaml
```

2. **Update Helm chart** (with simplified thanos config):
```bash
helm upgrade cloud-tuner-dev ./cloud-tuner-dev/
```

3. **Fix current stuck pod** (choose one option above)

## Expected Results
- **Cost savings**: 60-70% with spot-only nodes
- **No volume preemption**: Cross-zone storage prevents issues
- **Service protection**: PDBs prevent all pods going down at once
- **Simple maintenance**: No complex monitoring or automation