#!/usr/bin/env python3
"""Unit tests for CLI command parsing and argument handling"""

import unittest
from todocli.cli import (
    setup_parser,
    parse_task_path,
    try_parse_as_int,
    InvalidTaskPath,
)


class TestCLIArgumentParsing(unittest.TestCase):
    """Test argparse setup for all commands"""

    def setUp(self):
        self.parser = setup_parser()

    def test_ls_command(self):
        """Test 'ls' command parsing"""
        args = self.parser.parse_args(["ls"])
        self.assertTrue(hasattr(args, "func"))
        self.assertIsNotNone(args.func)

    def test_lst_command_with_list(self):
        """Test 'lst' command with list name"""
        args = self.parser.parse_args(["lst", "personal"])
        self.assertEqual(args.list_name, "personal")

    def test_lst_command_default_list(self):
        """Test 'lst' command defaults to 'Tasks'"""
        args = self.parser.parse_args(["lst"])
        self.assertEqual(args.list_name, "Tasks")

    def test_new_command_basic(self):
        """Test 'new' command with task name"""
        args = self.parser.parse_args(["new", "buy milk"])
        self.assertEqual(args.task_name, "buy milk")
        self.assertIsNone(args.reminder)
        self.assertIsNone(getattr(args, "list", None))

    def test_new_command_with_reminder(self):
        """Test 'new' command with -r flag"""
        args = self.parser.parse_args(["new", "-r", "9:00", "buy milk"])
        self.assertEqual(args.task_name, "buy milk")
        self.assertEqual(args.reminder, "9:00")

    def test_new_command_with_list_flag(self):
        """Test 'new' command with --list flag"""
        args = self.parser.parse_args(["new", "--list", "personal", "buy milk"])
        self.assertEqual(args.task_name, "buy milk")
        self.assertEqual(args.list, "personal")

    def test_new_command_with_short_list_flag(self):
        """Test 'new' command with -l flag"""
        args = self.parser.parse_args(["new", "-l", "work", "task"])
        self.assertEqual(args.task_name, "task")
        self.assertEqual(args.list, "work")

    def test_new_command_with_all_flags(self):
        """Test 'new' command with both -l and -r flags"""
        args = self.parser.parse_args(
            ["new", "-l", "personal", "-r", "9:00", "buy milk"]
        )
        self.assertEqual(args.task_name, "buy milk")
        self.assertEqual(args.list, "personal")
        self.assertEqual(args.reminder, "9:00")

    def test_new_command_with_important(self):
        """Test 'new' command with -I flag"""
        args = self.parser.parse_args(["new", "-I", "buy milk"])
        self.assertEqual(args.task_name, "buy milk")
        self.assertTrue(args.important)

    def test_new_command_with_important_long(self):
        """Test 'new' command with --important flag"""
        args = self.parser.parse_args(["new", "--important", "buy milk"])
        self.assertEqual(args.task_name, "buy milk")
        self.assertTrue(args.important)

    def test_new_command_without_important(self):
        """Test 'new' command defaults important to False"""
        args = self.parser.parse_args(["new", "buy milk"])
        self.assertFalse(args.important)

    def test_new_command_with_all_flags_including_important(self):
        """Test 'new' command with -l, -r, and -I flags"""
        args = self.parser.parse_args(
            ["new", "-l", "personal", "-r", "9:00", "-I", "buy milk"]
        )
        self.assertEqual(args.task_name, "buy milk")
        self.assertEqual(args.list, "personal")
        self.assertEqual(args.reminder, "9:00")
        self.assertTrue(args.important)

    def test_newl_command(self):
        """Test 'newl' command for creating lists"""
        args = self.parser.parse_args(["newl", "shopping"])
        self.assertEqual(args.list_name, "shopping")

    def test_complete_command_basic(self):
        """Test 'complete' command"""
        args = self.parser.parse_args(["complete", "task"])
        self.assertEqual(args.task_name, "task")
        self.assertIsNone(getattr(args, "list", None))

    def test_complete_command_with_list(self):
        """Test 'complete' command with --list flag"""
        args = self.parser.parse_args(["complete", "--list", "personal", "task"])
        self.assertEqual(args.task_name, "task")
        self.assertEqual(args.list, "personal")

    def test_rm_command_basic(self):
        """Test 'rm' command"""
        args = self.parser.parse_args(["rm", "task"])
        self.assertEqual(args.task_name, "task")

    def test_rm_command_with_list(self):
        """Test 'rm' command with -l flag"""
        args = self.parser.parse_args(["rm", "-l", "work", "task"])
        self.assertEqual(args.task_name, "task")
        self.assertEqual(args.list, "work")

    def test_interactive_flag(self):
        """Test -i/--interactive flag"""
        args = self.parser.parse_args(["-i", "ls"])
        self.assertTrue(args.interactive)

        args = self.parser.parse_args(["--interactive", "ls"])
        self.assertTrue(args.interactive)


