"""
CSV Upload Handler - Bulk Import Tags
Allows users to upload CSV file with resource tags
"""
import logging
import csv
import io
from tornado.web import RequestHandler
from app.database import AsyncSessionLocal
from app.database.models import Resource, VirtualTag, TagAudit
from app.handlers.health import BaseHandler
from sqlalchemy import select

logger = logging.getLogger(__name__)


class CSVUploadHandler(BaseHandler):
    """Handle CSV upload for bulk tag import"""
    
    async def post(self):
        """
        Upload CSV with format:
        resource_name,tag_key,tag_value,confidence
        
        Example CSV:
        resource_name,tag_key,tag_value,confidence
        prod-api-server-001,environment,production,1.0
        prod-api-server-001,team,backend,1.0
        prod-api-server-001,cost-center,engineering,1.0
        """
        try:
            # Get uploaded file
            if 'file' not in self.request.files:
                self.set_status(400)
                self.write_json({"error": "No file uploaded"})
                return
            
            file_info = self.request.files['file'][0]
            filename = file_info['filename']
            file_body = file_info['body'].decode('utf-8')
            
            # Validate file extension
            if not filename.endswith('.csv'):
                self.set_status(400)
                self.write_json({"error": "Only CSV files are supported"})
                return
            
            # Parse CSV
            csv_file = io.StringIO(file_body)
            csv_reader = csv.DictReader(csv_file)
            
            # Validate headers
            required_headers = {'resource_name', 'tag_key', 'tag_value'}
            headers = set(csv_reader.fieldnames or [])
            
            if not required_headers.issubset(headers):
                self.set_status(400)
                self.write_json({
                    "error": "Invalid CSV format",
                    "message": f"CSV must contain columns: {', '.join(required_headers)}",
                    "found": list(headers)
                })
                return
            
            # Process rows
            async with AsyncSessionLocal() as session:
                stats = {
                    "total_rows": 0,
                    "resources_found": 0,
                    "resources_not_found": 0,
                    "tags_created": 0,
                    "tags_updated": 0,
                    "errors": []
                }
                
                for row_num, row in enumerate(csv_reader, start=2):
                    stats["total_rows"] += 1
                    
                    try:
                        resource_name = row.get('resource_name', '').strip()
                        tag_key = row.get('tag_key', '').strip()
                        tag_value = row.get('tag_value', '').strip()
                        confidence = float(row.get('confidence', '1.0'))
                        
                        if not resource_name or not tag_key or not tag_value:
                            stats["errors"].append(f"Row {row_num}: Missing required fields")
                            continue
                        
                        # Find resource by name (case-insensitive)
                        result = await session.execute(
                            select(Resource).where(
                                Resource.name.ilike(f"%{resource_name}%")
                            )
                        )
                        resource = result.scalar_one_or_none()
                        
                        if not resource:
                            stats["resources_not_found"] += 1
                            stats["errors"].append(f"Row {row_num}: Resource '{resource_name}' not found")
                            continue
                        
                        stats["resources_found"] += 1
                        
                        # Check if tag already exists
                        tag_result = await session.execute(
                            select(VirtualTag).where(
                                (VirtualTag.resource_id == resource.resource_id) &
                                (VirtualTag.tag_key == tag_key)
                            )
                        )
                        existing_tag = tag_result.scalar_one_or_none()
                        
                        if existing_tag:
                            # Update existing tag
                            old_value = existing_tag.tag_value
                            existing_tag.tag_value = tag_value
                            existing_tag.confidence = confidence
                            existing_tag.source = "CSV_IMPORT"
                            existing_tag.approval_status = "APPROVED"  # CSV imports are pre-approved
                            
                            # Create audit log
                            audit = TagAudit(
                                resource_id=resource.resource_id,
                                action="CSV_UPDATE",
                                tag_key=tag_key,
                                old_value=old_value,
                                new_value=tag_value,
                                source="CSV_IMPORT",
                                performed_by="csv-upload",
                                tag_metadata={"filename": filename, "row": row_num}
                            )
                            session.add(audit)
                            stats["tags_updated"] += 1
                        else:
                            # Create new tag
                            new_tag = VirtualTag(
                                resource_id=resource.resource_id,
                                tag_key=tag_key,
                                tag_value=tag_value,
                                source="CSV_IMPORT",
                                confidence=confidence,
                                auto_applied=False,
                                approval_status="APPROVED",  # CSV imports are pre-approved
                                created_by="csv-upload"
                            )
                            session.add(new_tag)
                            
                            # Create audit log
                            audit = TagAudit(
                                resource_id=resource.resource_id,
                                action="CSV_CREATE",
                                tag_key=tag_key,
                                old_value=None,
                                new_value=tag_value,
                                source="CSV_IMPORT",
                                performed_by="csv-upload",
                                tag_metadata={"filename": filename, "row": row_num}
                            )
                            session.add(audit)
                            stats["tags_created"] += 1
                    
                    except Exception as e:
                        stats["errors"].append(f"Row {row_num}: {str(e)}")
                        logger.error(f"Error processing row {row_num}: {str(e)}")
                
                await session.commit()
            
            logger.info(f"CSV import completed: {stats}")
            
            self.write_json({
                "message": "CSV import completed",
                "filename": filename,
                "stats": stats
            })
        
        except Exception as e:
            logger.error(f"CSV upload error: {str(e)}")
            self.set_status(500)
            self.write_json({"error": str(e)})


class CSVExportHandler(BaseHandler):
    """Export current tags as CSV"""
    
    async def get(self):
        """
        Export all virtual tags as CSV
        Query params:
        - resource_name: filter by resource name
        - tag_key: filter by tag key
        """
        try:
            resource_name_filter = self.get_argument('resource_name', None)
            tag_key_filter = self.get_argument('tag_key', None)
            
            async with AsyncSessionLocal() as session:
                # Build query
                query = select(VirtualTag, Resource).join(
                    Resource, VirtualTag.resource_id == Resource.resource_id
                )
                
                if resource_name_filter:
                    query = query.where(Resource.name.ilike(f"%{resource_name_filter}%"))
                
                if tag_key_filter:
                    query = query.where(VirtualTag.tag_key == tag_key_filter)
                
                result = await session.execute(query)
                tags = result.all()
                
                # Generate CSV
                output = io.StringIO()
                csv_writer = csv.writer(output)
                
                # Write header
                csv_writer.writerow([
                    'resource_name', 'resource_id', 'cloud', 'resource_type',
                    'tag_key', 'tag_value', 'confidence', 'source', 'approval_status'
                ])
                
                # Write data
                for tag, resource in tags:
                    csv_writer.writerow([
                        resource.name,
                        resource.resource_id,
                        resource.cloud,
                        resource.resource_type,
                        tag.tag_key,
                        tag.tag_value,
                        tag.confidence,
                        tag.source,
                        tag.approval_status
                    ])
                
                csv_content = output.getvalue()
                
                # Set headers for file download
                self.set_header('Content-Type', 'text/csv')
                self.set_header('Content-Disposition', 'attachment; filename="virtual_tags_export.csv"')
                self.write(csv_content)
        
        except Exception as e:
            logger.error(f"CSV export error: {str(e)}")
            self.set_status(500)
            self.write_json({"error": str(e)})
