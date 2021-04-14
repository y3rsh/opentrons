import logging
from typing import Optional

from opentrons.drivers.smoothie_drivers.driver_3_0 import GCODE
from opentrons.hardware_control.emulation.parser import Command, Parser

from .abstract_emulator import AbstractEmulator

logger = logging.getLogger(__name__)

v = """Build version: EMULATOR, Build date: CURRENT, MCU: NONE, System Clock: NONE"""


class SmoothieEmulator(AbstractEmulator):
    """Smoothie emulator"""

    def __init__(self) -> None:
        self.x = self.y = self.z = self.a = self.b = self.c = 0.00
        self._parser = Parser(gcodes=list(GCODE))

    def handle(self, line: str) -> Optional[str]:
        """Handle a line"""
        results = (self._handle(c) for c in self._parser.parse(line))
        joined = ' '.join(r for r in results if r)
        return None if not joined else joined

    def _handle(self, command: Command) -> Optional[str]:
        """Handle a command."""
        logger.info(f"Got command {command}")
        if GCODE.HOMING_STATUS == command.gcode:
            return "X:0 Y:0 Z:0 A:0 B:0 C:0"
        elif GCODE.CURRENT_POSITION == command.gcode:
            return f"{command.gcode}\r\n\r\nok MCS: X:{self.x} Y:{self.y} " \
                   f"Z:{self.z} A:{self.a} B:{self.b} C:{self.c}"
        elif GCODE.VERSION == command.gcode:
            return v
        return None
