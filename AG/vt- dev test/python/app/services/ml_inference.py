"""
ML Inference Service - Python/Tornado Implementation
Predicts virtual tags based on resource patterns using rule-based logic
"""
from app.config import settings
from typing import Dict, List, Optional


class MLInferenceService:
    """ML Inference Service for tag prediction"""
    
    def __init__(self):
        self.model_version = settings.ml_model_version
        self.env_patterns = settings.environment_patterns
        self.team_patterns = settings.team_patterns
    
    async def infer_tags(self, resource) -> Dict:
        """
        Infer tags for a resource
        Returns: Dictionary with predictions and confidence scores
        """
        predictions = []
        resource_name = (resource.name or '').lower()
        resource_type = (resource.resource_type or '').lower()
        native_tags = resource.native_tags or {}
        
        # 1. Infer Environment Tag
        env_pred = self._predict_environment(resource_name, native_tags)
        if env_pred:
            predictions.append(env_pred)
        
        # 2. Infer Team Tag
        team_pred = self._predict_team(resource_name, resource_type, native_tags)
        if team_pred:
            predictions.append(team_pred)
        
        # 3. Infer Cost Center Tag (REQUIRED)
        cost_center_pred = self._predict_cost_center(env_pred, team_pred, native_tags)
        if cost_center_pred:
            predictions.append(cost_center_pred)
        
        # 4. Infer Owner Tag
        owner_pred = self._predict_owner(team_pred)
        if owner_pred:
            predictions.append(owner_pred)
        
        return {
            "resource_id": resource.resource_id,
            "model_version": self.model_version,
            "predictions": predictions
        }
    
    def _predict_environment(self, resource_name: str, native_tags: Dict) -> Optional[Dict]:
        """Predict environment tag"""
        # Check native tags first
        if native_tags.get('Environment') or native_tags.get('environment'):
            native_env = (native_tags.get('Environment') or native_tags.get('environment')).lower()
            return {
                "tag_key": "environment",
                "predicted_value": self._normalize_environment(native_env),
                "confidence": 0.98,
                "reasoning": "Normalized from native Environment tag",
                "source": "NATIVE_NORMALIZATION",
                "alternatives": []
            }
        
        # Pattern matching on resource name
        for env, patterns in self.env_patterns.items():
            for pattern in patterns:
                if pattern in resource_name:
                    return {
                        "tag_key": "environment",
                        "predicted_value": env,
                        "confidence": 0.95,
                        "reasoning": f"Resource name contains '{pattern}' keyword",
                        "source": "ML_PATTERN",
                        "alternatives": self._get_alternative_environments(env)
                    }
        
        # Default suggestion
        return {
            "tag_key": "environment",
            "predicted_value": "development",
            "confidence": 0.60,
            "reasoning": "Default suggestion based on common practice",
            "source": "ML_DEFAULT",
            "alternatives": [
                {"value": "staging", "confidence": 0.55},
                {"value": "production", "confidence": 0.50}
            ]
        }
    
    def _predict_team(self, resource_name: str, resource_type: str, native_tags: Dict) -> Optional[Dict]:
        """Predict team tag"""
        # Check native tags
        if native_tags.get('Team') or native_tags.get('team'):
            native_team = (native_tags.get('Team') or native_tags.get('team')).lower()
            return {
                "tag_key": "team",
                "predicted_value": native_team,
                "confidence": 0.98,
                "reasoning": "Extracted from native Team tag",
                "source": "NATIVE_NORMALIZATION",
                "alternatives": []
            }
        
        # Pattern matching on resource name
        for team, patterns in self.team_patterns.items():
            for pattern in patterns:
                if pattern in resource_name:
                    return {
                        "tag_key": "team",
                        "predicted_value": team,
                        "confidence": 0.85,
                        "reasoning": f"Resource name contains '{pattern}' keyword",
                        "source": "ML_PATTERN",
                        "alternatives": []
                    }
        
        # Resource type inference
        if 'db' in resource_type or 'database' in resource_type or 'storage' in resource_type:
            return {
                "tag_key": "team",
                "predicted_value": "backend",
                "confidence": 0.75,
                "reasoning": "Database/storage resource type suggests backend team",
                "source": "ML_TYPE_INFERENCE",
                "alternatives": [{"value": "devops", "confidence": 0.65}]
            }
        
        return None
    
    def _predict_cost_center(self, env_pred: Optional[Dict], team_pred: Optional[Dict], native_tags: Dict) -> Dict:
        """Predict cost center tag (REQUIRED - always returns a value)"""
        # Check native tags first
        for key in ['CostCenter', 'costCenter', 'cost-center']:
            if key in native_tags:
                return {
                    "tag_key": "cost-center",
                    "predicted_value": native_tags[key].lower(),
                    "confidence": 0.98,
                    "reasoning": "Extracted from native CostCenter tag",
                    "source": "NATIVE_NORMALIZATION",
                    "alternatives": []
                }
        
        # If no environment detected, provide default
        if not env_pred:
            return {
                "tag_key": "cost-center",
                "predicted_value": "engineering",
                "confidence": 0.65,
                "reasoning": "Default cost center (no environment or team detected)",
                "source": "ML_DEFAULT",
                "alternatives": [
                    {"value": "platform", "confidence": 0.60},
                    {"value": "production-ops", "confidence": 0.55}
                ]
            }
        
        env = env_pred['predicted_value']
        team = team_pred['predicted_value'] if team_pred else 'engineering'
        
        cost_center = "engineering"
        confidence = 0.80
        reasoning = "Default cost center for engineering resources"
        
        # Determine based on environment
        if env == "production":
            cost_center = "production-ops"
            confidence = 0.85
            reasoning = "Production resources typically under production-ops cost center"
        elif env in ["development", "test"]:
            cost_center = "engineering"
            confidence = 0.88
            reasoning = f"{env.capitalize()} resources under engineering cost center"
        elif env == "staging":
            cost_center = "engineering"
            confidence = 0.83
            reasoning = "Staging resources under engineering cost center"
        
        # Team takes priority over environment
        if team == "ml":
            cost_center = "research"
            confidence = 0.84
            reasoning = "ML team resources typically under research cost center"
        elif team == "devops":
            cost_center = "platform"
            confidence = 0.86
            reasoning = "DevOps team resources under platform cost center"
        
        return {
            "tag_key": "cost-center",
            "predicted_value": cost_center,
            "confidence": confidence,
            "reasoning": reasoning,
            "source": "ML_DERIVED",
            "alternatives": [
                {"value": "engineering", "confidence": 0.70},
                {"value": "platform", "confidence": 0.65},
                {"value": "production-ops", "confidence": 0.60}
            ]
        }
    
    def _predict_owner(self, team_pred: Optional[Dict]) -> Optional[Dict]:
        """Predict owner tag"""
        if not team_pred:
            return None
        
        team = team_pred['predicted_value']
        
        owner_map = {
            "frontend": "frontend-team@company.com",
            "backend": "backend-team@company.com",
            "data": "data-team@company.com",
            "devops": "devops-team@company.com",
            "ml": "ml-team@company.com"
        }
        
        owner = owner_map.get(team, "engineering@company.com")
        
        return {
            "tag_key": "owner",
            "predicted_value": owner,
            "confidence": 0.75,
            "reasoning": f"Inferred from team: {team}",
            "source": "ML_DERIVED",
            "alternatives": [{"value": "platform-team@company.com", "confidence": 0.65}]
        }
    
    def _normalize_environment(self, value: str) -> str:
        """Normalize environment values"""
        normalized = {
            "prod": "production",
            "prd": "production",
            "production": "production",
            "dev": "development",
            "develop": "development",
            "development": "development",
            "stg": "staging",
            "stage": "staging",
            "staging": "staging",
            "test": "test",
            "testing": "test",
            "qa": "test"
        }
        return normalized.get(value.lower(), value)
    
    def _get_alternative_environments(self, primary_env: str) -> List[Dict]:
        """Get alternative environment suggestions"""
        alternatives = {
            "production": [
                {"value": "staging", "confidence": 0.70},
                {"value": "development", "confidence": 0.65}
            ],
            "development": [
                {"value": "test", "confidence": 0.75},
                {"value": "staging", "confidence": 0.70}
            ],
            "staging": [
                {"value": "production", "confidence": 0.75},
                {"value": "test", "confidence": 0.70}
            ],
            "test": [
                {"value": "development", "confidence": 0.80},
                {"value": "staging", "confidence": 0.70}
            ]
        }
        return alternatives.get(primary_env, [])
