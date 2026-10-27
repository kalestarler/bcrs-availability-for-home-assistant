"""Set up a machine by searching for it by name or postal code."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)

from .api import BcrsApiError, async_geocode_postal_code, async_get_all_machines, distance_m
from .const import CONF_PLACE, DOMAIN, MAX_NAME_MATCHES, MAX_NEARBY_MATCHES

CONF_SEARCH = "search"
CONF_MACHINE = "machine"

POSTAL_CODE = re.compile(r"\d{6}")


class BcrsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Search for a machine, then pick it from a list."""

    VERSION = 1

    def __init__(self) -> None:
        self._matches: list[dict[str, Any]] = []
        self._labels: list[str] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            query = user_input[CONF_SEARCH].strip()
            session = async_get_clientsession(self.hass)
            try:
                machines = await async_get_all_machines(session)
                if POSTAL_CODE.fullmatch(query):
                    location = await async_geocode_postal_code(session, query)
                    if location is None:
                        errors[CONF_SEARCH] = "postal_code_not_found"
                    else:
                        lat, lng, _ = location
                        nearby = sorted(
                            ((distance_m(lat, lng, m["lat"], m["long"]), m) for m in machines),
                            key=lambda pair: pair[0],
                        )[:MAX_NEARBY_MATCHES]
                        self._matches = [m for _, m in nearby]
                        self._labels = [f"{m['place']} ({dist:,.0f} m away)" for dist, m in nearby]
                else:
                    words = query.lower().split()
                    found = sorted(
                        (m for m in machines if all(w in m["place"].lower() for w in words)),
                        key=lambda m: m["place"].lower(),
                    )[:MAX_NAME_MATCHES]
                    self._matches = found
                    self._labels = [m["place"] for m in found]
            except BcrsApiError:
                errors["base"] = "cannot_connect"
            if not errors and not self._matches:
                errors[CONF_SEARCH] = "no_match"
            if not errors:
                return await self.async_step_pick()

        schema = vol.Schema({vol.Required(CONF_SEARCH): TextSelector()})
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(schema, user_input),
            errors=errors,
        )

    async def async_step_pick(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            machine = self._matches[int(user_input[CONF_MACHINE])]
            place = machine["place"]
            await self.async_set_unique_id(" ".join(place.lower().split()))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=place,
                data={
                    CONF_PLACE: place,
                    CONF_LATITUDE: machine["lat"],
                    CONF_LONGITUDE: machine["long"],
                },
            )

        options = [SelectOptionDict(value=str(i), label=label) for i, label in enumerate(self._labels)]
        schema = vol.Schema(
            {
                vol.Required(CONF_MACHINE): SelectSelector(
                    SelectSelectorConfig(options=options, mode=SelectSelectorMode.DROPDOWN)
                )
            }
        )
        return self.async_show_form(
            step_id="pick",
            data_schema=schema,
            description_placeholders={"count": str(len(self._matches))},
        )
