"""Turn a recycle.gov.sg return point into a status label.

Mirrors the badge logic on recycle.gov.sg. Kept free of Home Assistant
imports so it can be tested on its own.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

# Opening hours from the API are Singapore local time.
SG_TZ = ZoneInfo("Asia/Singapore")

# Never "unavailable" or "unknown": those are reserved Home Assistant states.
STATUSES = [
    "available",
    "filling_fast",
    "closed",
    "maintenance",
    "full",
    "out_of_service",
    "removed",
    "not_launched",
]

_MINUTES_PER_WEEK = 7 * 24 * 60

_OUT_OF_SERVICE = {"OUT_OF_SERVICE", "UNAVAILABLE", "SUSPENDED", "OFFLINE", "ERROR"}
_REMOVED = {"REMOVED", "DECOMMISSIONED"}
_MAINTENANCE = {"MAINTENANCE", "UNDER_MAINTENANCE", "CLEANING", "SERVICE", "IN_SERVICE"}
_NOT_LAUNCHED = {"COMING_SOON", "PRE_LAUNCH"}


def _week_minute(day: int, hhmm: str) -> int:
    return day * 1440 + int(hhmm[:2]) * 60 + int(hhmm[2:4])


def is_open(opening_hours: dict[str, Any] | None, now: datetime) -> bool:
    """Whether the venue is open. Day 0 is Sunday, as in Google Places data."""
    if not opening_hours or opening_hours.get("alwaysOpen"):
        return True
    periods = opening_hours.get("periods")
    if not periods:
        return True
    now = now.astimezone(SG_TZ)
    current = _week_minute(now.isoweekday() % 7, now.strftime("%H%M"))
    for period in periods:
        if not period.get("close"):
            return True
        start = _week_minute(period["open"]["day"], period["open"]["time"])
        end = _week_minute(period["close"]["day"], period["close"]["time"])
        if end <= start:
            end += _MINUTES_PER_WEEK
        if start <= current < end or start <= current + _MINUTES_PER_WEEK < end:
            return True
    return False


def machine_status(point: dict[str, Any], now: datetime) -> str:
    """Status key for a return point, one of STATUSES."""
    raw = str(point.get("machineStatus") or "").strip()
    open_now = is_open(point.get("openingHours"), now)

    try:
        fill = float(raw)
    except ValueError:
        fill = None
    if fill is not None:
        if fill >= 100:
            return "full"
        if not open_now:
            return "closed"
        return "filling_fast" if fill > 75 else "available"

    key = "_".join(raw.upper().replace("-", " ").split())
    if key == "FULL":
        return "full"
    if key in _OUT_OF_SERVICE:
        return "out_of_service"
    if key in _REMOVED:
        return "removed"
    if key in _MAINTENANCE:
        return "maintenance"
    if key in _NOT_LAUNCHED:
        return "not_launched"
    return "available" if open_now else "closed"


def hours_today(point: dict[str, Any], now: datetime) -> str | None:
    """Today's opening hours as the site writes them, e.g. "10 am - 10 pm"."""
    opening_hours = point.get("openingHours")
    if not opening_hours:
        return None
    if opening_hours.get("alwaysOpen"):
        return "Open 24 hours"
    day = now.astimezone(SG_TZ).strftime("%A")
    for line in opening_hours.get("weekdayText") or []:
        name, _, hours = line.partition(": ")
        if name == day:
            return hours or None
    return None
