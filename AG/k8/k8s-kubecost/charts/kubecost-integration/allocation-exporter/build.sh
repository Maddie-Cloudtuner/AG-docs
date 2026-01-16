#!/bin/bash
# Build and push Kubecost Allocation Exporter Docker image

set -e

# Configuration
IMAGE_REPO="${IMAGE_REPO:-invincibledocker24/kubecost-allocation-exporter}"
IMAGE_TAG="${IMAGE_TAG:-v1.0.0}"
PUSH="${PUSH:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Kubecost Allocation Exporter${NC}"
echo "Repository: $IMAGE_REPO"
echo "Tag: $IMAGE_TAG"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t "${IMAGE_REPO}:${IMAGE_TAG}" .

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Docker image built successfully!${NC}"
echo ""

# Tag as latest
echo -e "${YELLOW}Tagging as latest...${NC}"
docker tag "${IMAGE_REPO}:${IMAGE_TAG}" "${IMAGE_REPO}:latest"

# Push to registry
if [ "$PUSH" = "true" ]; then
    echo -e "${YELLOW}Pushing to registry...${NC}"
    docker push "${IMAGE_REPO}:${IMAGE_TAG}"
    docker push "${IMAGE_REPO}:latest"

    if [ $? -ne 0 ]; then
        echo -e "${RED}Docker push failed!${NC}"
        exit 1
    fi

    echo -e "${GREEN}Images pushed successfully!${NC}"
else
    echo -e "${YELLOW}Skipping push (PUSH=false)${NC}"
fi

echo ""
echo -e "${GREEN}✓ Build complete!${NC}"
echo ""
echo "Image: ${IMAGE_REPO}:${IMAGE_TAG}"
echo ""
echo "To deploy:"
echo "  helm upgrade --install kubecost-integration ../../ \\"
echo "    --set allocationExporter.enabled=true \\"
echo "    --set allocationExporter.image.tag=${IMAGE_TAG} \\"
echo "    --set allocationExporter.config.tenantId=<your-cloud-account-id>"
