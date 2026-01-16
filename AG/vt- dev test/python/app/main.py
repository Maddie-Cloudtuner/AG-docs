"""
Tornado Application - Virtual Tagging System
Complete production-ready backend with automated tagging
"""
import tornado.ioloop
import tornado.web
import tornado.options
from tornado.options import define, options
import asyncio
import logging
import json

from app.config import settings
from app.database import init_db, close_db
from app.scheduler.jobs import start_scheduler, stop_scheduler

# Import all handlers
from app.handlers.resources import ResourcesHandler, ResourceByIdHandler, ResourceSuggestionsHandler, ResourceAuditHandler
from app.handlers.virtual_tags import VirtualTagsHandler, VirtualTagByIdHandler
from app.handlers.rules import RulesHandler, RuleByIdHandler
from app.handlers.ml import MLInferHandler, MLSuggestionsHandler, MLFeedbackHandler, MLStatsHandler
from app.handlers.scheduler import SchedulerTriggerHandler, SchedulerStatusHandler, SchedulerJobsHandler
from app.handlers.approvals import PendingApprovalsHandler, ApproveTagHandler, BulkApproveHandler
from app.handlers.csv_upload import CSVUploadHandler, CSVExportHandler
from app.handlers.health import HealthHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define command-line options
define("port", default=8000, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")


class Application(tornado.web.Application):
    """Main Tornado application"""
    
    def __init__(self):
        handlers = [
            # Health check
            (r"/api/health", HealthHandler),
            
            # Resources
            (r"/api/resources", ResourcesHandler),
            (r"/api/resources/([^/]+)", ResourceByIdHandler),
            (r"/api/resources/([^/]+)/suggestions", ResourceSuggestionsHandler),
            (r"/api/resources/([^/]+)/audit", ResourceAuditHandler),
            
            # Virtual Tags
            (r"/api/virtual-tags", VirtualTagsHandler),
            (r"/api/virtual-tags/([0-9]+)", VirtualTagByIdHandler),
            
            # Rules
            (r"/api/rules", RulesHandler),
            (r"/api/rules/([0-9]+)", RuleByIdHandler),
            
            # ML
            (r"/api/ml/infer/([^/]+)", MLInferHandler),
            (r"/api/ml/suggestions", MLSuggestionsHandler),
            (r"/api/ml/feedback", MLFeedbackHandler),
            (r"/api/ml/stats", MLStatsHandler),
            
            # Scheduler
            (r"/api/scheduler/trigger", SchedulerTriggerHandler),
            (r"/api/scheduler/status", SchedulerStatusHandler),
            (r"/api/scheduler/jobs", SchedulerJobsHandler),
            
            # Approvals
            (r"/api/approvals/pending", PendingApprovalsHandler),
            (r"/api/approvals/approve", ApproveTagHandler),
            (r"/api/approvals/bulk", BulkApproveHandler),
            
            # CSV Import/Export
            (r"/api/csv/upload", CSVUploadHandler),
            (r"/api/csv/export", CSVExportHandler),
        ]
        
        settings_dict = {
            "debug": options.debug,
            "autoreload": options.debug,
            "default_handler_class": NotFoundHandler,
        }
        
        super().__init__(handlers, **settings_dict)
        logger.info("✅ Tornado application initialized")


class NotFoundHandler(tornado.web.RequestHandler):
    """404 handler"""
    def prepare(self):
        self.set_status(404)
        self.write({"error": "Not Found", "message": "The requested endpoint does not exist"})
        self.finish()


async def startup():
    """Application startup tasks"""
    logger.info("🚀 Starting Virtual Tagging API...")
    await init_db()
    start_scheduler()
    logger.info("="*60)
    logger.info("  ✅ VIRTUAL TAGGING API STARTED")
    logger.info("  🌐 Port: %d", options.port)
    logger.info("  🐍 Framework: Tornado")
    logger.info("  🤖 Automation: ENABLED")
    logger.info("="*60)


async def shutdown():
    """Application shutdown tasks"""
    logger.info("🛑 Shutting down...")
    stop_scheduler()
    await close_db()
    logger.info("✅ Application shut down successfully")


def make_app():
    """Create and configure the Tornado application"""
    return Application()


async def main():
    """Main application entry point"""
    tornado.options.parse_command_line()
    
    # Startup tasks
    await startup()
    
    # Create and start application
    app = make_app()
    app.listen(options.port, address=settings.host)
    
    logger.info(f"Server running on http://{settings.host}:{options.port}")
    
    # Keep running until shutdown
    shutdown_event = asyncio.Event()
    
    try:
        await shutdown_event.wait()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Received shutdown signal")
    finally:
        await shutdown()


if __name__ == "__main__":
    asyncio.run(main())
