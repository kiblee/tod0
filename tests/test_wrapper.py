#!/usr/bin/env python3
"""Unit tests for graph API wrapper module"""

import unittest
from todocli.graphapi.wrapper import (
    ListNotFound,
    TaskNotFoundByName,
    TaskNotFoundByIndex,
    BASE_URL,
    BATCH_URL,
)


class TestWrapperExceptions(unittest.TestCase):
    """Test custom exception classes"""

    def test_list_not_found_exception(self):
        """Test ListNotFound exception message"""
        list_name = "NonExistentList"
        exc = ListNotFound(list_name)

        self.assertIn(list_name, exc.message)
        self.assertIn("could not be found", exc.message)

    def test_task_not_found_by_name_exception(self):
        """Test TaskNotFoundByName exception message"""
        task_name = "NonExistentTask"
        list_name = "Personal"
        exc = TaskNotFoundByName(task_name, list_name)

        self.assertIn(task_name, exc.message)
        self.assertIn(list_name, exc.message)
        self.assertIn("could not be found", exc.message)

    def test_task_not_found_by_index_exception(self):
        """Test TaskNotFoundByIndex exception message"""
        task_index = 999
        list_name = "Personal"
        exc = TaskNotFoundByIndex(task_index, list_name)

        self.assertIn(str(task_index), exc.message)
        self.assertIn(list_name, exc.message)
        self.assertIn("could not be found", exc.message)


class TestWrapperConstants(unittest.TestCase):
    """Test API endpoint URL constants"""

    def test_base_url_format(self):
        """Test BASE_URL is correctly formatted"""
        self.assertTrue(BASE_URL.startswith("https://graph.microsoft.com"))
        self.assertIn("/me/todo/lists", BASE_URL)

    def test_batch_url_format(self):
        """Test BATCH_URL is correctly formatted"""
        self.assertTrue(BATCH_URL.startswith("https://graph.microsoft.com"))
        self.assertIn("/$batch", BATCH_URL)


if __name__ == "__main__":
    unittest.main()
