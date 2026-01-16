"""
Test Suite for Schema-Validated ML Inference
=============================================

Run this script to test the ML inference integration with cloud_resource_tags
"""

import sys
sys.path.append('.')  # Add current directory to path

from ml_feature_extraction import SchemaValidatedInference, TagSchema
import psycopg2
from typing import List


class MockDatabase:
    """Mock database for testing without actual DB connection"""
    
    def __init__(self):
        self.mock_tags = self._create_mock_schema()
    
    def _create_mock_schema(self) -> List[TagSchema]:
        """Create mock cloud_resource_tags data"""
        return [
            # Critical Tags
            TagSchema(
                id=1,
                cloud_provider='All',
                resource_scope='Global',
                tag_category='Critical',
                tag_key='environment',
                value_type='Enum',
                allowed_values='dev, staging, prod, testing',
                is_case_sensitive=True,
                description='Deployment environment classification'
            ),
            TagSchema(
                id=2,
                cloud_provider='All',
                resource_scope='Global',
                tag_category='Critical',
                tag_key='cost-center',
                value_type='String',
                allowed_values=None,
                is_case_sensitive=False,
                description='Financial cost center for allocation'
            ),
            TagSchema(
                id=3,
                cloud_provider='All',
                resource_scope='Global',
                tag_category='Critical',
                tag_key='owner',
                value_type='String',
                allowed_values=None,
                is_case_sensitive=False,
                description='Resource owner'
            ),
            
            # Non-Critical Tags
            TagSchema(
                id=4,
                cloud_provider='AWS',
                resource_scope='Compute',
                tag_category='Non-Critical',
                tag_key='instance-role',
                value_type='Enum',
                allowed_values='web-server, app-server, database, worker',
                is_case_sensitive=True,
                description='AWS EC2 instance role'
            ),
            TagSchema(
                id=5,
                cloud_provider='All',
                resource_scope='Global',
                tag_category='Non-Critical',
                tag_key='team',
                value_type='Enum',
                allowed_values='frontend, backend, data, devops',
                is_case_sensitive=False,
                description='Team ownership'
            ),
            
            # Optional Tags
            TagSchema(
                id=6,
                cloud_provider='All',
                resource_scope='Compute',
                tag_category='Optional',
                tag_key='auto-shutdown',
                value_type='Boolean',
                allowed_values=None,
                is_case_sensitive=False,
                description='Auto-shutdown during off-hours'
            ),
        ]
    
    def cursor(self):
        return MockCursor(self.mock_tags)
    
    def close(self):
        pass


class MockCursor:
    """Mock cursor for testing"""
    
    def __init__(self, mock_tags):
        self.mock_tags = mock_tags
        self.results = []
    
    def execute(self, query, params=None):
        """Simulate query execution"""
        if params:
            provider, resource_scope = params
            # Filter tags by provider and scope
            self.results = [
                (t.id, t.cloud_provider, t.resource_scope, t.tag_category,
                 t.tag_key, t.value_type, t.allowed_values, t.is_case_sensitive,
                 t.description)
                for t in self.mock_tags
                if (t.cloud_provider == provider or t.cloud_provider == 'All')
                and (t.resource_scope == resource_scope or t.resource_scope == 'Global')
            ]
    
    def fetchall(self):
        return self.results
    
    def close(self):
        pass


def test_native_tag_validation():
    """Test native tag normalization"""
    print("\n" + "="*60)
    print("TEST 1: Native Tag Validation")
    print("="*60)
    
    db = MockDatabase()
    inference = SchemaValidatedInference(db)
    
    valid_tags = db.mock_tags
    
    # Test case 1: Valid environment tag
    result = inference.validate_native_tag('Environment', 'prod', valid_tags)
    assert result is not None, "Should validate 'prod'"
    assert result['predicted_value'] == 'prod'
    assert result['confidence'] == 0.98
    print("✅ Test 1.1 passed: Valid enum value")
    
    # Test case 2: Case normalization
    result = inference.validate_native_tag('Environment', 'PROD', valid_tags)
    assert result is not None, "Should normalize 'PROD' to 'prod'"
    assert result['predicted_value'] == 'prod'
    print("✅ Test 1.2 passed: Case normalization")
    
    # Test case 3: Invalid value
    result = inference.validate_native_tag('Environment', 'production', valid_tags)
    assert result is None, "Should reject 'production' (not in allowed values)"
    print("✅ Test 1.3 passed: Invalid value rejected")
    
    # Test case 4: Team tag (case-insensitive)
    result = inference.validate_native_tag('Team', 'BACKEND', valid_tags)
    assert result is not None
    assert result['predicted_value'] == 'backend'  # Normalized to lowercase
    print("✅ Test 1.4 passed: Case-insensitive normalization")
    
    print("\n✅ All native tag validation tests passed!\n")


