"""
Backend Integration Service for Virtual Tagging
=================================================
Integrates with your existing backend infrastructure.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging

# Import local modules
from db_models import (
    init_database, 
    CloudResource, 
    VirtualTag, 
    TagSchema, 
    NativeTagMapping,
    ResourceTypeRule,
    ServiceRule,
    TagAudit
)
from tag_mappings import (
    NATIVE_KEY_TO_SCHEMA_KEY,
    VALUE_NORMALIZATIONS,
    RESOURCE_TYPE_DEFAULTS,
    SERVICE_DEFAULTS,
    REGION_DEFAULTS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VirtualTagService:
    """
    Main service class for virtual tagging operations.
    Can be integrated into FastAPI/Flask backend.
    """
    
    def __init__(self, db_url: str = 'sqlite:///virtual_tags.db'):
        """Initialize with database connection"""
        self.engine, self.session = init_database(db_url)
        self._load_schema_from_db()
    
    def _load_schema_from_db(self):
        """Load schema for value validation"""
        self.schema_values = {}
        self.schema_category = {}
        
        schemas = self.session.query(TagSchema).all()
        for s in schemas:
            if s.tag_key not in self.schema_values:
                self.schema_values[s.tag_key] = set()
                self.schema_category[s.tag_key] = s.tag_category
            self.schema_values[s.tag_key].add(s.tag_value)
    
    # =========================================================================
    # CORE TAGGING OPERATIONS
    # =========================================================================
    
    def check_native_tags(self, native_tags: Dict[str, str]) -> List[Dict]:
        """
        Check native tags against schema (1:1 mapping).
        
        Args:
            native_tags: {"Env": "prod", "Project": "Analytics", ...}
        
        Returns:
            List of virtual tag matches with confidence scores
        """
        results = []
        
        for native_key, native_value in native_tags.items():
            # Map native key to schema key
            schema_key = NATIVE_KEY_TO_SCHEMA_KEY.get(native_key, native_key)
            
            # Normalize value
            normalized_value = VALUE_NORMALIZATIONS.get(native_value, native_value)
            
            # Determine confidence
            confidence = 0.98
            if schema_key in self.schema_values:
                if normalized_value not in self.schema_values[schema_key]:
                    confidence = 0.85
            
            results.append({
                'virtual_key': schema_key,
                'virtual_value': normalized_value,
                'source': 'NATIVE',
                'confidence': confidence,
                'native_key': native_key,
                'native_value': native_value,
                'reasoning': f'Mapped from native tag: {native_key}={native_value}'
            })
        
        return results
    
    def infer_from_resource_type(self, resource_type: str) -> List[Dict]:
        """Get default tags for a resource type"""
        results = []
        defaults = RESOURCE_TYPE_DEFAULTS.get(resource_type, {})
        
        for key, value in defaults.items():
            results.append({
                'virtual_key': key,
                'virtual_value': value,
                'source': 'RESOURCE_TYPE',
                'confidence': 0.80,
                'reasoning': f'Default for resource type: {resource_type}'
            })
        
        return results
    
    def infer_from_service(self, service_name: str) -> List[Dict]:
        """Get default tags for a service"""
        results = []
        defaults = SERVICE_DEFAULTS.get(service_name, {})
        
        for key, value in defaults.items():
            results.append({
                'virtual_key': key,
                'virtual_value': value,
                'source': 'SERVICE',
                'confidence': 0.75,
                'reasoning': f'Default for service: {service_name}'
            })
        
        return results
    
    def process_resource(
        self, 
        resource_id: str,
        native_tags: Dict[str, str] = None,
        resource_type: str = None,
        service_name: str = None,
        region: str = None
    ) -> Dict:
        """
        Complete processing of a single resource.
        Returns virtual tags with confidence and decision.
        """
        all_tags = []
        paths = []
        
        # 1. Check native tags
        if native_tags:
            native_results = self.check_native_tags(native_tags)
            if native_results:
                paths.append('NATIVE')
                all_tags.extend(native_results)
        
        existing_keys = {t['virtual_key'] for t in all_tags}
        
        # 2. Resource type inference
        if resource_type:
            type_tags = self.infer_from_resource_type(resource_type)
            for t in type_tags:
                if t['virtual_key'] not in existing_keys:
                    all_tags.append(t)
                    existing_keys.add(t['virtual_key'])
            if type_tags:
                paths.append('TYPE')
        
        # 3. Service inference
        if service_name:
            svc_tags = self.infer_from_service(service_name)
            for t in svc_tags:
                if t['virtual_key'] not in existing_keys:
                    all_tags.append(t)
                    existing_keys.add(t['virtual_key'])
            if svc_tags:
                paths.append('SERVICE')
        
        # 4. Region
        if region and region in REGION_DEFAULTS:
            if 'DataCenter' not in existing_keys:
                all_tags.append({
                    'virtual_key': 'DataCenter',
                    'virtual_value': REGION_DEFAULTS[region],
                    'source': 'REGION',
                    'confidence': 0.95,
                    'reasoning': f'From region: {region}'
                })
                paths.append('REGION')
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(all_tags)
        decision = self._get_decision(confidence, len(all_tags))
        
        return {
            'resource_id': resource_id,
            'virtual_tags': all_tags,
            'path': ' > '.join(paths),
            'confidence': confidence,
            'decision': decision
        }
    
    def _calculate_confidence(self, tags: List[Dict]) -> float:
        if not tags:
            return 0.0
        
        weights = {'Critical': 1.0, 'Non-Critical': 0.7, 'Optional': 0.4}
        total = sum(t['confidence'] * weights.get(self.schema_category.get(t['virtual_key'], 'Non-Critical'), 0.5) for t in tags)
        weight_sum = sum(weights.get(self.schema_category.get(t['virtual_key'], 'Non-Critical'), 0.5) for t in tags)
        
        return round(total / weight_sum, 4) if weight_sum > 0 else 0.0
    
    def _get_decision(self, confidence: float, num_tags: int) -> str:
        if confidence >= 0.90 and num_tags >= 2:
            return 'AUTO_APPROVE'
        elif confidence >= 0.75:
            return 'PENDING'
        elif confidence >= 0.50:
            return 'SUGGESTION'
        return 'REVIEW'
    
    # =========================================================================
    # DATABASE OPERATIONS
    # =========================================================================
    
    def save_virtual_tags(self, resource_id: str, tags: List[Dict], user: str = 'system') -> List[str]:
        """Save virtual tags to database"""
        saved_ids = []
        
        for tag in tags:
            vt = VirtualTag(
                resource_id=resource_id,
                tag_key=tag['virtual_key'],
                tag_value=tag['virtual_value'],
                source=tag['source'],
                confidence=tag['confidence'],
                reasoning=tag.get('reasoning', '')
            )
            self.session.add(vt)
            
            # Audit trail
            audit = TagAudit(
                resource_id=resource_id,
                action='CREATE',
                tag_key=tag['virtual_key'],
                new_value=tag['virtual_value'],
                performed_by=user
            )
            self.session.add(audit)
            saved_ids.append(vt.id)
        
        self.session.commit()
        return saved_ids
    
    def get_virtual_tags(self, resource_id: str) -> List[Dict]:
        """Get virtual tags for a resource"""
        tags = self.session.query(VirtualTag).filter(
            VirtualTag.resource_id == resource_id
        ).all()
        
        return [{
            'key': t.tag_key,
            'value': t.tag_value,
            'source': t.source,
            'confidence': t.confidence,
            'reasoning': t.reasoning
        } for t in tags]
    
    def load_schema_from_excel(self, filepath: str):
        """Load schema from Excel file into database"""
        import pandas as pd
        df = pd.read_excel(filepath)
        
        for _, row in df.iterrows():
            schema = TagSchema(
                cloud_provider=str(row.get('cloud_provider', 'All')),
                resource_scope=str(row.get('resource_scope', 'Global')),
                tag_category=str(row['tag_category']),
                tag_key=str(row['tag_key']),
                tag_value=str(row['tag_value']),
                is_case_sensitive=bool(row.get('is_case_sensitive', True))
            )
            self.session.merge(schema)
        
        self.session.commit()
        self._load_schema_from_db()
        logger.info(f"Loaded {len(df)} schema definitions")


# =============================================================================
# REST API ENDPOINTS (FastAPI example)
# =============================================================================

def create_fastapi_app():
    """Create FastAPI app with virtual tagging endpoints"""
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    
    app = FastAPI(title="Virtual Tagging API")
    service = VirtualTagService()
    
    class ProcessRequest(BaseModel):
        resource_id: str
        native_tags: Optional[Dict[str, str]] = None
        resource_type: Optional[str] = None
        service_name: Optional[str] = None
        region: Optional[str] = None
    
    @app.post("/api/v1/virtual-tags/process")
    def process_resource(req: ProcessRequest):
        """Process a resource and return virtual tags"""
        result = service.process_resource(
            resource_id=req.resource_id,
            native_tags=req.native_tags,
            resource_type=req.resource_type,
            service_name=req.service_name,
            region=req.region
        )
        return result
    
    @app.get("/api/v1/resources/{resource_id}/virtual-tags")
    def get_tags(resource_id: str):
        """Get virtual tags for a resource"""
        return service.get_virtual_tags(resource_id)
    
    @app.post("/api/v1/virtual-tags/check-native")
    def check_native(native_tags: Dict[str, str]):
        """Check native tags against schema"""
        return service.check_native_tags(native_tags)
    
    return app


if __name__ == '__main__':
    # Demo usage
    print("Virtual Tag Service Demo")
    print("=" * 50)
    
    service = VirtualTagService()
    
    # Example: Process a resource
    result = service.process_resource(
        resource_id='i-1234567890abcdef0',
        native_tags={'Env': 'prod', 'Project': 'Analytics'},
        resource_type='Instance',
        service_name='AmazonEC2',
        region='ap-south-1'
    )
    
    print(f"\nResource: {result['resource_id']}")
    print(f"Path: {result['path']}")
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"Decision: {result['decision']}")
    print("\nVirtual Tags:")
    for t in result['virtual_tags']:
        print(f"  {t['virtual_key']}: {t['virtual_value']} ({t['source']})")
