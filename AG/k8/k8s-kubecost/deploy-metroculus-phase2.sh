#!/bin/bash
# Deploy Phase 2 Metroculus with allocation exporter support

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
METROCULUS_DIR="${METROCULUS_DIR:-/Users/balaji/source/code/cloudtuner/cloud-tuner/metroculus}"
IMAGE_REPO="${IMAGE_REPO:-invincibledocker24/metroculusapi}"
IMAGE_TAG="${IMAGE_TAG:-v1.5.0-phase2}"
NAMESPACE="${NAMESPACE:-default}"
BUILD_IMAGE="${BUILD_IMAGE:-false}"
DEPLOYMENT_METHOD="${DEPLOYMENT_METHOD:-restart}"  # restart|rebuild|helm

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deploy Metroculus Phase 2${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Method: $DEPLOYMENT_METHOD"
echo "Image: $IMAGE_REPO:$IMAGE_TAG"
echo "Namespace: $NAMESPACE"
echo ""

# Function: Get current metroculus pod
get_metroculus_pod() {
    kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=metroculusapi -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo ""
}

# Method 1: Quick restart (copy file + restart)
if [ "$DEPLOYMENT_METHOD" == "restart" ]; then
    echo -e "${YELLOW}Method 1: Quick Restart (copy updated file)${NC}"

    POD=$(get_metroculus_pod)
    if [ -z "$POD" ]; then
        echo -e "${RED}✗ Metroculus pod not found${NC}"
        exit 1
    fi

    echo "Pod: $POD"

    # Copy updated file
    echo -e "${YELLOW}Copying updated kubecost_metrics.py...${NC}"
    kubectl cp ${METROCULUS_DIR}/metroculus_api/controllers/kubecost_metrics.py \
        ${NAMESPACE}/${POD}:/metroculus/metroculus_api/controllers/kubecost_metrics.py

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to copy file${NC}"
        exit 1
    fi

    # Restart deployment
    echo -e "${YELLOW}Restarting Metroculus deployment...${NC}"
    kubectl rollout restart deployment/metroculusapi -n $NAMESPACE

    # Wait for rollout
    echo -e "${YELLOW}Waiting for rollout to complete...${NC}"
    kubectl rollout status deployment/metroculusapi -n $NAMESPACE --timeout=120s

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Rollout failed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Metroculus restarted successfully${NC}"

# Method 2: Rebuild image and deploy
elif [ "$DEPLOYMENT_METHOD" == "rebuild" ]; then
    echo -e "${YELLOW}Method 2: Rebuild and Deploy${NC}"

    # Check if Metroculus directory exists
    if [ ! -d "$METROCULUS_DIR" ]; then
        echo -e "${RED}✗ Metroculus directory not found: $METROCULUS_DIR${NC}"
        exit 1
    fi

    cd $METROCULUS_DIR

    # Build image
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t ${IMAGE_REPO}:${IMAGE_TAG} .

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Docker build failed${NC}"
        exit 1
    fi

    # Push image
    echo -e "${YELLOW}Pushing image to registry...${NC}"
    docker push ${IMAGE_REPO}:${IMAGE_TAG}

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Docker push failed${NC}"
        exit 1
    fi

    # Update deployment
    echo -e "${YELLOW}Updating deployment image...${NC}"
    kubectl set image deployment/metroculusapi -n $NAMESPACE \
        metroculusapi=${IMAGE_REPO}:${IMAGE_TAG}

    # Wait for rollout
    echo -e "${YELLOW}Waiting for rollout to complete...${NC}"
    kubectl rollout status deployment/metroculusapi -n $NAMESPACE --timeout=120s

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Rollout failed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Metroculus deployed successfully${NC}"

# Method 3: Helm upgrade
elif [ "$DEPLOYMENT_METHOD" == "helm" ]; then
    echo -e "${YELLOW}Method 3: Helm Upgrade${NC}"

    # Check if Helm chart exists
    if [ ! -d "/Users/balaji/source/code/cloudtuner/cloudtuner-dev-helm/cloud-tuner-dev" ]; then
        echo -e "${RED}✗ Helm chart not found${NC}"
        exit 1
    fi

    cd /Users/balaji/source/code/cloudtuner/cloudtuner-dev-helm

    # Update Helm release
    echo -e "${YELLOW}Upgrading Helm release...${NC}"
    helm upgrade cloud-tuner-dev ./cloud-tuner-dev -n $NAMESPACE \
        --set metroculusapi.image.tag=${IMAGE_TAG}

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Helm upgrade failed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Helm upgrade successful${NC}"

else
    echo -e "${RED}✗ Unknown deployment method: $DEPLOYMENT_METHOD${NC}"
    echo "Valid methods: restart, rebuild, helm"
    exit 1
fi

# Verification
echo ""
echo -e "${YELLOW}Verifying deployment...${NC}"

sleep 5

NEW_POD=$(get_metroculus_pod)
if [ -z "$NEW_POD" ]; then
    echo -e "${RED}✗ Metroculus pod not found after deployment${NC}"
    exit 1
fi

POD_STATUS=$(kubectl get pod -n $NAMESPACE $NEW_POD -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo -e "${RED}✗ Pod not running (status: $POD_STATUS)${NC}"
    kubectl describe pod -n $NAMESPACE $NEW_POD
    exit 1
fi

echo -e "${GREEN}✓ Pod running: $NEW_POD${NC}"

# Check logs for Phase 2 initialization
echo -e "${YELLOW}Checking logs...${NC}"
kubectl logs -n $NAMESPACE $NEW_POD --tail=20 | grep -E "Phase|cluster costs" || true

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Next Steps:"
echo "  1. Test API: curl -s -H \"Secret: <secret>\" \"http://localhost:39069/metroculus/v2/kubecost_cluster_costs?...\""
echo "  2. Watch logs: kubectl logs -n $NAMESPACE -f $NEW_POD | grep -E 'Phase|cluster costs'"
echo "  3. Verify Phase 2: Look for \"Using Phase 2 exporter metrics\" in logs"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  /docs/kubecost/phase-2/metroculus-deployment.md"
echo ""
