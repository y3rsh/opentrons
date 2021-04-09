import asyncio
import logging
from typing import Mapping, Optional
from typing_extensions import Final
from enum import Enum
from opentrons.drivers.types import Temperature
from opentrons.drivers.asyncio.tempdeck import (
    SimulatingDriver, AbstractTempDeckDriver, TempDeckDriver)
from opentrons.drivers.rpi_drivers.types import USBPort
from opentrons.hardware_control.execution_manager import ExecutionManager
from opentrons.hardware_control.modules import update, mod_abc, types

log = logging.getLogger(__name__)

TEMP_POLL_INTERVAL_SECS = 1


class Status(str, Enum):
    HOLDING = 'holding at target'
    COOLING = 'cooling'
    HEATING = 'heating'
    IDLE = 'idle'


class TempDeck(mod_abc.AbstractModule):
    """
    Under development. API subject to change without a version bump
    """
    FIRST_GEN2_REVISION = 20

    @classmethod
    async def build(cls,
                    port: str,
                    usb_port: USBPort,
                    execution_manager: ExecutionManager,
                    interrupt_callback: types.InterruptCallback = None,
                    simulating: bool = False,
                    loop: asyncio.AbstractEventLoop = None,
                    sim_model: str = None):
        """Build a TempDeck"""
        driver: AbstractTempDeckDriver
        if not simulating:
            driver = await TempDeckDriver.create(port=port)
        else:
            driver = SimulatingDriver(sim_model=sim_model)

        mod = cls(port=port,
                  usb_port=usb_port,
                  execution_manager=execution_manager,
                  driver=driver,
                  device_info=await driver.get_device_info(),
                  loop=loop)
        return mod

    def __init__(self,
                 port: str,
                 usb_port: USBPort,
                 execution_manager: ExecutionManager,
                 driver: AbstractTempDeckDriver,
                 device_info: Mapping[str, str],
                 loop: asyncio.AbstractEventLoop = None
                 ) -> None:
        """Constructor"""
        super().__init__(port=port,
                         usb_port=usb_port,
                         loop=loop,
                         execution_manager=execution_manager)
        self._device_info = device_info
        self._driver = driver
        self._poller = TemperaturePoller(
            driver=self._driver,
            interval_seconds=TEMP_POLL_INTERVAL_SECS
        )

    def __del__(self):
        self._poller.stop()

    @classmethod
    def name(cls) -> str:
        return 'tempdeck'

    def model(self) -> str:
        return self._model_from_revision(self._device_info.get('model'))

    @classmethod
    def bootloader(cls) -> mod_abc.UploadFunction:
        return update.upload_via_avrdude

    async def set_temperature(self, celsius: float) -> None:
        """
        Set temperature in degree Celsius
        Range: 4 to 95 degree Celsius (QA tested).
        The internal temp range is -9 to 99 C, which is limited by the 2-digit
        temperature display. Any input outside of this range will be clipped
        to the nearest limit
        """
        await self.wait_for_is_running()
        await self._driver.set_temperature(celsius=celsius)
        # Wait until we reach the target temperature.
        while self.status != Status.HOLDING:
            await self._poller.wait_next_poll()

    async def start_set_temperature(self, celsius) -> None:
        """
        Set temperature in degree Celsius
        Range: 4 to 95 degree Celsius (QA tested).
        The internal temp range is -9 to 99 C, which is limited by the 2-digit
        temperature display. Any input outside of this range will be clipped
        to the nearest limit
        """
        await self.wait_for_is_running()
        await self._driver.set_temperature(celsius)

    async def await_temperature(self, awaiting_temperature: float):
        """
        Await temperature in degree Celsius
        Polls temperature module's temperature until
        the specified temperature is reached
        """
        if self.is_simulated:
            return

        await self.wait_for_is_running()

        while (
                self.status == Status.HEATING and
                self.temperature < awaiting_temperature
        ) or (
                self.status == Status.COOLING and
                self.temperature > awaiting_temperature
        ):
            await self._poller.wait_next_poll()

    async def deactivate(self):
        """ Stop heating/cooling and turn off the fan """
        await self.wait_for_is_running()
        await self._driver.deactivate()

    @property
    def device_info(self) -> Mapping[str, str]:
        return self._device_info

    @property
    def live_data(self) -> types.LiveData:
        return {
            'status': self.status,
            'data': {
                'currentTemp': self.temperature,
                'targetTemp': self.target
            }
        }

    @property
    def temperature(self) -> float:
        return self._poller.temperature.current

    @property
    def target(self) -> Optional[float]:
        return self._poller.temperature.target

    @property
    def status(self) -> str:
        return self._get_status(self._poller.temperature).value

    @property
    def is_simulated(self) -> bool:
        return isinstance(self._driver, SimulatingDriver)

    @property
    def interrupt_callback(self) -> types.InterruptCallback:
        return lambda x: None

    async def prep_for_update(self) -> str:
        model = self._device_info and self._device_info.get('model')
        if model in ('temp_deck_v1', 'temp_deck_v1.1', 'temp_deck_v2'):
            raise types.UpdateError("This Temperature Module can't be updated."
                                    "Please contact Opentrons Support.")
        await self._poller.stop_and_wait()
        await self._driver.enter_programming_mode()
        new_port = await update.find_bootloader_port()
        return new_port or self.port

    def has_available_update(self) -> bool:
        """ Override of abc implementation to suppress update notifications
        for v1, v1.1, and v2 temperature modules which cannot be updated """
        if not self._device_info:
            model = None
        else:
            model = self._device_info.get('model')
        if model in {'temp_deck_v1', 'temp_deck_v1.1', 'temp_deck_v2', None}:
            return False
        return super().has_available_update()

    @staticmethod
    def _get_status(temperature: Temperature) -> Status:
        """
        Determine the status from the temperature.

        Args:
            temperature: A Temperature instance

        Returns:
            The status
        """
        DELTA: Final = 0.7
        status = Status.IDLE
        if temperature.target is not None:
            diff = temperature.target - temperature.current
            if abs(diff) < DELTA:  # To avoid status fluctuation near target
                status = Status.HOLDING
            elif diff < 0:
                status = Status.COOLING
            else:
                status = Status.HEATING
        return status

    @staticmethod
    def _model_from_revision(revision: Optional[str]) -> str:
        """ Defines the revision -> model mapping"""
        if not revision or 'v' not in revision:
            log.error(f'bad revision: {revision}')
            return 'temperatureModuleV1'
        try:
            revision_num = float(revision.split('v')[-1])  # type: ignore
        except (ValueError, TypeError):
            # none or corrupt
            log.exception('no revision')
            return 'temperatureModuleV1'

        if revision_num < TempDeck.FIRST_GEN2_REVISION:
            return 'temperatureModuleV1'
        else:
            return 'temperatureModuleV2'


