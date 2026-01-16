# ML Inference Setup Guide
## Using cloud_resource_tags with Virtual Tagging

This guide explains how to set up and use the ML inference system with your `cloud_resource_tags_complete 1.xlsx` data.

---

## 📁 Files Created

### Documentation
1. **ML_INFERENCE_SCHEMA_INTEGRATION.md** - Complete architecture and workflow guide
2. **ML_TAG_VALIDATION_RULES.md** - Technical validation specifications

### Implementation
3. **ml_inference_config.sql** - PostgreSQL functions and views
4. **python/ml_feature_extraction.py** - Python ML inference engine
5. **python/test_ml_inference.py** - Test suite

### Support Files
6. **../excel_to_sql_converter.py** - Convert Excel to SQL
7. **../EXCEL_VALIDATION_CHECKLIST.md** - Excel validation guide

---

## 🚀 Quick Start

### Step 1: Prepare Your Excel Data

```powershell
# Install required Python packages
pip install pandas openpyxl psycopg2-binary

# Validate and convert Excel to SQL
cd c:\Users\LENOVO\Desktop\my_docs\AG
python excel_to_sql_converter.py
```

This will:
- ✅ Validate your Excel file structure
- ✅ Generate `cloud_resource_tags_from_excel.sql`
- ✅ Show summary statistics

### Step 2: Load Data into PostgreSQL

```powershell
# Create database (if not exists)
psql -U postgres -c "CREATE DATABASE cloudtuner_db;"

# Load the cloud_resource_tags table
psql -U postgres -d cloudtuner_db -f "c:\Users\LENOVO\Desktop\my_docs\AG\cloud_resource_tags_from_excel.sql"

# Load ML inference functions
psql -U postgres -d cloudtuner_db -f "c:\Users\LENOVO\Desktop\my_docs\AG\vt- dev test\ml_inference_config.sql"

# Verify installation
psql -U postgres -d cloudtuner_db -c "SELECT COUNT(*) FROM cloud_resource_tags;"
```

### Step 3: Test ML Inference

```powershell
cd "c:\Users\LENOVO\Desktop\my_docs\AG\vt- dev test\python"
python test_ml_inference.py
```

Expected output:
```
╔══════════════════════════════════════════════════════╗
║                                                        ║
║  ML INFERENCE SCHEMA INTEGRATION - TEST SUITE         ║
║                                                        ║
╚══════════════════════════════════════════════════════╝

TEST 1: Native Tag Validation
✅ Test 1.1 passed: Valid enum value
✅ Test 1.2 passed: Case normalization
...
✅✅✅ ALL TESTS PASSED! ✅✅✅
```

### Step 4: Integrate with Your Virtual Tagging System

Update your `virtual_tagger_worker` to use the new inference engine:

```python
from ml_feature_extraction import SchemaValidatedInference
import psycopg2

# Initialize
conn = psycopg2.connect(
    dbname="cloudtuner_db",
    user="postgres",
    password="your_password",
    host="localhost"
)

inference = SchemaValidatedInference(conn)

# Predict tags for a resource
resource = {
    "provider": "aws",
    "resource_type": "ec2",
    "name": "prod-backend-api-42",
    "native_tags": {"Team": "backend"}
}

predictions = inference.predict_tags(resource)

# Apply predictions with confidence >= 90%
for pred in predictions:
    if pred['confidence'] >= 0.90:
        apply_virtual_tag(resource_id, pred)
```

---

## 📊 How It Works

### Before (High Hallucination)
```
Resource Name: "my-server-xyz"
Native Tags: {}

ML Inference:
❌ Arbitrary keyword search → environment=production (60% confidence)
❌ Wild guessing → cost-center=engineering (50% confidence)
❌ No validation → can predict ANY value
```

### After (Schema-Validated)
```
Resource Name: "my-server-xyz"
Native Tags: {}

ML Inference:
1. Query cloud_resource_tags → Get valid tags for AWS Compute
2. Pattern match ONLY against allowed_values
3. Apply smart defaults for Critical tags only
   ✅ environment=dev (60% - safe default)
   ✅ cost-center=engineering (65% - derived default)
4. All predictions within schema bounds
```

---

## 🎯 Key Features

### 1. Schema-Constrained Predictions
- ✅ Only predicts tags that exist in `cloud_resource_tags` table
- ✅ Only suggests values from `allowed_values` for Enum types
- ✅ Respects `is_case_sensitive` per cloud provider

### 2. Confidence-Based Auto-Apply
| Confidence | Action | Example |
|-----------|--------|---------|
| ≥90% | Auto-apply | Native tag normalization, Pattern match for Critical tags |
| 70-89% | Suggest for review | Pattern match for Non-Critical, Derived defaults |
| <70% | Show as alternative | Smart defaults for missing Critical tags |

### 3. Validation & Normalization
- **AWS**: CamelCase or hyphen-separated, case-sensitive
- **Azure**: Case-insensitive normalization
- **GCP**: Enforce lowercase with underscores

### 4. Intelligent Reasoning
Every prediction includes:
- Source (NORMALIZED, PATTERN_MATCH, SMART_DEFAULT)
- Reasoning text from tag `description`
- Schema validation metadata
- Features used for prediction

---

## 🔧 Configuration

### Update Database Connection

Edit `python/ml_feature_extraction.py`:

