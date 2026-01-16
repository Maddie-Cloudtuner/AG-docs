# Virtual Tagging Scripts - How They Work

> **Location:** `c:\Users\LENOVO\Desktop\my_docs\AG\vt\theory\`

---

## Quick Start

```bash
cd c:\Users\LENOVO\Desktop\my_docs\AG\vt\theory
python virtual_tag_processor.py
```

This generates `virtual_tags_final.xlsx` with all resources tagged.

---

## The 4 Scripts

### 1. `tag_mappings.py` - Configuration

**Purpose:** Contains all 1:1 mappings between native tags and schema tags.

```
Native Tag Key  →  Schema Tag Key
─────────────────────────────────────
Env             →  Environment
STAGE           →  Environment
PROD            →  Environment
Project         →  Project
CreatedBy       →  Owner
```

**Also contains:**
- `VALUE_NORMALIZATIONS` - Maps `prod` → `prod`, `PRODUCTION` → `prod`, etc.
- `RESOURCE_TYPE_DEFAULTS` - Default tags for each resource type
- `SERVICE_DEFAULTS` - Default tags for each service
- `REGION_DEFAULTS` - Region to DataCenter mapping

---

### 2. `virtual_tag_processor.py` - Main Processor

**Purpose:** The main script that processes your Excel files.

**Flow:**
```
┌─────────────────────────────────────────────────────────────┐
│                    RESOURCE RECEIVED                         │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  1. CHECK NATIVE TAGS                                        │
│     - Decode Base64 column names                             │
│     - Map native key → schema key (1:1)                      │
│     - Normalize values (prod → prod)                         │
│     - Confidence: 98% if value matches schema                │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  2. RESOURCE TYPE DEFAULTS                                   │
│     - If resource_type = "Instance"                          │
│       → Add Department=Engineering, BackupRequired=true      │
│     - Confidence: 80%                                        │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  3. SERVICE DEFAULTS                                         │
│     - If service_name = "AmazonEC2"                          │
│       → Add Department=Engineering                           │
│     - Confidence: 75%                                        │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  4. REGION DEFAULTS                                          │
│     - If region = "ap-south-1"                               │
│       → Add DataCenter=India-Mumbai                          │
│     - Confidence: 95%                                        │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  5. CALCULATE CONFIDENCE & DECIDE                            │
│     - ≥90% + 2 tags → AUTO_APPROVE                          │
│     - ≥75%          → PENDING                                │
│     - ≥50%          → SUGGESTION                             │
│     - <50%          → REVIEW                                 │
└─────────────────────────────────────────────────────────────┘
```

**Usage:**
```python
from virtual_tag_processor import VirtualTagProcessor
import pandas as pd

schema_df = pd.read_excel('cloud_resource_tags_complete 1.xlsx')
resources_df = pd.read_excel('restapi.resources (1).xlsx')

processor = VirtualTagProcessor(schema_df)
results = processor.process_dataframe(resources_df, limit=5000)
```

---

### 3. `db_models.py` - Database Models

**Purpose:** SQLAlchemy models for production database.

**Tables:**

| Table | Purpose |
|-------|---------|
| `tag_schema` | Stores schema definitions (from Excel) |
| `native_tag_mappings` | 1:1 native → schema key mappings |
| `value_normalizations` | Value transformations |
| `resource_type_rules` | Default tags by resource type |
| `service_rules` | Default tags by service |
| `cloud_resources` | Your cloud resources |
| `virtual_tags` | Applied virtual tags |
| `tag_audit` | Audit trail of all changes |

**Usage:**
```python
from db_models import init_database

engine, session = init_database('postgresql://user:pass@localhost/virtual_tags')
# Tables are created automatically
```

---

### 4. `backend_service.py` - API Integration

**Purpose:** Ready-to-use service class and FastAPI endpoints.

**Service Class:**
```python
from backend_service import VirtualTagService

service = VirtualTagService()

# Process a resource
result = service.process_resource(
    resource_id='i-1234567890',
    native_tags={'Env': 'prod', 'Project': 'Analytics'},
    resource_type='Instance',
    service_name='AmazonEC2',
    region='ap-south-1'
)

print(result['virtual_tags'])  # List of virtual tags
print(result['confidence'])    # 0.85
print(result['decision'])      # 'PENDING'
```

**FastAPI Endpoints:**
```
POST /api/v1/virtual-tags/process     - Process a resource
GET  /api/v1/resources/{id}/virtual-tags - Get tags for resource
POST /api/v1/virtual-tags/check-native   - Check native tags only
```

---

## Data Flow Diagram

```
┌──────────────────────┐     ┌──────────────────────┐
│  cloud_resource_tags │     │  restapi.resources   │
│  (Schema - 226 rows) │     │  (Resources - 70K)   │
└──────────┬───────────┘     └──────────┬───────────┘
           │                            │
           ▼                            ▼
┌──────────────────────────────────────────────────┐
│              tag_mappings.py                      │
│  - Native key → Schema key                        │
│  - Value normalizations                           │
│  - Resource type defaults                         │
│  - Service defaults                               │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│          virtual_tag_processor.py                 │
│  1. Load schema for validation                    │
│  2. Decode Base64 tag columns                     │
│  3. Process each resource                         │
│  4. Generate virtual_tags_final.xlsx              │
└──────────────────────┬───────────────────────────┘
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
┌─────────────────────┐   ┌─────────────────────┐
│    db_models.py     │   │  backend_service.py │
│  (Database tables)  │   │  (REST API)         │
└─────────────────────┘   └─────────────────────┘
```

---

## Output Files

| File | Description |
|------|-------------|
| `virtual_tags_final.xlsx` | All resources with virtual tags applied |
| `virtual_tags_random_sample.xlsx` | Random sample of 5000 resources |
| `virtual_tags.db` | SQLite database (when using db_models) |

---

## Key Results

From random sample of 5,000 resources:

| Metric | Value |
|--------|-------|
| Resources with virtual tags | **87.2%** |
| Average confidence | **71.5%** |
| Auto-approve | 0.4% |
| Pending approval | 86.8% |
| Needs review | 12.8% |

---

## Requirements

```bash
pip install pandas openpyxl sqlalchemy fastapi
```
