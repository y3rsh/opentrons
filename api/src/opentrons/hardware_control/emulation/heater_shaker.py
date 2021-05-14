from typing import Optional

from opentrons.hardware_control.emulation.parser import Parser, Command
from opentrons.drivers.heater_shaker.constants import GCODE

from .abstract_emulator import AbstractEmulator


class HeaterShakerEmulator(AbstractEmulator):
    def __init__(self, parser: Parser) -> None:
        """Constructor"""
        self._parser = parser
        self._rpm = 0.0
        self._temperature = 0.0
        self._acceleration = 0.0

    def handle(self, line: str) -> Optional[str]:
        """Handle a line"""
        results = (self._handle(c) for c in self._parser.parse(line))
        joined = ' '.join(r for r in results if r)
        return None if not joined else joined

    def _handle(self, command: Command) -> Optional[str]:
        """Handle a command."""
        if command.gcode == GCODE.GET_RPM:
            pass
        elif command.gcode == GCODE.SET_RPM:
            pass
        elif command.gcode == GCODE.GET_TEMPERATURE:
            pass
        elif command.gcode == GCODE.SET_TEMPERATURE:
            pass
        elif command.gcode == GCODE.SET_ACCELERATION:
            pass
        return None



