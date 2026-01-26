#!/usr/bin/env python3
"""Test script for task names containing slashes (URLs, paths, etc.)"""

from todocli.cli import parse_task_path


def test_parse_task_path():
    """Test various scenarios for parse_task_path"""

    # Test 1: Traditional syntax without list flag
    print("Test 1: Traditional syntax 'buy milk'")
    list_name, task_name = parse_task_path("buy milk")
    assert list_name == "Tasks"
    assert task_name == "buy milk"
    print(f"  ✓ list: '{list_name}', task: '{task_name}'")

    # Test 2: Traditional syntax with list specified
    print("\nTest 2: Traditional syntax 'personal/buy milk'")
    list_name, task_name = parse_task_path("personal/buy milk")
    assert list_name == "personal"
    assert task_name == "buy milk"
    print(f"  ✓ list: '{list_name}', task: '{task_name}'")

    # Test 3: URL without list flag (should fail)
    print("\nTest 3: URL without list flag 'https://www.google.com/' (should fail)")
    try:
        list_name, task_name = parse_task_path("https://www.google.com/")
        print(
            f"  ✗ Should have failed but got: list: '{list_name}', task: '{task_name}'"
        )
    except Exception as e:
        print(f"  ✓ Expected failure: {e.message}")

    # Test 4: URL with list flag (should work!)
    print("\nTest 4: URL with --list flag")
    list_name, task_name = parse_task_path(
        "https://www.google.com/", list_name="personal"
    )
    assert list_name == "personal"
    assert task_name == "https://www.google.com/"
    print(f"  ✓ list: '{list_name}', task: '{task_name}'")

    # Test 5: URL with multiple slashes and list flag
    print("\nTest 5: Complex URL with --list flag")
    list_name, task_name = parse_task_path(
        "https://example.com/path/to/page", list_name="work"
    )
    assert list_name == "work"
    assert task_name == "https://example.com/path/to/page"
    print(f"  ✓ list: '{list_name}', task: '{task_name}'")

    # Test 6: Task with slash in name using list flag
    print("\nTest 6: Task 'check A/B testing' with --list flag")
    list_name, task_name = parse_task_path("check A/B testing", list_name="work")
    assert list_name == "work"
    assert task_name == "check A/B testing"
    print(f"  ✓ list: '{list_name}', task: '{task_name}'")

    # Test 7: List flag overrides slash parsing
    print("\nTest 7: 'foo/bar' with --list 'work' (list flag takes precedence)")
    list_name, task_name = parse_task_path("foo/bar", list_name="work")
    assert list_name == "work"
    assert task_name == "foo/bar"
    print(f"  ✓ list: '{list_name}', task: '{task_name}'")

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    test_parse_task_path()
