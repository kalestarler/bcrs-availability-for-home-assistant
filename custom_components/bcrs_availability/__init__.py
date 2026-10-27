"""BCRS Availability: live status of Singapore BCRS return machines."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import BcrsConfigEntry, BcrsCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: BcrsConfigEntry) -> bool:
    """Set up one machine."""
    coordinator = BcrsCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BcrsConfigEntry) -> bool:
    """Unload one machine."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
