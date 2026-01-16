"""
Virtual Tag Checker v2 - Enhanced for Resources WITHOUT Names/Tags
===================================================================

Key Insight from data analysis:
- 97.3% of resources have NO name
- 99.6% of resources have NO native tags
- Primary inference source: Resource Type + Service Name

This version focuses on maximizing tagging coverage using:
1. Resource Type → Default Tags mapping
2. Service Name → Default Tags mapping  
3. Region-based inference
4. Cloud Resource ID pattern analysis
"""

import pandas as pd
import base64
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


# =============================================================================
# DATA MODELS (same as v1)
# =============================================================================

class MatchType(Enum):
    EXACT = "EXACT"
    NORMALIZED_VALUE = "NORMALIZED_VALUE"
    FUZZY_KEY = "FUZZY_KEY"
    PATTERN_INFERRED = "PATTERN_INFERRED"
    RESOURCE_TYPE_INFERRED = "RESOURCE_TYPE_INFERRED"
    SERVICE_INFERRED = "SERVICE_INFERRED"
    REGION_INFERRED = "REGION_INFERRED"
    RESOURCE_ID_INFERRED = "RESOURCE_ID_INFERRED"
    DEFAULT_RULE = "DEFAULT_RULE"


@dataclass
class TagMatch:
    native_key: Optional[str]
    native_value: Optional[str]
    virtual_key: str
    virtual_value: str
    match_type: MatchType
    confidence: float
    category: str
    reasoning: str


@dataclass
class ResourceTagResult:
    resource_id: str
    resource_name: str
    resource_type: str
    service_name: str
    region: str
    has_native_tags: bool
    has_name: bool
    inference_path: str  # NATIVE_TAGS, NAME_PATTERN, RESOURCE_TYPE, SERVICE, REGION, DEFAULT
    matches: List[TagMatch] = field(default_factory=list)
    overall_confidence: float = 0.0
    decision: str = ""


# =============================================================================
# ENHANCED RESOURCE TYPE MAPPER
# =============================================================================

