#!/usr/bin/env python3
"""Unit tests for checklist item wrapper functions"""

import unittest
from todocli.graphapi.wrapper import (
    StepNotFoundByName,
    StepNotFoundByIndex,
    BASE_URL,
)


class TestStepExceptions(unittest.TestCase):
    """Test step-related exception classes"""

    def test_step_not_found_by_name_exception(self):
        """Test StepNotFoundByName exception message"""
        step_name = "NonExistentStep"
        task_name = "Buy groceries"
        exc = StepNotFoundByName(step_name, task_name)

        self.assertIn(step_name, exc.message)
        self.assertIn(task_name, exc.message)
        self.assertIn("could not be found", exc.message)

    def test_step_not_found_by_index_exception(self):
        """Test StepNotFoundByIndex exception message"""
        step_index = 999
        task_name = "Buy groceries"
        exc = StepNotFoundByIndex(step_index, task_name)

        self.assertIn(str(step_index), exc.message)
        self.assertIn(task_name, exc.message)
        self.assertIn("could not be found", exc.message)


class TestChecklistEndpointPattern(unittest.TestCase):
    """Test that the checklist endpoint URL is correctly constructed"""

    def test_checklist_endpoint_format(self):
        """Test the checklistItems endpoint follows the expected pattern"""
        list_id = "list123"
        task_id = "task456"
        endpoint = f"{BASE_URL}/{list_id}/tasks/{task_id}/checklistItems"

        self.assertIn("checklistItems", endpoint)
        self.assertIn(list_id, endpoint)
        self.assertIn(task_id, endpoint)
        self.assertTrue(endpoint.startswith("https://graph.microsoft.com"))

    def test_checklist_item_endpoint_format(self):
        """Test individual checklistItem endpoint format"""
        list_id = "list123"
        task_id = "task456"
        step_id = "step789"
        endpoint = f"{BASE_URL}/{list_id}/tasks/{task_id}/checklistItems/{step_id}"

        self.assertIn(step_id, endpoint)
        self.assertTrue(endpoint.endswith(step_id))


if __name__ == "__main__":
    unittest.main()
