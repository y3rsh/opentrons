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
        self._pos = {
            'X': 0,
            'Y': 0,
            'Z': 0,
            'A': 0,
            'B': 0,
            'C': 0,
        }
        self._home_status = {
            'X': 0,
            'Y': 0,
            'Z': 0,
            'A': 0,
            'B': 0,
            'C': 0,
        }
        self._speed = 0
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
            vals = " ".join(f"{k}:{v}" for k, v in self._pos.items())
            return vals
        elif GCODE.CURRENT_POSITION == command.gcode:
            vals = " ".join(f"{k}:{v}" for k, v in self._pos.items())
            return f"{command.gcode}\r\n\r\nok MCS: {vals}"
        elif GCODE.VERSION == command.gcode:
            return v
        elif GCODE.READ_INSTRUMENT_ID == command.gcode:
            if "L" in command.params:
                # P3HMV202020041605
                return "L:5033484D56323032303230303431363035000000000000000000000000000000"
            elif "R" in command.params:
                # P20SV202020070101
                return "R:5032305356323032303230303730313031000000000000000000000000000000"
        elif GCODE.READ_INSTRUMENT_MODEL == command.gcode:
            if "L" in command.params:
                # p20_multi_v2.0
                return "L:7032305F6D756C74695F76322E30000000000000000000000000000000000000"
            elif "R" in command.params:
                # p20_single_v2.0
                return "R:7032305F73696E676C655F76322E300000000000000000000000000000000000"
        elif GCODE.MOVE == command.gcode:
            if 'F' in command.params:
                self._speed = command.params.pop('F')
            for axis in command.params.keys():
                self._home_status[axis] = 0
            self._pos.update(command.params)
        elif GCODE.HOME == command.gcode:
            for axis in command.params.keys():
                self._home_status[axis] = 1
        return None

