# CloudTuner Virtual Tags - Complete Schema Definition
## Production-Ready API Schema for Virtual Tagging System

> **Industry Research**: This schema incorporates best practices from **Finout** (rule-based prioritization), **Vantage** (retroactive application & cross-provider normalization), and **Cloud Custodian** (declarative policy structure).

---

## 1. Core Schema Definitions

### 1.1 Virtual Tag Schema

```json
{
  "id": "uuid",
  "resource_id": "uuid",
  "tag_key": "string",
  "tag_value": "string",
  "source": "enum",
  "confidence": "float",
  "rule_id": "uuid",
  "created_by": "string",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "provenance": {
    "origin": "string",
    "applied_by": "string",
    "reasoning": "string",
    "alternatives": ["array"]
  },
  "metadata": {
    "is_override": "boolean",
    "overrides_native": "boolean",
    "auto_applied": "boolean",
    "user_confirmed": "boolean"
  }
}
```

**Tag Source Types**:
```json
{
  "source": {
    "NATIVE": "Imported from cloud provider",
    "INFERRED": "ML model prediction",
    "RULE_BASED": "Applied via automation rule",
    "AI_SUGGESTED": "AI recommendation pending approval",
    "USER_CONFIRMED": "User manually confirmed/edited",
    "MANUAL": "User manually created",
    "INHERITED": "Inherited from parent resource",
    "NORMALIZED": "Standardized from native tag"
  }
}
```

**Confidence Levels**:
```json
{
  "confidence_thresholds": {
    "HIGH": ">= 0.90",
    "MEDIUM": "0.70 - 0.89",
    "LOW": "< 0.70"
  },
  "auto_apply_threshold": 0.90,
  "manual_review_threshold": 0.70
}
```

---

### 1.2 Resource Schema

```json
{
  "id": "uuid",
  "provider": "enum[aws|gcp|azure]",
  "resource_id": "string",
  "resource_arn": "string",
  "resource_type": "string",
  "name": "string",
  "account_id": "string",
  "project_id": "string",
  "region": "string",
  "availability_zone": "string",
  "native_tags": {
    "key": "value"
  },
  "virtual_tags": [
    {
      "ref": "virtual_tags.id"
    }
  ],
  "metadata": {
    "service": "string",
    "instance_type": "string",
    "state": "string",
    "cost_daily": "float",
    "cost_monthly": "float",
    "created_date": "timestamp",
    "last_seen": "timestamp"
  },
  "relationships": {
    "parent_resource_id": "uuid",
    "child_resources": ["uuid"],
    "depends_on": ["uuid"]
  },
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "last_ingested": "timestamp"
}
```

---

### 1.3 Virtual Tag Rules Schema

```json
{
  "id": "uuid",
  "rule_name": "string",
  "description": "string",
  "enabled": "boolean",
  "priority": "integer",
  "scope": {
    "providers": ["aws", "gcp", "azure"],
    "resource_types": ["ec2", "s3", "gcs"],
    "accounts": ["string"],
    "regions": ["string"],
    "tags": {
      "key": "value"
    }
  },
  "conditions": {
    "operator": "enum[AND|OR|NOT]",
    "rules": [
      {
        "field": "string",
        "operator": "enum[CONTAINS|EQUALS|STARTS_WITH|ENDS_WITH|REGEX|IN|NOT_IN|EXISTS|NOT_EXISTS]",
        "value": "any",
        "case_sensitive": "boolean"
      }
    ]
  },
  "actions": {
    "apply_tags": [
      {
        "tag_key": "string",
        "tag_value": "string",
        "override_existing": "boolean",
        "confidence": "float"
      }
    ]
  },
  "evaluation_mode": "enum[IMMEDIATE|SCHEDULED|EVENT_DRIVEN]",
  "created_by": "string",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "last_executed": "timestamp",
  "execution_stats": {
    "total_executions": "integer",
    "resources_matched": "integer",
    "tags_applied": "integer",
    "last_success": "timestamp",
    "last_failure": "timestamp"
  }
}
```

**Example Rule**:
```json
{
  "id": "rule-001",
  "rule_name": "Auto-tag Production Environment",
  "enabled": true,
  "priority": 1,
  "scope": {
    "providers": ["aws", "gcp"],
    "resource_types": ["*"]
  },
  "conditions": {
    "operator": "OR",
    "rules": [
      {
        "field": "name",
        "operator": "CONTAINS",
        "value": "prod",
        "case_sensitive": false
      },
      {
        "field": "native_tags.Environment",
        "operator": "EQUALS",
        "value": "Production"
      }
    ]
  },
  "actions": {
    "apply_tags": [
      {
        "tag_key": "environment",
        "tag_value": "production",
        "override_existing": true,
        "confidence": 0.95
      },
      {
        "tag_key": "cost-center",
        "tag_value": "engineering",
        "override_existing": false,
        "confidence": 0.85
      }
    ]
  },
  "evaluation_mode": "IMMEDIATE"
}
```

---

### 1.4 Tag Mapping/Normalization Schema

```json
{
  "id": "uuid",
  "mapping_name": "string",
  "source_provider": "enum[aws|gcp|azure]",
  "target_schema": "unified",
  "mappings": [
    {
      "source_key": "string",
      "target_key": "string",
      "value_mappings": {
        "source_value": "target_value"
      },
      "transformation": {
        "type": "enum[LOWERCASE|UPPERCASE|NORMALIZE|REGEX]",
        "pattern": "string",
        "replacement": "string"
      }
    }
  ],
  "enabled": "boolean",
  "created_at": "timestamp"
}
```

