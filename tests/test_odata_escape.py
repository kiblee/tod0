#!/usr/bin/env python3
"""Unit tests for OData string escaping in graph API wrapper"""

import unittest
from unittest.mock import patch, MagicMock
from todocli.graphapi.wrapper import (
    _escape_odata_string,
    get_task_id_by_name,
    TaskNotFoundByName,
)


class TestEscapeOdataString(unittest.TestCase):
    """Test _escape_odata_string helper"""

    def test_plain_text_unchanged(self):
        """Test that plain text passes through unchanged"""
        self.assertEqual(_escape_odata_string("Buy milk"), "Buy milk")

    def test_cyrillic_text_unchanged(self):
        """Test that Cyrillic text passes through unchanged"""
        self.assertEqual(
            _escape_odata_string("Купить молоко"),
            "Купить молоко",
        )

    def test_single_quote_doubled(self):
        """Test that single quotes are doubled per OData spec"""
        self.assertEqual(_escape_odata_string("it's done"), "it''s done")

    def test_multiple_single_quotes(self):
        """Test multiple single quotes in one string"""
        self.assertEqual(
            _escape_odata_string("it's Alice's task"),
            "it''s Alice''s task",
        )

    def test_hash_double_encoded(self):
        """Test that '#' is double-percent-encoded for URL safety"""
        self.assertEqual(
            _escape_odata_string("task #tag"),
            "task %2523tag",
        )

    def test_ampersand_double_encoded(self):
        """Test that '&' is double-percent-encoded for URL safety"""
        self.assertEqual(
            _escape_odata_string("bread & butter"),
            "bread %2526 butter",
        )

    def test_plus_double_encoded(self):
        """Test that '+' is double-percent-encoded for URL safety"""
        self.assertEqual(
            _escape_odata_string("1+1=2"),
            "1%252B1=2",
        )

    def test_all_special_chars_combined(self):
        """Test string with all special characters at once"""
        self.assertEqual(
            _escape_odata_string("it's a #tag & 1+1"),
            "it''s a %2523tag %2526 1%252B1",
        )

    def test_empty_string(self):
        """Test that empty string returns empty string"""
        self.assertEqual(_escape_odata_string(""), "")

    def test_only_special_chars(self):
        """Test string consisting entirely of special characters"""
        self.assertEqual(_escape_odata_string("#&#"), "%2523%2526%2523")

    def test_safe_url_chars_unchanged(self):
        """Test that other URL-safe special chars are not affected"""
        for char in ["?", "=", "/", ":", "(", ")"]:
            value = f"task {char} test"
            self.assertEqual(
                _escape_odata_string(value),
                value,
                f"Character '{char}' should not be escaped",
            )