class ResourceTypeMapper:
    """
    Comprehensive mapping from resource types to default tags.
    This is the PRIMARY inference method for resources without names/tags.
    """
    
    # === COMPUTE ===
    COMPUTE_TYPES = {
        'Instance': {
            'ManagedBy': ('compute', 0.85),
            'BackupRequired': ('true', 0.75),
            'Department': ('Engineering', 0.70),
        },
        'Serverless': {
            'ManagedBy': ('serverless', 0.90),
            'Application': ('serverless', 0.70),
            'Department': ('Engineering', 0.70),
        },
        'Compute Engine': {
            'ManagedBy': ('compute', 0.85),
            'BackupRequired': ('true', 0.75),
            'Department': ('Engineering', 0.70),
        },
    }
    
    # === STORAGE ===
    STORAGE_TYPES = {
        'Volume': {
            'BackupRequired': ('true', 0.80),
            'StorageClass': ('standard', 0.65),
            'Department': ('Engineering', 0.65),
        },
        'Bucket': {
            'StorageClass': ('standard', 0.70),
            'Versioning': ('enabled', 0.60),
            'Department': ('Engineering', 0.65),
        },
        'Snapshot': {
            'BackupRequired': ('archive', 0.85),
            'RetentionDays': ('30', 0.60),
            'Department': ('Engineering', 0.65),
        },
        'Storage Snapshot': {
            'BackupRequired': ('archive', 0.85),
            'RetentionDays': ('30', 0.60),
        },
    }
    
    # === NETWORKING ===
    NETWORK_TYPES = {
        'IP Address': {
            'NetworkTier': ('standard', 0.75),
            'Department': ('DevOps', 0.70),
        },
        'Load Balancer': {
            'NetworkTier': ('public', 0.80),
            'Department': ('DevOps', 0.70),
        },
        'NAT Gateway': {
            'NetworkTier': ('internal', 0.80),
            'Department': ('DevOps', 0.70),
        },
        'DNS Query': {
            'NetworkTier': ('standard', 0.70),
            'Department': ('DevOps', 0.65),
        },
        'DNS Zone': {
            'NetworkTier': ('standard', 0.70),
            'Department': ('DevOps', 0.65),
        },
    }
    
    # === DATA/ML ===
    DATA_TYPES = {
        'BigQuery': {
            'Application': ('data-pipeline', 0.80),
            'Department': ('Data', 0.75),
        },
        'Vertex AI': {
            'Application': ('ml-model', 0.85),
            'Department': ('Data', 0.80),
        },
        'Cloud Logging': {
            'Application': ('monitoring', 0.80),
            'Department': ('DevOps', 0.75),
        },
        'Cloud Monitoring': {
            'Application': ('monitoring', 0.85),
            'Department': ('DevOps', 0.75),
        },
    }
    
    # === MANAGEMENT/SYSTEM ===
    SYSTEM_TYPES = {
        'AWS Systems Manager': {
            'ManagedBy': ('aws-systems', 0.90),
            'Application': ('monitoring', 0.70),
            'Department': ('DevOps', 0.80),
        },
        'API Request': {
            'Application': ('web-api', 0.70),
            'Department': ('Engineering', 0.65),
        },
        'Data Transfer': {
            'Department': ('Engineering', 0.60),
        },
    }
    
    def __init__(self):
        # Combine all type mappings
        self.all_mappings = {}
        self.all_mappings.update(self.COMPUTE_TYPES)
        self.all_mappings.update(self.STORAGE_TYPES)
        self.all_mappings.update(self.NETWORK_TYPES)
        self.all_mappings.update(self.DATA_TYPES)
        self.all_mappings.update(self.SYSTEM_TYPES)
    
    def get_tags_for_type(self, resource_type: str) -> List[TagMatch]:
        """Get default tags for a resource type"""
        matches = []
        
        if resource_type in self.all_mappings:
            for tag_key, (tag_value, confidence) in self.all_mappings[resource_type].items():
                # Determine category based on tag key
                category = self._get_category(tag_key)
                
                matches.append(TagMatch(
                    native_key=None,
                    native_value=None,
                    virtual_key=tag_key,
                    virtual_value=tag_value,
                    match_type=MatchType.RESOURCE_TYPE_INFERRED,
                    confidence=confidence,
                    category=category,
                    reasoning=f"Default tag for resource type: {resource_type}"
                ))
        
        return matches
    
    def _get_category(self, tag_key: str) -> str:
        """Determine tag category"""
        critical = ['Environment', 'Owner', 'CostCenter', 'Application', 'Department']
        non_critical = ['Project', 'Team', 'BackupRequired', 'ManagedBy']
        
        if tag_key in critical:
            return 'Critical'
        elif tag_key in non_critical:
            return 'Non-Critical'
        return 'Optional'


# =============================================================================
# SERVICE NAME MAPPER
# =============================================================================

class ServiceNameMapper:
    """Map service names to default tags"""
    
    SERVICE_MAPPINGS = {
        # AWS Services
        'AmazonEC2': {
            'Owner': ('compute-team@company.com', 0.60),
            'Department': ('Engineering', 0.75),
        },
        'AmazonS3': {
            'Owner': ('storage-team@company.com', 0.60),
            'Department': ('Engineering', 0.75),
        },
        'AWSLambda': {
            'Application': ('serverless', 0.80),
            'Department': ('Engineering', 0.75),
        },
        'AWSSystemsManager': {
            'ManagedBy': ('aws-systems', 0.90),
            'Department': ('DevOps', 0.85),
        },
        'AmazonVPC': {
            'Department': ('DevOps', 0.80),
            'NetworkTier': ('internal', 0.70),
        },
        'AmazonRDS': {
            'BackupRequired': ('true', 0.90),
            'Department': ('Engineering', 0.75),
        },
        'AmazonEKS': {
            'ManagedBy': ('kubernetes', 0.85),
            'Department': ('DevOps', 0.80),
        },
        'AWSBackup': {
            'BackupRequired': ('true', 0.95),
            'Department': ('DevOps', 0.75),
        },
        
        # GCP Services
        'Compute Engine': {
            'Owner': ('compute-team@company.com', 0.60),
            'Department': ('Engineering', 0.75),
        },
        'BigQuery': {
            'Application': ('data-pipeline', 0.80),
            'Department': ('Data', 0.80),
        },
        'Vertex AI': {
            'Application': ('ml-model', 0.85),
            'Department': ('Data', 0.85),
        },
        'Cloud Logging': {
            'Application': ('monitoring', 0.80),
            'Department': ('DevOps', 0.80),
        },
        'Cloud Monitoring': {
            'Application': ('monitoring', 0.85),
            'Department': ('DevOps', 0.80),
        },
    }
    
    def get_tags_for_service(self, service_name: str) -> List[TagMatch]:
        """Get default tags for a service"""
        matches = []
        
        if service_name in self.SERVICE_MAPPINGS:
            for tag_key, (tag_value, confidence) in self.SERVICE_MAPPINGS[service_name].items():
                category = 'Critical' if tag_key in ['Owner', 'Department', 'Application'] else 'Non-Critical'
                
                matches.append(TagMatch(
                    native_key=None,
                    native_value=None,
                    virtual_key=tag_key,
                    virtual_value=tag_value,
                    match_type=MatchType.SERVICE_INFERRED,
                    confidence=confidence,
                    category=category,
                    reasoning=f"Default tag for service: {service_name}"
                ))
        
        return matches


