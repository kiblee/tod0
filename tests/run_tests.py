#!/usr/bin/env python3
"""
Test runner for tod0 project.
Runs all unit tests that don't require API credentials.
"""

import sys
import unittest

# Discover and run all test files matching pattern
if __name__ == "__main__":
    loader = unittest.TestLoader()
    start_dir = "tests"
    pattern = "test_*.py"

    # Exclude integration tests that require API credentials
    suite = unittest.TestSuite()

    # Add each unit test explicitly (excludes test_cli_url_integration.py)
    suite.addTests(loader.loadTestsFromName("tests.test_datetime_parser"))
    suite.addTests(loader.loadTestsFromName("tests.test_task_names_with_slashes"))
    suite.addTests(loader.loadTestsFromName("tests.test_cli_commands"))
    suite.addTests(loader.loadTestsFromName("tests.test_models"))
    suite.addTests(loader.loadTestsFromName("tests.test_wrapper"))
    suite.addTests(loader.loadTestsFromName("tests.test_checklist_item_model"))
    suite.addTests(loader.loadTestsFromName("tests.test_checklist_wrapper"))
    suite.addTests(loader.loadTestsFromName("tests.test_checklist_cli"))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with non-zero status if tests failed
    sys.exit(not result.wasSuccessful())
