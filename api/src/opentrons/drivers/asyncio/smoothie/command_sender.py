import logging

from opentrons.drivers.asyncio.communication import SerialConnection
from opentrons.drivers.asyncio.smoothie.constants import GCODE, \
    SMOOTHIE_COMMAND_TERMINATOR
from opentrons.drivers.command_builder import CommandBuilder


log = logging.getLogger(__name__)


class SmoothieCommandSender:
    def __init__(self, connection: SerialConnection):
        """
        Construct a smoothie command sender.

        Args:
            connection: The connection to use.
        """
        self._connection = connection

    async def send_command(self, command: CommandBuilder, retries: int = 0) -> str:
        """
        Send a command followed by a wait.
        Args:
            command: The command to send.
            retries: The number of retries.

        Returns: The command response.
        """
        cmd_str = command.build()
        command_result = await self._connection.send_command(
            data=cmd_str, retries=retries
        )

        command_result = self._remove_unwanted_characters(
            command=cmd_str, response=command_result
        )

        wait_command = CommandBuilder(
            terminator=SMOOTHIE_COMMAND_TERMINATOR
        ).add_gcode(
            gcode=GCODE.WAIT
        )

        await self._connection.send_command(
            data=wait_command.build(),
            retries=0
        )

        return command_result

    @staticmethod
    def _remove_unwanted_characters(command: str, response: str) -> str:
        # smoothieware can enter a weird state, where it repeats back
        # the sent command at the beginning of its response.
        # Check for this echo, and strips the command from the response
        def _is_token_command(_s: str) -> bool:
            """check if token is a command"""
            # A single letter token cannot be assumed to be a command.
            # For example: "M369 L" response is "L:2132121212".
            return len(_s) > 1
        # Split at spaces.
        tokens = (c.strip() for c in command.strip().split(' '))
        # A list of commands to remove from response. Including the entire
        # command.
        remove_from_response = [command] + [
            c for c in tokens if _is_token_command(c)
        ]

        # also removing any inadvertent newline/return characters
        # this is ok because all data we need from Smoothie is returned on
        # the first line in the response
        remove_from_response += ['\r', '\n']
        modified_response = str(response)

        for cmd in remove_from_response:
            modified_response = modified_response.replace(cmd, '')

        if modified_response != response:
            log.debug(f'Removed characters from response: {response}')
            log.debug(f'Newly formatted response: {modified_response}')

        return modified_response.strip()
