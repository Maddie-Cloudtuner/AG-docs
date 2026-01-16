# Cloud-Tuner Image Versions

## Global Configuration
| Parameter | Value |
|-----------|-------|
| Global Tag | v1.3.0 |

## Service Images

| Service Name | Image Repository | Tag | Pull Policy |
|--------------|-----------------|-----|-------------|
| etcd | index.docker.io/invincibledocker24/etcd | v1.3.0 | IfNotPresent |
| mariadb | index.docker.io/invincibledocker24/mariadb | v1.3.0 | IfNotPresent |
| mongo | index.docker.io/invincibledocker24/mongo | v1.3.0-dev | IfNotPresent |
| rabbitmq | index.docker.io/invincibledocker24/rabbitmq | v1.3.0 | IfNotPresent |
| redis | index.docker.io/invincibledocker24/redis | v1.3.0 | IfNotPresent |
| restapi (dev) | index.docker.io/invincibledocker24/rest_api | v1.3.0-co2 | Always |
| payments (dev) | index.docker.io/invincibledocker24/payments_server | v1.3.0 | IfNotPresent |
| auth (dev) | index.docker.io/invincibledocker24/auth | v1.3.0 | Always |
| keeper | index.docker.io/invincibledocker24/keeper | v1.3.0 | Always |
| phpmyadmin | index.docker.io/invincibledocker24/phpmyadmin | v1.3.0 | IfNotPresent |
| herald | index.docker.io/invincibledocker24/herald | v1.3.0 | IfNotPresent |
| elk | index.docker.io/invincibledocker24/elk | v1.3.0 | IfNotPresent |
| filebeat | index.docker.io/invincibledocker24/filebeat | v1.3.0 | IfNotPresent |
| pgvector | pgvector/pgvector | pg17 | IfNotPresent |
| chat-agent | index.docker.io/invincibledocker24/chat-agent | v1.3.0 | IfNotPresent |
| mcp-mongo | invincibledocker24/mongodb-mcp | 0.1.0 | IfNotPresent |
| mcp-maria | index.docker.io/invincibledocker24/mariadb-mcp | 0.1.0 | IfNotPresent |
| agentic-chatbot | index.docker.io/invincibledocker24/agentic-chatbot | v1.3.1 | Always |
| admin | index.docker.io/invincibledocker24/admin | v1.3.0 | Always |
| ngui (dev) | index.docker.io/invincibledocker24/ngui | v1.3.0-dev-chatbot | Always |
| minio | index.docker.io/invincibledocker24/minio | v1.3.0 | IfNotPresent |
| diworker | index.docker.io/invincibledocker24/diworker | v1.3.0-dev-4 | Always |
| katara_service | index.docker.io/invincibledocker24/katara_service | v1.3.0-dev | IfNotPresent |
| katara_worker | index.docker.io/invincibledocker24/katara_worker | v1.3.0-dev | IfNotPresent |
| bumischeduler | index.docker.io/invincibledocker24/bumischeduler | v1.3.0 | IfNotPresent |
| bumiworker | index.docker.io/invincibledocker24/bumiworker | v1.3.0 | Always |
| report_import_scheduler | index.docker.io/invincibledocker24/cleanelkdb | v1.3.0 | IfNotPresent |
| resource_discovery | index.docker.io/invincibledocker24/resource_discovery | v1.3.0 | Always |
| demo_org_cleanup | index.docker.io/invincibledocker24/demo_org_cleanup | v1.3.0 | IfNotPresent |
| resource_observer | index.docker.io/invincibledocker24/resource_observer | v1.3.0 | IfNotPresent |
| resource_violations | index.docker.io/invincibledocker24/resource_violations | v1.3.0 | IfNotPresent |
| calendar_observer | index.docker.io/invincibledocker24/calendar_observer | v1.3.0 | IfNotPresent |
| influxdb | index.docker.io/invincibledocker24/influxdb | v1.3.0 | IfNotPresent |
| cleaninfluxdb | index.docker.io/invincibledocker24/cleaninfluxdb | v1.3.0 | IfNotPresent |
| grafana | index.docker.io/invincibledocker24/grafana | v1.3.0 | IfNotPresent |
| grafana-nginx | index.docker.io/invincibledocker24/grafana_nginx | v1.3.0 | IfNotPresent |
| insider_scheduler | index.docker.io/invincibledocker24/insider_scheduler | v1.3.0 | IfNotPresent |
| insider_worker | index.docker.io/invincibledocker24/insider_worker | v1.3.0 | IfNotPresent |
| insider_api | index.docker.io/invincibledocker24/insider_api | v1.3.0 | Always |
| slacker | index.docker.io/invincibledocker24/slacker | v1.3.0 | IfNotPresent |
| error_pages | index.docker.io/invincibledocker24/error_pages | v1.3.0 | IfNotPresent |
| metroculus_scheduler | index.docker.io/invincibledocker24/metroculus_scheduler | v1.3.0 | IfNotPresent |
| metroculus_worker | index.docker.io/invincibledocker24/metroculus_worker | v1.3.0 | Always |
| metroculus_api | index.docker.io/invincibledocker24/metroculus_api | v1.3.0 | Always |
| webhook_executor | index.docker.io/invincibledocker24/webhook_executor | v1.3.0 | IfNotPresent |
| slacker_executor | index.docker.io/invincibledocker24/slacker_executor | v1.3.0 | IfNotPresent |
| herald_executor | index.docker.io/invincibledocker24/herald_executor | v1.3.0 | IfNotPresent |
| keeper_executor | index.docker.io/invincibledocker24/keeper_executor | v1.3.0 | IfNotPresent |
| booking_observer | index.docker.io/invincibledocker24/booking_observer | v1.3.0 | IfNotPresent |
| organization_violations | index.docker.io/invincibledocker24/organization_violations | v1.3.0 | IfNotPresent |
| cleanmongodb | index.docker.io/invincibledocker24/cleanmongodb | v1.3.0 | IfNotPresent |
| trapper_scheduler | index.docker.io/invincibledocker24/trapper_scheduler | v1.3.0 | Always |
| trapper_worker | index.docker.io/invincibledocker24/trapper_worker | v1.3.0 | IfNotPresent |
| risp_scheduler | index.docker.io/invincibledocker24/risp_scheduler | v1.3.0 | IfNotPresent |
| risp_worker | index.docker.io/invincibledocker24/risp_worker | v1.3.0 | Always |
| gemini_scheduler | index.docker.io/invincibledocker24/gemini_scheduler | v1.3.0 | IfNotPresent |
| gemini_worker | index.docker.io/invincibledocker24/gemini_worker | v1.3.0 | IfNotPresent |
| bi_scheduler | index.docker.io/invincibledocker24/bi_scheduler | v1.3.0 | IfNotPresent |
| bi_exporter | index.docker.io/invincibledocker24/bi_exporter | v1.3.0 | IfNotPresent |
| failed_imports_dataset_generator | index.docker.io/invincibledocker24/failed_imports_dataset_generator | v1.3.0 | IfNotPresent |
| thanos-receive | index.docker.io/invincibledocker24/thanos-receive | v1.3.0 | IfNotPresent |
| thanos-storegateway | index.docker.io/invincibledocker24/thanos-storegateway | v1.3.0 | IfNotPresent |
| thanos-query | index.docker.io/invincibledocker24/thanos-query | v1.3.0 | IfNotPresent |
| thanos-compactor | index.docker.io/invincibledocker24/thanos-compactor | v1.3.0 | IfNotPresent |
| thanos-web | index.docker.io/invincibledocker24/thanos-web | v1.3.0 | IfNotPresent |
| diproxy | index.docker.io/invincibledocker24/diproxy | v1.3.0 | IfNotPresent |
| pharos_receiver | index.docker.io/invincibledocker24/pharos_receiver | v1.3.0 | IfNotPresent |
| pharos_worker | index.docker.io/invincibledocker24/pharos_worker | v1.3.0 | IfNotPresent |
| ohsu | index.docker.io/invincibledocker24/ohsu | v1.3.0 | IfNotPresent |
| users_dataset_generator | index.docker.io/invincibledocker24/users_dataset_generator | v1.3.0 | IfNotPresent |
| power_schedule | index.docker.io/invincibledocker24/power_schedule | v1.3.0 | Always |
| layout_cleaner | index.docker.io/invincibledocker24/layout_cleaner | v1.3.0 | IfNotPresent |
| monthly_bill_generator | index.docker.io/invincibledocker24/monthly_bill_generator | v1.3.0 | IfNotPresent |
| cleanelkdb | index.docker.io/invincibledocker24/cleanelkdb | v1.3.0 | IfNotPresent |
| currency_rate_updater | index.docker.io/invincibledocker24/rest_api | v1.3.0 | IfNotPresent |

## Version Exceptions

Services using non-standard tags:

| Service | Tag | Reason |
|---------|-----|--------|
| mongo | v1.3.0-dev | Development version |
| restapi (dev) | v1.3.0-co2 | CO2 feature version |
| ngui (dev) | v1.3.0-dev-chatbot | Chatbot integration version |
| diworker | v1.3.0-dev-4 | Development iteration 4 |
| katara_service | v1.3.0-dev | Development version |
| katara_worker | v1.3.0-dev | Development version |
| agentic-chatbot | v1.3.1 | Minor version ahead |
| mcp-mongo | 0.1.0 | Independent versioning |
| mcp-maria | 0.1.0 | Independent versioning |
| pgvector | pg17 | PostgreSQL 17 base |

## Pull Policy Summary

| Policy | Count | Services |
|--------|-------|----------|
| IfNotPresent | 66 | Most services |
| Always | 16 | Dev/frequently updated services |

## Notes
- Total services: 82
- Services using global tag (v1.3.0): 72
- Services with custom tags: 10
- External images (non-invincibledocker24): 1 (pgvector)
