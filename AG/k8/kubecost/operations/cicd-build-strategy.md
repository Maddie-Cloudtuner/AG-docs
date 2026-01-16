# Cloud-Tuner CI/CD Build Strategy & Service Dependencies

## Executive Summary

This document provides a comprehensive strategy for managing image builds, versioning, and CI/CD automation for the Cloud-Tuner platform upgrade from v1.3.0 to v1.4.0.

**Key Metrics:**
- Total Services: 82 container images
- Services with Tools Dependencies: 19 (requires rebuild on tools changes)
- Standalone Services: 63 (can be retagged or built independently)
- Critical Build Triggers: 3 (cloud_adapter, optscale_time, optscale_exceptions)

---

## 1. Service Classification for CI/CD

### Category A: RETAG ONLY (35 services)
**Description:** Infrastructure and stable services with no code dependencies on tools/
**Action:** Simple retag from v1.3.0 → v1.4.0 (no rebuild needed unless service code changed)
**Build Time:** ~5 minutes (retag + push)

| Service | Current Tag | Repository | Notes |
|---------|-------------|------------|-------|
| etcd | v1.3.0 | invincibledocker24/etcd | Infrastructure |
| mariadb | v1.3.0 | invincibledocker24/mariadb | Database |
| mongo | v1.3.0-dev | invincibledocker24/mongo | Database |
| rabbitmq | v1.3.0 | invincibledocker24/rabbitmq | Message queue |
| redis | v1.3.0 | invincibledocker24/redis | Cache |
| phpmyadmin | v1.3.0 | invincibledocker24/phpmyadmin | Admin UI |
| elk | v1.3.0 | invincibledocker24/elk | Logging |
| filebeat | v1.3.0 | invincibledocker24/filebeat | Log shipper |
| minio | v1.3.0 | invincibledocker24/minio | Object storage |
| influxdb | v1.3.0 | invincibledocker24/influxdb | Time-series DB |
| grafana | v1.3.0 | invincibledocker24/grafana | Monitoring UI |
| grafana-nginx | v1.3.0 | invincibledocker24/grafana_nginx | Reverse proxy |
| error_pages | v1.3.0 | invincibledocker24/error_pages | Static pages |
| admin | v1.3.0 | invincibledocker24/admin | Admin service |
| keeper | v1.3.0 | invincibledocker24/keeper | Key management |
| herald | v1.3.0 | invincibledocker24/herald | Notification engine |
| slacker | v1.3.0 | invincibledocker24/slacker | Slack integration |
| ohsu | v1.3.0 | invincibledocker24/ohsu | Workflow engine |
| diproxy | v1.3.0 | invincibledocker24/diproxy | Metrics proxy |
| thanos-receive | v1.3.0 | invincibledocker24/thanos-receive | Metrics ingestion |
| thanos-storegateway | v1.3.0 | invincibledocker24/thanos-storegateway | Long-term storage |
| thanos-query | v1.3.0 | invincibledocker24/thanos-query | Metrics query |
| thanos-compactor | v1.3.0 | invincibledocker24/thanos-compactor | Data compaction |
| thanos-web | v1.3.0 | invincibledocker24/thanos-web | Metrics UI |
| pharos_receiver | v1.3.0 | invincibledocker24/pharos_receiver | Event receiver |
| pharos_worker | v1.3.0 | invincibledocker24/pharos_worker | Event processor |
| webhook_executor | v1.3.0 | invincibledocker24/webhook_executor | Webhook handler |
| slacker_executor | v1.3.0 | invincibledocker24/slacker_executor | Slack executor |
| herald_executor | v1.3.0 | invincibledocker24/herald_executor | Notification executor |
| keeper_executor | v1.3.0 | invincibledocker24/keeper_executor | Key executor |
| cleaninfluxdb | v1.3.0 | invincibledocker24/cleaninfluxdb | DB cleanup |
| cleanmongodb | v1.3.0 | invincibledocker24/cleanmongodb | DB cleanup |
| cleanelkdb | v1.3.0 | invincibledocker24/cleanelkdb | DB cleanup |
| layout_cleaner | v1.3.0 | invincibledocker24/layout_cleaner | Data cleanup |
| monthly_bill_generator | v1.3.0 | invincibledocker24/monthly_bill_generator | Billing |

