# Cloud Resource Type to Scope Mapping

A comprehensive mapping of cloud resource types to their functional scopes across AWS, GCP, and Azure.

---

## 📊 Scope Categories

| Scope | Description |
|-------|-------------|
| **Compute** | Virtual machines, containers, serverless functions, batch processing |
| **Storage** | Object storage, block storage, file storage, archival |
| **Database** | Relational, NoSQL, caching, data warehousing |
| **Network** | Virtual networks, load balancers, CDN, DNS, gateways |
| **Security** | Identity, access management, secrets, encryption, firewalls |
| **Analytics** | Big data, data processing, BI, streaming |
| **AI/ML** | Machine learning, AI services, vision, NLP |
| **Integration** | Messaging, queuing, API management, event-driven |
| **Management** | Monitoring, logging, automation, governance |
| **Developer Tools** | CI/CD, repositories, build services |
| **IoT** | Internet of Things platforms and services |
| **Migration** | Data migration, application migration tools |
| **Containers** | Container orchestration, registries, services |

---

## ☁️ AWS (Amazon Web Services)

### Compute

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `aws_instance` | EC2 | Elastic Compute Cloud virtual servers |
| `aws_launch_template` | EC2 | Templates for launching EC2 instances |
| `aws_autoscaling_group` | Auto Scaling | Automatically scale EC2 capacity |
| `aws_spot_instance_request` | EC2 Spot | Spare compute capacity at reduced cost |
| `aws_spot_fleet_request` | EC2 Spot Fleet | Multiple Spot Instance requests |
| `aws_lambda_function` | Lambda | Serverless compute service |
| `aws_lambda_layer_version` | Lambda | Lambda function layers |
| `aws_batch_job_definition` | Batch | Batch computing jobs |
| `aws_batch_compute_environment` | Batch | Batch compute environments |
| `aws_lightsail_instance` | Lightsail | Simple virtual private servers |
| `aws_elastic_beanstalk_environment` | Elastic Beanstalk | Application deployment platform |
| `aws_apprunner_service` | App Runner | Container-based web apps |
| `aws_outposts_rack` | Outposts | AWS infrastructure on-premises |

### Storage

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `aws_s3_bucket` | S3 | Simple Storage Service buckets |
| `aws_s3_object` | S3 | Objects within S3 buckets |
| `aws_s3_bucket_versioning` | S3 | S3 bucket versioning config |
| `aws_s3_glacier_vault` | Glacier | Archive storage vaults |
| `aws_ebs_volume` | EBS | Elastic Block Store volumes |
| `aws_ebs_snapshot` | EBS | EBS volume snapshots |
| `aws_efs_file_system` | EFS | Elastic File System |
| `aws_efs_mount_target` | EFS | EFS mount points |
| `aws_fsx_lustre_file_system` | FSx for Lustre | High-performance file system |
| `aws_fsx_windows_file_system` | FSx for Windows | Windows file server |
| `aws_fsx_ontap_file_system` | FSx for NetApp ONTAP | Enterprise file storage |
| `aws_fsx_openzfs_file_system` | FSx for OpenZFS | ZFS-based file system |
| `aws_storagegateway_gateway` | Storage Gateway | Hybrid cloud storage |
| `aws_backup_vault` | AWS Backup | Centralized backup storage |
| `aws_datasync_task` | DataSync | Data transfer automation |

### Database

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `aws_db_instance` | RDS | Relational Database Service instance |
| `aws_rds_cluster` | RDS Aurora | Aurora DB cluster |
| `aws_rds_cluster_instance` | RDS Aurora | Aurora cluster instances |
| `aws_db_subnet_group` | RDS | Database subnet groups |
| `aws_db_parameter_group` | RDS | Database parameter groups |
| `aws_dynamodb_table` | DynamoDB | NoSQL database tables |
| `aws_dynamodb_global_table` | DynamoDB | Multi-region tables |
| `aws_elasticache_cluster` | ElastiCache | In-memory caching (Redis/Memcached) |
| `aws_elasticache_replication_group` | ElastiCache | Redis replication groups |
| `aws_redshift_cluster` | Redshift | Data warehouse cluster |
| `aws_redshift_serverless_workgroup` | Redshift Serverless | Serverless data warehouse |
| `aws_neptune_cluster` | Neptune | Graph database |
| `aws_docdb_cluster` | DocumentDB | MongoDB-compatible database |
| `aws_timestream_database` | Timestream | Time-series database |
| `aws_keyspaces_table` | Keyspaces | Cassandra-compatible database |
| `aws_memorydb_cluster` | MemoryDB | Redis-compatible in-memory database |
| `aws_qldb_ledger` | QLDB | Quantum Ledger Database |

### Network

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `aws_vpc` | VPC | Virtual Private Cloud |
| `aws_subnet` | VPC | VPC subnets |
| `aws_internet_gateway` | VPC | Internet gateway |
| `aws_nat_gateway` | VPC | NAT gateway |
| `aws_route_table` | VPC | Route tables |
| `aws_network_acl` | VPC | Network ACLs |
| `aws_security_group` | VPC | Security groups |
| `aws_vpc_peering_connection` | VPC | VPC peering |
| `aws_vpn_gateway` | VPN | VPN gateway |
| `aws_vpn_connection` | VPN | Site-to-Site VPN |
| `aws_customer_gateway` | VPN | Customer gateway |
| `aws_lb` | ELB | Application/Network Load Balancer |
| `aws_lb_target_group` | ELB | Load balancer target groups |
| `aws_elb` | ELB Classic | Classic Load Balancer |
| `aws_cloudfront_distribution` | CloudFront | CDN distribution |
| `aws_cloudfront_function` | CloudFront | Edge functions |
| `aws_route53_zone` | Route 53 | DNS hosted zone |
| `aws_route53_record` | Route 53 | DNS records |
| `aws_route53_health_check` | Route 53 | DNS health checks |
| `aws_dx_connection` | Direct Connect | Dedicated network connection |
| `aws_dx_gateway` | Direct Connect | Direct Connect gateway |
| `aws_transit_gateway` | Transit Gateway | Central network hub |
| `aws_transit_gateway_attachment` | Transit Gateway | TGW attachments |
| `aws_global_accelerator` | Global Accelerator | Network performance optimization |
| `aws_api_gateway_rest_api` | API Gateway | REST API management |
| `aws_apigatewayv2_api` | API Gateway v2 | HTTP/WebSocket APIs |
| `aws_elastic_ip` | EC2 | Elastic IP addresses |
| `aws_network_interface` | EC2 | Elastic network interfaces |
| `aws_privatelink_endpoint` | PrivateLink | Private connectivity to services |
| `aws_vpc_endpoint` | VPC | VPC endpoints |

