"""
Resource Discovery Service - Python/Tornado Implementation
Simulates cloud resource discovery with continuous new resource generation
"""
import uuid
import random
from datetime import datetime
from sqlalchemy import select, func
from app.database.models import Resource
from typing import List, Dict


class ResourceDiscoveryService:
    """Service for discovering cloud resources"""
    
    def __init__(self):
        # Cloud providers and resource types for simulation
        self.clouds = ["AWS", "GCP", "Azure"]
        self.aws_types = ["EC2 Instance", "S3 Bucket", "RDS Database", "Lambda Function", "ECS Task"]
        self.gcp_types = ["Compute Instance", "Cloud Storage", "Cloud SQL", "Cloud Function", "GKE Cluster"]
        self.azure_types = ["Virtual Machine", "Blob Storage", "SQL Database", "Function App", "AKS Cluster"]
        self.environments = ["prod", "dev", "staging", "test"]
        self.teams = ["backend", "frontend", "data", "devops", "ml"]
    
    async def simulate_new_resource_discovery(self, session, count: int = 20) -> List[Resource]:
        """
        Simulate discovering new cloud resources
        Creates 20 new resources each time it's called
        """
        new_resources = []
        
        # Get current resource count for unique naming
        result = await session.execute(select(func.count(Resource.id)))
        current_count = result.scalar()
        
        for i in range(count):
            cloud = random.choice(self.clouds)
            
            # Select resource type based on cloud
            if cloud == "AWS":
                resource_type = random.choice(self.aws_types)
            elif cloud == "GCP":
                resource_type = random.choice(self.gcp_types)
            else:
                resource_type = random.choice(self.azure_types)
            
            # Generate resource details
            env = random.choice(self.environments)
            team = random.choice(self.teams)
            resource_num = current_count + i + 1
            
            # Create unique resource ID
            if cloud == "AWS":
                resource_id = f"arn:aws:{resource_type.split()[0].lower()}:us-east-1:123456789012:resource/{uuid.uuid4().hex[:8]}"
            elif cloud == "GCP":
                resource_id = f"projects/project-{uuid.uuid4().hex[:8]}/zones/us-central1-a/instances/{uuid.uuid4().hex[:12]}"
            else:
                resource_id = f"azure-{resource_type.split()[0].lower()}-{uuid.uuid4()}"
            
            # Create resource name with environment and team hints
            name = f"{env}-{team}-{resource_type.split()[0].lower()}-{resource_num:04d}"
            
            # Generate realistic native tags
            native_tags = {
                "Environment": env.capitalize(),
                "Team": team.capitalize(),
            }
            
            # Add cost center tag with some probability
            if random.random() > 0.3:
                cost_centers = ["engineering", "product", "data-analytics", "operations", "research"]
                native_tags["CostCenter"] = random.choice(cost_centers)
            
            # Add owner tag with some probability
            if random.random() > 0.5:
                native_tags["Owner"] = f"{team}-team@company.com"
            
            # Create resource
            new_resource = Resource(
                resource_id=resource_id,
                name=name,
                cloud=cloud,
                account_id=str(random.randint(100000000000, 999999999999)),
                resource_type=resource_type,
                native_tags=native_tags
            )
            
            session.add(new_resource)
            new_resources.append(new_resource)
        
        await session.commit()
        return new_resources
    
    async def discover_resources(self, session) -> List[Resource]:
        """
        Discover new resources from cloud providers
        In production, this would call AWS/GCP/Azure APIs
        For demo, we simulate discovering new resources
        """
        # Simulate new resource discovery
        new_resources = await self.simulate_new_resource_discovery(session, count=20)
        return new_resources
    
    async def get_untagged_resources(self, session) -> List[Resource]:
        """
        Get resources that don't have virtual tags
        These need ML inference and auto-tagging
        """
        from app.database.models import VirtualTag
        
        # Get all resources
        all_resources_result = await session.execute(select(Resource))
        all_resources = all_resources_result.scalars().all()
        
        # Get all resources with virtual tags
        tagged_resources_result = await session.execute(select(VirtualTag.resource_id).distinct())
        tagged_resource_ids = {row[0] for row in tagged_resources_result}
        
        # Filter untagged resources
        untagged = [r for r in all_resources if r.resource_id not in tagged_resource_ids]
        
        return untagged
    
    async def get_resources_needing_inference(self, session) -> List[Resource]:
        """
        Get resources that need ML inference
        (resources without recent ML inferences)
        """
        from app.database.models import MLInference
        
        # Get all resources
        all_resources_result = await session.execute(select(Resource))
        all_resources = all_resources_result.scalars().all()
        
        # Get resources with recent inferences
        inferred_result = await session.execute(select(MLInference.resource_id).distinct())
        inferred_ids = {row[0] for row in inferred_result}
        
        # Filter resources needing inference
        need_inference = [r for r in all_resources if r.resource_id not in inferred_ids]
        
        return need_inference
