import logging
from typing import Optional, List
from opentrons.drivers.asyncio.thermocycler.driver import GCODE
from opentrons.drivers.types import ThermocyclerLidStatus

from .abstract_emulator import AbstractEmulator
from . import util

logger = logging.getLogger(__name__)

SERIAL = "fake_serial"
MODEL = "thermocycler_emulator"
VERSION = 1


class ThermocyclerEmulator(AbstractEmulator):
    """Thermocycler emulator"""

    def __init__(self) -> None:
        self.lid_target_temp = util.OptionalValue[float]()
        self.lid_current_temp: float = util.TEMPERATURE_ROOM
        self.lid_status = ThermocyclerLidStatus.CLOSED
        self.lid_at_target: Optional[bool] = None
        self.plate_total_hold_time = util.OptionalValue[float]()
        self.plate_time_remaining = util.OptionalValue[float]()
        self.plate_target_temp = util.OptionalValue[float]()
        self.plate_current_temp: float = util.TEMPERATURE_ROOM
        self.plate_volume = util.OptionalValue[float]()
        self.plate_at_target = util.OptionalValue[float]()
        self.plate_ramp_rate = util.OptionalValue[float]()

    def handle(self, words: List[str]) -> Optional[str]:  # noqa: C901
        """
        Handle a command.

        TODO: AL 20210218 create dispatch map and remove 'noqa(C901)'
        """
        cmd = words[0]
        logger.info(f"Got command {cmd}")
        if cmd == GCODE.OPEN_LID:
            self.lid_status = ThermocyclerLidStatus.OPEN
        elif cmd == GCODE.CLOSE_LID:
            self.lid_status = ThermocyclerLidStatus.CLOSED
        elif cmd == GCODE.GET_LID_STATUS:
            return f"Lid:{self.lid_status}"
        elif cmd == GCODE.SET_LID_TEMP:
            par = util.parse_parameter(words[1])
            assert par.prefix == "S"
            self.lid_target_temp.val = par.value
            self.lid_current_temp = self.lid_target_temp.val
        elif cmd == GCODE.GET_LID_TEMP:
            return f"T:{self.lid_target_temp} C:{self.lid_current_temp} " \
                   f"H:none Total_H:none At_target?:0"
        elif cmd == GCODE.EDIT_PID_PARAMS:
            pass
        elif cmd == GCODE.SET_PLATE_TEMP:
            pars = (util.parse_parameter(p) for p in words[1:])
            for par in pars:
                if par.prefix == 'S':
                    self.plate_target_temp.val = par.value
                    self.plate_current_temp = self.plate_target_temp.val
                elif par.prefix == 'V':
                    self.plate_volume.val = par.value
                elif par.prefix == 'H':
                    self.plate_total_hold_time.val = par.value
                    self.plate_time_remaining.val = par.value
        elif cmd == GCODE.GET_PLATE_TEMP:
            return f"T:{self.plate_target_temp} " \
                   f"C:{self.plate_current_temp} " \
                   f"H:{self.plate_time_remaining} " \
                   f"Total_H:{self.plate_total_hold_time} " \
                   f"At_target?:{self.plate_at_target}"
        elif cmd == GCODE.SET_RAMP_RATE:
            par = util.parse_parameter(words[1])
            assert par.prefix == "S"
            self.plate_ramp_rate.val = par.value
        elif cmd == GCODE.DEACTIVATE_ALL:
            pass
        elif cmd == GCODE.DEACTIVATE_LID:
            pass
        elif cmd == GCODE.DEACTIVATE_BLOCK:
            pass
        elif cmd == GCODE.DEVICE_INFO:
            return f"serial:{SERIAL} model:{MODEL} version:{VERSION}"
        return None

    @staticmethod
    def get_terminator() -> bytes:
        return b'\r\n'
