"""Coordinator for Navimow Custom i210 MQTT Stats — v1.1."""
from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import ACTION_MAP, DOMAIN, SUB_ACTION_MAP, VEHICLE_STATE_MAP

_LOGGER = logging.getLogger(__name__)


class NavimowI210Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that hooks into navimow_custom MQTT and tracks type-2 stats.

    Owned sensors (not duplicating andershagenhansen):
      Type 1: vehicle_state, task_delay
      Type 2: mowing_percentage, mowing_week_area, subtotal_area,
              current_mow_progress, current_mow_boundary,
              action, sub_action, mow_start_type
    """

    def __init__(self, hass: HomeAssistant, device_id: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device_id}",
            update_interval=None,  # push-only, no polling
        )
        self.device_id = device_id
        self.data: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # State restore (called from sensor async_added_to_hass)
    # ------------------------------------------------------------------

    def restore_value(self, key: str, value: Any) -> None:
        """Pre-fill a value restored from HA recorder."""
        if key not in self.data:
            self.data[key] = value
            _LOGGER.debug(
                "navimow_custom_i210: restored %s=%s for device=%s",
                key, value, self.device_id,
            )

    # ------------------------------------------------------------------
    # MQTT handlers
    # ------------------------------------------------------------------

    def handle_mqtt_payload(self, topic: str, payload: dict[str, Any]) -> None:
        """Process raw MQTT payload forwarded from navimow_custom."""
        msg_type = payload.get("type")
        if msg_type == 2:
            self._handle_type2(payload)
        elif msg_type in (1, 4):
            self._handle_type1(payload)

    def _handle_type2(self, payload: dict[str, Any]) -> None:
        """Mowing progress stats (type 2)."""
        updated: dict[str, Any] = {}

        _safe_int(payload, "mowingPercentage", "mowing_percentage", updated)
        _safe_float(payload, "mowingWeekArea", "mowing_week_area", updated)
        _safe_float(payload, "subtotalArea", "subtotal_area", updated)
        _safe_int(payload, "currentMowProgress", "current_mow_progress", updated)
        _safe_int(payload, "currentMowBoundary", "current_mow_boundary", updated)
        _safe_int(payload, "mowStartType", "mow_start_type", updated)

        raw_action = payload.get("action")
        if raw_action is not None:
            try:
                action_int = int(raw_action)
                updated["action"] = ACTION_MAP.get(action_int, str(action_int))
                updated["action_raw"] = action_int
            except (ValueError, TypeError):
                pass

        raw_sub = payload.get("subAction")
        if raw_sub is not None:
            try:
                sub_int = int(raw_sub)
                updated["sub_action"] = SUB_ACTION_MAP.get(sub_int, str(sub_int))
                updated["sub_action_raw"] = sub_int
            except (ValueError, TypeError):
                pass

        self._apply(updated)

    def _handle_type1(self, payload: dict[str, Any]) -> None:
        """Position + vehicleState (type 1 / type 4)."""
        updated: dict[str, Any] = {}

        raw_vs = payload.get("vehicleState")
        if raw_vs is not None:
            try:
                vs_int = int(raw_vs)
                updated["vehicle_state"] = VEHICLE_STATE_MAP.get(vs_int, str(vs_int))
                updated["vehicle_state_raw"] = vs_int
            except (ValueError, TypeError):
                pass

        raw_delay = payload.get("taskDelay")
        if raw_delay is not None:
            updated["task_delay"] = bool(raw_delay)

        self._apply(updated)

    def _apply(self, updated: dict[str, Any]) -> None:
        if updated:
            self.data.update(updated)
            _LOGGER.debug(
                "navimow_custom_i210 update device=%s data=%s",
                self.device_id, json.dumps(updated),
            )
            self.hass.loop.call_soon_threadsafe(self._push_update)

    @callback
    def _push_update(self) -> None:
        self.async_set_updated_data(dict(self.data))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


# ------------------------------------------------------------------
# Private helpers
# ------------------------------------------------------------------

def _safe_int(payload: dict, src: str, dst: str, out: dict) -> None:
    val = payload.get(src)
    if val is not None:
        try:
            out[dst] = int(val)
        except (ValueError, TypeError):
            pass


def _safe_float(payload: dict, src: str, dst: str, out: dict) -> None:
    val = payload.get(src)
    if val is not None:
        try:
            out[dst] = float(val)
        except (ValueError, TypeError):
            pass
