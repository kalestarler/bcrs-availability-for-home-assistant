"""Status and opening hours sensors for a BCRS machine."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import BcrsConfigEntry, BcrsCoordinator
from .status import STATUSES, hours_today, machine_status

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BcrsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the sensors for one machine."""
    coordinator = entry.runtime_data
    async_add_entities([BcrsStatusSensor(coordinator), BcrsHoursTodaySensor(coordinator)])


class BcrsEntity(CoordinatorEntity[BcrsCoordinator]):
    """Shared device info for a machine's entities."""

    _attr_has_entity_name = True
    _attr_attribution = "Data from recycle.gov.sg"

    def __init__(self, coordinator: BcrsCoordinator, key: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.unique_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            name=coordinator.place,
            manufacturer="BCRS",
            model="Return point",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.recycle.gov.sg/materials/beverage",
        )


class BcrsStatusSensor(BcrsEntity, SensorEntity):
    """Available, full, closed and so on."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = STATUSES

    def __init__(self, coordinator: BcrsCoordinator) -> None:
        super().__init__(coordinator, "status")

    @property
    def native_value(self) -> str:
        return machine_status(self.coordinator.data, dt_util.utcnow())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        hours = data.get("openingHours") or {}
        return {
            "machine_status": data.get("machineStatus"),
            "opening_hours": "Open 24 hours" if hours.get("alwaysOpen") else hours.get("weekdayText"),
            "remarks": data.get("remarks"),
        }


class BcrsHoursTodaySensor(BcrsEntity, SensorEntity):
    """Today's opening hours, e.g. "10 am - 10 pm"."""

    def __init__(self, coordinator: BcrsCoordinator) -> None:
        super().__init__(coordinator, "hours_today")

    @property
    def native_value(self) -> str:
        return hours_today(self.coordinator.data, dt_util.utcnow()) or "Not listed"