class TemperaturePoller:
    def __init__(
            self,
            driver: AbstractTempDeckDriver,
            interval_seconds: float) -> None:
        """Construct the poller."""
        self._driver = driver
        self._condition = asyncio.Condition()
        self._shutdown_event = asyncio.Event()
        self._temperature = Temperature(current=25, target=None)
        self._interval = interval_seconds
        self._task = asyncio.create_task(self._poller())

    @property
    def temperature(self) -> Temperature:
        """Get the most recent temperature."""
        return self._temperature

    async def wait_next_poll(self) -> Temperature:
        """Wait for the next poll result."""
        # TODO Fail on self._shutdown_event.is_set == True
        async with self._condition:
            await self._condition.wait()
            return self._temperature

    def stop(self) -> None:
        """Stop the poller."""
        self._shutdown_event.set()

    async def stop_and_wait(self) -> None:
        """Stop the poller and wait for it to complete."""
        self.stop()
        await self._task

    async def _poller(self) -> None:
        """Poll the temperature. This is the task entry point."""
        while True:
            temperature = await self._driver.get_temperature()
            async with self._condition:
                self._temperature = temperature
                self._condition.notify_all()
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self._interval
                )
            except asyncio.TimeoutError:
                # Continue polling
                pass
            else:
                log.debug('Tempdeck poller terminating')
                break
