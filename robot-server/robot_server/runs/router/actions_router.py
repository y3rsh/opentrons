"""Router for /runs actions endpoints."""
import logging

from fastapi import APIRouter, Depends, status
from datetime import datetime
from typing import Union
from typing_extensions import Literal

from opentrons.protocol_engine.errors import ProtocolEngineStoppedError

from robot_server.errors import ErrorDetails, ErrorBody
from robot_server.service.dependencies import get_current_time, get_unique_id
from robot_server.service.json_api import RequestModel, SimpleBody, PydanticResponse
from robot_server.service.task_runner import TaskRunner

from ..run_store import RunStore, RunNotFoundError
from ..run_view import RunView
from ..action_models import RunAction, RunActionType, RunActionCreate
from ..engine_store import EngineStore
from ..dependencies import get_run_store, get_engine_store
from .base_router import RunNotFound, RunStopped


log = logging.getLogger(__name__)
actions_router = APIRouter()


class RunActionNotAllowed(ErrorDetails):
    """An error if one tries to issue an unsupported run action."""

    id: Literal["RunActionNotAllowed"] = "RunActionNotAllowed"
    title: str = "Run Action Not Allowed"


@actions_router.post(  # noqa: C901
    path="/runs/{runId}/actions",
    summary="Issue a control action to the run",
    description="Provide an action in order to control execution of the run.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"model": SimpleBody[RunAction]},
        status.HTTP_409_CONFLICT: {
            "model": ErrorBody[Union[RunActionNotAllowed, RunStopped]],
        },
        status.HTTP_404_NOT_FOUND: {"model": ErrorBody[RunNotFound]},
    },
)
async def create_run_action(
    runId: str,
    request_body: RequestModel[RunActionCreate],
    run_view: RunView = Depends(RunView),
    run_store: RunStore = Depends(get_run_store),
    engine_store: EngineStore = Depends(get_engine_store),
    action_id: str = Depends(get_unique_id),
    created_at: datetime = Depends(get_current_time),
    task_runner: TaskRunner = Depends(TaskRunner),
) -> PydanticResponse[SimpleBody[RunAction]]:
    """Create a run control action.

    Arguments:
        runId: Run ID pulled from the URL.
        request_body: Input payload from the request body.
        run_view: Resource model builder.
        run_store: Run storage interface.
        engine_store: Protocol engine and runner storage.
        action_id: Generated ID to assign to the control action.
        created_at: Timestamp to attach to the control action.
        task_runner: Background task runner.
    """
    try:
        prev_run = run_store.get(run_id=runId)
    except RunNotFoundError as e:
        raise RunNotFound(detail=str(e)).as_error(status.HTTP_404_NOT_FOUND)

    if not prev_run.is_current:
        raise RunStopped(detail=f"Run {runId} is not the current run").as_error(
            status.HTTP_409_CONFLICT
        )

    action, next_run = run_view.with_action(
        run=prev_run,
        action_id=action_id,
        action_data=request_body.data,
        created_at=created_at,
    )

    try:
        if action.actionType == RunActionType.PLAY:
            # TODO(mc, 2022-01-11): this won't work very well for HTTP-only
            # runs, which is ok at the time of writing but needs to be addressed
            if engine_store.runner.was_started():
                log.info(f'Resuming run "{runId}".')
                engine_store.runner.play()
            else:
                log.info(f'Starting run "{runId}".')
                task_runner.run(engine_store.runner.run)

        elif action.actionType == RunActionType.PAUSE:
            log.info(f'Pausing run "{runId}".')
            engine_store.runner.pause()

        elif action.actionType == RunActionType.STOP:
            log.info(f'Stopping run "{runId}".')
            task_runner.run(engine_store.runner.stop)

    except ProtocolEngineStoppedError as e:
        raise RunActionNotAllowed(detail=str(e)).as_error(status.HTTP_409_CONFLICT)

    run_store.upsert(run=next_run)

    return await PydanticResponse.create(
        content=SimpleBody.construct(data=action),
        status_code=status.HTTP_201_CREATED,
    )
