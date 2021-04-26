import pytest
from opentrons.drivers.asyncio.smoothie import parse_utils
from opentrons.drivers.utils import ParseError


def test_parse_position_response(smoothie):
    good_data = 'ok M114.2 X:10 Y:20 Z:30 A:40 B:50 C:60'
    bad_data = 'ok M114.2 X:10 Y:20: Z:30A:40 B:50 C:60'
    res = parse_utils._parse_position_response(good_data)
    expected = {
        'X': 10,
        'Y': 20,
        'Z': 30,
        'A': 40,
        'B': 50,
        'C': 60,
    }
    assert res == expected
    with pytest.raises(ParseError):
        parse_utils._parse_position_response(bad_data)

