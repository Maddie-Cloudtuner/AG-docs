# Virtual Tagging ML Inference Project

Production-ready ML inference system that uses `cloud_resource_tags` table as authoritative reference to eliminate hallucination from raw metadata parsing.

## 🎯 What This Does

Transforms ML tag prediction from **hallucination-prone** to **schema-validated**:

**Before (High Hallucination)**:
- Predicts ANY value from arbitrary patterns
- No validation against allowed values
- Inconsistent tag names and values
- Confidence based on guessing

**After (Zero Hallucination)**:
- Only predicts values from your `cloud_resource_tags_complete 1.xlsx`
- Validates against `allowed_values` for Enum types
- Enforces case sensitivity per cloud provider
- Confidence based on schema matching

## 🚀 Quick Start

```powershell
# One command setup
.\setup.bat

# Run examples
python python\example_predictions.py

# Run tests
python python\test_ml_inference.py
```

**Full guide**: See [QUICKSTART.md](QUICKSTART.md)

## 📁 Project Structure

```
vt-dev-test/
├── QUICKSTART.md                           ← Start here!
├── README_ML_INFERENCE.md                   ← Complete documentation
├── ML_INFERENCE_SCHEMA_INTEGRATION.md       ← Architecture guide
├── ML_TAG_VALIDATION_RULES.md               ← Validation specs
│
├── setup.bat                                ← Automated setup script
├── requirements.txt                         ← Python dependencies
├── .env.example                             ← Configuration template
│
├── ml_inference_config.sql                  ← Database functions
│
└── python/
    ├── config.py                            ← Configuration loader
    ├── db_utils.py                          ← Database utilities
    ├── ml_feature_extraction.py             ← ML inference engine
    ├── test_ml_inference.py                 ← Test suite (14 tests)
    └── example_predictions.py               ← Live examples
```

## 🎓 How It Works

### 1. Your Excel is Ground Truth
```
cloud_resource_tags_complete 1.xlsx
   ↓ (excel_to_sql_converter.py)
SQL INSERT statements
   ↓ (psql load)
cloud_resource_tags table
   ↓ (SchemaValidatedInference)
Schema-validated predictions
```

###  2. Query Schema Before Predicting
```python
# Get valid tags for AWS EC2
valid_tags = query("SELECT * FROM cloud_resource_tags WHERE provider='AWS' AND scope='Compute'")

# Only predict these tags with these values
environment: ['dev', 'staging', 'prod', 'testing']
cost-center: String (any value)
instance-role: ['web-server', 'app-server', 'database', 'worker']
```

### 3. Validate Every Prediction
```python
predicted_value = "production"
allowed_values = ['dev', 'staging', 'prod', 'testing']

if predicted_value not in allowed_values:
    prediction = None  # Don't hallucinate! ✅
```

## ✨ Key Features

- **Zero Hallucination**: All predictions constrained to schema
- **Enum Validation**: Only values from `allowed_values`
- **Case Sensitivity**: AWS CamelCase, GCP lowercase, Azure case-insensitive
- **Confidence Scoring**: Category-based (Critical=high, Optional=low)
- **Smart Defaults**: Only for Critical tags
- **Complete Provenance**: Tracks reasoning for every prediction

## 📊 Examples

### Example 1: Well-Tagged Resource
```python
resource = {
    "provider": "aws",
    "resource_type": "ec2",
    "name": "prod-api-server",
    "native_tags": {"Environment": "Production", "Team": "backend"}
}

predictions = inference.predict_tags(resource)

# Result:
# ✅ environment = prod (98% - NORMALIZED from native tag)
# ✅ team = backend (98% - NORMALIZED from native tag)
# ⚠️ cost-center = production-ops (85% - DERIVED from environment)
# ⚠️ owner = backend-team@company.com (75% - DERIVED from team)
```

