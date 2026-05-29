"""Sensor platform for Navimow Custom i210 MQTT Stats — v1.1.

All sensors appear under a dedicated sub-device linked via_device to the
parent Navimow device. Sensors already owned by andershagenhansen's
navimow_custom (battery, posture_x/y/theta) are never created here.
Last known values are restored from the HA recorder on startup via
RestoreEntity so sensors never show 'unknown' after a reboot.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfArea
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PARENT_DOMAIN, SUBDEVICE_SUFFIX
from .coordinator import NavimowI210Coordinator


@dataclass(frozen=True, kw_only=True)
class NavimowI210SensorDescription(SensorEntityDescription):
    """Describes a Navimow i210 sensor."""
    value_fn: Callable[[NavimowI210Coordinator], Any]
    is_numeric: bool = True  # False for string/enum sensors


# -----------------------------------------------------------------------
# Sensor definitions
# NEVER add: battery, posture_x, posture_y, posture_theta
# Those are owned by andershagenhansen/navimow_custom
# -----------------------------------------------------------------------
SENSOR_DESCRIPTIONS: tuple[NavimowI210SensorDescription, ...] = (

    # ---- Mowing progress (type 2) ------------------------------------

    # ---- Dedicated battery sensor -------------------------------
    NavimowI210SensorDescription(
        key="battery_i210",
        name="Battery i210",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY,
        icon="mdi:battery",
        is_numeric=True,
        value_fn=lambda c: c.get("battery_i210"),
    ),

    NavimowI210SensorDescription(
        key="mowing_percentage",
        name="Mowing Percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:percent",
        is_numeric=True,
        value_fn=lambda c: c.get("mowing_percentage"),
    ),
    NavimowI210SensorDescription(
        key="mowing_week_area",
        name="Mowing Week Area",
        native_unit_of_measurement=UnitOfArea.SQUARE_METERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:grass",
        is_numeric=True,
        value_fn=lambda c: c.get("mowing_week_area"),
    ),
    NavimowI210SensorDescription(
        key="subtotal_area",
        name="Session Area",
        native_unit_of_measurement=UnitOfArea.SQUARE_METERS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:grid",
        is_numeric=True,
        value_fn=lambda c: c.get("subtotal_area"),
    ),
    NavimowI210SensorDescription(
        key="current_mow_progress",
        name="Mow Progress (strips)",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:counter",
        is_numeric=True,
        value_fn=lambda c: c.get("current_mow_progress"),
    ),
    NavimowI210SensorDescription(
        key="current_mow_boundary",
        name="Mow Boundary",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:vector-square",
        is_numeric=True,
        value_fn=lambda c: c.get("current_mow_boundary"),
    ),

    # ---- Action / state (type 2) ------------------------------------
    NavimowI210SensorDescription(
        key="action",
        name="Action",
        icon="mdi:robot-mower",
        is_numeric=False,
        value_fn=lambda c: c.get("action"),
    ),
    NavimowI210SensorDescription(
        key="sub_action",
        name="Sub Action",
        icon="mdi:robot-mower-outline",
        is_numeric=False,
        value_fn=lambda c: c.get("sub_action"),
    ),
    NavimowI210SensorDescription(
        key="mow_start_type",
        name="Mow Start Type",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:play-circle-outline",
        is_numeric=True,
        value_fn=lambda c: c.get("mow_start_type"),
    ),

    # ---- Vehicle state (type 1) ------------------------------------
    NavimowI210SensorDescription(
        key="vehicle_state",
        name="Vehicle State",
        icon="mdi:state-machine",
        is_numeric=False,
        value_fn=lambda c: c.get("vehicle_state"),
    ),
    NavimowI210SensorDescription(
        key="task_delay",
        name="Task Delay",
        icon="mdi:timer-sand",
        is_numeric=False,
        value_fn=lambda c: c.get("task_delay"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Navimow i210 sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    devices_meta: list[dict] = data["devices_meta"]

    entities: list[NavimowI210Sensor] = []
    for meta in devices_meta:
        device = meta["device"]
        coordinator: NavimowI210Coordinator = meta["coordinator"]
        for description in SENSOR_DESCRIPTIONS:
            entities.append(
                NavimowI210Sensor(
                    coordinator=coordinator,
                    description=description,
                    device=device,
                )
            )

    async_add_entities(entities)


class NavimowI210Sensor(
    CoordinatorEntity[NavimowI210Coordinator],
    RestoreEntity,
    SensorEntity,
):
    """A Navimow i210 MQTT stats sensor.

    - Attached to a sub-device linked via_device to the parent Navimow device.
    - Restores last known value from HA recorder on startup.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NavimowI210Coordinator,
        description: NavimowI210SensorDescription,
        device: Any,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._description = description
        self._device = device

        self._attr_unique_id = (
            f"{DOMAIN}_{device.id}_{description.key}"
        )
        self._attr_name = description.name

        # Sub-device: "<Device Name> i210 Stats"
        # Linked to the parent device via via_device so it groups correctly
        # in the HA UI without sharing the parent entity list.
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{device.id}_{SUBDEVICE_SUFFIX}")},
            name=f"{device.name} i210 Stats",
            manufacturer="Navimow / janreimen",
            model="i210 MQTT Stats v1.1.2",
            via_device=(PARENT_DOMAIN, device.id),
        )

    # ------------------------------------------------------------------
    # Restore last known state from HA recorder on startup
    # ------------------------------------------------------------------

    async def async_added_to_hass(self) -> None:
        """Called when entity is added — restore last state from DB."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is None:
            return
        if last_state.state in ("unknown", "unavailable", "None", "none"):
            return

        key = self._description.key
        if self._description.is_numeric:
            try:
                self.coordinator.restore_value(key, float(last_state.state))
            except ValueError:
                pass
        else:
            self.coordinator.restore_value(key, last_state.state)

        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    @property
    def native_value(self) -> Any:
        return self._description.value_fn(self.coordinator)

    @property
    def available(self) -> bool:
        # Available once at least one MQTT message has arrived
        # OR we have a restored value from DB
        return bool(self.coordinator.data)
