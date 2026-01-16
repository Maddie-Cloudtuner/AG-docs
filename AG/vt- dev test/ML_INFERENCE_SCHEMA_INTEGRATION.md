# ML Inference Schema Integration Guide
## Using cloud_resource_tags as Authoritative Reference

This document explains how the Virtual Tagging ML inference system uses the `cloud_resource_tags` table as the authoritative reference to reduce hallucination and improve prediction accuracy.

---

## Overview

**Problem**: Previous ML inference relied on parsing raw resource metadata (names, types, unstructured native tags), leading to high hallucination rates when resources had ambiguous or missing information.

**Solution**: Use the `cloud_resource_tags` table as ground truth. All ML predictions are constrained to the standardized tag schema, with validation against allowed values, case sensitivity rules, and tag categories.

---

## Architecture Changes

### Before: 3-Tier Detection (Metadata-Based)
```
1. Native Tag Extraction → Parse raw cloud tags
2. Pattern Matching → Search for keywords in resource names
3. Intelligent Defaults → Arbitrary defaults based on assumptions
```

**Issue**: High hallucination when resources don't match patterns.

### After: 4-Tier Schema-Validated Detection
```
1. Schema Query → Get valid tags from cloud_resource_tags table
2. Native Tag Normalization → Validate against allowed_values
3. Schema-Constrained Pattern Matching → Only keywords from schema
4. Category-Based Defaults → Defaults based on tag_category priority
```

**Benefit**: Predictions are always within defined schema bounds.

---

## ML Inference Flow

### Step 1: Resource Classification
```python
# Identify resource provider and scope
resource = {
    "provider": "aws",
    "resource_type": "ec2",
    "name": "prod-web-server-01",
    "native_tags": {"Environment": "Production"}
}

# Map resource_type to resource_scope
scope_mapping = {
    "ec2": "Compute",
    "s3": "Storage",
    "rds": "Database",
    "vpc": "Network"
}
resource_scope = scope_mapping.get(resource["resource_type"], "Global")
```

### Step 2: Query Valid Tags from Schema
```python
# Query cloud_resource_tags table
valid_tags = query_db("""
    SELECT tag_key, tag_category, value_type, allowed_values, 
           is_case_sensitive, description
    FROM cloud_resource_tags
    WHERE cloud_provider IN (?, 'All')
      AND resource_scope IN (?, 'Global')
    ORDER BY 
        CASE tag_category 
            WHEN 'Critical' THEN 1
            WHEN 'Non-Critical' THEN 2
            WHEN 'Optional' THEN 3
        END
""", [resource["provider"], resource_scope])

# Result: Only predict tags that exist in this list
# Example for AWS Compute:
# - environment (Critical, Enum, dev,staging,prod,testing)
# - cost-center (Critical, String)
# - owner (Critical, String)
# - instance-role (Non-Critical, Enum, web-server,app-server,...)
# - auto-shutdown (Optional, Boolean)
```

### Step 3: Native Tag Validation
```python
def validate_native_tag(native_key, native_value, valid_tags_df):
    """
    Validate and normalize native cloud tags against schema
    """
    # Find matching tag in schema (case-insensitive search)
    schema_tag = valid_tags_df[
        valid_tags_df['tag_key'].str.lower() == native_key.lower()
    ].iloc[0] if len(valid_tags_df) > 0 else None
    
    if not schema_tag:
        # Tag not in schema, skip
        return None
    
    # Normalize value
    normalized_value = native_value
    
    # If Enum type, validate against allowed_values
    if schema_tag['value_type'] == 'Enum':
        allowed = [v.strip() for v in schema_tag['allowed_values'].split(',')]
        
        # Case-sensitive matching
        if schema_tag['is_case_sensitive']:
            if normalized_value not in allowed:
                # Try to find case-insensitive match for normalization
                matches = [v for v in allowed if v.lower() == normalized_value.lower()]
                if matches:
                    normalized_value = matches[0]
                else:
                    return None  # Invalid value
        else:
            # Case-insensitive matching
            normalized_value = next(
                (v for v in allowed if v.lower() == normalized_value.lower()),
                None
            )
            if not normalized_value:
                return None
    
    return {
        "tag_key": schema_tag['tag_key'],
        "tag_value": normalized_value,
        "confidence": 0.98,
        "source": "NORMALIZED",
        "reasoning": f"Normalized from native tag '{native_key}'. {schema_tag['description']}"
    }

# Example usage
native_tags = {"Environment": "Production"}
result = validate_native_tag("Environment", "Production", valid_tags)
# Result: {"tag_key": "environment", "tag_value": "prod", "confidence": 0.98, ...}
```

