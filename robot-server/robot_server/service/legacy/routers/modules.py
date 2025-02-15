import typing
import asyncio
from starlette import status
from fastapi import Path, APIRouter, Depends

from opentrons.hardware_control import modules, HardwareControlAPI
from opentrons.hardware_control.modules import AbstractModule

from robot_server.errors import LegacyErrorResponse
from robot_server.hardware import get_hardware
from robot_server.service.legacy.models import V1BasicResponse
from robot_server.service.legacy.models.modules import (
    Module,
    ModuleSerial,
    Modules,
    SerialCommandResponse,
    SerialCommand,
    PhysicalPort,
)

router = APIRouter()


@router.get(
    "/modules",
    description="Describe the modules attached to the OT-2",
    response_model=Modules,
)
async def get_modules(
    hardware: HardwareControlAPI = Depends(get_hardware),
) -> Modules:
    attached_modules = hardware.attached_modules
    module_data = [
        Module(
            name=mod.name(),  # TODO: legacy, remove
            displayName=mod.name(),  # TODO: legacy, remove
            model=mod.device_info.get("model"),  # type: ignore
            moduleModel=mod.model(),
            port=mod.port,  # /dev/ttyS0
            usbPort=PhysicalPort(hub=mod.usb_port.hub, port=mod.usb_port.port_number),
            serial=mod.device_info.get("serial"),  # type: ignore
            revision=mod.device_info.get("model"),  # type: ignore
            fwVersion=mod.device_info.get("version"),  # type: ignore
            hasAvailableUpdate=mod.has_available_update(),
            # TODO: these type ignores are necessary for now because of imprecision in
            # the return values on the hardware side now that we're actually chekcing
            # the types
            status=mod.live_data["status"],  # type: ignore
            data=mod.live_data["data"],  # type: ignore
        )
        for mod in attached_modules
    ]
    return Modules(modules=module_data)


@router.get(
    path="/modules/{serial}/data",
    summary="Get live data for a specific module",
    description=(
        "This is similar to the values in GET /modules, but "
        "for only a specific currently-attached module"
    ),
    response_model=ModuleSerial,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": LegacyErrorResponse},
    },
)
async def get_module_serial(
    serial: str = Path(..., description="Serial number of the module"),
    hardware: HardwareControlAPI = Depends(get_hardware),
) -> ModuleSerial:
    res = None

    attached_modules = hardware.attached_modules
    matching_module = find_matching_module(serial, attached_modules)
    if matching_module and hasattr(matching_module, "live_data"):
        res = matching_module.live_data

    if not res:
        raise LegacyErrorResponse(message="Module not found").as_error(
            status.HTTP_404_NOT_FOUND
        )

    # TODO(mc, 2020-09-17): types of res.get(...) do not match what
    # ModuleSerial expects
    return ModuleSerial(
        status=res.get("status"),  # type: ignore[arg-type]
        data=res.get("data"),  # type: ignore[arg-type]
    )


@router.post(
    path="/modules/{serial}",
    summary="Execute a command on a specific module",
    description=(
        "Command a module to take an action. Valid actions "
        "depend on the specific module attached, which is "
        "the model value from GET /modules/{serial}/data or "
        "GET /modules"
    ),
    response_model=SerialCommandResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": LegacyErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": LegacyErrorResponse},
    },
)
async def post_serial_command(
    command: SerialCommand,
    serial: str = Path(..., description="Serial number of the module"),
    hardware: HardwareControlAPI = Depends(get_hardware),
) -> SerialCommandResponse:
    """Send a command on device identified by serial"""
    attached_modules = hardware.attached_modules
    if not attached_modules:
        raise LegacyErrorResponse(message="No connected modules").as_error(
            status.HTTP_404_NOT_FOUND
        )

    # Search for the module
    matching_mod = find_matching_module(serial, attached_modules)

    if not matching_mod:
        raise LegacyErrorResponse(message="Specified module not found").as_error(
            status.HTTP_404_NOT_FOUND
        )

    if hasattr(matching_mod, command.command_type):
        clean_args = command.args or []
        method = getattr(matching_mod, command.command_type)
        try:
            if asyncio.iscoroutinefunction(method):
                val = await method(*clean_args)
            else:
                val = method(*clean_args)
        except TypeError as e:
            raise LegacyErrorResponse(
                message=f"Server encountered a TypeError "
                f"while running {method} : {e}. "
                f"Possibly a type mismatch in args"
            ).as_error(status.HTTP_400_BAD_REQUEST)
        else:
            return SerialCommandResponse(message="Success", returnValue=val)
    else:
        raise LegacyErrorResponse(
            message=f"Module does not have command: {command.command_type}"
        ).as_error(status.HTTP_400_BAD_REQUEST)


@router.post(
    path="/modules/{serial}/update",
    summary="Initiate a firmware update on a specific module",
    description=(
        "Command robot to flash its bundled firmware file "
        "for this module's type to this specific module"
    ),
    response_model=V1BasicResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": LegacyErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": LegacyErrorResponse},
    },
)
async def post_serial_update(
    serial: str = Path(..., description="Serial number of the module"),
    hardware: HardwareControlAPI = Depends(get_hardware),
) -> V1BasicResponse:
    """Update module firmware"""
    attached_modules = hardware.attached_modules
    matching_module = find_matching_module(serial, attached_modules)

    if not matching_module:
        raise LegacyErrorResponse(message=f"Module {serial} not found").as_error(
            status.HTTP_404_NOT_FOUND
        )

    try:
        if matching_module.bundled_fw:
            await asyncio.wait_for(
                modules.update_firmware(
                    matching_module,
                    matching_module.bundled_fw.path,
                    asyncio.get_event_loop(),
                ),
                100,
            )
            return V1BasicResponse(message=f"Successfully updated module {serial}")
        else:
            res = (
                f"Bundled fw file not found for module of "
                f"type: {matching_module.name()}"
            )
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    except modules.UpdateError as e:
        res = f"Update error: {e}"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    except asyncio.TimeoutError:
        res = "Module not responding"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    raise LegacyErrorResponse(message=res).as_error(status_code)


def find_matching_module(
    serial: str, attached_modules: typing.List[AbstractModule]
) -> typing.Optional[AbstractModule]:
    """
    Given a serial name try to find a matching attached instrument.

    :param serial: Serial number
    :param attached_modules: List of attached modules
    :return: The module if found otherwise None
    """
    if attached_modules:
        for m in attached_modules:
            if m.device_info.get("serial") == serial:
                return m
    return None
