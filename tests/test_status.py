"""Tests for the status logic. Run: python3 -m unittest discover tests"""

import importlib.util
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Load status.py directly: the package __init__ needs Home Assistant.
_path = Path(__file__).parent.parent / "custom_components" / "bcrs_availability" / "status.py"
_spec = importlib.util.spec_from_file_location("bcrs_status", _path)
status = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(status)

SG = ZoneInfo("Asia/Singapore")
TUESDAY_NOON = datetime(2026, 10, 27, 12, 0, tzinfo=SG)
TUESDAY_LATE = datetime(2026, 10, 27, 23, 30, tzinfo=SG)

DAILY_10_TO_22 = {
    "alwaysOpen": False,
    "periods": [{"open": {"day": d, "time": "1000"}, "close": {"day": d, "time": "2200"}} for d in range(7)],
    "weekdayText": [
        f"{day}: 10 am - 10 pm"
        for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    ],
}


def point(machine_status, opening_hours=DAILY_10_TO_22):
    return {"machineStatus": machine_status, "openingHours": opening_hours}


class MachineStatusTest(unittest.TestCase):
    def test_running_and_open(self):
        self.assertEqual(status.machine_status(point("RUNNING"), TUESDAY_NOON), "available")

    def test_running_but_venue_closed(self):
        self.assertEqual(status.machine_status(point("RUNNING"), TUESDAY_LATE), "closed")

    def test_full_overrides_hours(self):
        self.assertEqual(status.machine_status(point("full"), TUESDAY_LATE), "full")

    def test_spellings_are_normalised(self):
        self.assertEqual(status.machine_status(point("out-of-service"), TUESDAY_NOON), "out_of_service")
        self.assertEqual(status.machine_status(point("Under Maintenance"), TUESDAY_NOON), "maintenance")
        self.assertEqual(status.machine_status(point("DECOMMISSIONED"), TUESDAY_NOON), "removed")
        self.assertEqual(status.machine_status(point("PRE_LAUNCH"), TUESDAY_NOON), "not_launched")

    def test_fill_level(self):
        self.assertEqual(status.machine_status(point("80"), TUESDAY_NOON), "filling_fast")
        self.assertEqual(status.machine_status(point("40"), TUESDAY_NOON), "available")
        self.assertEqual(status.machine_status(point(100), TUESDAY_LATE), "full")
        self.assertEqual(status.machine_status(point("40"), TUESDAY_LATE), "closed")

    def test_unknown_or_missing_status_follows_hours(self):
        self.assertEqual(status.machine_status(point(None), TUESDAY_NOON), "available")
        self.assertEqual(status.machine_status(point("UNKNOWN"), TUESDAY_LATE), "closed")

    def test_no_hours_listed_counts_as_open(self):
        self.assertEqual(status.machine_status(point("RUNNING", None), TUESDAY_LATE), "available")

    def test_never_returns_reserved_states(self):
        for raw in ("UNAVAILABLE", "OFFLINE", "UNKNOWN", "", None):
            self.assertNotIn(status.machine_status(point(raw), TUESDAY_NOON), ("unavailable", "unknown"))


class OpeningHoursTest(unittest.TestCase):
    def test_overnight_period_wraps(self):
        hours = {"periods": [{"open": {"day": 2, "time": "2000"}, "close": {"day": 3, "time": "0200"}}]}
        self.assertTrue(status.is_open(hours, TUESDAY_LATE))
        self.assertFalse(status.is_open(hours, TUESDAY_NOON))

    def test_saturday_to_sunday_wraps_around_the_week(self):
        hours = {"periods": [{"open": {"day": 6, "time": "2200"}, "close": {"day": 0, "time": "0200"}}]}
        self.assertTrue(status.is_open(hours, datetime(2026, 11, 1, 1, 0, tzinfo=SG)))  # Sunday 1 am

    def test_period_without_close_is_24_hours(self):
        self.assertTrue(status.is_open({"periods": [{"open": {"day": 0, "time": "0000"}}]}, TUESDAY_LATE))

    def test_uses_singapore_time_whatever_the_input_zone(self):
        utc_noon_sg = datetime(2026, 10, 27, 4, 0, tzinfo=ZoneInfo("UTC"))
        self.assertTrue(status.is_open(DAILY_10_TO_22, utc_noon_sg))


class HoursTodayTest(unittest.TestCase):
    def test_todays_line(self):
        self.assertEqual(status.hours_today(point("RUNNING"), TUESDAY_NOON), "10 am - 10 pm")

    def test_always_open(self):
        self.assertEqual(status.hours_today(point("RUNNING", {"alwaysOpen": True}), TUESDAY_NOON), "Open 24 hours")

    def test_not_listed(self):
        self.assertIsNone(status.hours_today(point("RUNNING", None), TUESDAY_NOON))


if __name__ == "__main__":
    unittest.main()
