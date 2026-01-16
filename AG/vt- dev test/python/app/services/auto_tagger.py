"""
Auto Tagger Service - Python/Tornado Implementation
Orchestrates automated tagging using ML inference and rules
"""
from datetime import datetime
from typing import List, Dict
from sqlalchemy import select
from app.database.models import Resource, VirtualTag, Rule, MLInference, TagAudit
from app.services.ml_inference import MLInferenceService
from app.config import settings


class AutoTaggerService:
    """Service for automated tag application"""
    
    def __init__(self):
        self.ml_service = MLInferenceService()
        self.auto_apply_threshold = settings.auto_apply_threshold
        self.manual_review_threshold = settings.manual_review_threshold
    
    async def process_resource(self, resource: Resource, session) -> Dict:
        """
        Process a single resource for automated tagging
        Returns: Dictionary with applied tags and suggestions
        """
        tags_applied = 0
        suggestions_stored = 0
        
        # Step 1: Run ML Inference
        ml_result = await self.ml_service.infer_tags(resource)
        
        # Store ML inference result
        inference = MLInference(
            resource_id=resource.resource_id,
            model_version=ml_result['model_version'],
            predictions=ml_result['predictions']
        )
        session.add(inference)
        
        # Step 2: Get applicable rules
        rules_result = await session.execute(select(Rule))
        rules = rules_result.scalars().all()
        
        rule_tags = await self._apply_rules(resource, rules)
        
        # Step 3: Merge ML predictions and rules (rules take priority)
        final_tags = self._merge_tags(ml_result['predictions'], rule_tags)
        
        # Step 4: Apply tags based on confidence
        # First, get ALL existing tags for this resource to avoid duplicates
        existing_tags_result = await session.execute(
            select(VirtualTag).where(VirtualTag.resource_id == resource.resource_id)
        )
        existing_tags = existing_tags_result.scalars().all()
        # Normalize existing tag keys to lowercase for comparison
        existing_tags_map = {tag.tag_key.lower(): tag for tag in existing_tags}
        
        for tag_data in final_tags:
            confidence = tag_data.get('confidence', 0)
            tag_key = tag_data['tag_key'].lower()  # NORMALIZE TO LOWERCASE
            tag_value = tag_data['predicted_value']
            source = tag_data.get('source', 'INFERRED')
            
            # Skip if tag already exists for this resource (case-insensitive check)
            if tag_key in existing_tags_map:
                continue
            
            if confidence >= self.auto_apply_threshold:
                # Auto-apply high-confidence tags
                new_tag = VirtualTag(
                    resource_id=resource.resource_id,
                    tag_key=tag_key,  # Already lowercase
                    tag_value=tag_value,
                    source=source,
                    confidence=confidence,
                    auto_applied=True,
                    approval_status="PENDING",
                    created_by="auto-tagger"
                )
                session.add(new_tag)
                
                # Create audit log
                audit = TagAudit(
                    resource_id=resource.resource_id,
                    action="AUTO_APPLY",
                    tag_key=tag_key,
                    old_value=None,
                    new_value=tag_value,
                    source=source,
                    performed_by="auto-tagger",
                    tag_metadata={"confidence": confidence, "reasoning": tag_data.get('reasoning', '')}
                )
                session.add(audit)
                
                tags_applied += 1
            
            elif confidence >= self.manual_review_threshold:
                # Store as suggestion for manual review
                # Suggestions are stored in MLInference predictions
                suggestions_stored += 1
        
        return {
            "resource_id": resource.resource_id,
            "tags_applied": tags_applied,
            "suggestions_stored": suggestions_stored
        }
    
    async def process_batch(self, resources: List[Resource], session)  -> Dict:
        """
        Process multiple resources in batch
        Returns: Summary statistics
        """
        total_resources = len(resources)
        total_tags_applied = 0
        total_suggestions = 0
        
        for resource in resources:
            result = await self.process_resource(resource, session)
            total_tags_applied += result['tags_applied']
            total_suggestions += result['suggestions_stored']
        
        return {
            "resources_processed": total_resources,
            "tags_applied": total_tags_applied,
            "suggestions_stored": total_suggestions
        }
    
    async def _apply_rules(self, resource: Resource, rules: List[Rule]) -> List[Dict]:
        """Apply tagging rules to a resource"""
        rule_tags = []
        
        for rule in rules:
            if self._evaluate_condition(resource, rule.condition):
                rule_tags.append({
                    "tag_key": rule.tag_key.lower(),  # NORMALIZE TO LOWERCASE
                    "predicted_value": rule.tag_value,
                    "confidence": 1.0,  # Rules have 100% confidence
                    "source": "RULE_BASED",
                    "reasoning": f"Applied by rule: {rule.rule_name}",
                    "rule_id": rule.id
                })
        
        return rule_tags
    
    def _evaluate_condition(self, resource: Resource, condition: str) -> bool:
        """
        Evaluate rule condition against resource
        Simple string matching for demo (production would use proper parser)
        """
        resource_name = resource.name.lower()
        
        # Parse condition (simplified)
        if "CONTAINS" in condition:
            parts = condition.split("CONTAINS")
            if len(parts) == 2:
                field = parts[0].strip().lower()
                value = parts[1].strip().strip("'\"").lower()
                
                if field == "name":
                    return value in resource_name
        
        return False
    
    def _merge_tags(self, ml_predictions: List[Dict], rule_tags: List[Dict]) -> List[Dict]:
        """
        Merge ML predictions and rule-based tags
        Rules take priority over ML predictions
        Normalizes all tag keys to lowercase
        """
        # Build map of rule tags (normalized to lowercase)
        rule_map = {tag['tag_key'].lower(): tag for tag in rule_tags}
        
        # Build map of ML tags (normalized to lowercase)
        ml_map = {tag['tag_key'].lower(): tag for tag in ml_predictions}
        
        # Merge: rules override ML
        merged = {}
        
        # Add all rule tags first (highest priority)
        for key, tag in rule_map.items():
            merged[key] = tag
        
        # Add ML tags that don't conflict with rules
        for key, tag in ml_map.items():
            if key not in merged:
                # Normalize tag_key in the tag dict as well
                tag_copy = tag.copy()
                tag_copy['tag_key'] = key
                merged[key] = tag_copy
        
        return list(merged.values())
