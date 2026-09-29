from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from application.devices.dto import DeviceDto
from application.devices.mappers import devices_to_dtos
from application.locations.config_service import LocationConfigService
from application.locations.dto import (
    BuildLocationConfigRequestDto,
    LocationConfigDto,
    LocationDto,
    ZoneDto,
    ZoneWriteDto,
)
from application.locations.zone_assignment_service import ZoneAssignmentService
from domain.locations.errors import ConfigurationError
from infrastructure.db import get_db
from infrastructure.persistence.location_repository import LocationRepository
from infrastructure.persistence.device_repository import DeviceRepository

router = APIRouter(
    prefix="/api/locations",
    tags=["locations"],
)


def get_service(
    db: Session = Depends(get_db),
) -> LocationConfigService:
    return LocationConfigService(LocationRepository(db))


@router.post(
    "/config",
    response_model=LocationConfigDto,
    status_code=status.HTTP_201_CREATED,
)
def create_config(
    request: BuildLocationConfigRequestDto,
    service: LocationConfigService = Depends(get_service),
):
    try:
        return service.build_and_save(request)
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[LocationDto],
)
def list_locations(
    service: LocationConfigService = Depends(get_service),
):
    return service.list_locations()


@router.get(
    "/{location_id}/config",
    response_model=LocationConfigDto,
)
def get_config(
    location_id: UUID,
    service: LocationConfigService = Depends(get_service),
):
    result = service.get_config(location_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Location not found")

    return result


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_location(
    location_id: UUID,
    service: LocationConfigService = Depends(get_service),
):
    if not service.delete_location(location_id):
        raise HTTPException(status_code=404, detail="Location not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{location_id}/zones",
    response_model=ZoneDto,
    status_code=status.HTTP_201_CREATED,
)
def add_zone(
    location_id: UUID,
    request: ZoneWriteDto,
    service: LocationConfigService = Depends(get_service),
):
    try:
        result = service.add_zone(location_id, request)
    except ConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Location not found")

    return result


@router.patch(
    "/{location_id}/zones/{zone_id}",
    response_model=ZoneDto,
)
def update_zone(
    location_id: UUID,
    zone_id: UUID,
    request: ZoneWriteDto,
    service: LocationConfigService = Depends(get_service),
):
    try:
        result = service.update_zone(location_id, zone_id, request)
    except ConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Zone not found")

    return result


@router.delete(
    "/{location_id}/zones/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_zone(
    location_id: UUID,
    zone_id: UUID,
    service: LocationConfigService = Depends(get_service),
):
    try:
        result = service.delete_zone(location_id, zone_id)
    except ConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Zone not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{location_id}/zones/{zone_id}/devices",
    response_model=list[DeviceDto],
)
def list_zone_devices(
    location_id: UUID,
    zone_id: UUID,
    db: Session = Depends(get_db),
):
    service = ZoneAssignmentService(
        DeviceRepository(db),
        LocationRepository(db),
    )

    devices = service.list_devices(
        location_id,
        zone_id,
    )

    if devices is None:
        raise HTTPException(
            status_code=404,
            detail="Zone not found in this location",
        )

    return devices_to_dtos(devices)