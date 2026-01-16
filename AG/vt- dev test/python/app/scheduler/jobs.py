"""
Scheduler Jobs - Python/Tornado Implementation
APScheduler jobs for automated resource discovery and tagging
"""
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database import AsyncSessionLocal
from app.database.models import Resource, SchedulerJob
from app.services.resource_discovery import ResourceDiscoveryService
from app.services.auto_tagger import AutoTaggerService
from app.config import settings

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()

# Service instances
discovery_service = ResourceDiscoveryService()
auto_tagger_service = AutoTaggerService()


async def resource_discovery_job():
    """
    Main job: Discover resources and apply automated tagging
    Runs every 1 minute
    """
    job_name = "discovery"
    started_at = datetime.utcnow()
    
    logger.info("🔍 [SCHEDULER] ===== Resource Discovery & Auto-Tagging Started =====")
    logger.info(f"[SCHEDULER] Time: {started_at.isoformat()}")
    
    async with AsyncSessionLocal() as session:
        # Create job record
        job_record = SchedulerJob(
            job_name=job_name,
            status="RUNNING",
            started_at=started_at
        )
        session.add(job_record)
        await session.commit()
        
        try:
            # Step 0: Discover NEW resources (simulate continuous discovery)
            logger.info("[SCHEDULER] Step 0: Discovering new cloud resources...")
            new_resources = await discovery_service.discover_resources(session)
            logger.info(f"[SCHEDULER] ✨ Discovered {len(new_resources)} new resources!")
            
            # Step 1: Get untagged resources
            logger.info("[SCHEDULER] Step 1: Finding untagged resources...")
            untagged_resources = await discovery_service.get_untagged_resources(session)
            logger.info(f"[SCHEDULER] Found {len(untagged_resources)} untagged resources")
            
            # Step 2: Get resources needing ML inference
            logger.info("[SCHEDULER] Step 2: Finding resources needing ML inference...")
            need_inference = await discovery_service.get_resources_needing_inference(session)
            logger.info(f"[SCHEDULER] Found {len(need_inference)} resources needing inference")
            
            # Step 3: Process resources (limited batch)
            batch_size = min(settings.max_resources_per_batch, len(untagged_resources))
            if batch_size > 0:
                logger.info(f"[SCHEDULER] Step 3: Processing {batch_size} resources...")
                batch = untagged_resources[:batch_size]
                result = await auto_tagger_service.process_batch(batch, session)
                
                await session.commit()
                
                # Update job record
                job_record.status = "COMPLETED"
                job_record.completed_at = datetime.utcnow()
                job_record.resources_processed = result['resources_processed']
                job_record.tags_applied = result['tags_applied']
                
                await session.commit()
                
                logger.info(f"[AUTO-TAGGER] Completed: {result['tags_applied']} tags applied, "
                          f"{result['suggestions_stored']} suggestions stored")
            else:
                logger.info("[SCHEDULER] No untagged resources to process")
                job_record.status = "COMPLETED"
                job_record.completed_at = datetime.utcnow()
                job_record.resources_processed = 0
                job_record.tags_applied = 0
                await session.commit()
            
            logger.info("✅ [SCHEDULER] ===== Resource Discovery & Auto-Tagging Completed =====")
            
        except Exception as e:
            logger.error(f"❌ [SCHEDULER] Error in discovery job: {str(e)}")
            job_record.status = "FAILED"
            job_record.completed_at = datetime.utcnow()
            job_record.errors = str(e)
            await session.commit()


async def re_evaluation_job():
    """
    Re-evaluate tags with low confidence
    Runs hourly
    """
    logger.info("🔄 [SCHEDULER] Running tag re-evaluation job...")
    
    async with AsyncSessionLocal() as session:
        from app.database.models import VirtualTag
        from sqlalchemy import select
        
        # Find low-confidence auto-applied tags
        result = await session.execute(
            select(VirtualTag).where(
                (VirtualTag.confidence < 0.90) &
                (VirtualTag.auto_applied == True)
            )
        )
        low_confidence_tags = result.scalars().all()
        
        logger.info(f"[SCHEDULER] Found {len(low_confidence_tags)} low-confidence tags for re-evaluation")
        
        # In production, would re-run ML inference
        # For now, just log
        
    logger.info("✅ [SCHEDULER] Re-evaluation job completed")


