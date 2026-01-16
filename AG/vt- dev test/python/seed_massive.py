"""
Seed 100,000 cloud resources for testing
"""
import asyncio
import random
import uuid
from sqlalchemy import select, func
from app.database import init_db, AsyncSessionLocal
from app.database.models import Resource


async def seed_massive_resources():
    """Generate 100,000 cloud resources"""
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Check current count
        result = await session.execute(select(func.count(Resource.id)))
        current_count = result.scalar()
        print(f"Current resources: {current_count}")
        
        # Configuration
        clouds = ["AWS", "GCP", "Azure"]
        aws_types = ["EC2 Instance", "S3 Bucket", "RDS Database", "Lambda Function", "ECS Task"]
        gcp_types = ["Compute Instance", "Cloud Storage", "Cloud SQL", "Cloud Function", "GKE Cluster"]
        azure_types = ["Virtual Machine", "Blob Storage", "SQL Database", "Function App", "AKS Cluster"]
        environments = ["prod", "dev", "staging", "test"]
        teams = ["backend", "frontend", "data", "devops", "ml"]
        cost_centers = ["engineering", "product", "data-analytics", "operations", "research"]
        
        target_count = 100000
        resources_to_add = target_count - current_count
        
        if resources_to_add <= 0:
            print(f"Already have {current_count} resources!")
            return
        
        print(f"Adding {resources_to_add} resources to reach {target_count}...")
        
        batch_size = 1000
        batches = resources_to_add // batch_size
        
        for batch_num in range(batches):
            resources = []
            
            for i in range(batch_size):
                resource_num = current_count + (batch_num * batch_size) + i + 1
                
                cloud = random.choice(clouds)
                
                # Select resource type based on cloud
                if cloud == "AWS":
                    resource_type = random.choice(aws_types)
                elif cloud == "GCP":
                    resource_type = random.choice(gcp_types)
                else:
                    resource_type = random.choice(azure_types)
                
                env = random.choice(environments)
                team = random.choice(teams)
                
                # Create unique resource ID
                if cloud == "AWS":
                    resource_id = f"arn:aws:{resource_type.split()[0].lower()}:us-east-1:123456789012:resource/{uuid.uuid4().hex[:8]}"
                elif cloud == "GCP":
                    resource_id = f"projects/project-{uuid.uuid4().hex[:8]}/zones/us-central1-a/instances/{uuid.uuid4().hex[:12]}"
                else:
                    resource_id = f"azure-{resource_type.split()[0].lower()}-{uuid.uuid4()}"
                
                name = f"{env}-{team}-{resource_type.split()[0].lower()}-{resource_num:06d}"
                
                # Generate native tags
                native_tags = {
                    "Environment": env.capitalize(),
                    "Team": team.capitalize(),
                }
                
                # Add cost center (70% probability)
                if random.random() > 0.3:
                    native_tags["CostCenter"] = random.choice(cost_centers)
                
                # Add owner (50% probability)
                if random.random() > 0.5:
                    native_tags["Owner"] = f"{team}-team@company.com"
                
                resource = Resource(
                    resource_id=resource_id,
                    name=name,
                    cloud=cloud,
                    account_id=str(random.randint(100000000000, 999999999999)),
                    resource_type=resource_type,
                    native_tags=native_tags
                )
                
                resources.append(resource)
            
            # Bulk insert batch
            session.add_all(resources)
            await session.commit()
            
            print(f"✓ Batch {batch_num + 1}/{batches} completed ({(batch_num + 1) * batch_size} resources)")
        
        # Final count
        result = await session.execute(select(func.count(Resource.id)))
        final_count = result.scalar()
        print(f"\n✅ DONE! Total resources: {final_count:,}")


if __name__ == "__main__":
    asyncio.run(seed_massive_resources())
