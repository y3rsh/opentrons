import logging
import re
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
        self._pos = {'A': 0, 'B': 0, 'C': 0, 'X': 0, 'Y': 0, 'Z': 0}
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
        self._parser = SmoothieParser(gcodes=list(GCODE))

    def handle(self, line: str) -> Optional[str]:
        """Handle a line"""
        results = (self._handle(c) for c in self._parser.parse(line))
        joined = ' '.join(r for r in results if r)
        return None if not joined else joined

    def _handle(self, command: Command) -> Optional[str]:
        """Handle a command."""
        # TODO (al, 2021-04-28): break this up into multiple functions.
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
            assert 'L' in command.params or 'R' in command.params, "Missing mount"
            self._pipette_id.update(command.params)
        elif GCODE.WRITE_INSTRUMENT_MODEL == command.gcode:
            assert 'L' in command.params or 'R' in command.params, "Missing mount"
            self._pipette_model.update(command.params)
        elif GCODE.MOVE == command.gcode:
            if 'F' in command.params:
                self._speed = command.params.pop('F')
            for axis in command.params.keys():
                self._home_status[axis] = 0
            self._pos.update(command.params)
        elif GCODE.HOME == command.gcode:
            for axis in command.params.keys():
                self._pos[axis] = HOMED_POSITION[axis]
                self._home_status[axis] = 1
        return None


class SmoothieParser(Parser):
    """Override Parser for special handling of some Smoothie gcodes."""

    WRITE_INSTRUMENT_RE = re.compile(r"(?P<mount>[LR])\s*(?P<value>[a-f0-9]+)")

    @staticmethod
    def _build_args(gcode: str, body: str) -> Command:
        """Override to handle irregular gcode params."""
        if gcode == GCODE.WRITE_INSTRUMENT_MODEL or gcode == GCODE.WRITE_INSTRUMENT_ID:
            pars = (i.groupdict() for i in SmoothieParser.WRITE_INSTRUMENT_RE.finditer(body))
            return Command(gcode=gcode, params={p['mount']: p['value'] for p in pars})

        return Parser._build_args(gcode=gcode, body=body)