### Security

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `aws_iam_user` | IAM | Identity and Access Management users |
| `aws_iam_group` | IAM | IAM groups |
| `aws_iam_role` | IAM | IAM roles |
| `aws_iam_policy` | IAM | IAM policies |
| `aws_iam_instance_profile` | IAM | EC2 instance profiles |
| `aws_iam_access_key` | IAM | User access keys |
| `aws_iam_saml_provider` | IAM | SAML identity providers |
| `aws_iam_openid_connect_provider` | IAM | OIDC providers |
| `aws_kms_key` | KMS | Key Management Service keys |
| `aws_kms_alias` | KMS | KMS key aliases |
| `aws_secretsmanager_secret` | Secrets Manager | Secrets storage |
| `aws_ssm_parameter` | SSM | Parameter Store |
| `aws_acm_certificate` | ACM | SSL/TLS certificates |
| `aws_waf_web_acl` | WAF | Web Application Firewall |
| `aws_wafv2_web_acl` | WAFv2 | WAF v2 rules |
| `aws_shield_protection` | Shield | DDoS protection |
| `aws_guardduty_detector` | GuardDuty | Threat detection |
| `aws_inspector_assessment_template` | Inspector | Security assessment |
| `aws_macie2_classification_job` | Macie | Data discovery and protection |
| `aws_securityhub_account` | Security Hub | Security posture management |
| `aws_firewall_manager_policy` | Firewall Manager | Cross-account firewall rules |
| `aws_network_firewall` | Network Firewall | VPC network firewall |
| `aws_cognito_user_pool` | Cognito | User authentication |
| `aws_cognito_identity_pool` | Cognito | Federated identities |
| `aws_directory_service_directory` | Directory Service | Managed Active Directory |
| `aws_sso_instance` | SSO | Single Sign-On |

### Analytics

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `aws_athena_workgroup` | Athena | Interactive SQL queries on S3 |
| `aws_athena_database` | Athena | Athena databases |
| `aws_emr_cluster` | EMR | Elastic MapReduce big data |
| `aws_emr_serverless_application` | EMR Serverless | Serverless big data |
| `aws_glue_catalog_database` | Glue | Data catalog databases |
| `aws_glue_catalog_table` | Glue | Data catalog tables |
| `aws_glue_job` | Glue | ETL jobs |
| `aws_glue_crawler` | Glue | Data crawlers |
| `aws_kinesis_stream` | Kinesis | Real-time data streaming |
| `aws_kinesis_firehose_delivery_stream` | Kinesis Firehose | Data delivery |
| `aws_kinesis_analytics_application` | Kinesis Analytics | Stream processing |
| `aws_quicksight_analysis` | QuickSight | BI dashboards and analytics |
| `aws_quicksight_dataset` | QuickSight | QuickSight datasets |
| `aws_lakeformation_resource` | Lake Formation | Data lake management |
| `aws_opensearch_domain` | OpenSearch | Search and analytics |
| `aws_elasticsearch_domain` | Elasticsearch | Elasticsearch Service |
| `aws_msk_cluster` | MSK | Managed Kafka |
| `aws_databrew_project` | DataBrew | Data preparation |
| `aws_redshift_datashare` | Redshift | Data sharing |

### AI/ML

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `aws_sagemaker_domain` | SageMaker | ML development environment |
| `aws_sagemaker_notebook_instance` | SageMaker | Jupyter notebooks |
| `aws_sagemaker_endpoint` | SageMaker | ML model endpoints |
| `aws_sagemaker_model` | SageMaker | ML models |
| `aws_sagemaker_training_job` | SageMaker | Model training jobs |
| `aws_sagemaker_feature_group` | SageMaker | Feature store |
| `aws_sagemaker_pipeline` | SageMaker | ML pipelines |
| `aws_rekognition_project` | Rekognition | Computer vision |
| `aws_comprehend_entity_recognizer` | Comprehend | NLP analysis |
| `aws_lex_bot` | Lex | Conversational AI |
| `aws_polly_lexicon` | Polly | Text-to-speech |
| `aws_transcribe_vocabulary` | Transcribe | Speech-to-text |
| `aws_translate_terminology` | Translate | Language translation |
| `aws_textract_document_analyzer` | Textract | Document analysis |
| `aws_forecast_dataset` | Forecast | Time-series forecasting |
| `aws_personalize_dataset_group` | Personalize | Personalization |
| `aws_bedrock_model_customization_job` | Bedrock | Foundation models |
| `aws_comprehendmedical_entity` | Comprehend Medical | Medical NLP |
| `aws_kendra_index` | Kendra | Intelligent search |

### Integration

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `aws_sns_topic` | SNS | Simple Notification Service |
| `aws_sns_subscription` | SNS | SNS subscriptions |
| `aws_sqs_queue` | SQS | Simple Queue Service |
| `aws_eventbridge_rule` | EventBridge | Event rules |
| `aws_eventbridge_bus` | EventBridge | Event buses |
| `aws_eventbridge_pipe` | EventBridge Pipes | Event routing |
| `aws_sfn_state_machine` | Step Functions | Workflow orchestration |
| `aws_mq_broker` | Amazon MQ | Message broker |
| `aws_appflow_flow` | AppFlow | SaaS integration |
| `aws_appsync_graphql_api` | AppSync | GraphQL APIs |
| `aws_swf_domain` | SWF | Simple Workflow Service |

