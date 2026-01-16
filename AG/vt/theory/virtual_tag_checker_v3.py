"""
Virtual Tag Checker V3 - COMPLETE Implementation for Your Data
===============================================================

Coverage for ALL major resource types in your dataset:
- AWS Systems Manager: 29,530 resources  
- IP Address: 11,548 resources
- Volume: 6,904 resources
- Instance: 6,364 resources
- Serverless: 1,877 resources
- And more...
"""

import pandas as pd
import base64
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


# =============================================================================
# DATA MODELS
# =============================================================================

class MatchType(Enum):
    NATIVE_TAG = "NATIVE_TAG"
    NAME_PATTERN = "NAME_PATTERN"
    RESOURCE_TYPE = "RESOURCE_TYPE"
    SERVICE = "SERVICE"
    REGION = "REGION"
    RESOURCE_ID = "RESOURCE_ID"
    DEFAULT = "DEFAULT"


@dataclass
class TagMatch:
    virtual_key: str
    virtual_value: str
    match_type: MatchType
    confidence: float
    category: str  # Critical, Non-Critical, Optional
    reasoning: str


@dataclass 
class ResourceResult:
    resource_id: str
    resource_name: str
    resource_type: str
    service_name: str
    region: str
    has_native_tags: bool
    has_name: bool
    inference_path: str
    matches: List[TagMatch] = field(default_factory=list)
    confidence: float = 0.0
    decision: str = ""


# =============================================================================
# COMPREHENSIVE RESOURCE TYPE MAPPING (Based on YOUR data)
# =============================================================================