**Example Mappings**:
```json
{
  "id": "mapping-001",
  "mapping_name": "AWS to Unified Schema",
  "source_provider": "aws",
  "target_schema": "unified",
  "mappings": [
    {
      "source_key": "Environment",
      "target_key": "environment",
      "value_mappings": {
        "prod": "production",
        "dev": "development",
        "stg": "staging",
        "test": "testing"
      },
      "transformation": {
        "type": "LOWERCASE"
      }
    },
    {
      "source_key": "CostCenter",
      "target_key": "cost-center",
      "value_mappings": {
        "ENG": "engineering",
        "MKT": "marketing",
        "OPS": "operations"
      }
    },
    {
      "source_key": "Owner",
      "target_key": "owner",
      "transformation": {
        "type": "REGEX",
        "pattern": "^([a-zA-Z]+)$",
        "replacement": "$1@company.com"
      }
    }
  ]
}
```

---

### 1.5 Compliance Policy Schema

```json
{
  "id": "uuid",
  "policy_name": "string",
  "description": "string",
  "policy_type": "enum[REQUIRED_TAGS|VALUE_VALIDATION|CONDITIONAL_REQUIREMENT|TAG_FORMAT|TAG_COUNT]",
  "severity": "enum[CRITICAL|HIGH|MEDIUM|LOW]",
  "enabled": "boolean",
  "scope": {
    "providers": ["string"],
    "resource_types": ["string"],
    "accounts": ["string"],
    "tags": {
      "key": "value"
    }
  },
  "rules": {
    "conditions": {},
    "requirements": {},
    "validations": {}
  },
  "enforcement": {
    "mode": "enum[AUDIT|ENFORCE|PREVENT]",
    "auto_remediate": "boolean",
    "remediation_actions": []
  },
  "notification": {
    "channels": ["email", "slack", "webhook"],
    "recipients": ["string"],
    "template": "string"
  },
  "created_by": "string",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "last_evaluated": "timestamp"
}
```

**Policy Examples**:

**1. Required Tags Policy**:
```json
{
  "id": "policy-001",
  "policy_name": "Production Required Tags",
  "policy_type": "REQUIRED_TAGS",
  "severity": "CRITICAL",
  "enabled": true,
  "scope": {
    "providers": ["aws", "gcp", "azure"],
    "resource_types": ["*"]
  },
  "rules": {
    "conditions": {
      "virtual_tags.environment": "production"
    },
    "requirements": {
      "required_tags": ["cost-center", "owner", "backup", "data-classification"],
      "all_required": true
    }
  },
  "enforcement": {
    "mode": "AUDIT",
    "auto_remediate": false
  },
  "notification": {
    "channels": ["email", "slack"],
    "recipients": ["finops-team@company.com"]
  }
}
```

**2. Tag Value Validation Policy**:
```json
{
  "id": "policy-002",
  "policy_name": "Environment Value Validation",
  "policy_type": "VALUE_VALIDATION",
  "severity": "HIGH",
  "enabled": true,
  "rules": {
    "validations": {
      "tag_key": "environment",
      "allowed_values": ["production", "staging", "development", "sandbox", "test"],
      "case_sensitive": false,
      "allow_empty": false
    }
  },
  "enforcement": {
    "mode": "ENFORCE",
    "auto_remediate": true,
    "remediation_actions": [
      {
        "type": "NORMALIZE_VALUE",
        "mapping": {
          "prod": "production",
          "dev": "development",
          "stg": "staging"
        }
      }
    ]
  }
}
```

**3. Conditional Tag Policy** (Inspired by Cloud Custodian):
```json
{
  "id": "policy-003",
  "policy_name": "Database Backup Requirement",
  "policy_type": "CONDITIONAL_REQUIREMENT",
  "severity": "CRITICAL",
  "rules": {
    "conditions": {
      "operator": "AND",
      "rules": [
        {
          "field": "resource_type",
          "operator": "IN",
          "value": ["rds", "dynamodb", "cloud-sql", "cosmos-db"]
        },
        {
          "field": "virtual_tags.environment",
          "operator": "EQUALS",
          "value": "production"
        }
      ]
    },
    "requirements": {
      "required_tags": ["backup", "backup-schedule", "retention-days"],
      "tag_validations": {
        "backup": {
          "allowed_values": ["enabled", "documented-exception"]
        },
        "retention-days": {
          "type": "integer",
          "min": 30,
          "max": 365
        }
      }
    }
  }
}
```

---

### 1.6 Compliance Status Schema

```json
{
  "id": "uuid",
  "resource_id": "uuid",
  "policy_id": "uuid",
  "is_compliant": "boolean",
  "compliance_score": "float",
  "violations": [
    {
      "violation_type": "string",
      "severity": "string",
      "description": "string",
      "missing_tags": ["string"],
      "invalid_tags": [
        {
          "tag_key": "string",
          "current_value": "string",
          "expected_values": ["string"],
          "reason": "string"
        }
      ],
      "detected_at": "timestamp"
    }
  ],
  "evaluated_at": "timestamp",
  "next_evaluation": "timestamp"
}
```

---

### 1.7 ML Inference Schema

```json
{
  "id": "uuid",
  "resource_id": "uuid",
  "model_version": "string",
  "predictions": [
    {
      "tag_key": "string",
      "predicted_value": "string",
      "confidence": "float",
      "reasoning": "string",
      "alternatives": [
        {
          "value": "string",
          "confidence": "float"
        }
      ],
      "features_used": {
        "resource_name": "string",
        "resource_type": "string",
        "account_patterns": "string",
        "similar_resources": ["uuid"],
        "historical_accuracy": "float"
      }
    }
  ],
  "user_feedback": {
    "accepted": ["string"],
    "rejected": ["string"],
    "modified": [
      {
        "tag_key": "string",
        "predicted_value": "string",
        "actual_value": "string"
      }
    ]
  },
  "predicted_at": "timestamp",
  "feedback_at": "timestamp"
}
```

---

### 1.8 Tag Audit Trail Schema

