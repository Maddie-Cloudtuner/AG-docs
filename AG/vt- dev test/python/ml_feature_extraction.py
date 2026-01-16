"""
ML Feature Extraction with cloud_resource_tags Schema Integration
==================================================================

This module implements schema-validated ML inference for virtual tagging.
All predictions are constrained to the cloud_resource_tags table.

Usage:
    from ml_feature_extraction import SchemaValidatedInference
    
    inference = SchemaValidatedInference(db_connection)
    predictions = inference.predict_tags(resource)
"""

import psycopg2
from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass


@dataclass
class TagSchema:
    """Represents a tag definition from cloud_resource_tags table"""
    id: int
    cloud_provider: str
    resource_scope: str
    tag_category: str
    tag_key: str
    value_type: str
    allowed_values: Optional[str]
    is_case_sensitive: bool
    description: str


class SchemaValidatedInference:
    """
    ML Inference engine that uses cloud_resource_tags as authoritative reference
    """
    
    # Resource type to scope mapping
    SCOPE_MAPPING = {
        # AWS
        'ec2': 'Compute', 'lambda': 'Compute', 'ecs': 'Compute',
        's3': 'Storage', 'ebs': 'Storage', 'efs': 'Storage',
        'rds': 'Database', 'dynamodb': 'Database', 'elasticache': 'Database',
        'vpc': 'Network', 'elb': 'Network', 'alb': 'Network', 'cloudfront': 'Network',
        
        # GCP
        'compute-engine': 'Compute', 'cloud-functions': 'Compute', 'gke': 'Compute',
        'cloud-storage': 'Storage', 'persistent-disk': 'Storage',
        'cloud-sql': 'Database', 'bigtable': 'Database', 'firestore': 'Database',
        'vpc-network': 'Network', 'cloud-load-balancer': 'Network',
        
        # Azure
        'virtual-machine': 'Compute', 'azure-functions': 'Compute', 'aks': 'Compute',
        'blob-storage': 'Storage', 'disk': 'Storage',
        'sql-database': 'Database', 'cosmos-db': 'Database',
        'virtual-network': 'Network', 'application-gateway': 'Network',
    }
    
    def __init__(self, db_connection):
        """
        Initialize with database connection
        
        Args:
            db_connection: psycopg2 connection to PostgreSQL database
        """
        self.conn = db_connection
        self.schema_cache = {}
    
    def get_valid_tags(self, provider: str, resource_scope: str) -> List[TagSchema]:
        """
        Query cloud_resource_tags table for applicable tags
        
        Args:
            provider: Cloud provider (aws, gcp, azure)
            resource_scope: Resource scope (Global, Compute, Database, Storage, Network)
        
        Returns:
            List of TagSchema objects ordered by category priority
        """
        cache_key = f"{provider}:{resource_scope}"
        if cache_key in self.schema_cache:
            return self.schema_cache[cache_key]
        
        cursor = self.conn.cursor()
        query = """
            SELECT id, cloud_provider, resource_scope, tag_category, tag_key,
                   value_type, allowed_values, is_case_sensitive, description
            FROM cloud_resource_tags
            WHERE cloud_provider IN (%s, 'All')
              AND resource_scope IN (%s, 'Global')
            ORDER BY 
                CASE tag_category 
                    WHEN 'Critical' THEN 1
                    WHEN 'Non-Critical' THEN 2
                    WHEN 'Optional' THEN 3
                END,
                tag_key
        """
        
        cursor.execute(query, (provider, resource_scope))
        
        tags = []
        for row in cursor.fetchall():
            tags.append(TagSchema(
                id=row[0],
                cloud_provider=row[1],
                resource_scope=row[2],
                tag_category=row[3],
                tag_key=row[4],
                value_type=row[5],
                allowed_values=row[6],
                is_case_sensitive=row[7],
                description=row[8]
            ))
        
        cursor.close()
        self.schema_cache[cache_key] = tags
        return tags
    
    def _get_resource_scope(self, resource_type: str) -> str:
        """Map resource type to scope"""
        return self.SCOPE_MAPPING.get(resource_type.lower(), 'Global')
    
    def validate_native_tag(
        self, 
        native_key: str, 
        native_value: str, 
        valid_tags: List[TagSchema]
    ) -> Optional[Dict]:
        """
        Validate and normalize a native cloud tag against schema
        
        Args:
            native_key: Original tag key from cloud provider
            native_value: Original tag value
            valid_tags: List of valid TagSchema objects
        
        Returns:
            Prediction dict if valid, None otherwise
        """
        # Find matching tag in schema (case-insensitive key match)
        schema_tag = next(
            (t for t in valid_tags if t.tag_key.lower() == native_key.lower()),
            None
        )
        
        if not schema_tag:
            return None
        
        normalized_value = native_value
        
        # Validate Enum types against allowed_values
        if schema_tag.value_type == 'Enum' and schema_tag.allowed_values:
            allowed = [v.strip() for v in schema_tag.allowed_values.split(',')]
            
            if schema_tag.is_case_sensitive:
                # Exact match required
                if normalized_value not in allowed:
                    # Try to normalize common variations
                    matches = [v for v in allowed if v.lower() == normalized_value.lower()]
                    if matches:
                        normalized_value = matches[0]
                    else:
                        return None  # Invalid value
            else:
                # Case-insensitive match
                normalized_value = next(
                    (v for v in allowed if v.lower() == normalized_value.lower()),
                    None
                )
                if not normalized_value:
                    return None
        
        # Validate Boolean type
        if schema_tag.value_type == 'Boolean':
            bool_map = {
                'true': 'true', 'false': 'false',
                'yes': 'true', 'no': 'false',
                '1': 'true', '0': 'false'
            }
            normalized_value = bool_map.get(normalized_value.lower(), normalized_value.lower())
        
        return {
            'tag_key': schema_tag.tag_key,
            'predicted_value': normalized_value,
            'confidence': 0.98,
            'source': 'NORMALIZED',
            'reasoning': f"Normalized from native tag '{native_key}'. {schema_tag.description}",
            'schema_validation': {
                'schema_id': schema_tag.id,
                'is_valid': True,
                'tag_category': schema_tag.tag_category,
                'value_type': schema_tag.value_type,
                'case_sensitive': schema_tag.is_case_sensitive
            },
            'features_used': {
                'native_tag_key': native_key,
                'native_tag_value': native_value
            }
        }
    
    def pattern_match_with_schema(
        self,
        resource_name: str,
        valid_tags: List[TagSchema]
    ) -> List[Dict]:
        """
        Pattern matching constrained to schema-defined Enum values
        
        Args:
            resource_name: Resource name to search for patterns
            valid_tags: List of valid TagSchema objects
        
        Returns:
            List of prediction dicts
        """
        predictions = []
        predicted_keys = set()
        
        for tag_schema in valid_tags:
            if tag_schema.tag_key in predicted_keys:
                continue  # Already predicted this tag
            
            if tag_schema.value_type != 'Enum' or not tag_schema.allowed_values:
                continue  # Only pattern match for Enum types
            
            allowed_values = [v.strip() for v in tag_schema.allowed_values.split(',')]
            
            # Check if any allowed value appears in resource name
            for value in allowed_values:
                # Build search pattern
                if tag_schema.is_case_sensitive:
                    pattern = value
                    search_in = resource_name
                else:
                    pattern = value.lower()
                    search_in = resource_name.lower()
                
                # Use word boundary for more accurate matching
                if re.search(rf'\b{re.escape(pattern)}\b', search_in):
                    # Calculate confidence based on category
                    confidence_map = {
                        'Critical': 0.95,
                        'Non-Critical': 0.85,
                        'Optional': 0.75
                    }
                    confidence = confidence_map.get(tag_schema.tag_category, 0.80)
                    
                    predictions.append({
                        'tag_key': tag_schema.tag_key,
                        'predicted_value': value,
                        'confidence': confidence,
                        'source': 'PATTERN_MATCH',
                        'reasoning': f"Resource name contains '{value}' keyword. {tag_schema.description}",
                        'schema_validation': {
                            'schema_id': tag_schema.id,
                            'is_valid': True,
                            'tag_category': tag_schema.tag_category,
                            'value_type': 'Enum'
                        },
                        'features_used': {
                            'resource_name': resource_name,
                            'matched_pattern': pattern
                        }
                    })
                    
                    predicted_keys.add(tag_schema.tag_key)
                    break  # Only predict one value per tag
        
        return predictions
    
    def apply_smart_defaults(
        self,
        predicted_tags: List[Dict],
        valid_tags: List[TagSchema],
        resource: Dict
    ) -> List[Dict]:
        """
        Apply category-based intelligent defaults for missing Critical tags
        
        Args:
            predicted_tags: Already predicted tags
            valid_tags: List of valid TagSchema objects
            resource: Resource metadata dict
        
        Returns:
            List of default prediction dicts
        """
        predicted_keys = {p['tag_key'] for p in predicted_tags}
        
        # Only apply defaults for Critical tags
        critical_tags = [
            t for t in valid_tags 
            if t.tag_category == 'Critical' and t.tag_key not in predicted_keys
        ]
        
        defaults = []
        
        for tag_schema in critical_tags:
            default_value = None
            confidence = 0.60
            reasoning = ""
            
            # Environment defaults
            if tag_schema.tag_key.lower() == 'environment':
                # Safer to default to development
                allowed = [v.strip() for v in tag_schema.allowed_values.split(',')] if tag_schema.allowed_values else []
                default_value = next((v for v in allowed if 'dev' in v.lower()), 'development')
                reasoning = "Default to development environment (safer assumption for untagged resources)"
            
            # Cost-center defaults (derive from environment)
            elif 'cost' in tag_schema.tag_key.lower() and 'center' in tag_schema.tag_key.lower():
                env_tag = next((p for p in predicted_tags if 'environment' in p['tag_key'].lower()), None)
                if env_tag and 'prod' in env_tag['predicted_value'].lower():
                    default_value = 'production-ops'
                    confidence = 0.85
                    reasoning = "Derived from production environment"
                else:
                    default_value = 'engineering'
                    confidence = 0.65
                    reasoning = "Default cost center for non-production resources"
            
            # Owner defaults (derive from team if available)
            elif tag_schema.tag_key.lower() == 'owner':
                team_tag = next((p for p in predicted_tags if 'team' in p['tag_key'].lower()), None)
                if team_tag:
                    default_value = f"{team_tag['predicted_value']}-team@company.com"
                    confidence = 0.75
                    reasoning = f"Derived from team '{team_tag['predicted_value']}'"
            
            if default_value:
                defaults.append({
                    'tag_key': tag_schema.tag_key,
                    'predicted_value': default_value,
                    'confidence': confidence,
                    'source': 'SMART_DEFAULT',
                    'reasoning': f"{reasoning}. {tag_schema.description}",
                    'schema_validation': {
                        'schema_id': tag_schema.id,
                        'is_valid': True,
                        'tag_category': 'Critical'
                    },
                    'features_used': {
                        'derived_from': [p['tag_key'] for p in predicted_tags]
                    }
                })
        
        return defaults
    
    def predict_tags(self, resource: Dict) -> List[Dict]:
        """
        Main entry point: Predict virtual tags for a resource
        
        Args:
            resource: Dict with keys:
                - provider: str (aws, gcp, azure)
                - resource_type: str (ec2, s3, rds, etc.)
                - name: str
                - native_tags: Dict[str, str]
        
        Returns:
            List of prediction dicts with schema validation
        """
        provider = resource.get('provider', '').lower()
        resource_type = resource.get('resource_type', '').lower()
        resource_name = resource.get('name', '')
        native_tags = resource.get('native_tags', {})
        
        # Step 1: Determine resource scope
        resource_scope = self._get_resource_scope(resource_type)
        
        # Step 2: Get valid tags from schema
        valid_tags = self.get_valid_tags(provider, resource_scope)
        
        if not valid_tags:
            return []  # No schema defined for this resource
        
        predictions = []
        
        # Step 3: Validate and normalize native tags
        for native_key, native_value in native_tags.items():
            prediction = self.validate_native_tag(native_key, native_value, valid_tags)
            if prediction:
                predictions.append(prediction)
        
        # Step 4: Schema-constrained pattern matching
        pattern_predictions = self.pattern_match_with_schema(resource_name, valid_tags)
        
        # Only add pattern predictions if not already predicted from native tags
        predicted_keys = {p['tag_key'] for p in predictions}
        for pred in pattern_predictions:
            if pred['tag_key'] not in predicted_keys:
                predictions.append(pred)
        
        # Step 5: Apply smart defaults for missing Critical tags
        default_predictions = self.apply_smart_defaults(predictions, valid_tags, resource)
        predictions.extend(default_predictions)
        
        # Sort by confidence (highest first)
        predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return predictions


# Example usage
if __name__ == "__main__":
    # Connect to database
    conn = psycopg2.connect(
        dbname="cloudtuner_db",
        user="postgres",
        password="your_password",
        host="localhost",
        port=5432
    )
    
    # Initialize inference engine
    inference = SchemaValidatedInference(conn)
    
    # Example resource
    resource = {
        "provider": "aws",
        "resource_type": "ec2",
        "name": "prod-backend-api-42",
        "native_tags": {
            "Team": "backend",
            "CostCenter": "ENG"
        }
    }
    
    # Predict tags
    predictions = inference.predict_tags(resource)
    
    # Print results
    print(f"\nPredictions for {resource['name']}:\n")
    for pred in predictions:
        auto_apply = "✅ AUTO-APPLY" if pred['confidence'] >= 0.90 else "⚠️ REVIEW"
        print(f"{auto_apply} | {pred['tag_key']} = {pred['predicted_value']}")
        print(f"   Confidence: {pred['confidence']:.0%} | Source: {pred['source']}")
        print(f"   Reasoning: {pred['reasoning']}\n")
    
    conn.close()
