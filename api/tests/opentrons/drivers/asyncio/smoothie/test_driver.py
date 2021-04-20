from copy import deepcopy

from opentrons.drivers.asyncio.communication import AlarmResponse
from opentrons.drivers.asyncio.smoothie import constants, parse_utils
import opentrons.drivers.asyncio.smoothie.parse_utils
from mock import AsyncMock
from unittest.mock import Mock
import pytest
from opentrons.drivers.asyncio.smoothie.command_sender import \
    SmoothieCommandSender
from opentrons.drivers.rpi_drivers.gpio_simulator import SimulatingGPIOCharDev
from opentrons.drivers.types import MoveSplit

from opentrons.config.robot_configs import (
    DEFAULT_GANTRY_STEPS_PER_MM, DEFAULT_PIPETTE_CONFIGS)
from opentrons.drivers.asyncio.smoothie import driver


@pytest.fixture
async def mock_connection() -> AsyncMock:
    """The mock SerialConnection."""
    return AsyncMock(spec=SmoothieCommandSender)


@pytest.fixture
def sim_gpio() -> SimulatingGPIOCharDev:
    """The mock GPI."""
    return SimulatingGPIOCharDev("sim")


@pytest.fixture
def smoothie(mock_connection: AsyncMock, sim_gpio) -> driver.SmoothieDriver:
    """The smoothie driver under test."""
    from opentrons.config import robot_configs

    d = driver.SmoothieDriver(
        connection=mock_connection,
        config=robot_configs.load(),
        gpio_chardev=sim_gpio
    )
    yield d


def position(x, y, z, a, b, c):
    return {axis: value for axis, value in zip('XYZABC', [x, y, z, a, b, c])}


async def test_update_position(smoothie: driver.SmoothieDriver,
                               mock_connection: AsyncMock) -> None:
    """It should update the position."""
    mock_connection.send_command.return_value = 'ok MCS: X:1.0000 Y:2.0000 Z:3.0000 A:4.5000 B:0.0000 C:0.0000'

    await smoothie.update_position()
    expected = {
        'X': 1,
        'Y': 2,
        'Z': 3,
        'A': 4.5,
        'B': 0,
        'C': 0
    }
    assert smoothie.position == expected


async def test_update_position_retry(
        smoothie: driver.SmoothieDriver, mock_connection: AsyncMock
) -> None:
    """It should retry after a parse error."""
    mock_connection.send_command.side_effect = [
        # first attempt to read, we get bad data
        'ok MCS: X:0.0000 Y:MISTAKE Z:0.0000 A:0.0000 B:0.0000 C:0.0000',
        # following attempts to read, we get good data
        'ok MCS: X:0.0000 Y:321.00 Z:0.0000 A:0.0000 B:0.0000 C:0.0000'
    ]

    await smoothie.update_position()
    expected = {
        'X': 0,
        'Y': 321.00,
        'Z': 0,
        'A': 0,
        'B': 0,
        'C': 0
    }
    assert smoothie.position == expected


def test_active_dwelling_current_push_pop(smoothie):
    assert smoothie._active_current_settings != \
           smoothie._dwelling_current_settings

    old_active_currents = deepcopy(smoothie._active_current_settings)
    old_dwelling_currents = deepcopy(smoothie._dwelling_current_settings)

    smoothie.push_active_current()
    smoothie.set_active_current({'X': 2.0, 'Y': 2.0, 'Z': 2.0, 'A': 2.0})
    smoothie.pop_active_current()

    assert smoothie._active_current_settings == old_active_currents
    assert smoothie._dwelling_current_settings == old_dwelling_currents