def test_pattern_matching():
    """Test schema-constrained pattern matching"""
    print("="*60)
    print("TEST 2: Pattern Matching")
    print("="*60)
    
    db = MockDatabase()
    inference = SchemaValidatedInference(db)
    
    valid_tags = db.mock_tags
    
    # Test case 1: Environment pattern match
    predictions = inference.pattern_match_with_schema('prod-api-server', valid_tags)
    env_pred = next((p for p in predictions if p['tag_key'] == 'environment'), None)
    assert env_pred is not None, "Should detect 'prod' in resource name"
    assert env_pred['predicted_value'] == 'prod'
    assert env_pred['confidence'] == 0.95  # Critical tag
    print("✅ Test 2.1 passed: Environment pattern matched")
    
    # Test case 2: Team pattern match
    predictions = inference.pattern_match_with_schema('backend-service-01', valid_tags)
    team_pred = next((p for p in predictions if p['tag_key'] == 'team'), None)
    assert team_pred is not None
    assert team_pred['predicted_value'] == 'backend'
    print("✅ Test 2.2 passed: Team pattern matched")
    
    # Test case 3: No pattern match
    predictions = inference.pattern_match_with_schema('random-server-xyz', valid_tags)
    assert len(predictions) == 0, "Should not match any patterns"
    print("✅ Test 2.3 passed: No false positives")
    
    print("\n✅ All pattern matching tests passed!\n")


def test_smart_defaults():
    """Test intelligent default application"""
    print("="*60)
    print("TEST 3: Smart Defaults")
    print("="*60)
    
    db = MockDatabase()
    inference = SchemaValidatedInference(db)
    
    valid_tags = db.mock_tags
    
    # Test case 1: Default environment
    predicted_tags = []  # No predictions yet
    resource = {'provider': 'aws', 'resource_type': 'ec2'}
    
    defaults = inference.apply_smart_defaults(predicted_tags, valid_tags, resource)
    env_default = next((d for d in defaults if 'environment' in d['tag_key'].lower()), None)
    assert env_default is not None
    assert 'dev' in env_default['predicted_value'].lower()
    print("✅ Test 3.1 passed: Default environment is dev")
    
    # Test case 2: Cost-center derived from environment
    predicted_tags = [{
        'tag_key': 'environment',
        'predicted_value': 'prod',
        'confidence': 0.95
    }]
    
    defaults = inference.apply_smart_defaults(predicted_tags, valid_tags, resource)
    cc_default = next((d for d in defaults if 'cost-center' in d['tag_key'].lower()), None)
    assert cc_default is not None
    assert 'production' in cc_default['predicted_value'].lower()
    assert cc_default['confidence'] == 0.85
    print("✅ Test 3.2 passed: Cost-center derived from prod environment")
    
    # Test case 3: Owner derived from team
    predicted_tags = [{
        'tag_key': 'team',
        'predicted_value': 'backend',
        'confidence': 0.98
    }]
    
    defaults = inference.apply_smart_defaults(predicted_tags, valid_tags, resource)
    owner_default = next((d for d in defaults if 'owner' in d['tag_key'].lower()), None)
    assert owner_default is not None
    assert 'backend-team@company.com' in owner_default['predicted_value']
    print("✅ Test 3.3 passed: Owner derived from team")
    
    print("\n✅ All smart defaults tests passed!\n")


