import opentrons.drivers.asyncio.smoothie.constants
import pytest
from mock import AsyncMock, call
from opentrons.drivers.asyncio.communication import SerialConnection
from opentrons.drivers.asyncio.smoothie import driver
from opentrons.drivers.asyncio.smoothie.command_sender import SmoothieCommandSender
from opentrons.drivers.command_builder import CommandBuilder


@pytest.fixture
def mock_serial_connection() -> AsyncMock:
    """Mock serial connection."""
    return AsyncMock(spec=SerialConnection)


@pytest.fixture
def subject(mock_serial_connection: AsyncMock) -> SmoothieCommandSender:
    """The test subject."""
    return SmoothieCommandSender(connection=mock_serial_connection)


@pytest.fixture
def command() -> CommandBuilder:
    """A command fixture"""
    return CommandBuilder(
        terminator=opentrons.drivers.asyncio.smoothie.constants.SMOOTHIE_COMMAND_TERMINATOR
    ).add_gcode(
        "M123"
    ).add_int(
        "F", 2
    )


async def test_command_sender_calls_commands(
        subject: SmoothieCommandSender, mock_serial_connection: AsyncMock, command: CommandBuilder
) -> None:
    """It should send the requested command followed by a wait."""
    await subject.send_command(command=command, retries=3)

    assert mock_serial_connection.send_command.call_args_list == [
        call(data=command.build(), retries=3),
        call(data=CommandBuilder(
            terminator=opentrons.drivers.asyncio.smoothie.constants.SMOOTHIE_COMMAND_TERMINATOR
        ).add_gcode(
            opentrons.drivers.asyncio.smoothie.constants.GCODE.WAIT
        ).build(), retries=0)
    ]


async def test_command_sender_returns_result(
        subject: SmoothieCommandSender, mock_serial_connection: AsyncMock, command: CommandBuilder
) -> None:
    """It should return the result of command."""
    mock_serial_connection.send_command.side_effect = [
        "a", "b"
    ]

    result = await subject.send_command(command=command, retries=3)
    assert result == "a"


async def test_command_sender_sanitized_response(
        subject: SmoothieCommandSender,
        mock_serial_connection: AsyncMock,
        command: CommandBuilder
) -> None:
    """It should return sanitized result."""
    mock_serial_connection.send_command.side_effect = [
        f"{command.build()}\r\n  a  \r\n",
        "b"
    ]

    result = await subject.send_command(command=command, retries=3)
    assert result == "a"


@pytest.mark.parametrize(
    argnames=["cmd", "resp", "expected"],
    argvalues=[
        # Remove command from response
        ["G28.2B", "G28.2B", ""],
        ["G28.2B G1", "G28.2B G1", ""],
        ["G28.2B G1", "G1G28.2BG1", ""],
        # Remove command and whitespace from response
        ["\r\nG52\r\n\r\n", "\r\nG52\r\n\r\n", ""],
        ["\r\nG52\r\n\r\nsome-data\r\nok\r\n",
         "\r\nG52\r\n\r\nsome-data\r\nok\r\nTESTS-RULE",
         "TESTS-RULE"
         ],
        ["\r\nG52\r\n\r\nsome-data\r\nok\r\n",
         "G52\r\n\r\nsome-data\r\nokT\r\nESTS-RULE",
         "TESTS-RULE"],
        # L is not a command echo but a token
        ["M371 L \r\n\r\n",
         "L:703130",
         "L:703130"],
        # R is not a command echo but a token
        ["M3 R \r\n\r\n",
         "M3R:703130",
         "R:703130"],
        ["M369 L \r\n\r\n",
         "M369 L \r\n\r\nL:5032304D56323032303230303432323036000000000000000000000000000000",  # noqa: E501
         "L:5032304D56323032303230303432323036000000000000000000000000000000"]
    ]
)
def test_remove_serial_echo(
        cmd: str, resp: str, expected: str):
    """It should remove unwanted characters only."""
    res = SmoothieCommandSender._remove_unwanted_characters(
        cmd, resp)
    assert res == expected
