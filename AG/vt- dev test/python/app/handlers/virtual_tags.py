import tornado.web
import json
from datetime import datetime
from sqlalchemy import select, and_, delete
from app.handlers.health import BaseHandler
from app.database import AsyncSessionLocal
from app.database.models import VirtualTag, TagAudit, Resource


class VirtualTagsHandler(BaseHandler):
    """Handle /api/virtual-tags - GET all and POST new tags"""
    
    async def get(self):
        """GET all virtual tags"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(VirtualTag))
            tags = result.scalars().all()
            
            tags_data = []
            for tag in tags:
                tags_data.append({
                    "id": tag.id,
                    "resource_id": tag.resource_id,
                    "tag_key": tag.tag_key,
                    "tag_value": tag.tag_value,
                    "source": tag.source,
                    "confidence": tag.confidence,
                    "auto_applied": tag.auto_applied,
                    "created_by": tag.created_by,
                    "created_at": tag.created_at.isoformat() if tag.created_at else None
                })
            
            self.write_json(tags_data)
    
    async def post(self):
        """POST - Create new virtual tag"""
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            
            resource_id = data.get('resource_id')
            tag_key = data.get('tag_key')
            tag_value = data.get('tag_value')
            source = data.get('source', 'MANUAL')
            confidence = data.get('confidence', 1.0)
            created_by = data.get('created_by', 'manual')
            
            if not all([resource_id, tag_key, tag_value]):
                self.write_error_json(400, "Missing required fields")
                return
            
            async with AsyncSessionLocal() as session:
                # Check if resource exists
                resource_result = await session.execute(
                    select(Resource).where(Resource.resource_id == resource_id)
                )
                if not resource_result.scalar_one_or_none():
                    self.write_error_json(404, "Resource not found")
                    return
                
                # Check if tag already exists (UPSERT behavior)
                existing_result = await session.execute(
                    select(VirtualTag).where(and_(
                        VirtualTag.resource_id == resource_id,
                        VirtualTag.tag_key == tag_key
                    ))
                )
                existing_tag = existing_result.scalar_one_or_none()
                
                if existing_tag:
                    # Update existing tag
                    old_value = existing_tag.tag_value
                    existing_tag.tag_value = tag_value
                    existing_tag.source = source
                    existing_tag.confidence = confidence
                    existing_tag.updated_at = datetime.utcnow()
                    
                    # Create audit log
                    audit = TagAudit(
                        resource_id=resource_id,
                        action="UPDATE",
                        tag_key=tag_key,
                        old_value=old_value,
                        new_value=tag_value,
                        source=source,
                        performed_by=created_by
                    )
                    session.add(audit)
                    
                    await session.commit()
                    await session.refresh(existing_tag)
                    
                    self.write_json({
                        "id": existing_tag.id,
                        "resource_id": existing_tag.resource_id,
                        "tag_key": existing_tag.tag_key,
                        "tag_value": existing_tag.tag_value,
                        "message": "Virtual tag updated successfully"
                    })
                else:
                    # Create new tag
                    new_tag = VirtualTag(
                        resource_id=resource_id,
                        tag_key=tag_key,
                        tag_value=tag_value,
                        source=source,
                        confidence=confidence,
                        created_by=created_by
                    )
                    
                    session.add(new_tag)
                    
                    # Create audit log
                    audit = TagAudit(
                        resource_id=resource_id,
                        action="CREATE",
                        tag_key=tag_key,
                        old_value=None,
                        new_value=tag_value,
                        source=source,
                        performed_by=created_by
                    )
                    session.add(audit)
                    
                    await session.commit()
                    await session.refresh(new_tag)
                    
                    self.write_json({
                        "id": new_tag.id,
                        "resource_id": new_tag.resource_id,
                        "tag_key": new_tag.tag_key,
                        "tag_value": new_tag.tag_value,
                        "message": "Virtual tag created successfully"
                    }, status_code=201)
        
        except Exception as e:
            self.write_error_json(400, str(e))


class VirtualTagByIdHandler(BaseHandler):
    """Handle /api/virtual-tags/:id - GET, DELETE single tag"""
    
    async def get(self, tag_id):
        """GET single virtual tag by ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(VirtualTag).where(VirtualTag.id == int(tag_id))
            )
            tag = result.scalar_one_or_none()
            
            if not tag:
                self.write_error_json(404, "Virtual tag not found")
                return
            
            self.write_json({
                "id": tag.id,
                "resource_id": tag.resource_id,
                "tag_key": tag.tag_key,
                "tag_value": tag.tag_value,
                "source": tag.source,
                "confidence": tag.confidence,
                "auto_applied": tag.auto_applied,
                "created_by": tag.created_by,
                "created_at": tag.created_at.isoformat() if tag.created_at else None
            })
    
    async def delete(self, tag_id):
        """DELETE virtual tag"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(VirtualTag).where(VirtualTag.id == int(tag_id))
            )
            tag = result.scalar_one_or_none()
            
            if not tag:
                self.write_error_json(404, "Virtual tag not found")
                return
            
            # Create audit log before deletion
            audit = TagAudit(
                resource_id=tag.resource_id,
                action="DELETE",
                tag_key=tag.tag_key,
                old_value=tag.tag_value,
                new_value=None,
                source=tag.source,
                performed_by="manual"
            )
            session.add(audit)
            
            # Delete tag
            await session.delete(tag)
            await session.commit()
            
            self.write_json({
                "message": f"Virtual tag {tag_id} deleted successfully"
            })