```json
{
  "id": "uuid",
  "resource_id": "uuid",
  "action": "enum[CREATE|UPDATE|DELETE|AUTO_APPLY|BULK_UPDATE]",
  "tag_key": "string",
  "old_value": "string",
  "new_value": "string",
  "source": "string",
  "performed_by": "string",
  "reason": "string",
  "rule_id": "uuid",
  "policy_id": "uuid",
  "confidence": "float",
  "metadata": {
    "ip_address": "string",
    "user_agent": "string",
    "api_version": "string"
  },
  "timestamp": "timestamp"
}
```

---

## 2. API Endpoint Definitions

### 2.1 Virtual Tags API

**Base Path**: `/api/v1/virtual-tags`

#### GET `/resources/{resource_id}/virtual-tags`
**Description**: Get all virtual tags for a specific resource

**Response**:
```json
{
  "resource_id": "uuid",
  "resource_name": "web-server-prod-001",
  "provider": "aws",
  "resource_type": "ec2",
  "virtual_tags": [
    {
      "key": "environment",
      "value": "production",
      "source": "INFERRED",
      "confidence": 0.95,
      "created_at": "2025-11-25T10:00:00Z",
      "updated_at": "2025-11-25T10:00:00Z",
      "provenance": {
        "origin": "ML Model v2.3",
        "applied_by": "virtual_tagger_worker",
        "reasoning": "Resource name contains 'prod' keyword"
      }
    },
    {
      "key": "cost-center",
      "value": "engineering",
      "source": "USER_CONFIRMED",
      "confidence": 1.0,
      "created_at": "2025-11-24T14:30:00Z",
      "updated_at": "2025-11-25T09:15:00Z"
    }
  ],
  "native_tags": {
    "Name": "web-server-prod-001",
    "CreatedBy": "terraform"
  },
  "compliance_status": {
    "is_compliant": true,
    "score": 1.0,
    "violations": [],
    "last_checked": "2025-11-25T12:00:00Z"
  },
  "ml_suggestions": [
    {
      "key": "owner",
      "value": "platform-team@company.com",
      "confidence": 0.89,
      "reasoning": "Based on similar resources in this account",
      "alternatives": [
        {
          "value": "devops-team@company.com",
          "confidence": 0.76
        }
      ]
    },
    {
      "key": "project",
      "value": "web-platform",
      "confidence": 0.82,
      "reasoning": "Inferred from resource name pattern"
    }
  ]
}
```

#### POST `/virtual-tags/apply`
**Description**: Apply virtual tags to resource(s)

**Request**:
```json
{
  "resource_ids": ["uuid"],
  "tags": [
    {
      "key": "string",
      "value": "string",
      "override_existing": "boolean"
    }
  ],
  "source": "MANUAL",
  "apply_to_children": "boolean",
  "reason": "string"
}
```

**Response**:
```json
{
  "success": true,
  "tags_applied": 5,
  "resources_updated": 3,
  "errors": [],
  "audit_ids": ["uuid"]
}
```

#### PUT `/virtual-tags/{tag_id}`
**Description**: Update an existing virtual tag

#### DELETE `/virtual-tags/{tag_id}`
**Description**: Delete a virtual tag

#### POST `/virtual-tags/bulk-apply`
**Description**: Bulk apply tags based on filters

**Request**:
```json
{
  "filters": {
    "provider": "aws",
    "resource_type": "ec2",
    "region": "us-east-1",
    "tags": {
      "environment": "production"
    }
  },
  "tags": [
    {
      "key": "backup",
      "value": "daily"
    }
  ],
  "dry_run": true
}
```

---

### 2.2 Tag Rules API

**Base Path**: `/api/v1/tag-rules`

#### GET `/tag-rules`
**Description**: List all tag rules

**Query Parameters**:
- `enabled`: boolean
- `priority`: integer
- `scope.provider`: string
- `limit`: integer
- `offset`: integer

#### POST `/tag-rules`
**Description**: Create a new tag rule

#### PUT `/tag-rules/{rule_id}`
**Description**: Update a tag rule

#### DELETE `/tag-rules/{rule_id}`
**Description**: Delete a tag rule

#### POST `/tag-rules/{rule_id}/execute`
**Description**: Manually trigger rule execution

**Response**:
```json
{
  "rule_id": "uuid",
  "execution_id": "uuid",
  "status": "RUNNING",
  "resources_evaluated": 1250,
  "tags_applied": 892,
  "started_at": "2025-11-25T10:00:00Z"
}
```

#### POST `/tag-rules/test`
**Description**: Test a rule without applying tags

**Request**:
```json
{
  "rule": {
    "conditions": {},
    "actions": {}
  },
  "test_resources": ["uuid"]
}
```

**Response**:
```json
{
  "matched_resources": 3,
  "would_apply_tags": [
    {
      "resource_id": "uuid",
      "tags": [
        {
          "key": "environment",
          "value": "production"
        }
      ]
    }
  ]
}
```

---

### 2.3 Compliance API

**Base Path**: `/api/v1/compliance`

#### GET `/compliance/status`
**Description**: Get overall compliance status

**Query Parameters**:
- `provider`: string
- `resource_type`: string
- `policy_id`: uuid
- `severity`: string

**Response**:
```json
{
  "overall_compliance_score": 0.87,
  "total_resources": 2500,
  "compliant_resources": 2175,
  "non_compliant_resources": 325,
  "by_severity": {
    "CRITICAL": {
      "total_violations": 45,
      "resources_affected": 45
    },
    "HIGH": {
      "total_violations": 123,
      "resources_affected": 98
    },
    "MEDIUM": {
      "total_violations": 157,
      "resources_affected": 182
    }
  },
  "by_policy": [
    {
      "policy_id": "uuid",
      "policy_name": "Production Required Tags",
      "compliance_score": 0.92,
      "violations": 45
    }
  ],
  "trend": {
    "score_change_7d": "+0.05",
    "violations_change_7d": "-23"
  }
}
```

#### POST `/compliance/policies`
**Description**: Create a compliance policy

#### PUT `/compliance/policies/{policy_id}`
**Description**: Update a compliance policy

