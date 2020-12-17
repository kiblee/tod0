import unittest
from datetime import datetime, timedelta

from todocli.datetime_parser import (
    parse_datetime,
    add_day_if_past,
    ErrorParsingTime,
    TimeExpressionNotRecognized,
)


class TestDatetimeParser(unittest.TestCase):
    def test_sadd_day_if_datetime_is_in_past(self):
        dt_now = datetime.now()
        dt = dt_now - timedelta(minutes=1)
        dt = add_day_if_past(dt)
        assert dt.day > dt_now.day

        dt = dt_now + timedelta(hours=1)
        dt = add_day_if_past(dt)
        assert dt.day == dt_now.day

    def test_am_pm_time1(self):
        input_str = "07:00 pm"
        dt = parse_datetime(input_str)
        dt_expected = datetime.now().replace(hour=19, minute=0, second=0, microsecond=0)
        dt_expected = add_day_if_past(dt_expected)
        assert dt == dt_expected

    def test_am_pm_time2(self):
        input_str = "7:00 pm"
        dt = parse_datetime(input_str)
        dt_expected = datetime.now().replace(hour=19, minute=0, second=0, microsecond=0)
        dt_expected = add_day_if_past(dt_expected)
        assert dt == dt_expected

    def test_am_pm_time3(self):
        input_str = "12:00 am"
        dt = parse_datetime(input_str)
        dt_expected = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        dt_expected = add_day_if_past(dt_expected)
        assert dt == dt_expected

    def test_time_strings(self):
        times = [
            "07:00",
            "7:00",
            "0:00",
            "17:30",
            "6:30 am",
            "6:30 pm",
            "06:30 am",
            "06:30 pm",
            "00:00 am",
            "12:00 am",
            "24.06. 12:00",
            "24.06. 6:00",
            "24.6. 6:00",
            "24.6. 06:00",
            "24.6. 12:00",
            "6.6. 06:06",
            "6.6. 6:06",
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
            "morning",
            "evening",
            "tomorrow",
        ]

        for time in times:
            print(f"testing time: {time}")
            parse_datetime(time)

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
