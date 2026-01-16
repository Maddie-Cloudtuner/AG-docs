"""
Example: Predict tags for AWS resources
Demonstrates ML inference with schema validation
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ml_feature_extraction import SchemaValidatedInference
from db_utils import get_db_connection
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_predictions(resource, predictions):
    """Pretty print predictions"""
    print("\n" + "="*80)
    print(f"📦 Resource: {resource['name']}")
    print(f"   Provider: {resource['provider'].upper()}")
    print(f"   Type: {resource['resource_type']}")
    print(f"   Native Tags: {resource.get('native_tags', {})}")
    print("="*80)
    
    if not predictions:
        print("\n⚠️  No predictions generated")
        return
    
    print(f"\n🎯 Generated {len(predictions)} predictions:\n")
    
    for i, pred in enumerate(predictions, 1):
        # Confidence indicator
        if pred['confidence'] >= Config.ML_CONFIDENCE_AUTO_APPLY:
            badge = "✅ AUTO-APPLY"
            color = "\033[92m"  # Green
        elif pred['confidence'] >= Config.ML_CONFIDENCE_REVIEW:
            badge = "⚠️  REVIEW"
            color = "\033[93m"  # Yellow
        else:
            badge = "ℹ️  ALTERNATIVE"
            color = "\033[94m"  # Blue
        
        reset_color = "\033[0m"
        
        print(f"{i}. {color}{badge}{reset_color}")
        print(f"   Tag: {pred['tag_key']} = {pred['predicted_value']}")
        print(f"   Confidence: {pred['confidence']:.0%}")
        print(f"   Source: {pred['source']}")
        
        # Schema validation
        if 'schema_validation' in pred:
            schema = pred['schema_validation']
            print(f"   ✓ Schema Validated: {schema.get('tag_category', 'N/A')} tag")
        
        print(f"   Reasoning: {pred['reasoning'][:100]}...")
        print()


def example_well_tagged_resource():
    """Example 1: Well-tagged production resource"""
    print("\n" + "🔵"*40)
    print("EXAMPLE 1: Well-Tagged Production Resource")
    print("🔵"*40)
    
    resource = {
        "provider": "aws",
        "resource_type": "ec2",
        "name": "prod-backend-api-42",
        "native_tags": {
            "Environment": "Production",
            "Team": "backend",
            "CostCenter": "ENG"
        }
    }
    
    conn = get_db_connection()
    inference = SchemaValidatedInference(conn)
    
    predictions = inference.predict_tags(resource)
    print_predictions(resource, predictions)
    
    conn.close()


def example_minimal_tags():
    """Example 2: Minimal tags, rely on pattern matching"""
    print("\n" + "🟡"*40)
    print("EXAMPLE 2: Minimal Tags - Pattern Matching")
    print("🟡"*40)
    
    resource = {
        "provider": "aws",
        "resource_type": "ec2",
        "name": "staging-web-server-01",
        "native_tags": {}
    }
    
    conn = get_db_connection()
    inference = SchemaValidatedInference(conn)
    
    predictions = inference.predict_tags(resource)
    print_predictions(resource, predictions)
    
    conn.close()


def example_no_patterns():
    """Example 3: No patterns, use smart defaults"""
    print("\n" + "🟠"*40)
    print("EXAMPLE 3: No Patterns - Smart Defaults")
    print("🟠"*40)
    
    resource = {
        "provider": "gcp",
        "resource_type": "compute-engine",
        "name": "instance-xyz-123",
        "native_tags": {}
    }
    
    conn = get_db_connection()
    inference = SchemaValidatedInference(conn)
    
    predictions = inference.predict_tags(resource)
    print_predictions(resource, predictions)
    
    conn.close()


def example_database_resource():
    """Example 4: Database resource with specific scope"""
    print("\n" + "🟣"*40)
    print("EXAMPLE 4: Database Resource (Specific Scope)")
    print("🟣"*40)
    
    resource = {
        "provider": "aws",
        "resource_type": "rds",
        "name": "prod-mysql-db-primary",
        "native_tags": {
            "Environment": "prod",
            "DataClassification": "confidential"
        }
    }
    
    conn = get_db_connection()
    inference = SchemaValidatedInference(conn)
    
    predictions = inference.predict_tags(resource)
    print_predictions(resource, predictions)
    
    conn.close()


def example_custom_resource():
    """Example 5: Custom resource from user input"""
    print("\n" + "🟢"*40)
    print("EXAMPLE 5: Custom Resource (Interactive)")
    print("🟢"*40)
    
    print("\nEnter resource details:")
    provider = input("Provider (aws/gcp/azure) [aws]: ").strip() or "aws"
    resource_type = input("Resource type (ec2/s3/rds/etc) [ec2]: ").strip() or "ec2"
    name = input("Resource name [my-server]: ").strip() or "my-server"
    
    # Optional native tags
    native_tags = {}
    while True:
        add_tag = input("\nAdd native tag? (y/n) [n]: ").strip().lower()
        if add_tag != 'y':
            break
        tag_key = input("  Tag key: ").strip()
        tag_value = input("  Tag value: ").strip()
        if tag_key and tag_value:
            native_tags[tag_key] = tag_value
    
    resource = {
        "provider": provider,
        "resource_type": resource_type,
        "name": name,
        "native_tags": native_tags
    }
    
    conn = get_db_connection()
    inference = SchemaValidatedInference(conn)
    
    predictions = inference.predict_tags(resource)
    print_predictions(resource, predictions)
    
    conn.close()


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("🚀 ML INFERENCE EXAMPLES - Schema-Validated Predictions")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Database: {Config.DB_NAME}")
    print(f"  Auto-apply threshold: {Config.ML_CONFIDENCE_AUTO_APPLY:.0%}")
    print(f"  Review threshold: {Config.ML_CONFIDENCE_REVIEW:.0%}")
    
    # Run examples
    try:
        example_well_tagged_resource()
        example_minimal_tags()
        example_no_patterns()
        example_database_resource()
        
        # Interactive example
        interactive = input("\n\nRun interactive example? (y/n) [n]: ").strip().lower()
        if interactive == 'y':
            example_custom_resource()
        
        print("\n" + "="*80)
        print("✅ All examples completed successfully!")
        print("="*80)
        print("\nKey Takeaways:")
        print("  • All predictions are constrained to cloud_resource_tags schema")
        print("  • No hallucination - only values from allowed_values")
        print("  • Confidence-based auto-apply decision")
        print("  • Clear reasoning for every prediction")
        print("\n")
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
