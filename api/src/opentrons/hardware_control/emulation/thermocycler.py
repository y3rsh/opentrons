import logging
from typing import Optional
from opentrons.drivers.asyncio.thermocycler.driver import GCODE
from opentrons.drivers.types import ThermocyclerLidStatus
from opentrons.hardware_control.emulation.parser import Parser, Command

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
        self._parser = Parser(gcodes=list(GCODE))

    def handle(self, line: str) -> Optional[str]:
        """Handle a line"""
        results = (self._handle(c) for c in self._parser.parse(line))
        joined = ' '.join(r for r in results if r)
        return None if not joined else joined

    def _handle(self, command: Command) -> Optional[str]:  # noqa: C901
        """
        Handle a command.

        TODO: AL 20210218 create dispatch map and remove 'noqa(C901)'
        """
        logger.info(f"Got command {command}")
        if command.gcode == GCODE.OPEN_LID:
            self.lid_status = ThermocyclerLidStatus.OPEN
        elif command.gcode == GCODE.CLOSE_LID:
            self.lid_status = ThermocyclerLidStatus.CLOSED
        elif command.gcode == GCODE.GET_LID_STATUS:
            return f"Lid:{self.lid_status}"
        elif command.gcode == GCODE.SET_LID_TEMP:
            self.lid_target_temp.val = command.params['S']
            self.lid_current_temp = self.lid_target_temp.val
        elif command.gcode == GCODE.GET_LID_TEMP:
            return f"T:{self.lid_target_temp} C:{self.lid_current_temp} " \
                   f"H:none Total_H:none At_target?:0"
        elif command.gcode == GCODE.EDIT_PID_PARAMS:
            pass
        elif command.gcode == GCODE.SET_PLATE_TEMP:
            for prefix, value in command.params.items():
                if prefix == 'S':
                    self.plate_target_temp.val = value
                    self.plate_current_temp = self.plate_target_temp.val
                elif prefix == 'V':
                    self.plate_volume.val = value
                elif prefix == 'H':
                    self.plate_total_hold_time.val = value
                    self.plate_time_remaining.val = value
        elif command.gcode == GCODE.GET_PLATE_TEMP:
            return f"T:{self.plate_target_temp} " \
                   f"C:{self.plate_current_temp} " \
                   f"H:{self.plate_time_remaining} " \
                   f"Total_H:{self.plate_total_hold_time} " \
                   f"At_target?:{self.plate_at_target}"
        elif command.gcode == GCODE.SET_RAMP_RATE:
            self.plate_ramp_rate.val = command.params['S']
        elif command.gcode == GCODE.DEACTIVATE_ALL:
            pass
        elif command.gcode == GCODE.DEACTIVATE_LID:
            pass
        elif command.gcode == GCODE.DEACTIVATE_BLOCK:
            pass
        elif command.gcode == GCODE.DEVICE_INFO:
            return f"serial:{SERIAL} model:{MODEL} version:{VERSION}"
        return None

    @staticmethod
    def get_terminator() -> bytes:
        return b'\r\n'
