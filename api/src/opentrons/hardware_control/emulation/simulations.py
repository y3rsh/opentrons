from typing import Optional


class Simulation:
    def tick(self) -> None:
        pass


class Temperature(Simulation):
    """A model with a current and target temperature. The current temperate is
    always moving towards the target.
    """

    def __init__(self, percent_per_tick: float, close_enough: float,
                 current: float) -> None:
        """Construct a temperature simulation.

        Args:
            percent_per_tick: what percent of the difference between target
                and current to move each tick.
            close_enough: how close to target is considered close enough
            current: the starting temperature
        """
        self._percent_per_tick = percent_per_tick
        self._close_enough = close_enough
        self._current = current
        self._target: Optional[float] = None

    def tick(self) -> None:
        if self._target is None:
            return

        diff = self._target - self._current
        abs_diff = abs(diff)

        m = self._close_enough if abs_diff < self._close_enough else abs_diff * self._close_enough

        if diff > 0:
            self._current += m
        else:
            self._current -= m

    def set_target(self, target: float) -> None:
        self._target = target

    @property
    def current(self) -> float:
        return self._current

    @property
    def target(self) -> Optional[float]:
        return self._target


class TemperatureWithHold(Temperature):
    """A model with a current, target temperature and hold time. The current
     temperate is always moving towards the target.

     When the current temperature is within close enough from target the hold time
     decrements once per tick.
    """
    def __init__(self, percent_per_tick: float, close_enough: float,
                 current: float) -> None:
        """Construct a temperature with hold simulation."""
        super().__init__(percent_per_tick=percent_per_tick,
                         close_enough=close_enough, current=current)
        self._total_hold: Optional[float] = None
        self._hold: Optional[float] = None

    def tick(self) -> None:
        super().tick()
        if self.target is not None and self._hold is not None:
            if abs(self.target - self.current) < self._close_enough:
                self._hold = max(0, self._hold - 1)

    def set_hold(self, hold: float) -> None:
        self._total_hold = hold
        self._hold = hold

    @property
    def time_remaining(self) -> Optional[float]:
        return self._hold

    @property
    def total_hold(self) -> Optional[float]:
        return self._total_hold
