"""
Native Tag to Schema Mapping - 1:1 Mapping Configuration
=========================================================
Maps native tag keys to schema tag keys and values.
"""

# Native Tag Key → Schema Tag Key (1:1 Mapping)
NATIVE_KEY_TO_SCHEMA_KEY = {
    # Environment mappings
    'Env': 'Environment',
    'STAGE': 'Environment', 
    'PROD': 'Environment',
    'PRODUCTION': 'Environment',
    'TEST': 'Environment',
    'env': 'Environment',
    'environment': 'Environment',
    
    # Project/Application  
    'Project': 'Project',
    'Project Owner': 'Owner',
    'user:Application': 'Application',
    'Purpose': 'Application',
    
    # Ownership
    'CreatedBy': 'Owner',
    'Owner': 'Owner',
    'owner': 'Owner',
    
    # Infrastructure
    'name': 'Name',
    'Name': 'Name',
    'RetentionDays': 'RetentionDays',
    'CloudTuner': 'ManagedBy',
    
    # Kubernetes
    'KubernetesCluster': 'Application',
    'eks:cluster-name': 'Application',
    'aws:eks:cluster-name': 'Application',
    
    # Stack/Deployment
    'user:Stack': 'Application',
    'deployment': 'Application',
    'aws:cloudformation:stack-name': 'Application',
}

# Native Value → Schema Value (Normalization)
VALUE_NORMALIZATIONS = {
    # Environment values
    'prod': 'prod',
    'production': 'prod',
    'PROD': 'prod',
    'PRODUCTION': 'prod',
    'prd': 'prod',
    
    'dev': 'dev',
    'development': 'dev',
    'DEV': 'dev',
    
    'staging': 'staging',
    'stag': 'staging',
    'stage': 'staging',
    'STAGE': 'staging',
    'STG': 'staging',
    
    'test': 'testing',
    'testing': 'testing',
    'TEST': 'testing',
    'qa': 'testing',
    'QA': 'testing',
}

# All Resource Types from your data → Default Tags
RESOURCE_TYPE_DEFAULTS = {
    'AWS Systems Manager': {'Department': 'DevOps', 'ManagedBy': 'aws-ssm', 'Application': 'monitoring'},
    'IP Address': {'Department': 'DevOps', 'NetworkTier': 'standard'},
    'Volume': {'Department': 'Engineering', 'BackupRequired': 'true'},
    'Instance': {'Department': 'Engineering', 'BackupRequired': 'true', 'ManagedBy': 'compute'},
    'Serverless': {'Department': 'Engineering', 'Application': 'serverless'},
    'Snapshot': {'Department': 'DevOps', 'BackupRequired': 'archive'},
    'Bucket': {'Department': 'Engineering', 'StorageClass': 'standard'},
    'India GST': {'Department': 'Finance', 'DataClassification': 'financial'},
    'Storage Snapshot': {'Department': 'DevOps', 'BackupRequired': 'archive'},
    'Vertex AI': {'Department': 'Data', 'Application': 'ml-model'},
    'Data Transfer': {'Department': 'Engineering'},
    'Load Balancer': {'Department': 'DevOps', 'NetworkTier': 'public'},
    'DNS Query': {'Department': 'DevOps'},
    'DNS Zone': {'Department': 'DevOps'},
    'NAT Gateway': {'Department': 'DevOps', 'NetworkTier': 'internal'},
    'Compute Engine': {'Department': 'Engineering', 'ManagedBy': 'compute'},
    'Cloud Logging': {'Department': 'DevOps', 'Application': 'monitoring'},
    'Cloud Monitoring': {'Department': 'DevOps', 'Application': 'monitoring'},
    'BigQuery': {'Department': 'Data', 'Application': 'data-pipeline'},
    'EC2 Container Registry': {'Department': 'DevOps', 'Application': 'containers'},
    'API Request': {'Department': 'Engineering', 'Application': 'web-api'},
    'API Calls': {'Department': 'Engineering', 'Application': 'web-api'},
    'ACM': {'Department': 'DevOps', 'Application': 'security'},
    'AmazonLocationService': {'Department': 'Engineering', 'Application': 'location-services'},
    'APS3-Resource-Operation-Count': {'Department': 'Engineering'},
    'USE1-Resource-Operation-Count': {'Department': 'Engineering'},
    'Management Tools - AWS CloudTrail Free Events Recorded': {'Department': 'DevOps', 'Compliance': 'audit'},
    'Data Payload': {'Department': 'Engineering'},
    'AWS Glue': {'Department': 'Data', 'Application': 'data-pipeline'},
    'AWS Backup Storage': {'Department': 'DevOps', 'BackupRequired': 'true'},
    'Rekognition Image API': {'Department': 'Data', 'Application': 'ml-model'},
    'Compute': {'Department': 'Engineering', 'ManagedBy': 'compute'},
    'Lightsail Networking': {'Department': 'Engineering'},
    'Lightsail Instance': {'Department': 'Engineering'},
    'Secret': {'Department': 'DevOps', 'Application': 'security'},
    'Networking': {'Department': 'DevOps'},
    'AWS Amplify': {'Department': 'Engineering', 'Application': 'web-api'},
    'reCAPTCHA Enterprise': {'Department': 'Engineering', 'Application': 'security'},
    'Route53-Domains': {'Department': 'DevOps'},
    'Tax': {'Department': 'Finance'},
    'Provisioned IOPS': {'Department': 'Engineering'},
    'Cloud Video Intelligence API': {'Department': 'Data', 'Application': 'ml-model'},
    'Amazon DynamoDB On-Demand Backup Storage': {'Department': 'Engineering', 'BackupRequired': 'true'},
    'Storage': {'Department': 'Engineering'},
    'Sending Email': {'Department': 'Engineering'},
    'Enterprise Applications': {'Department': 'Engineering'},
    'Cloud Document AI API': {'Department': 'Data', 'Application': 'ml-model'},
    'Developer Tools': {'Department': 'Engineering'},
}

