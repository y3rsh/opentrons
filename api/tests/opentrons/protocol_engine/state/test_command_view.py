"""Labware state store tests."""
import pytest
from collections import OrderedDict
from typing import List, NamedTuple, Sequence, Tuple

from opentrons.protocol_engine import EngineStatus, commands as cmd, errors
from opentrons.protocol_engine.state.commands import CommandState, CommandView


from .command_fixtures import (
    create_pending_command,
    create_running_command,
    create_failed_command,
    create_completed_command,
)


def get_command_view(
    is_running: bool = False,
    is_stopped: bool = False,
    commands_by_id: Sequence[Tuple[str, cmd.Command]] = (),
) -> CommandView:
    """Get a command view test subject."""
    state = CommandState(
        is_running=is_running,
        is_stopped=is_stopped,
        commands_by_id=OrderedDict(commands_by_id),
    )

    return CommandView(state=state)


def test_get_by_id() -> None:
    """It should get a command by ID from state."""
    command = create_completed_command(command_id="command-id")
    subject = get_command_view(commands_by_id=[("command-id", command)])

    assert subject.get("command-id") == command


def test_get_command_bad_id() -> None:
    """It should raise if a requested command ID isn't in state."""
    command = create_completed_command(command_id="command-id")
    subject = get_command_view(commands_by_id=[("command-id", command)])

    with pytest.raises(errors.CommandDoesNotExistError):
        subject.get("asdfghjkl")


def test_get_all() -> None:
    """It should get all the commands from the state."""
    command_1 = create_completed_command(command_id="command-id-1")
    command_2 = create_running_command(command_id="command-id-2")
    command_3 = create_pending_command(command_id="command-id-3")

    subject = get_command_view(
        commands_by_id=[
            ("command-id-1", command_1),
            ("command-id-2", command_2),
            ("command-id-3", command_3),
        ]
    )

    assert subject.get_all() == [command_1, command_2, command_3]


def test_get_next_queued_returns_first_pending() -> None:
    """It should return the first command that's pending."""
    pending_command = create_pending_command()
    running_command = create_running_command()
    completed_command = create_completed_command()

    subject = get_command_view(
        is_running=True,
        commands_by_id=[
            ("command-id-1", running_command),
            ("command-id-2", completed_command),
            ("command-id-3", pending_command),
            ("command-id-4", pending_command),
        ],
    )

    assert subject.get_next_queued() == "command-id-3"


def test_get_next_queued_returns_none_when_no_pending() -> None:
    """It should return None if there are no pending commands to return."""
    running_command = create_running_command(command_id="command-id-1")
    completed_command = create_completed_command(command_id="command-id-2")
    failed_command = create_failed_command(command_id="command-id-3")

    subject = get_command_view()

    assert subject.get_next_queued() is None

    subject = get_command_view(
        is_running=True,
        commands_by_id=[
            ("command-id-1", running_command),
            ("command-id-2", completed_command),
            ("command-id-3", failed_command),
        ],
    )

    assert subject.get_next_queued() is None


def test_get_next_queued_returns_none_when_earlier_command_failed() -> None:
    """It should return None if any prior-added command is failed."""
    running_command = create_running_command(command_id="command-id-1")
    completed_command = create_completed_command(command_id="command-id-2")
    failed_command = create_failed_command(command_id="command-id-3")
    pending_command = create_pending_command(command_id="command-id-4")

    subject = get_command_view(
        is_running=True,
        commands_by_id=[
            ("command-id-1", running_command),
            ("command-id-2", completed_command),
            ("command-id-3", failed_command),
            ("command-id-4", pending_command),
        ],
    )

    assert subject.get_next_queued() is None


def test_get_next_queued_returns_none_if_stopped() -> None:
    """It should return None if the engine is not running."""
    pending_command = create_pending_command(command_id="command-id-1")

    subject = get_command_view(
        is_running=False,
        commands_by_id=[
            ("command-id-1", pending_command),
        ],
    )

    assert subject.get_next_queued() is None


