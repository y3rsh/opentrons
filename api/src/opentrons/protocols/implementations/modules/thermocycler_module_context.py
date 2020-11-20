import logging
from typing import List, Optional

from opentrons import types
from opentrons.hardware_control.modules import Thermocycler, ThermocyclerStep
from opentrons.hardware_control.types import Axis
from opentrons.protocols.geometry.module_geometry import ThermocyclerGeometry
from opentrons.protocols.implementations.interfaces.labware import \
    LabwareInterface
from opentrons.protocols.implementations.interfaces.modules.thermocycler_module_context import \
    ThermocyclerContextInterface
from opentrons.protocols.implementations.interfaces.protocol_context import \
    ProtocolContextInterface
from opentrons.protocols.implementations.modules.module_context import \
    ModuleBase


MODULE_LOG = logging.getLogger(__name__)


class ThermocyclerModuleContextImplementation(ModuleBase,
                                              ThermocyclerContextInterface):

    def __init__(
            self,
            protocol_context: ProtocolContextInterface,
            hw_module: Thermocycler,
            geometry: ThermocyclerGeometry):
        super().__init__(protocol_context, geometry)
        self._module = hw_module

    def open_lid(self) -> None:
        self._prepare_for_lid_move()
        self._geometry.lid_status = self._module.open()

    def close_lid(self) -> None:
        self._prepare_for_lid_move()
        self._geometry.lid_status = self._module.close()

    def set_block_temperature(self, temperature: float,
                              hold_time_seconds: Optional[float] = None,
                              hold_time_minutes: Optional[float] = None,
                              ramp_rate: Optional[float] = None,
                              block_max_volume: Optional[float] = None) -> None:
        self._module.set_temperature(
            temperature=temperature,
            hold_time_seconds=hold_time_seconds,
            hold_time_minutes=hold_time_minutes,
            ramp_rate=ramp_rate,
            volume=block_max_volume)

    def set_lid_temperature(self, temperature: float) -> None:
        self._module.set_lid_temperature(temperature)

    def execute_profile(self,
                        steps: List[ThermocyclerStep],
                        repetitions: int,
                        block_max_volume: Optional[float] = None) -> None:
        if repetitions <= 0:
            raise ValueError("repetitions must be a positive integer")
        for step in steps:
            if step.get('temperature') is None:
                raise ValueError(
                    "temperature must be defined for each step in cycle")
            hold_mins = step.get('hold_time_minutes')
            hold_secs = step.get('hold_time_seconds')
            if hold_mins is None and hold_secs is None:
                raise ValueError(
                    "either hold_time_minutes or hold_time_seconds must be"
                    "defined for each step in cycle")
        self._module.cycle_temperatures(steps=steps,
                                        repetitions=repetitions,
                                        volume=block_max_volume)

    def deactivate_lid(self) -> None:
        self._module.deactivate_lid()

    def deactivate_block(self) -> None:
        self._module.deactivate_block()

    def deactivate(self) -> None:
        self._module.deactivate()

    def get_lid_status(self) -> str:
        return self._module.lid_status

    def get_block_temperature_status(self) -> str:
        return self._module.status

    def get_lid_temperature_status(self) -> str:
        return self._module.lid_temp_status

    def get_block_temperature(self) -> float:
        return self._module.temperature

    def get_block_target_temperature(self) -> float:
        return self._module.target

    def get_lid_temperature(self) -> float:
        return self._module.lid_temp

    def get_lid_target_temperature(self) -> float:
        return self._module.lid_target

    def get_ramp_rate(self) -> float:
        return self._module.ramp_rate

    def get_hold_time(self) -> int:
        return self._module.hold_time

    def get_total_cycle_count(self) -> int:
        return self._module.total_cycle_count

    def get_current_cycle_index(self) -> int:
        return self._module.current_cycle_index

    def get_total_step_count(self) -> int:
        return self._module.total_step_count

    def get_current_step_index(self) -> int:
        return self._module.current_step_index

    def _prepare_for_lid_move(self):
        loaded_instruments = [
            instr for mount, instr in
            self._protocol_context.get_loaded_instruments().items()
            if instr is not None
        ]
        try:
            instr = loaded_instruments[0]
        except IndexError:
            MODULE_LOG.warning(
                "Cannot assure a safe gantry position to avoid colliding"
                " with the lid of the Thermocycler Module.")
        else:
            ctx_impl = self._protocol_context
            instr_impl = instr
            hardware = ctx_impl.get_hardware().hardware

            hardware.retract(instr_impl.get_mount())
            high_point = hardware.current_position(instr_impl.get_mount())
            fixed_trash = ctx_impl.get_fixed_trash()
            # TODO AL 20201120 Remove this isinstance check. Deck should
            #  standardize on LabwareInterface objects.
            if isinstance(fixed_trash, LabwareInterface):
                trash_top = fixed_trash.get_wells()[0].get_geometry().top()
            else:
                trash_top = fixed_trash.wells()[0].top()
            safe_point = trash_top.point._replace(
                    z=high_point[Axis.by_mount(instr_impl.get_mount())])
            instr.move_to(types.Location(safe_point, None), force_direct=True)

    def flag_unsafe_move(self,
                         to_loc: types.Location,
                         from_loc: types.Location):
        """Raise an exception on an unsafe move to or from labware on
        thermocycler."""
        to_lw, to_well = to_loc.labware.get_parent_labware_and_well()
        from_lw, from_well = from_loc.labware.get_parent_labware_and_well()
        labware = self.get_geometry().labware
        if labware is not None and \
                (labware == to_lw or labware == from_lw) and \
                self.get_lid_status() != 'open':
            raise RuntimeError(
                "Cannot move to labware loaded in Thermocycler"
                " when lid is not fully open.")