### Step 4: Schema-Constrained Pattern Matching
```python
def pattern_match_with_schema(resource_name, valid_tags_df):
    """
    Pattern matching constrained to schema-defined values
    """
    predictions = []
    
    for idx, tag_schema in valid_tags_df.iterrows():
        if tag_schema['value_type'] != 'Enum':
            continue  # Only pattern match for Enum types
        
        allowed_values = [v.strip() for v in tag_schema['allowed_values'].split(',')]
        
        # Check if any allowed value appears in resource name
        for value in allowed_values:
            # Build search pattern
            pattern = value.lower() if not tag_schema['is_case_sensitive'] else value
            search_in = resource_name.lower() if not tag_schema['is_case_sensitive'] else resource_name
            
            if pattern in search_in:
                confidence = 0.95 if tag_schema['tag_category'] == 'Critical' else 0.85
                
                predictions.append({
                    "tag_key": tag_schema['tag_key'],
                    "tag_value": value,
                    "confidence": confidence,
                    "source": "PATTERN_MATCH",
                    "reasoning": f"Resource name contains '{value}' keyword. {tag_schema['description']}"
                })
                break  # Only predict one value per tag
    
    return predictions

# Example
resource_name = "prod-web-server-01"
predictions = pattern_match_with_schema(resource_name, valid_tags)
# Result: environment=production (95% confidence)
```

### Step 5: Category-Based Intelligent Defaults
```python
def apply_smart_defaults(predicted_tags, valid_tags_df, resource):
    """
    Apply defaults for missing Critical tags only
    """
    predicted_keys = [p['tag_key'] for p in predicted_tags]
    
    # Get missing Critical tags
    critical_tags = valid_tags_df[
        (valid_tags_df['tag_category'] == 'Critical') &
        (~valid_tags_df['tag_key'].isin(predicted_keys))
    ]
    
    defaults = []
    for idx, tag_schema in critical_tags.iterrows():
        default_value = None
        confidence = 0.60
        reasoning = ""
        
        if tag_schema['tag_key'] == 'environment':
            # Safer to default to dev than prod
            default_value = 'development'
            reasoning = "Default to development environment (safer assumption)"
        
        elif tag_schema['tag_key'] == 'cost-center':
            # Derive from environment if available
            env_tag = next((p for p in predicted_tags if p['tag_key'] == 'environment'), None)
            if env_tag and env_tag['tag_value'] == 'production':
                default_value = 'production-ops'
                confidence = 0.85
            else:
                default_value = 'engineering'
                confidence = 0.65
            reasoning = f"Default cost center based on environment inference"
        
        if default_value:
            defaults.append({
                "tag_key": tag_schema['tag_key'],
                "tag_value": default_value,
                "confidence": confidence,
                "source": "SMART_DEFAULT",
                "reasoning": f"{reasoning}. {tag_schema['description']}"
            })
    
    return defaults
```

---

## Confidence Scoring Algorithm

### Schema-Based Confidence Levels

| Detection Method | Tag Category | Has Enum Match | Confidence | Auto-Apply |
|-----------------|--------------|----------------|------------|------------|
| Native tag normalization | Critical | Yes | 98% | ✅ Yes |
| Native tag normalization | Critical | No | 95% | ✅ Yes |
| Native tag normalization | Non-Critical | Yes | 95% | ✅ Yes |
| Pattern match | Critical | Yes | 95% | ✅ Yes |
| Pattern match | Non-Critical | Yes | 85% | ⚠️ Review |
| Pattern match | Optional | Yes | 75% | ⚠️ Review |
| Smart default | Critical | N/A | 60-85% | ❌ No |
| Outside schema | Any | N/A | <50% | ❌ Discard |