**Retag Script:**
```bash
#!/bin/bash
# retag-stable-services.sh
SERVICES=(
  "etcd" "mariadb" "rabbitmq" "redis" "phpmyadmin" "elk" "filebeat"
  "minio" "influxdb" "grafana" "grafana_nginx" "error_pages" "admin"
  "keeper" "herald" "slacker" "ohsu" "diproxy" "thanos-receive"
  "thanos-storegateway" "thanos-query" "thanos-compactor" "thanos-web"
  "pharos_receiver" "pharos_worker" "webhook_executor" "slacker_executor"
  "herald_executor" "keeper_executor" "cleaninfluxdb" "cleanmongodb"
  "cleanelkdb" "layout_cleaner" "monthly_bill_generator"
)

for service in "${SERVICES[@]}"; do
  docker pull invincibledocker24/${service}:v1.3.0
  docker tag invincibledocker24/${service}:v1.3.0 invincibledocker24/${service}:v1.4.0
  docker push invincibledocker24/${service}:v1.4.0
done
```

---

### Category B: SCHEDULERS - BUILD ON DEMAND (15 services)
**Description:** Scheduler services that trigger workers (minimal code, usually cron wrappers)
**Action:** Rebuild only if scheduler logic changed, otherwise retag
**Build Time:** ~2-3 minutes each (simple Python scripts)

| Service | Dependencies | Rebuild Trigger |
|---------|--------------|-----------------|
| bumischeduler | None | Schedule logic change |
| insider_scheduler | optscale_time | Schedule + tools change |
| metroculus_scheduler | optscale_time | Schedule + tools change |
| trapper_scheduler | optscale_time | Schedule + tools change |
| risp_scheduler | None | Schedule logic change |
| gemini_scheduler | optscale_time | Schedule + tools change |
| bi_scheduler | optscale_time | Schedule + tools change |
| report_import_scheduler | None | Schedule logic change |
| demo_org_cleanup | None | Schedule logic change |
| resource_observer | None | Schedule logic change |
| resource_violations | None | Schedule logic change |
| calendar_observer | optscale_time | Schedule + tools change |
| booking_observer | None | Schedule logic change |
| organization_violations | None | Schedule logic change |
| power_schedule | cloud_adapter, optscale_time | Schedule + tools change |

**Build Strategy:**
- Default: Retag from v1.3.0
- If tools/optscale_time changed: Rebuild schedulers with optscale_time dependency
- If cloud_adapter changed: Rebuild power_schedule

---

### Category C: TOOLS-DEPENDENT SERVICES (19 services) ⚠️
**Description:** Services with dependencies on /tools/ folder - MUST rebuild when tools change
**Action:** ALWAYS rebuild when tools modules change
**Build Time:** ~10-15 minutes each (includes dependencies)

#### C1: Critical Path Services (5 services - highest priority)

| Service | Tools Dependencies | Rebuild Priority | Build Time |
|---------|-------------------|------------------|------------|
| **restapi** | cloud_adapter, optscale_types | P0 - CRITICAL | 15 min |
| **auth** | optscale_time, optscale_exceptions | P0 - CRITICAL | 12 min |
| **payments** | optscale_time, optscale_exceptions | P0 - CRITICAL | 10 min |
| **diworker** | cloud_adapter, optscale_time, optscale_data | P1 - HIGH | 12 min |
| **bumiworker** | cloud_adapter, optscale_time | P1 - HIGH | 10 min |

#### C2: Worker Services (9 services - parallel build possible)

| Service | Tools Dependencies | Build Priority | Can Build Parallel |
|---------|-------------------|----------------|-------------------|
| insider_api | cloud_adapter, optscale_time, optscale_exceptions | P1 | Yes (insider family) |
| insider_worker | optscale_time | P2 | Yes (insider family) |
| metroculus_api | cloud_adapter, optscale_time, optscale_exceptions | P1 | Yes (metroculus family) |
| metroculus_worker | cloud_adapter, optscale_time | P2 | Yes (metroculus family) |
| risp_worker | cloud_adapter, optscale_time | P2 | Yes (risp family) |
| trapper_worker | cloud_adapter, optscale_time | P2 | Yes (trapper family) |
| gemini_worker | optscale_time | P2 | Yes (standalone) |
| bi_exporter | optscale_time, optscale_exceptions | P2 | Yes (standalone) |
| resource_discovery | cloud_adapter, optscale_time | P1 | Yes (standalone) |

