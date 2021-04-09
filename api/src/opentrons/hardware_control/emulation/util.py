import re
import dataclasses


TEMPERATURE_ROOM = 23

PREFIX_NUMBER_RE = re.compile(r"(?P<prefix>[A-Z])(?P<value>-*\d+\.?\d*)")


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
