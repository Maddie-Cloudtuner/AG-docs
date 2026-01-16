"""
Excel to SQL Converter for cloud_resource_tags
Converts the Excel file to SQL INSERT statements
"""

import pandas as pd
import sys

def excel_to_sql(excel_file_path, output_sql_path):
    """
    Convert Excel file to SQL INSERT statements for cloud_resource_tags table
    
    Args:
        excel_file_path: Path to the Excel file
        output_sql_path: Path where SQL file will be saved
    """
    
    # Read Excel file
    print(f"Reading Excel file: {excel_file_path}")
    df = pd.read_excel(excel_file_path)
    
    # Expected columns
    expected_columns = [
        'cloud_provider', 'resource_scope', 'tag_category', 'tag_key',
        'value_type', 'allowed_values', 'is_case_sensitive', 'description'
    ]
    
    # Validate columns
    missing_cols = set(expected_columns) - set(df.columns)
    if missing_cols:
        print(f"WARNING: Missing columns: {missing_cols}")
        print(f"Available columns: {list(df.columns)}")
        return False
    
    # Generate SQL
    sql_statements = []
    sql_statements.append("-- Generated SQL INSERT statements from Excel\n")
    sql_statements.append("-- File: cloud_resource_tags_complete 1.xlsx\n")
    sql_statements.append(f"-- Total rows: {len(df)}\n\n")
    
    # Group by tag_category for better organization
    for category in ['Critical', 'Non-Critical', 'Optional']:
        category_df = df[df['tag_category'] == category]
        if len(category_df) > 0:
            sql_statements.append(f"-- {category} Tags ({len(category_df)} entries)\n")
            
            for idx, row in category_df.iterrows():
                # Handle NULL values
                allowed_values = f"'{row['allowed_values']}'" if pd.notna(row['allowed_values']) else 'NULL'
                is_case_sensitive = 'TRUE' if row['is_case_sensitive'] == True or row['is_case_sensitive'] == 'TRUE' else 'FALSE'
                
                # Escape single quotes in description
                description = str(row['description']).replace("'", "''")
                
                sql = f"""INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, value_type, allowed_values, is_case_sensitive, description) VALUES
('{row['cloud_provider']}', '{row['resource_scope']}', '{row['tag_category']}', '{row['tag_key']}', '{row['value_type']}', {allowed_values}, {is_case_sensitive}, '{description}');\n"""
                
                sql_statements.append(sql)
            
            sql_statements.append("\n")
    
    # Write to file
    with open(output_sql_path, 'w', encoding='utf-8') as f:
        f.writelines(sql_statements)
    
    print(f"\n✓ Successfully converted {len(df)} rows to SQL")
    print(f"✓ Output saved to: {output_sql_path}")
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Total tags: {len(df)}")
    print(f"Critical: {len(df[df['tag_category'] == 'Critical'])}")
    print(f"Non-Critical: {len(df[df['tag_category'] == 'Non-Critical'])}")
    print(f"Optional: {len(df[df['tag_category'] == 'Optional'])}")
    print("\nBy Cloud Provider:")
    print(df['cloud_provider'].value_counts().to_string())
    print("\nBy Resource Scope:")
    print(df['resource_scope'].value_counts().to_string())
    
    return True

def validate_excel_structure(excel_file_path):
    """
    Validate the Excel file structure matches requirements
    """
    print("=== Validating Excel Structure ===\n")
    
    df = pd.read_excel(excel_file_path)
    issues = []
    
    # Check 1: Environment tag validation
    env_tags = df[df['tag_key'] == 'Environment']
    if len(env_tags) == 0:
        issues.append("❌ CRITICAL: Environment tag not found")
    else:
        env_tag = env_tags.iloc[0]
        if env_tag['tag_category'] != 'Critical':
            issues.append(f"❌ Environment tag category should be 'Critical', got '{env_tag['tag_category']}'")
        if env_tag['allowed_values'] != 'dev, staging, prod, testing':
            issues.append(f"❌ Environment allowed_values should be 'dev, staging, prod, testing', got '{env_tag['allowed_values']}'")
        if env_tag['is_case_sensitive'] != True and env_tag['is_case_sensitive'] != 'TRUE':
            issues.append(f"❌ Environment is_case_sensitive should be TRUE, got '{env_tag['is_case_sensitive']}'")
    
    # Check 2: Minimum 20 unique tags
    unique_tags = df['tag_key'].nunique()
    if unique_tags < 20:
        issues.append(f"⚠️  WARNING: Only {unique_tags} unique tags found, requirement is at least 20")
    else:
        print(f"✓ Found {unique_tags} unique tags (requirement: >= 20)")
    
    # Check 3: Cloud provider validation
    valid_providers = ['AWS', 'Azure', 'GCP', 'All']
    invalid_providers = df[~df['cloud_provider'].isin(valid_providers)]
    if len(invalid_providers) > 0:
        issues.append(f"❌ Invalid cloud_provider values found: {invalid_providers['cloud_provider'].unique()}")
    else:
        print("✓ All cloud_provider values are valid")
    
    # Check 4: Tag category validation
    valid_categories = ['Critical', 'Non-Critical', 'Optional']
    invalid_categories = df[~df['tag_category'].isin(valid_categories)]
    if len(invalid_categories) > 0:
        issues.append(f"❌ Invalid tag_category values: {invalid_categories['tag_category'].unique()}")
    else:
        print("✓ All tag_category values are valid")
    
    # Check 5: Value type validation
    valid_types = ['String', 'Enum', 'Date', 'Boolean']
    invalid_types = df[~df['value_type'].isin(valid_types)]
    if len(invalid_types) > 0:
        issues.append(f"❌ Invalid value_type values: {invalid_types['value_type'].unique()}")
    else:
        print("✓ All value_type values are valid")
    
    # Check 6: Resource scope coverage
    scopes = df['resource_scope'].unique()
    required_scopes = ['Global', 'Compute', 'Database', 'Storage', 'Network']
    missing_scopes = set(required_scopes) - set(scopes)
    if missing_scopes:
        issues.append(f"⚠️  WARNING: Missing resource scopes: {missing_scopes}")
    else:
        print(f"✓ All required resource scopes covered: {list(scopes)}")
    
    # Print results
    print("\n=== Validation Results ===")
    if len(issues) == 0:
        print("✓✓✓ All validations passed! ✓✓✓")
        return True
    else:
        print(f"\nFound {len(issues)} issue(s):\n")
        for issue in issues:
            print(issue)
        return False

if __name__ == "__main__":
    excel_file = r"c:\Users\LENOVO\Desktop\my_docs\AG\cloud_resource_tags_complete 1.xlsx"
    output_sql = r"c:\Users\LENOVO\Desktop\my_docs\AG\cloud_resource_tags_from_excel.sql"
    
    # First validate
    is_valid = validate_excel_structure(excel_file)
    
    print("\n" + "="*50 + "\n")
    
    # Then convert
    if is_valid or input("\nValidation had issues. Continue with conversion? (y/n): ").lower() == 'y':
        excel_to_sql(excel_file, output_sql)
    else:
        print("Conversion cancelled.")
