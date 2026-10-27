"""Client for the recycle.gov.sg map API and OneMap postal code search.

recycle.gov.sg has no documented API. This uses the same requests as the
"Find a return point" map on https://www.recycle.gov.sg/materials/beverage.
Machine IDs there get reissued, so machines are found by location and name.
"""

from __future__ import annotations

import json
import math
from typing import Any

import aiohttp

from .const import SEARCH_RADIUS_M

API_BASE = "https://www.recycle.gov.sg/api/trpc"
ONEMAP_SEARCH = "https://www.onemap.gov.sg/api/common/elastic/search"
USER_AGENT = "bcrs-availability-for-home-assistant (+https://github.com/kalestarler/bcrs-availability-for-home-assistant)"
TIMEOUT = aiohttp.ClientTimeout(total=30)

_MATERIALS = {
    m: m == "BEVERAGE"
    for m in ("PAPER", "PLASTIC", "METAL", "GLASS", "EWASTE", "TEXTILE", "BEVERAGE", "OTHER")
}
_EWASTE = {m: False for m in ("BATTERIES", "LAMPS", "ICT_EQUIPMENT", "INK", "TONER_CARTRIDGES")}
_SINGAPORE_BOUNDS = {"neLat": 1.48, "neLng": 104.1, "swLat": 1.15, "swLng": 103.59}


class BcrsApiError(Exception):
    """recycle.gov.sg or OneMap could not be reached or replied unexpectedly."""


async def _get_json(session: aiohttp.ClientSession, url: str, params: dict[str, str]) -> Any:
    try:
        async with session.get(
            url, params=params, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT
        ) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=None)
    except (aiohttp.ClientError, TimeoutError, ValueError) as err:
        raise BcrsApiError(f"Request to {url} failed: {err}") from err


async def _trpc(session: aiohttp.ClientSession, procedure: str, query: dict[str, Any]) -> list[dict[str, Any]]:
    data = await _get_json(
        session,
        f"{API_BASE}/{procedure}",
        {"input": json.dumps({"json": query}, separators=(",", ":"))},
    )
    try:
        points = data["result"]["data"]["json"]
    except (KeyError, TypeError) as err:
        raise BcrsApiError(f"Unexpected reply from {procedure}") from err
    if not isinstance(points, list):
        raise BcrsApiError(f"Unexpected reply from {procedure}")
    return points


async def async_get_all_machines(session: aiohttp.ClientSession) -> list[dict[str, Any]]:
    """Every BCRS machine in Singapore: name and coordinates, no live status."""
    return await _trpc(
        session,
        "recyclingPoints.filteredByMaterialInBounds",
        {"filter": _MATERIALS, "eWasteFilter": _EWASTE, "bounds": _SINGAPORE_BOUNDS, "openOnly": False},
    )


async def async_get_machines_near(
    session: aiohttp.ClientSession, lat: float, lng: float, radius: int = SEARCH_RADIUS_M
) -> list[dict[str, Any]]:
    """BCRS machines within `radius` metres, with live status and opening hours."""
    return await _trpc(
        session,
        "recyclingPoints.filteredWithinRadius",
        {
            "center": {"lat": lat, "long": lng},
            "radius": radius,
            "openOnly": False,
            "filter": _MATERIALS,
            "eWasteFilter": _EWASTE,
        },
    )


async def async_geocode_postal_code(
    session: aiohttp.ClientSession, postal_code: str
) -> tuple[float, float, str] | None:
    """Latitude, longitude and a label for a Singapore postal code, or None."""
    data = await _get_json(
        session,
        ONEMAP_SEARCH,
        {"searchVal": postal_code, "returnGeom": "Y", "getAddrDetails": "N", "pageNum": "1"},
    )
    results = data.get("results") if isinstance(data, dict) else None
    if not results:
        return None
    hit = results[0]
    return float(hit["LATITUDE"]), float(hit["LONGITUDE"]), hit.get("SEARCHVAL", postal_code)


def _normalise(name: str) -> str:
    return " ".join(name.lower().split())


def find_machine(points: list[dict[str, Any]], place: str) -> dict[str, Any] | None:
    """The point named `place`, ignoring case and spacing."""
    wanted = _normalise(place)
    return next((p for p in points if _normalise(p.get("place", "")) == wanted), None)


def distance_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Approximate distance in metres (fine at Singapore's scale)."""
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1) * math.cos(math.radians(lat1))
    return 6371000 * math.hypot(dlat, dlng)