class TestGetTaskIdByNameEndpoint(unittest.TestCase):
    """Test that get_task_id_by_name builds the correct OData filter URL"""

    @patch("todocli.graphapi.wrapper.get_oauth_session")
    @patch("todocli.graphapi.wrapper.get_list_id_by_name")
    def test_plain_name_filter(self, mock_get_list_id, mock_get_session):
        """Test OData filter URL for a plain task name"""
        mock_get_list_id.return_value = "list123"
        mock_response = MagicMock()
        mock_response.content = b'{"value": [{"id": "task1", "title": "Buy milk", "importance": "normal", "status": "notStarted", "createdDateTime": "2024-01-01T00:00:00.0000000Z", "lastModifiedDateTime": "2024-01-01T00:00:00.0000000Z", "isReminderOn": false}]}'
        mock_get_session.return_value.get.return_value = mock_response

        get_task_id_by_name("Tasks", "Buy milk")

        called_url = mock_get_session.return_value.get.call_args[0][0]
        self.assertIn("$filter=title eq 'Buy milk'", called_url)

    @patch("todocli.graphapi.wrapper.get_oauth_session")
    @patch("todocli.graphapi.wrapper.get_list_id_by_name")
    def test_hash_tag_filter(self, mock_get_list_id, mock_get_session):
        """Test OData filter URL for task name containing '#' (tag)"""
        mock_get_list_id.return_value = "list123"
        mock_response = MagicMock()
        mock_response.content = b'{"value": [{"id": "task1", "title": "Do stuff #work", "importance": "normal", "status": "notStarted", "createdDateTime": "2024-01-01T00:00:00.0000000Z", "lastModifiedDateTime": "2024-01-01T00:00:00.0000000Z", "isReminderOn": false}]}'
        mock_get_session.return_value.get.return_value = mock_response

        get_task_id_by_name("Tasks", "Do stuff #work")

        called_url = mock_get_session.return_value.get.call_args[0][0]
        self.assertIn("%2523", called_url)
        self.assertNotIn("#work", called_url)

    @patch("todocli.graphapi.wrapper.get_oauth_session")
    @patch("todocli.graphapi.wrapper.get_list_id_by_name")
    def test_ampersand_filter(self, mock_get_list_id, mock_get_session):
        """Test OData filter URL for task name containing '&'"""
        mock_get_list_id.return_value = "list123"
        mock_response = MagicMock()
        mock_response.content = b'{"value": [{"id": "task1", "title": "bread & butter", "importance": "normal", "status": "notStarted", "createdDateTime": "2024-01-01T00:00:00.0000000Z", "lastModifiedDateTime": "2024-01-01T00:00:00.0000000Z", "isReminderOn": false}]}'
        mock_get_session.return_value.get.return_value = mock_response

        get_task_id_by_name("Tasks", "bread & butter")

        called_url = mock_get_session.return_value.get.call_args[0][0]
        self.assertIn("%2526", called_url)
        self.assertNotIn("& butter", called_url)

    @patch("todocli.graphapi.wrapper.get_oauth_session")
    @patch("todocli.graphapi.wrapper.get_list_id_by_name")
    def test_plus_filter(self, mock_get_list_id, mock_get_session):
        """Test OData filter URL for task name containing '+'"""
        mock_get_list_id.return_value = "list123"
        mock_response = MagicMock()
        mock_response.content = b'{"value": [{"id": "task1", "title": "1+1=2", "importance": "normal", "status": "notStarted", "createdDateTime": "2024-01-01T00:00:00.0000000Z", "lastModifiedDateTime": "2024-01-01T00:00:00.0000000Z", "isReminderOn": false}]}'
        mock_get_session.return_value.get.return_value = mock_response

        get_task_id_by_name("Tasks", "1+1=2")

        called_url = mock_get_session.return_value.get.call_args[0][0]
        self.assertIn("%252B", called_url)
        self.assertNotIn("+1", called_url)

    @patch("todocli.graphapi.wrapper.get_oauth_session")
    @patch("todocli.graphapi.wrapper.get_list_id_by_name")
    def test_single_quote_filter(self, mock_get_list_id, mock_get_session):
        """Test OData filter URL for task name containing single quote"""
        mock_get_list_id.return_value = "list123"
        mock_response = MagicMock()
        mock_response.content = b'{"value": [{"id": "task1", "title": "it\'s done", "importance": "normal", "status": "notStarted", "createdDateTime": "2024-01-01T00:00:00.0000000Z", "lastModifiedDateTime": "2024-01-01T00:00:00.0000000Z", "isReminderOn": false}]}'
        mock_get_session.return_value.get.return_value = mock_response

        get_task_id_by_name("Tasks", "it's done")

        called_url = mock_get_session.return_value.get.call_args[0][0]
        self.assertIn("it''s done", called_url)

    @patch("todocli.graphapi.wrapper.get_oauth_session")
    @patch("todocli.graphapi.wrapper.get_list_id_by_name")
    def test_not_found_raises_exception(self, mock_get_list_id, mock_get_session):
        """Test that TaskNotFoundByName is raised for non-existent task"""
        mock_get_list_id.return_value = "list123"
        mock_response = MagicMock()
        mock_response.content = b'{"value": []}'
        mock_get_session.return_value.get.return_value = mock_response

        with self.assertRaises(TaskNotFoundByName):
            get_task_id_by_name("Tasks", "NonExistent")


if __name__ == "__main__":
    unittest.main()