#### DELETE `/compliance/policies/{policy_id}`
**Description**: Delete a compliance policy

#### POST `/compliance/recheck`
**Description**: Trigger compliance re-evaluation

**Request**:
```json
{
  "scope": {
    "resource_ids": ["uuid"],
    "policy_ids": ["uuid"],
    "providers": ["aws"]
  }
}
```

#### GET `/compliance/violations`
**Description**: List compliance violations

**Response**:
```json
{
  "violations": [
    {
      "id": "uuid",
      "resource_id": "uuid",
      "resource_name": "db-prod-001",
      "policy_id": "uuid",
      "policy_name": "Production Required Tags",
      "severity": "CRITICAL",
      "violation_type": "MISSING_TAGS",
      "missing_tags": ["backup", "owner"],
      "detected_at": "2025-11-25T10:00:00Z",
      "status": "OPEN",
      "assigned_to": "finops-team"
    }
  ],
  "pagination": {
    "total": 325,
    "limit": 50,
    "offset": 0
  }
}
```

---

### 2.4 Tag Schema & Mapping API

**Base Path**: `/api/v1/tag-schema`

#### GET `/tag-schema`
**Description**: Get unified tag schema

**Response**:
```json
{
  "schema_version": "1.0",
  "tag_definitions": [
    {
      "key": "environment",
      "display_name": "Environment",
      "description": "Deployment environment",
      "type": "enum",
      "allowed_values": ["production", "staging", "development", "sandbox", "test"],
      "required": true,
      "category": "CRITICAL",
      "validation": {
        "case_sensitive": false,
        "allow_custom": false
      }
    },
    {
      "key": "cost-center",
      "display_name": "Cost Center",
      "description": "Department or team responsible for costs",
      "type": "string",
      "required": true,
      "category": "CRITICAL",
      "validation": {
        "pattern": "^[a-z-]+$",
        "min_length": 2,
        "max_length": 50
      }
    },
    {
      "key": "owner",
      "display_name": "Owner",
      "description": "Email of the responsible person/team",
      "type": "email",
      "required": true,
      "category": "CRITICAL",
      "validation": {
        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      }
    }
  ]
}
```

#### POST `/tag-mappings`
**Description**: Create tag mapping for normalization

#### GET `/tag-mappings`
**Description**: List all tag mappings

---

### 2.5 ML Inference API

**Base Path**: `/api/v1/ml`

#### POST `/ml/infer`
**Description**: Get ML tag predictions for resources

**Request**:
```json
{
  "resource_ids": ["uuid"],
  "tag_keys": ["environment", "cost-center", "owner"],
  "include_alternatives": true,
  "min_confidence": 0.7
}
```

**Response**:
```json
{
  "predictions": [
    {
      "resource_id": "uuid",
      "tags": [
        {
          "key": "environment",
          "value": "production",
          "confidence": 0.95,
          "reasoning": "Resource name pattern matches production naming convention",
          "alternatives": [
            {
              "value": "staging",
              "confidence": 0.62
            }
          ]
        }
      ]
    }
  ],
  "model_version": "2.3.1",
  "predicted_at": "2025-11-25T10:00:00Z"
}
```

#### POST `/ml/feedback`
**Description**: Provide feedback on ML predictions

**Request**:
```json
{
  "prediction_id": "uuid",
  "resource_id": "uuid",
  "feedback": [
    {
      "tag_key": "environment",
      "predicted_value": "production",
      "actual_value": "production",
      "action": "ACCEPTED"
    },
    {
      "tag_key": "cost-center",
      "predicted_value": "engineering",
      "actual_value": "platform",
      "action": "CORRECTED"
    }
  ]
}
```

#### GET `/ml/models`
**Description**: Get ML model information and performance metrics

**Response**:
```json
{
  "models": [
    {
      "tag_key": "environment",
      "model_type": "RandomForest",
      "version": "2.3.1",
      "accuracy": 0.95,
      "precision": 0.93,
      "recall": 0.96,
      "f1_score": 0.94,
      "trained_at": "2025-11-18T00:00:00Z",
      "training_samples": 15000
    }
  ]
}
```

---

### 2.6 Audit API

**Base Path**: `/api/v1/audit`

#### GET `/audit/trail`
**Description**: Get audit trail for tag changes

**Query Parameters**:
- `resource_id`: uuid
- `tag_key`: string
- `action`: enum
- `performed_by`: string
- `start_date`: timestamp
- `end_date`: timestamp

**Response**:
```json
{
  "audit_logs": [
    {
      "id": "uuid",
      "resource_id": "uuid",
      "resource_name": "web-server-prod-001",
      "action": "UPDATE",
      "tag_key": "environment",
      "old_value": "staging",
      "new_value": "production",
      "source": "MANUAL",
      "performed_by": "john.doe@company.com",
      "reason": "Resource promoted to production",
      "timestamp": "2025-11-25T10:00:00Z"
    }
  ]
}
```

#### GET `/audit/reports`
**Description**: Generate audit reports

---

## 3. Database Schema (PostgreSQL)

### 3.1 Core Tables