class TestParseTaskPath(unittest.TestCase):
    """Test parse_task_path function"""

    def test_simple_task_name(self):
        """Test task name without list defaults to 'Tasks'"""
        list_name, task_name = parse_task_path("buy milk")
        self.assertEqual(list_name, "Tasks")
        self.assertEqual(task_name, "buy milk")

    def test_task_with_list_name(self):
        """Test task name with list specified"""
        list_name, task_name = parse_task_path("personal/buy milk")
        self.assertEqual(list_name, "personal")
        self.assertEqual(task_name, "buy milk")

    def test_task_with_explicit_list(self):
        """Test task with explicit list_name parameter"""
        list_name, task_name = parse_task_path("buy milk", list_name="work")
        self.assertEqual(list_name, "work")
        self.assertEqual(task_name, "buy milk")

    def test_url_with_explicit_list(self):
        """Test URL task name with explicit list (issue #70)"""
        list_name, task_name = parse_task_path(
            "https://www.google.com/", list_name="personal"
        )
        self.assertEqual(list_name, "personal")
        self.assertEqual(task_name, "https://www.google.com/")

    def test_complex_url_with_explicit_list(self):
        """Test complex URL with multiple slashes"""
        list_name, task_name = parse_task_path(
            "https://example.com/path/to/page", list_name="work"
        )
        self.assertEqual(list_name, "work")
        self.assertEqual(task_name, "https://example.com/path/to/page")

    def test_explicit_list_overrides_slash_parsing(self):
        """Test that explicit list takes precedence over slash parsing"""
        list_name, task_name = parse_task_path("foo/bar", list_name="work")
        self.assertEqual(list_name, "work")
        self.assertEqual(task_name, "foo/bar")

    def test_multiple_slashes_without_list_raises_error(self):
        """Test that multiple slashes without explicit list raises error"""
        with self.assertRaises(InvalidTaskPath) as context:
            parse_task_path("https://www.google.com/")
        self.assertIn("path can only contain one '/'", str(context.exception.message))

    def test_task_number_format(self):
        """Test task specified by number"""
        list_name, task_name = parse_task_path("personal/0")
        self.assertEqual(list_name, "personal")
        self.assertEqual(task_name, "0")

    def test_empty_task_name(self):
        """Test empty task name"""
        list_name, task_name = parse_task_path("")
        self.assertEqual(list_name, "Tasks")
        self.assertEqual(task_name, "")

    def test_special_characters_in_task_name(self):
        """Test task names with special characters"""
        list_name, task_name = parse_task_path("check A/B testing", list_name="work")
        self.assertEqual(list_name, "work")
        self.assertEqual(task_name, "check A/B testing")


class TestTryParseAsInt(unittest.TestCase):
    """Test try_parse_as_int helper function"""

    def test_valid_integer_string(self):
        """Test parsing valid integer string"""
        result = try_parse_as_int("42")
        self.assertEqual(result, 42)
        self.assertIsInstance(result, int)

    def test_zero(self):
        """Test parsing zero"""
        result = try_parse_as_int("0")
        self.assertEqual(result, 0)

    def test_negative_integer(self):
        """Test parsing negative integer"""
        result = try_parse_as_int("-5")
        self.assertEqual(result, -5)

    def test_non_integer_string(self):
        """Test that non-integer strings are returned as-is"""
        result = try_parse_as_int("buy milk")
        self.assertEqual(result, "buy milk")
        self.assertIsInstance(result, str)

    def test_float_string(self):
        """Test that float strings are returned as-is"""
        result = try_parse_as_int("3.14")
        self.assertEqual(result, "3.14")
        self.assertIsInstance(result, str)

    def test_empty_string(self):
        """Test empty string"""
        result = try_parse_as_int("")
        self.assertEqual(result, "")

    def test_mixed_alphanumeric(self):
        """Test mixed alphanumeric string"""
        result = try_parse_as_int("task123")
        self.assertEqual(result, "task123")


if __name__ == "__main__":
    unittest.main()