```python
# Line ~450
conn = psycopg2.connect(
    dbname="cloudtuner_db",
    user="your_db_user",
    password="your_db_password",
    host="your_db_host",
    port=5432
)
```

### Customize Smart Defaults

Edit `apply_smart_defaults()` function in `ml_feature_extraction.py`:

```python
# Line ~280
if tag_schema.tag_key.lower() == 'environment':
    # Change default environment
    default_value = 'sandbox'  # Instead of 'development'
    confidence = 0.65
```

### Add Custom Resource Type Mappings

Edit SCOPE_MAPPING in `ml_feature_extraction.py`:

```python
# Line ~30
SCOPE_MAPPING = {
    'my-custom-type': 'Compute',
    # ... existing mappings
}
```

---

## 📈 Monitoring ML Performance

### Query Prediction Statistics

```sql
-- View ML inference success rate
SELECT 
    source,
    AVG(confidence) as avg_confidence,
    COUNT(*) as prediction_count
FROM ml_inference
GROUP BY source;

-- Check schema validation pass rate
SELECT 
    schema_validation->>'is_valid' as is_valid,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
FROM ml_inference
GROUP BY schema_validation->>'is_valid';
```

### Test Individual Tags

```sql
-- Test environment tag validation
SELECT * FROM validate_tag_value('AWS', 'Environment', 'prod');

-- Get all allowed values for a tag
SELECT get_tag_allowed_values('AWS', 'Environment');
```

---

## 🐛 Troubleshooting

### Issue: "No tags predicted"
```python
# Check if schema has tags for this resource type
SELECT * FROM get_valid_tags_for_resource('aws', 'Compute');
# Should return rows
```

### Issue: "Confidence too low"
```python
# Check tag category - Critical tags get +10% confidence boost
SELECT tag_category FROM cloud_resource_tags WHERE tag_key = 'your-tag';
```

### Issue: "Pattern not matching"
```python
# Verify allowed_values includes your keyword
SELECT allowed_values FROM cloud_resource_tags 
WHERE tag_key = 'environment';
# Should include 'prod', 'dev', etc.
```

---

## 📚 Documentation Reference

### For Developers
- **ML_INFERENCE_SCHEMA_INTEGRATION.md** - Complete workflow examples
- **ML_TAG_VALIDATION_RULES.md** - Validation logic specification
- **python/ml_feature_extraction.py** - Inline code documentation

### For Database Admins
- **ml_inference_config.sql** - SQL function definitions with examples

### For Data Curators
- **EXCEL_VALIDATION_CHECKLIST.md** - How to maintain tag schema
- **excel_to_sql_converter.py** - Validation and conversion tool

---

## 🔄 Updating Tag Schema

When you update `cloud_resource_tags_complete 1.xlsx`:

```powershell
# 1. Validate changes
python excel_to_sql_converter.py

# 2. Regenerate SQL
# Output: cloud_resource_tags_from_excel.sql

# 3. Apply to database
psql -U postgres -d cloudtuner_db -c "TRUNCATE cloud_resource_tags;"
psql -U postgres -d cloudtuner_db -f cloud_resource_tags_from_excel.sql

# 4. Refresh ML features
psql -U postgres -d cloudtuner_db -c "SELECT refresh_ml_tag_features();"

# 5. Clear cache in Python (restart application)
```

---

## ✅ Success Criteria

Your ML inference is working correctly if:

1. ✅ `test_ml_inference.py` passes all tests
2. ✅ Predictions have `schema_validation.is_valid = true`
3. ✅ No predictions outside `allowed_values` for Enum tags
4. ✅ Confidence scores align with detection method
5. ✅ Reasoning text is descriptive and helpful

---

## 🎓 Training Your Team

### For ML Engineers
Read: `ML_INFERENCE_SCHEMA_INTEGRATION.md` → Section "ML Inference Flow"

### For Backend Developers
1. Read: `python/ml_feature_extraction.py` docstrings
2. Run: `test_ml_inference.py`
3. Integrate: Use `SchemaValidatedInference` class

### For Frontend Developers
Display predictions with:
- Confidence badges (Green ≥90%, Yellow 70-89%, Red <70%)
- "Schema Validated ✓" indicator
- Tag category labels
- Reasoning tooltips

---

## 🚨 Production Checklist

Before deploying to production:

- [ ] Excel file validated with zero errors
- [ ] SQL loaded into production database
- [ ] All test cases passing
- [ ] Database connection configured for prod
- [ ] Monitoring dashboards set up
- [ ] Team trained on schema maintenance
- [ ] Rollback plan documented

---

## 💡 Pro Tips

1. **Start with Critical tags only** - Add Non-Critical and Optional tags gradually
2. **Monitor false positives** - Track `user_feedback` in ML schema to improve models
3. **Use materialized view** - Query `ml_tag_features` instead of base table for better performance
4. **Cache schema** - Already implemented in `SchemaValidatedInference.__init__`
5. **Regular audits** - Review `allowed_values` quarterly to add new patterns

---

## 🆘 Support

If you need help:
1. Check logs for specific error messages
2. Run `test_ml_inference.py` to isolate issues
3. Query database directly to verify schema
4. Review validation rules in `ML_TAG_VALIDATION_RULES.md`

For questions about the implementation, refer to the relevant documentation file based on your role.