```sql
-- Resources table
CREATE TABLE resources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider VARCHAR(10) NOT NULL CHECK (provider IN ('aws', 'gcp', 'azure')),
  resource_id VARCHAR(500) NOT NULL,
  resource_arn TEXT,
  resource_type VARCHAR(100) NOT NULL,
  name VARCHAR(500),
  account_id VARCHAR(100),
  project_id VARCHAR(100),
  region VARCHAR(50),
  availability_zone VARCHAR(50),
  native_tags JSONB DEFAULT '{}',
  metadata JSONB DEFAULT '{}',
  relationships JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_ingested TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP,
  UNIQUE(provider, resource_id)
);

CREATE INDEX idx_resources_provider ON resources(provider);
CREATE INDEX idx_resources_type ON resources(resource_type);
CREATE INDEX idx_resources_account ON resources(account_id);
CREATE INDEX idx_resources_region ON resources(region);
CREATE INDEX idx_resources_native_tags ON resources USING gin(native_tags);
CREATE INDEX idx_resources_last_ingested ON resources(last_ingested);

-- Virtual tags table
CREATE TABLE virtual_tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resource_id UUID NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
  tag_key VARCHAR(100) NOT NULL,
  tag_value TEXT NOT NULL,
  source VARCHAR(20) NOT NULL CHECK (source IN ('NATIVE','INFERRED','RULE_BASED','AI_SUGGESTED','USER_CONFIRMED','MANUAL','INHERITED','NORMALIZED')),
  confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
  rule_id UUID,
  created_by VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  provenance JSONB DEFAULT '{}',
  metadata JSONB DEFAULT '{}',
  deleted_at TIMESTAMP,
  UNIQUE(resource_id, tag_key, deleted_at)
);

CREATE INDEX idx_virtual_tags_resource ON virtual_tags(resource_id);
CREATE INDEX idx_virtual_tags_key ON virtual_tags(tag_key);
CREATE INDEX idx_virtual_tags_value ON virtual_tags(tag_value);
CREATE INDEX idx_virtual_tags_source ON virtual_tags(source);
CREATE INDEX idx_virtual_tags_confidence ON virtual_tags(confidence);
CREATE INDEX idx_virtual_tags_rule ON virtual_tags(rule_id);
CREATE INDEX idx_virtual_tags_composite ON virtual_tags(resource_id, tag_key, source);

-- Virtual tag rules table
CREATE TABLE virtual_tag_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rule_name VARCHAR(200) NOT NULL,
  description TEXT,
  enabled BOOLEAN DEFAULT TRUE,
  priority INTEGER NOT NULL DEFAULT 999,
  scope JSONB NOT NULL DEFAULT '{}',
  conditions JSONB NOT NULL,
  actions JSONB NOT NULL,
  evaluation_mode VARCHAR(20) DEFAULT 'SCHEDULED' CHECK (evaluation_mode IN ('IMMEDIATE','SCHEDULED','EVENT_DRIVEN')),
  created_by VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_executed TIMESTAMP,
  execution_stats JSONB DEFAULT '{}',
  deleted_at TIMESTAMP,
  UNIQUE(rule_name, deleted_at)
);

CREATE INDEX idx_rules_enabled ON virtual_tag_rules(enabled);
CREATE INDEX idx_rules_priority ON virtual_tag_rules(priority);
CREATE INDEX idx_rules_scope ON virtual_tag_rules USING gin(scope);

-- Tag mappings table
CREATE TABLE tag_mappings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mapping_name VARCHAR(200) NOT NULL,
  source_provider VARCHAR(10) NOT NULL,
  target_schema VARCHAR(50) DEFAULT 'unified',
  mappings JSONB NOT NULL,
  enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(mapping_name)
);

CREATE INDEX idx_mappings_provider ON tag_mappings(source_provider);
CREATE INDEX idx_mappings_enabled ON tag_mappings(enabled);

-- Compliance policies table
CREATE TABLE compliance_policies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  policy_name VARCHAR(200) NOT NULL,
  description TEXT,
  policy_type VARCHAR(50) NOT NULL CHECK (policy_type IN ('REQUIRED_TAGS','VALUE_VALIDATION','CONDITIONAL_REQUIREMENT','TAG_FORMAT','TAG_COUNT')),
  severity VARCHAR(20) NOT NULL CHECK (severity IN ('CRITICAL','HIGH','MEDIUM','LOW')),
  enabled BOOLEAN DEFAULT TRUE,
  scope JSONB DEFAULT '{}',
  rules JSONB NOT NULL,
  enforcement JSONB DEFAULT '{}',
  notification JSONB DEFAULT '{}',
  created_by VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_evaluated TIMESTAMP,
  deleted_at TIMESTAMP,
  UNIQUE(policy_name, deleted_at)
);

CREATE INDEX idx_policies_type ON compliance_policies(policy_type);
CREATE INDEX idx_policies_severity ON compliance_policies(severity);
CREATE INDEX idx_policies_enabled ON compliance_policies(enabled);

-- Compliance status table
CREATE TABLE compliance_status (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resource_id UUID NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
  policy_id UUID NOT NULL REFERENCES compliance_policies(id) ON DELETE CASCADE,
  is_compliant BOOLEAN DEFAULT FALSE,
  compliance_score FLOAT DEFAULT 0,
  violations JSONB DEFAULT '[]',
  evaluated_at TIMESTAMP DEFAULT NOW(),
  next_evaluation TIMESTAMP,
  UNIQUE(resource_id, policy_id)
);

CREATE INDEX idx_compliance_resource ON compliance_status(resource_id);
CREATE INDEX idx_compliance_policy ON compliance_status(policy_id);
CREATE INDEX idx_compliance_is_compliant ON compliance_status(is_compliant);
CREATE INDEX idx_compliance_score ON compliance_status(compliance_score);

-- ML inference table
CREATE TABLE ml_inferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resource_id UUID NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
  model_version VARCHAR(20) NOT NULL,
  predictions JSONB NOT NULL,
  user_feedback JSONB DEFAULT '{}',
  predicted_at TIMESTAMP DEFAULT NOW(),
  feedback_at TIMESTAMP
);

CREATE INDEX idx_ml_resource ON ml_inferences(resource_id);
CREATE INDEX idx_ml_model_version ON ml_inferences(model_version);
CREATE INDEX idx_ml_predicted_at ON ml_inferences(predicted_at);

-- Tag audit trail table
CREATE TABLE tag_audit (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resource_id UUID REFERENCES resources(id) ON DELETE SET NULL,
  action VARCHAR(50) NOT NULL CHECK (action IN ('CREATE','UPDATE','DELETE','AUTO_APPLY','BULK_UPDATE')),
  tag_key VARCHAR(100),
  old_value TEXT,
  new_value TEXT,
  source VARCHAR(20),
  performed_by VARCHAR(100),
  reason TEXT,
  rule_id UUID,
  policy_id UUID,
  confidence FLOAT,
  metadata JSONB DEFAULT '{}',
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_resource ON tag_audit(resource_id);
CREATE INDEX idx_audit_action ON tag_audit(action);
CREATE INDEX idx_audit_tag_key ON tag_audit(tag_key);
CREATE INDEX idx_audit_performed_by ON tag_audit(performed_by);
CREATE INDEX idx_audit_timestamp ON tag_audit(timestamp DESC);
CREATE INDEX idx_audit_rule ON tag_audit(rule_id);
CREATE INDEX idx_audit_policy ON tag_audit(policy_id);

-- Tag schema definitions table
CREATE TABLE tag_schema (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tag_key VARCHAR(100) NOT NULL UNIQUE,
  display_name VARCHAR(200),
  description TEXT,
  data_type VARCHAR(20) DEFAULT 'string' CHECK (data_type IN ('string','enum','integer','float','boolean','email','url','date')),
  allowed_values TEXT[],
  required BOOLEAN DEFAULT FALSE,
  category VARCHAR(20) CHECK (category IN ('CRITICAL','HIGH','MEDIUM','LOW')),
  validation JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_schema_key ON tag_schema(tag_key);
CREATE INDEX idx_schema_required ON tag_schema(required);
CREATE INDEX idx_schema_category ON tag_schema(category);
```

