import logging
from typing import Optional

from opentrons.drivers.smoothie_drivers import HOMED_POSITION
from opentrons.drivers.smoothie_drivers.driver_3_0 import GCODE
from opentrons.hardware_control.emulation.parser import Command, Parser

from .abstract_emulator import AbstractEmulator

logger = logging.getLogger(__name__)

v = """Build version: EMULATOR, Build date: CURRENT, MCU: NONE, System Clock: NONE"""


class SmoothieEmulator(AbstractEmulator):
    """Smoothie emulator"""

    def __init__(self) -> None:
        self._pos = HOMED_POSITION.copy()
        self._home_status = {
            'X': 0,
            'Y': 0,
            'Z': 0,
            'A': 0,
            'B': 0,
            'C': 0,
        }
        self._speed = 0
        self._pipette_model = {
            # p20_multi_v2.0
            "L": "7032305F6D756C74695F76322E30000000000000000000000000000000000000",
            # p20_single_v2.0
            "R": "7032305F73696E676C655F76322E300000000000000000000000000000000000"
        }
        self._pipette_id = {
            # P3HMV202020041605
            "L": "5033484D56323032303230303431363035000000000000000000000000000000",
            # P20SV202020070101
            "R": "5032305356323032303230303730313031000000000000000000000000000000"
        }
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
            vals = " ".join(f"{k}:{v}" for k, v in self._home_status.items())
            return vals
        elif GCODE.CURRENT_POSITION == command.gcode:
            vals = " ".join(f"{k}:{v}" for k, v in self._pos.items())
            return f"{command.gcode}\r\n\r\nok MCS: {vals}"
        elif GCODE.VERSION == command.gcode:
            return v
        elif GCODE.READ_INSTRUMENT_ID == command.gcode:
            if "L" in command.params:
                return f"L:{self._pipette_id['L']}"
            elif "R" in command.params:
                return f"R:{self._pipette_id['R']}"
        elif GCODE.READ_INSTRUMENT_MODEL == command.gcode:
            if "L" in command.params:
                return f"L:{self._pipette_model['L']}"
            elif "R" in command.params:
                return f"R:{self._pipette_model['R']}"
        elif GCODE.WRITE_INSTRUMENT_ID == command.gcode:
            pass
            # print("AM", command.params)
            # t = sorted(command.params.keys(), key=lambda x: len(x))
            # self._pipette_id.update({t[0]: t[1]})
        elif GCODE.WRITE_INSTRUMENT_MODEL == command.gcode:
            pass
            # print("AAM", command.params)
            # t = sorted(command.params.keys(), key=lambda x: len(x))
            # self._pipette_model.update({t[0]: t[1]})
        elif GCODE.MOVE == command.gcode:
            if 'F' in command.params:
                self._speed = command.params.pop('F')
            for axis in command.params.keys():
                self._home_status[axis] = 0
            self._pos.update(command.params)
        elif GCODE.HOME == command.gcode:
            self._pos = HOMED_POSITION.copy()
            for axis in command.params.keys():
                self._home_status[axis] = 1
        return None

