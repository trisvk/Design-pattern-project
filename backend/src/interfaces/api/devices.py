from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from application.devices.dto import DeviceDto
from application.devices.dto import AssignZoneRequestDto
from application.devices.family_service import DeviceFamilyService
from application.devices.mappers import devices_to_dtos
from application.locations.zone_assignment_service import ZoneAssignmentService
from infrastructure.db import get_db
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


@router.get("", response_model=list[DeviceDto])
def list_devices(
    family: str | None = Query(default=None),
    role: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[DeviceDto]:
    repo = DeviceRepository(db)
    service = DeviceFamilyService(repo)

    devices = service.list_devices(
        device_family=family,
        role=role,
    )

    return devices_to_dtos(devices)


@router.post(
    "/provision",
    response_model=list[DeviceDto],
    status_code=status.HTTP_201_CREATED,
)
def provision_devices(
    family: str = Query(...),
    db: Session = Depends(get_db),
) -> list[DeviceDto]:
    repo = DeviceRepository(db)
    service = DeviceFamilyService(repo)

    try:
        devices = service.provision_family(family)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return devices_to_dtos(devices)

@router.patch("/{id}/zone", status_code=status.HTTP_204_NO_CONTENT)
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
        sampling_interval_seconds=(
            device.sampling_interval_seconds
        ),
        tracking_enabled=device.tracking_enabled,
    )

