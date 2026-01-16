# Excel File Validation Checklist
## cloud_resource_tags_complete 1.xlsx

Use this checklist to manually validate your Excel file before converting to SQL.

---

## ✅ Required Column Headers (in exact order)

Your Excel should have these 8 columns:

1. **cloud_provider** - Values: AWS, Azure, GCP, or All
2. **resource_scope** - Values: Global, Compute, Database, Storage, Network
3. **tag_category** - Values: Critical, Non-Critical, Optional
4. **tag_key** - The tag name (e.g., Environment, CostCenter)
5. **value_type** - Values: String, Enum, Date, Boolean
6. **allowed_values** - Comma-separated list for Enum type, blank for others
7. **is_case_sensitive** - Values: TRUE or FALSE
8. **description** - Text description of the tag

---

## ✅ Critical Validation Checks

### 1. Environment Tag (REQUIRED)
- [ ] **tag_key** = "Environment" exists
- [ ] **tag_category** = "Critical"
- [ ] **allowed_values** = "dev, staging, prod, testing" (exact match)
- [ ] **is_case_sensitive** = TRUE
- [ ] **cloud_provider** = "All"
- [ ] **resource_scope** = "Global"

### 2. Minimum Tag Count
- [ ] At least **20 unique tag_key** values (as per requirements)
- [ ] Recommended: 30-40 tags for comprehensive coverage

### 3. Tag Category Distribution
- [ ] **Critical tags**: 8-12 entries (environment, cost-center, owner, business-unit, etc.)
- [ ] **Non-Critical tags**: 12-18 entries (team, application-id, version, etc.)
- [ ] **Optional tags**: 8-15 entries (created-date, backup-enabled, expiry-date, etc.)

### 4. Resource Scope Coverage
Must have tags for ALL these scopes:
- [ ] **Global** - Tags applicable to all resources
- [ ] **Compute** - EC2, VMs, Compute Engine
- [ ] **Database** - RDS, SQL, Cloud SQL
- [ ] **Storage** - S3, Blob Storage, GCS
- [ ] **Network** - VPC, VNet, Firewall rules

### 5. Cloud Provider Coverage
- [ ] **All** - Universal tags (environment, cost-center, owner)
- [ ] **AWS** - AWS-specific tags with CamelCase/mixed case
- [ ] **Azure** - Azure-specific tags (case-insensitive)
- [ ] **GCP** - GCP-specific tags (all lowercase with underscores)

### 6. Value Type Validation
For each row:
- [ ] If **value_type** = "Enum", then **allowed_values** must NOT be blank
- [ ] If **value_type** = "String", "Date", or "Boolean", then **allowed_values** should be blank (NULL)

### 7. Case Sensitivity Rules
- [ ] AWS tags: Mix of TRUE and FALSE (depends on tag)
- [ ] Azure tags: Mostly FALSE (case-insensitive)
- [ ] GCP tags: All TRUE (case-sensitive, lowercase only)
- [ ] Critical tags like Environment: TRUE

---

## 📋 Sample Row Examples

### Critical Tag Example:
| cloud_provider | resource_scope | tag_category | tag_key | value_type | allowed_values | is_case_sensitive | description |
|---|---|---|---|---|---|---|---|
| All | Global | Critical | Environment | Enum | dev, staging, prod, testing | TRUE | Deployment environment classification for resource lifecycle management |

### Non-Critical Tag Example:
| cloud_provider | resource_scope | tag_category | tag_key | value_type | allowed_values | is_case_sensitive | description |
|---|---|---|---|---|---|---|---|
| AWS | Compute | Non-Critical | InstanceRole | Enum | web-server, app-server, database, worker | TRUE | AWS EC2 instance role classification |

### Optional Tag Example:
| cloud_provider | resource_scope | tag_category | tag_key | value_type | allowed_values | is_case_sensitive | description |
|---|---|---|---|---|---|---|---|
| All | Compute | Optional | AutoShutdown | Boolean | | FALSE | Flag indicating if resource should be automatically shut down during off-hours |

---

## 🔍 Common Issues to Check

### Data Quality Issues:
- [ ] No blank rows in the middle of data
- [ ] No duplicate tag_key + cloud_provider + resource_scope combinations
- [ ] All descriptions are meaningful (not just "tag description")
- [ ] Proper spelling in allowed_values (no typos like "prodction")

### Formatting Issues:
- [ ] Boolean values are TRUE/FALSE (not Yes/No or 1/0)
- [ ] Enum allowed_values use comma-space separation: "value1, value2, value3"
- [ ] No leading/trailing spaces in tag_key names
- [ ] Consistent use of hyphen vs underscore in tag names

### Cloud-Specific Issues:
- [ ] GCP tags are all lowercase with underscores (e.g., `cost_center` not `CostCenter`)
- [ ] AWS tags follow their conventions (CamelCase or hyphen-separated)
- [ ] Azure tags are descriptive (can be any case)

---

## 🚀 Next Steps After Validation

Once you've verified all checkboxes above:

1. **Install pandas** (if not already):
   ```powershell
   pip install pandas openpyxl
   ```

2. **Run the converter**:
   ```powershell
   python c:\Users\LENOVO\Desktop\my_docs\AG\excel_to_sql_converter.py
   ```

3. **Review the generated SQL**:
   - File will be created at: `c:\Users\LENOVO\Desktop\my_docs\AG\cloud_resource_tags_from_excel.sql`
   - Manually review the INSERT statements
   - Compare with the original `cloud_resource_tags.sql` I created

4. **Execute the SQL**:
   ```sql
   -- In PostgreSQL
   \i 'c:/Users/LENOVO/Desktop/my_docs/AG/cloud_resource_tags_from_excel.sql'
   ```

---

## 📊 Expected Summary Stats

After conversion, you should see output like:

```
Total tags: 35-45
Critical: 10-12
Non-Critical: 15-20
Optional: 10-15

By Cloud Provider:
All       15-20
AWS       8-12
Azure     5-8
GCP       5-8

By Resource Scope:
Global    12-18
Compute   8-12
Database  6-10
Storage   6-10
Network   3-6
```

---

## ❓ Questions to Ask Yourself

1. **Completeness**: Does this cover all critical tags my organization needs for cost allocation?
2. **Accuracy**: Are the allowed values realistic for my cloud environment?
3. **Consistency**: Do the tag naming conventions match my existing standards?
4. **ML Usability**: Will ML models be able to validate predictions against these enums?
5. **Extensibility**: Can I easily add new tags later without breaking the schema?

---

## 🆘 If You Find Issues

If validation fails:
1. Fix the issues in the Excel file
2. Re-run the validation
3. Don't proceed to SQL conversion until all checks pass

**Contact me** if you need help with:
- Specific tag recommendations
- Cloud provider best practices
- ML inference integration questions