### Management

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `aws_cloudwatch_metric_alarm` | CloudWatch | Metric alarms |
| `aws_cloudwatch_log_group` | CloudWatch Logs | Log groups |
| `aws_cloudwatch_dashboard` | CloudWatch | Dashboards |
| `aws_cloudwatch_event_rule` | CloudWatch Events | Event rules |
| `aws_cloudtrail` | CloudTrail | API activity logging |
| `aws_config_rule` | Config | Configuration compliance |
| `aws_config_aggregation_authorization` | Config | Multi-account config |
| `aws_organizations_account` | Organizations | AWS Organizations |
| `aws_organizations_organizational_unit` | Organizations | Organizational units |
| `aws_organizations_policy` | Organizations | Service control policies |
| `aws_servicecatalog_portfolio` | Service Catalog | IT service catalog |
| `aws_systems_manager_document` | Systems Manager | Automation documents |
| `aws_ssm_maintenance_window` | Systems Manager | Maintenance windows |
| `aws_ssm_patch_baseline` | Systems Manager | Patch management |
| `aws_health_event` | Health | Service health |
| `aws_trusted_advisor_check` | Trusted Advisor | Best practices |
| `aws_controltower_landing_zone` | Control Tower | Multi-account governance |
| `aws_budgets_budget` | Budgets | Cost budgets |
| `aws_ce_cost_category` | Cost Explorer | Cost categorization |
| `aws_resourcegroups_group` | Resource Groups | Resource organization |
| `aws_license_manager_license_configuration` | License Manager | License tracking |

### Developer Tools

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `aws_codecommit_repository` | CodeCommit | Git repositories |
| `aws_codebuild_project` | CodeBuild | Build service |
| `aws_codepipeline` | CodePipeline | CI/CD pipelines |
| `aws_codedeploy_application` | CodeDeploy | Deployment service |
| `aws_codedeploy_deployment_group` | CodeDeploy | Deployment groups |
| `aws_codeartifact_repository` | CodeArtifact | Artifact management |
| `aws_codestar_project` | CodeStar | Development projects |
| `aws_cloud9_environment` | Cloud9 | Cloud IDE |
| `aws_xray_group` | X-Ray | Application tracing |
| `aws_codeguru_profiler_profiling_group` | CodeGuru | Code analysis |
| `aws_amplify_app` | Amplify | Full-stack app hosting |
| `aws_amplify_branch` | Amplify | Branch deployments |

### Containers

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `aws_ecs_cluster` | ECS | Elastic Container Service cluster |
| `aws_ecs_service` | ECS | ECS services |
| `aws_ecs_task_definition` | ECS | Task definitions |
| `aws_ecs_capacity_provider` | ECS | Capacity providers |
| `aws_eks_cluster` | EKS | Elastic Kubernetes Service |
| `aws_eks_node_group` | EKS | EKS node groups |
| `aws_eks_fargate_profile` | EKS | Fargate profiles |
| `aws_eks_addon` | EKS | EKS add-ons |
| `aws_ecr_repository` | ECR | Container registry |
| `aws_ecr_public_repository` | ECR Public | Public container registry |
| `aws_fargate_profile` | Fargate | Serverless containers |

### IoT

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `aws_iot_thing` | IoT Core | IoT devices |
| `aws_iot_thing_group` | IoT Core | Device groups |
| `aws_iot_policy` | IoT Core | IoT policies |
| `aws_iot_certificate` | IoT Core | Device certificates |
| `aws_iot_topic_rule` | IoT Core | Message routing |
| `aws_iot_analytics_dataset` | IoT Analytics | IoT data analytics |
| `aws_iot_events_detector_model` | IoT Events | Event detection |
| `aws_iot_sitewise_asset` | IoT SiteWise | Industrial IoT |
| `aws_greengrass_group` | Greengrass | Edge IoT |
| `aws_iot_fleet_hub_application` | IoT Fleet Hub | Fleet management |

### Migration

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `aws_dms_replication_instance` | DMS | Database Migration Service |
| `aws_dms_endpoint` | DMS | Migration endpoints |
| `aws_dms_replication_task` | DMS | Replication tasks |
| `aws_transfer_server` | Transfer Family | SFTP/FTPS servers |
| `aws_transfer_user` | Transfer Family | Transfer users |
| `aws_snowball_job` | Snowball | Data transport |
| `aws_mgn_source_server` | MGN | Application migration |
| `aws_appstream_fleet` | AppStream | Application streaming |
| `aws_workspaces_workspace` | WorkSpaces | Virtual desktops |

---

## 🔷 GCP (Google Cloud Platform)

### Compute

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `google_compute_instance` | Compute Engine | Virtual machine instances |
| `google_compute_instance_template` | Compute Engine | Instance templates |
| `google_compute_instance_group_manager` | Compute Engine | Managed instance groups |
| `google_compute_autoscaler` | Compute Engine | Autoscaling |
| `google_compute_region_instance_group_manager` | Compute Engine | Regional MIGs |
| `google_cloudfunctions_function` | Cloud Functions | Serverless functions (Gen 1) |
| `google_cloudfunctions2_function` | Cloud Functions | Serverless functions (Gen 2) |
| `google_cloud_run_service` | Cloud Run | Serverless containers |
| `google_cloud_run_v2_service` | Cloud Run v2 | Cloud Run services |
| `google_cloud_run_v2_job` | Cloud Run Jobs | Container jobs |
| `google_app_engine_application` | App Engine | PaaS application hosting |
| `google_app_engine_flexible_app_version` | App Engine Flex | Flexible environment |
| `google_app_engine_standard_app_version` | App Engine Standard | Standard environment |
| `google_compute_reservation` | Compute Engine | Reserved capacity |
| `google_compute_sole_tenant_node_group` | Compute Engine | Dedicated physical servers |
| `google_dataflow_job` | Dataflow | Stream/batch processing |
| `google_dataproc_cluster` | Dataproc | Managed Spark/Hadoop |
| `google_dataproc_batch` | Dataproc | Serverless Spark |

### Storage

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `google_storage_bucket` | Cloud Storage | Object storage buckets |
| `google_storage_bucket_object` | Cloud Storage | Storage objects |
| `google_storage_bucket_iam_binding` | Cloud Storage | Bucket IAM |
| `google_compute_disk` | Persistent Disk | Block storage |
| `google_compute_snapshot` | Persistent Disk | Disk snapshots |
| `google_compute_image` | Compute Engine | Custom images |
| `google_filestore_instance` | Filestore | Managed NFS |
| `google_storage_transfer_job` | Storage Transfer | Data transfer |
| `google_backup_dr_management_server` | Backup and DR | Backup service |
| `google_netapp_volume` | NetApp Volumes | Enterprise file storage |
| `google_parallelstore_instance` | Parallelstore | High-performance storage |

