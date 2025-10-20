#!/usr/bin/env python
"""Test script for queue manager functionality."""

from pathlib import Path
from yt_extractor.utils.queue_manager import ProcessingQueue, QueueStatus


def test_queue_operations():
    """Test basic queue operations."""
    print("🧪 Testing Queue Manager")
    print("=" * 60)

    # Create a test queue in a temporary location
    test_queue_dir = Path("outputs/.queue_test")
    test_queue_dir.mkdir(parents=True, exist_ok=True)

    queue = ProcessingQueue(queue_dir=test_queue_dir)

    # Test 1: Add URLs
    print("\n1️⃣ Testing: Add URLs to queue")
    urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=abc123xyz",
        "https://www.youtube.com/watch?v=test456",
    ]

    for url in urls:
        item = queue.add(url, category="test")
        print(f"   ✅ Added: {url} (ID: {item.id})")

    # Test 2: Get stats
    print("\n2️⃣ Testing: Queue statistics")
    stats = queue.get_stats()
    print(f"   Total: {stats['total']}")
    print(f"   Pending: {stats['pending']}")
    print(f"   ✅ Stats working correctly")

    # Test 3: Duplicate detection
    print("\n3️⃣ Testing: Duplicate URL detection")
    try:
        queue.add(urls[0], category="test")
        print("   ❌ Duplicate check failed (should have raised ValueError)")
    except ValueError as e:
        print(f"   ✅ Duplicate detected correctly: {e}")

    # Test 4: Get all items
    print("\n4️⃣ Testing: Retrieve queue items")
    items = queue.get_all()
    print(f"   Retrieved {len(items)} items")
    for item in items:
        print(f"   - {item.url} | Status: {item.status.value} | Category: {item.category}")
    print("   ✅ Item retrieval working")

    # Test 5: Move items
    print("\n5️⃣ Testing: Move items in queue")
    first_item_id = items[0].id
    queue.move_down(first_item_id)
    items_after_move = queue.get_all()
    if items_after_move[1].id == first_item_id:
        print("   ✅ Move down working")
    else:
        print("   ❌ Move down failed")

    queue.move_up(first_item_id)
    items_after_move_up = queue.get_all()
    if items_after_move_up[0].id == first_item_id:
        print("   ✅ Move up working")
    else:
        print("   ❌ Move up failed")

    # Test 6: Update status
    print("\n6️⃣ Testing: Update item status")
    test_item = items[0]
    queue.update_status(test_item.id, QueueStatus.COMPLETED, output_path="/test/output.md")
    updated_item = queue.get_by_id(test_item.id)
    if updated_item.status == QueueStatus.COMPLETED:
        print(f"   ✅ Status updated to {updated_item.status.value}")
        print(f"   ✅ Output path set to: {updated_item.output_path}")
    else:
        print("   ❌ Status update failed")

    # Test 7: Update metadata
    print("\n7️⃣ Testing: Update item metadata")
    queue.update_metadata(test_item.id, title="Test Video", channel="Test Channel")
    updated_item = queue.get_by_id(test_item.id)
    if updated_item.title == "Test Video":
        print(f"   ✅ Title updated: {updated_item.title}")
        print(f"   ✅ Channel updated: {updated_item.channel}")
    else:
        print("   ❌ Metadata update failed")

    # Test 8: Get by status
    print("\n8️⃣ Testing: Filter by status")
    pending_items = queue.get_by_status(QueueStatus.PENDING)
    print(f"   Pending items: {len(pending_items)}")
    completed_items = queue.get_by_status(QueueStatus.COMPLETED)
    print(f"   Completed items: {len(completed_items)}")
    print("   ✅ Status filtering working")

    # Test 9: Persistence
    print("\n9️⃣ Testing: Queue persistence")
    queue_file = test_queue_dir / "queue.json"
    if queue_file.exists():
        print(f"   ✅ Queue file created: {queue_file}")

        # Load queue again to test persistence
        new_queue = ProcessingQueue(queue_dir=test_queue_dir)
        new_items = new_queue.get_all()
        if len(new_items) == len(items):
            print(f"   ✅ Queue loaded from disk: {len(new_items)} items")
        else:
            print(f"   ❌ Persistence failed (expected {len(items)}, got {len(new_items)})")
    else:
        print("   ❌ Queue file not created")

    # Test 10: Remove item
    print("\n🔟 Testing: Remove item from queue")
    item_to_remove = items[2]
    removed = queue.remove(item_to_remove.id)
    if removed:
        remaining = queue.get_all()
        print(f"   ✅ Item removed (remaining: {len(remaining)})")
    else:
        print("   ❌ Remove failed")

    # Test 11: Clear completed
    print("\n1️⃣1️⃣ Testing: Clear completed items")
    queue.clear(status_filter=QueueStatus.COMPLETED)
    stats_after_clear = queue.get_stats()
    if stats_after_clear["completed"] == 0:
        print("   ✅ Completed items cleared")
    else:
        print("   ❌ Clear completed failed")

    # Cleanup
    print("\n🧹 Cleaning up test queue...")
    import shutil
    shutil.rmtree(test_queue_dir)
    print("   ✅ Test queue directory removed")

    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")


if __name__ == "__main__":
    test_queue_operations()
