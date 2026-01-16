import tornado.web
import json
from datetime import datetime
from sqlalchemy import select, func
from app.handlers.health import BaseHandler
from app.database import AsyncSessionLocal
from app.database.models import Resource, MLInference, VirtualTag
from app.services.ml_inference import MLInferenceService


class MLInferHandler(BaseHandler):
    """Handle /api/ml/infer/:resource_id - Trigger ML inference"""
    
    async def post(self, resource_id):
        """POST - Trigger ML inference for a resource"""
        try:
            async with AsyncSessionLocal() as session:
                # Get resource
                result = await session.execute(
                    select(Resource).where(Resource.resource_id == resource_id)
                )
                resource = result.scalar_one_or_none()
                
                if not resource:
                    self.write_error_json(404, "Resource not found")
                    return
                
                # Run ML inference
                ml_service = MLInferenceService()
                inference_result = await ml_service.infer_tags(resource)
                
                # Store inference result
                new_inference = MLInference(
                    resource_id=resource_id,
                    model_version=inference_result['model_version'],
                    predictions=inference_result['predictions']
                )
                
                session.add(new_inference)
                await session.commit()
                await session.refresh(new_inference)
                
                self.write_json({
                    "resource_id": resource_id,
                    "model_version": inference_result['model_version'],
                    "predictions": inference_result['predictions'],
                    "predicted_at": new_inference.predicted_at.isoformat(),
                    "message": "ML inference completed successfully"
                })
        
        except Exception as e:
            self.write_error_json(500, str(e))


class MLSuggestionsHandler(BaseHandler):
    """Handle /api/ml/suggestions - GET all ML suggestions"""
    
    async def get(self):
        """GET all pending ML suggestions across resources"""
        async with AsyncSessionLocal() as session:
            # Get all ML inferences
            result = await session.execute(select(MLInference))
            inferences = result.scalars().all()
            
            # Get all virtual tags
            vt_result = await session.execute(select(VirtualTag))
            virtual_tags = vt_result.scalars().all()
            
            # Build map of existing tags
            existing_tags = {}
            for tag in virtual_tags:
                if tag.resource_id not in existing_tags:
                    existing_tags[tag.resource_id] = set()
                existing_tags[tag.resource_id].add(tag.tag_key)
            
            # Filter medium-confidence suggestions not already tagged
            suggestions = []
            for inference in inferences:
                resource_tags = existing_tags.get(inference.resource_id, set())
                
                for pred in inference.predictions:
                    # Medium confidence (70-89%) and not already a virtual tag
                    if 0.70 <= pred.get('confidence', 0) < 0.90:
                        if pred['tag_key'] not in resource_tags:
                            suggestions.append({
                                "resource_id": inference.resource_id,
                                "tag_key": pred['tag_key'],
                                "predicted_value": pred['predicted_value'],
                                "confidence": pred['confidence'],
                                "reasoning": pred.get('reasoning', ''),
                                "predicted_at": inference.predicted_at.isoformat() if inference.predicted_at else None
                            })
            
            self.write_json(suggestions)


class MLFeedbackHandler(BaseHandler):
    """Handle /api/ml/feedback - POST user feedback on predictions"""
    
    async def post(self):
        """POST - Submit user feedback on ML predictions"""
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            
            resource_id = data.get('resource_id')
            prediction = data.get('prediction')
            accepted = data.get('accepted', False)
            
            # Log feedback (in production, this would update ML model)
            feedback_log = {
                "resource_id": resource_id,
                "prediction": prediction,
                "accepted": accepted,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # TODO: Store feedback for ML model retraining
            
            self.write_json({
                "message": "Feedback received successfully",
                "feedback": feedback_log
            })
        
        except Exception as e:
            self.write_error_json(400, str(e))


class MLStatsHandler(BaseHandler):
    """Handle /api/ml/stats - GET ML inference statistics"""
    
    async def get(self):
        """GET ML inference statistics"""
        from app.config import settings
        
        async with AsyncSessionLocal() as session:
            # Count total inferences
            total_inferences_result = await session.execute(
                select(func.count(MLInference.id))
            )
            total_inferences = total_inferences_result.scalar()
            
            # Count ML-sourced tags
            ml_tags_result = await session.execute(
                select(func.count(VirtualTag.id)).where(
                    VirtualTag.source.in_(['INFERRED', 'ML_PATTERN', 'ML_DERIVED'])
                )
            )
            ml_tags_applied = ml_tags_result.scalar()
            
            # Count auto-applied tags
            auto_applied_result = await session.execute(
                select(func.count(VirtualTag.id)).where(VirtualTag.auto_applied == True)
            )
            auto_applied_count = auto_applied_result.scalar()
            
            self.write_json({
                "total_inferences": total_inferences or 0,
                "ml_tags_applied": ml_tags_applied or 0,
                "auto_applied_tags": auto_applied_count or 0,
                "model_version": settings.ml_model_version,
                "auto_apply_threshold": settings.auto_apply_threshold,
                "manual_review_threshold": settings.manual_review_threshold
            })
