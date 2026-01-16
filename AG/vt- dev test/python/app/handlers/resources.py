import tornado.web
import json
from sqlalchemy import select, and_
from app.handlers.health import BaseHandler
from app.database import AsyncSessionLocal
from app.database.models import Resource, VirtualTag, MLInference, TagAudit


class ResourcesHandler(BaseHandler):
    """Handle /api/resources - GET all resources and POST new resource"""
    
    async def get(self):
        """GET all resources with virtual tags and ML suggestions (PAGINATED)"""
        # Get pagination parameters
        limit = int(self.get_argument('limit', '50'))  # Default 50 per page
        offset = int(self.get_argument('offset', '0'))  # Default start at 0
        
        # Limit max to 1000 per page
        limit = min(limit, 1000)
        
        async with AsyncSessionLocal() as session:
            # Get total count
            from sqlalchemy import func
            count_result = await session.execute(select(func.count(Resource.id)))
            total_count = count_result.scalar()
            
            # Get paginated resources
            result = await session.execute(
                select(Resource)
                .order_by(Resource.id)
                .limit(limit)
                .offset(offset)
            )
            resources = result.scalars().all()
            
            # Get resource IDs for this page
            resource_ids = [r.resource_id for r in resources]
            
            # Get virtual tags only for current page resources
            vt_result = await session.execute(
                select(VirtualTag).where(VirtualTag.resource_id.in_(resource_ids))
            )
            virtual_tags = vt_result.scalars().all()
            
            # Get ML inferences only for current page resources
            ml_result = await session.execute(
                select(MLInference).where(MLInference.resource_id.in_(resource_ids))
            )
            ml_inferences = ml_result.scalars().all()
            
            # Build response
            resources_data = []
            for resource in resources:
                # Get virtual tags for this resource
                resource_tags = {}
                tags_metadata = []
                
                for tag in virtual_tags:
                    if tag.resource_id == resource.resource_id:
                        resource_tags[tag.tag_key] = tag.tag_value
                        tags_metadata.append({
                            "key": tag.tag_key,
                            "value": tag.tag_value,
                            "source": tag.source,
                            "confidence": tag.confidence,
                            "auto_applied": tag.auto_applied
                        })
                
                # Get ML suggestions (medium confidence 70-89%)
                ml_suggestions = []
                for inference in ml_inferences:
                    if inference.resource_id == resource.resource_id:
                        for pred in inference.predictions:
                            if 0.70 <= pred.get('confidence', 0) < 0.90:
                                # Check if not already a virtual tag
                                if pred['tag_key'] not in resource_tags:
                                    ml_suggestions.append(pred)
                
                resources_data.append({
                    "id": resource.id,
                    "resource_id": resource.resource_id,
                    "name": resource.name,
                    "cloud": resource.cloud,
                    "account_id": resource.account_id,
                    "resource_type": resource.resource_type,
                    "native_tags": resource.native_tags,
                    "virtual_tags": resource_tags,
                    "virtual_tags_metadata": tags_metadata,
                    "ml_suggestions": ml_suggestions,
                    "created_at": resource.created_at.isoformat() if resource.created_at else None
                })
            
            # Return paginated response
            self.write_json({
                "resources": resources_data,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total_count
                }
            })
    
    async def post(self):
        """POST - Add new dummy resource"""
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            
            async with AsyncSessionLocal() as session:
                new_resource = Resource(
                    resource_id=data.get('resource_id'),
                    name=data.get('name'),
                    cloud=data.get('cloud'),
                    account_id=data.get('account_id'),
                    resource_type=data.get('resource_type'),
                    native_tags=data.get('native_tags', {})
                )
                
                session.add(new_resource)
                await session.commit()
                await session.refresh(new_resource)
                
                self.write_json({
                    "id": new_resource.id,
                    "resource_id": new_resource.resource_id,
                    "name": new_resource.name,
                    "message": "Resource created successfully"
                }, status_code=201)
        
        except Exception as e:
            self.write_error_json(400, str(e))


class ResourceByIdHandler(BaseHandler):
    """Handle /api/resources/:id - GET single resource"""
    
    async def get(self, resource_id):
        """GET single resource by ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Resource).where(Resource.resource_id == resource_id)
            )
            resource = result.scalar_one_or_none()
            
            if not resource:
                self.write_error_json(404, "Resource not found")
                return
            
            # Get virtual tags
            vt_result = await session.execute(
                select(VirtualTag).where(VirtualTag.resource_id == resource_id)
            )
            virtual_tags = vt_result.scalars().all()
            
            resource_tags = {}
            for tag in virtual_tags:
                resource_tags[tag.tag_key] = tag.tag_value
            
            self.write_json({
                "id": resource.id,
                "resource_id": resource.resource_id,
                "name": resource.name,
                "cloud": resource.cloud,
                "account_id": resource.account_id,
                "resource_type": resource.resource_type,
                "native_tags": resource.native_tags,
                "virtual_tags": resource_tags,
                "created_at": resource.created_at.isoformat() if resource.created_at else None
            })


class ResourceSuggestionsHandler(BaseHandler):
    """Handle /api/resources/:id/suggestions - GET ML suggestions for resource"""
    
    async def get(self, resource_id):
        """GET ML suggestions for a specific resource"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(MLInference).where(MLInference.resource_id == resource_id)
            )
            inference = result.scalar_one_or_none()
            
            if not inference:
                self.write_json([])
                return
            
            # Filter medium-confidence predictions
            suggestions = [
                pred for pred in inference.predictions
                if 0.70 <= pred.get('confidence', 0) < 0.90
            ]
            
            self.write_json(suggestions)


class ResourceAuditHandler(BaseHandler):
    """Handle /api/resources/:id/audit - GET audit trail for resource"""
    
    async def get(self, resource_id):
        """GET audit trail for a specific resource"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(TagAudit)
                .where(TagAudit.resource_id == resource_id)
                .order_by(TagAudit.timestamp.desc())
            )
            audit_records = result.scalars().all()
            
            audit_data = []
            for record in audit_records:
                audit_data.append({
                    "id": record.id,
                    "resource_id": record.resource_id,
                    "action": record.action,
                    "tag_key": record.tag_key,
                    "old_value": record.old_value,
                    "new_value": record.new_value,
                    "source": record.source,
                    "performed_by": record.performed_by,
                    "metadata": record.tag_metadata,  # Changed from record.metadata
                    "timestamp": record.timestamp.isoformat() if record.timestamp else None
                })
            
            self.write_json(audit_data)