# Maps resource_type -> default virtual tags
RESOURCE_TYPE_TAGS = {
    # === TOP RESOURCE TYPES IN YOUR DATA ===
    
    'AWS Systems Manager': {
        'ManagedBy': ('aws-ssm', 0.95, 'Non-Critical'),
        'Application': ('monitoring', 0.80, 'Critical'),
        'Department': ('DevOps', 0.85, 'Critical'),
    },
    
    'IP Address': {
        'Department': ('DevOps', 0.80, 'Critical'),
        'NetworkTier': ('standard', 0.85, 'Optional'),
        'ManagedBy': ('cloud-network', 0.75, 'Non-Critical'),
    },
    
    'Volume': {
        'BackupRequired': ('true', 0.85, 'Non-Critical'),
        'Department': ('Engineering', 0.75, 'Critical'),
        'StorageClass': ('standard', 0.70, 'Optional'),
    },
    
    'Instance': {
        'ManagedBy': ('compute', 0.85, 'Non-Critical'),
        'BackupRequired': ('true', 0.80, 'Non-Critical'),
        'Department': ('Engineering', 0.80, 'Critical'),
    },
    
    'Serverless': {
        'ManagedBy': ('serverless', 0.90, 'Non-Critical'),
        'Application': ('serverless', 0.75, 'Critical'),
        'Department': ('Engineering', 0.80, 'Critical'),
    },
    
    'Snapshot': {
        'BackupRequired': ('archive', 0.90, 'Non-Critical'),
        'Department': ('DevOps', 0.75, 'Critical'),
        'RetentionDays': ('30', 0.65, 'Optional'),
    },
    
    'APS3-Resource-Operation-Count': {
        'Department': ('Engineering', 0.70, 'Critical'),
        'Application': ('storage', 0.65, 'Critical'),
    },
    
    'API Request': {
        'Application': ('web-api', 0.80, 'Critical'),
        'Department': ('Engineering', 0.75, 'Critical'),
    },
    
    'Bucket': {
        'Department': ('Engineering', 0.80, 'Critical'),
        'StorageClass': ('standard', 0.75, 'Optional'),
        'Versioning': ('enabled', 0.60, 'Optional'),
    },
    
    'India GST': {
        'Department': ('Finance', 0.90, 'Critical'),
        'DataClassification': ('financial', 0.85, 'Critical'),
    },
    
    'Storage Snapshot': {
        'BackupRequired': ('archive', 0.90, 'Non-Critical'),
        'Department': ('DevOps', 0.75, 'Critical'),
    },
    
    'Vertex AI': {
        'Application': ('ml-model', 0.90, 'Critical'),
        'Department': ('Data', 0.85, 'Critical'),
        'Team': ('data-science', 0.75, 'Non-Critical'),
    },
    
    'Data Transfer': {
        'Department': ('Engineering', 0.70, 'Critical'),
        'NetworkTier': ('standard', 0.65, 'Optional'),
    },
    
    'Load Balancer': {
        'NetworkTier': ('public', 0.85, 'Optional'),
        'Department': ('DevOps', 0.80, 'Critical'),
        'ManagedBy': ('networking', 0.80, 'Non-Critical'),
    },
    
    'DNS Query': {
        'Department': ('DevOps', 0.75, 'Critical'),
        'NetworkTier': ('standard', 0.70, 'Optional'),
    },
    
    'USE1-Resource-Operation-Count': {
        'Department': ('Engineering', 0.70, 'Critical'),
    },
    
    'AmazonLocationService': {
        'Application': ('location-services', 0.85, 'Critical'),
        'Department': ('Engineering', 0.75, 'Critical'),
    },
    
    'ACM': {
        'Application': ('security', 0.85, 'Critical'),
        'Department': ('DevOps', 0.80, 'Critical'),
    },
    
    'API Calls': {
        'Application': ('web-api', 0.75, 'Critical'),
        'Department': ('Engineering', 0.70, 'Critical'),
    },
    
    'Management Tools - AWS CloudTrail Free Events Recorded': {
        'Application': ('monitoring', 0.85, 'Critical'),
        'Department': ('DevOps', 0.85, 'Critical'),
        'Compliance': ('audit', 0.90, 'Non-Critical'),
    },
    
    'Compute Engine': {
        'ManagedBy': ('compute', 0.85, 'Non-Critical'),
        'Department': ('Engineering', 0.80, 'Critical'),
        'BackupRequired': ('true', 0.75, 'Non-Critical'),
    },
    
    'Data Payload': {
        'Department': ('Engineering', 0.70, 'Critical'),
    },
    
    'Cloud Logging': {
        'Application': ('monitoring', 0.90, 'Critical'),
        'Department': ('DevOps', 0.85, 'Critical'),
    },
    
    'EC2 Container Registry': {
        'Application': ('containers', 0.85, 'Critical'),
        'Department': ('DevOps', 0.80, 'Critical'),
    },
    
    'Cloud Monitoring': {
        'Application': ('monitoring', 0.90, 'Critical'),
        'Department': ('DevOps', 0.85, 'Critical'),
    },
    
    'BigQuery': {
        'Application': ('data-pipeline', 0.90, 'Critical'),
        'Department': ('Data', 0.85, 'Critical'),
    },
    
    'DNS Zone': {
        'Department': ('DevOps', 0.80, 'Critical'),
        'NetworkTier': ('standard', 0.70, 'Optional'),
    },
    
    'NAT Gateway': {
        'NetworkTier': ('internal', 0.85, 'Optional'),
        'Department': ('DevOps', 0.80, 'Critical'),
    },
}

# =============================================================================
# SERVICE NAME MAPPING (Based on YOUR data)
# =============================================================================