#### C3: Frontend & Utilities (5 services)

| Service | Tools Dependencies | Build Priority | Notes |
|---------|-------------------|----------------|-------|
| ngui | None (but check if using API client) | P2 | Frontend rebuild |
| chat_agent | None (AI service) | P3 | Independent |
| agentic_chatbot | None (AI service) | P3 | Independent |
| failed_imports_dataset_generator | optscale_time | P3 | Utility |
| users_dataset_generator | optscale_time | P3 | Utility |

---

### Category D: RAPID DEVELOPMENT SERVICES (8 services)
**Description:** Services frequently modified during development cycles
**Action:** Manual build + versioning (use dev tags: v1.4.0-dev, v1.4.0-dev-2, etc.)
**Build Time:** Variable (5-15 minutes each)

| Service | Current Tag | Development Pattern | Notes |
|---------|-------------|---------------------|-------|
| diworker | v1.3.0-dev-4 | Frequent updates | Data ingestion changes |
| katara_service | v1.3.0-dev | Active development | Cost optimization |
| katara_worker | v1.3.0-dev | Active development | Worker companion |
| restapi | v1.3.0-co2 | Feature branches | CO2 tracking feature |
| ngui | v1.3.0-dev-chatbot | Feature branches | UI with chatbot |
| mongo | v1.3.0-dev | Database iterations | Schema changes |
| agentic_chatbot | v1.3.1 | Independent versioning | AI model updates |
| mcp-mongo | 0.1.0 | Independent versioning | MCP server |
| mcp-maria | 0.1.0 | Independent versioning | MCP server |

**Versioning Strategy for Dev Services:**
```
v1.4.0-dev          # First development iteration
v1.4.0-dev-2        # Second iteration (bug fixes)
v1.4.0-dev-feature  # Feature-specific builds
v1.4.0-co2          # Feature branch (CO2 tracking)
v1.4.0              # Final stable release
```

---

## 2. Tools Dependencies Matrix

### Tools Modules Impact Analysis

| Tools Module | Affected Services | Rebuild Count | Impact Level |
|--------------|-------------------|---------------|--------------|
| **cloud_adapter** | restapi, diworker, bumiworker, insider_api, metroculus_api, metroculus_worker, risp_worker, trapper_worker, power_schedule, resource_discovery | 10 | 🔴 CRITICAL |
| **optscale_time** | auth, payments, diworker, bumiworker, insider_api, insider_worker, insider_scheduler, metroculus_api, metroculus_worker, metroculus_scheduler, risp_worker, trapper_worker, trapper_scheduler, gemini_worker, gemini_scheduler, bi_scheduler, bi_exporter, power_schedule, resource_discovery + utilities | 19 | 🔴 CRITICAL |
| **optscale_exceptions** | auth, payments, insider_api, metroculus_api, bi_exporter | 5 | 🟡 MEDIUM |
| **optscale_data** | diworker | 1 | 🟢 LOW |
| **optscale_types** | restapi | 1 | 🟢 LOW |
| **optscale_password** | (none found) | 0 | ⚪ NONE |
| **cloudtuner_bill** | (none found) | 0 | ⚪ NONE |

### Build Trigger Rules

**IF changed: `tools/cloud_adapter`** → Rebuild:
```
1. restapi (P0)
2. diworker (P1)
3. bumiworker (P1)
4. insider_api (P1)
5. metroculus_api (P1)
6. metroculus_worker (P2)
7. risp_worker (P2)
8. trapper_worker (P2)
9. power_schedule (P2)
10. resource_discovery (P1)
```
**Total: 10 services, Est. time: 100-120 minutes (sequential), 30-40 minutes (parallel)**

**IF changed: `tools/optscale_time`** → Rebuild:
```
All 19 services listed above + schedulers
```
**Total: 19 services, Est. time: 180-220 minutes (sequential), 45-60 minutes (parallel)**

**IF changed: `tools/optscale_exceptions`** → Rebuild:
```
1. auth (P0)
2. payments (P0)
3. insider_api (P1)
4. metroculus_api (P1)
5. bi_exporter (P2)
```
**Total: 5 services, Est. time: 50-60 minutes (sequential), 15-20 minutes (parallel)**

---

## 3. CI/CD Pipeline Design

### Pipeline Stages

