# Quick Start Guide
## ML Inference with Schema Validation

Get started in 5 minutes! This guide will help you set up and run the ML inference system with your Excel data.

---

## 🚀 One-Command Setup (Windows)

```powershell
# Run the automated setup script
cd "c:\Users\LENOVO\Desktop\my_docs\AG\vt- dev test"
.\setup.bat
```

The script will:
1. ✅ Check Python installation
2. ✅ Create virtual environment
3. ✅ Install all dependencies
4. ✅ Set up configuration
5. ✅ Convert Excel to SQL
6. ✅ Initialize database

---

## 📋 Manual Setup (If you prefer step-by-step)

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure Environment
```powershell
# Copy template
copy .env.example .env

# Edit .env and set your database password
notepad .env
```

### 3. Convert Excel to SQL
```powershell
cd ..
python excel_to_sql_converter.py
cd "vt- dev test"
```

### 4. Setup Database
```powershell
# Create database
psql -U postgres -c "CREATE DATABASE cloudtuner_db;"

# Load cloud_resource_tags table
psql -U postgres -d cloudtuner_db -f "..\cloud_resource_tags_from_excel.sql"

# Load ML functions
psql -U postgres -d cloudtuner_db -f "ml_inference_config.sql"
```

---

## ✅ Verify Installation

### Test Database Connection
```powershell
python -c "from python.db_utils import test_connection; test_connection()"
```

Expected output:
```
Connected to database: cloudtuner_db
Database connection successful: PostgreSQL 14.x...
```

### Run Test Suite
```powershell
cd python
python test_ml_inference.py
```

Expected output:
```
╔══════════════════════════════════════════════════════╗
║  ML INFERENCE SCHEMA INTEGRATION - TEST SUITE         ║
╚══════════════════════════════════════════════════════╝

...
✅✅✅ ALL TESTS PASSED! ✅✅✅
```

---

## 🎯 Try It Out!

### Run Example Predictions
```powershell
cd python
python example_predictions.py
```

You'll see 4 automated examples:
1. **Well-tagged production resource** - Shows full normalization
2. **Minimal tags** - Demonstrates pattern matching
3. **No patterns** - Uses smart defaults
4. **Database resource** - Scope-specific tags
5. **Interactive mode** - Enter your own resource details

### Example Output
```
📦 Resource: prod-backend-api-42
   Provider: AWS
   Type: ec2
   Native Tags: {'Environment': 'Production', 'Team': 'backend'}

🎯 Generated 4 predictions:

1. ✅ AUTO-APPLY
   Tag: environment = prod
   Confidence: 98%
   Source: NORMALIZED
   ✓ Schema Validated: Critical tag
   Reasoning: Normalized from native tag 'Environment'...

2. ✅ AUTO-APPLY
   Tag: team = backend
   Confidence: 98%
   Source: NORMALIZED
   ...
```

---

## 🔧 Using in Your Code

### Basic Usage
```python
from python.ml_feature_extraction import SchemaValidatedInference
from python.db_utils import get_db_connection

# Initialize
conn = get_db_connection()
inference = SchemaValidatedInference(conn)

# Predict tags
resource = {
    "provider": "aws",
    "resource_type": "ec2",
    "name": "my-server",
    "native_tags": {"Team": "backend"}
}

predictions = inference.predict_tags(resource)

# Apply high-confidence predictions
for pred in predictions:
    if pred['confidence'] >= 0.90:
        apply_virtual_tag(resource_id, pred['tag_key'], pred['predicted_value'])

conn.close()
```

### With Configuration
```python
from python.config import Config
from python.ml_feature_extraction import SchemaValidatedInference
from python.db_utils import get_db_connection

conn = get_db_connection()
inference = SchemaValidatedInference(conn)

predictions = inference.predict_tags(resource)

# Use configured thresholds
for pred in predictions:
    if pred['confidence'] >= Config.ML_CONFIDENCE_AUTO_APPLY:
        # Auto-apply
        apply_virtual_tag(pred)
    elif pred['confidence'] >= Config.ML_CONFIDENCE_REVIEW:
        # Queue for review
        queue_for_review(pred)
    else:
        # Show as alternative
        show_alternative(pred)
```

