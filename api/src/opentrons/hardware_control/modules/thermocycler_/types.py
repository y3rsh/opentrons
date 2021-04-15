from enum import Enum


class TemperatureStatus(str, Enum):
    HOLDING = 'holding at target'
    COOLING = 'cooling'
    HEATING = 'heating'
    IDLE = 'idle'
    ERROR = 'error'