### Database

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `google_sql_database_instance` | Cloud SQL | Managed MySQL/PostgreSQL/SQL Server |
| `google_sql_database` | Cloud SQL | SQL databases |
| `google_sql_user` | Cloud SQL | Database users |
| `google_spanner_instance` | Cloud Spanner | Globally distributed database |
| `google_spanner_database` | Cloud Spanner | Spanner databases |
| `google_bigtable_instance` | Bigtable | Wide-column NoSQL |
| `google_bigtable_table` | Bigtable | Bigtable tables |
| `google_firestore_database` | Firestore | Document database |
| `google_firestore_document` | Firestore | Firestore documents |
| `google_datastore_index` | Datastore | NoSQL indexes |
| `google_redis_instance` | Memorystore Redis | Managed Redis |
| `google_memcache_instance` | Memorystore Memcached | Managed Memcached |
| `google_alloydb_cluster` | AlloyDB | PostgreSQL-compatible DB |
| `google_alloydb_instance` | AlloyDB | AlloyDB instances |
| `google_database_migration_service_connection_profile` | DMS | Migration profiles |

### Network

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `google_compute_network` | VPC | Virtual Private Cloud |
| `google_compute_subnetwork` | VPC | VPC subnets |
| `google_compute_firewall` | VPC | Firewall rules |
| `google_compute_router` | Cloud Router | Network routing |
| `google_compute_route` | VPC | Custom routes |
| `google_compute_vpn_gateway` | Cloud VPN | VPN gateway |
| `google_compute_vpn_tunnel` | Cloud VPN | VPN tunnels |
| `google_compute_ha_vpn_gateway` | Cloud VPN | HA VPN |
| `google_compute_interconnect_attachment` | Cloud Interconnect | Dedicated interconnect |
| `google_compute_global_forwarding_rule` | Cloud Load Balancing | Global forwarding |
| `google_compute_forwarding_rule` | Cloud Load Balancing | Regional forwarding |
| `google_compute_target_http_proxy` | Cloud Load Balancing | HTTP proxy |
| `google_compute_target_https_proxy` | Cloud Load Balancing | HTTPS proxy |
| `google_compute_backend_service` | Cloud Load Balancing | Backend services |
| `google_compute_url_map` | Cloud Load Balancing | URL maps |
| `google_compute_health_check` | Cloud Load Balancing | Health checks |
| `google_compute_ssl_certificate` | Cloud Load Balancing | SSL certificates |
| `google_compute_global_address` | VPC | Global IP addresses |
| `google_compute_address` | VPC | Regional IP addresses |
| `google_dns_managed_zone` | Cloud DNS | DNS zones |
| `google_dns_record_set` | Cloud DNS | DNS records |
| `google_compute_network_peering` | VPC | VPC peering |
| `google_service_networking_connection` | VPC | Private service access |
| `google_network_connectivity_hub` | Network Connectivity | Network hub |
| `google_network_connectivity_spoke` | Network Connectivity | Network spokes |
| `google_network_services_edge_cache_service` | Media CDN | CDN services |
| `google_compute_packet_mirroring` | VPC | Packet mirroring |
| `google_network_security_security_profile` | Cloud NGFW | Network security |
| `google_compute_network_endpoint_group` | VPC | NEGs |

### Security

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `google_project_iam_member` | IAM | Project-level IAM |
| `google_project_iam_binding` | IAM | IAM bindings |
| `google_project_iam_policy` | IAM | IAM policies |
| `google_service_account` | IAM | Service accounts |
| `google_service_account_key` | IAM | Service account keys |
| `google_organization_iam_member` | IAM | Org-level IAM |
| `google_folder_iam_member` | IAM | Folder-level IAM |
| `google_kms_key_ring` | Cloud KMS | Key rings |
| `google_kms_crypto_key` | Cloud KMS | Encryption keys |
| `google_kms_crypto_key_version` | Cloud KMS | Key versions |
| `google_secret_manager_secret` | Secret Manager | Secrets storage |
| `google_secret_manager_secret_version` | Secret Manager | Secret versions |
| `google_compute_security_policy` | Cloud Armor | WAF/DDoS protection |
| `google_recaptcha_enterprise_key` | reCAPTCHA Enterprise | Bot detection |
| `google_iap_tunnel_instance_iam_member` | IAP | Identity-Aware Proxy |
| `google_iap_web_backend_service_iam_member` | IAP | Web IAP |
| `google_identity_platform_config` | Identity Platform | Authentication |
| `google_access_context_manager_access_policy` | VPC Service Controls | Access policies |
| `google_access_context_manager_service_perimeter` | VPC Service Controls | Service perimeters |
| `google_certificate_manager_certificate` | Certificate Manager | SSL certificates |
| `google_binary_authorization_policy` | Binary Authorization | Container security |
| `google_security_center_source` | Security Command Center | Security findings |
| `google_assured_workloads_workload` | Assured Workloads | Compliance controls |

### Analytics

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `google_bigquery_dataset` | BigQuery | Data warehouse datasets |
| `google_bigquery_table` | BigQuery | BigQuery tables |
| `google_bigquery_job` | BigQuery | Query jobs |
| `google_bigquery_routine` | BigQuery | Functions/procedures |
| `google_bigquery_data_transfer_config` | BigQuery DT | Data transfers |
| `google_bigquery_reservation` | BigQuery | Slot reservations |
| `google_bigquery_bi_reservation` | BigQuery BI Engine | BI acceleration |
| `google_pubsub_topic` | Pub/Sub | Message topics |
| `google_pubsub_subscription` | Pub/Sub | Subscriptions |
| `google_pubsub_lite_topic` | Pub/Sub Lite | Lite topics |
| `google_dataflow_flex_template_job` | Dataflow | Flex template jobs |
| `google_data_catalog_entry` | Data Catalog | Metadata management |
| `google_data_catalog_tag_template` | Data Catalog | Tag templates |
| `google_dataplex_lake` | Dataplex | Data lakes |
| `google_dataplex_zone` | Dataplex | Data zones |
| `google_looker_instance` | Looker | BI platform |
| `google_composer_environment` | Cloud Composer | Managed Airflow |

