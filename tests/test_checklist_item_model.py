#!/usr/bin/env python3
"""Unit tests for ChecklistItem model"""

import unittest
from todocli.models.checklistitem import ChecklistItem


class TestChecklistItemModel(unittest.TestCase):
    """Test ChecklistItem model initialization and properties"""

    def test_basic_item_creation(self):
        """Test creating a ChecklistItem from API response"""
        api_response = {
            "id": "step123",
            "displayName": "Buy eggs",
            "isChecked": False,
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
        }
        item = ChecklistItem(api_response)

        self.assertEqual(item.id, "step123")
        self.assertEqual(item.display_name, "Buy eggs")
        self.assertFalse(item.is_checked)
        self.assertIsNotNone(item.created_datetime)
        self.assertIsNone(item.checked_datetime)

    def test_checked_item(self):
        """Test creating a checked ChecklistItem"""
        api_response = {
            "id": "step456",
            "displayName": "Buy milk",
            "isChecked": True,
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
            "checkedDateTime": "2024-01-25T11:00:00.0000000Z",
        }
        item = ChecklistItem(api_response)

        self.assertTrue(item.is_checked)
        self.assertIsNotNone(item.checked_datetime)

    def test_unchecked_item_no_checked_datetime(self):
        """Test that unchecked item has no checked_datetime"""
        api_response = {
            "id": "step789",
            "displayName": "Buy bread",
            "isChecked": False,
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
        }
        item = ChecklistItem(api_response)

        self.assertFalse(item.is_checked)
        self.assertIsNone(item.checked_datetime)

    def test_checked_datetime_null_value(self):
        """Test that null checkedDateTime is handled as None"""
        api_response = {
            "id": "step101",
            "displayName": "Clean kitchen",
            "isChecked": False,
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
            "checkedDateTime": None,
        }
        item = ChecklistItem(api_response)

        self.assertFalse(item.is_checked)
        self.assertIsNone(item.checked_datetime)

    def test_display_name_preserved(self):
        """Test that display name with special characters is preserved"""
        api_response = {
            "id": "step201",
            "displayName": "Check A/B testing results (urgent!)",
            "isChecked": False,
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
        }
        item = ChecklistItem(api_response)

        self.assertEqual(item.display_name, "Check A/B testing results (urgent!)")

    def test_datetime_without_fractional_seconds(self):
        """Test parsing datetime without fractional seconds (checklistItems API format)"""
        api_response = {
            "id": "step301",
            "displayName": "Step",
            "isChecked": True,
            "createdDateTime": "2026-02-04T19:08:45Z",
            "checkedDateTime": "2026-02-04T19:10:00Z",
        }
        item = ChecklistItem(api_response)

        self.assertIsNotNone(item.created_datetime)
        self.assertIsNotNone(item.checked_datetime)

    def test_datetime_with_fractional_seconds(self):
        """Test parsing datetime with fractional seconds (standard Graph API format)"""
        api_response = {
            "id": "step401",
            "displayName": "Step",
            "isChecked": False,
            "createdDateTime": "2024-01-25T10:00:00.0000000Z",
        }
        item = ChecklistItem(api_response)

        self.assertIsNotNone(item.created_datetime)


if __name__ == "__main__":
    unittest.main()
