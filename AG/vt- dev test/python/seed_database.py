"""
Database Seeder - Generate 1000 mock resources across AWS, GCP, Azure
"""
import asyncio
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy import select
from app.database import AsyncSessionLocal, init_db
from app.database.models import Resource, Rule

# Cloud configurations
CLOUDS = ["AWS", "GCP", "Azure"]
ENVIRONMENTS = ["prod", "dev", "staging", "test"]
TEAMS = ["frontend", "backend", "data", "devops", "ml", "analytics"]
SERVICES = ["web", "api", "database", "cache", "queue", "analytics", "ml-model", "microservice"]

RESOURCE_TYPES = {
    "AWS": ["ec2", "s3", "rds", "lambda", "dynamodb", "elb", "eks", "ecs", "cloudfront", "redshift"],
    "GCP": ["compute", "storage", "sql", "function", "gke", "bigquery", "dataproc", "dataflow"],
    "Azure": ["vm", "blob", "sql", "function", "aks", "cosmosdb", "synapse", "databricks"]
}

COST_CENTERS = [
    "production-ops",
    "engineering",
    "data-analytics",
    "platform",
    "research",
    "marketing",
    "sales"
]

OWNERS = [
    "frontend-team@company.com",
    "backend-team@company.com",
    "data-team@company.com",
    "devops-team@company.com",
    "ml-team@company.com",
    "platform-team@company.com"
]

APPLICATIONS = ["ecommerce", "analytics", "crm", "billing", "reporting", "monitoring", "ml-platform"]


def generate_resource_id(cloud: str, resource_type: str, index: int) -> str:
    """Generate realistic cloud-specific resource IDs"""
    if cloud == "AWS":
        return f"aws-{resource_type}-{str(uuid.uuid4())[:8]}"
    elif cloud == "GCP":
        return f"gcp-{resource_type}-{str(index).zfill(16)}"
    else:  # Azure
        return f"azure-{resource_type}-{str(uuid.uuid4())}"


def generate_account_id(cloud: str) -> str:
    """Generate cloud-specific account IDs"""
    if cloud == "AWS":
        return str(random.randint(100000000000, 999999999999))
    elif cloud == "GCP":
        return f"my-gcp-project-{random.randint(1000, 9999)}"
    else:  # Azure
        return f"subscription-{str(uuid.uuid4())}"


def generate_native_tags(env: str, team: str) -> dict:
    """Generate realistic native tags"""
    tags = {}
    
    # Environment tag - 70% have it
    if random.random() > 0.3:
        tags["Environment"] = env.capitalize()
    
    # Team tag - 60% have it
    if random.random() > 0.4:
        tags["Team"] = team
    
    # CreatedBy tag - 50% have it
    if random.random() > 0.5:
        tags["CreatedBy"] = random.choice(["terraform", "manual", "cloudformation", "ARM"])
    
    # CostCenter tag - 80% have it (REQUIRED TAG)
    if random.random() > 0.2:
        tags["CostCenter"] = random.choice(COST_CENTERS)
    
    # Owner tag - 40% have it
    if random.random() > 0.6:
        tags["Owner"] = random.choice(OWNERS)
    
    # Application tag - 30% have it
    if random.random() > 0.7:
        tags["Application"] = random.choice(APPLICATIONS)
    
    # Project tag - 20% have it
    if random.random() > 0.8:
        tags["Project"] = f"project-{random.choice(['alpha', 'beta', 'gamma', 'delta'])}"
    
    return tags


async def seed_resources(session, count: int = 1000):
    """Generate and insert mock resources"""
    print(f"🌱 Seeding {count} resources...")
    
    resources = []
    for i in range(1, count + 1):
        cloud = random.choice(CLOUDS)
        env = random.choice(ENVIRONMENTS)
        team = random.choice(TEAMS)
        service = random.choice(SERVICES)
        resource_type = random.choice(RESOURCE_TYPES[cloud])
        
        resource_id = generate_resource_id(cloud, resource_type, i)
        name = f"{env}-{team}-{service}-{str(i).zfill(3)}"
        account_id = generate_account_id(cloud)
        native_tags = generate_native_tags(env, team)
        
        # Random creation date within last 90 days
        days_ago = random.randint(0, 90)
        created_at = datetime.utcnow() - timedelta(days=days_ago)
        
        resource = Resource(
            resource_id=resource_id,
            name=name,
            cloud=cloud,
            account_id=account_id,
            resource_type=resource_type,
            native_tags=native_tags,
            created_at=created_at
        )
        resources.append(resource)
        
        if i % 100 == 0:
            print(f"  Generated {i}/{count} resources...")
    
    session.add_all(resources)
    await session.commit()
    print(f"✅ Successfully seeded {count} resources!")


async def seed_rules(session):
    """Create default tagging rules"""
    print("🌱 Seeding default rules...")
    
    rules = [
        Rule(
            rule_name="Production Environment Tagging",
            condition="name CONTAINS 'prod'",
            tag_key="CostCenter",
            tag_value="Production",
            scope="All",
            priority=1,
            created_by="system"
        ),
        Rule(
            rule_name="Development Environment Tagging",
            condition="name CONTAINS 'dev'",
            tag_key="CostCenter",
            tag_value="Development",
            scope="All",
            priority=1,
            created_by="system"
        ),
        Rule(
            rule_name="Data Team Resources",
            condition="name CONTAINS 'data'",
            tag_key="team",
            tag_value="data",
            scope="All",
            priority=2,
            created_by="system"
        ),
    ]
    
    session.add_all(rules)
    await session.commit()
    print(f"✅ Successfully seeded {len(rules)} rules!")


async def main():
    """Main seeding function"""
    print("\n" + "="*60)
    print("  🌱 DATABASE SEEDER - Virtual Tagging System")
    print("="*60 + "\n")
    
    # Initialize database
    print("📦 Initializing database...")
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Check if data already exists
        result = await session.execute(select(Resource).limit(1))
        existing = result.scalar_one_or_none()
        
        if existing:
            print("⚠️  Database already contains data!")
            response = input("Do you want to clear and reseed? (yes/no): ")
            if response.lower() != "yes":
                print("❌ Seeding cancelled")
                return
            
            # Clear existing data
            print("🗑️  Clearing existing data...")
            await session.execute("TRUNCATE TABLE resources, virtual_tags, rules, ml_inferences, tag_audit, scheduler_jobs CASCADE")
            await session.commit()
        
        # Seed data
        await seed_resources(session, count=1000)
        await seed_rules(session)
    
    print("\n" + "="*60)
    print("  ✅ SEEDING COMPLETED SUCCESSFULLY!")
    print("="*60 + "\n")
    print(f"📊 Summary:")
    print(f"  - Resources: 1000 (AWS, GCP, Azure)")
    print(f"  - Rules: 3 default rules")
    print(f"\n🚀 You can now start the API server!")


if __name__ == "__main__":
    asyncio.run(main())
