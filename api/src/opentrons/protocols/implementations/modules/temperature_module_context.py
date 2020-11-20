from opentrons.hardware_control.modules import TempDeck
from opentrons.protocols.geometry.module_geometry import ModuleGeometry
from opentrons.protocols.implementations.interfaces.modules.temperature_module_context import \
    TemperatureModuleContextInterface
from opentrons.protocols.implementations.interfaces.protocol_context import \
    ProtocolContextInterface
from opentrons.protocols.implementations.modules.module_context import \
    ModuleBase


class TemperatureModuleContextImplementation(ModuleBase, TemperatureModuleContextInterface):

    def __init__(
            self,
            protocol_context: ProtocolContextInterface,
            hw_module: TempDeck,
            geometry: ModuleGeometry):
        super().__init__(protocol_context, geometry)
        self._module = hw_module

    def set_temperature(self, celsius: float) -> None:
        self._module.set_temperature(celsius)

    def start_set_temperature(self, celsius: float) -> None:
        self._module.start_set_temperature(celsius)

    def await_temperature(self, celsius: float) -> None:
        self._module.await_temperature(celsius)

    def deactivate(self) -> None:
        self._module.deactivate()

    def get_temperature(self) -> float:
        return self._module.temperature

    def get_target_temperature(self) -> float:
        return self._module.target

    def get_status(self) -> str:
        return self._module.status

