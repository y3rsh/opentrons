"""Base protocol engine types and interfaces."""
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Union, Tuple
from typing_extensions import final

from opentrons.types import DeckSlotName


class DeckSlotLocation(BaseModel):
    """Location for labware placed in a single slot."""

    slot: DeckSlotName


LabwareLocation = Union[DeckSlotLocation]
"""Union of all legal labware locations."""


@final
class WellOrigin(str, Enum):
    """Origin of WellLocation offset."""

    TOP = "top"
    BOTTOM = "bottom"


class WellLocation(BaseModel):
    """A relative location in reference to a well's location."""

    # todo(mm, 2021-03-24): How is this interpreted for 8-Channel pipettes?
    # Offset relative to the back-most targeted well? Offset relative to all
    # targeted wells at once? If you have an 8-Channel and are targeting a
    # column of wells that aren't exactly 9 mm apart, the offset would be
    # different for each well.

    origin: WellOrigin = WellOrigin.TOP
    offset: Tuple[float, float, float] = (0, 0, 0)


class DeckLocation(BaseModel):
    """A symbolic reference to a location on the deck.

    Specified as the pipette, labware, and well. A `DeckLocation` may be
    combined with a `WellLocation` to produce an absolute position in deck
    coordinates.
    """

    pipette_id: str
    labware_id: str
    well_name: str


@final
@dataclass(frozen=True)
class Dimensions:
    """Dimensions of an object in deck-space."""

    x: float
    y: float
    z: float
