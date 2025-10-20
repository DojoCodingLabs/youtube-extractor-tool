#!/usr/bin/env python
"""Test script for code review fixes."""

from pathlib import Path
from yt_extractor.utils.queue_manager import ProcessingQueue, QueueStatus, _validate_youtube_url, _sanitize_category


def test_url_validation():
    """Test URL validation."""
    print("\n🧪 Testing URL Validation")
    print("=" * 60)

    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtube.com/watch?v=abc123",
        "https://youtu.be/xyz789",
        "http://www.youtube.com/watch?v=test123",
    ]

    invalid_urls = [
        "not a url",
        "https://vimeo.com/123456",
        "https://google.com",
        "",
        None,
        123,
        "youtube.com/watch",  # Missing protocol
    ]

    print("\n✅ Valid URLs:")
    for url in valid_urls:
        result = _validate_youtube_url(url)
        status = "✅" if result else "❌"
        print(f"   {status} {url}: {result}")

    print("\n❌ Invalid URLs:")
    for url in invalid_urls:
        try:
            result = _validate_youtube_url(url)
            status = "❌" if result else "✅"
            print(f"   {status} {url}: {result}")
        except Exception as e:
            print(f"   ✅ {url}: Raised {type(e).__name__}")


def test_category_sanitization():
    """Test category sanitization."""
    print("\n🧪 Testing Category Sanitization")
    print("=" * 60)

    valid_categories = [
        ("AI/Agents", "AI/Agents"),
        ("  Business  ", "Business"),
        ("Crypto/DeFi/Trading", "Crypto/DeFi/Trading"),
        ("", None),
        ("   ", None),
        (None, None),
    ]

    dangerous_categories = [
        "../etc/passwd",
        "AI\\Agents",
        "test\0null",
        "../../home",
    ]

    print("\n✅ Valid Categories:")
    for input_cat, expected in valid_categories:
        try:
            result = _sanitize_category(input_cat)
            status = "✅" if result == expected else "❌"
            print(f"   {status} '{input_cat}' → '{result}' (expected: '{expected}')")
        except Exception as e:
            print(f"   ❌ '{input_cat}': Unexpected error: {e}")

    print("\n❌ Dangerous Categories (should raise ValueError):")
    for cat in dangerous_categories:
        try:
            result = _sanitize_category(cat)
            print(f"   ❌ '{cat}': Should have raised ValueError, got '{result}'")
        except ValueError as e:
            print(f"   ✅ '{cat}': Correctly raised ValueError")
        except Exception as e:
            print(f"   ⚠️ '{cat}': Raised {type(e).__name__}: {e}")


def test_queue_size_limit():
    """Test queue size limit."""
    print("\n🧪 Testing Queue Size Limit")
    print("=" * 60)

    test_queue_dir = Path("outputs/.queue_test_limit")
    test_queue_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Create queue with max_size=5
        queue = ProcessingQueue(queue_dir=test_queue_dir, max_size=5)

        print("\n   Adding items up to limit...")
        for i in range(5):
            url = f"https://www.youtube.com/watch?v=test{i:03d}"
            queue.add(url, category="test")
            print(f"   ✅ Added item {i+1}/5")

        # Try to add one more (should fail)
        print("\n   Attempting to add beyond limit...")
        try:
            queue.add("https://www.youtube.com/watch?v=overflow", category="test")
            print("   ❌ Should have raised ValueError for queue full")
        except ValueError as e:
            if "full" in str(e):
                print(f"   ✅ Correctly raised ValueError: {e}")
            else:
                print(f"   ⚠️ Raised ValueError but wrong message: {e}")

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_queue_dir)
        print("\n   🧹 Cleaned up test queue")


def test_invalid_url_rejection():
    """Test that invalid URLs are rejected."""
    print("\n🧪 Testing Invalid URL Rejection")
    print("=" * 60)

    test_queue_dir = Path("outputs/.queue_test_invalid")
    test_queue_dir.mkdir(parents=True, exist_ok=True)

    try:
        queue = ProcessingQueue(queue_dir=test_queue_dir)

        invalid_urls = [
            "not a url",
            "https://vimeo.com/123",
            "",
            "http://google.com/watch?v=fake",
        ]

        for url in invalid_urls:
            try:
                queue.add(url)
                print(f"   ❌ '{url}': Should have been rejected")
            except ValueError as e:
                print(f"   ✅ '{url}': Correctly rejected - {e}")

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_queue_dir)
        print("\n   🧹 Cleaned up test queue")


def test_atomic_save():
    """Test atomic file save."""
    print("\n🧪 Testing Atomic File Save")
    print("=" * 60)

    test_queue_dir = Path("outputs/.queue_test_atomic")
    test_queue_dir.mkdir(parents=True, exist_ok=True)

    try:
        queue = ProcessingQueue(queue_dir=test_queue_dir)

        # Add an item
        queue.add("https://www.youtube.com/watch?v=test123")

        # Check that temp file doesn't exist after save
        temp_file = queue.queue_file.with_suffix('.tmp')
        if temp_file.exists():
            print("   ❌ Temp file still exists after save")
        else:
            print("   ✅ Temp file cleaned up (atomic rename successful)")

        # Check that queue file exists
        if queue.queue_file.exists():
            print("   ✅ Queue file exists")
        else:
            print("   ❌ Queue file missing")

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_queue_dir)
        print("\n   🧹 Cleaned up test queue")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING CODE REVIEW FIXES")
    print("="*60)

    test_url_validation()
    test_category_sanitization()
    test_queue_size_limit()
    test_invalid_url_rejection()
    test_atomic_save()

    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60 + "\n")
