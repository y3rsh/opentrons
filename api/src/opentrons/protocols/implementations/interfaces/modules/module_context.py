from abc import abstractmethod, ABC
from typing import Optional

from opentrons.protocols.geometry.module_geometry import ModuleGeometry
from opentrons.protocols.implementations.interfaces.labware import \
    LabwareInterface


class ModuleContextInterface(ABC):

    @abstractmethod
    def load_labware_object(
            self,
            labware: LabwareInterface) -> LabwareInterface:
        ...

    @abstractmethod
    def load_labware(
            self,
            name: str,
            label: Optional[str] = None,
            namespace: Optional[str] = None,
            version: int = 1) -> LabwareInterface:
        ...

    @abstractmethod
    def get_geometry(self) -> ModuleGeometry:
        ...