### Example 2: Minimal Tags (Pattern Matching)
```python
resource = {
    "provider": "aws",
    "resource_type": "ec2",
    "name": "staging-web-01",
    "native_tags": {}
}

predictions = inference.predict_tags(resource)

# Result:
# ✅ environment = staging (95% - PATTERN_MATCH from name)
# ℹ️ cost-center = engineering (65% - SMART_DEFAULT)
```

## 🧪 Testing

```powershell
# Run full test suite
cd python
python test_ml_inference.py
```

**14 test cases** covering:
- Native tag validation (4 tests)
- Pattern matching (3 tests)
- Smart defaults (3 tests)
- End-to-end inference (2 tests)
- Confidence scoring (2 tests)

## 🔧 Configuration

Edit `.env`:
```bash
# Database
DB_HOST=localhost
DB_NAME=cloudtuner_db
DB_USER=postgres
DB_PASSWORD=your_password

# ML Settings
ML_CONFIDENCE_AUTO_APPLY_THRESHOLD=0.90
ML_CONFIDENCE_REVIEW_THRESHOLD=0.70
```

## 📈 Performance

- **Schema Caching**: Tags cached in memory per (provider, scope)
- **Materialized Views**: Precomputed ML features
- **Indexed Queries**: Fast lookups on (provider, scope, category)
- **Batch Processing**: Process multiple resources efficiently

## 🛠️ Integration

### Add to Your Virtual Tagger Worker

```python
from ml_feature_extraction import SchemaValidatedInference
from db_utils import get_db_connection
from config import Config

# Initialize once
conn = get_db_connection()
inference = SchemaValidatedInference(conn)

# Process resources
for resource in resources:
    predictions = inference.predict_tags(resource)
    
    for pred in predictions:
        if pred['confidence'] >= Config.ML_CONFIDENCE_AUTO_APPLY:
            apply_to_database(resource_id, pred)
        else:
            queue_for_review(resource_id, pred)
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [QUICKSTART.md](QUICKSTART.md) | Get started in 5 minutes |
| [README_ML_INFERENCE.md](README_ML_INFERENCE.md) | Complete guide |
| [ML_INFERENCE_SCHEMA_INTEGRATION.md](ML_INFERENCE_SCHEMA_INTEGRATION.md) | Architecture & workflows |
| [ML_TAG_VALIDATION_RULES.md](ML_TAG_VALIDATION_RULES.md) | Validation specifications |

## 🔄 Updating Tags

When you update your Excel file:

```powershell
# 1. Convert to SQL
python ..\excel_to_sql_converter.py

# 2. Reload database
psql -U postgres -d cloudtuner_db -c "TRUNCATE cloud_resource_tags;"
psql -U postgres -d cloudtuner_db -f "..\cloud_resource_tags_from_excel.sql"

# 3. Refresh ML features
psql -U postgres -d cloudtuner_db -c "SELECT refresh_ml_tag_features();"

# 4. Clear cache (restart app)
```

## ✅ Production Checklist

Before deploying:

- [ ] Excel file validated (zero errors)
- [ ] All tests passing
- [ ] Database properly indexed
- [ ] Configuration set for production
- [ ] Logging configured
- [ ] Monitoring dashboards ready
- [ ] Team trained on schema maintenance

## 🆘 Support

**Issues?**
1. Check [QUICKSTART.md](QUICKSTART.md) troubleshooting section
2. Run `python test_ml_inference.py` to diagnose
3. Verify database: `SELECT COUNT(*) FROM cloud_resource_tags;`

**Questions?**
- Architecture: See `ML_INFERENCE_SCHEMA_INTEGRATION.md`
- Validation: See `ML_TAG_VALIDATION_RULES.md`
- Setup: See `QUICKSTART.md`

## 📝 License

Internal project for CloudTuner.ai Virtual Tagging System

---

**Ready to eliminate ML hallucination?** Run `.\setup.bat` and try `python python\example_predictions.py`! 🚀
