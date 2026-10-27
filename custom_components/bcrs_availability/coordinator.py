"""Polls recycle.gov.sg for one machine."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BcrsApiError, async_get_machines_near, find_machine
from .const import CONF_PLACE, DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

type BcrsConfigEntry = ConfigEntry[BcrsCoordinator]


class BcrsCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches the latest data for the configured machine."""

    config_entry: BcrsConfigEntry

    def __init__(self, hass: HomeAssistant, entry: BcrsConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} {entry.data[CONF_PLACE]}",
            update_interval=SCAN_INTERVAL,
        )
        self.place: str = entry.data[CONF_PLACE]
        self._lat: float = entry.data[CONF_LATITUDE]
        self._lng: float = entry.data[CONF_LONGITUDE]

    async def _async_update_data(self) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)
        try:
            points = await async_get_machines_near(session, self._lat, self._lng)
        except BcrsApiError as err:
            raise UpdateFailed(f"Couldn't reach recycle.gov.sg: {err}") from err
        point = find_machine(points, self.place)
        if point is None:
            raise UpdateFailed(
                f"{self.place} is no longer listed at its saved location on recycle.gov.sg. "
                "It may have been renamed or removed. Delete it and add it again."
            )
        return point
