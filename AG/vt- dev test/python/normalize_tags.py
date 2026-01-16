"""
Normalize all existing tag keys to lowercase and remove duplicates
"""
import asyncio
from sqlalchemy import select, update, delete
from app.database import init_db, AsyncSessionLocal
from app.database.models import VirtualTag


async def normalize_tag_keys():
    """Normalize all tag keys to lowercase and remove duplicates"""
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Get all tags
        result = await session.execute(select(VirtualTag))
        all_tags = result.scalars().all()
        
        print(f"Total tags: {len(all_tags)}")
        
        # Update all tag keys to lowercase
        for tag in all_tags:
            if tag.tag_key != tag.tag_key.lower():
                tag.tag_key = tag.tag_key.lower()
        
        await session.commit()
        print("✅ Normalized all tag keys to lowercase")
        
        # Now find and remove duplicates
        result = await session.execute(select(VirtualTag))
        all_tags = result.scalars().all()
        
        # Group by (resource_id, tag_key)
        tag_groups = {}
        for tag in all_tags:
            key = (tag.resource_id, tag.tag_key.lower())
            if key not in tag_groups:
                tag_groups[key] = []
            tag_groups[key].append(tag)
        
        # Find and remove duplicates  
        source_priority = {
            "RULE_BASED": 1,
            "CSV_IMPORT": 2,
            "NATIVE_NORMALIZATION": 3,
            "ML_PATTERN": 4,
            "ML_DERIVED": 5,
            "ML_DEFAULT": 6,
            "INFERRED": 7,
            "MANUAL": 1
        }
        
        duplicates_to_delete = []
        for (resource_id, tag_key), tags in tag_groups.items():
            if len(tags) > 1:
                # Sort by priority
                sorted_tags = sorted(
                    tags,
                    key=lambda t: (
                        source_priority.get(t.source, 99),
                        -t.confidence
                    )
                )
                
                # Keep first, delete rest
                keep = sorted_tags[0]
                delete = sorted_tags[1:]
                
                print(f"\nDuplicate: {tag_key}")
                print(f"  KEEP: {keep.tag_value} ({keep.source}, conf={keep.confidence})")
                for tag in delete:
                    print(f"  DELETE: {tag.tag_value} ({tag.source}, conf={tag.confidence})")
                    duplicates_to_delete.append(tag.id)
        
        if duplicates_to_delete:
            print(f"\n🗑️  Deleting {len(duplicates_to_delete)} duplicate tags...")
            await session.execute(
                delete(VirtualTag).where(VirtualTag.id.in_(duplicates_to_delete))
            )
            await session.commit()
        
        # Final count
        result = await session.execute(select(VirtualTag))
        final_count = len(result.scalars().all())
        
        print(f"\n✅ Done!")
        print(f"   Final tag count: {final_count}")
        print(f"   Duplicates removed: {len(duplicates_to_delete)}")


if __name__ == "__main__":
    asyncio.run(normalize_tag_keys())
