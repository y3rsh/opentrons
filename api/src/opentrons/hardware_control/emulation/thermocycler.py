import logging
from typing import Optional, List
from opentrons.drivers.asyncio.thermocycler.driver import GCODE
from opentrons.drivers.types import ThermocyclerLidStatus

from .abstract_emulator import AbstractEmulator

logger = logging.getLogger(__name__)

SERIAL = "fake_serial"
MODEL = "thermocycler_emulator"
VERSION = 1


class ThermocyclerEmulator(AbstractEmulator):
    """Thermocycler emulator"""

    def __init__(self) -> None:
        self.target_temp = 0
        self.current_temp = 0
        self.lid_status = ThermocyclerLidStatus.CLOSED
        self.at_target = None
        self.total_hold_time = None
        self.time_remaining = None

    def handle(self, words: List[str]) -> Optional[str]:  # noqa: C901
        """
        Handle a command.

        TODO: AL 20210218 create dispatch map and remove 'noqa(C901)'
        """
        cmd = words[0]
        logger.info(f"Got command {cmd}")
        if cmd == GCODE.OPEN_LID:
            pass
        elif cmd == GCODE.CLOSE_LID:
            pass
        elif cmd == GCODE.GET_LID_STATUS:
            return f"Lid:{self.lid_status}"
        elif cmd == GCODE.SET_LID_TEMP:
            pass
        elif cmd == GCODE.GET_LID_TEMP:
            return f"T:{self.target_temp} C:{self.current_temp} " \
                   f"H:none Total_H:none At_target?:0"
        elif cmd == GCODE.EDIT_PID_PARAMS:
            pass
        elif cmd == GCODE.SET_PLATE_TEMP:
            pass
        elif cmd == GCODE.GET_PLATE_TEMP:
            return f"T:{self.target_temp} C:{self.current_temp} " \
                   f"H:{self.time_remaining} Total_H:{self.total_hold_time} " \
                   f"At_target?:{self.at_target}"
        elif cmd == GCODE.SET_RAMP_RATE:
            pass
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
