"""Synchronous ProtocolEngine client module."""
from uuid import uuid4
from typing import cast

from .. import commands
from ..state import StateView
from ..types import DeckSlotLocation
from .transports import AbstractSyncTransport


class SyncClient:
    """Synchronously interact with a `ProtocolEngine`.

    A `ProtocolEngine` normally provides an ``async`` interface for executing
    commands. This class wraps that with a synchronous interface. Each
    method blocks until the underlying command completes and returns a result,
    or raises an exception if the underlying command has an error.

    In the future, this class could also abstract away stuff like running
    the `ProtocolEngine` in a separate process.
    """

    def __init__(self, transport: AbstractSyncTransport) -> None:
        """Initialize the client with a transport."""
        self._transport = transport

    @property
    def state(self) -> StateView:
        """Get a view of the engine's state."""
        return self._transport.state

    @staticmethod
    def _create_command_id() -> str:
        return str(uuid4())

    def load_labware(
        self,
        location: DeckSlotLocation,
        load_name: str,
        namespace: str,
        version: int,
    ) -> commands.LoadLabwareResult:
        """Execute a ``LoadLabwareRequest``, returning the result."""
        request = commands.LoadLabwareRequest(
            location=location,
            loadName=load_name,
            namespace=namespace,
            version=version,
        )
        result = self._transport.execute_command(
            request=request,
            command_id=self._create_command_id(),
        )

        return cast(commands.LoadLabwareResult, result)
    
    def aspirate(
        self,
        volume: float,
        rate: float,
    ) -> commands.AspirateResult:
        """Execute an ``AspirateRequest``, returning the result."""
        request = commands.AspirateRequest(
            pipetteId="?????",  # fix before merge
            labwareId="?????",  # fix before merge
            wellName="?????",  # fix before merge
            wellLocation="?????", # fix before merge
            volume=volume,
        )
        # Fix before merge: AspirateRequest needs to take a rate?
        result = self._transport.execute_command(
            request=request,
            command_id=self._create_command_id()
        )
        
        # Fix before merge:
        # Is this right? Copies the load_labware() implementation, but
        # is a FailedAspirateResult still an AspirateResult?
        # What forces the caller to check for command failure? Are they meant
        # to do an isinstance() check? Should we raise an exception?
        return cast(commands.AspirateResult, result)
