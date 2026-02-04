#!/usr/bin/env python3
"""Unit tests for checklist CLI commands (argument parsing)"""

import unittest
from todocli.cli import setup_parser


class TestChecklistCLIArgParsing(unittest.TestCase):
    """Test that CLI parsers correctly parse checklist command arguments"""

    def setUp(self):
        self.parser = setup_parser()

    # new-step

    def test_new_step_basic(self):
        """Test new-step command with list/task format"""
        args = self.parser.parse_args(
            ["new-step", "Shopping/Buy groceries", "Buy eggs"]
        )
        self.assertEqual(args.task_name, "Shopping/Buy groceries")
        self.assertEqual(args.step_name, "Buy eggs")

    def test_new_step_default_list(self):
        """Test new-step command without list prefix"""
        args = self.parser.parse_args(["new-step", "Buy groceries", "Buy eggs"])
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.step_name, "Buy eggs")

    def test_new_step_with_list_flag(self):
        """Test new-step with --list flag"""
        args = self.parser.parse_args(
            ["new-step", "Buy groceries", "Buy eggs", "-l", "Shopping"]
        )
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.step_name, "Buy eggs")
        self.assertEqual(args.list, "Shopping")

    # list-steps

    def test_list_steps_basic(self):
        """Test list-steps command with list/task format"""
        args = self.parser.parse_args(["list-steps", "Shopping/Buy groceries"])
        self.assertEqual(args.task_name, "Shopping/Buy groceries")

    def test_list_steps_default_list(self):
        """Test list-steps without list prefix"""
        args = self.parser.parse_args(["list-steps", "Buy groceries"])
        self.assertEqual(args.task_name, "Buy groceries")

    def test_list_steps_with_list_flag(self):
        """Test list-steps with --list flag"""
        args = self.parser.parse_args(["list-steps", "Buy groceries", "-l", "Shopping"])
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.list, "Shopping")

    # complete-step

    def test_complete_step_basic(self):
        """Test complete-step command"""
        args = self.parser.parse_args(
            ["complete-step", "Shopping/Buy groceries", "Buy eggs"]
        )
        self.assertEqual(args.task_name, "Shopping/Buy groceries")
        self.assertEqual(args.step_name, "Buy eggs")

    def test_complete_step_by_index(self):
        """Test complete-step with numeric step index"""
        args = self.parser.parse_args(["complete-step", "Shopping/Buy groceries", "0"])
        self.assertEqual(args.step_name, "0")

    def test_complete_step_with_list_flag(self):
        """Test complete-step with --list flag"""
        args = self.parser.parse_args(
            ["complete-step", "Buy groceries", "Buy eggs", "-l", "Shopping"]
        )
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.step_name, "Buy eggs")
        self.assertEqual(args.list, "Shopping")

    # rm-step

    def test_rm_step_basic(self):
        """Test rm-step command"""
        args = self.parser.parse_args(["rm-step", "Shopping/Buy groceries", "Buy eggs"])
        self.assertEqual(args.task_name, "Shopping/Buy groceries")
        self.assertEqual(args.step_name, "Buy eggs")

    def test_rm_step_by_index(self):
        """Test rm-step with numeric step index"""
        args = self.parser.parse_args(["rm-step", "Shopping/Buy groceries", "2"])
        self.assertEqual(args.step_name, "2")

    def test_rm_step_with_list_flag(self):
        """Test rm-step with --list flag"""
        args = self.parser.parse_args(
            ["rm-step", "Buy groceries", "Buy eggs", "-l", "Shopping"]
        )
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.step_name, "Buy eggs")
        self.assertEqual(args.list, "Shopping")

    # lst --steps flag

    def test_lst_steps_flag(self):
        """Test lst command with --steps flag"""
        args = self.parser.parse_args(["lst", "Shopping", "-s"])
        self.assertEqual(args.list_name, "Shopping")
        self.assertTrue(args.steps)

    def test_lst_steps_flag_long(self):
        """Test lst command with --steps long flag"""
        args = self.parser.parse_args(["lst", "Shopping", "--steps"])
        self.assertTrue(args.steps)

    def test_lst_no_steps_flag(self):
        """Test lst command without --steps defaults to False"""
        args = self.parser.parse_args(["lst", "Shopping"])
        self.assertFalse(args.steps)


if __name__ == "__main__":
    unittest.main()
