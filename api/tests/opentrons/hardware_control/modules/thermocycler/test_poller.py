# from mock import AsyncMock, MagicMock
# import pytest
# from opentrons.drivers.asyncio.communication.serial_connection import \
#     AlarmResponse
# from opentrons.drivers.asyncio.thermocycler import AbstractThermocyclerDriver
# from opentrons.hardware_control.modules.thermocycler_.poller import (
#     Poller, Listener, State
# )
#
#
# @pytest.fixture
# def mock_driver() -> AsyncMock:
#     """Thermocycler driver mock."""
#     return AsyncMock(spec=AbstractThermocyclerDriver)
#
#
# @pytest.fixture
# def mock_listener() -> MagicMock:
#     """Mock listener."""
#     return MagicMock(spec=Listener)
#
#
# @pytest.fixture
# async def subject(mock_driver: AsyncMock, mock_listener: MagicMock) -> Poller:
#     """Test subject."""
#     p = Poller(interval_seconds=.01, driver=mock_driver, listener=mock_listener)
#     yield p
#     await p.stop_and_wait()
#
#
# def test_poller_raise(
#         subject: Poller, mock_driver: AsyncMock, mock_listener: MagicMock) -> None:
#     """It should call listener on polling error."""
#     exc = AlarmResponse()
#
#     def raiser():
#         raise exc
#
#     mock_driver.get_lid_status.side_effect = raiser
#
#     mock_listener.assert_called_once_with(exc)
