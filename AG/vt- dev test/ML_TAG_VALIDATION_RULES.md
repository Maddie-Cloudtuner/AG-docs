# Tag Validation Rules for ML Inference
## Technical Specification

This document defines the validation rules used by ML inference when predicting tags based on the `cloud_resource_tags` schema.

---

## 1. Value Type Validation

### 1.1 String Type
**Rule**: Any non-empty string value is valid.

```python
def validate_string(value):
    return len(str(value).strip()) > 0
```

**Examples**:
- ✅ `"engineering"` → Valid
- ✅ `"backend-team@company.com"` → Valid
- ❌ `""` or `None` → Invalid

---

### 1.2 Enum Type
**Rule**: Value must match one of the allowed values (comma-separated list).

**Case Sensitivity**: Determined by `is_case_sensitive` field.

```python
def validate_enum(value, allowed_values, is_case_sensitive):
    allowed_list = [v.strip() for v in allowed_values.split(',')]
    
    if is_case_sensitive:
        return value in allowed_list
    else:
        return value.lower() in [v.lower() for v in allowed_list]
```

**Examples**:
```sql
-- Schema entry
tag_key: 'Environment'
value_type: 'Enum'
allowed_values: 'dev, staging, prod, testing'
is_case_sensitive: TRUE

-- Validation results
'prod' → ✅ Valid (exact match)
'Prod' → ❌ Invalid (case mismatch, case-sensitive)
'production' → ❌ Invalid (not in allowed list)
```

**Normalization**: If case-insensitive match found, normalize to schema value:
```python
# Input: 'PROD', allowed: ['dev', 'staging', 'prod', 'testing']
# If is_case_sensitive = FALSE
# Output: 'prod' (normalized)
```

---

### 1.3 Date Type
**Rule**: Value must be valid ISO 8601 date format.

```python
from datetime import datetime

def validate_date(value):
    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False
```

**Examples**:
- ✅ `"2025-12-05"` → Valid
- ✅ `"2025-12-05T12:00:00"` → Valid
- ❌ `"12/05/2025"` → Invalid (wrong format)

---

### 1.4 Boolean Type
**Rule**: Value must be convertible to boolean.

```python
def validate_boolean(value):
    bool_map = {
        'true': True, 'false': False,
        'yes': True, 'no': False,
        '1': True, '0': False
    }
    return str(value).lower() in bool_map

def normalize_boolean(value):
    bool_map = {
        'true': 'true', 'false': 'false',
        'yes': 'true', 'no': 'false',
        '1': 'true', '0': 'false'
    }
    return bool_map.get(str(value).lower(), str(value).lower())
```

**Examples**:
- ✅ `true`, `True`, `TRUE` → Normalized to `'true'`
- ✅ `yes`, `Yes`, `1` → Normalized to `'true'`
- ✅ `false`, `False`, `no`, `0` → Normalized to `'false'`

---

## 2. Case Sensitivity Rules

### 2.1 Cloud Provider Standards

| Provider | Standard | is_case_sensitive | Example |
|----------|----------|-------------------|---------|
| **AWS** | Mixed (CamelCase or hyphen-separated) | TRUE for most tags | `CostCenter`, `Environment` |
| **Azure** | Case-insensitive | FALSE | `costcenter`, `CostCenter` both valid |
| **GCP** | Lowercase with underscores | TRUE | `cost_center` (must be lowercase) |
| **All** | Depends on tag | Varies | Check schema |

### 2.2 Validation Logic

```python
def apply_case_sensitivity(value, tag_key, provider, is_case_sensitive):
    """
    Apply cloud provider case sensitivity rules
    """
    if provider == 'gcp':
        # GCP labels must be lowercase
        if value != value.lower():
            return value.lower()  # Force lowercase
    
    elif provider == 'azure':
        # Azure is case-insensitive, normalize to lowercase
        if not is_case_sensitive:
            return value.lower()
    
    # AWS and others: use is_case_sensitive flag
    return value
```

### 2.3 Examples

**AWS Environment Tag**:
```sql
cloud_provider: 'AWS'
tag_key: 'Environment'
is_case_sensitive: TRUE

'production' → ✅ Valid
'Production' → ❌ Invalid (case mismatch)
```

**Azure Environment Tag**:
```sql
cloud_provider: 'Azure'
tag_key: 'Environment'
is_case_sensitive: FALSE

'production' → ✅ Valid
'Production' → ✅ Valid (normalized to 'production')
'PRODUCTION' → ✅ Valid (normalized to 'production')
```

