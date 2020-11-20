from typing import Optional

from opentrons.hardware_control.modules import MagDeck
from opentrons.protocols.geometry.module_geometry import ModuleGeometry
from opentrons.protocols.implementations.interfaces.modules.magnetic_module_context import \
    MagneticModuleContextInterface
from opentrons.protocols.implementations.interfaces.protocol_context import \
    ProtocolContextInterface
from opentrons.protocols.implementations.modules.module_context import \
    ModuleBase


class MageneticModuleContextImplementation(ModuleBase, MagneticModuleContextInterface):

    def __init__(
            self,
            protocol_context: ProtocolContextInterface,
            hw_module: MagDeck,
            geometry: ModuleGeometry):
        super().__init__(protocol_context, geometry)
        self._module = hw_module

    def calibrate(self) -> None:
        self._module.calibrate()

    def engage(self, height: float) -> None:
        self._module.engage(height)

    def disengage(self) -> None:
        self._module.deactivate()

    def get_status(self) -> str:
        return self._module.status
