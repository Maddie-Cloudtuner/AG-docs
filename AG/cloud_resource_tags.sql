-- Production-ready PostgreSQL script for cloud_resource_tags table
-- Based on AWS, Azure, and GCP Cloud Adoption Framework and FinOps standards

CREATE TABLE cloud_resource_tags (
    id SERIAL PRIMARY KEY,
    cloud_provider VARCHAR(20) NOT NULL CHECK (cloud_provider IN ('AWS', 'Azure', 'GCP', 'All')),
    resource_scope VARCHAR(50) NOT NULL,
    tag_category VARCHAR(20) NOT NULL CHECK (tag_category IN ('Critical', 'Non-Critical', 'Optional')),
    tag_key VARCHAR(255) NOT NULL,
    value_type VARCHAR(20) NOT NULL CHECK (value_type IN ('String', 'Enum', 'Date', 'Boolean')),
    allowed_values TEXT,
    is_case_sensitive BOOLEAN NOT NULL,
    description TEXT NOT NULL
);

-- Insert Critical Tags
INSERT INTO cloud_resource_tags (cloud_provider, resource_scope, tag_category, tag_key, value_type, allowed_values, is_case_sensitive, description) VALUES
('All', 'Global', 'Critical', 'Environment', 'Enum', 'dev, staging, prod, testing', TRUE, 'Deployment environment classification for resource lifecycle management and policy enforcement'),
('All', 'Global', 'Critical', 'CostCenter', 'String', NULL, FALSE, 'Financial cost center or budget code for accurate cost allocation and chargeback/showback reporting'),
('All', 'Global', 'Critical', 'Owner', 'String', NULL, FALSE, 'Individual or team responsible for the resource, critical for accountability and incident response'),
('All', 'Global', 'Critical', 'BusinessUnit', 'String', NULL, FALSE, 'Organizational division or department owning the resource for financial tracking and governance'),
('All', 'Global', 'Critical', 'Application', 'String', NULL, FALSE, 'Application or workload name the resource belongs to, essential for grouping and cost analysis'),
('AWS', 'Global', 'Critical', 'Project', 'String', NULL, TRUE, 'AWS project identifier for grouping resources by initiative or customer'),
('Azure', 'Global', 'Critical', 'CostCenter', 'String', NULL, FALSE, 'Azure cost center for financial operations and budget allocation'),
('GCP', 'Global', 'Critical', 'cost_center', 'String', NULL, TRUE, 'GCP label for cost center tracking (lowercase as per GCP standards)'),
('All', 'Database', 'Critical', 'DataClassification', 'Enum', 'public, internal, confidential, restricted', TRUE, 'Sensitivity level of data for compliance and security policy enforcement'),
('All', 'Compute', 'Critical', 'Criticality', 'Enum', 'tier1, tier2, tier3, mission-critical', FALSE, 'Business criticality level for SLA management and disaster recovery prioritization'),

