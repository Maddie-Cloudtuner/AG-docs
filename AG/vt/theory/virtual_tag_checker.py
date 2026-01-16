"""
Virtual Tag Checker - Implementation for CloudTuner Virtual Tagging System
===========================================================================

This script handles the "Check Native Tag" step in the Virtual Tagging workflow:
- YES path: Resource has native tags → Match against schema
- NO path: Resource has NO native tags → Pattern matching + Resource type inference

Usage:
    python virtual_tag_checker.py

Requirements:
    pip install pandas openpyxl
"""

import pandas as pd
import base64
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


# =============================================================================
# DATA MODELS
# =============================================================================

class MatchType(Enum):
    EXACT = "EXACT"                       # Key and value both match exactly
    NORMALIZED_VALUE = "NORMALIZED_VALUE"  # Key matches, value normalized
    FUZZY_KEY = "FUZZY_KEY"               # Key matched via fuzzy/case-insensitive
    PATTERN_INFERRED = "PATTERN_INFERRED"  # Inferred from resource name pattern
    RESOURCE_TYPE_INFERRED = "RESOURCE_TYPE_INFERRED"  # Inferred from resource type
    RULE_BASED = "RULE_BASED"             # Applied via business rule


class TagCategory(Enum):
    CRITICAL = "Critical"
    NON_CRITICAL = "Non-Critical"
    OPTIONAL = "Optional"


@dataclass
class TagMatch:
    """Represents a matched/inferred tag"""
    native_key: Optional[str]        # Original key from cloud (None if inferred)
    native_value: Optional[str]      # Original value from cloud (None if inferred)
    virtual_key: str                 # Standardized/matched key
    virtual_value: str               # Standardized/matched value
    match_type: MatchType
    confidence: float                # 0.0 to 1.0
    category: str                    # Critical, Non-Critical, Optional
    reasoning: str                   # Why this match was made


@dataclass
class ResourceTagResult:
    """Complete tagging result for a resource"""
    resource_id: str
    resource_name: str
    resource_type: str
    service_name: str
    region: str
    has_native_tags: bool
    path_taken: str                  # "YES" or "NO" 
    matches: List[TagMatch] = field(default_factory=list)
    overall_confidence: float = 0.0
    decision: str = ""               # AUTO_APPROVE, PENDING, SUGGESTION, REJECT


# =============================================================================
# SCHEMA INDEX BUILDER
# =============================================================================

class TagSchemaIndex:
    """
    Pre-computed index for fast tag lookups.
    Converts O(n) scans to O(1) hash lookups.
    """
    
    def __init__(self, schema_df: pd.DataFrame):
        self.key_lookup: Dict[str, Dict] = {}           # tag_key → info
        self.value_lookup: Dict[Tuple[str, str], Dict] = {}  # (key, value) → info
        self.key_variations: Dict[str, List[str]] = {}  # lowercase → originals
        self.all_values_by_key: Dict[str, set] = {}     # key → set of valid values
        
        self._build_index(schema_df)
    
    def _build_index(self, df: pd.DataFrame):
        """Build lookup indexes from schema dataframe"""
        for _, row in df.iterrows():
            key = str(row['tag_key'])
            value = str(row['tag_value'])
            category = str(row['tag_category'])
            case_sensitive = bool(row['is_case_sensitive']) if pd.notna(row['is_case_sensitive']) else True
            
            # Key lookup
            if key not in self.key_lookup:
                self.key_lookup[key] = {
                    'category': category,
                    'case_sensitive': case_sensitive,
                    'values': set()
                }
            self.key_lookup[key]['values'].add(value)
            
            # Value lookup
            self.value_lookup[(key, value)] = {
                'category': category,
                'is_valid': True
            }
            
            # Case-insensitive variations
            lower_key = key.lower()
            if lower_key not in self.key_variations:
                self.key_variations[lower_key] = []
            if key not in self.key_variations[lower_key]:
                self.key_variations[lower_key].append(key)
            
            # All values by key
            if key not in self.all_values_by_key:
                self.all_values_by_key[key] = set()
            self.all_values_by_key[key].add(value)
    
    def find_key(self, native_key: str) -> Optional[Tuple[str, Dict, str]]:
        """
        Find matching schema key for a native tag key.
        Returns: (canonical_key, key_info, match_type) or None
        """
        # Try exact match first
        if native_key in self.key_lookup:
            return (native_key, self.key_lookup[native_key], 'EXACT')
        
        # Try case-insensitive match
        lower_key = native_key.lower()
        if lower_key in self.key_variations:
            canonical = self.key_variations[lower_key][0]
            return (canonical, self.key_lookup[canonical], 'FUZZY')
        
        return None
    
    def is_valid_value(self, key: str, value: str) -> bool:
        """Check if value is valid for given key"""
        return (key, value) in self.value_lookup
    
    def get_valid_values(self, key: str) -> set:
        """Get all valid values for a key"""
        return self.all_values_by_key.get(key, set())