# =============================================================================
# REGION MAPPER
# =============================================================================

class RegionMapper:
    """Infer tags from region information"""
    
    REGION_MAPPINGS = {
        # AWS Regions
        'ap-south-1': ('India', 'Asia'),
        'ap-southeast-1': ('Singapore', 'Asia'),
        'us-east-1': ('US-East', 'Americas'),
        'us-west-2': ('US-West', 'Americas'),
        'eu-west-1': ('Ireland', 'Europe'),
        'eu-central-1': ('Frankfurt', 'Europe'),
        
        # GCP Regions
        'us-central1': ('US-Central', 'Americas'),
        'us': ('US', 'Americas'),
        'asia-south1': ('India', 'Asia'),
        
        # Azure Regions
        'South India': ('India', 'Asia'),
        'East US': ('US-East', 'Americas'),
    }
    
    def get_tags_for_region(self, region: str) -> List[TagMatch]:
        """Get tags based on region"""
        matches = []
        
        if region in self.REGION_MAPPINGS:
            location, geo = self.REGION_MAPPINGS[region]
            
            matches.append(TagMatch(
                native_key=None,
                native_value=None,
                virtual_key='DataCenter',
                virtual_value=location,
                match_type=MatchType.REGION_INFERRED,
                confidence=0.95,
                category='Optional',
                reasoning=f"Inferred from region: {region}"
            ))
        
        return matches


# =============================================================================
# RESOURCE ID PATTERN ANALYZER
# =============================================================================

class ResourceIdAnalyzer:
    """
    Extract information from cloud resource IDs.
    Many IDs follow patterns that reveal environment/type.
    """
    
    PATTERNS = {
        # AWS patterns
        r'^i-[0-9a-f]+$': ('Instance', 'AmazonEC2', 0.90),
        r'^vol-[0-9a-f]+$': ('Volume', 'AmazonEC2', 0.90),
        r'^snap-[0-9a-f]+$': ('Snapshot', 'AmazonEC2', 0.90),
        r'^eni-[0-9a-f]+$': ('NetworkInterface', 'AmazonVPC', 0.90),
        r'^subnet-[0-9a-f]+$': ('Subnet', 'AmazonVPC', 0.90),
        r'^sg-[0-9a-f]+$': ('SecurityGroup', 'AmazonVPC', 0.90),
        r'^ami-[0-9a-f]+$': ('AMI', 'AmazonEC2', 0.90),
        r'^arn:aws:': ('', '', 0),  # ARN - will parse further
        
        # Contains prod/dev/staging in ID
        r'prod': ('Environment:prod', None, 0.70),
        r'staging|stag': ('Environment:staging', None, 0.70),
        r'dev': ('Environment:dev', None, 0.65),
    }
    
    def analyze_id(self, resource_id: str) -> List[TagMatch]:
        """Analyze resource ID for patterns"""
        matches = []
        
        if not resource_id:
            return matches
        
        resource_id_lower = resource_id.lower()
        
        # Check for environment in ID
        if 'prod' in resource_id_lower:
            matches.append(TagMatch(
                native_key=None,
                native_value=None,
                virtual_key='Environment',
                virtual_value='prod',
                match_type=MatchType.RESOURCE_ID_INFERRED,
                confidence=0.70,
                category='Critical',
                reasoning=f"Pattern 'prod' found in resource ID"
            ))
        elif 'staging' in resource_id_lower or 'stag' in resource_id_lower:
            matches.append(TagMatch(
                native_key=None,
                native_value=None,
                virtual_key='Environment',
                virtual_value='staging',
                match_type=MatchType.RESOURCE_ID_INFERRED,
                confidence=0.70,
                category='Critical',
                reasoning=f"Pattern 'staging' found in resource ID"
            ))
        elif 'dev' in resource_id_lower:
            matches.append(TagMatch(
                native_key=None,
                native_value=None,
                virtual_key='Environment',
                virtual_value='dev',
                match_type=MatchType.RESOURCE_ID_INFERRED,
                confidence=0.65,
                category='Critical',
                reasoning=f"Pattern 'dev' found in resource ID"
            ))
        
        return matches


