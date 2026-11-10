from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from domain.actuators.ports import ActuatorPort, PolicyViolationError
from infrastructure.adapters.actuators.logging_decorator import LoggingActuatorDecorator
from infrastructure.adapters.actuators.max_runtime_decorator import MaxRunTimeActuatorDecorator
from infrastructure.adapters.actuators.simulation import SimulationActuatorAdapter
from infrastructure.db import get_db
from infrastructure.persistence.actuator_state_repository import ActuatorStateRepository
from infrastructure.persistence.execution_log_repository import ExecutionLogRepository


router = APIRouter(prefix="/api/actuators", tags=["actuators"])


class ExecutionDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_id: UUID
    success: bool
    policy_applied: list[str]
    message: str | None
    created_at: datetime


class ApplyRequest(BaseModel):
    command: str
    payload: dict = Field(default_factory=dict)


def build_actuator_port(
    state_repo: ActuatorStateRepository,
    log_repo: ExecutionLogRepository,
) -> ActuatorPort:
    # Order: logging (outermost) -> maxRunTime -> simulation (innermost)
    return LoggingActuatorDecorator(
        MaxRunTimeActuatorDecorator(SimulationActuatorAdapter(), state_repo),
        log_repo,
    )


@router.get("/executions", response_model=list[ExecutionDto])
def list_executions(
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[ExecutionDto]:
    rows = ExecutionLogRepository(db).list_recent(limit)
    return [ExecutionDto.model_validate(row) for row in rows]


@router.post(
    "/{device_id}/apply",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Apply a command to an actuator",
    description="Runs the command through the decorated actuator port "
                "(logging → max run time → simulation). Every attempt is "
                "written to the execution log.",
    responses={404: {"description": "Actuator not found"},
               409: {"description": "Blocked by policy (max run time exceeded)"}},
)
def apply_command(
    device_id: UUID,
    body: ApplyRequest,
    db: Session = Depends(get_db),
) -> None:
    state_repo = ActuatorStateRepository(db)

    if not state_repo.actuator_exists(device_id):
        raise HTTPException(status_code=404, detail="Actuator not found")

    port = build_actuator_port(state_repo, ExecutionLogRepository(db))

    try:
        port.apply(device_id, body.command, body.payload)
    except PolicyViolationError as exc:
        raise HTTPException(status_code=409, detail=exc.message) from exc

    return None