# =============================================================================
# BASE64 TAG DECODER
# =============================================================================

class TagDecoder:
    """Handles decoding of Base64 encoded tag column names"""
    
    def __init__(self, df: pd.DataFrame):
        self.column_mapping: Dict[str, str] = {}  # encoded_column → decoded_key
        self.tag_columns: List[str] = []          # List of tag columns
        
        self._decode_columns(df)
    
    def _decode_columns(self, df: pd.DataFrame):
        """Decode all tag column names"""
        for col in df.columns:
            if col.startswith('tags.'):
                self.tag_columns.append(col)
                encoded = col.replace('tags.', '')
                try:
                    decoded = base64.b64decode(encoded).decode('utf-8')
                    self.column_mapping[col] = decoded
                except Exception:
                    # If decode fails, use original
                    self.column_mapping[col] = encoded
    
    def get_decoded_key(self, column: str) -> str:
        """Get decoded key name for a column"""
        return self.column_mapping.get(column, column)
    
    def get_tag_columns(self) -> List[str]:
        """Get list of all tag columns"""
        return self.tag_columns


# =============================================================================
# PATTERN MATCHING (NO PATH)
# =============================================================================

class PatternMatcher:
    """
    Pattern matching for resources WITHOUT native tags.
    Infers tags from resource name and metadata.
    """
    
    # Common patterns to detect from resource names
    ENVIRONMENT_PATTERNS = {
        r'[-_]prod[-_]|[-_]production[-_]|^prod[-_]|[-_]prod$': ('Environment', 'prod', 0.90),
        r'[-_]stag[-_]|[-_]staging[-_]|^stag[-_]|[-_]stag$': ('Environment', 'staging', 0.88),
        r'[-_]dev[-_]|[-_]development[-_]|^dev[-_]|[-_]dev$': ('Environment', 'dev', 0.85),
        r'[-_]test[-_]|[-_]testing[-_]|^test[-_]|[-_]test$': ('Environment', 'testing', 0.85),
        r'[-_]qa[-_]|^qa[-_]|[-_]qa$': ('Environment', 'testing', 0.80),
        r'[-_]uat[-_]|^uat[-_]|[-_]uat$': ('Environment', 'staging', 0.80),
    }
    
    # Application patterns
    APPLICATION_PATTERNS = {
        r'web[-_]?api|api[-_]?gateway|rest[-_]?api': ('Application', 'web-api', 0.75),
        r'data[-_]?pipeline|etl|data[-_]?flow': ('Application', 'data-pipeline', 0.75),
        r'ml[-_]?model|machine[-_]?learning|ai[-_]': ('Application', 'ml-model', 0.75),
        r'monitoring|observability|metrics': ('Application', 'monitoring', 0.70),
        r'auth[-_]?service|authentication|oauth': ('Application', 'auth-service', 0.75),
        r'lambda|serverless|function': ('Application', 'serverless', 0.70),
    }
    
    # Team/Owner patterns
    TEAM_PATTERNS = {
        r'platform|infra': ('Team', 'platform', 0.65),
        r'devops|sre|ops': ('Team', 'devops', 0.65),
        r'data[-_]?team|analytics': ('Team', 'data', 0.65),
        r'frontend|ui[-_]|web[-_]': ('Team', 'frontend', 0.60),
        r'backend|api[-_]': ('Team', 'backend', 0.60),
    }
    
    def match_patterns(self, resource_name: str, resource_type: str, service_name: str) -> List[TagMatch]:
        """
        Extract tag suggestions from resource name using pattern matching.
        This is the "NO" path in the workflow.
        """
        matches = []
        name_lower = (resource_name or '').lower()
        
        # Check environment patterns
        for pattern, (key, value, conf) in self.ENVIRONMENT_PATTERNS.items():
            if re.search(pattern, name_lower, re.IGNORECASE):
                matches.append(TagMatch(
                    native_key=None,
                    native_value=None,
                    virtual_key=key,
                    virtual_value=value,
                    match_type=MatchType.PATTERN_INFERRED,
                    confidence=conf,
                    category='Critical',
                    reasoning=f"Pattern '{pattern}' found in resource name"
                ))
                break  # Only one environment
        
        # Check application patterns
        for pattern, (key, value, conf) in self.APPLICATION_PATTERNS.items():
            if re.search(pattern, name_lower, re.IGNORECASE):
                matches.append(TagMatch(
                    native_key=None,
                    native_value=None,
                    virtual_key=key,
                    virtual_value=value,
                    match_type=MatchType.PATTERN_INFERRED,
                    confidence=conf,
                    category='Critical',
                    reasoning=f"Pattern '{pattern}' found in resource name"
                ))
                break  # Only one application type
        
        # Check team patterns
        for pattern, (key, value, conf) in self.TEAM_PATTERNS.items():
            if re.search(pattern, name_lower, re.IGNORECASE):
                matches.append(TagMatch(
                    native_key=None,
                    native_value=None,
                    virtual_key=key,
                    virtual_value=value,
                    match_type=MatchType.PATTERN_INFERRED,
                    confidence=conf,
                    category='Non-Critical',
                    reasoning=f"Pattern '{pattern}' found in resource name"
                ))
                break
        
        return matches