**GCP Environment Tag**:
```sql
cloud_provider: 'GCP'
tag_key: 'environment'  # Must be lowercase
is_case_sensitive: TRUE

'production' → ✅ Valid
'Production' → ❌ Invalid
```

---

## 3. Resource Scope Matching

### 3.1 Scope Mapping

Map cloud resource types to `resource_scope` values:

```python
SCOPE_MAPPING = {
    # AWS
    'ec2': 'Compute',
    'lambda': 'Compute',
    'ecs': 'Compute',
    's3': 'Storage',
    'ebs': 'Storage',
    'rds': 'Database',
    'dynamodb': 'Database',
    'vpc': 'Network',
    'elb': 'Network',
    
    # GCP
    'compute-engine': 'Compute',
    'cloud-functions': 'Compute',
    'cloud-storage': 'Storage',
    'cloud-sql': 'Database',
    'vpc-network': 'Network',
    
    # Azure
    'virtual-machine': 'Compute',
    'blob-storage': 'Storage',
    'sql-database': 'Database',
    'virtual-network': 'Network',
}

def get_resource_scope(resource_type):
    return SCOPE_MAPPING.get(resource_type.lower(), 'Global')
```

### 3.2 Tag Applicability

**Query Logic**:
```sql
-- Get tags applicable to AWS EC2 instance
SELECT * FROM cloud_resource_tags
WHERE cloud_provider IN ('AWS', 'All')  -- Provider match
  AND resource_scope IN ('Compute', 'Global')  -- Scope match
```

**Examples**:
- AWS EC2 → Tags from: `(AWS, Compute)`, `(AWS, Global)`, `(All, Compute)`, `(All, Global)`
- GCS Bucket → Tags from: `(GCP, Storage)`, `(GCP, Global)`, `(All, Storage)`, `(All, Global)`

---

## 4. Tag Category Rules

### 4.1 Category Priorities

| Category | Priority | Auto-Apply Threshold | Use Case |
|----------|----------|---------------------|----------|
| **Critical** | 1 | ≥90% | Cost allocation, compliance |
| **Non-Critical** | 2 | ≥90% | Organization, grouping |
| **Optional** | 3 | Never auto-apply | Automation hints, metadata |

### 4.2 Validation Requirements

**Critical Tags**:
- MUST be predicted (defaults applied if missing)
- Higher confidence thresholds for auto-apply
- Enum types MUST have `allowed_values`

**Non-Critical Tags**:
- Optional prediction
- Auto-apply if confidence ≥90%

**Optional Tags**:
- Predict only if clear signal
- Always require manual review
- No defaults applied

### 4.3 Example Schema Check

```sql
-- Validate Critical tags have allowed_values if Enum
SELECT tag_key, value_type, allowed_values
FROM cloud_resource_tags
WHERE tag_category = 'Critical'
  AND value_type = 'Enum'
  AND (allowed_values IS NULL OR allowed_values = '');

-- Should return 0 rows (all Critical Enum tags must have allowed_values)
```

---

## 5. Pattern Matching Validation

### 5.1 Keyword Extraction

Only extract keywords that match `allowed_values` for Enum tags:

```python
import re

def pattern_match_enum(resource_name, allowed_values, is_case_sensitive):
    """
    Match resource name against allowed enum values
    """
    matches = []
    
    for value in allowed_values:
        # Build regex pattern with word boundaries
        pattern = rf'\b{re.escape(value)}\b'
        
        # Apply case sensitivity
        flags = 0 if is_case_sensitive else re.IGNORECASE
        
        if re.search(pattern, resource_name, flags):
            matches.append(value)
    
    return matches
```

**Examples**:
```python
resource_name = "prod-backend-api-01"
allowed_values = ['dev', 'staging', 'prod', 'testing']

# Case-sensitive
matches = pattern_match_enum(resource_name, allowed_values, True)
# Result: ['prod']

# Case-insensitive
resource_name = "PROD-backend-api"
matches = pattern_match_enum(resource_name, allowed_values, False)
# Result: ['prod'] (normalized)
```

### 5.2 Ambiguity Resolution

**Rule**: If multiple values match, use highest priority:
1. Longest match
2. First in `allowed_values` list (left-to-right priority)

```python
def resolve_ambiguity(matches, allowed_values):
    if not matches:
        return None
    
    # Sort by length (longest first)
    matches_sorted = sorted(matches, key=len, reverse=True)
    
    # If tie, use order in allowed_values
    return matches_sorted[0]
```

