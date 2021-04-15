import asyncio
from abc import abstractmethod, ABC
from dataclasses import dataclass

from opentrons.drivers.asyncio.communication.serial_connection import SerialException
from opentrons.drivers.asyncio.thermocycler import AbstractThermocyclerDriver
from opentrons.drivers.types import (
    PlateTemperature, ThermocyclerLidStatus, Temperature
)


@dataclass
class State:
    """Polled thermocycler status."""
    plate_temperature: PlateTemperature
    lid_temperature: Temperature
    lid_status: ThermocyclerLidStatus


class Listener(ABC):
    """Interface of poller listener"""

    @abstractmethod
    def on_state(self, state: State) -> None:
        """
        Called by poller notifying result of new poll.

        Args:
            state: The latest poll result.

        Returns: None
        """
        ...

    @abstractmethod
    def on_error(self, exception: Exception) -> None:
        """
        Called by poller to notify of a poll error.

        Args:
            exception: The raised exception

        Returns: None
        """
        ...

    @abstractmethod
    def on_terminated(self) -> None:
        """
        Called by poller when it is terminating.

        Returns: None
        """
        ...


class Poller:
    def __init__(
            self,
            interval_seconds: float,
            driver: AbstractThermocyclerDriver,
            listener: Listener) -> None:
        """
        Constructor.

        Args:
            interval_seconds: time in between polls.
            driver: the thermocycler driver
            listener: event listener
        """
        self._shutdown_event = asyncio.Event()
        self._interval = interval_seconds
        self._listener = listener
        self._driver = driver
        self._task = asyncio.create_task(self._poller())

    def stop(self) -> None:
        """Signal poller to stop."""
        self._shutdown_event.set()

    async def stop_and_wait(self) -> None:
        """Stop poller and wait for it to terminate."""
        self.stop()
        await self._task

    async def _poller(self) -> None:
        """Poll thermocycler status."""
        while True:
            try:
                lid_status = await self._driver.get_lid_status()
                temperature = await self._driver.get_lid_temperature()
                plate_temperature = await self._driver.get_plate_temperature()
                self._listener.on_state(
                    state=State(
                        plate_temperature=plate_temperature,
                        lid_temperature=temperature,
                        lid_status=lid_status
                    )
                )
            except SerialException as e:
                self._listener.on_error(e)

            try:
                await asyncio.wait_for(self._shutdown_event.wait(), self._interval)
            except asyncio.TimeoutError:
                pass
            else:
                break

        self._listener.on_terminated()