### 3.2 Views

```sql
-- Materialized view for resource tag coverage
CREATE MATERIALIZED VIEW resource_tag_coverage AS
SELECT 
  r.id,
  r.provider,
  r.resource_type,
  r.account_id,
  COUNT(vt.id) as virtual_tag_count,
  COUNT(DISTINCT vt.tag_key) as unique_tag_keys,
  COUNT(CASE WHEN ts.required = TRUE THEN 1 END) as required_tags_present,
  (SELECT COUNT(*) FROM tag_schema WHERE required = TRUE) as total_required_tags,
  CASE 
    WHEN (SELECT COUNT(*) FROM tag_schema WHERE required = TRUE) = 0 THEN 1.0
    ELSE COUNT(CASE WHEN ts.required = TRUE THEN 1 END)::FLOAT / 
         (SELECT COUNT(*) FROM tag_schema WHERE required = TRUE)::FLOAT
  END as coverage_score
FROM resources r
LEFT JOIN virtual_tags vt ON r.id = vt.resource_id AND vt.deleted_at IS NULL
LEFT JOIN tag_schema ts ON vt.tag_key = ts.tag_key
WHERE r.deleted_at IS NULL
GROUP BY r.id, r.provider, r.resource_type, r.account_id;

CREATE UNIQUE INDEX idx_coverage_resource ON resource_tag_coverage(id);
CREATE INDEX idx_coverage_score ON resource_tag_coverage(coverage_score);

-- View for compliance dashboard
CREATE VIEW compliance_dashboard AS
SELECT 
  cp.id AS policy_id,
  cp.policy_name,
  cp.policy_type,
  cp.severity,
  COUNT(DISTINCT cs.resource_id) as total_resources_evaluated,
  COUNT(DISTINCT CASE WHEN cs.is_compliant = TRUE THEN cs.resource_id END) as compliant_resources,
  COUNT(DISTINCT CASE WHEN cs.is_compliant = FALSE THEN cs.resource_id END) as non_compliant_resources,
  AVG(cs.compliance_score) as avg_compliance_score,
  SUM(jsonb_array_length(cs.violations)) as total_violations
FROM compliance_policies cp
LEFT JOIN compliance_status cs ON cp.id = cs.policy_id
WHERE cp.enabled = TRUE AND cp.deleted_at IS NULL
GROUP BY cp.id, cp.policy_name, cp.policy_type, cp.severity;
```

---

## 4. Elasticsearch Index Schema

### 4.1 Virtual Tags Index

```json
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 2,
    "analysis": {
      "analyzer": {
        "tag_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "asciifolding"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "resource_id": {
        "type": "keyword"
      },
      "resource_name": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "provider": {
        "type": "keyword"
      },
      "resource_type": {
        "type": "keyword"
      },
      "account_id": {
        "type": "keyword"
      },
      "region": {
        "type": "keyword"
      },
      "virtual_tags": {
        "type": "nested",
        "properties": {
          "key": {
            "type": "keyword"
          },
          "value": {
            "type": "text",
            "fields": {
              "keyword": {
                "type": "keyword"
              }
            }
          },
          "source": {
            "type": "keyword"
          },
          "confidence": {
            "type": "float"
          },
          "created_at": {
            "type": "date"
          }
        }
      },
      "native_tags": {
        "type": "object",
        "enabled": true
      },
      "compliance_status": {
        "type": "keyword"
      },
      "compliance_score": {
        "type": "float"
      },
      "last_updated": {
        "type": "date"
      },
      "metadata": {
        "type": "object",
        "enabled": true
      }
    }
  }
}
```

---

## 5. Message Queue Schema

### 5.1 Queue Definitions

**Queue Names and Purposes**:

1. **`virtual_tags.ingestion`** - Raw resource data from cloud providers
2. **`virtual_tags.normalization`** - Tag normalization and mapping
3. **`virtual_tags.inference`** - ML-based tag prediction
4. **`virtual_tags.compliance`** - Compliance policy evaluation
5. **`virtual_tags.audit`** - Audit logging and reporting
6. **`virtual_tags.alerts`** - Alert generation and notification

### 5.2 Message Schema

```json
{
  "message_id": "uuid",
  "queue": "string",
  "timestamp": "timestamp",
  "priority": "integer",
  "payload": {
    "event_type": "string",
    "resource_id": "uuid",
    "data": {}
  },
  "metadata": {
    "source": "string",
    "correlation_id": "uuid",
    "retry_count": "integer",
    "max_retries": "integer"
  }
}
```