# =============================================================================
# RESOURCE TYPE INFERENCE
# =============================================================================

class ResourceTypeInferrer:
    """
    Infer tags based on resource type and service name.
    Part of the "NO" path in the workflow.
    """
    
    # Resource type to suggested tags mapping
    RESOURCE_TYPE_RULES = {
        'Instance': [
            ('ManagedBy', 'compute', 0.70, 'Optional'),
            ('BackupRequired', 'true', 0.60, 'Non-Critical'),
        ],
        'Volume': [
            ('BackupRequired', 'true', 0.75, 'Non-Critical'),
            ('StorageClass', 'standard', 0.50, 'Optional'),
        ],
        'Bucket': [
            ('StorageClass', 'standard', 0.60, 'Optional'),
            ('Versioning', 'enabled', 0.50, 'Optional'),
        ],
        'Serverless': [
            ('ManagedBy', 'serverless', 0.80, 'Optional'),
        ],
        'Snapshot': [
            ('BackupRequired', 'archive', 0.70, 'Non-Critical'),
        ],
        'Load Balancer': [
            ('NetworkTier', 'public', 0.65, 'Optional'),
        ],
    }
    
    # Service name to suggested tags
    SERVICE_RULES = {
        'AmazonEC2': [('Department', 'Engineering', 0.55, 'Non-Critical')],
        'AmazonS3': [('Department', 'Engineering', 0.55, 'Non-Critical')],
        'AWSLambda': [('Department', 'Engineering', 0.55, 'Non-Critical')],
        'AmazonRDS': [
            ('Department', 'Engineering', 0.55, 'Non-Critical'),
            ('BackupRequired', 'true', 0.80, 'Non-Critical'),
        ],
        'Vertex AI': [('Application', 'ml-model', 0.70, 'Critical')],
        'BigQuery': [('Application', 'data-pipeline', 0.65, 'Critical')],
    }
    
    def infer_from_resource_type(self, resource_type: str, service_name: str) -> List[TagMatch]:
        """Infer tags based on resource type and service"""
        matches = []
        
        # Check resource type rules
        if resource_type in self.RESOURCE_TYPE_RULES:
            for key, value, conf, category in self.RESOURCE_TYPE_RULES[resource_type]:
                matches.append(TagMatch(
                    native_key=None,
                    native_value=None,
                    virtual_key=key,
                    virtual_value=value,
                    match_type=MatchType.RESOURCE_TYPE_INFERRED,
                    confidence=conf,
                    category=category,
                    reasoning=f"Inferred from resource type: {resource_type}"
                ))
        
        # Check service rules
        if service_name in self.SERVICE_RULES:
            for key, value, conf, category in self.SERVICE_RULES[service_name]:
                # Don't duplicate if already added
                existing_keys = [m.virtual_key for m in matches]
                if key not in existing_keys:
                    matches.append(TagMatch(
                        native_key=None,
                        native_value=None,
                        virtual_key=key,
                        virtual_value=value,
                        match_type=MatchType.RESOURCE_TYPE_INFERRED,
                        confidence=conf,
                        category=category,
                        reasoning=f"Inferred from service: {service_name}"
                    ))
        
        return matches


