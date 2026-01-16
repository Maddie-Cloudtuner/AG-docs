import tornado.web
import json
from sqlalchemy import select, desc
from app.handlers.health import BaseHandler
from app.database import AsyncSessionLocal
from app.database.models import SchedulerJob
from app.scheduler.jobs import trigger_discovery_job, get_scheduler_info


class SchedulerTriggerHandler(BaseHandler):
    """Handle /api/scheduler/trigger - Manually trigger scheduler jobs"""
    
    async def post(self):
        """POST - Manually trigger a scheduler job"""
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            job_name = data.get('job')
            
            if job_name == 'discovery':
                # Trigger discovery job manually
                result = await trigger_discovery_job()
                self.write_json({
                    "message": "Discovery job triggered successfully",
                    "result": result
                })
            else:
                self.write_error_json(400, f"Unknown job: {job_name}")
        
        except Exception as e:
            self.write_error_json(500, str(e))


class SchedulerStatusHandler(BaseHandler):
    """Handle /api/scheduler/status - GET scheduler status"""
    
    async def get(self):
        """GET scheduler status and configuration"""
        try:
            scheduler_info = get_scheduler_info()
            self.write_json(scheduler_info)
        except Exception as e:
            self.write_error_json(500, str(e))


class SchedulerJobsHandler(BaseHandler):
    """Handle /api/scheduler/jobs - GET job execution history"""
    
    async def get(self):
        """GET recent scheduler job executions"""
        try:
            # Get limit from query parameter
            limit = self.get_argument('limit', '20')
            limit = int(limit)
            
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(SchedulerJob)
                    .order_by(desc(SchedulerJob.started_at))
                    .limit(limit)
                )
                jobs = result.scalars().all()
                
                jobs_data = []
                for job in jobs:
                    jobs_data.append({
                        "id": job.id,
                        "job_name": job.job_name,
                        "status": job.status,
                        "started_at": job.started_at.isoformat() if job.started_at else None,
                        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                        "resources_processed": job.resources_processed,
                        "tags_applied": job.tags_applied,
                        "errors": job.errors
                    })
                
                self.write_json({"jobs": jobs_data})
        
        except Exception as e:
            self.write_error_json(500, str(e))