**Example - Ingestion Message**:
```json
{
  "message_id": "msg-12345",
  "queue": "virtual_tags.ingestion",
  "timestamp": "2025-11-25T10:00:00Z",
  "priority": 5,
  "payload": {
    "event_type": "RESOURCE_DISCOVERED",
    "resource_id": "i-1234567890abcdef0",
    "data": {
      "provider": "aws",
      "resource_type": "ec2",
      "name": "web-server-prod-001",
      "native_tags": {
        "Name": "web-server-prod-001",
        "Environment": "Production"
      },
      "metadata": {
        "instance_type": "t3.medium",
        "region": "us-east-1"
      }
    }
  },
  "metadata": {
    "source": "resource_discovery_service",
    "correlation_id": "corr-67890",
    "retry_count": 0,
    "max_retries": 3
  }
}
```

---

## 6. GraphQL Schema

```graphql
type Query {
  resource(id: ID!): Resource
  resources(filter: ResourceFilter, limit: Int, offset: Int): [Resource!]!
  virtualTag(id: ID!): VirtualTag
  virtualTags(filter: VirtualTagFilter): [VirtualTag!]!
  tagRule(id: ID!): TagRule
  tagRules(enabled: Boolean): [TagRule!]!
  compliancePolicy(id: ID!): CompliancePolicy
  compliancePolicies(enabled: Boolean): [CompliancePolicy!]!
  complianceStatus(resourceId: ID, policyId: ID): [ComplianceStatus!]!
  tagSchema: [TagDefinition!]!
  mlPredictions(resourceId: ID!): MLInference
}

type Mutation {
  applyVirtualTags(input: ApplyTagsInput!): ApplyTagsResult!
  updateVirtualTag(id: ID!, input: UpdateTagInput!): VirtualTag!
  deleteVirtualTag(id: ID!): Boolean!
  
  createTagRule(input: CreateRuleInput!): TagRule!
  updateTagRule(id: ID!, input: UpdateRuleInput!): TagRule!
  deleteTagRule(id: ID!): Boolean!
  executeTagRule(id: ID!): RuleExecutionResult!
  
  createCompliancePolicy(input: CreatePolicyInput!): CompliancePolicy!
  updateCompliancePolicy(id: ID!, input: UpdatePolicyInput!): CompliancePolicy!
  deleteCompliancePolicy(id: ID!): Boolean!
  
  submitMLFeedback(input: MLFeedbackInput!): Boolean!
}

type Resource {
  id: ID!
  provider: CloudProvider!
  resourceId: String!
  resourceArn: String
  resourceType: String!
  name: String
  accountId: String
  region: String
  nativeTags: JSON
  virtualTags: [VirtualTag!]!
  complianceStatus: [ComplianceStatus!]!
  mlSuggestions: [TagSuggestion!]!
  metadata: ResourceMetadata
  relationships: ResourceRelationships
  createdAt: DateTime!
  updatedAt: DateTime!
  lastIngested: DateTime!
}

type VirtualTag {
  id: ID!
  resourceId: ID!
  key: String!
  value: String!
  source: TagSource!
  confidence: Float
  ruleId: ID
  createdBy: String
  createdAt: DateTime!
  updatedAt: DateTime!
  provenance: Provenance
  metadata: JSON
}

type TagRule {
  id: ID!
  ruleName: String!
  description: String
  enabled: Boolean!
  priority: Int!
  scope: RuleScope!
  conditions: JSON!
  actions: JSON!
  evaluationMode: EvaluationMode!
  executionStats: ExecutionStats
  createdAt: DateTime!
  updatedAt: DateTime!
  lastExecuted: DateTime
}

type CompliancePolicy {
  id: ID!
  policyName: String!
  description: String
  policyType: PolicyType!
  severity: Severity!
  enabled: Boolean!
  scope: PolicyScope
  rules: JSON!
  enforcement: EnforcementConfig
  createdAt: DateTime!
  updatedAt: DateTime!
}

type ComplianceStatus {
  id: ID!
  resource: Resource!
  policy: CompliancePolicy!
  isCompliant: Boolean!
  complianceScore: Float!
  violations: [Violation!]!
  evaluatedAt: DateTime!
  nextEvaluation: DateTime
}

type TagSuggestion {
  key: String!
  value: String!
  confidence: Float!
  reasoning: String
  alternatives: [TagAlternative!]
}

type MLInference {
  id: ID!
  resource: Resource!
  modelVersion: String!
  predictions: [TagPrediction!]!
  userFeedback: JSON
  predictedAt: DateTime!
}

enum CloudProvider {
  AWS
  GCP
  AZURE
}

enum TagSource {
  NATIVE
  INFERRED
  RULE_BASED
  AI_SUGGESTED
  USER_CONFIRMED
  MANUAL
  INHERITED
  NORMALIZED
}

enum PolicyType {
  REQUIRED_TAGS
  VALUE_VALIDATION
  CONDITIONAL_REQUIREMENT
  TAG_FORMAT
  TAG_COUNT
}

enum Severity {
  CRITICAL
  HIGH
  MEDIUM
  LOW
}

enum EvaluationMode {
  IMMEDIATE
  SCHEDULED
  EVENT_DRIVEN
}

input ResourceFilter {
  provider: CloudProvider
  resourceType: String
  accountId: String
  region: String
  tags: JSON
}

input ApplyTagsInput {
  resourceIds: [ID!]!
  tags: [TagInput!]!
  source: TagSource!
  applyToChildren: Boolean
  reason: String
}

input TagInput {
  key: String!
  value: String!
  overrideExisting: Boolean
}
```

---

## 7. Implementation Checklist

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up PostgreSQL database with all core tables
- [ ] Create Elasticsearch indices
- [ ] Implement basic REST API for virtual tags CRUD
- [ ] Set up message queue infrastructure (RabbitMQ/SQS)
- [ ] Implement resource ingestion from AWS/GCP/Azure