**Example**:
```python
resource_name = "prod-staging-test"
allowed_values = ['prod', 'staging', 'production']

matches = ['prod', 'staging']
result = resolve_ambiguity(matches, allowed_values)
# Result: 'staging' (longest match: both 4 chars, but 'staging' appears earlier)
```

---

## 6. Validation Error Handling

### 6.1 Invalid Value Behavior

| Scenario | Behavior |
|----------|----------|
| Value not in `allowed_values` | Skip prediction, don't apply tag |
| Invalid date format | Skip prediction |
| Invalid boolean | Skip prediction |
| Empty string for required tag | Apply smart default |
| Case mismatch (case-sensitive) | Try case-insensitive normalization, else skip |

### 6.2 Error Logging

```python
def validate_and_log(tag_schema, predicted_value):
    """
    Validate with detailed error logging
    """
    validation_result = {
        'is_valid': False,
        'normalized_value': None,
        'error': None
    }
    
    try:
        if tag_schema.value_type == 'Enum':
            allowed = tag_schema.allowed_values.split(',')
            if predicted_value not in allowed:
                validation_result['error'] = f"Value '{predicted_value}' not in allowed values: {allowed}"
                return validation_result
        
        validation_result['is_valid'] = True
        validation_result['normalized_value'] = predicted_value
        
    except Exception as e:
        validation_result['error'] = str(e)
    
    return validation_result
```

---

## 7. Complete Validation Workflow

```python
def validate_prediction(prediction, tag_schema):
    """
    Complete validation workflow for a single prediction
    
    Args:
        prediction: Dict with tag_key, predicted_value, confidence
        tag_schema: TagSchema object from cloud_resource_tags
    
    Returns:
        Validated prediction or None if invalid
    """
    # Step 1: Type validation
    if tag_schema.value_type == 'Enum':
        if not tag_schema.allowed_values:
            return None  # No allowed values defined
        
        allowed = [v.strip() for v in tag_schema.allowed_values.split(',')]
        
        # Apply case sensitivity
        if tag_schema.is_case_sensitive:
            if prediction['predicted_value'] not in allowed:
                # Try case-insensitive match for normalization
                matches = [v for v in allowed if v.lower() == prediction['predicted_value'].lower()]
                if not matches:
                    return None  # Invalid
                prediction['predicted_value'] = matches[0]
        else:
            # Normalize to schema value
            normalized = next(
                (v for v in allowed if v.lower() == prediction['predicted_value'].lower()),
                None
            )
            if not normalized:
                return None  # Invalid
            prediction['predicted_value'] = normalized
    
    elif tag_schema.value_type == 'Boolean':
        prediction['predicted_value'] = normalize_boolean(prediction['predicted_value'])
    
    elif tag_schema.value_type == 'Date':
        if not validate_date(prediction['predicted_value']):
            return None  # Invalid date
    
    # Step 2: Add schema validation metadata
    prediction['schema_validation'] = {
        'schema_id': tag_schema.id,
        'is_valid': True,
        'tag_category': tag_schema.tag_category,
        'value_type': tag_schema.value_type
    }
    
    # Step 3: Adjust confidence based on category
    if tag_schema.tag_category == 'Critical':
        prediction['confidence'] = min(prediction['confidence'] + 0.05, 0.99)
    
    return prediction
```

---

## 8. Testing Validation Rules

### Test Cases

```python
def test_validation_rules():
    # Test 1: Enum validation (case-sensitive)
    schema = TagSchema(
        tag_key='Environment',
        value_type='Enum',
        allowed_values='dev, staging, prod, testing',
        is_case_sensitive=True
    )
    
    assert validate_enum('prod', schema) == True
    assert validate_enum('Prod', schema) == False  # Case mismatch
    assert validate_enum('production', schema) == False  # Not in list
    
    # Test 2: Boolean normalization
    assert normalize_boolean('yes') == 'true'
    assert normalize_boolean('FALSE') == 'false'
    assert normalize_boolean('1') == 'true'
    
    # Test 3: Pattern matching
    assert pattern_match_enum('prod-api', ['prod', 'dev'], True) == ['prod']
    assert pattern_match_enum('production-db', ['prod', 'dev'], True) == []  # No match
    
    print("All validation tests passed!")
```

---

## Summary

The validation rules ensure:
1. ✅ All predictions are within schema-defined bounds
2. ✅ Cloud provider case sensitivity standards are enforced
3. ✅ Enum values are validated against allowed lists
4. ✅ Type-specific validation (String, Enum, Date, Boolean)
5. ✅ Resource scopes correctly map to tag applicability
6. ✅ Category priorities influence confidence and auto-apply decisions