async def cleanup_job():
    """
    Cleanup old audit records and ML inferences
    Runs daily at 2 AM
    """
    logger.info("🗑️  [SCHEDULER] Running cleanup job...")
    
    async with AsyncSessionLocal() as session:
        from app.database.models import TagAudit
        from sqlalchemy import select, delete
        
        # Keep only last 1000 audit records
        count_result = await session.execute(select(func.count(TagAudit.id)))
        total_count = count_result.scalar()
        
        if total_count > 1000:
            # Delete oldest records
            to_delete = total_count - 1000
            oldest_result = await session.execute(
                select(TagAudit.id)
                .order_by(TagAudit.timestamp.asc())
                .limit(to_delete)
            )
            oldest_ids = [row[0] for row in oldest_result]
            
            await session.execute(
                delete(TagAudit).where(TagAudit.id.in_(oldest_ids))
            )
            await session.commit()
            
            logger.info(f"[SCHEDULER] Deleted {to_delete} old audit records")
        
    logger.info("✅ [SCHEDULER] Cleanup job completed")


def start_scheduler():
    """Start the APScheduler"""
    if scheduler.running:
        logger.warning("Scheduler already running")
        return
    
    logger.info("🚀 [SCHEDULER] Initializing automated tagging scheduler...")
    
    # Discovery job - every 2 minutes
    scheduler.add_job(
        resource_discovery_job,
        CronTrigger(minute='*/2'),
        id='discovery_job',
        name='Resource Discovery & Auto-Tagging',
        replace_existing=True
    )
    logger.info("[SCHEDULER] Discovery interval: */2 * * * *")
    
    # Re-evaluation job - every hour
    scheduler.add_job(
        re_evaluation_job,
        CronTrigger(hour='*'),
        id='re_evaluation_job',
        name='Tag Re-evaluation',
        replace_existing=True
    )
    logger.info("[SCHEDULER] Re-evaluation interval: 0 * * * *")
    
    # Cleanup job - daily at 2 AM
    scheduler.add_job(
        cleanup_job,
        CronTrigger(hour=2, minute=0),
        id='cleanup_job',
        name='Audit Cleanup',
        replace_existing=True
    )
    logger.info("[SCHEDULER] Cleanup interval: 0 2 * * *")
    
    # Start scheduler
    scheduler.start()
    logger.info("✅ [SCHEDULER] All cron jobs scheduled successfully")
    
    # Run initial discovery after 5 seconds
    scheduler.add_job(
        resource_discovery_job,
        'date',
        run_date=datetime.now() + timedelta(seconds=5),
        id='initial_discovery'
    )
    logger.info("[SCHEDULER] Scheduled initial discovery job")


def stop_scheduler():
    """Stop the APScheduler"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("✅ [SCHEDULER] Stopped successfully")


async def trigger_discovery_job():
    """Manually trigger discovery job"""
    logger.info("🔍 [SCHEDULER] Manually triggering discovery job...")
    await resource_discovery_job()
    return {"status": "completed"}


def get_scheduler_info():
    """Get scheduler status and configuration"""
    jobs = scheduler.get_jobs()
    
    job_stats = {}
    for job in jobs:
        if job.id in ['discovery_job', 're_evaluation_job', 'cleanup_job']:
            job_stats[job.id.replace('_job', '')] = {
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
    
    return {
        "enabled": settings.enable_auto_tagging,
        "active_jobs": len(jobs),
        "intervals": {
            "discovery": "*/2 * * * *",
            "reEvaluation": "0 * * * *",
            "cleanup": "0 2 * * *"
        },
        "job_stats": job_stats
    }
