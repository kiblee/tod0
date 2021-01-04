import unittest
import todocli

from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from todocli.utils.datetime_util import (
    parse_datetime,
    add_day_if_past,
    ErrorParsingTime,
    TimeExpressionNotRecognized,
)


class TestDatetimeParser(unittest.TestCase):
    @patch.object(todocli.utils.datetime_util, "datetime", Mock(wraps=datetime))
    def test_add_day_if_datetime_is_in_past(self):
        dt_now = datetime(2020, 1, 1, 9, 0)
        todocli.utils.datetime_util.datetime.now.return_value = dt_now
        dt = dt_now - timedelta(minutes=1)
        dt = add_day_if_past(dt)
        self.assertGreater(dt.day, dt_now.day)

        dt = dt_now + timedelta(hours=1)
        dt = add_day_if_past(dt)
        self.assertEqual(dt.day, dt_now.day)

    def test_am_pm_time1(self):
        input_str = "07:00 pm"
        dt = parse_datetime(input_str)
        dt_expected = datetime.now().replace(hour=19, minute=0, second=0, microsecond=0)
        dt_expected = add_day_if_past(dt_expected)
        self.assertEqual(dt, dt_expected)

    def test_am_pm_time2(self):
        input_str = "7:00 pm"
        dt = parse_datetime(input_str)
        dt_expected = datetime.now().replace(hour=19, minute=0, second=0, microsecond=0)
        dt_expected = add_day_if_past(dt_expected)
        self.assertEqual(dt, dt_expected)

    def test_am_pm_time3(self):
        input_str = "12:00 am"
        dt = parse_datetime(input_str)
        dt_expected = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        dt_expected = add_day_if_past(dt_expected)
        self.assertEqual(dt, dt_expected)

    @patch.object(todocli.utils.datetime_util, "datetime", Mock(wraps=datetime))
    def test_time_strings(self):
        # (user input, simulated 'now' time, expected output)
        times = [
            ("07:00", datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 2, 7, 0)),
            ("7:00", datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 2, 7, 0)),
            ("0:00", datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 2, 0, 0)),
            ("17:30", datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 1, 17, 30)),
            ("6:30 am", datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 2, 6, 30)),
            ("6:30 pm", datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 1, 18, 30)),
            ("06:30 am", datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 2, 6, 30)),
            ("06:30 pm", datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 1, 18, 30)),
            ("00:00 am", datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 2, 0, 0)),
            ("12:00 am", datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 2, 0, 0)),
            ("24.06. 12:00", datetime(2020, 6, 24, 9, 0), datetime(2020, 6, 24, 12, 0)),
            ("24.06. 6:00", datetime(2020, 6, 23, 9, 0), datetime(2020, 6, 24, 6, 0)),
            ("24.6. 6:00", datetime(2020, 6, 23, 9, 0), datetime(2020, 6, 24, 6, 0)),
            ("24.6. 06:00", datetime(2020, 6, 23, 9, 0), datetime(2020, 6, 24, 6, 0)),
            ("24.6. 12:00", datetime(2020, 6, 24, 9, 0), datetime(2020, 6, 24, 12, 0)),
            ("6.6. 06:06", datetime(2020, 6, 5, 9, 0), datetime(2020, 6, 6, 6, 6)),
            ("6.6. 6:06", datetime(2020, 6, 5, 9, 0), datetime(2020, 6, 6, 6, 6)),
            # "04/27 12:00 am",
            # "04/27 2:00 am",
            # "04/27 3:00 pm",
            # "04/27 10:00 pm",
            # "4/27 10:00 pm",
            # "4/27 09:00 pm",
            # "4/27 9:00 pm",
            # "4/4 9:00 pm",
            # "4/4 09:00 pm",
            # "4/4 12:00 pm",
            ("morning", datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 2, 7, 0)),
            ("evening", datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 1, 18, 0)),
            ("tomorrow", datetime(2020, 1, 1, 9, 0), datetime(2020, 1, 2, 7, 0)),
        ]

        for user_input, simulated_now_time, expected_output in times:
            print(f"testing time: {user_input}")
            todocli.utils.datetime_util.datetime.now.return_value = simulated_now_time
            return_val = parse_datetime(user_input)
            self.assertEqual(return_val, expected_output)

    def test_invalid_time(self):
        invalid_times = [
            "24:00",
            "25:00",
            "25123:00",
            "0:12345",
            "12:30 sam",
            "12:30 pom",
            "abfdsa",
        ]

        for time in invalid_times:
            print(f"testing time: {time}")
            try:
                self.assertRaises(Exception, parse_datetime(time))
            except ErrorParsingTime:
                pass
            except TimeExpressionNotRecognized:
                pass
            else:
                raise


if __name__ == "__main__":
    unittest.main()
