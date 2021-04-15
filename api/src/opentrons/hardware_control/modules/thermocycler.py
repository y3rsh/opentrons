import asyncio
import logging
from typing import Union, Optional, List, Callable, Dict
from opentrons.drivers.rpi_drivers.types import USBPort
from opentrons.drivers.types import ThermocyclerLidStatus

from ..execution_manager import ExecutionManager
from . import types, update, mod_abc
from opentrons.drivers.thermocycler.driver import (
    HOLD_TIME_FUZZY_SECONDS
)
from opentrons.drivers.asyncio.thermocycler import (
    AbstractThermocyclerDriver, SimulatingDriver, ThermocyclerDriver
)


MODULE_LOG = logging.getLogger(__name__)


class Thermocycler(mod_abc.AbstractModule):
    """
    Under development. API subject to change without a version bump
    """
    @classmethod
    async def build(cls,
                    port: str,
                    usb_port: USBPort,
                    execution_manager: ExecutionManager,
                    interrupt_callback: types.InterruptCallback = None,
                    simulating: bool = False,
                    loop: asyncio.AbstractEventLoop = None,
                    sim_model: str = None):
        """Build and connect to a Thermocycler
        """
        driver: AbstractThermocyclerDriver
        if not simulating:
            driver = await ThermocyclerDriver.create(port=port)
        else:
            driver = SimulatingDriver()

        mod = cls(port=port,
                  usb_port=usb_port,
                  driver=driver,
                  device_info=await driver.get_device_info(),
                  interrupt_callback=interrupt_callback,
                  loop=loop,
                  execution_manager=execution_manager)
        return mod

    def __init__(self,
                 port: str,
                 usb_port: USBPort,
                 execution_manager: ExecutionManager,
                 driver: AbstractThermocyclerDriver,
                 device_info: Dict[str, str],
                 interrupt_callback: types.InterruptCallback = None,
                 loop: asyncio.AbstractEventLoop = None
                 ) -> None:
        """
        Constructor

        Args:
            port: The port the thermocycler is connected to.
            usb_port: The USB port.
            execution_manager: The hardware execution manager.
            driver: The thermocycler driver.
            device_info: The thermocycler device info.
            interrupt_callback: Optional interrupt callback.
            loop: Optional loop.
        """
        super().__init__(port=port,
                         usb_port=usb_port,
                         loop=loop,
                         execution_manager=execution_manager)
        self._driver = driver
        self._device_info = device_info
        self._interrupt_cb = interrupt_callback

        self._total_cycle_count: Optional[int] = None
        self._current_cycle_index: Optional[int] = None
        self._total_step_count: Optional[int] = None
        self._current_step_index: Optional[int] = None

    @classmethod
    def name(cls) -> str:
        return 'thermocycler'

    def model(self) -> str:
        return 'thermocyclerModuleV1'

    @classmethod
    def bootloader(cls) -> types.UploadFunction:
        return update.upload_via_bossa

    def _clear_cycle_counters(self) -> None:
        """Clear the cycle counters."""
        self._total_cycle_count = None
        self._current_cycle_index = None
        self._total_step_count = None
        self._current_step_index = None

    async def deactivate_lid(self):
        """Deactivate the lid heating pad"""
        await self.wait_for_is_running()
        return await self._driver.deactivate_lid()

    async def deactivate_block(self):
        """Deactivate the block peltiers"""
        await self.wait_for_is_running()
        self._clear_cycle_counters()
        return await self._driver.deactivate_block()

    async def deactivate(self):
        """Deactivate the block peltiers and lid heating pad"""
        await self.wait_for_is_running()
        self._clear_cycle_counters()
        return await self._driver.deactivate_all()

    async def open(self) -> str:
        """Open the lid if it is closed"""
        await self.wait_for_is_running()
        await self._driver.open_lid()
        return ThermocyclerLidStatus.OPEN

    async def close(self) -> str:
        """ Close the lid if it is open"""
        await self.wait_for_is_running()
        await self._driver.close_lid()
        return ThermocyclerLidStatus.CLOSED

    async def set_temperature(
            self,
            temperature: float,
            hold_time_seconds: Optional[float] = None,
            hold_time_minutes: Optional[float] = None,
            ramp_rate: Optional[float] = None,
            volume: Optional[float] = None) -> None:
        """
        Set the temperature and wait.

        If hold time is set this function will return after
        the hold time expires.

        Otherwise it will return when the terget temperature is reached.

        Args:
            temperature: The target temperature.
            hold_time_seconds: Optional number of seconds to wait.
            hold_time_minutes: Optional number of minutes to wait.
            ramp_rate: Optional ramp rate.
            volume: Optional volume.

        Returns: None
        """
        await self.wait_for_is_running()
        seconds = hold_time_seconds if hold_time_seconds is not None else 0
        minutes = hold_time_minutes if hold_time_minutes is not None else 0
        total_seconds = seconds + (minutes * 60)
        hold_time = total_seconds if total_seconds > 0 else 0
        if ramp_rate is not None:
            await self._driver.set_ramp_rate(ramp_rate=ramp_rate)
        await self._driver.set_plate_temperature(
            temp=temperature,
            hold_time=hold_time,
            volume=volume)

        if hold_time:
            task = self._loop.create_task(
                self.wait_for_hold(hold_time))
        else:
            task = self._loop.create_task(
                self.wait_for_temp())
        await self.make_cancellable(task)
        await task

    async def cycle_temperatures(self,
                                 steps: List[types.ThermocyclerStep],
                                 repetitions: int,
                                 volume: float = None) -> None:
        """
        Begin a set temperature cycle.

        Args:
            steps: The set temperature steps.
            repetitions: Number of repetitions.
            volume: Optional volume.

        Returns: None
        """
        await self.wait_for_is_running()
        self._total_cycle_count = repetitions
        self._total_step_count = len(steps)

        task = self._loop.create_task(
            self._execute_cycles(steps,
                                 repetitions,
                                 volume))
        await self.make_cancellable(task)
        await task

    async def set_lid_temperature(self, temperature: float):
        """ Set the lid temperature in deg Celsius """
        await self.wait_for_is_running()
        await self._driver.set_lid_temperature(temp=temperature)
        task = self._loop.create_task(self.wait_for_lid_temp())
        await self.make_cancellable(task)
        await task

    async def wait_for_lid_temp(self):
        """
        This method only exits if lid target temperature has been reached.

        Subject to change without a version bump.
        """
        if self.is_simulated:
            return

        while self._driver.lid_temp_status != 'holding at target':
            await asyncio.sleep(0.1)

    async def wait_for_temp(self):
        """
        This method only exits if set temperature has been reached.

        Subject to change without a version bump.
        """
        if self.is_simulated:
            return

        while self.status != 'holding at target':
            await asyncio.sleep(0.1)

    async def wait_for_hold(self, hold_time=0):
        """
        This method returns only when hold time has elapsed
        """
        if self.is_simulated:
            return

        # If hold time is within the HOLD_TIME_FUZZY_SECONDS time gap, then,
        # because of the driver's status poller delays, it is impossible to
        # know for certain if self.hold_time holds the most recent value.
        # So instead of counting on the cached self.hold_time, it is better to
        # just wait for hold_time time. (Skip if hold_time = 0 since we don't
        # want to wait in that case. Cached self.hold_time would be 0 anyway)
        if 0 < hold_time <= HOLD_TIME_FUZZY_SECONDS:
            await asyncio.sleep(hold_time)
        else:
            while self.hold_time != 0:
                await asyncio.sleep(0.1)

    @property
    def lid_target(self):
        return self._driver.lid_target

    @property
    def lid_temp(self):
        return self._driver.lid_temp

    @property
    def lid_status(self):
        return self._driver.lid_status

    @property
    def lid_temp_status(self):
        return self._driver.lid_temp_status

    @property
    def ramp_rate(self):
        return self._driver.ramp_rate

    @property
    def hold_time(self):
        return self._driver.hold_time

    @property
    def temperature(self):
        return self._driver.temperature

    @property
    def target(self):
        return self._driver.target

    @property
    def status(self):
        return self._driver.status

    @property
    def device_info(self):
        return self._device_info

    @property
    def total_cycle_count(self):
        return self._total_cycle_count

    @property
    def current_cycle_index(self):
        return self._current_cycle_index

    @property
    def total_step_count(self):
        return self._total_step_count

    @property
    def current_step_index(self):
        return self._current_step_index

    @property
    def live_data(self):
        return {
            'status': self.status,
            'data': {
                'lid': self.lid_status,
                'lidTarget': self.lid_target,
                'lidTemp': self.lid_temp,
                'currentTemp': self.temperature,
                'targetTemp': self.target,
                'holdTime': self.hold_time,
                'rampRate': self.ramp_rate,
                'currentCycleIndex': self.current_cycle_index,
                'totalCycleCount': self.total_cycle_count,
                'currentStepIndex': self.current_step_index,
                'totalStepCount': self.total_step_count,
            }
        }

    @property
    def is_simulated(self):
        return isinstance(self._driver, SimulatingDriver)

    @property
    def interrupt_callback(self):
        """ Fetch the current interrupt callback

        Exposes the interrupt callback used with the TCPoller, so it can be re-
        hooked in the new module instance after a firmware update.
        """
        return self._interrupt_cb

    async def prep_for_update(self):
        await self._driver.enter_programming_mode()

        new_port = await update.find_bootloader_port()

        return new_port or self.port

    async def _execute_cycle_step(
            self,
            step: types.ThermocyclerStep,
            volume: Optional[float]) -> None:
        """
        Execute a themrocycler step.

        Args:
            step: The set temperature parameters.
            volume: The volume

        Returns: None
        """
        await self.wait_for_is_running()

        temperature = step.get('temperature')
        hold_time_minutes = step.get('hold_time_minutes', None)
        hold_time_seconds = step.get('hold_time_seconds', None)
        ramp_rate = step.get('ramp_rate', None)
        await self.set_temperature(temperature=temperature,
                                   hold_time_minutes=hold_time_minutes,
                                   hold_time_seconds=hold_time_seconds,
                                   ramp_rate=ramp_rate,
                                   volume=volume)

    async def _execute_cycles(self,
                              steps: List[types.ThermocyclerStep],
                              repetitions: int,
                              volume: Optional[float] = None) -> None:
        """
        Execute cycles.

        Args:
            steps: The set temperature steps.
            repetitions: The number of repetitions
            volume: The optional volume.

        Returns: None
        """
        for rep in range(repetitions):
            self._current_cycle_index = rep + 1  # science starts at 1
            for step_idx, step in enumerate(steps):
                self._current_step_index = step_idx + 1  # science starts at 1
                await self._execute_cycle_step(step, volume)
                await self.wait_for_hold()