### AI/ML

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `google_vertex_ai_dataset` | Vertex AI | ML datasets |
| `google_vertex_ai_endpoint` | Vertex AI | Model endpoints |
| `google_vertex_ai_model` | Vertex AI | ML models |
| `google_vertex_ai_training_pipeline` | Vertex AI | Training pipelines |
| `google_vertex_ai_feature_store` | Vertex AI | Feature store |
| `google_vertex_ai_tensorboard` | Vertex AI | Experiment tracking |
| `google_vertex_ai_index` | Vertex AI | Vector search |
| `google_notebooks_instance` | Vertex AI Notebooks | Jupyter notebooks |
| `google_workbench_instance` | Vertex AI Workbench | ML workstation |
| `google_ml_engine_model` | AI Platform | Legacy ML models |
| `google_dialogflow_agent` | Dialogflow | Conversational AI |
| `google_dialogflow_cx_agent` | Dialogflow CX | Advanced agents |
| `google_document_ai_processor` | Document AI | Document processing |
| `google_vision_product_set` | Vision AI | Product search |
| `google_speech_custom_class` | Speech-to-Text | Speech recognition |
| `google_text_to_speech_voice` | Text-to-Speech | Voice synthesis |
| `google_translate_glossary` | Translation | Language translation |
| `google_automl_model` | AutoML | Automated ML |

### Integration

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `google_cloud_scheduler_job` | Cloud Scheduler | Cron job service |
| `google_cloud_tasks_queue` | Cloud Tasks | Task queues |
| `google_workflows_workflow` | Workflows | Workflow orchestration |
| `google_eventarc_trigger` | Eventarc | Event-driven triggers |
| `google_api_gateway_api` | API Gateway | API management |
| `google_api_gateway_gateway` | API Gateway | API gateways |
| `google_apigee_organization` | Apigee | Full API management |
| `google_apigee_environment` | Apigee | API environments |
| `google_integration_connectors_connection` | Integration Connectors | App integration |

### Management

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `google_monitoring_alert_policy` | Cloud Monitoring | Alert policies |
| `google_monitoring_notification_channel` | Cloud Monitoring | Notification channels |
| `google_monitoring_dashboard` | Cloud Monitoring | Dashboards |
| `google_monitoring_uptime_check_config` | Cloud Monitoring | Uptime checks |
| `google_monitoring_metric_descriptor` | Cloud Monitoring | Custom metrics |
| `google_logging_metric` | Cloud Logging | Log-based metrics |
| `google_logging_sink` | Cloud Logging | Log sinks |
| `google_logging_bucket_config` | Cloud Logging | Log buckets |
| `google_logging_log_view` | Cloud Logging | Log views |
| `google_cloud_asset_organization_feed` | Cloud Asset Inventory | Asset feeds |
| `google_org_policy_policy` | Organization Policy | Org policies |
| `google_resource_manager_lien` | Resource Manager | Resource locks |
| `google_billing_budget` | Cloud Billing | Cost budgets |
| `google_error_reporting_sink` | Error Reporting | Error tracking |
| `google_cloud_deploy_delivery_pipeline` | Cloud Deploy | Continuous delivery |
| `google_project` | Resource Manager | GCP projects |
| `google_folder` | Resource Manager | Folders |
| `google_organization` | Resource Manager | Organizations |

### Developer Tools

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `google_cloudbuild_trigger` | Cloud Build | Build triggers |
| `google_cloudbuild_worker_pool` | Cloud Build | Worker pools |
| `google_sourcerepo_repository` | Cloud Source Repositories | Git repos |
| `google_artifact_registry_repository` | Artifact Registry | Package registry |
| `google_container_registry` | Container Registry | Container images |
| `google_firebase_project` | Firebase | App development platform |
| `google_firebase_hosting_site` | Firebase Hosting | Static web hosting |
| `google_firebase_database_instance` | Firebase Realtime DB | Realtime database |
| `google_cloud_shell_environment` | Cloud Shell | Browser-based shell |

### Containers

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `google_container_cluster` | GKE | Google Kubernetes Engine |
| `google_container_node_pool` | GKE | Node pools |
| `google_gke_hub_membership` | GKE Hub | Fleet membership |
| `google_gke_hub_feature` | GKE Hub | Fleet features |
| `google_container_attached_cluster` | Anthos | Attached clusters |
| `google_gke_backup_backup_plan` | GKE Backup | Backup plans |
| `google_artifact_registry_repository` | Artifact Registry | Container registry |
| `google_container_analysis_note` | Container Analysis | Vulnerability scanning |

### IoT

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `google_cloudiot_registry` | Cloud IoT Core | Device registry |
| `google_cloudiot_device` | Cloud IoT Core | IoT devices |
| `google_edgecontainer_cluster` | Distributed Cloud Edge | Edge containers |

### Migration

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `google_database_migration_service_migration_job` | DMS | Database migration |
| `google_storage_transfer_job` | Storage Transfer | Data transfer |
| `google_vmware_engine_private_cloud` | VMware Engine | VMware workloads |
| `google_workstations_workstation` | Cloud Workstations | Dev workstations |
| `google_workstations_workstation_cluster` | Cloud Workstations | Workstation clusters |

---

## 🔶 Azure (Microsoft Azure)