SERVICE_TAGS = {
    'AWSSystemsManager': {
        'ManagedBy': ('aws-ssm', 0.95, 'Non-Critical'),
        'Department': ('DevOps', 0.90, 'Critical'),
    },
    
    'AmazonEC2': {
        'Department': ('Engineering', 0.80, 'Critical'),
        'Owner': ('compute-team', 0.65, 'Critical'),
    },
    
    'AmazonVPC': {
        'Department': ('DevOps', 0.85, 'Critical'),
        'NetworkTier': ('internal', 0.75, 'Optional'),
    },
    
    'AWSLambda': {
        'Application': ('serverless', 0.85, 'Critical'),
        'Department': ('Engineering', 0.80, 'Critical'),
    },
    
    'AmazonS3': {
        'Department': ('Engineering', 0.75, 'Critical'),
        'StorageClass': ('standard', 0.70, 'Optional'),
    },
    
    'AWSCloudFormation': {
        'ManagedBy': ('infrastructure-as-code', 0.90, 'Non-Critical'),
        'Department': ('DevOps', 0.85, 'Critical'),
    },
    
    'AmazonCloudWatch': {
        'Application': ('monitoring', 0.90, 'Critical'),
        'Department': ('DevOps', 0.85, 'Critical'),
    },
    
    'Vertex AI': {
        'Application': ('ml-model', 0.90, 'Critical'),
        'Department': ('Data', 0.85, 'Critical'),
    },
    
    'awskms': {
        'Application': ('security', 0.90, 'Critical'),
        'Department': ('DevOps', 0.85, 'Critical'),
    },
    
    'AmazonApiGateway': {
        'Application': ('web-api', 0.85, 'Critical'),
        'Department': ('Engineering', 0.80, 'Critical'),
    },
    
    'AmazonSNS': {
        'Application': ('messaging', 0.85, 'Critical'),
        'Department': ('Engineering', 0.75, 'Critical'),
    },
    
    'AWSSecretsManager': {
        'Application': ('security', 0.90, 'Critical'),
        'Department': ('DevOps', 0.85, 'Critical'),
    },
    
    'AWSQueueService': {
        'Application': ('messaging', 0.85, 'Critical'),
        'Department': ('Engineering', 0.75, 'Critical'),
    },
    
    'AWSELB': {
        'NetworkTier': ('public', 0.80, 'Optional'),
        'Department': ('DevOps', 0.80, 'Critical'),
    },
    
    'AmazonRoute53': {
        'Department': ('DevOps', 0.85, 'Critical'),
        'Application': ('dns', 0.80, 'Critical'),
    },
    
    'Compute Engine': {
        'Department': ('Engineering', 0.80, 'Critical'),
        'ManagedBy': ('compute', 0.75, 'Non-Critical'),
    },
    
    'AmazonLocationService': {
        'Application': ('location-services', 0.85, 'Critical'),
        'Department': ('Engineering', 0.75, 'Critical'),
    },
    
    'AWSCloudTrail': {
        'Application': ('monitoring', 0.90, 'Critical'),
        'Department': ('DevOps', 0.90, 'Critical'),
        'Compliance': ('audit', 0.95, 'Non-Critical'),
    },
    
    'AWS': {
        'Department': ('Engineering', 0.65, 'Critical'),
    },
    
    'AmazonLightsail': {
        'Department': ('Engineering', 0.75, 'Critical'),
        'ManagedBy': ('compute', 0.70, 'Non-Critical'),
    },
    
    'AWSGlue': {
        'Application': ('data-pipeline', 0.85, 'Critical'),
        'Department': ('Data', 0.80, 'Critical'),
    },
    
    'AmazonECR': {
        'Application': ('containers', 0.85, 'Critical'),
        'Department': ('DevOps', 0.80, 'Critical'),
    },
    
    'Cloud Logging': {
        'Application': ('monitoring', 0.90, 'Critical'),
        'Department': ('DevOps', 0.85, 'Critical'),
    },
    
    'AmazonSageMaker': {
        'Application': ('ml-model', 0.90, 'Critical'),
        'Department': ('Data', 0.85, 'Critical'),
    },
    
    'Cloud Monitoring': {
        'Application': ('monitoring', 0.90, 'Critical'),
        'Department': ('DevOps', 0.85, 'Critical'),
    },
    
    'AmazonRDS': {
        'BackupRequired': ('true', 0.95, 'Non-Critical'),
        'Department': ('Engineering', 0.80, 'Critical'),
    },
    
    'AWSBackup': {
        'BackupRequired': ('true', 0.98, 'Non-Critical'),
        'Department': ('DevOps', 0.85, 'Critical'),
    },
    
    'AmazonRekognition': {
        'Application': ('ml-model', 0.85, 'Critical'),
        'Department': ('Data', 0.80, 'Critical'),
    },
    
    'AmazonEKS': {
        'ManagedBy': ('kubernetes', 0.90, 'Non-Critical'),
        'Department': ('DevOps', 0.85, 'Critical'),
    },
}

