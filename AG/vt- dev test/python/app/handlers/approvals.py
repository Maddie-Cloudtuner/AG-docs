"""
Approval Handler - Tag Approval Workflow
Handles pending tag approvals and approve/deny actions
"""
import logging
from tornado.web import RequestHandler
import json
from sqlalchemy import select, update
from app.database import AsyncSessionLocal
from app.database.models import VirtualTag, Resource, TagAudit
from app.handlers.health import BaseHandler

logger = logging.getLogger(__name__)


class PendingApprovalsHandler(BaseHandler):
    """Get all tags pending approval"""
    
    async def get(self):
        async with AsyncSessionLocal() as session:
            try:
                # Get all auto-applied tags with pending approval status
                result = await session.execute(
                    select(VirtualTag, Resource).join(
                        Resource, VirtualTag.resource_id == Resource.resource_id
                    ).where(
                        (VirtualTag.auto_applied == True) &
                        (VirtualTag.approval_status == "PENDING")
                    ).order_by(VirtualTag.created_at.desc())
                )
                
                pending_tags = []
                for tag, resource in result:
                    pending_tags.append({
                        "id": tag.id,
                        "resource_id": tag.resource_id,
                        "resource_name": resource.name,
                        "cloud": resource.cloud,
                        "resource_type": resource.resource_type,
                        "tag_key": tag.tag_key,
                        "tag_value": tag.tag_value,
                        "source": tag.source,
                        "confidence": tag.confidence,
                        "created_by": tag.created_by,
                        "created_at": tag.created_at.isoformat() if tag.created_at else None
                    })
                
                self.write_json({
                    "pending_approvals": pending_tags,
                    "count": len(pending_tags)
                })
                
            except Exception as e:
                logger.error(f"Error fetching pending approvals: {str(e)}")
                self.set_status(500)
                self.write_json({"error": str(e)})


class ApproveTagHandler(BaseHandler):
    """Approve or deny a tag"""
    
    async def post(self):
        async with AsyncSessionLocal() as session:
            try:
                data = json.loads(self.request.body)
                tag_id = data.get("tag_id")
                action = data.get("action")  # "APPROVED" or "DENIED"
                user = data.get("user", "admin")
                
                if not tag_id or action not in ["APPROVED", "DENIED"]:
                    self.set_status(400)
                    self.write_json({"error": "Invalid request. Need tag_id and action (APPROVED/DENIED)"})
                    return
                
                # Get the tag
                result = await session.execute(
                    select(VirtualTag).where(VirtualTag.id == tag_id)
                )
                tag = result.scalar_one_or_none()
                
                if not tag:
                    self.set_status(404)
                    self.write_json({"error": "Tag not found"})
                    return
                
                # Update approval status
                tag.approval_status = action
                
                # Create audit log
                audit = TagAudit(
                    resource_id=tag.resource_id,
                    action=action,
                    tag_key=tag.tag_key,
                    old_value="PENDING",
                    new_value=action,
                    source=tag.source,
                    performed_by=user,
                    tag_metadata={"tag_id": tag_id, "confidence": tag.confidence}
                )
                session.add(audit)
                
                await session.commit()
                
                self.write_json({
                    "message": f"Tag {action.lower()} successfully",
                    "tag_id": tag_id,
                    "status": action
                })
                
            except Exception as e:
                logger.error(f"Error approving/denying tag: {str(e)}")
                await session.rollback()
                self.set_status(500)
                self.write_json({"error": str(e)})


class BulkApproveHandler(BaseHandler):
    """Bulk approve or deny multiple tags"""
    
    async def post(self):
        async with AsyncSessionLocal() as session:
            try:
                data = json.loads(self.request.body)
                tag_ids = data.get("tag_ids", [])
                action = data.get("action")  # "APPROVED" or "DENIED"
                user = data.get("user", "admin")
                
                if not tag_ids or action not in ["APPROVED", "DENIED"]:
                    self.set_status(400)
                    self.write_json({"error": "Invalid request"})
                    return
                
                # Update all tags
                result = await session.execute(
                    update(VirtualTag)
                    .where(VirtualTag.id.in_(tag_ids))
                    .values(approval_status=action)
                )
                
                # Create audit logs
                for tag_id in tag_ids:
                    tag_result = await session.execute(
                        select(VirtualTag).where(VirtualTag.id == tag_id)
                    )
                    tag = tag_result.scalar_one_or_none()
                    
                    if tag:
                        audit = TagAudit(
                            resource_id=tag.resource_id,
                            action=action,
                            tag_key=tag.tag_key,
                            old_value="PENDING",
                            new_value=action,
                            source=tag.source,
                            performed_by=user,
                            tag_metadata={"tag_id": tag_id, "bulk_action": True}
                        )
                        session.add(audit)
                
                await session.commit()
                
                self.write_json({
                    "message": f"{len(tag_ids)} tags {action.lower()} successfully",
                    "count": len(tag_ids),
                    "status": action
                })
                
            except Exception as e:
                logger.error(f"Error bulk approving/denying tags: {str(e)}")
                await session.rollback()
                self.set_status(500)
                self.write_json({"error": str(e)})