-- Insert Non-Critical Tags
('All', 'Global', 'Non-Critical', 'ApplicationID', 'String', NULL, FALSE, 'Unique application identifier for tracking resources across multiple applications'),
('AWS', 'Compute', 'Non-Critical', 'InstanceRole', 'Enum', 'web-server, app-server, database, worker', TRUE, 'AWS EC2 instance role classification for operational management'),
('Azure', 'Compute', 'Non-Critical', 'ServiceClass', 'String', NULL, FALSE, 'Azure VM service classification for resource organization'),
('GCP', 'Compute', 'Non-Critical', 'instance_type', 'Enum', 'web, api, worker, data-processing', TRUE, 'GCP Compute Engine instance type label (lowercase per GCP standards)'),
('All', 'Storage', 'Non-Critical', 'DataRetention', 'String', NULL, FALSE, 'Retention policy identifier for lifecycle management and compliance'),
('AWS', 'Storage', 'Non-Critical', 'StorageClass', 'Enum', 'logs, backups, user-data, archives', TRUE, 'AWS S3 bucket data classification for lifecycle policies'),
('Azure', 'Storage', 'Non-Critical', 'DataType', 'String', NULL, FALSE, 'Azure Storage data type classification for management and access control'),
('GCP', 'Storage', 'Non-Critical', 'storage_purpose', 'Enum', 'backup, archive, analytics, logs', TRUE, 'GCP Cloud Storage bucket purpose label (lowercase per GCP standards)'),
('All', 'Database', 'Non-Critical', 'Version', 'String', NULL, FALSE, 'Database version or schema version for change tracking'),
('AWS', 'Database', 'Non-Critical', 'DatabaseEngine', 'Enum', 'postgres, mysql, oracle, sqlserver', FALSE, 'AWS RDS database engine identifier'),
('Azure', 'Database', 'Non-Critical', 'SQLType', 'String', NULL, FALSE, 'Azure SQL database type classification'),
('GCP', 'Database', 'Non-Critical', 'db_engine', 'Enum', 'postgresql, mysql, sqlserver', TRUE, 'GCP Cloud SQL database engine label (lowercase per GCP standards)'),
('All', 'Network', 'Non-Critical', 'NetworkZone', 'Enum', 'dmz, internal, external, trusted', FALSE, 'Network security zone classification for access control'),
('AWS', 'Network', 'Non-Critical', 'VPCName', 'String', NULL, TRUE, 'AWS VPC identifier for network resource grouping'),
('Azure', 'Network', 'Non-Critical', 'VNetName', 'String', NULL, FALSE, 'Azure Virtual Network name for resource organization'),
('GCP', 'Network', 'Non-Critical', 'vpc_name', 'String', NULL, TRUE, 'GCP VPC network name label (lowercase per GCP standards)'),

-- Insert Optional Tags
('All', 'Global', 'Optional', 'CreatedDate', 'Date', NULL, FALSE, 'Resource creation timestamp for age-based analysis and lifecycle management'),
('All', 'Global', 'Optional', 'CreatedBy', 'String', NULL, FALSE, 'User or service principal that created the resource for audit trails'),
('All', 'Compute', 'Optional', 'AutoShutdown', 'Boolean', NULL, FALSE, 'Flag indicating if resource should be automatically shut down during off-hours'),
('All', 'Compute', 'Optional', 'BackupEnabled', 'Boolean', NULL, FALSE, 'Indicates whether backup is enabled for the resource'),
('AWS', 'Compute', 'Optional', 'AutoScaling', 'Boolean', NULL, FALSE, 'AWS EC2 auto-scaling enablement flag for capacity management'),
('Azure', 'Compute', 'Optional', 'AutoStart', 'Boolean', NULL, FALSE, 'Azure VM automatic start schedule flag for cost optimization'),
('GCP', 'Compute', 'Optional', 'auto_shutdown_schedule', 'String', NULL, TRUE, 'GCP Compute Engine shutdown schedule label (lowercase per GCP standards)'),
('All', 'Storage', 'Optional', 'ExpiryDate', 'Date', NULL, FALSE, 'Temporary resource expiration date for automated cleanup'),
('All', 'Database', 'Optional', 'ComplianceScope', 'Enum', 'gdpr, hipaa, pci-dss, sox, none', FALSE, 'Regulatory compliance scope for the database resource'),
('AWS', 'Network', 'Optional', 'Monitoring', 'Boolean', NULL, FALSE, 'AWS CloudWatch monitoring enablement flag'),
('Azure', 'Network', 'Optional', 'LogAnalytics', 'Boolean', NULL, FALSE, 'Azure Monitor Log Analytics enablement for network resources'),
('GCP', 'Network', 'Optional', 'monitoring_enabled', 'Boolean', NULL, TRUE, 'GCP Cloud Monitoring flag (lowercase per GCP standards)');

-- Create indexes for performance optimization
CREATE INDEX idx_cloud_provider ON cloud_resource_tags(cloud_provider);
CREATE INDEX idx_resource_scope ON cloud_resource_tags(resource_scope);
CREATE INDEX idx_tag_category ON cloud_resource_tags(tag_category);
CREATE INDEX idx_tag_key ON cloud_resource_tags(tag_key);