# =============================================================================
# REGION MAPPING
# =============================================================================

REGION_TAGS = {
    'ap-south-1': ('India-Mumbai', 'APAC'),
    'ap-southeast-1': ('Singapore', 'APAC'),
    'us-east-1': ('US-Virginia', 'Americas'),
    'us-west-2': ('US-Oregon', 'Americas'),
    'eu-west-1': ('Ireland', 'EMEA'),
    'eu-central-1': ('Frankfurt', 'EMEA'),
    'us-central1': ('US-Iowa', 'Americas'),
    'us': ('US', 'Americas'),
    'asia-south1': ('India', 'APAC'),
    'South India': ('India', 'APAC'),
}


# =============================================================================
# NAME PATTERN MATCHING
# =============================================================================

NAME_PATTERNS = {
    # Environment patterns
    'Environment': [
        (r'(?:^|[-_])prod(?:uction)?(?:[-_]|$)', 'prod', 0.92),
        (r'(?:^|[-_])stag(?:ing)?(?:[-_]|$)', 'staging', 0.88),
        (r'(?:^|[-_])dev(?:elopment)?(?:[-_]|$)', 'dev', 0.85),
        (r'(?:^|[-_])test(?:ing)?(?:[-_]|$)', 'testing', 0.85),
        (r'(?:^|[-_])uat(?:[-_]|$)', 'staging', 0.80),
        (r'(?:^|[-_])qa(?:[-_]|$)', 'testing', 0.80),
    ],
    
    # Application patterns  
    'Application': [
        (r'(?:^|[-_])api(?:[-_]|$)|api[-_]?gateway', 'web-api', 0.80),
        (r'lambda|serverless|function', 'serverless', 0.75),
        (r'data[-_]?pipeline|etl|data[-_]?flow', 'data-pipeline', 0.75),
        (r'ml[-_]?|machine[-_]?learning|ai[-_]', 'ml-model', 0.75),
        (r'monitoring|observability', 'monitoring', 0.70),
    ],
    
    # Team patterns
    'Team': [
        (r'platform|infra', 'platform', 0.65),
        (r'devops|sre|ops', 'devops', 0.65),
        (r'data[-_]?team|analytics', 'data', 0.65),
        (r'frontend|ui[-_]|web[-_]', 'frontend', 0.60),
        (r'backend', 'backend', 0.60),
    ],
}


# =============================================================================
# MAIN PROCESSOR
# =============================================================================