# =============================================================================
# NATIVE TAG CHECKER (YES PATH)
# =============================================================================

class NativeTagChecker:
    """
    Main checker for resources WITH native tags.
    This is the "YES" path in the workflow.
    """
    
    def __init__(self, schema_index: TagSchemaIndex, decoder: TagDecoder):
        self.schema = schema_index
        self.decoder = decoder
    
    def check_resource(self, resource_row: pd.Series) -> List[TagMatch]:
        """
        Check native tags against schema.
        Returns list of matches with confidence scores.
        """
        matches = []
        
        for col in self.decoder.get_tag_columns():
            value = resource_row.get(col)
            if pd.isna(value) or value is None or str(value).strip() == '':
                continue
            
            value = str(value).strip()
            decoded_key = self.decoder.get_decoded_key(col)
            
            # Try to find matching schema key
            result = self.schema.find_key(decoded_key)
            
            if result:
                canonical_key, key_info, key_match_type = result
                
                # Check if value is valid
                if self.schema.is_valid_value(canonical_key, value):
                    # EXACT MATCH - 98% confidence!
                    matches.append(TagMatch(
                        native_key=decoded_key,
                        native_value=value,
                        virtual_key=canonical_key,
                        virtual_value=value,
                        match_type=MatchType.EXACT,
                        confidence=0.98,
                        category=key_info['category'],
                        reasoning="Exact match: key and value both found in schema"
                    ))
                else:
                    # Key matches but value not in allowed set
                    # Try to normalize the value
                    normalized = self._normalize_value(value, self.schema.get_valid_values(canonical_key))
                    
                    if normalized:
                        matches.append(TagMatch(
                            native_key=decoded_key,
                            native_value=value,
                            virtual_key=canonical_key,
                            virtual_value=normalized,
                            match_type=MatchType.NORMALIZED_VALUE,
                            confidence=0.85,
                            category=key_info['category'],
                            reasoning=f"Value normalized: '{value}' → '{normalized}'"
                        ))
                    else:
                        # Value couldn't be normalized, use as-is with lower confidence
                        matches.append(TagMatch(
                            native_key=decoded_key,
                            native_value=value,
                            virtual_key=canonical_key,
                            virtual_value=value,
                            match_type=MatchType.FUZZY_KEY,
                            confidence=0.70,
                            category=key_info['category'],
                            reasoning=f"Key matched but value '{value}' not in schema"
                        ))
            else:
                # Key not found in schema - this is an unknown tag
                # Could be a candidate for schema expansion
                pass
        
        return matches
    
    def _normalize_value(self, value: str, valid_values: set) -> Optional[str]:
        """Try to normalize a value to match a valid schema value"""
        value_lower = value.lower().strip()
        
        # Common normalizations
        normalizations = {
            'prod': 'prod',
            'production': 'prod',
            'prd': 'prod',
            'dev': 'dev',
            'development': 'dev',
            'stg': 'staging',
            'stage': 'staging',
            'test': 'testing',
            'tst': 'testing',
        }
        
        # Check if there's a direct normalization
        if value_lower in normalizations:
            normalized = normalizations[value_lower]
            if normalized in valid_values:
                return normalized
        
        # Try case-insensitive match against valid values
        for valid in valid_values:
            if value_lower == valid.lower():
                return valid
        
        return None


# =============================================================================
# CONFIDENCE CALCULATOR
# =============================================================================

class ConfidenceCalculator:
    """
    Calculate overall confidence score based on matched tags.
    Uses the formula: Key Match (40%) + Value Match (50%) + Category Weight (10%)
    """
    
    CATEGORY_WEIGHTS = {
        'Critical': 1.0,
        'Non-Critical': 0.7,
        'Optional': 0.4
    }
    
    def calculate(self, matches: List[TagMatch]) -> float:
        """Calculate weighted overall confidence"""
        if not matches:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for match in matches:
            # Base confidence from the match
            base_conf = match.confidence
            
            # Apply category weight
            cat_weight = self.CATEGORY_WEIGHTS.get(match.category, 0.5)
            
            # Weighted score
            weighted_score = base_conf * cat_weight
            total_score += weighted_score
            total_weight += cat_weight
        
        if total_weight == 0:
            return 0.0
        
        return round(total_score / total_weight, 4)
    
    def get_decision(self, confidence: float) -> str:
        """Determine action based on confidence threshold"""
        if confidence >= 0.90:
            return "AUTO_APPROVE"
        elif confidence >= 0.70:
            return "PENDING_APPROVAL"
        elif confidence >= 0.50:
            return "SUGGESTION"
        else:
            return "REJECT"