```
┌─────────────────────────────────────────────────────────────┐
│ STAGE 0: Version Bump & Change Detection (1-2 min)         │
├─────────────────────────────────────────────────────────────┤
│ • Update version in values.yaml: v1.3.0 → v1.4.0           │
│ • Git diff to detect changed modules                        │
│ • Determine rebuild scope based on changes                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: Tools & Common Libraries (5-10 min)               │
├─────────────────────────────────────────────────────────────┤
│ • Build all tools/* modules (if changed)                    │
│ • Build optscale_client/* modules (if changed)              │
│ • Publish to internal PyPI or package repository            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: Critical Path Services (10-15 min, parallel)      │
├─────────────────────────────────────────────────────────────┤
│ Parallel Jobs:                                              │
│   Job A: restapi (if tools changed OR code changed)         │
│   Job B: auth (if tools changed OR code changed)            │
│   Job C: payments (if tools changed OR code changed)        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: Worker Layer (10-15 min, parallel)                │
├─────────────────────────────────────────────────────────────┤
│ Parallel Jobs:                                              │
│   Job A: diworker + bumiworker                              │
│   Job B: insider_api + insider_worker                       │
│   Job C: metroculus_api + metroculus_worker                 │
│   Job D: risp_worker + trapper_worker                       │
│   Job E: resource_discovery + power_schedule                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 4: Schedulers & Utilities (5-10 min, parallel)       │
├─────────────────────────────────────────────────────────────┤
│ • All scheduler services (if tools changed)                 │
│ • Utility services (bi_exporter, gemini_worker, etc.)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 5: Frontend & AI Services (5-10 min, parallel)       │
├─────────────────────────────────────────────────────────────┤
│   Job A: ngui                                               │
│   Job B: agentic_chatbot                                    │
│   Job C: chat_agent                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 6: Retag Stable Services (5 min)                     │
├─────────────────────────────────────────────────────────────┤
│ • Bulk retag all Category A services                        │
│ • Fast operation (pull, tag, push)                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 7: Update Helm Chart & Deploy (2-5 min)              │
├─────────────────────────────────────────────────────────────┤
│ • Update values.yaml with new versions                      │
│ • Commit changes                                            │
│ • Deploy to dev/staging environment                         │
└─────────────────────────────────────────────────────────────┘
```

### Build Time Estimates

| Scenario | Sequential Time | Parallel Time | Services Built |
|----------|----------------|---------------|----------------|
| **Full Release (All)** | 240-300 min (~4-5 hours) | 60-90 min (~1-1.5 hours) | 82 services |
| **Tools: cloud_adapter changed** | 100-120 min | 30-40 min | 10 services |
| **Tools: optscale_time changed** | 180-220 min | 45-60 min | 19 services |
| **Tools: optscale_exceptions changed** | 50-60 min | 15-20 min | 5 services |
| **Single service changed** | 10-15 min | 10-15 min | 1 service |
| **Dev iteration (3-5 services)** | 30-45 min | 15-20 min | 3-5 services |

---

## 4. GitHub Actions Workflow Examples

### Workflow 1: Smart Build on Tools Change