### Compute

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `azurerm_virtual_machine` | Virtual Machines | Classic VMs |
| `azurerm_linux_virtual_machine` | Virtual Machines | Linux VMs |
| `azurerm_windows_virtual_machine` | Virtual Machines | Windows VMs |
| `azurerm_virtual_machine_scale_set` | VM Scale Sets | Auto-scaling VMs |
| `azurerm_linux_virtual_machine_scale_set` | VM Scale Sets | Linux VMSS |
| `azurerm_windows_virtual_machine_scale_set` | VM Scale Sets | Windows VMSS |
| `azurerm_availability_set` | Availability Sets | HA grouping |
| `azurerm_proximity_placement_group` | Proximity Placement | Low-latency grouping |
| `azurerm_dedicated_host` | Dedicated Hosts | Dedicated physical servers |
| `azurerm_dedicated_host_group` | Dedicated Hosts | Host groups |
| `azurerm_function_app` | Azure Functions | Serverless functions |
| `azurerm_linux_function_app` | Azure Functions | Linux functions |
| `azurerm_windows_function_app` | Azure Functions | Windows functions |
| `azurerm_app_service` | App Service | Web app hosting |
| `azurerm_app_service_plan` | App Service | App service plans |
| `azurerm_linux_web_app` | App Service | Linux web apps |
| `azurerm_windows_web_app` | App Service | Windows web apps |
| `azurerm_static_site` | Static Web Apps | Static site hosting |
| `azurerm_batch_account` | Azure Batch | Batch computing |
| `azurerm_batch_pool` | Azure Batch | Batch pools |
| `azurerm_spring_cloud_app` | Spring Apps | Spring Boot apps |
| `azurerm_container_app` | Container Apps | Serverless containers |
| `azurerm_container_app_environment` | Container Apps | Container environments |
| `azurerm_maintenance_configuration` | Maintenance | VM maintenance |
| `azurerm_image` | Compute | Custom VM images |
| `azurerm_shared_image` | Compute Gallery | Shared images |
| `azurerm_shared_image_gallery` | Compute Gallery | Image galleries |

### Storage

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `azurerm_storage_account` | Storage Account | General-purpose storage |
| `azurerm_storage_container` | Blob Storage | Blob containers |
| `azurerm_storage_blob` | Blob Storage | Binary large objects |
| `azurerm_storage_share` | File Storage | Azure Files shares |
| `azurerm_storage_queue` | Queue Storage | Message queues |
| `azurerm_storage_table` | Table Storage | NoSQL tables |
| `azurerm_storage_data_lake_gen2_filesystem` | Data Lake Gen2 | ADLS Gen2 |
| `azurerm_data_lake_store` | Data Lake Gen1 | ADLS Gen1 |
| `azurerm_managed_disk` | Managed Disks | VM disks |
| `azurerm_snapshot` | Managed Disks | Disk snapshots |
| `azurerm_disk_encryption_set` | Managed Disks | Disk encryption |
| `azurerm_hpc_cache` | HPC Cache | High-performance cache |
| `azurerm_netapp_account` | NetApp Files | Enterprise NFS |
| `azurerm_netapp_pool` | NetApp Files | Capacity pools |
| `azurerm_netapp_volume` | NetApp Files | File volumes |
| `azurerm_recovery_services_vault` | Recovery Services | Backup vault |
| `azurerm_backup_policy_vm` | Backup | VM backup policies |
| `azurerm_storage_sync` | File Sync | Sync service |

### Database

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `azurerm_mssql_server` | Azure SQL | SQL Server |
| `azurerm_mssql_database` | Azure SQL | SQL databases |
| `azurerm_mssql_elasticpool` | Azure SQL | Elastic pools |
| `azurerm_mssql_managed_instance` | Azure SQL MI | Managed instances |
| `azurerm_mysql_server` | MySQL | MySQL servers |
| `azurerm_mysql_flexible_server` | MySQL Flexible | Flexible MySQL |
| `azurerm_mysql_database` | MySQL | MySQL databases |
| `azurerm_postgresql_server` | PostgreSQL | PostgreSQL servers |
| `azurerm_postgresql_flexible_server` | PostgreSQL Flexible | Flexible PostgreSQL |
| `azurerm_postgresql_database` | PostgreSQL | PostgreSQL databases |
| `azurerm_mariadb_server` | MariaDB | MariaDB servers |
| `azurerm_cosmosdb_account` | Cosmos DB | Multi-model database |
| `azurerm_cosmosdb_sql_database` | Cosmos DB | SQL API databases |
| `azurerm_cosmosdb_mongo_database` | Cosmos DB | MongoDB API |
| `azurerm_cosmosdb_cassandra_keyspace` | Cosmos DB | Cassandra API |
| `azurerm_cosmosdb_gremlin_database` | Cosmos DB | Gremlin API |
| `azurerm_cosmosdb_table` | Cosmos DB | Table API |
| `azurerm_redis_cache` | Azure Cache for Redis | Managed Redis |
| `azurerm_redis_enterprise_cluster` | Redis Enterprise | Enterprise Redis |
| `azurerm_synapse_workspace` | Synapse Analytics | Data warehouse |
| `azurerm_synapse_sql_pool` | Synapse Analytics | SQL pools |
| `azurerm_synapse_spark_pool` | Synapse Analytics | Spark pools |
| `azurerm_kusto_cluster` | Data Explorer | Time-series analytics |
| `azurerm_kusto_database` | Data Explorer | Kusto databases |

### Network

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `azurerm_virtual_network` | Virtual Network | VNets |
| `azurerm_subnet` | Virtual Network | Subnets |
| `azurerm_network_security_group` | NSG | Network security |
| `azurerm_network_interface` | NIC | Network interfaces |
| `azurerm_public_ip` | Public IP | Public IP addresses |
| `azurerm_public_ip_prefix` | Public IP | IP prefixes |
| `azurerm_nat_gateway` | NAT Gateway | NAT gateway |
| `azurerm_route_table` | Route Tables | Custom routing |
| `azurerm_virtual_network_gateway` | VPN Gateway | VPN/ExpressRoute |
| `azurerm_vpn_gateway` | VPN Gateway | Virtual WAN VPN |
| `azurerm_local_network_gateway` | VPN Gateway | On-prem gateway |
| `azurerm_vpn_site` | Virtual WAN | VPN sites |
| `azurerm_virtual_wan` | Virtual WAN | WAN hub |
| `azurerm_virtual_hub` | Virtual WAN | Virtual hubs |
| `azurerm_express_route_circuit` | ExpressRoute | Private connection |
| `azurerm_express_route_gateway` | ExpressRoute | ExpressRoute gateway |
| `azurerm_lb` | Load Balancer | Network load balancer |
| `azurerm_lb_rule` | Load Balancer | LB rules |
| `azurerm_application_gateway` | Application Gateway | L7 load balancer |
| `azurerm_frontdoor` | Front Door | Global load balancer |
| `azurerm_cdn_frontdoor_profile` | Front Door CDN | CDN with WAF |
| `azurerm_cdn_profile` | CDN | Content delivery |
| `azurerm_cdn_endpoint` | CDN | CDN endpoints |
| `azurerm_dns_zone` | DNS | Public DNS zones |
| `azurerm_private_dns_zone` | Private DNS | Private DNS |
| `azurerm_dns_a_record` | DNS | A records |
| `azurerm_private_endpoint` | Private Link | Private endpoints |
| `azurerm_private_link_service` | Private Link | Private services |
| `azurerm_traffic_manager_profile` | Traffic Manager | DNS load balancing |
| `azurerm_network_watcher` | Network Watcher | Network monitoring |
| `azurerm_virtual_network_peering` | VNet Peering | VNet connections |
| `azurerm_bastion_host` | Bastion | Secure VM access |
| `azurerm_api_management` | API Management | API gateway |
| `azurerm_application_insights` | Application Insights | APM |
| `azurerm_web_application_firewall_policy` | WAF | Web firewall |
| `azurerm_firewall` | Azure Firewall | Network firewall |
| `azurerm_firewall_policy` | Azure Firewall | Firewall policies |

