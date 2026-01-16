#!/bin/bash
# Phase 2 Kubecost Integration Verification Script
# Tests all components of the allocation exporter deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-kubecost-dev}"
RELEASE_NAME="${RELEASE_NAME:-kubecost-dev}"
TENANT_ID="${TENANT_ID:-d603f6e0-aff4-4e89-962d-c56f16b69404}"
CLOUD_ACCOUNT_ID="${CLOUD_ACCOUNT_ID:-5635f99d-4dc6-4e31-891f-4e8990925c83}"
METROCULUS_SECRET="${METROCULUS_SECRET:-fc83d31-461d-44c5-b4d5-41a32d6c36a1}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Phase 2 Verification Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Namespace: $NAMESPACE"
echo "Release: $RELEASE_NAME"
echo "Tenant ID: $TENANT_ID"
echo ""

# Test 1: Check Exporter Pod
echo -e "${YELLOW}[1/8] Checking Allocation Exporter Pod...${NC}"
EXPORTER_POD=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=kubecost-allocation-exporter -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$EXPORTER_POD" ]; then
    echo -e "${RED}✗ Exporter pod not found${NC}"
    exit 1
fi

POD_STATUS=$(kubectl get pod -n $NAMESPACE $EXPORTER_POD -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo -e "${RED}✗ Exporter pod not running (status: $POD_STATUS)${NC}"
    kubectl describe pod -n $NAMESPACE $EXPORTER_POD
    exit 1
fi

echo -e "${GREEN}✓ Exporter pod running: $EXPORTER_POD${NC}"

# Test 2: Check Exporter Logs
echo -e "${YELLOW}[2/8] Checking Exporter Logs...${NC}"
LAST_LOG=$(kubectl logs -n $NAMESPACE $EXPORTER_POD --tail=5 | grep "Exported cluster-level metrics" | tail -1)

if [ -z "$LAST_LOG" ]; then
    echo -e "${RED}✗ No recent export logs found${NC}"
    kubectl logs -n $NAMESPACE $EXPORTER_POD --tail=20
    exit 1
fi

echo -e "${GREEN}✓ Last export: $LAST_LOG${NC}"

# Test 3: Check Exporter Metrics Endpoint
echo -e "${YELLOW}[3/8] Checking Exporter Metrics Endpoint...${NC}"
kubectl port-forward -n $NAMESPACE svc/kubecost-allocation-exporter 9103:9103 > /dev/null 2>&1 &
PF_PID=$!
sleep 3

CLUSTER_COST=$(curl -s http://localhost:9103/metrics 2>/dev/null | grep "^cloudtuner_kubecost_cluster_total_cost{" | awk '{print $2}')
kill $PF_PID 2>/dev/null || true

if [ -z "$CLUSTER_COST" ]; then
    echo -e "${RED}✗ No cluster cost metric found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Cluster total cost: \$$CLUSTER_COST/hour${NC}"

# Test 4: Check Prometheus Server
echo -e "${YELLOW}[4/8] Checking Prometheus Server...${NC}"
PROM_POD=$(kubectl get pods -n $NAMESPACE -l app=prometheus,component=server -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$PROM_POD" ]; then
    echo -e "${RED}✗ Prometheus pod not found${NC}"
    exit 1
fi

POD_STATUS=$(kubectl get pod -n $NAMESPACE $PROM_POD -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo -e "${RED}✗ Prometheus pod not running (status: $POD_STATUS)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prometheus pod running: $PROM_POD${NC}"

# Test 5: Check Prometheus Has Metrics
echo -e "${YELLOW}[5/8] Checking Prometheus Scraped Metrics...${NC}"
kubectl port-forward -n $NAMESPACE svc/${RELEASE_NAME}-prometheus-server 9090:80 > /dev/null 2>&1 &
PF_PID=$!
sleep 3

PROM_RESULT=$(curl -s 'http://localhost:9090/api/v1/query?query=cloudtuner_kubecost_exporter_scrape_success' 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['result'][0]['value'][1] if d['data']['result'] else '0')" 2>/dev/null || echo "0")
kill $PF_PID 2>/dev/null || true

if [ "$PROM_RESULT" != "1" ]; then
    echo -e "${RED}✗ Exporter metrics not in Prometheus (scrape_success=$PROM_RESULT)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prometheus successfully scraping exporter${NC}"

# Test 6: Check Remote Write
echo -e "${YELLOW}[6/8] Checking Prometheus Remote Write...${NC}"
kubectl port-forward -n $NAMESPACE svc/${RELEASE_NAME}-prometheus-server 9090:80 > /dev/null 2>&1 &
PF_PID=$!
sleep 3

REMOTE_SAMPLES=$(curl -s 'http://localhost:9090/api/v1/query?query=prometheus_remote_storage_samples_total' 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); results=d['data']['result']; print(results[0]['value'][1] if results else '0')" 2>/dev/null || echo "0")
kill $PF_PID 2>/dev/null || true

if [ "$REMOTE_SAMPLES" == "0" ]; then
    echo -e "${RED}✗ No samples sent via remote_write${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Remote write active: $REMOTE_SAMPLES samples sent${NC}"

# Test 7: Check Kubecost
echo -e "${YELLOW}[7/8] Checking Kubecost Cost Analyzer...${NC}"
KUBECOST_POD=$(kubectl get pods -n $NAMESPACE -o name 2>/dev/null | grep "^pod/${RELEASE_NAME}-[a-z0-9]\+-[a-z0-9]\+$" | grep -v exporter | grep -v prometheus | head -1 | sed 's/pod\///' || echo "")

if [ -z "$KUBECOST_POD" ]; then
    echo -e "${RED}✗ Kubecost pod not found${NC}"
    exit 1
fi

POD_STATUS=$(kubectl get pod -n $NAMESPACE $KUBECOST_POD -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo -e "${RED}✗ Kubecost pod not running (status: $POD_STATUS)${NC}"
    exit 1
fi

# Check if all containers ready
CONTAINERS_READY=$(kubectl get pod -n $NAMESPACE $KUBECOST_POD -o jsonpath='{.status.containerStatuses[*].ready}' | tr ' ' '\n' | grep -c "true")
CONTAINERS_TOTAL=$(kubectl get pod -n $NAMESPACE $KUBECOST_POD -o jsonpath='{.status.containerStatuses[*].ready}' | wc -w | tr -d ' ')

if [ "$CONTAINERS_READY" != "$CONTAINERS_TOTAL" ]; then
    echo -e "${YELLOW}⚠ Kubecost containers not all ready ($CONTAINERS_READY/$CONTAINERS_TOTAL)${NC}"
else
    echo -e "${GREEN}✓ Kubecost running: $KUBECOST_POD ($CONTAINERS_READY/$CONTAINERS_TOTAL containers ready)${NC}"
fi

# Test 8: Check Metroculus (Optional)
echo -e "${YELLOW}[8/8] Checking Metroculus API (Optional)...${NC}"
METROCULUS_POD=$(kubectl get pods -n default -l app.kubernetes.io/name=metroculusapi -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$METROCULUS_POD" ]; then
    echo -e "${YELLOW}⚠ Metroculus pod not found (skipping)${NC}"
else
    kubectl port-forward -n default svc/metroculusapi 39069:80 > /dev/null 2>&1 &
    PF_PID=$!
    sleep 3

    START_DATE=$(date -u -v-1d +%s 2>/dev/null || date -u -d "1 day ago" +%s)
    END_DATE=$(date -u +%s)

    METROCULUS_RESPONSE=$(curl -s -H "Secret: $METROCULUS_SECRET" \
        "http://localhost:39069/metroculus/v2/kubecost_cluster_costs?cloud_account_id=$TENANT_ID&start_date=$START_DATE&end_date=$END_DATE" 2>/dev/null || echo "")

    kill $PF_PID 2>/dev/null || true

    if [ -z "$METROCULUS_RESPONSE" ]; then
        echo -e "${YELLOW}⚠ Metroculus API not responding (may not be deployed)${NC}"
    elif echo "$METROCULUS_RESPONSE" | grep -q "error\|Error"; then
        echo -e "${YELLOW}⚠ Metroculus API returned error${NC}"
    else
        echo -e "${GREEN}✓ Metroculus API responding${NC}"
    fi
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ All Core Checks Passed!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Summary:"
echo "  • Exporter: $EXPORTER_POD"
echo "  • Cluster Cost: \$$CLUSTER_COST/hour"
echo "  • Prometheus Scraping: Active"
echo "  • Remote Write: $REMOTE_SAMPLES samples"
echo "  • Kubecost: Running ($CONTAINERS_READY/$CONTAINERS_TOTAL)"
echo ""
echo "Next Steps:"
echo "  1. Verify metrics in Thanos"
echo "  2. Update Metroculus API to use exporter metrics"
echo "  3. Test end-to-end flow"
echo ""
echo -e "${BLUE}For detailed verification, see:${NC}"
echo "  /docs/kubecost/phase-2/deployment-summary.md"
echo "  /docs/kubecost/phase-2/completion-plan.md"
echo ""