---

## 📊 What's Happening Under the Hood

### Without Schema Validation (Old Way - HIGH HALLUCINATION)
```python
# Can predict ANY value
environment = detect_from_name(resource_name)  # Could be anything!
# Result: "production", "prod", "prd", "p", etc. ❌
```

### With Schema Validation (New Way - ZERO HALLUCINATION)
```python
# Query schema first
valid_envs = get_tag_allowed_values('AWS', 'Environment')
# Returns: ['dev', 'staging', 'prod', 'testing']

# Only predict if matches schema
if detected_keyword in valid_envs:
    environment = detected_keyword  # ✅ Guaranteed valid
else:
    environment = None  # Don't hallucinate!
```

---

## 🎓 Understanding the Output

### Confidence Badges

| Badge | Confidence | Meaning | Auto-Apply? |
|-------|-----------|---------|-------------|
| ✅ AUTO-APPLY | ≥90% | High confidence, safe to apply | Yes |
| ⚠️ REVIEW | 70-89% | Medium confidence, needs review | No |
| ℹ️ ALTERNATIVE | <70% | Low confidence, show as option | No |

### Source Types

| Source | Description |
|--------|-------------|
| NORMALIZED | From native cloud tag, validated against schema |
| PATTERN_MATCH | Detected from resource name, matches allowed_values |
| SMART_DEFAULT | Intelligent default for Critical tags |

### Schema Validation

Every prediction includes:
```json
{
  "schema_validation": {
    "schema_id": 1,
    "is_valid": true,
    "tag_category": "Critical",
    "value_type": "Enum"
  }
}
```

This proves the prediction came from your `cloud_resource_tags` table!

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'psycopg2'"
```powershell
pip install psycopg2-binary
```

### "Database connection failed"
1. Check PostgreSQL is running: `psql -U postgres`
2. Verify .env file has correct DB_PASSWORD
3. Test connection: `python -c "from python.db_utils import test_connection; test_connection()"`

### "cloud_resource_tags table not found"
```powershell
# Run database setup
psql -U postgres -d cloudtuner_db -f "..\cloud_resource_tags_from_excel.sql"
psql -U postgres -d cloudtuner_db -f "ml_inference_config.sql"
```

### "No predictions generated"
1. Check if tags exist for this resource type:
   ```sql
   SELECT * FROM get_valid_tags_for_resource('aws', 'Compute');
   ```
2. Verify Excel file has tags for the resource scope

---

## 📚 Next Steps

1. **Read the docs**: `README_ML_INFERENCE.md` - Complete guide
2. **Understand validation**: `ML_TAG_VALIDATION_RULES.md` - Technical specs
3. **See architecture**: `ML_INFERENCE_SCHEMA_INTEGRATION.md` - How it works
4. **Integrate**: Add to your `virtual_tagger_worker` service

---

## 💡 Pro Tips

1. **Start simple**: Run `example_predictions.py` to see it work
2. **Test with your data**: Use the interactive mode (option 5)
3. **Monitor confidence**: Check which predictions auto-apply vs need review
4. **Update schema**: Edit Excel → run converter → reload DB
5. **Cache enabled**: Schema cached for performance (clear by restarting)

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Database created and loaded
- [ ] Test suite passes
- [ ] Examples run successfully
- [ ] Understand confidence thresholds
- [ ] Ready to integrate!

---

**🎉 Congratulations!** You now have a production-ready ML inference system that:
- ✅ Uses your Excel as single source of truth
- ✅ Eliminates hallucination through schema validation
- ✅ Provides transparent reasoning
- ✅ Auto-applies high-confidence predictions

Questions? Check the full documentation in `README_ML_INFERENCE.md`