### Confidence Calculation
```python
def calculate_confidence(detection_method, tag_category, enum_match):
    base_confidence = {
        "NORMALIZED": 0.98,
        "PATTERN_MATCH": 0.85,
        "SMART_DEFAULT": 0.65
    }[detection_method]
    
    # Category boost
    if tag_category == "Critical":
        base_confidence += 0.10
    elif tag_category == "Optional":
        base_confidence -= 0.10
    
    # Enum match boost
    if enum_match and detection_method == "PATTERN_MATCH":
        base_confidence += 0.10
    
    return min(base_confidence, 0.99)
```

---

## Complete Example Workflow

### Input Resource
```json
{
  "provider": "aws",
  "resource_type": "ec2",
  "resource_id": "i-1234567890abcdef0",
  "name": "prod-backend-api-42",
  "native_tags": {
    "Team": "backend",
    "CostCenter": "ENG"
  }
}
```

### ML Inference Process

**Step 1**: Query schema → Get 15 valid tags for AWS Compute
**Step 2**: Validate native tags
- Team → team (normalized, 98% confidence)
- CostCenter → cost-center (value mapped ENG→engineering, 95% confidence)

**Step 3**: Pattern matching
- Found "prod" in name → environment=production (95% confidence)
- Found "backend" in name → already have team tag, skip

**Step 4**: Smart defaults
- Critical tag "owner" missing → Derive from team → owner=backend-team@company.com (75% confidence)

### Final Output
```json
{
  "resource_id": "i-1234567890abcdef0",
  "predictions": [
    {
      "tag_key": "environment",
      "predicted_value": "production",
      "confidence": 0.95,
      "source": "PATTERN_MATCH",
      "schema_validation": {
        "is_valid": true,
        "tag_category": "Critical",
        "value_type": "Enum",
        "allowed_values": "dev, staging, prod, testing"
      },
      "reasoning": "Resource name contains 'prod' keyword. Deployment environment classification for resource lifecycle management.",
      "auto_applied": true
    },
    {
      "tag_key": "team",
      "predicted_value": "backend",
      "confidence": 0.98,
      "source": "NORMALIZED",
      "schema_validation": {
        "is_valid": true,
        "tag_category": "Non-Critical"
      },
      "reasoning": "Normalized from native tag 'Team'.",
      "auto_applied": true
    },
    {
      "tag_key": "cost-center",
      "predicted_value": "engineering",
      "confidence": 0.95,
      "source": "NORMALIZED",
      "schema_validation": {
        "is_valid": true,
        "tag_category": "Critical"
      },
      "reasoning": "Normalized from native tag 'CostCenter' (ENG→engineering mapping).",
      "auto_applied": true
    },
    {
      "tag_key": "owner",
      "predicted_value": "backend-team@company.com",
      "confidence": 0.75,
      "source": "SMART_DEFAULT",
      "schema_validation": {
        "is_valid": true,
        "tag_category": "Critical"
      },
      "reasoning": "Derived from team tag. Individual or team responsible for the resource.",
      "auto_applied": false
    }
  ]
}
```

---

## Key Benefits

1. **Reduced Hallucination**: Predictions constrained to schema-defined values
2. **Improved Accuracy**: Enum validation ensures only valid values are predicted
3. **Case Sensitivity**: Automatic enforcement per cloud provider standards
4. **Clear Reasoning**: Descriptions from schema explain why tags were predicted
5. **Confidence Transparency**: Category-based scoring shows prediction reliability
6. **Audit Trail**: Schema IDs tracked for compliance and debugging

---

## Integration Points

### Database Query Layer
See: `ml_inference_config.sql` for database functions

### Python ML Pipeline
See: `python/ml_feature_extraction.py` for implementation

### API Response Enhancement
See: `../vt/schema.md` Section 1.7 for updated ML Inference Schema

### Frontend Display
Tags display with "Schema Validated ✓" badge and category indicators
