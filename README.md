
Changelog

v1.1.2

Added

- Added dedicated "battery_i210" sensor to avoid conflicts with other Navimow Home Assistant integrations
- Added "ACTION_MAP[-1] = "unknown"" fallback for unsupported or missing mower action states
- Added migration stub for future Home Assistant config entry migrations

Changed

- Increased supported mowing height limit from "60mm" to "70mm"
- Updated integration version references to "1.1.2"
- Improved compatibility with multiple MQTT payload formats:
  - "battery"
  - "batteryLevel"

Fixed

- Prevented entity collisions with:
  - andershagenhansen/navimow_custom
- Improved handling of undefined mower states during startup or MQTT reconnects

Notes

After upgrading:

1. Reload the integration or restart Home Assistant
2. Verify the new battery entity appears:
   - "sensor.navimow_battery_i210"
3. Confirm mowing height values above "60mm" are accepted by your mower firmware

Known limitations

- Some mower firmware versions may still reject values above "60mm"
- MQTT/API-side restrictions may still apply depending on Navimow firmware version

v1.1.1

Added

- Added dedicated "battery_i210" sensor
- Added fallback action state:
  - "-1 = "unknown""

Changed

- Updated integration version to "1.1.1"
- Updated internal device model string to:
  - "i210 MQTT Stats v1.1.1"
- Added support for multiple MQTT battery payload formats:
  - "battery"
  - "batteryLevel"

Fixed

- Prevented battery sensor conflicts with:
  - andershagenhansen/navimow_custom
- Improved handling of undefined mower action states
- Reduced risk of "KeyError" or invalid HA states during startup/reconnect situations

Technical changes

Added to "const.py":

ACTION_MAP = {
    -1: "unknown",
    0: "none",
    1: "start",
    2: "pause",
    3: "resume",
    4: "return_to_base",
    5: "charging",
    6: "scheduled",
    7: "manual",
    8: "mowing",
}

Notes

After upgrading:

1. Reload the integration or restart Home Assistant
2. Verify the new battery entity exists:
   - "sensor.navimow_battery_i210"
3. Existing integrations should continue to work without conflicts

v1.1.0

Extension Plugin for Segway Navimow i210 LIDAR, needs the andershagenhansen Plugin (https://github.com/andershagenhansen/navimow-ha-custom) installed.

No future Auth required, extends the good work of https://github.com/andershagenhansen
