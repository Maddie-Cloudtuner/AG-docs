import tornado.web
import json
from sqlalchemy import select
from app.handlers.health import BaseHandler
from app.database import AsyncSessionLocal
from app.database.models import Rule


class RulesHandler(BaseHandler):
    """Handle /api/rules - GET all and POST new rules"""
    
    async def get(self):
        """GET all tagging rules"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Rule))
            rules = result.scalars().all()
            
            rules_data = []
            for rule in rules:
                rules_data.append({
                    "id": rule.id,
                    "rule_name": rule.rule_name,
                    "condition": rule.condition,
                    "tag_key": rule.tag_key,
                    "tag_value": rule.tag_value,
                    "scope": rule.scope,
                    "priority": rule.priority,
                    "created_by": rule.created_by,
                    "created_at": rule.created_at.isoformat() if rule.created_at else None
                })
            
            self.write_json(rules_data)
    
    async def post(self):
        """POST - Create new tagging rule"""
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            
            rule_name = data.get('rule_name')
            condition = data.get('condition')
            tag_key = data.get('tag_key')
            tag_value = data.get('tag_value')
            
            if not all([rule_name, condition, tag_key, tag_value]):
                self.write_error_json(400, "Missing required fields")
                return
            
            async with AsyncSessionLocal() as session:
                new_rule = Rule(
                    rule_name=rule_name,
                    condition=condition,
                    tag_key=tag_key,
                    tag_value=tag_value,
                    scope=data.get('scope', 'All'),
                    priority=data.get('priority', 1),
                    created_by=data.get('created_by', 'manual')
                )
                
                session.add(new_rule)
                await session.commit()
                await session.refresh(new_rule)
                
                self.write_json({
                    "id": new_rule.id,
                    "rule_name": new_rule.rule_name,
                    "message": "Rule created successfully"
                }, status_code=201)
        
        except Exception as e:
            self.write_error_json(400, str(e))


class RuleByIdHandler(BaseHandler):
    """Handle /api/rules/:id - GET, DELETE single rule"""
    
    async def get(self, rule_id):
        """GET single rule by ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Rule).where(Rule.id == int(rule_id))
            )
            rule = result.scalar_one_or_none()
            
            if not rule:
                self.write_error_json(404, "Rule not found")
                return
            
            self.write_json({
                "id": rule.id,
                "rule_name": rule.rule_name,
                "condition": rule.condition,
                "tag_key": rule.tag_key,
                "tag_value": rule.tag_value,
                "scope": rule.scope,
                "priority": rule.priority,
                "created_by": rule.created_by,
                "created_at": rule.created_at.isoformat() if rule.created_at else None
            })
    
    async def delete(self, rule_id):
        """DELETE rule"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Rule).where(Rule.id == int(rule_id))
            )
            rule = result.scalar_one_or_none()
            
            if not rule:
                self.write_error_json(404, "Rule not found")
                return
            
            await session.delete(rule)
            await session.commit()
            
            self.write_json({
                "message": f"Rule {rule_id} deleted successfully"
            })