```yaml
# .github/workflows/smart-build.yml
name: Smart Build on Changes

on:
  push:
    branches: [main, develop]
    paths:
      - 'tools/**'
      - '**/requirements.txt'
      - '**/Dockerfile'

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      cloud_adapter_changed: ${{ steps.changes.outputs.cloud_adapter }}
      optscale_time_changed: ${{ steps.changes.outputs.optscale_time }}
      optscale_exceptions_changed: ${{ steps.changes.outputs.optscale_exceptions }}
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 2

      - name: Detect changed tools
        id: changes
        run: |
          if git diff HEAD^ HEAD --name-only | grep -q "tools/cloud_adapter"; then
            echo "cloud_adapter=true" >> $GITHUB_OUTPUT
          fi
          if git diff HEAD^ HEAD --name-only | grep -q "tools/optscale_time"; then
            echo "optscale_time=true" >> $GITHUB_OUTPUT
          fi
          if git diff HEAD^ HEAD --name-only | grep -q "tools/optscale_exceptions"; then
            echo "optscale_exceptions=true" >> $GITHUB_OUTPUT
          fi

  build-cloud-adapter-dependents:
    needs: detect-changes
    if: needs.detect-changes.outputs.cloud_adapter_changed == 'true'
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service:
          - restapi
          - diworker
          - bumiworker
          - insider/insider_api
          - metroculus/metroculus_api
          - metroculus/metroculus_worker
          - risp/risp_worker
          - trapper/trapper_worker
          - docker_images/power_schedule
          - docker_images/resource_discovery
    steps:
      - uses: actions/checkout@v3

      - name: Build ${{ matrix.service }}
        run: |
          cd ${{ matrix.service }}
          docker build -t invincibledocker24/${{ matrix.service }}:v1.4.0 .
          docker push invincibledocker24/${{ matrix.service }}:v1.4.0

  build-optscale-time-dependents:
    needs: detect-changes
    if: needs.detect-changes.outputs.optscale_time_changed == 'true'
    runs-on: ubuntu-latest
    strategy:
      max-parallel: 5
      matrix:
        service:
          - auth/auth_server
          - payments/payments_server
          - diworker
          - bumiworker
          # ... add all 19 services
    steps:
      - uses: actions/checkout@v3

      - name: Build ${{ matrix.service }}
        run: |
          cd ${{ matrix.service }}
          docker build -t invincibledocker24/${{ matrix.service }}:v1.4.0 .
          docker push invincibledocker24/${{ matrix.service }}:v1.4.0
```

### Workflow 2: Version Bump & Retag

```yaml
# .github/workflows/version-bump.yml
name: Version Bump v1.3.0 → v1.4.0

on:
  workflow_dispatch:
    inputs:
      old_version:
        description: 'Old version (e.g., v1.3.0)'
        required: true
        default: 'v1.3.0'
      new_version:
        description: 'New version (e.g., v1.4.0)'
        required: true
        default: 'v1.4.0'

jobs:
  retag-stable-services:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service:
          - etcd
          - mariadb
          - rabbitmq
          - redis
          - minio
          # ... all Category A services
    steps:
      - name: Retag ${{ matrix.service }}
        run: |
          docker pull invincibledocker24/${{ matrix.service }}:${{ github.event.inputs.old_version }}
          docker tag invincibledocker24/${{ matrix.service }}:${{ github.event.inputs.old_version }} \
                     invincibledocker24/${{ matrix.service }}:${{ github.event.inputs.new_version }}
          docker push invincibledocker24/${{ matrix.service }}:${{ github.event.inputs.new_version }}

  update-helm-chart:
    needs: retag-stable-services
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Update values.yaml
        run: |
          sed -i "s/tag: &tag ${{ github.event.inputs.old_version }}/tag: &tag ${{ github.event.inputs.new_version }}/g" \
            cloud-tuner-dev/values.yaml

      - name: Commit changes
        run: |
          git config user.name "CI Bot"
          git config user.email "ci@cloudtuner.io"
          git add cloud-tuner-dev/values.yaml
          git commit -m "chore: bump version to ${{ github.event.inputs.new_version }}"
          git push
```

### Workflow 3: Individual Service Build

```yaml
# .github/workflows/build-service.yml
name: Build Individual Service

on:
  workflow_dispatch:
    inputs:
      service_name:
        description: 'Service to build (e.g., restapi, diworker)'
        required: true
      version_tag:
        description: 'Version tag (e.g., v1.4.0-dev, v1.4.0)'
        required: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build ${{ github.event.inputs.service_name }}
        run: |
          cd ${{ github.event.inputs.service_name }}
          docker build -t invincibledocker24/${{ github.event.inputs.service_name }}:${{ github.event.inputs.version_tag }} .
          docker push invincibledocker24/${{ github.event.inputs.service_name }}:${{ github.event.inputs.version_tag }}
```

---

## 5. Manual Build Checklists

### Checklist 1: Full v1.4.0 Release Build