### Security

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `azurerm_user_assigned_identity` | Managed Identity | User identities |
| `azurerm_role_assignment` | RBAC | Role assignments |
| `azurerm_role_definition` | RBAC | Custom roles |
| `azuread_application` | Azure AD | App registrations |
| `azuread_service_principal` | Azure AD | Service principals |
| `azuread_user` | Azure AD | AD users |
| `azuread_group` | Azure AD | AD groups |
| `azuread_conditional_access_policy` | Azure AD | Conditional access |
| `azurerm_key_vault` | Key Vault | Secrets/keys/certs |
| `azurerm_key_vault_secret` | Key Vault | Secrets |
| `azurerm_key_vault_key` | Key Vault | Encryption keys |
| `azurerm_key_vault_certificate` | Key Vault | Certificates |
| `azurerm_key_vault_managed_hardware_security_module` | HSM | Hardware security |
| `azurerm_security_center_subscription_pricing` | Defender for Cloud | Security posture |
| `azurerm_security_center_contact` | Defender for Cloud | Security contacts |
| `azurerm_sentinel_alert_rule` | Microsoft Sentinel | SIEM rules |
| `azurerm_sentinel_data_connector` | Microsoft Sentinel | Data connectors |
| `azurerm_ddos_protection_plan` | DDoS Protection | DDoS mitigation |
| `azurerm_network_security_rule` | NSG | Security rules |
| `azurerm_application_security_group` | ASG | App security groups |
| `azurerm_disk_access` | Disk Access | Disk security |
| `azurerm_confidential_ledger` | Confidential Ledger | Immutable data |

### Analytics

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `azurerm_data_factory` | Data Factory | ETL/ELT pipelines |
| `azurerm_data_factory_pipeline` | Data Factory | Data pipelines |
| `azurerm_data_factory_dataset_azure_blob` | Data Factory | Blob datasets |
| `azurerm_databricks_workspace` | Databricks | Apache Spark |
| `azurerm_hdinsight_hadoop_cluster` | HDInsight | Hadoop clusters |
| `azurerm_hdinsight_spark_cluster` | HDInsight | Spark clusters |
| `azurerm_hdinsight_kafka_cluster` | HDInsight | Kafka clusters |
| `azurerm_hdinsight_hbase_cluster` | HDInsight | HBase clusters |
| `azurerm_stream_analytics_job` | Stream Analytics | Real-time analytics |
| `azurerm_eventhub_namespace` | Event Hubs | Event streaming |
| `azurerm_eventhub` | Event Hubs | Event hubs |
| `azurerm_analysis_services_server` | Analysis Services | OLAP |
| `azurerm_powerbi_embedded` | Power BI Embedded | BI embedding |
| `azurerm_purview_account` | Microsoft Purview | Data governance |
| `azurerm_data_share_account` | Data Share | Data sharing |
| `azurerm_data_catalog` | Data Catalog | Metadata catalog |

### AI/ML

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `azurerm_machine_learning_workspace` | Machine Learning | ML workspace |
| `azurerm_machine_learning_compute_cluster` | Machine Learning | Compute clusters |
| `azurerm_machine_learning_compute_instance` | Machine Learning | Compute instances |
| `azurerm_machine_learning_inference_cluster` | Machine Learning | AKS inference |
| `azurerm_cognitive_account` | Cognitive Services | AI services |
| `azurerm_cognitive_deployment` | Azure OpenAI | OpenAI deployments |
| `azurerm_search_service` | Cognitive Search | AI-powered search |
| `azurerm_bot_service_azure_bot` | Bot Service | Chat bots |
| `azurerm_bot_channel_ms_teams` | Bot Service | Teams integration |
| `azurerm_video_analyzer` | Video Analyzer | Video analytics |
| `azurerm_maps_account` | Azure Maps | Geospatial services |

### Integration

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `azurerm_servicebus_namespace` | Service Bus | Enterprise messaging |
| `azurerm_servicebus_queue` | Service Bus | Queues |
| `azurerm_servicebus_topic` | Service Bus | Topics |
| `azurerm_servicebus_subscription` | Service Bus | Subscriptions |
| `azurerm_logic_app_workflow` | Logic Apps | Workflow automation |
| `azurerm_logic_app_integration_account` | Logic Apps | B2B integration |
| `azurerm_eventgrid_topic` | Event Grid | Event routing |
| `azurerm_eventgrid_domain` | Event Grid | Event domains |
| `azurerm_eventgrid_system_topic` | Event Grid | System topics |
| `azurerm_relay_namespace` | Relay | Hybrid connections |
| `azurerm_notification_hub_namespace` | Notification Hubs | Push notifications |
| `azurerm_notification_hub` | Notification Hubs | Notification hubs |
| `azurerm_signalr_service` | SignalR | Real-time messaging |
| `azurerm_web_pubsub` | Web PubSub | WebSocket messaging |