# =============================================================================
# MAIN PROCESSOR v2
# =============================================================================

class VirtualTagProcessorV2:
    """
    Enhanced processor optimized for resources WITHOUT names and tags.
    Uses a cascade of inference methods.
    """
    
    def __init__(self, resources_df: pd.DataFrame, schema_df: pd.DataFrame = None):
        self.resources_df = resources_df
        
        # Initialize mappers
        self.resource_type_mapper = ResourceTypeMapper()
        self.service_mapper = ServiceNameMapper()
        self.region_mapper = RegionMapper()
        self.id_analyzer = ResourceIdAnalyzer()
        
        # Decode tag columns for native tag checking
        self.tag_columns = []
        self.column_mapping = {}
        for col in resources_df.columns:
            if col.startswith('tags.'):
                self.tag_columns.append(col)
                encoded = col.replace('tags.', '')
                try:
                    self.column_mapping[col] = base64.b64decode(encoded).decode('utf-8')
                except:
                    self.column_mapping[col] = encoded
        
        print(f"Initialized V2 processor with {len(resources_df)} resources")
        print(f"Found {len(self.tag_columns)} tag columns")
    
    def process_resource(self, idx: int, row: pd.Series) -> ResourceTagResult:
        """Process a single resource with enhanced inference"""
        
        # Extract resource info
        resource_id = str(row.get('cloud_resource_id', f'unknown-{idx}'))
        resource_name = str(row.get('name', '')) if pd.notna(row.get('name')) else ''
        resource_type = str(row.get('resource_type', '')) if pd.notna(row.get('resource_type')) else ''
        service_name = str(row.get('service_name', '')) if pd.notna(row.get('service_name')) else ''
        region = str(row.get('region', '')) if pd.notna(row.get('region')) else ''
        
        # Check data availability
        has_native_tags = self._has_native_tags(row)
        has_name = bool(resource_name.strip())
        
        all_matches = []
        inference_paths = []
        
        # === CASCADE OF INFERENCE METHODS ===
        
        # 1. Native tags (if available) - Highest priority
        if has_native_tags:
            inference_paths.append("NATIVE_TAGS")
            native_matches = self._check_native_tags(row)
            all_matches.extend(native_matches)
        
        # 2. Name pattern matching (if name available)
        if has_name:
            inference_paths.append("NAME_PATTERN")
            name_matches = self._pattern_match_name(resource_name)
            self._merge_matches(all_matches, name_matches)
        
        # 3. Resource ID analysis
        id_matches = self.id_analyzer.analyze_id(resource_id)
        if id_matches:
            inference_paths.append("RESOURCE_ID")
            self._merge_matches(all_matches, id_matches)
        
        # 4. Resource Type inference - PRIMARY for most resources
        if resource_type:
            inference_paths.append("RESOURCE_TYPE")
            type_matches = self.resource_type_mapper.get_tags_for_type(resource_type)
            self._merge_matches(all_matches, type_matches)
        
        # 5. Service Name inference
        if service_name:
            inference_paths.append("SERVICE")
            service_matches = self.service_mapper.get_tags_for_service(service_name)
            self._merge_matches(all_matches, service_matches)
        
        # 6. Region inference
        if region:
            inference_paths.append("REGION")
            region_matches = self.region_mapper.get_tags_for_region(region)
            self._merge_matches(all_matches, region_matches)
        
        # Calculate confidence
        overall_confidence = self._calculate_confidence(all_matches)
        decision = self._get_decision(overall_confidence)
        
        return ResourceTagResult(
            resource_id=resource_id,
            resource_name=resource_name,
            resource_type=resource_type,
            service_name=service_name,
            region=region,
            has_native_tags=has_native_tags,
            has_name=has_name,
            inference_path=" → ".join(inference_paths) if inference_paths else "NONE",
            matches=all_matches,
            overall_confidence=overall_confidence,
            decision=decision
        )
    
    def _has_native_tags(self, row: pd.Series) -> bool:
        """Check if resource has any native tags"""
        for col in self.tag_columns:
            if pd.notna(row.get(col)) and str(row.get(col)).strip():
                return True
        return False
    
    def _check_native_tags(self, row: pd.Series) -> List[TagMatch]:
        """Check native tags against schema (simplified)"""
        matches = []
        for col in self.tag_columns:
            value = row.get(col)
            if pd.notna(value) and str(value).strip():
                decoded_key = self.column_mapping.get(col, col)
                matches.append(TagMatch(
                    native_key=decoded_key,
                    native_value=str(value),
                    virtual_key=decoded_key,
                    virtual_value=str(value),
                    match_type=MatchType.EXACT,
                    confidence=0.90,  # High confidence for native tags
                    category='Non-Critical',
                    reasoning=f"Native tag found: {decoded_key}={value}"
                ))
        return matches
    
    def _pattern_match_name(self, name: str) -> List[TagMatch]:
        """Pattern matching on resource name"""
        matches = []
        name_lower = name.lower()
        
        # Environment patterns
        env_patterns = [
            (r'[-_]prod[-_]|[-_]production[-_]|^prod[-_]|[-_]prod$', 'prod', 0.90),
            (r'[-_]staging[-_]|[-_]stag[-_]', 'staging', 0.88),
            (r'[-_]dev[-_]|[-_]development[-_]', 'dev', 0.85),
            (r'[-_]test[-_]|[-_]testing[-_]', 'testing', 0.85),
        ]
        
        for pattern, value, conf in env_patterns:
            if re.search(pattern, name_lower):
                matches.append(TagMatch(
                    native_key=None,
                    native_value=None,
                    virtual_key='Environment',
                    virtual_value=value,
                    match_type=MatchType.PATTERN_INFERRED,
                    confidence=conf,
                    category='Critical',
                    reasoning=f"Pattern '{pattern}' found in name"
                ))
                break
        
        return matches
    
    def _merge_matches(self, existing: List[TagMatch], new: List[TagMatch]):
        """Merge new matches, avoiding duplicates. Higher confidence wins."""
        existing_keys = {m.virtual_key: m for m in existing}
        
        for match in new:
            if match.virtual_key in existing_keys:
                # Keep the one with higher confidence
                if match.confidence > existing_keys[match.virtual_key].confidence:
                    existing.remove(existing_keys[match.virtual_key])
                    existing.append(match)
                    existing_keys[match.virtual_key] = match
            else:
                existing.append(match)
                existing_keys[match.virtual_key] = match
    
    def _calculate_confidence(self, matches: List[TagMatch]) -> float:
        """Calculate weighted confidence"""
        if not matches:
            return 0.0
        
        category_weights = {'Critical': 1.0, 'Non-Critical': 0.7, 'Optional': 0.4}
        
        total_score = sum(m.confidence * category_weights.get(m.category, 0.5) for m in matches)
        total_weight = sum(category_weights.get(m.category, 0.5) for m in matches)
        
        return round(total_score / total_weight, 4) if total_weight > 0 else 0.0
    
    def _get_decision(self, confidence: float) -> str:
        """Get decision based on confidence"""
        if confidence >= 0.90:
            return "AUTO_APPROVE"
        elif confidence >= 0.70:
            return "PENDING_APPROVAL"
        elif confidence >= 0.50:
            return "SUGGESTION"
        return "NEEDS_REVIEW"  # Changed from REJECT to be more useful
    
    def process_all(self, limit: Optional[int] = None) -> List[ResourceTagResult]:
        """Process all resources"""
        results = []
        total = min(limit, len(self.resources_df)) if limit else len(self.resources_df)
        
        print(f"\nProcessing {total} resources...")
        
        for idx, row in self.resources_df.head(total).iterrows():
            result = self.process_resource(idx, row)
            results.append(result)
            
            if (idx + 1) % 5000 == 0:
                print(f"  Processed {idx + 1}/{total} resources...")
        
        return results
    
    def generate_report(self, results: List[ResourceTagResult]) -> pd.DataFrame:
        """Generate report dataframe"""
        report_data = []
        
        for r in results:
            virtual_tags = {m.virtual_key: m.virtual_value for m in r.matches}
            
            report_data.append({
                'resource_id': r.resource_id,
                'resource_name': r.resource_name,
                'resource_type': r.resource_type,
                'service_name': r.service_name,
                'region': r.region,
                'has_native_tags': r.has_native_tags,
                'has_name': r.has_name,
                'inference_path': r.inference_path,
                'num_tags': len(r.matches),
                'confidence': r.overall_confidence,
                'decision': r.decision,
                'virtual_tags': json.dumps(virtual_tags),
            })
        
        return pd.DataFrame(report_data)


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Virtual Tag Checker V2 - Optimized for Resources WITHOUT Names/Tags")
    print("=" * 70)
    
    RESOURCES_FILE = "restapi.resources (1).xlsx"
    OUTPUT_FILE = "virtual_tag_results_v2.xlsx"
    
    print(f"\nLoading resources from {RESOURCES_FILE}...")
    resources_df = pd.read_excel(RESOURCES_FILE)
    print(f"Loaded {len(resources_df)} resources")
    
    # Data analysis
    has_name = resources_df['name'].notna().sum()
    has_tags = sum(1 for _, row in resources_df.head(1000).iterrows() 
                   if any(pd.notna(row.get(c)) for c in resources_df.columns if c.startswith('tags.')))
    
    print(f"\n=== DATA AVAILABILITY ===")
    print(f"Resources with name: {has_name} ({has_name/len(resources_df)*100:.1f}%)")
    print(f"Resources with tags (sample 1000): ~{has_tags/10:.1f}%")
    
    # Initialize and process
    processor = VirtualTagProcessorV2(resources_df)
    
    print("\nProcessing...")
    results = processor.process_all(limit=5000)  # Process 5000 for demo
    
    # Generate report
    report_df = processor.generate_report(results)
    
    # Statistics
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    total = len(results)
    
    print(f"\nData Availability:")
    with_name = sum(1 for r in results if r.has_name)
    with_tags = sum(1 for r in results if r.has_native_tags)
    print(f"  With name: {with_name} ({with_name/total*100:.1f}%)")
    print(f"  With native tags: {with_tags} ({with_tags/total*100:.1f}%)")
    
    print(f"\nDecision Distribution:")
    for decision in ["AUTO_APPROVE", "PENDING_APPROVAL", "SUGGESTION", "NEEDS_REVIEW"]:
        count = sum(1 for r in results if r.decision == decision)
        print(f"  {decision}: {count} ({count/total*100:.1f}%)")
    
    print(f"\nTag Coverage:")
    with_tags_applied = sum(1 for r in results if len(r.matches) > 0)
    avg_tags = sum(len(r.matches) for r in results) / total
    print(f"  Resources with at least 1 virtual tag: {with_tags_applied} ({with_tags_applied/total*100:.1f}%)")
    print(f"  Average tags per resource: {avg_tags:.1f}")
    
    avg_conf = sum(r.overall_confidence for r in results) / total
    print(f"\nAverage Confidence: {avg_conf:.1%}")
    
    # Top inference paths
    print(f"\nTop Inference Paths:")
    path_counts = {}
    for r in results:
        path_counts[r.inference_path] = path_counts.get(r.inference_path, 0) + 1
    for path, count in sorted(path_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {path}: {count}")
    
    # Save
    report_df.to_excel(OUTPUT_FILE, index=False)
    print(f"\nResults saved to {OUTPUT_FILE}")
    
    # Sample results
    print("\n" + "=" * 70)
    print("SAMPLE RESULTS")
    print("=" * 70)
    
    for r in results[:8]:
        print(f"\n{'─'*50}")
        print(f"Resource: {r.resource_name or r.resource_id[:50]}")
        print(f"Type: {r.resource_type} | Service: {r.service_name}")
        print(f"Path: {r.inference_path}")
        print(f"Confidence: {r.overall_confidence:.1%} | Decision: {r.decision}")
        if r.matches:
            print(f"Virtual Tags ({len(r.matches)}):")
            for m in r.matches[:4]:
                print(f"  • {m.virtual_key}: {m.virtual_value} ({m.match_type.value}, {m.confidence:.0%})")


if __name__ == "__main__":
    main()