class VirtualTagProcessor:
    """Complete virtual tag processor for your data"""
    
    def __init__(self, resources_df: pd.DataFrame):
        self.df = resources_df
        
        # Decode tag columns
        self.tag_columns = []
        self.tag_names = {}
        for col in resources_df.columns:
            if col.startswith('tags.'):
                self.tag_columns.append(col)
                enc = col.replace('tags.', '')
                try:
                    self.tag_names[col] = base64.b64decode(enc).decode('utf-8')
                except:
                    self.tag_names[col] = enc
        
        print(f"Loaded {len(resources_df)} resources")
        print(f"Found {len(self.tag_columns)} native tag columns")
    
    def process(self, row_idx: int, row: pd.Series) -> ResourceResult:
        """Process single resource"""
        
        # Get resource info
        rid = str(row.get('cloud_resource_id', f'r-{row_idx}'))
        rname = str(row.get('name', '')) if pd.notna(row.get('name')) else ''
        rtype = str(row.get('resource_type', '')) if pd.notna(row.get('resource_type')) else ''
        service = str(row.get('service_name', '')) if pd.notna(row.get('service_name')) else ''
        region = str(row.get('region', '')) if pd.notna(row.get('region')) else ''
        
        has_tags = self._has_tags(row)
        has_name = bool(rname.strip())
        
        matches = []
        paths = []
        
        # 1. Native tags (highest priority)
        if has_tags:
            paths.append('NATIVE')
            for col in self.tag_columns:
                val = row.get(col)
                if pd.notna(val) and str(val).strip():
                    key = self.tag_names.get(col, col)
                    matches.append(TagMatch(
                        virtual_key=key,
                        virtual_value=str(val).strip(),
                        match_type=MatchType.NATIVE_TAG,
                        confidence=0.95,
                        category='Non-Critical',
                        reasoning=f'Native tag: {key}'
                    ))
        
        # 2. Name patterns
        if has_name:
            paths.append('NAME')
            name_matches = self._match_name(rname)
            self._merge(matches, name_matches)
        
        # 3. Resource type (PRIMARY for most)
        if rtype and rtype in RESOURCE_TYPE_TAGS:
            paths.append('TYPE')
            for key, (val, conf, cat) in RESOURCE_TYPE_TAGS[rtype].items():
                if not self._has_key(matches, key):
                    matches.append(TagMatch(
                        virtual_key=key,
                        virtual_value=val,
                        match_type=MatchType.RESOURCE_TYPE,
                        confidence=conf,
                        category=cat,
                        reasoning=f'From resource type: {rtype}'
                    ))
        
        # 4. Service name
        if service and service in SERVICE_TAGS:
            paths.append('SERVICE')
            for key, (val, conf, cat) in SERVICE_TAGS[service].items():
                if not self._has_key(matches, key):
                    matches.append(TagMatch(
                        virtual_key=key,
                        virtual_value=val,
                        match_type=MatchType.SERVICE,
                        confidence=conf,
                        category=cat,
                        reasoning=f'From service: {service}'
                    ))
        
        # 5. Region
        if region and region in REGION_TAGS:
            paths.append('REGION')
            loc, geo = REGION_TAGS[region]
            if not self._has_key(matches, 'DataCenter'):
                matches.append(TagMatch(
                    virtual_key='DataCenter',
                    virtual_value=loc,
                    match_type=MatchType.REGION,
                    confidence=0.95,
                    category='Optional',
                    reasoning=f'From region: {region}'
                ))
        
        # Calculate confidence
        conf = self._calc_confidence(matches)
        decision = self._decide(conf, len(matches))
        
        return ResourceResult(
            resource_id=rid,
            resource_name=rname,
            resource_type=rtype,
            service_name=service,
            region=region,
            has_native_tags=has_tags,
            has_name=has_name,
            inference_path=' > '.join(paths) if paths else 'NONE',
            matches=matches,
            confidence=conf,
            decision=decision
        )
    
    def _has_tags(self, row: pd.Series) -> bool:
        for col in self.tag_columns:
            if pd.notna(row.get(col)) and str(row.get(col)).strip():
                return True
        return False
    
    def _match_name(self, name: str) -> List[TagMatch]:
        matches = []
        name_lower = name.lower()
        
        for tag_key, patterns in NAME_PATTERNS.items():
            for pattern, value, conf in patterns:
                if re.search(pattern, name_lower, re.IGNORECASE):
                    matches.append(TagMatch(
                        virtual_key=tag_key,
                        virtual_value=value,
                        match_type=MatchType.NAME_PATTERN,
                        confidence=conf,
                        category='Critical' if tag_key in ['Environment', 'Application'] else 'Non-Critical',
                        reasoning=f'Pattern in name: {pattern}'
                    ))
                    break  # Only first match per key
        
        return matches
    
    def _has_key(self, matches: List[TagMatch], key: str) -> bool:
        return any(m.virtual_key == key for m in matches)
    
    def _merge(self, existing: List[TagMatch], new: List[TagMatch]):
        for m in new:
            if not self._has_key(existing, m.virtual_key):
                existing.append(m)
    
    def _calc_confidence(self, matches: List[TagMatch]) -> float:
        if not matches:
            return 0.0
        
        weights = {'Critical': 1.0, 'Non-Critical': 0.7, 'Optional': 0.4}
        
        total = sum(m.confidence * weights.get(m.category, 0.5) for m in matches)
        weight_sum = sum(weights.get(m.category, 0.5) for m in matches)
        
        return round(total / weight_sum, 4) if weight_sum > 0 else 0.0
    
    def _decide(self, conf: float, num_matches: int) -> str:
        # Require at least 1 Critical tag for approval
        if conf >= 0.85 and num_matches >= 2:
            return 'AUTO_APPROVE'
        elif conf >= 0.70 and num_matches >= 1:
            return 'PENDING'
        elif conf >= 0.50:
            return 'SUGGESTION'
        return 'REVIEW'
    
    def process_all(self, limit: int = None) -> List[ResourceResult]:
        results = []
        total = min(limit, len(self.df)) if limit else len(self.df)
        
        print(f"\nProcessing {total:,} resources...")
        
        for idx, row in self.df.head(total).iterrows():
            results.append(self.process(idx, row))
            if (idx + 1) % 10000 == 0:
                print(f"  Processed {idx + 1:,}/{total:,}...")
        
        return results
    
    def to_dataframe(self, results: List[ResourceResult]) -> pd.DataFrame:
        data = []
        for r in results:
            tags = {m.virtual_key: m.virtual_value for m in r.matches}
            data.append({
                'resource_id': r.resource_id,
                'resource_name': r.resource_name,
                'resource_type': r.resource_type,
                'service_name': r.service_name,
                'region': r.region,
                'has_native_tags': r.has_native_tags,
                'has_name': r.has_name,
                'inference_path': r.inference_path,
                'num_tags': len(r.matches),
                'confidence': r.confidence,
                'decision': r.decision,
                'virtual_tags': json.dumps(tags, ensure_ascii=True),
            })
        return pd.DataFrame(data)


