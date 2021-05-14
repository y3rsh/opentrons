from enum import Enum


class GCODE(str, Enum):
    """Heater shaker GCODE."""
    SET_RPM = "M3"
    GET_RPM = "M123"
    SET_TEMPERATURE = "M104"
    GET_TEMPERATURE = "M105"
    SET_ACCELERATION = "M204"
