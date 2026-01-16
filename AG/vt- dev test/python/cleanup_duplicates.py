"""
Clean up duplicate tags - keep only highest confidence/priority tag per resource+key
"""
import asyncio
from sqlalchemy import select, delete
from app.database import init_db, AsyncSessionLocal
from app.database.models import VirtualTag


async def cleanup_duplicate_tags():
    """Remove duplicate tags, keeping only the highest priority one"""
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Get all tags
        result = await session.execute(select(VirtualTag))
        all_tags = result.scalars().all()
        
        # Group by resource_id + tag_key
        tag_groups = {}
        for tag in all_tags:
            key = (tag.resource_id, tag.tag_key)
            if key not in tag_groups:
                tag_groups[key] = []
            tag_groups[key].append(tag)
        
        # Find duplicates
        duplicates_to_delete = []
        stats = {
            "total_tags": len(all_tags),
            "duplicate_groups": 0,
            "tags_to_delete": 0
        }
        
        source_priority = {
            "RULE_BASED": 1,
            "NATIVE_NORMALIZATION": 2,
            "ML_PATTERN": 3,
            "ML_DERIVED": 4,
            "ML_DEFAULT": 5,
            "CSV_IMPORT": 2,
            "INFERRED": 6,
            "MANUAL": 1
        }
        
        for (resource_id, tag_key), tags in tag_groups.items():
            if len(tags) > 1:
                stats["duplicate_groups"] += 1
                print(f"\nDuplicate found: {resource_id} - {tag_key}")
                print(f"  {len(tags)} tags with this key")
                
                # Sort by priority (source priority, then confidence)
                sorted_tags = sorted(
                    tags,
                    key=lambda t: (
                        source_priority.get(t.source, 99),
                        -t.confidence  # Higher confidence first
                    )
                )
                
                # Keep the first (highest priority), delete the rest
                keep_tag = sorted_tags[0]
                delete_tags = sorted_tags[1:]
                
                print(f"  KEEPING: {keep_tag.tag_value} (source: {keep_tag.source}, confidence: {keep_tag.confidence})")
                
                for tag in delete_tags:
                    print(f"  DELETING: {tag.tag_value} (source: {tag.source}, confidence: {tag.confidence})")
                    duplicates_to_delete.append(tag.id)
                    stats["tags_to_delete"] += 1
        
        # Delete duplicates
        if duplicates_to_delete:
            print(f"\n🗑️  Deleting {len(duplicates_to_delete)} duplicate tags...")
            await session.execute(
                delete(VirtualTag).where(VirtualTag.id.in_(duplicates_to_delete))
            )
            await session.commit()
        
        # Final stats
        result = await session.execute(select(VirtualTag))
        final_count = len(result.scalars().all())
        
        print(f"\n✅ Cleanup Complete!")
        print(f"   Total tags before: {stats['total_tags']}")
        print(f"   Duplicate groups found: {stats['duplicate_groups']}")
        print(f"   Tags deleted: {stats['tags_to_delete']}")
        print(f"   Total tags after: {final_count}")


if __name__ == "__main__":
    asyncio.run(cleanup_duplicate_tags())
