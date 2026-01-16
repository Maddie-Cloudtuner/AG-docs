
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


INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Environment', 'dev', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Environment', 'staging', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Environment', 'prod', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Environment', 'testing', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Owner', 'engineering@company.com', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Owner', 'devops@company.com', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Owner', 'platform@company.com', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Owner', 'infrastructure@company.com', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'CostCenter', 'IT-001', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'CostCenter', 'IT-002', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'CostCenter', 'ENG-001', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'CostCenter', 'OPS-001', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'CostCenter', 'INFRA-001', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Application', 'web-api', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Application', 'data-pipeline', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Application', 'ml-model', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Application', 'monitoring', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Application', 'auth-service', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Department', 'Engineering', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Department', 'DevOps', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Department', 'DataScience', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Department', 'Infrastructure', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Critical', 'Department', 'Security', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'Project', 'CustomerPortal', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'Project', 'DataPlatform', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'Project', 'MLOps', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'Project', 'InternalTools', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'Project', 'Migration', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'Team', 'Team1', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'Team', 'Team2', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'Team', 'Team3', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'Team', 'Platform', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'Team', 'SRE', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'DataClassification', 'public', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'DataClassification', 'internal', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'DataClassification', 'confidential', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Non-Critical', 'DataClassification', 'restricted', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'Version', 'v1.0', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'Version', 'v1.1', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'Version', 'v2.0', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'Version', 'beta', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'Version', 'alpha', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'ManagedBy', 'terraform', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'ManagedBy', 'cloudformation', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'ManagedBy', 'manual', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'ManagedBy', 'ansible', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'ManagedBy', 'automation', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'CreatedDate', '2025-01-01 00:00:00', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'CreatedDate', '2025-03-15 00:00:00', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'CreatedDate', '2025-06-20 00:00:00', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'CreatedDate', '2025-09-10 00:00:00', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'CreatedDate', '2025-12-01 00:00:00', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'ExpiryDate', '2026-01-01 00:00:00', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'ExpiryDate', '2026-06-01 00:00:00', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'ExpiryDate', '2027-01-01 00:00:00', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'ExpiryDate', 'never', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('All', 'Global', 'Optional', 'ExpiryDate', 'temporary', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Critical', 'Name', 'web-server-01', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Critical', 'Name', 'api-gateway-01', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Critical', 'Name', 'lambda-processor', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Critical', 'Name', 'batch-worker-01', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Critical', 'Name', 'compute-01', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Critical', 'BackupRequired', 'True', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Critical', 'BackupRequired', 'False', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Non-Critical', 'InstanceType', 't3.medium', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Non-Critical', 'InstanceType', 't3.large', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Non-Critical', 'InstanceType', 'm5.xlarge', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Non-Critical', 'InstanceType', 'c5.2xlarge', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Non-Critical', 'InstanceType', 'r5.large', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Non-Critical', 'LaunchTemplate', 'default-template', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Non-Critical', 'LaunchTemplate', 'high-memory-template', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Non-Critical', 'LaunchTemplate', 'compute-optimized', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Non-Critical', 'LaunchTemplate', 'gpu-template', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Non-Critical', 'LaunchTemplate', 'baseline', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Optional', 'AutoShutdown', 'True', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Optional', 'AutoShutdown', 'False', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Optional', 'AutoShutdown', '22:00:00', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Optional', 'AutoShutdown', '23:30:00', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Optional', 'SLA', '99.9', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Optional', 'SLA', '99.99', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Optional', 'SLA', '99.999', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Optional', 'SLA', 'best-effort', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Compute', 'Optional', 'SLA', 'none', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Critical', 'BackupRequired', 'True', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Critical', 'BackupRequired', 'False', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Critical', 'Compliance', 'HIPAA', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Critical', 'Compliance', 'PCI-DSS', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Critical', 'Compliance', 'SOC2', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Critical', 'Compliance', 'GDPR', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Critical', 'Compliance', 'none', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Non-Critical', 'EngineType', 'postgres', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Non-Critical', 'EngineType', 'mysql', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Non-Critical', 'EngineType', 'mariadb', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Non-Critical', 'EngineType', 'oracle', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Non-Critical', 'EngineType', 'mssql', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Optional', 'RetentionDays', '7', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Optional', 'RetentionDays', '14', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Optional', 'RetentionDays', '30', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Optional', 'RetentionDays', '60', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Optional', 'RetentionDays', '90', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Optional', 'MultiAZ', 'True', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Database', 'Optional', 'MultiAZ', 'False', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Critical', 'DataClassification', 'public', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Critical', 'DataClassification', 'internal', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Critical', 'DataClassification', 'confidential', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Critical', 'DataClassification', 'restricted', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Non-Critical', 'ArchiveAfterDays', '30', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Non-Critical', 'ArchiveAfterDays', '60', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Non-Critical', 'ArchiveAfterDays', '90', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Non-Critical', 'ArchiveAfterDays', '180', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Non-Critical', 'ArchiveAfterDays', 'never', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Non-Critical', 'StorageClass', 'standard', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Non-Critical', 'StorageClass', 'ia', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Non-Critical', 'StorageClass', 'glacier', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Non-Critical', 'StorageClass', 'glacier-deep', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Non-Critical', 'StorageClass', 'intelligent-tiering', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Optional', 'Versioning', 'enabled', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Optional', 'Versioning', 'disabled', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Storage', 'Optional', 'Versioning', 'suspended', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Network', 'Critical', 'SecurityGroup', 'sg-internal', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Network', 'Critical', 'SecurityGroup', 'sg-external', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Network', 'Critical', 'SecurityGroup', 'sg-database', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Network', 'Critical', 'SecurityGroup', 'sg-lambda', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Network', 'Critical', 'SecurityGroup', 'sg-default', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Network', 'Critical', 'NetworkTier', 'public', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Network', 'Critical', 'NetworkTier', 'private', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Network', 'Critical', 'NetworkTier', 'protected', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Network', 'Critical', 'NetworkTier', 'isolated', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Network', 'Optional', 'NatGateway', 'required', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Network', 'Optional', 'NatGateway', 'optional', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('AWS', 'Network', 'Optional', 'NatGateway', 'none', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Critical', 'vm-size-category', 'small', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Critical', 'vm-size-category', 'medium', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Critical', 'vm-size-category', 'large', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Critical', 'vm-size-category', 'xlarge', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Critical', 'vm-size-category', 'xxlarge', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Critical', 'ComputeType', 'vm', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Critical', 'ComputeType', 'vmss', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Critical', 'ComputeType', 'container-instance', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Critical', 'ComputeType', 'app-service', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Non-Critical', 'patch-group', 'patch-group-1', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Non-Critical', 'patch-group', 'patch-group-2', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Non-Critical', 'patch-group', 'patch-group-3', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Non-Critical', 'patch-group', 'critical', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Non-Critical', 'patch-group', 'standard', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Optional', 'AutoshutdownSchedule', 'daily-22:00', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Optional', 'AutoshutdownSchedule', 'daily-23:30', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Optional', 'AutoshutdownSchedule', 'weekdays-20:00', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Compute', 'Optional', 'AutoshutdownSchedule', 'disabled', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Critical', 'data-tier', 'basic', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Critical', 'data-tier', 'standard', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Critical', 'data-tier', 'premium', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Critical', 'data-tier', 'hyperscale', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Critical', 'DatabaseType', 'sql-server', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Critical', 'DatabaseType', 'mysql', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Critical', 'DatabaseType', 'postgresql', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Critical', 'DatabaseType', 'cosmosdb', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Critical', 'DatabaseType', 'mariadb', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Non-Critical', 'backup-retention', '7', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Non-Critical', 'backup-retention', '14', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Non-Critical', 'backup-retention', '30', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Non-Critical', 'backup-retention', '60', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Database', 'Non-Critical', 'backup-retention', '90', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Storage', 'Critical', 'StorageAccountType', 'standard-lrs', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Storage', 'Critical', 'StorageAccountType', 'standard-grs', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Storage', 'Critical', 'StorageAccountType', 'premium-lrs', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Storage', 'Critical', 'StorageAccountType', 'premium-zrs', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Storage', 'Non-Critical', 'blob-tier', 'hot', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Storage', 'Non-Critical', 'blob-tier', 'cool', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Storage', 'Non-Critical', 'blob-tier', 'archive', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Storage', 'Non-Critical', 'blob-tier', 'cold', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Storage', 'Optional', 'RedundancyLevel', 'local', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Storage', 'Optional', 'RedundancyLevel', 'geo', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Storage', 'Optional', 'RedundancyLevel', 'zone', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Storage', 'Optional', 'RedundancyLevel', 'geo-zone', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Network', 'Critical', 'network-policy', 'restrictive', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Network', 'Critical', 'network-policy', 'moderate', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Network', 'Critical', 'network-policy', 'permissive', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Network', 'Critical', 'network-policy', 'zero-trust', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Network', 'Non-Critical', 'NetworkSecurityLevel', 'public', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Network', 'Non-Critical', 'NetworkSecurityLevel', 'internal', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Network', 'Non-Critical', 'NetworkSecurityLevel', 'private', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('Azure', 'Network', 'Non-Critical', 'NetworkSecurityLevel', 'isolated', FALSE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Critical', 'machine-type', 'e2-medium', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Critical', 'machine-type', 'e2-standard-2', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Critical', 'machine-type', 'n1-standard-4', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Critical', 'machine-type', 'n2-standard-8', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Critical', 'machine-type', 'c2-standard-16', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Critical', 'compute-tier', 'standard', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Critical', 'compute-tier', 'performance', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Critical', 'compute-tier', 'custom', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Critical', 'compute-tier', 'gpu-enabled', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Critical', 'compute-tier', 'memory-optimized', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Optional', 'preemptible', 'True', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Optional', 'preemptible', 'False', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Optional', 'image-family', 'debian-11', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Optional', 'image-family', 'debian-12', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Optional', 'image-family', 'ubuntu-20.04', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Optional', 'image-family', 'ubuntu-22.04', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Compute', 'Optional', 'image-family', 'windows-2022', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Database', 'Critical', 'replication-type', 'regional', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Database', 'Critical', 'replication-type', 'zonal', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Database', 'Critical', 'replication-type', 'multi-region', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Database', 'Critical', 'replication-type', 'cross-region', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Database', 'Critical', 'database-engine', 'cloudsql-mysql', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Database', 'Critical', 'database-engine', 'cloudsql-postgres', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Database', 'Critical', 'database-engine', 'cloudsql-sqlserver', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Database', 'Critical', 'database-engine', 'firestore', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Database', 'Critical', 'database-engine', 'bigtable', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Database', 'Non-Critical', 'backup-enabled', 'True', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Database', 'Non-Critical', 'backup-enabled', 'False', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Storage', 'Critical', 'bucket-class', 'standard', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Storage', 'Critical', 'bucket-class', 'nearline', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Storage', 'Critical', 'bucket-class', 'coldline', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Storage', 'Critical', 'bucket-class', 'archive', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Storage', 'Non-Critical', 'storage-tier', 'hot', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Storage', 'Non-Critical', 'storage-tier', 'warm', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Storage', 'Non-Critical', 'storage-tier', 'cold', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Storage', 'Non-Critical', 'storage-tier', 'frozen', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Storage', 'Optional', 'versioning-enabled', 'True', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Storage', 'Optional', 'versioning-enabled', 'False', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Network', 'Critical', 'network-tier', 'premium', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Network', 'Critical', 'network-tier', 'standard', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Network', 'Non-Critical', 'firewall-rule-type', 'allow', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Network', 'Non-Critical', 'firewall-rule-type', 'deny', TRUE);

INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, tag_value, is_case_sensitive)
VALUES ('GCP', 'Network', 'Non-Critical', 'firewall-rule-type', 'logging-only', TRUE);


-- Create indexes
CREATE INDEX IF NOT EXISTS idx_cloud_provider ON cloud_resource_tags(cloud_provider);
CREATE INDEX IF NOT EXISTS idx_resource_scope ON cloud_resource_tags(resource_scope);
CREATE INDEX IF NOT EXISTS idx_tag_category ON cloud_resource_tags(tag_category);
CREATE INDEX IF NOT EXISTS idx_tag_key ON cloud_resource_tags(tag_key);
CREATE INDEX IF NOT EXISTS idx_composite ON cloud_resource_tags(cloud_provider, resource_scope, tag_category);
