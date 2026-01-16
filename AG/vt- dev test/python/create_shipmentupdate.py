"""
Create a new resource and auto-tag it
"""
import asyncio
from sqlalchemy import select
from app.database import init_db, AsyncSessionLocal
from app.database.models import Resource, VirtualTag
from app.services.auto_tagger import AutoTaggerService


async def create_and_tag_resource():
    """Create new resource and auto-tag it"""
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Create new resource
        new_resource = Resource(
            resource_id="aws-ec2-shipmentupdate-001",
            name="shipmentupdate",
            cloud="AWS",
            account_id="aws-account-123456789",
            resource_type="EC2 Instance",
            native_tags={}  # No native tags
        )
        
        session.add(new_resource)
        await session.commit()
        await session.refresh(new_resource)
        
        print(f"✅ Created resource: {new_resource.name}")
        print(f"   ID: {new_resource.resource_id}")
        print(f"   Cloud: {new_resource.cloud}")
        print(f"   Type: {new_resource.resource_type}")
        
        # Run auto-tagger
        print(f"\n🤖 Running auto-tagger...")
        auto_tagger = AutoTaggerService()
        result = await auto_tagger.process_resource(new_resource, session)
        
        await session.commit()
        
        print(f"   Tags applied: {result['tags_applied']}")
        print(f"   Suggestions stored: {result['suggestions_stored']}")
        
        # Fetch and display all tags
        tags_result = await session.execute(
            select(VirtualTag).where(VirtualTag.resource_id == new_resource.resource_id)
        )
        tags = tags_result.scalars().all()
        
        print(f"\n📋 Virtual Tags Generated:")
        print(f"{'='*80}")
        for tag in tags:
            print(f"   {tag.tag_key:15} = {tag.tag_value:20} (source: {tag.source:20}, confidence: {tag.confidence:.0%})")
        
        print(f"\n{'='*80}")
        print(f"Total tags: {len(tags)}")


if __name__ == "__main__":
    asyncio.run(create_and_tag_resource())
