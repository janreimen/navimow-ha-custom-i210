"""Config flow for Navimow Custom i210 MQTT Stats — v1.1."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN, VERSION


class NavimowI210ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Single-step config flow — no credentials needed.

    Piggybacks entirely on navimow_custom's OAuth2 + MQTT connection.
    """

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="Navimow i210 MQTT Stats",
                data={},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={
                "version": VERSION,
                "info": (
                    "Adds mowing progress sensors (percentage, area, action, "
                    "vehicle state) by subscribing to the same MQTT stream as "
                    "navimow_custom. No credentials required. "
                    "Sensors appear under a dedicated sub-device linked to "
                    "your Navimow device."
                ),
            },
        )