```markdown
## Pre-Build
- [ ] Update version in values.yaml: v1.3.0 → v1.4.0
- [ ] Review all changed files since last release
- [ ] Identify which tools modules changed
- [ ] Run tests for changed services

## Build Phase 1: Tools (if changed)
- [ ] Build tools/cloud_adapter
- [ ] Build tools/optscale_time
- [ ] Build tools/optscale_exceptions
- [ ] Build tools/optscale_data
- [ ] Build tools/optscale_types

## Build Phase 2: Critical Services
- [ ] Build restapi → v1.4.0
- [ ] Build auth → v1.4.0
- [ ] Build payments → v1.4.0

## Build Phase 3: Workers (parallel)
- [ ] Build diworker → v1.4.0
- [ ] Build bumiworker → v1.4.0
- [ ] Build insider_api → v1.4.0
- [ ] Build insider_worker → v1.4.0
- [ ] Build metroculus_api → v1.4.0
- [ ] Build metroculus_worker → v1.4.0
- [ ] Build risp_worker → v1.4.0
- [ ] Build trapper_worker → v1.4.0
- [ ] Build resource_discovery → v1.4.0
- [ ] Build power_schedule → v1.4.0

## Build Phase 4: Schedulers & Utilities
- [ ] Build all schedulers (if optscale_time changed)
- [ ] Build bi_exporter → v1.4.0
- [ ] Build gemini_worker → v1.4.0

## Build Phase 5: Frontend
- [ ] Build ngui → v1.4.0
- [ ] Build agentic_chatbot → v1.4.1
- [ ] Build chat_agent → v1.4.0

## Retag Phase
- [ ] Run retag script for all 35 Category A services

## Post-Build
- [ ] Update IMAGE_VERSIONS.md
- [ ] Test deploy to dev environment
- [ ] Verify all services start successfully
- [ ] Run smoke tests
- [ ] Tag git release: v1.4.0
```

### Checklist 2: Quick Dev Iteration Build

```markdown
## Scenario: Working on diworker + cloud_adapter changes

- [ ] Identify changed files
- [ ] Update diworker to v1.4.0-dev-5
- [ ] Build cloud_adapter module
- [ ] Build diworker → v1.4.0-dev-5
- [ ] Update values.yaml with dev tag
- [ ] Deploy to dev namespace
- [ ] Test changes
- [ ] If stable, retag to v1.4.0
```

---

## 6. Service Family Build Groups

For parallel builds, group related services together:

### Group A: Core Platform (Sequential, P0)
```
1. restapi (15 min)
2. auth (12 min)
3. payments (10 min)
Total: 37 minutes
```

### Group B: Data Workers (Parallel, P1)
```
Parallel:
- diworker (12 min)
- bumiworker (10 min)
- resource_discovery (10 min)
Total: 12 minutes (parallel)
```

### Group C: Insider Family (Parallel, P2)
```
Parallel:
- insider_api (12 min)
- insider_worker (8 min)
- insider_scheduler (3 min)
Total: 12 minutes (parallel)
```

### Group D: Metroculus Family (Parallel, P2)
```
Parallel:
- metroculus_api (12 min)
- metroculus_worker (10 min)
- metroculus_scheduler (3 min)
Total: 12 minutes (parallel)
```

### Group E: RISP + Trapper (Parallel, P2)
```
Parallel:
- risp_worker (10 min)
- risp_scheduler (3 min)
- trapper_worker (10 min)
- trapper_scheduler (3 min)
Total: 10 minutes (parallel)
```

### Group F: Remaining Workers (Parallel, P3)
```
Parallel:
- gemini_worker (8 min)
- gemini_scheduler (3 min)
- bi_exporter (8 min)
- bi_scheduler (3 min)
Total: 8 minutes (parallel)
```

---

## 7. Quick Reference Commands

### Build a single service
```bash
cd /Users/balaji/source/code/cloudtuner/cloud-tuner/{service_name}
docker build -t invincibledocker24/{service_name}:v1.4.0 .
docker push invincibledocker24/{service_name}:v1.4.0
```

### Retag existing image
```bash
docker pull invincibledocker24/{service_name}:v1.3.0
docker tag invincibledocker24/{service_name}:v1.3.0 invincibledocker24/{service_name}:v1.4.0
docker push invincibledocker24/{service_name}:v1.4.0
```

### Build service family (parallel)
```bash
# Terminal 1
cd insider/insider_api && docker build -t invincibledocker24/insider_api:v1.4.0 . && docker push invincibledocker24/insider_api:v1.4.0

# Terminal 2
cd insider/insider_worker && docker build -t invincibledocker24/insider_worker:v1.4.0 . && docker push invincibledocker24/insider_worker:v1.4.0

# Terminal 3
cd insider/insider_scheduler && docker build -t invincibledocker24/insider_scheduler:v1.4.0 . && docker push invincibledocker24/insider_scheduler:v1.4.0
```

