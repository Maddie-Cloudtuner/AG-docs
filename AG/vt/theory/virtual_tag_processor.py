"""
Complete Virtual Tag Processor - Production Ready
==================================================
1:1 Native Tag Mapping with Database Support
"""

import pandas as pd
import base64
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Import mappings
from tag_mappings import (
    NATIVE_KEY_TO_SCHEMA_KEY,
    VALUE_NORMALIZATIONS, 
    RESOURCE_TYPE_DEFAULTS,
    SERVICE_DEFAULTS,
    REGION_DEFAULTS
)


@dataclass
class VirtualTagResult:
    key: str
    value: str
    source: str  # NATIVE, INFERRED, RESOURCE_TYPE, SERVICE, REGION
    confidence: float
    reasoning: str
    native_key: Optional[str] = None
    native_value: Optional[str] = None


@dataclass
class ProcessingResult:
    resource_id: str
    name: str
    resource_type: str
    service_name: str
    region: str
    has_native_tags: bool
    path: str
    tags: List[VirtualTagResult] = field(default_factory=list)
    confidence: float = 0.0
    decision: str = ""


class VirtualTagProcessor:
    """
    Complete processor with 1:1 native tag mapping.
    
    Flow:
    1. Check native tags → Map to schema keys (1:1)
    2. Normalize values → Match against allowed values
    3. Apply resource type defaults
    4. Apply service defaults
    5. Apply region defaults
    6. Calculate confidence and make decision
    """
    
    def __init__(self, schema_df: pd.DataFrame = None):
        """Initialize with schema for value validation"""
        self.schema_values = {}  # tag_key → set of allowed values
        self.schema_category = {}  # tag_key → category
        
        if schema_df is not None:
            self._load_schema(schema_df)
        
        self.tag_decoder = {}  # Cached column → decoded key
    
    def _load_schema(self, df: pd.DataFrame):
        """Load schema for value validation"""
        for _, row in df.iterrows():
            key = row['tag_key']
            value = row['tag_value']
            category = row['tag_category']
            
            if key not in self.schema_values:
                self.schema_values[key] = set()
                self.schema_category[key] = category
            self.schema_values[key].add(value)
    
    def decode_tag_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Decode Base64 tag column names"""
        if self.tag_decoder:
            return self.tag_decoder
            
        for col in df.columns:
            if col.startswith('tags.'):
                enc = col.replace('tags.', '')
                try:
                    self.tag_decoder[col] = base64.b64decode(enc).decode('utf-8')
                except:
                    self.tag_decoder[col] = enc
        return self.tag_decoder
    
    def check_native_tags(self, row: pd.Series, decoder: Dict[str, str]) -> List[VirtualTagResult]:
        """
        Check native tags and map 1:1 to schema keys.
        This is the YES path in the workflow.
        """
        results = []
        
        for col, native_key in decoder.items():
            value = row.get(col)
            if pd.isna(value) or str(value).strip() == '':
                continue
            
            native_value = str(value).strip()
            
            # Step 1: Map native key to schema key (1:1 mapping)
            schema_key = NATIVE_KEY_TO_SCHEMA_KEY.get(native_key, native_key)
            
            # Step 2: Normalize value if mapping exists
            normalized_value = VALUE_NORMALIZATIONS.get(native_value, native_value)
            
            # Step 3: Check if value is in schema's allowed values
            confidence = 0.98  # Default high confidence for native tags
            
            if schema_key in self.schema_values:
                if normalized_value in self.schema_values[schema_key]:
                    confidence = 0.98  # Exact match
                elif native_value in self.schema_values[schema_key]:
                    normalized_value = native_value
                    confidence = 0.98
                else:
                    confidence = 0.85  # Key matches but value not in schema
            
            results.append(VirtualTagResult(
                key=schema_key,
                value=normalized_value,
                source='NATIVE',
                confidence=confidence,
                reasoning=f"Native tag: {native_key}={native_value}",
                native_key=native_key,
                native_value=native_value
            ))
        
        return results
    
    def apply_resource_type_defaults(self, resource_type: str, existing_keys: set) -> List[VirtualTagResult]:
        """Apply default tags based on resource type"""
        results = []
        
        defaults = RESOURCE_TYPE_DEFAULTS.get(resource_type, {})
        for key, value in defaults.items():
            if key not in existing_keys:
                results.append(VirtualTagResult(
                    key=key,
                    value=value,
                    source='RESOURCE_TYPE',
                    confidence=0.80,
                    reasoning=f"Default for resource type: {resource_type}"
                ))
        
        return results
    
    def apply_service_defaults(self, service_name: str, existing_keys: set) -> List[VirtualTagResult]:
        """Apply default tags based on service"""
        results = []
        
        defaults = SERVICE_DEFAULTS.get(service_name, {})
        for key, value in defaults.items():
            if key not in existing_keys:
                results.append(VirtualTagResult(
                    key=key,
                    value=value,
                    source='SERVICE',
                    confidence=0.75,
                    reasoning=f"Default for service: {service_name}"
                ))
        
        return results
    
    def apply_region_defaults(self, region: str, existing_keys: set) -> List[VirtualTagResult]:
        """Apply region-based tags"""
        results = []
        
        if region in REGION_DEFAULTS and 'DataCenter' not in existing_keys:
            results.append(VirtualTagResult(
                key='DataCenter',
                value=REGION_DEFAULTS[region],
                source='REGION',
                confidence=0.95,
                reasoning=f"From region: {region}"
            ))
        
        return results
    
    def calculate_confidence(self, tags: List[VirtualTagResult]) -> float:
        """Calculate weighted confidence based on tag categories"""
        if not tags:
            return 0.0
        
        category_weights = {'Critical': 1.0, 'Non-Critical': 0.7, 'Optional': 0.4}
        
        total = 0.0
        weight_sum = 0.0
        
        for tag in tags:
            cat = self.schema_category.get(tag.key, 'Non-Critical')
            weight = category_weights.get(cat, 0.5)
            total += tag.confidence * weight
            weight_sum += weight
        
        return round(total / weight_sum, 4) if weight_sum > 0 else 0.0
    
    def get_decision(self, confidence: float, num_tags: int) -> str:
        """Decision based on confidence and coverage"""
        if confidence >= 0.90 and num_tags >= 2:
            return 'AUTO_APPROVE'
        elif confidence >= 0.75:
            return 'PENDING'
        elif confidence >= 0.50:
            return 'SUGGESTION'
        return 'REVIEW'
    
    def process_resource(self, row: pd.Series, decoder: Dict[str, str]) -> ProcessingResult:
        """Process a single resource"""
        
        # Extract info
        rid = str(row.get('cloud_resource_id', ''))
        name = str(row.get('name', '')) if pd.notna(row.get('name')) else ''
        rtype = str(row.get('resource_type', '')) if pd.notna(row.get('resource_type')) else ''
        service = str(row.get('service_name', '')) if pd.notna(row.get('service_name')) else ''
        region = str(row.get('region', '')) if pd.notna(row.get('region')) else ''
        
        all_tags = []
        paths = []
        
        # Step 1: Check native tags (1:1 mapping)
        native_tags = self.check_native_tags(row, decoder)
        has_native = len(native_tags) > 0
        
        if has_native:
            paths.append('NATIVE')
            all_tags.extend(native_tags)
        
        # Get existing keys to avoid duplicates
        existing_keys = {t.key for t in all_tags}
        
        # Step 2: Apply resource type defaults
        if rtype:
            type_tags = self.apply_resource_type_defaults(rtype, existing_keys)
            if type_tags:
                paths.append('TYPE')
                all_tags.extend(type_tags)
                existing_keys.update(t.key for t in type_tags)
        
        # Step 3: Apply service defaults
        if service:
            svc_tags = self.apply_service_defaults(service, existing_keys)
            if svc_tags:
                paths.append('SERVICE')
                all_tags.extend(svc_tags)
                existing_keys.update(t.key for t in svc_tags)
        
        # Step 4: Apply region defaults
        if region:
            reg_tags = self.apply_region_defaults(region, existing_keys)
            if reg_tags:
                paths.append('REGION')
                all_tags.extend(reg_tags)
        
        # Calculate confidence and decision
        confidence = self.calculate_confidence(all_tags)
        decision = self.get_decision(confidence, len(all_tags))
        
        return ProcessingResult(
            resource_id=rid,
            name=name,
            resource_type=rtype,
            service_name=service,
            region=region,
            has_native_tags=has_native,
            path=' > '.join(paths) if paths else 'NONE',
            tags=all_tags,
            confidence=confidence,
            decision=decision
        )
    
    def process_dataframe(self, df: pd.DataFrame, limit: int = None) -> List[ProcessingResult]:
        """Process entire dataframe"""
        decoder = self.decode_tag_columns(df)
        results = []
        total = min(limit, len(df)) if limit else len(df)
        
        print(f"Processing {total:,} resources...")
        
        for idx, row in df.head(total).iterrows():
            results.append(self.process_resource(row, decoder))
            if (idx + 1) % 10000 == 0:
                print(f"  Processed {idx+1:,}/{total:,}...")
        
        return results
    
    def to_dataframe(self, results: List[ProcessingResult]) -> pd.DataFrame:
        """Convert results to DataFrame for export"""
        data = []
        for r in results:
            tags_dict = {t.key: t.value for t in r.tags}
            native_tags = {t.native_key: t.native_value for t in r.tags if t.native_key}
            
            data.append({
                'resource_id': r.resource_id,
                'name': r.name,
                'resource_type': r.resource_type,
                'service_name': r.service_name,
                'region': r.region,
                'has_native_tags': r.has_native_tags,
                'path': r.path,
                'num_tags': len(r.tags),
                'confidence': r.confidence,
                'decision': r.decision,
                'virtual_tags': json.dumps(tags_dict, ensure_ascii=True),
                'native_tags_found': json.dumps(native_tags, ensure_ascii=True),
            })
        
        return pd.DataFrame(data)


def main():
    print('=' * 65)
    print('Virtual Tag Processor - 1:1 Native Tag Mapping')
    print('=' * 65)
    
    # Load data
    print('\nLoading schema...')
    schema_df = pd.read_excel('cloud_resource_tags_complete 1.xlsx')
    print(f'  Schema loaded: {len(schema_df)} definitions')
    
    print('\nLoading resources...')
    resources_df = pd.read_excel('restapi.resources (1).xlsx')
    print(f'  Resources loaded: {len(resources_df):,}')
    
    # Initialize processor with schema
    processor = VirtualTagProcessor(schema_df)
    
    # Process
    results = processor.process_dataframe(resources_df, limit=5000)
    
    # Generate report
    report = processor.to_dataframe(results)
    
    # Stats
    print('\n' + '=' * 65)
    print('RESULTS')
    print('=' * 65)
    
    total = len(results)
    with_native = sum(1 for r in results if r.has_native_tags)
    with_tags = sum(1 for r in results if r.tags)
    
    print(f'\nTotal processed: {total:,}')
    print(f'With native tags: {with_native} ({with_native/total*100:.1f}%)')
    print(f'With virtual tags: {with_tags} ({with_tags/total*100:.1f}%)')
    
    print('\nDecisions:')
    for dec in ['AUTO_APPROVE', 'PENDING', 'SUGGESTION', 'REVIEW']:
        cnt = sum(1 for r in results if r.decision == dec)
        print(f'  {dec}: {cnt:,} ({cnt/total*100:.1f}%)')
    
    print(f'\nAverage confidence: {sum(r.confidence for r in results)/total:.1%}')
    
    # Save
    report.to_excel('virtual_tags_final.xlsx', index=False)
    print('\nSaved to virtual_tags_final.xlsx')
    
    # Show samples with native tags
    print('\n' + '=' * 65)
    print('SAMPLE - Resources WITH Native Tags')
    print('=' * 65)
    
    native_samples = [r for r in results if r.has_native_tags][:5]
    for r in native_samples:
        print(f'\n{"─"*50}')
        print(f'Resource: {r.name or r.resource_id[:50]}')
        print(f'Type: {r.resource_type} | Service: {r.service_name}')
        print(f'Path: {r.path} | Confidence: {r.confidence:.0%} | {r.decision}')
        print(f'Virtual Tags:')
        for t in r.tags[:6]:
            src = f'[{t.source}]'
            if t.native_key:
                print(f'  {t.key}: {t.value} {src} <- {t.native_key}={t.native_value}')
            else:
                print(f'  {t.key}: {t.value} {src}')


if __name__ == '__main__':
    main()