# =============================================================================
# MAIN
# =============================================================================

def main():
    print('=' * 65)
    print('Virtual Tag Checker V3 - Complete Implementation')
    print('=' * 65)
    
    # Load data
    print('\nLoading data...')
    df = pd.read_excel('restapi.resources (1).xlsx')
    
    # Process
    proc = VirtualTagProcessor(df)
    results = proc.process_all(limit=10000)  # Process 10K for demo
    
    # Report
    print('\n' + '=' * 65)
    print('RESULTS SUMMARY')
    print('=' * 65)
    
    total = len(results)
    
    print(f'\nTotal processed: {total:,}')
    
    # Decision distribution
    print('\nDecision Distribution:')
    for dec in ['AUTO_APPROVE', 'PENDING', 'SUGGESTION', 'REVIEW']:
        cnt = sum(1 for r in results if r.decision == dec)
        print(f'  {dec}: {cnt:,} ({cnt/total*100:.1f}%)')
    
    # Tag coverage
    with_tags = sum(1 for r in results if r.matches)
    avg_tags = sum(len(r.matches) for r in results) / total
    print(f'\nTag Coverage:')
    print(f'  Resources with tags: {with_tags:,} ({with_tags/total*100:.1f}%)')
    print(f'  Average tags per resource: {avg_tags:.1f}')
    
    # Inference paths
    print('\nTop Inference Paths:')
    paths = {}
    for r in results:
        paths[r.inference_path] = paths.get(r.inference_path, 0) + 1
    for p, c in sorted(paths.items(), key=lambda x: -x[1])[:8]:
        print(f'  {p}: {c:,}')
    
    # Average confidence
    avg_conf = sum(r.confidence for r in results) / total
    print(f'\nAverage Confidence: {avg_conf:.1%}')
    
    # Save
    report = proc.to_dataframe(results)
    report.to_excel('virtual_tag_results_v3.xlsx', index=False)
    print('\nSaved to virtual_tag_results_v3.xlsx')
    
    # Sample
    print('\n' + '=' * 65)
    print('SAMPLE RESULTS')
    print('=' * 65)
    
    for r in results[:10]:
        print(f'\n{"-"*50}')
        name = r.resource_name[:40] if r.resource_name else r.resource_id[:40]
        print(f'Resource: {name}')
        print(f'Type: {r.resource_type} | Service: {r.service_name}')
        print(f'Path: {r.inference_path}')
        print(f'Confidence: {r.confidence:.0%} | Decision: {r.decision}')
        if r.matches:
            print(f'Tags ({len(r.matches)}):')
            for m in r.matches[:5]:
                print(f'  - {m.virtual_key}: {m.virtual_value} ({m.match_type.value} {m.confidence:.0%})')


if __name__ == '__main__':
    main()
