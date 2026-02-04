#!/usr/bin/env python3
"""Unit tests for recurrence expression parsing"""

import unittest
from datetime import date
from unittest.mock import patch

from todocli.utils.recurrence_util import parse_recurrence, InvalidRecurrenceExpression


class TestParseRecurrence(unittest.TestCase):
    """Test parse_recurrence function"""

    def setUp(self):
        self.today = date(2026, 2, 4)
        self.patcher = patch(
            "todocli.utils.recurrence_util.date",
            wraps=date,
        )
        self.mock_date = self.patcher.start()
        self.mock_date.today.return_value = self.today

    def tearDown(self):
        self.patcher.stop()

    def test_none_input(self):
        """Test None input returns None"""
        self.assertIsNone(parse_recurrence(None))

    def test_empty_string(self):
        """Test empty string returns None"""
        self.assertIsNone(parse_recurrence(""))
        self.assertIsNone(parse_recurrence("   "))

    def test_daily(self):
        """Test 'daily' preset"""
        result = parse_recurrence("daily")
        self.assertEqual(result["pattern"]["type"], "daily")
        self.assertEqual(result["pattern"]["interval"], 1)
        self.assertEqual(result["range"]["type"], "noEnd")
        self.assertEqual(result["range"]["startDate"], "2026-02-04")

    def test_weekly(self):
        """Test 'weekly' preset"""
        result = parse_recurrence("weekly")
        self.assertEqual(result["pattern"]["type"], "weekly")
        self.assertEqual(result["pattern"]["interval"], 1)

    def test_weekdays(self):
        """Test 'weekdays' preset sets mon-fri"""
        result = parse_recurrence("weekdays")
        self.assertEqual(result["pattern"]["type"], "weekly")
        self.assertEqual(result["pattern"]["interval"], 1)
        self.assertEqual(
            result["pattern"]["daysOfWeek"],
            ["monday", "tuesday", "wednesday", "thursday", "friday"],
        )

    def test_monthly(self):
        """Test 'monthly' preset sets dayOfMonth from today"""
        result = parse_recurrence("monthly")
        self.assertEqual(result["pattern"]["type"], "absoluteMonthly")
        self.assertEqual(result["pattern"]["interval"], 1)
        self.assertEqual(result["pattern"]["dayOfMonth"], 4)

    def test_yearly(self):
        """Test 'yearly' preset sets dayOfMonth and month from today"""
        result = parse_recurrence("yearly")
        self.assertEqual(result["pattern"]["type"], "absoluteYearly")
        self.assertEqual(result["pattern"]["interval"], 1)
        self.assertEqual(result["pattern"]["dayOfMonth"], 4)
        self.assertEqual(result["pattern"]["month"], 2)

    def test_every_n_days(self):
        """Test 'every 2 days' custom interval"""
        result = parse_recurrence("every 2 days")
        self.assertEqual(result["pattern"]["type"], "daily")
        self.assertEqual(result["pattern"]["interval"], 2)

    def test_every_n_weeks(self):
        """Test 'every 3 weeks' custom interval"""
        result = parse_recurrence("every 3 weeks")
        self.assertEqual(result["pattern"]["type"], "weekly")
        self.assertEqual(result["pattern"]["interval"], 3)

    def test_every_n_months(self):
        """Test 'every 2 months' custom interval"""
        result = parse_recurrence("every 2 months")
        self.assertEqual(result["pattern"]["type"], "absoluteMonthly")
        self.assertEqual(result["pattern"]["interval"], 2)
        self.assertEqual(result["pattern"]["dayOfMonth"], 4)

    def test_every_n_years(self):
        """Test 'every 1 year' custom interval"""
        result = parse_recurrence("every 1 year")
        self.assertEqual(result["pattern"]["type"], "absoluteYearly")
        self.assertEqual(result["pattern"]["interval"], 1)

    def test_weekly_with_days(self):
        """Test 'weekly:mon,fri' with day specifiers"""
        result = parse_recurrence("weekly:mon,fri")
        self.assertEqual(result["pattern"]["type"], "weekly")
        self.assertEqual(result["pattern"]["interval"], 1)
        self.assertEqual(result["pattern"]["daysOfWeek"], ["monday", "friday"])

    def test_every_n_weeks_with_days(self):
        """Test 'every 2 weeks:mon,wed,fri' with day specifiers"""
        result = parse_recurrence("every 2 weeks:mon,wed,fri")
        self.assertEqual(result["pattern"]["type"], "weekly")
        self.assertEqual(result["pattern"]["interval"], 2)
        self.assertEqual(
            result["pattern"]["daysOfWeek"], ["monday", "wednesday", "friday"]
        )

    def test_case_insensitive(self):
        """Test that input is case insensitive"""
        result = parse_recurrence("Daily")
        self.assertEqual(result["pattern"]["type"], "daily")

        result = parse_recurrence("WEEKLY:MON,FRI")
        self.assertEqual(result["pattern"]["daysOfWeek"], ["monday", "friday"])

    def test_whitespace_handling(self):
        """Test that extra whitespace is handled"""
        result = parse_recurrence("  daily  ")
        self.assertEqual(result["pattern"]["type"], "daily")

    def test_invalid_expression(self):
        """Test that invalid expressions raise InvalidRecurrenceExpression"""
        with self.assertRaises(InvalidRecurrenceExpression):
            parse_recurrence("biweekly")

    def test_invalid_day_abbreviation(self):
        """Test that invalid day abbreviations raise InvalidRecurrenceExpression"""
        with self.assertRaises(InvalidRecurrenceExpression):
            parse_recurrence("weekly:monday,fri")

    def test_range_always_no_end(self):
        """Test that range is always noEnd with today's date"""
        for expr in ["daily", "weekly", "monthly", "yearly"]:
            result = parse_recurrence(expr)
            self.assertEqual(result["range"]["type"], "noEnd")
            self.assertEqual(result["range"]["startDate"], "2026-02-04")

    def test_singular_unit(self):
        """Test singular unit forms work"""
        result = parse_recurrence("every 1 day")
        self.assertEqual(result["pattern"]["type"], "daily")
        self.assertEqual(result["pattern"]["interval"], 1)

        result = parse_recurrence("every 1 week")
        self.assertEqual(result["pattern"]["type"], "weekly")

        result = parse_recurrence("every 1 month")
        self.assertEqual(result["pattern"]["type"], "absoluteMonthly")


if __name__ == "__main__":
    unittest.main()