### Phase 2: Core Features (Weeks 3-5)
- [ ] Implement tag normalization and mapping engine
- [ ] Build rule-based tagging engine with priority support
- [ ] Create compliance policy framework
- [ ] Implement audit trail logging
- [ ] Build GraphQL API layer

### Phase 3: ML Integration (Weeks 6-8)
- [ ] Train initial ML models for tag inference
- [ ] Implement ML prediction API
- [ ] Build confidence scoring system
- [ ] Create feedback loop for model improvement
- [ ] Implement A/B testing for model deployment

### Phase 4: Advanced Features (Weeks 9-10)
- [ ] Build scheduler service for periodic tasks
- [ ] Implement alert generation and notification system
- [ ] Create compliance dashboard
- [ ] Build tag coverage reporting
- [ ] Implement retroactive tag application

### Phase 5: Testing & Optimization (Weeks 11-12)
- [ ] Performance testing and optimization
- [ ] Security audit and hardening
- [ ] Integration testing across all services
- [ ] User acceptance testing
- [ ] Documentation and deployment

---

## 8. Key Design Decisions (Based on Industry Research)

### From Finout:
✅ **Priority-based rule execution** - Rules ordered by priority, higher priority overrides lower  
✅ **Boolean logic in conditions** - Complex AND/OR/NOT conditions for flexible filtering  
✅ **Instant tag application** - Real-time updates when rules match  

### From Vantage:
✅ **Retroactive application** - Apply tags to historical data  
✅ **Override capabilities** - Virtual tags can override native tags  
✅ **Cross-provider normalization** - Unified schema across AWS/GCP/Azure  
✅ **Audit logging** - Complete trail of all tag changes  

### From Cloud Custodian:
✅ **Declarative policy structure** - YAML-like JSON policies  
✅ **Tag-based filtering** - Rich filter capabilities (exists, absent, pattern matching)  
✅ **Action-based enforcement** - Auto-remediation actions  
✅ **Resource type flexibility** - Works across all cloud resource types  

---

## 9. Success Metrics

### Tag Coverage
- **Target**: 90%+ resources have all critical tags
- **Metric**: `(resources_with_critical_tags / total_resources) * 100`

### ML Accuracy
- **Target**: 85%+ accuracy for environment tag
- **Metric**: `correct_predictions / total_predictions`

### Compliance Score
- **Target**: 95%+ compliance across all policies
- **Metric**: `compliant_resources / total_resources`

### Automation Rate
- **Target**: 70%+ tags auto-applied
- **Metric**: `(auto_applied_tags / total_virtual_tags) * 100`

---

## 10. Security Considerations

1. **Data Encryption**: All tags encrypted at rest in PostgreSQL
2. **Access Control**: RBAC for tag management operations
3. **Audit Trail**: Complete history of all tag modifications
4. **API Authentication**: JWT tokens with role-based permissions
5. **Data Privacy**: PII detection in tag values with automatic redaction
6. **Network Security**: mTLS for inter-service communication

---

## 11. Scalability Considerations

1. **Database Partitioning**: Partition `virtual_tags` and `tag_audit` tables by date
2. **Caching**: Redis cache for frequently accessed tags
3. **Async Processing**: Queue-based architecture for heavy operations
4. **Read Replicas**: PostgreSQL read replicas for query performance
5. **Elasticsearch Sharding**: Distribute index across multiple shards
6. **Horizontal Scaling**: Kubernetes-based auto-scaling for all services

---

## Appendix A: Tag Taxonomy (Production Ready)

### Critical Tags (Required)
1. **environment**: `production|staging|development|sandbox|test`
2. **cost-center**: Department/team identifier
3. **owner**: Email of responsible person/team

### High Priority Tags
4. **project**: Project identifier
5. **team**: Team name
6. **application**: Application/service name

### Medium Priority Tags
7. **business-unit**: Business division
8. **data-classification**: `public|internal|confidential|restricted`
9. **backup**: Backup schedule
10. **auto-stop**: Auto-shutdown schedule

### Low Priority Tags
11. **compliance**: Compliance framework (e.g., `pci-dss`, `hipaa`)
12. **expiration-date**: Resource cleanup date
13. **created-by**: Creator username

---

## Appendix B: Example Use Cases

### Use Case 1: Auto-tag Production Resources
```json
{
  "rule_name": "Production Environment Detection",
  "conditions": {
    "operator": "OR",
    "rules": [
      {"field": "name", "operator": "CONTAINS", "value": "prod"},
      {"field": "native_tags.Environment", "operator": "EQUALS", "value": "Production"}
    ]
  },
  "actions": {
    "apply_tags": [
      {"tag_key": "environment", "tag_value": "production"},
      {"tag_key": "backup", "tag_value": "daily"},
      {"tag_key": "data-classification", "tag_value": "confidential"}
    ]
  }
}
```

### Use Case 2: Enforce Required Tags for Production Databases
```json
{
  "policy_name": "Production Database Requirements",
  "policy_type": "CONDITIONAL_REQUIREMENT",
  "conditions": {
    "resource_type": "IN:rds,dynamodb,cloud-sql",
    "tags.environment": "production"
  },
  "requirements": {
    "required_tags": ["backup", "owner", "data-classification", "retention-days"]
  }
}
```

### Use Case 3: Normalize Cost Center Tags
```json
{
  "mapping_name": "Cost Center Normalization",
  "mappings": [
    {
      "source_key": "CostCenter",
      "target_key": "cost-center",
      "value_mappings": {
        "ENG": "engineering",
        "MKT": "marketing",
        "OPS": "operations",
        "SALES": "sales"
      }
    }
  ]
}
```

---

**Schema Version**: 1.0.0  
**Last Updated**: 2025-11-25  
**Author**: CloudTuner FinOps Team  
**Status**: Production Ready
