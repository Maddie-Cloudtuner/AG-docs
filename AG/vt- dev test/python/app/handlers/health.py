import tornado.web
import json
from datetime import datetime


class BaseHandler(tornado.web.RequestHandler):
    """Base handler with common functionality"""
    
    def set_default_headers(self):
        """Set CORS and content-type headers"""
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
    
    def options(self, *args):
        """Handle OPTIONS requests for CORS"""
        self.set_status(204)
        self.finish()
    
    def write_json(self, data, status_code=200):
        """Write JSON response"""
        self.set_status(status_code)
        self.write(json.dumps(data, default=str))
    
    def write_error_json(self, status_code, message):
        """Write error JSON response"""
        self.set_status(status_code)
        self.write(json.dumps({
            "error": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }))


class HealthHandler(BaseHandler):
    """Health check endpoint"""
    
    async def get(self):
        """GET /api/health"""
        from app.config import settings
        
        self.write_json({
            "status": "healthy",
            "message": "Virtual Tagging API is running",
            "automation_enabled": settings.enable_auto_tagging,
            "framework": "Tornado",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        })