def test_get_is_complete() -> None:
    """It should be able to tell if a command is complete."""
    completed_command = create_completed_command(command_id="command-id-1")
    running_command = create_running_command(command_id="command-id-2")
    pending_command = create_pending_command(command_id="command-id-3")

    subject = get_command_view(
        commands_by_id=[
            ("command-id-1", completed_command),
            ("command-id-2", running_command),
            ("command-id-3", pending_command),
        ]
    )

    assert subject.get_is_complete("command-id-1") is True
    assert subject.get_is_complete("command-id-2") is False
    assert subject.get_is_complete("command-id-3") is False


def test_get_is_complete_with_failed_command() -> None:
    """It should return true if a given command will never be executed."""
    failed_command = create_failed_command(command_id="command-id-1")
    pending_command = create_pending_command(command_id="command-id-2")

    subject = get_command_view(
        commands_by_id=[
            ("command-id-1", failed_command),
            ("command-id-2", pending_command),
        ]
    )

    assert subject.get_is_complete("command-id-1") is True
    assert subject.get_is_complete("command-id-2") is True


def test_get_is_complete_with_all_commands() -> None:
    """It should check whether all commands are completed if no command is specified."""
    completed_command = create_completed_command(command_id="command-id-1")
    running_command = create_running_command(command_id="command-id-2")
    pending_command = create_pending_command(command_id="command-id-3")
    failed_command = create_failed_command(command_id="command-id-4")

    subject = get_command_view(
        commands_by_id=[
            ("command-id-4", failed_command),
            ("command-id-2", pending_command),
        ]
    )

    assert subject.get_is_complete() is True

    subject = get_command_view(
        commands_by_id=[
            ("command-id-1", completed_command),
            ("command-id-2", running_command),
        ]
    )

    assert subject.get_is_complete() is False

    subject = get_command_view(
        commands_by_id=[
            ("command-id-1", completed_command),
            ("command-id-2", completed_command),
        ]
    )

    assert subject.get_is_complete() is True


class GetStatusSpec(NamedTuple):
    """Spec data for get_status tests."""

    subject: CommandView
    expected_status: EngineStatus


get_status_specs: List[GetStatusSpec] = [
    GetStatusSpec(
        subject=get_command_view(is_running=False, is_stopped=False, commands_by_id=[]),
        expected_status=EngineStatus.READY_TO_START,
    ),
    GetStatusSpec(
        subject=get_command_view(
            is_running=False,
            is_stopped=False,
            commands_by_id=[("command-id", create_pending_command())],
        ),
        expected_status=EngineStatus.READY_TO_START,
    ),
    GetStatusSpec(
        subject=get_command_view(
            is_running=False,
            is_stopped=False,
            commands_by_id=[("command-id", create_running_command())],
        ),
        expected_status=EngineStatus.PAUSED,
    ),
    GetStatusSpec(
        subject=get_command_view(
            is_running=True,
            is_stopped=False,
            commands_by_id=[],
        ),
        expected_status=EngineStatus.RUNNING,
    ),
    GetStatusSpec(
        subject=get_command_view(
            is_running=True,
            is_stopped=False,
            commands_by_id=[("command-id", create_failed_command())],
        ),
        expected_status=EngineStatus.FAILED,
    ),
    GetStatusSpec(
        subject=get_command_view(
            is_running=False,
            is_stopped=False,
            commands_by_id=[("command-id", create_failed_command())],
        ),
        expected_status=EngineStatus.FAILED,
    ),
    GetStatusSpec(
        subject=get_command_view(
            is_running=False,
            is_stopped=True,
            commands_by_id=[("command-id", create_failed_command())],
        ),
        expected_status=EngineStatus.FAILED,
    ),
    GetStatusSpec(
        subject=get_command_view(
            is_running=False,
            is_stopped=True,
            commands_by_id=[],
        ),
        expected_status=EngineStatus.SUCCEEDED,
    ),
]


@pytest.mark.parametrize(GetStatusSpec._fields, get_status_specs)
def test_get_status(subject: CommandView, expected_status: EngineStatus) -> None:
    """It should set a status according to the command queue and running flag.

    1. Not running, not done, only queued commands: READY_TO_START
    2. Not running, not done, with commands: PAUSED
    3. Running, not done, no failed commands: RUNNING
    4. Any failed commands: FAILED
    5. Done, no failed commands: SUCCEEDED
    """
    assert subject.get_status() == expected_status