### Check which services need rebuild (after tools change)
```bash
# If cloud_adapter changed:
echo "Rebuild: restapi diworker bumiworker insider_api metroculus_api metroculus_worker risp_worker trapper_worker power_schedule resource_discovery"

# If optscale_time changed:
echo "Rebuild: ALL 19 services + schedulers"

# If optscale_exceptions changed:
echo "Rebuild: auth payments insider_api metroculus_api bi_exporter"
```

---

## 8. Recommendations for v1.4.0 Upgrade

### Pre-Upgrade Planning
1. **Audit all code changes since v1.3.0**
   - Run: `git log v1.3.0..HEAD --name-only`
   - Identify which services have actual code changes

2. **Check tools module changes**
   - Most critical: cloud_adapter, optscale_time
   - Determine rebuild scope based on changes

3. **Prioritize build order**
   - Critical path services first (restapi, auth, payments)
   - Workers second
   - Schedulers and utilities last

### Build Strategy Options

**Option 1: Conservative (Full Rebuild)**
- Rebuild all 47 tools-dependent services
- Retag remaining 35 stable services
- Time: 60-90 minutes (parallel)
- Confidence: Highest

**Option 2: Smart Rebuild (Recommended)**
- Rebuild only services with code changes OR tools dependencies
- Retag all unchanged services
- Time: 30-60 minutes (depending on changes)
- Confidence: High

**Option 3: Minimal Rebuild**
- Rebuild only services with actual code changes
- Retag everything else
- Time: 15-30 minutes
- Confidence: Medium (requires thorough testing)

### Post-Upgrade Validation
1. Deploy to dev environment
2. Run smoke tests on critical services:
   - REST API health check
   - Auth flow test
   - Worker job submission test
   - Metrics ingestion test
3. Monitor logs for 24 hours
4. Gradual rollout to staging → production

---

## 9. Future Improvements

### Short-term (v1.4.x)
- [ ] Implement automated dependency detection
- [ ] Create build matrix in CI/CD
- [ ] Add build caching for faster rebuilds
- [ ] Implement smoke test suite

### Medium-term (v1.5.x)
- [ ] Migrate to monorepo with unified versioning
- [ ] Implement semantic versioning for tools modules
- [ ] Create service dependency graph visualization
- [ ] Add automated rollback on failed deployments

### Long-term (v2.0)
- [ ] Migrate to Kubernetes-native CI/CD (Argo CD, Flux)
- [ ] Implement GitOps workflow
- [ ] Add automated canary deployments
- [ ] Create service mesh for better observability

---

## Appendix: Service Build Matrix

| Service | Category | Tools Deps | Build Time | Priority | Parallel Group |
|---------|----------|------------|------------|----------|----------------|
| restapi | C1 | cloud_adapter, optscale_types | 15m | P0 | Core-A |
| auth | C1 | optscale_time, optscale_exceptions | 12m | P0 | Core-A |
| payments | C1 | optscale_time, optscale_exceptions | 10m | P0 | Core-A |
| diworker | C1 | cloud_adapter, optscale_time, optscale_data | 12m | P1 | Workers-B |
| bumiworker | C1 | cloud_adapter, optscale_time | 10m | P1 | Workers-B |
| insider_api | C2 | cloud_adapter, optscale_time, optscale_exceptions | 12m | P1 | Insider-C |
| insider_worker | C2 | optscale_time | 8m | P2 | Insider-C |
| metroculus_api | C2 | cloud_adapter, optscale_time, optscale_exceptions | 12m | P1 | Metroculus-D |
| metroculus_worker | C2 | cloud_adapter, optscale_time | 10m | P2 | Metroculus-D |
| risp_worker | C2 | cloud_adapter, optscale_time | 10m | P2 | RISP-E |
| trapper_worker | C2 | cloud_adapter, optscale_time | 10m | P2 | Trapper-E |
| gemini_worker | C2 | optscale_time | 8m | P2 | Workers-F |
| bi_exporter | C2 | optscale_time, optscale_exceptions | 8m | P2 | Workers-F |
| resource_discovery | C2 | cloud_adapter, optscale_time | 10m | P1 | Workers-B |
| power_schedule | C2 | cloud_adapter, optscale_time | 8m | P2 | Workers-B |

---

**Document Version:** 1.0
**Last Updated:** 2025-10-01
**Next Review:** Before v1.4.0 release
