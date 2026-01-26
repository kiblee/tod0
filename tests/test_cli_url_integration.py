#!/usr/bin/env python3
"""
Real integration test for URL support in task names.
This test actually creates tasks in Microsoft To-Do and verifies they exist.

Prerequisites:
- Valid API credentials configured in ~/.config/tod0/keys.yml
- Network connection

Note: This test creates a 'test-list' and adds tasks to it.
      Run 'tod0' after the test to manually verify the changes.
"""

import sys
import todocli.graphapi.wrapper as wrapper
from todocli.cli import parse_task_path


def test_url_in_task_name():
    """Integration test: Create task with URL using --list flag"""

    print("=" * 70)
    print("INTEGRATION TEST: Task names with URLs")
    print("=" * 70)

    # Setup: Create test list
    print("\n1. Setting up test list...")
    try:
        wrapper.create_list("test-list")
        print("   ✓ Created 'test-list'")
    except Exception as e:
        print(f"   → List may already exist: {e}")

    # Test 1: Create task with URL using new --list flag
    print("\n2. Creating task with URL using --list flag...")
    task_url = "https://github.com/kiblee/tod0/issues/70"
    list_name, task_name = parse_task_path(task_url, list_name="test-list")

    print(f"   Parsed as: list='{list_name}', task='{task_name}'")

    try:
        wrapper.create_task(task_name=task_name, list_name=list_name)
        print(f"   ✓ Created task: '{task_name}'")
    except Exception as e:
        print(f"   ✗ Failed to create task: {e}")
        sys.exit(1)

    # Test 2: Verify the task exists
    print("\n3. Verifying task was created...")
    try:
        tasks = wrapper.get_tasks(list_name="test-list")
        task_titles = [t.title for t in tasks]

        if task_url in task_titles:
            print(f"   ✓ Task found in list! Title: '{task_url}'")
        else:
            print(f"   ✗ Task not found in list")
            print(f"   Found tasks: {task_titles}")
            sys.exit(1)
    except Exception as e:
        print(f"   ✗ Failed to retrieve tasks: {e}")
        sys.exit(1)

    # Test 3: Create another task with multiple slashes
    print("\n4. Creating task with complex URL...")
    complex_url = "https://docs.microsoft.com/en-us/graph/api/overview"
    list_name, task_name = parse_task_path(complex_url, list_name="test-list")

    try:
        wrapper.create_task(task_name=task_name, list_name=list_name)
        print(f"   ✓ Created task: '{task_name}'")
    except Exception as e:
        print(f"   ✗ Failed to create task: {e}")
        sys.exit(1)

    # Test 4: Verify both tasks exist
    print("\n5. Verifying both tasks exist...")
    try:
        tasks = wrapper.get_tasks(list_name="test-list")
        task_titles = [t.title for t in tasks]

        if task_url in task_titles and complex_url in task_titles:
            print(f"   ✓ Both URL tasks found!")
            print(f"   Tasks in list: {len(task_titles)}")
            for title in task_titles:
                print(f"     - {title}")
        else:
            print(f"   ✗ Not all tasks found")
            print(f"   Found tasks: {task_titles}")
            sys.exit(1)
    except Exception as e:
        print(f"   ✗ Failed to retrieve tasks: {e}")
        sys.exit(1)

    # Test 5: Complete a URL task
    print("\n6. Completing URL task...")
    try:
        wrapper.complete_task(list_name="test-list", task_name=task_url)
        print(f"   ✓ Completed task: '{task_url}'")
    except Exception as e:
        print(f"   ✗ Failed to complete task: {e}")
        sys.exit(1)

    # Test 6: Remove the other URL task
    print("\n7. Removing URL task...")
    try:
        wrapper.remove_task("test-list", complex_url)
        print(f"   ✓ Removed task: '{complex_url}'")
    except Exception as e:
        print(f"   ✗ Failed to remove task: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("=" * 70)
    print("\nWhat was tested:")
    print("  ✓ Creating tasks with URLs containing slashes")
    print("  ✓ Verifying tasks exist in Microsoft To-Do")
    print("  ✓ Completing URL tasks")
    print("  ✓ Removing URL tasks")
    print("\nTo verify manually:")
    print("  1. Run 'tod0' to see the 'test-list' in the TUI")
    print("  2. Check Microsoft To-Do web/app")
    print("  3. Note: One task was completed (filtered from active view)")
    print("  4. One task was deleted")


if __name__ == "__main__":
    try:
        test_url_in_task_name()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
