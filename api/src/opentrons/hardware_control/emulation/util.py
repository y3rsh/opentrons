import re
import dataclasses
from typing import Optional, Generic, TypeVar

TEMPERATURE_ROOM = 23

PREFIX_NUMBER_RE = re.compile(r"(?P<prefix>[A-Z])(?P<value>-*\d+\.?\d*)")


ValueType = TypeVar('ValueType')


class OptionalValue(Generic[ValueType]):
    _value: Optional[ValueType]

    def __init__(self, value: Optional[ValueType] = None):
        self._value = value

    @property
    def val(self) -> Optional[ValueType]:
        return self._value

    @val.setter
    def val(self, value: Optional[ValueType]) -> None:
        self._value = value

    def __repr__(self) -> str:
        return "none" if self._value is None else str(self._value)


@dataclasses.dataclass
class Parameter:
    prefix: str
    value: float


def parse_parameter(par: str) -> Parameter:
    """
    Parse a parameter: a one letter prefix followed by a numerical value

    Args:
        par: A string like F1234 or B-123.221

    Returns:
        A Parameter or raises an error
    """
    m = PREFIX_NUMBER_RE.match(par)
    assert m, f"Not a valid parameter {par}"
    p = m.groupdict()
    return Parameter(
        prefix=p['prefix'],
        value=float(p['value'])
    )
