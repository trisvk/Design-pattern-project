from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from application.commands.dto import CommandLogDto, CommandRequestDto
from application.commands.service import CommandService
from application.devices.family_service import ActuatorNotFoundError
from domain.commands.invoker import UnknownCommandError
from infrastructure.db import get_db
from infrastructure.persistence.actuator_state_repository import ActuatorStateRepository
from infrastructure.persistence.command_log_repository import CommandLogRepository
from infrastructure.persistence.execution_log_repository import ExecutionLogRepository


router = APIRouter(prefix="/api/commands", tags=["commands"])


def get_command_service(db: Session = Depends(get_db)) -> CommandService:
    return CommandService(
        ActuatorStateRepository(db),
        CommandLogRepository(db),
        ExecutionLogRepository(db),
    )


@router.post(
    "",
    response_model=CommandLogDto,
    summary="Execute a command on an actuator",
    description="200 = success or failed (log row). 409 = rejected by state (log row). "
                "400 = unknown command type (no row). 404 = device missing or not an actuator.",
    responses={
        400: {"description": "Unknown command type"},
        404: {"description": "Actuator not found"},
        409: {"model": CommandLogDto, "description": "Rejected: not allowed in current state"},
    },
)
def submit_command(
    body: CommandRequestDto,
    service: CommandService = Depends(get_command_service),
):
    try:
        result = service.submit(body)
    except ActuatorNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UnknownCommandError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result.status == "rejected":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(result),
        )

    return result


@router.get("", response_model=list[CommandLogDto], summary="List command history")
def list_commands(
    limit: int = Query(default=50, ge=1, le=200),
    service: CommandService = Depends(get_command_service),
) -> list[CommandLogDto]:
    return service.list_history(limit)