# All Service Names from your data → Default Tags
SERVICE_DEFAULTS = {
    'AWSSystemsManager': {'Department': 'DevOps', 'ManagedBy': 'aws-ssm'},
    'AmazonEC2': {'Department': 'Engineering'},
    'AmazonVPC': {'Department': 'DevOps'},
    'AWSLambda': {'Department': 'Engineering', 'Application': 'serverless'},
    'AmazonS3': {'Department': 'Engineering'},
    'AWSCloudFormation': {'Department': 'DevOps', 'ManagedBy': 'iac'},
    'AmazonCloudWatch': {'Department': 'DevOps', 'Application': 'monitoring'},
    'Vertex AI': {'Department': 'Data', 'Application': 'ml-model'},
    'awskms': {'Department': 'DevOps', 'Application': 'security'},
    'AmazonApiGateway': {'Department': 'Engineering', 'Application': 'web-api'},
    'AmazonSNS': {'Department': 'Engineering', 'Application': 'messaging'},
    'AWSSecretsManager': {'Department': 'DevOps', 'Application': 'security'},
    'AWSQueueService': {'Department': 'Engineering', 'Application': 'messaging'},
    'AWSELB': {'Department': 'DevOps', 'NetworkTier': 'public'},
    'AmazonRoute53': {'Department': 'DevOps', 'Application': 'dns'},
    'Compute Engine': {'Department': 'Engineering'},
    'AmazonLocationService': {'Department': 'Engineering', 'Application': 'location-services'},
    'AWSCloudTrail': {'Department': 'DevOps', 'Application': 'monitoring', 'Compliance': 'audit'},
    'AWS': {'Department': 'Engineering'},
    'AmazonLightsail': {'Department': 'Engineering'},
    'AWSGlue': {'Department': 'Data', 'Application': 'data-pipeline'},
    'AmazonECR': {'Department': 'DevOps', 'Application': 'containers'},
    'Cloud Logging': {'Department': 'DevOps', 'Application': 'monitoring'},
    'AmazonSageMaker': {'Department': 'Data', 'Application': 'ml-model'},
    'Cloud Monitoring': {'Department': 'DevOps', 'Application': 'monitoring'},
    'AmazonRDS': {'Department': 'Engineering', 'BackupRequired': 'true'},
    'AWSBackup': {'Department': 'DevOps', 'BackupRequired': 'true'},
    'AmazonRekognition': {'Department': 'Data', 'Application': 'ml-model'},
    'AmazonEKS': {'Department': 'DevOps', 'ManagedBy': 'kubernetes'},
    'AWSTransfer': {'Department': 'Engineering'},
    'AmazonDynamoDB': {'Department': 'Engineering'},
    'AWSEvents': {'Department': 'Engineering'},
    'AmazonSES': {'Department': 'Engineering'},
    'AmazonEFS': {'Department': 'Engineering'},
    # Add more as needed
}

# Region → DataCenter mapping
REGION_DEFAULTS = {
    'ap-south-1': 'India-Mumbai',
    'ap-southeast-1': 'Singapore',
    'us-east-1': 'US-Virginia',
    'us-west-2': 'US-Oregon',
    'eu-west-1': 'Ireland',
    'eu-central-1': 'Frankfurt',
    'us-central1': 'US-Iowa',
    'us': 'US',
    'asia-south1': 'India',
    'South India': 'India',
}
