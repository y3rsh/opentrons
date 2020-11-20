from abc import ABC
from typing import Optional

from opentrons.protocols.geometry.module_geometry import ModuleGeometry
from opentrons.protocols.implementations.interfaces.labware import \
    LabwareInterface
from opentrons.protocols.implementations.interfaces.modules.module_context \
    import ModuleContextInterface
from opentrons.protocols.implementations.interfaces.protocol_context import \
    ProtocolContextInterface


class ModuleBase(ModuleContextInterface):
    def __init__(
            self,
            protocol_context: ProtocolContextInterface,
            geometry: ModuleGeometry):
        """
        Constructor

        :param protocol_context: The protocol context implementation.
        :param geometry: Module geometry
        """
        self._protocol_context = protocol_context
        self._geometry = geometry

    def load_labware_object(
            self,
            labware: LabwareInterface) -> LabwareInterface:
        """Specify the presence of labware on the module."""
        mod_labware = self._geometry.add_labware(labware=labware)
        self._protocol_context.get_deck().recalculate_high_z()
        return mod_labware

    def load_labware(
            self,
            name: str,
            label: Optional[str] = None,
            namespace: Optional[str] = None,
            version: int = 1) -> LabwareInterface:
        """Load and specify the presence of labware on the module."""
        return self._protocol_context.load_labware(
            load_name=name,
            location=str(self._geometry.location.labware),
            namespace=namespace,
            version=version
        )

    def get_geometry(self) -> ModuleGeometry:
        """Get the module geometry"""
        return self._geometry
