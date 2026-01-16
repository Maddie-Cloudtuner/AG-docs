"""
Convert user's Excel file to SQL for cloud_resource_tags table
Handles actual column structure from their file
"""

import pandas as pd

# Read Excel
df = pd.read_excel(r'c:\Users\LENOVO\Desktop\my_docs\AG\cloud_resource_tags_complete 1.xlsx')

print(f"Total rows in Excel: {len(df)}")
print(f"Columns: {list(df.columns)}")

# Generate CREATE TABLE
sql = []
sql.append("""
-- Create cloud_resource_tags table from Excel
CREATE TABLE IF NOT EXISTS cloud_resource_tags (
    id SERIAL PRIMARY KEY,
    cloud_provider VARCHAR(20) NOT NULL,
    resource_scope VARCHAR(50) NOT NULL,
    tag_category VARCHAR(20) NOT NULL,
    tag_key VARCHAR(255) NOT NULL,
    tag_value TEXT,
    is_case_sensitive BOOLEAN NOT NULL DEFAULT FALSE
);

-- Clear existing data
TRUNCATE cloud_resource_tags RESTART IDENTITY;

""")

# Generate INSERT statements
for idx, row in df.iterrows():
    provider = str(row['cloud_provider']).replace("'", "''")
    scope = str(row['resource_scope']).replace("'", "''")
    category = str(row['tag_category']).replace("'", "''")
    key = str(row['tag_key']).replace("'", "''")
    value = str(row['tag_value']).replace("'", "''") if pd.notna(row['tag_value']) else ''
    case_sensitive = 'TRUE' if row['is_case_sensitive'] == True or str(row['is_case_sensitive']).upper() == 'TRUE' else 'FALSE'
    
    insert = f"""INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('{provider}', '{scope}', '{category}', '{key}', '{value}', {case_sensitive});
"""
    sql.append(insert)

# Add indexes
sql.append("""
-- Create indexes
CREATE INDEX IF NOT EXISTS idx_cloud_provider ON cloud_resource_tags(cloud_provider);
CREATE INDEX IF NOT EXISTS idx_resource_scope ON cloud_resource_tags(resource_scope);
CREATE INDEX IF NOT EXISTS idx_tag_category ON cloud_resource_tags(tag_category);
CREATE INDEX IF NOT EXISTS idx_tag_key ON cloud_resource_tags(tag_key);
CREATE INDEX IF NOT EXISTS idx_composite ON cloud_resource_tags(cloud_provider, resource_scope, tag_category);
""")

# Write to file
output_file = r'c:\Users\LENOVO\Desktop\my_docs\AG\cloud_resource_tags_load.sql'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql))

print(f"\nGenerated SQL file: {output_file}")
print(f"Total INSERT statements: {len(df)}")
