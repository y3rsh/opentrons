from dataclasses import asdict
from datetime import datetime

from opentrons.protocol_engine import ProtocolEngine
from opentrons.protocol_engine.commands import LoadLabwareResult

from robot_server.service.session.models import session as models
from robot_server.service.session.command_execution import CommandQueue, \
    CommandExecutor
from robot_server.service.session.configuration import SessionConfiguration
from robot_server.service.session.session_types import BaseSession, \
    SessionMetaData
from robot_server.service.session.session_types.live_protocol.command_executor import LiveProtocolCommandExecutor    # noqa: E501


class LiveProtocolSession(BaseSession):

    def __init__(self,
                 configuration: SessionConfiguration,
                 instance_meta: SessionMetaData,
                 protocol_engine: ProtocolEngine):
        """Constructor"""
        super(self.__class__, self).__init__(configuration, instance_meta)

        self._protocol_engine = protocol_engine
        self._executor = LiveProtocolCommandExecutor(
            protocol_engine=protocol_engine
        )

    @classmethod
    async def create(cls,
                     configuration: SessionConfiguration,
                     instance_meta: SessionMetaData) -> 'LiveProtocolSession':
        await configuration.hardware.home()
        return LiveProtocolSession(
            configuration=configuration,
            instance_meta=instance_meta,
            protocol_engine=await ProtocolEngine.create(configuration.hardware)
        )

    @property
    def command_executor(self) -> CommandExecutor:
        return self._executor

    @property
    def command_queue(self) -> CommandQueue:
        pass

    @property
    def session_type(self) -> models.SessionType:
        return models.SessionType.live_protocol

    def get_response_model(self) -> models.LiveProtocolResponseAttributes:
        def make_json_friendly(i):
            if isinstance(i, datetime):
                return str(i)
            return i
        commands = [
            {
                "commandId": v[0],
                "command": {k: make_json_friendly(v) for k, v in asdict(v[1]).items()}
            }
            for v in sorted(
                self._protocol_engine.state_store.commands.get_all_commands(),
                key=lambda t: t[1].created_at)
        ]
        labware = [
            {
                "labwareId": labware_id,
                "definition": labware_data.definition,
                "location": labware_data.location,
            }
            for labware_id, labware_data in self._protocol_engine.state_store.labware.get_all_labware()
        ]
        pipettes = [
            {"pipetteId": pipette_id,
             "mount": pipette_data.mount.name,
             "name": pipette_data.pipette_name,
             } for pipette_id, pipette_data in self._protocol_engine.state_store.pipettes.get_all_pipettes()
        ]

        return models.LiveProtocolResponseAttributes(
            id=self.meta.identifier,
            createdAt=self.meta.created_at,
            createParams=self.meta.create_params,
            details=models.LiveProtocolSessionDetails(
                commands=commands,
                labware=labware,
                pipettes=pipettes,
            )
        )
