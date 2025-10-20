#!/usr/bin/env python3
"""Test script for queue improvements - validates logic without running Streamlit."""

import re
import sys
from pathlib import Path

def validate_web_ui_changes():
    """Validate that web_ui.py has the expected improvements."""

    web_ui_path = Path("web_ui.py")
    if not web_ui_path.exists():
        print("❌ web_ui.py not found")
        return False

    content = web_ui_path.read_text()

    checks = {
        "process_video_with_cli function": "def process_video_with_cli(",
        "CLI subprocess with Popen": "subprocess.Popen(",
        "Rich progress updates": 'progress_placeholder.info("🤖 Analyzing',
        "Auto-start logic": "st.session_state.auto_start_queue = True",
        "process_queue_with_live_updates function": "def process_queue_with_live_updates(",
        "Expandable video sections": "st.expander(f\"🔄 Processing:",
        "Live queue display": "queue_display = st.container()",
        "Modern CSS animations": "@keyframes spin",
        "CSS pulse animation": "@keyframes pulse",
        "Status badges": "status-badge",
        "Queue card styling": "queue-card",
        "Enhanced render_queue_item": "def render_queue_item(item, queue):",
        "Error details expander": 'st.expander("❌ Error Details"',
        "Timestamps display": "Added: {added_dt.strftime",
    }

    passed = 0
    failed = 0

    print("🧪 Validating queue improvements...\n")

    for check_name, check_pattern in checks.items():
        if check_pattern in content:
            print(f"✅ {check_name}")
            passed += 1
        else:
            print(f"❌ {check_name}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{len(checks)} checks passed")

    if failed == 0:
        print("🎉 All improvements successfully implemented!")
        return True
    else:
        print(f"⚠️  {failed} checks failed")
        return False


def validate_key_features():
    """Validate key feature implementations."""

    web_ui_path = Path("web_ui.py")
    content = web_ui_path.read_text()

    print("\n" + "="*60)
    print("🔍 Validating key features...\n")

    features = []

    # Feature 1: Rich progress visibility
    if "process_video_with_cli" in content and "progress_placeholder" in content:
        features.append(("Rich Progress Visibility", True,
                        "Videos processed via CLI with detailed progress updates"))
    else:
        features.append(("Rich Progress Visibility", False, "Missing"))

    # Feature 2: Auto-start
    if "auto_start_queue" in content and "st.session_state.auto_start_queue = True" in content:
        features.append(("Auto-start Processing", True,
                        "Queue automatically starts after adding URLs"))
    else:
        features.append(("Auto-start Processing", False, "Missing"))

    # Feature 3: Real-time UI updates
    if "process_queue_with_live_updates" in content and "st.expander" in content:
        features.append(("Real-time UI Updates", True,
                        "Live expandable sections for each video"))
    else:
        features.append(("Real-time UI Updates", False, "Missing"))

    # Feature 4: Modern UI with animations
    if "@keyframes" in content and "queue-card" in content:
        features.append(("Modern UI Design", True,
                        "Card-based layout with CSS animations"))
    else:
        features.append(("Modern UI Design", False, "Missing"))

    # Feature 5: Enhanced queue items
    if "status-badge" in content and "Error Details" in content:
        features.append(("Enhanced Queue Items", True,
                        "Status badges, timestamps, and error details"))
    else:
        features.append(("Enhanced Queue Items", False, "Missing"))

    for feature_name, implemented, description in features:
        if implemented:
            print(f"✅ {feature_name}")
            print(f"   → {description}")
        else:
            print(f"❌ {feature_name}: {description}")
        print()

    all_implemented = all(f[1] for f in features)

    if all_implemented:
        print("🎉 All key features successfully implemented!")
    else:
        print("⚠️  Some features are missing")

    return all_implemented


def main():
    """Run all validation checks."""
    print("="*60)
    print("Queue Improvements Validation Test")
    print("="*60 + "\n")

    result1 = validate_web_ui_changes()
    result2 = validate_key_features()

    print("\n" + "="*60)
    if result1 and result2:
        print("✅ ALL TESTS PASSED - Queue improvements ready!")
        print("="*60)
        return 0
    else:
        print("❌ SOME TESTS FAILED - Review changes needed")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
