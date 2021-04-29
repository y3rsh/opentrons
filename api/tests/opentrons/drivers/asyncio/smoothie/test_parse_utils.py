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


def test_parse_pipette_data():
    msg = 'TestsRule!!'
    mount = 'L'
    good_data = mount + ': ' + parse_utils._byte_array_to_hex_string(msg.encode())
    parsed = parse_utils._parse_instrument_data(
        good_data).get(mount)
    assert parsed.decode() == msg


def test_read_pipette_v13(smoothie, monkeypatch):
    driver = smoothie
    driver.simulating = False

    def _new_send_message(
            command, timeout=None, suppress_error_msg=True):
        return 'L:' + parse_utils._byte_array_to_hex_string(
            b'p300_single_v13')

    monkeypatch.setattr(driver, '_send_command', _new_send_message)

    res = driver.read_pipette_model('left')
    assert res == 'p300_single_v1.3'