def test_complete_inference():
    """Test end-to-end inference"""
    print("="*60)
    print("TEST 4: Complete Inference Workflow")
    print("="*60)
    
    db = MockDatabase()
    inference = SchemaValidatedInference(db)
    
    # Test resource 1: Well-tagged production resource
    resource1 = {
        'provider': 'aws',
        'resource_type': 'ec2',
        'name': 'prod-backend-api-42',
        'native_tags': {
            'Environment': 'prod',
            'Team': 'backend',
            'CostCenter': 'engineering'
        }
    }
    
    predictions1 = inference.predict_tags(resource1)
    
    assert len(predictions1) >= 3, "Should have at least 3 predictions"
    
    # Check environment (from native tag)
    env_pred = next((p for p in predictions1 if p['tag_key'] == 'environment'), None)
    assert env_pred is not None
    assert env_pred['predicted_value'] == 'prod'
    assert env_pred['source'] == 'NORMALIZED'
    assert env_pred['confidence'] == 0.98
    print("✅ Resource 1: Environment normalized from native tag")
    
    # Check team (from native tag)
    team_pred = next((p for p in predictions1 if p['tag_key'] == 'team'), None)
    assert team_pred is not None
    assert team_pred['predicted_value'] == 'backend'
    print("✅ Resource 1: Team normalized from native tag")
    
    # Check owner (smart default from team)
    owner_pred = next((p for p in predictions1 if p['tag_key'] == 'owner'), None)
    assert owner_pred is not None
    assert 'backend-team@company.com' in owner_pred['predicted_value']
    assert owner_pred['source'] == 'SMART_DEFAULT'
    print("✅ Resource 1: Owner derived as smart default")
    
    print("\n" + "-"*60)
    
    # Test resource 2: Minimal tags, rely on pattern matching
    resource2 = {
        'provider': 'aws',
        'resource_type': 'ec2',
        'name': 'staging-web-server-01',
        'native_tags': {}
    }
    
    predictions2 = inference.predict_tags(resource2)
    
    # Should detect 'staging' from name
    env_pred2 = next((p for p in predictions2 if p['tag_key'] == 'environment'), None)
    assert env_pred2 is not None
    assert env_pred2['predicted_value'] == 'staging'
    assert env_pred2['source'] == 'PATTERN_MATCH'
    print("✅ Resource 2: Environment detected from resource name")
    
    # Should have cost-center default
    cc_pred2 = next((p for p in predictions2 if 'cost-center' in p['tag_key'].lower()), None)
    assert cc_pred2 is not None
    assert cc_pred2['source'] == 'SMART_DEFAULT'
    print("✅ Resource 2: Cost-center applied as default")
    
    print("\n✅ All complete inference tests passed!\n")


def test_confidence_scoring():
    """Test confidence calculation"""
    print("="*60)
    print("TEST 5: Confidence Scoring")
    print("="*60)
    
    db = MockDatabase()
    inference = SchemaValidatedInference(db)
    
    resource = {
        'provider': 'aws',
        'resource_type': 'ec2',
        'name': 'prod-backend',
        'native_tags': {'Environment': 'prod'}
    }
    
    predictions = inference.predict_tags(resource)
    
    # Native tag should have highest confidence
    env_pred = next(p for p in predictions if p['tag_key'] == 'environment')
    assert env_pred['confidence'] == 0.98, "Native tag should be 98%"
    print("✅ Native tag confidence: 98%")
    
    # Pattern match should have high confidence for Critical tags
    resource2 = {
        'provider': 'aws',
        'resource_type': 'ec2',
        'name': 'staging-api',
        'native_tags': {}
    }
    predictions2 = inference.predict_tags(resource2)
    env_pred2 = next((p for p in predictions2 if p['tag_key'] == 'environment'), None)
    if env_pred2:
        assert env_pred2['confidence'] == 0.95, "Pattern match for Critical should be 95%"
        print("✅ Pattern match (Critical) confidence: 95%")
    
    print("\n✅ All confidence scoring tests passed!\n")


def run_all_tests():
    """Run all test suites"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║  ML INFERENCE SCHEMA INTEGRATION - TEST SUITE".center(60) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_native_tag_validation()
        test_pattern_matching()
        test_smart_defaults()
        test_complete_inference()
        test_confidence_scoring()
        
        print("\n" + "="*60)
        print("✅✅✅ ALL TESTS PASSED! ✅✅✅")
        print("="*60)
        print("\nML inference is correctly integrated with cloud_resource_tags schema.")
        print("Ready for production use with your Excel data.\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
