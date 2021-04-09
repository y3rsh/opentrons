import logging
from typing import Optional, List
from opentrons.drivers.asyncio.magdeck.driver import GCODE
from .abstract_emulator import AbstractEmulator
from . import util

logger = logging.getLogger(__name__)


SERIAL = "fake_serial"
MODEL = "magdeck_emulator"
VERSION = 1


class MagDeckEmulator(AbstractEmulator):
    """Magdeck emulator"""

    def __init__(self) -> None:
        self.height: float = 0
        self.position: float = 0

    def handle(self, words: List[str]) -> Optional[str]:
        """Handle a command."""
        cmd = words[0]
        logger.info(f"Got command {cmd}")
        if cmd == GCODE.HOME:
            self.height = 0
        elif cmd == GCODE.MOVE:
            par = util.parse_parameter(words[1])
            assert par.prefix == 'Z'
            self.position = par.value
        elif cmd == GCODE.PROBE_PLATE:
            self.height = 45
        elif cmd == GCODE.GET_PLATE_HEIGHT:
            return f"height:{self.height}"
        elif cmd == GCODE.GET_CURRENT_POSITION:
            return f"Z:{self.position}"
        elif cmd == GCODE.DEVICE_INFO:
            return f"serial:{SERIAL} model:{MODEL} version:{VERSION}"
        elif cmd == GCODE.PROGRAMMING_MODE:
            pass
        return None
