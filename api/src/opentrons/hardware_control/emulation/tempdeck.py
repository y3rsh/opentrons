import logging
from typing import Optional, List

from opentrons.drivers.asyncio.tempdeck.driver import GCODE

from .abstract_emulator import AbstractEmulator

logger = logging.getLogger(__name__)

SERIAL = "fake_serial"
MODEL = "temp_emulator"
VERSION = 1


class TempDeckEmulator(AbstractEmulator):
    """TempDeck emulator"""

    def __init__(self) -> None:
        self.target_temp = 0.0
        self.current_temp = 0.0

    def handle(self, words: List[str]) -> Optional[str]:
        """Handle a command."""
        cmd = words[0]
        logger.info(f"Got command {cmd}")
        if cmd == GCODE.GET_TEMP:
            return f"T:{self.target_temp} C:{self.current_temp}"
        elif cmd == GCODE.SET_TEMP:
            assert words[1][0] == 'S'
            self._set_target(float(words[1][1:]))
            pass
        elif cmd == GCODE.DISENGAGE:
            self._set_target(23)
            pass
        elif cmd == GCODE.DEVICE_INFO:
            return f"serial:{SERIAL} model:{MODEL} version:{VERSION}"
        elif cmd == GCODE.PROGRAMMING_MODE:
            pass
        return None

    def _set_target(self, target_temp: float) -> None:
        self.target_temp = target_temp
        self.current_temp = self.target_temp
