from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.devices.dto import (
    AssignZoneRequestDto,
    DeviceDto,
)
from application.devices.family_service import (
    ActuatorNotFoundError,
    DeviceFamilyService,
)
from application.devices.mappers import devices_to_dtos
from application.locations.zone_assignment_service import (
    ZoneAssignmentService,
)
from domain.actuators.state import IllegalTransitionError
from infrastructure.db import get_db
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.location_repository import LocationRepository


router = APIRouter(
    prefix="/api/devices",
    tags=["devices"],
)


class SamplingRequest(BaseModel):
    sampling_interval_seconds: int
    tracking_enabled: bool


class SamplingResponse(BaseModel):
    sampling_interval_seconds: int
    tracking_enabled: bool


class TransitionRequest(BaseModel):
    target: str


class TransitionResponse(BaseModel):
    state: str
    allowed_commands: list[str]


@router.get("", response_model=list[DeviceDto])
def list_devices(
    family: str | None = Query(default=None),
    role: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[DeviceDto]:
    service = DeviceFamilyService(
        DeviceRepository(db),
        ActuatorStateRepository(db),
    )

    return service.list_device_dtos(
        device_family=family,
        role=role,
    )


@router.post(
    "/provision",
    response_model=list[DeviceDto],
    status_code=status.HTTP_201_CREATED,
)
def provision_devices(
    family: str = Query(...),
    db: Session = Depends(get_db),
) -> list[DeviceDto]:
    state_repo = ActuatorStateRepository(db)

    service = DeviceFamilyService(
        DeviceRepository(db),
        state_repo,
    )

    try:
        devices = service.provision_family(family)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    actuator_ids = [
        device.id
        for device in devices
        if device.role == "actuator" and device.id is not None
    ]

    states = state_repo.get_states(actuator_ids)

    return devices_to_dtos(devices, states)


@router.patch(
    "/{id}/zone",
    status_code=status.HTTP_204_NO_CONTENT,
)
def assign_device_zone(
    id: UUID,
    request: AssignZoneRequestDto,
    db: Session = Depends(get_db),
):
    service = ZoneAssignmentService(
        DeviceRepository(db),
        LocationRepository(db),
    )

    success = service.assign(id, request.zone_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Device or zone not found",
        )

    return None


@router.patch(
    "/{device_id}/sampling",
    response_model=SamplingResponse,
)
def update_sampling(
    device_id: UUID,
    body: SamplingRequest,
    db: Session = Depends(get_db),
) -> SamplingResponse:
    if body.sampling_interval_seconds < 5:
        raise HTTPException(
            status_code=400,
            detail="Sampling interval must be at least 5 seconds",
        )

    repo = DeviceRepository(db)

    device = repo.update_sampling(
        device_id,
        body.sampling_interval_seconds,
        body.tracking_enabled,
    )

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )

    return SamplingResponse(
        sampling_interval_seconds=device.sampling_interval_seconds,
        tracking_enabled=device.tracking_enabled,
    )


@router.post(
    "/{device_id}/transition",
    response_model=TransitionResponse,
)
def transition_device(
    device_id: UUID,
    body: TransitionRequest,
    db: Session = Depends(get_db),
) -> TransitionResponse:
    service = DeviceFamilyService(
        DeviceRepository(db),
        ActuatorStateRepository(db),
    )

    try:
        result = service.transition_actuator(
            device_id,
            body.target,
        )

    except ActuatorNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except IllegalTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return TransitionResponse(**result)
