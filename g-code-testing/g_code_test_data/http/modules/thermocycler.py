from functools import partial
from g_code_test_data.http.http_settings import HTTP_SETTINGS, S3_BASE
from g_code_test_data.g_code_configuration import HTTPGCodeConfirmConfig
from robot_server.service.legacy.routers.modules import post_serial_command
from robot_server.service.legacy.models.modules import SerialCommand


THERMOCYCLER_CLOSE = HTTPGCodeConfirmConfig(
        name='thermocycler_close',
        s3_path=f"{S3_BASE}/thermocycler_close.txt",
        executable=partial(
            post_serial_command,
            command=SerialCommand(command_type='close'),
            serial=HTTP_SETTINGS.thermocycler.serial_number,
        ),
        settings=HTTP_SETTINGS,
    )

THERMOCYCLER_OPEN = HTTPGCodeConfirmConfig(
        name='thermocycler_open',
        s3_path=f"{S3_BASE}/thermocycler_open.txt",
        executable=partial(
            post_serial_command,
            command=SerialCommand(command_type='open'),
            serial=HTTP_SETTINGS.thermocycler.serial_number,
        ),
        settings=HTTP_SETTINGS,
    )

THERMOCYCLER_DEACTIVATE = HTTPGCodeConfirmConfig(
        name='thermocycler_deactivate',
        s3_path=f"{S3_BASE}/thermocycler_deactivate.txt",
        executable=partial(
            post_serial_command,
            command=SerialCommand(command_type='deactivate'),
            serial=HTTP_SETTINGS.thermocycler.serial_number,
        ),
        settings=HTTP_SETTINGS,
    )

THERMOCYCLER_DEACTIVATE_BLOCK = HTTPGCodeConfirmConfig(
        name='thermocycler_deactivate_block',
        s3_path=f"{S3_BASE}/thermocycler_deactivate_block.txt",
        executable=partial(
            post_serial_command,
            command=SerialCommand(command_type='deactivate_block'),
            serial=HTTP_SETTINGS.thermocycler.serial_number,
        ),
        settings=HTTP_SETTINGS,
    )

THERMOCYCLER_DEACTIVATE_LID = HTTPGCodeConfirmConfig(
        name='thermocycler_deactivate_lid',
        s3_path=f"{S3_BASE}/thermocycler_deactivate_lid.txt",
        executable=partial(
            post_serial_command,
            command=SerialCommand(command_type='deactivate_lid'),
            serial=HTTP_SETTINGS.thermocycler.serial_number,
        ),
        settings=HTTP_SETTINGS,
    )

THERMOCYCLER_CYCLE_TEMPERATURES = HTTPGCodeConfirmConfig(
        name='thermocycler_cycle_temperatures',
        s3_path=f"{S3_BASE}/thermocycler_cycle_temperatures.txt",
        executable=partial(
            post_serial_command,
            command=SerialCommand(
                command_type='cycle_temperatures', args=[
                    [{'temperature': 1.0}, {'temperature': 2.0}, {'temperature': 1.0}]
                    , 1
                ]
            ),
            serial=HTTP_SETTINGS.thermocycler.serial_number,
        ),
        settings=HTTP_SETTINGS,
    )

THERMOCYCLER_SET_LID_TEMPERATURE = HTTPGCodeConfirmConfig(
        name='thermocycler_set_lid_temperature',
        s3_path=f"{S3_BASE}/thermocycler_set_lid_temperature.txt",
        executable=partial(
            post_serial_command,
            command=SerialCommand(command_type='set_lid_temperature', args=[37.0]),
            serial=HTTP_SETTINGS.thermocycler.serial_number,
        ),
        settings=HTTP_SETTINGS,
    )

THERMOCYCLER_SET_TEMPERATURE = HTTPGCodeConfirmConfig(
        name='thermocycler_set_temperature',
        s3_path=f"{S3_BASE}/thermocycler_set_temperature.txt",
        executable=partial(
            post_serial_command,
            command=SerialCommand(command_type='set_temperature', args=[1.0]),
            serial=HTTP_SETTINGS.thermocycler.serial_number,
        ),
        settings=HTTP_SETTINGS,
    )

THERMOCYCLER_CONFIGURATIONS = [
    THERMOCYCLER_CLOSE,
    THERMOCYCLER_OPEN,
    THERMOCYCLER_DEACTIVATE,
    THERMOCYCLER_DEACTIVATE_BLOCK,
    THERMOCYCLER_DEACTIVATE_LID,
    THERMOCYCLER_CYCLE_TEMPERATURES,
    THERMOCYCLER_SET_LID_TEMPERATURE,
    THERMOCYCLER_SET_TEMPERATURE,
]