# =============================================================================
# MAIN VIRTUAL TAG PROCESSOR
# =============================================================================

class VirtualTagProcessor:
    """
    Main processor that orchestrates the entire virtual tagging workflow.
    Handles both YES and NO paths.
    """
    
    def __init__(self, schema_df: pd.DataFrame, resources_df: pd.DataFrame):
        # Build schema index
        self.schema_index = TagSchemaIndex(schema_df)
        
        # Create decoder for Base64 tag columns
        self.decoder = TagDecoder(resources_df)
        
        # Initialize components
        self.native_checker = NativeTagChecker(self.schema_index, self.decoder)
        self.pattern_matcher = PatternMatcher()
        self.type_inferrer = ResourceTypeInferrer()
        self.confidence_calc = ConfidenceCalculator()
        
        # Store dataframe
        self.resources_df = resources_df
        
        print(f"Initialized with {len(schema_df)} schema rules")
        print(f"Found {len(self.decoder.get_tag_columns())} tag columns in resources")
    
    def process_resource(self, idx: int, row: pd.Series) -> ResourceTagResult:
        """Process a single resource through the virtual tagging workflow"""
        
        # Extract resource info
        resource_id = str(row.get('cloud_resource_id', f'unknown-{idx}'))
        resource_name = str(row.get('name', '')) if pd.notna(row.get('name')) else ''
        resource_type = str(row.get('resource_type', '')) if pd.notna(row.get('resource_type')) else ''
        service_name = str(row.get('service_name', '')) if pd.notna(row.get('service_name')) else ''
        region = str(row.get('region', '')) if pd.notna(row.get('region')) else ''
        
        # Check if resource has any native tags
        has_native_tags = self._has_native_tags(row)
        
        all_matches = []
        
        if has_native_tags:
            # YES PATH: Resource has native tags → match against schema
            path_taken = "YES"
            native_matches = self.native_checker.check_resource(row)
            all_matches.extend(native_matches)
            
            # If native tags gave low matches, supplement with inference
            if len(native_matches) < 2:
                pattern_matches = self.pattern_matcher.match_patterns(
                    resource_name, resource_type, service_name
                )
                # Only add if not already matched
                existing_keys = [m.virtual_key for m in all_matches]
                for pm in pattern_matches:
                    if pm.virtual_key not in existing_keys:
                        all_matches.append(pm)
        
        else:
            # NO PATH: No native tags → pattern matching + type inference
            path_taken = "NO"
            
            # Step 1: Pattern matching on name
            if resource_name:
                pattern_matches = self.pattern_matcher.match_patterns(
                    resource_name, resource_type, service_name
                )
                all_matches.extend(pattern_matches)
            
            # Step 2: Resource type inference
            if resource_type or service_name:
                type_matches = self.type_inferrer.infer_from_resource_type(
                    resource_type, service_name
                )
                # Only add if not already matched
                existing_keys = [m.virtual_key for m in all_matches]
                for tm in type_matches:
                    if tm.virtual_key not in existing_keys:
                        all_matches.append(tm)
        
        # Calculate overall confidence
        overall_confidence = self.confidence_calc.calculate(all_matches)
        decision = self.confidence_calc.get_decision(overall_confidence)
        
        return ResourceTagResult(
            resource_id=resource_id,
            resource_name=resource_name,
            resource_type=resource_type,
            service_name=service_name,
            region=region,
            has_native_tags=has_native_tags,
            path_taken=path_taken,
            matches=all_matches,
            overall_confidence=overall_confidence,
            decision=decision
        )
    
    def _has_native_tags(self, row: pd.Series) -> bool:
        """Check if a resource has any non-null native tags"""
        for col in self.decoder.get_tag_columns():
            value = row.get(col)
            if pd.notna(value) and str(value).strip() != '':
                return True
        return False
    
    def process_all(self, limit: Optional[int] = None) -> List[ResourceTagResult]:
        """Process all resources (or up to limit)"""
        results = []
        total = min(limit, len(self.resources_df)) if limit else len(self.resources_df)
        
        print(f"\nProcessing {total} resources...")
        
        for idx, row in self.resources_df.head(total).iterrows():
            result = self.process_resource(idx, row)
            results.append(result)
            
            if (idx + 1) % 1000 == 0:
                print(f"  Processed {idx + 1}/{total} resources...")
        
        return results
    
    def generate_report(self, results: List[ResourceTagResult]) -> pd.DataFrame:
        """Generate a summary report from processing results"""
        report_data = []
        
        for r in results:
            # Flatten matches into readable format
            virtual_tags = {m.virtual_key: m.virtual_value for m in r.matches}
            
            report_data.append({
                'resource_id': r.resource_id,
                'resource_name': r.resource_name,
                'resource_type': r.resource_type,
                'service_name': r.service_name,
                'region': r.region,
                'has_native_tags': r.has_native_tags,
                'path_taken': r.path_taken,
                'num_matches': len(r.matches),
                'confidence': r.overall_confidence,
                'decision': r.decision,
                'virtual_tags': json.dumps(virtual_tags),
                'match_details': json.dumps([{
                    'key': m.virtual_key,
                    'value': m.virtual_value,
                    'type': m.match_type.value,
                    'confidence': m.confidence,
                    'reasoning': m.reasoning
                } for m in r.matches])
            })
        
        return pd.DataFrame(report_data)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main entry point"""
    print("=" * 60)
    print("Virtual Tag Checker - CloudTuner Implementation")
    print("=" * 60)
    
    # File paths (adjust if needed)
    SCHEMA_FILE = "cloud_resource_tags_complete 1.xlsx"
    RESOURCES_FILE = "restapi.resources (1).xlsx"
    OUTPUT_FILE = "virtual_tag_results.xlsx"
    
    # Load data
    print(f"\n1. Loading schema from {SCHEMA_FILE}...")
    schema_df = pd.read_excel(SCHEMA_FILE)
    print(f"   Loaded {len(schema_df)} schema definitions")
    
    print(f"\n2. Loading resources from {RESOURCES_FILE}...")
    resources_df = pd.read_excel(RESOURCES_FILE)
    print(f"   Loaded {len(resources_df)} resources")
    
    # Initialize processor
    print("\n3. Initializing Virtual Tag Processor...")
    processor = VirtualTagProcessor(schema_df, resources_df)
    
    # Process resources (limit for demo, remove limit for full processing)
    print("\n4. Processing resources...")
    results = processor.process_all(limit=1000)  # Process first 1000 for demo
    
    # Generate report
    print("\n5. Generating report...")
    report_df = processor.generate_report(results)
    
    # Statistics
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    total = len(results)
    yes_path = sum(1 for r in results if r.path_taken == "YES")
    no_path = sum(1 for r in results if r.path_taken == "NO")
    
    print(f"\nPath Distribution:")
    print(f"  YES path (has native tags): {yes_path} ({yes_path/total*100:.1f}%)")
    print(f"  NO path (no native tags):   {no_path} ({no_path/total*100:.1f}%)")
    
    print(f"\nDecision Distribution:")
    for decision in ["AUTO_APPROVE", "PENDING_APPROVAL", "SUGGESTION", "REJECT"]:
        count = sum(1 for r in results if r.decision == decision)
        print(f"  {decision}: {count} ({count/total*100:.1f}%)")
    
    avg_conf = sum(r.overall_confidence for r in results) / total
    print(f"\nAverage Confidence: {avg_conf:.2%}")
    
    # Save results
    report_df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n6. Results saved to {OUTPUT_FILE}")
    
    # Show sample results
    print("\n" + "=" * 60)
    print("SAMPLE RESULTS (first 5)")
    print("=" * 60)
    
    for r in results[:5]:
        print(f"\n{'='*40}")
        print(f"Resource: {r.resource_name or r.resource_id}")
        print(f"Type: {r.resource_type} | Service: {r.service_name}")
        print(f"Path: {r.path_taken} | Confidence: {r.overall_confidence:.2%} | Decision: {r.decision}")
        print(f"Virtual Tags:")
        for m in r.matches:
            print(f"  - {m.virtual_key}: {m.virtual_value} ({m.match_type.value}, {m.confidence:.0%})")
            print(f"    Reason: {m.reasoning}")


if __name__ == "__main__":
    main()
