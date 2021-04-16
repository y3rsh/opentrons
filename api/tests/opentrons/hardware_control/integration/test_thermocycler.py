import asyncio

import pytest
from opentrons.drivers.rpi_drivers.types import USBPort
from opentrons.hardware_control import ExecutionManager
from opentrons.hardware_control.emulation.app import THERMOCYCLER_PORT
from opentrons.hardware_control.modules import Thermocycler


@pytest.fixture
async def thermocycler(
        loop: asyncio.BaseEventLoop,
        emulation_app) -> Thermocycler:
    """Thermocycler fixture."""
    execution_manager = ExecutionManager(loop)
    module = await Thermocycler.build(
        port=f"socket://127.0.0.1:{THERMOCYCLER_PORT}",
        execution_manager=execution_manager,
        usb_port=USBPort(name="", port_number=1, sub_names=[], device_path="",
                         hub=1),
        loop=loop
    )
    yield module
    module.cleanup()
    await execution_manager.cancel()


def test_device_info(thermocycler: Thermocycler):
    """It should have device info."""
    assert {'model': 'thermocycler_emulator', 'serial': 'fake_serial',
            'version': '1'} == thermocycler.device_info


async def test_lid_status(thermocycler: Thermocycler):
    """It should run open and close lid."""
    await thermocycler.wait_next_poll()
    assert thermocycler.lid_status == "closed"

    await thermocycler.open()
    await thermocycler.wait_next_poll()
    assert thermocycler.lid_status == "open"

    await thermocycler.close()
    await thermocycler.wait_next_poll()
    assert thermocycler.lid_status == "closed"


async def test_lid_temperature(thermocycler: Thermocycler):
    """It should cycle lid temperature."""
    await thermocycler.set_lid_temperature(temperature=50)
    assert thermocycler.lid_target == 50


async def test_plate_temperature(thermocycler: Thermocycler):
    """It should cycle plate temperature."""
    await thermocycler.set_temperature(temperature=52, hold_time_seconds=0.1)
    assert thermocycler.temperature == 52