### Management

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `azurerm_log_analytics_workspace` | Log Analytics | Centralized logging |
| `azurerm_log_analytics_solution` | Log Analytics | Solutions |
| `azurerm_monitor_action_group` | Monitor | Alert actions |
| `azurerm_monitor_metric_alert` | Monitor | Metric alerts |
| `azurerm_monitor_diagnostic_setting` | Monitor | Diagnostic settings |
| `azurerm_monitor_autoscale_setting` | Monitor | Autoscale rules |
| `azurerm_automation_account` | Automation | Runbook automation |
| `azurerm_automation_runbook` | Automation | Runbooks |
| `azurerm_automation_schedule` | Automation | Schedules |
| `azurerm_policy_definition` | Azure Policy | Policy definitions |
| `azurerm_policy_assignment` | Azure Policy | Policy assignments |
| `azurerm_policy_set_definition` | Azure Policy | Policy initiatives |
| `azurerm_management_group` | Management Groups | Subscription grouping |
| `azurerm_resource_group` | Resource Manager | Resource groups |
| `azurerm_subscription` | Subscriptions | Azure subscriptions |
| `azurerm_management_lock` | Resource Manager | Resource locks |
| `azurerm_blueprint_definition` | Blueprints | Environment templates |
| `azurerm_cost_management_export` | Cost Management | Cost exports |
| `azurerm_consumption_budget` | Cost Management | Budgets |
| `azurerm_advisor_recommendation` | Advisor | Recommendations |
| `azurerm_service_health_alert` | Service Health | Health alerts |
| `azurerm_notification_hub` | Notification | Push notifications |

### Developer Tools

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `azurerm_dev_test_lab` | DevTest Labs | Development environments |
| `azurerm_dev_test_virtual_machine` | DevTest Labs | Lab VMs |
| `azurerm_devops_project` | Azure DevOps | DevOps projects |
| `azurerm_container_registry` | Container Registry | Docker registry |
| `azurerm_container_registry_task` | Container Registry | Build tasks |
| `azurerm_source_control_token` | App Service | Source control |
| `azuread_application_registration` | Azure AD | App registration |
| `azurerm_managed_application_definition` | Managed Apps | App definitions |
| `azurerm_template_deployment` | ARM Templates | Template deployments |
| `azurerm_resource_deployment_script` | Deployment Scripts | Custom deployment |
| `azurerm_lab_service_lab` | Lab Services | Lab environments |

### Containers

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `azurerm_kubernetes_cluster` | AKS | Azure Kubernetes Service |
| `azurerm_kubernetes_cluster_node_pool` | AKS | Node pools |
| `azurerm_kubernetes_fleet_manager` | AKS | Fleet management |
| `azurerm_container_group` | Container Instances | ACI containers |
| `azurerm_container_registry` | ACR | Container registry |
| `azurerm_container_registry_webhook` | ACR | Registry webhooks |
| `azurerm_service_fabric_cluster` | Service Fabric | Microservices platform |
| `azurerm_service_fabric_managed_cluster` | Service Fabric | Managed clusters |
| `azurerm_arc_kubernetes_cluster` | Azure Arc | Hybrid Kubernetes |

### IoT

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `azurerm_iothub` | IoT Hub | IoT message hub |
| `azurerm_iothub_dps` | IoT Hub DPS | Device provisioning |
| `azurerm_iothub_consumer_group` | IoT Hub | Consumer groups |
| `azurerm_iot_security_solution` | Defender for IoT | IoT security |
| `azurerm_iot_time_series_insights_environment` | Time Series Insights | IoT analytics |
| `azurerm_digital_twins_instance` | Digital Twins | Digital twin models |
| `azurerm_sphere_catalog` | Azure Sphere | Secure IoT devices |
| `azurerm_iot_central_application` | IoT Central | IoT SaaS platform |
| `azurerm_iot_hub_endpoint` | IoT Hub | Message routing |

### Migration

| Resource Type | Service Name | Description |
|--------------|--------------|-------------|
| `azurerm_database_migration_service` | DMS | Database migration |
| `azurerm_database_migration_project` | DMS | Migration projects |
| `azurerm_site_recovery_fabric` | Site Recovery | Disaster recovery |
| `azurerm_site_recovery_replication_policy` | Site Recovery | Replication policies |
| `azurerm_site_recovery_replicated_vm` | Site Recovery | Replicated VMs |
| `azurerm_data_box_edge_device` | Data Box | Data transfer devices |
| `azurerm_vmware_private_cloud` | VMware Solution | VMware on Azure |
| `azurerm_stack_hci_cluster` | Azure Stack HCI | Hybrid infrastructure |
| `azurerm_migrate_project` | Azure Migrate | Migration hub |
| `azurerm_virtual_desktop_host_pool` | Virtual Desktop | AVD host pools |
| `azurerm_virtual_desktop_workspace` | Virtual Desktop | AVD workspaces |
| `azurerm_virtual_desktop_application_group` | Virtual Desktop | App groups |

---

## 📋 Quick Reference Summary

### Resource Count by Scope and Provider

| Scope | AWS | GCP | Azure |
|-------|-----|-----|-------|
| Compute | 13 | 18 | 27 |
| Storage | 15 | 11 | 18 |
| Database | 17 | 15 | 23 |
| Network | 30 | 28 | 35 |
| Security | 26 | 23 | 22 |
| Analytics | 19 | 17 | 16 |
| AI/ML | 19 | 18 | 11 |
| Integration | 11 | 9 | 14 |
| Management | 20 | 17 | 21 |
| Developer Tools | 12 | 9 | 11 |
| Containers | 11 | 8 | 9 |
| IoT | 10 | 3 | 9 |
| Migration | 9 | 5 | 12 |

---

## 🏷️ Usage in Virtual Tagging

This mapping is essential for the Virtual Tagging system to:

1. **Normalize Resource Classification**: Ensure consistent scope categorization across multi-cloud environments
2. **Apply Scope-Based Tags**: Automatically tag resources with their functional scope
3. **Enable Scope-Based Filtering**: Filter resources by scope in dashboards and reports
4. **Cost Allocation**: Aggregate costs by scope category across providers
5. **Policy Enforcement**: Apply scope-specific governance policies
6. **ML Training**: Use scope as a feature for tag inference models

---

*Document generated for CloudTuner.ai Virtual Tagging System*  
*Last Updated: December 2024*
