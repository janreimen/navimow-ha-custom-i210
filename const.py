"""Constants for Navimow Custom i210 MQTT Stats integration."""

DOMAIN = "navimow_custom_i210"
VERSION = "1.1.1"

# Parent integration domain (andershagenhansen)
PARENT_DOMAIN = "navimow_custom"

# Sub-device suffix — i210 stats appear as a sub-device of the main Navimow device
SUBDEVICE_SUFFIX = "i210_stats"

# Vehicle state mapping (from MQTT vehicleState int)
VEHICLE_STATE_MAP = {
    0: "idle",
    1: "mowing",
    2: "returning",
    3: "charging",
    4: "mowing",
    5: "paused",
    6: "error",
    7: "offline",
}

# Action mapping (from MQTT action int)
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

# Sub-action mapping (from MQTT subAction int)
SUB_ACTION_MAP = {
    -1: "unknown",
    0: "none",
    1: "leaving_base",
    2: "mowing",
    3: "returning",
    4: "docking",
    5: "charging",
    6: "in_progress",
}

# Sensors already handled by andershagenhansen — never duplicate these
PARENT_OWNED_KEYS = {
    "posture_x",
    "posture_y",
    "posture_theta",
}