@pytest.mark.skip()
async def test_functional(smoothie: driver.SmoothieDriver):
    assert smoothie.position == position(0, 0, 0, 0, 0, 0)

    await smoothie.move({'X': 0, 'Y': 1, 'Z': 2, 'A': 3, 'B': 4, 'C': 5})
    assert smoothie.position == position(0, 1, 2, 3, 4, 5)

    await smoothie.move({'X': 1, 'Z': 3, 'C': 6})
    assert smoothie.position == position(1, 1, 3, 3, 4, 6)

    await smoothie.home(axis='abc', disabled='')
    assert smoothie.position == position(
        1, 1, 3,
        smoothie.homed_position['A'],
        smoothie.homed_position['B'],
        smoothie.homed_position['C'])

    await smoothie.home(disabled='')
    assert smoothie.position == smoothie.homed_position


async def test_read_pipette_v13(smoothie: driver.SmoothieDriver, mock_connection: AsyncMock):
    mock_connection.send_command.return_value = 'L:' + parse_utils.byte_array_to_hex_string(b'p300_single_v13')
    res = await smoothie.read_pipette_model('left')
    assert res == 'p300_single_v1.3'


async def test_switch_state(smoothie: driver.SmoothieDriver, mock_connection: AsyncMock):
    smoothie_switch_res = 'X_max:0 Y_max:0 Z_max:0 A_max:0 B_max:0 C_max:0' \
                          ' _pins ' \
                          '(XL)2.01:0 (YL)2.01:0 (ZL)2.01:0 ' \
                          '(AL)2.01:0 (BL)2.01:0 (CL)2.01:0 Probe: 0\r\n'

    mock_connection.send_command.return_value = smoothie_switch_res

    expected = {
        'X': False,
        'Y': False,
        'Z': False,
        'A': False,
        'B': False,
        'C': False,
        'Probe': False
    }
    r = await smoothie.switch_state()
    assert r == expected

    smoothie_switch_res = 'X_max:0 Y_max:0 Z_max:0 A_max:1 B_max:0 C_max:0' \
                          ' _pins ' \
                          '(XL)2.01:0 (YL)2.01:0 (ZL)2.01:0 ' \
                          '(AL)2.01:0 (BL)2.01:0 (CL)2.01:0 Probe: 1\r\n'

    mock_connection.send_command.return_value = smoothie_switch_res

    expected = {
        'X': False,
        'Y': False,
        'Z': False,
        'A': True,
        'B': False,
        'C': False,
        'Probe': True
    }
    r = await smoothie.switch_state()
    assert r == expected


async def test_clear_limit_switch(smoothie: driver.SmoothieDriver, mock_connection: AsyncMock):
    """
    This functions as a contract test around recovery from a limit-switch hit.
    Note that this *does not* itself guarantee correct physical behavior--this
    interaction has been designed and tested on the robot manually and then
    encoded in this test. If requirements change around physical behavior, then
    this test will need to be revised.
    """
    cmd_list = []

    def write_mock(command, retries):
        cmd_list.append(command.build())
        if constants.GCODE.MOVE in command:
            raise AlarmResponse("ALARM: Hard limit +C")
        elif constants.GCODE.CURRENT_POSITION in command:
            return 'ok M114.2 X:10 Y:20 Z:30 A:40 B:50 C:60'
        elif constants.GCODE.HOMING_STATUS in command:
            return 'X:1 Y:1 Z:1 A:1 B:1 C:1'
        else:
            return "ok"

    mock_connection.send_command.side_effect = write_mock

    # This will cause a limit-switch error and not back off
    with pytest.raises(driver.SmoothieError):
        await smoothie.move({'C': 100})

    assert [c.strip() for c in cmd_list] == [
        # attempt to move and fail
        'M907 A0.1 B0.05 C0.05 X0.3 Y0.3 Z0.1 G4 P0.005 G0 C100.3 G0 C100',
        # recover from failure
        'M999',
        'G28.6',
        # set current for homing the failed axis (C)
        'M907 A0.1 B0.05 C0.05 X0.3 Y0.3 Z0.1 G4 P0.005 G28.2 C',
        # set current back to idling after home
        'M907 A0.1 B0.05 C0.05 X0.3 Y0.3 Z0.1 G4 P0.005',
        # update position
        'M114.2',
        'M907 A0.1 B0.05 C0.05 X0.3 Y0.3 Z0.1 G4 P0.005',
    ]
