"""Navimow Custom i210 MQTT Stats v1.1.

Hooks into the navimow_custom (andershagenhansen) MQTT pipeline and exposes
mowing-progress sensors that the parent integration ignores.

Parent owns: battery, posture_x, posture_y, posture_theta, device_tracker,
             lawn_mower, button.
This integration owns: mowing_percentage, mowing_week_area, subtotal_area,
                       current_mow_progress, current_mow_boundary,
                       action, sub_action, mow_start_type, vehicle_state,
                       task_delay.

Entities appear under a dedicated sub-device
  "<Device Name> i210 Stats"
linked via_device to the parent Navimow device so they show up grouped
in the HA device page without polluting the parent device entity list.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, PARENT_DOMAIN, SUBDEVICE_SUFFIX
from .coordinator import NavimowI210Coordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up navimow_custom_i210 by piggybacking on navimow_custom."""
    hass.data.setdefault(DOMAIN, {})

    parent_data = hass.data.get(PARENT_DOMAIN)
    if not parent_data:
        raise ConfigEntryNotReady(
            "navimow_custom not loaded yet — "
            "navimow_custom_i210 must start after navimow_custom."
        )

    all_coordinators: dict[str, NavimowI210Coordinator] = {}
    devices_meta: list[dict[str, Any]] = []

    for _entry_id, data in parent_data.items():
        devices = data.get("devices", [])
        parent_coordinators: dict = data.get("coordinators", {})

        for device in devices:
            device_id = device.id
            coord = NavimowI210Coordinator(hass, device_id)
            all_coordinators[device_id] = coord

            devices_meta.append({
                "device": device,
                "coordinator": coord,
            })

            parent_coord = parent_coordinators.get(device_id)
            if parent_coord is not None:
                _patch_parent_coordinator(parent_coord, coord, device_id)
                _LOGGER.info(
                    "navimow_custom_i210 v1.1: hooked device=%s", device_id
                )
            else:
                _LOGGER.warning(
                    "navimow_custom_i210: no parent coordinator for device=%s",
                    device_id,
                )

    if not devices_meta:
        raise ConfigEntryNotReady(
            "No Navimow devices found in navimow_custom. "
            "Ensure navimow_custom is configured and has discovered devices."
        )

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinators": all_coordinators,
        "devices_meta": devices_meta,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


def _patch_parent_coordinator(
    parent_coord: Any,
    i210_coord: NavimowI210Coordinator,
    device_id: str,
) -> None:
    """Wrap parent coordinator's handle_raw_mqtt to forward to i210 coordinator."""
    original = parent_coord.handle_raw_mqtt

    def patched(topic: str, payload: dict[str, Any], did: str) -> None:
        original(topic, payload, did)
        if did == device_id:
            try:
                i210_coord.handle_mqtt_payload(topic, payload)
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug(
                    "navimow_custom_i210: MQTT forward error: %s", err
                )

    parent_coord.handle_raw_mqtt = patched


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload navimow_custom_i210."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
