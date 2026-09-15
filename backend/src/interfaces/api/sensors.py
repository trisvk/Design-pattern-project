from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.sensor_service import SensorService
from infrastructure.db import get_db
from infrastructure.device_repository import DeviceRepository


router = APIRouter(
    prefix="/api/sensors",
    tags=["sensors"],
)


class SensorCreateRequest(BaseModel):
    type: str
    display_name: str | None = None


class SensorResponse(BaseModel):
    id: UUID
    device_type: str
    display_name: str | None
    default_config: dict


@router.get("", response_model=list[SensorResponse])
def list_sensors(
    db: Session = Depends(get_db),
) -> list[SensorResponse]:
    repo = DeviceRepository(db)
    service = SensorService(repo)

    sensors = service.list_sensors()

    return [
        SensorResponse(
            id=sensor.id,
            device_type=sensor.device_type,
            display_name=sensor.display_name,
            default_config=sensor.default_config,
        )
        for sensor in sensors
    ]


@router.post(
    "",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sensor(
    request: SensorCreateRequest,
    db: Session = Depends(get_db),
) -> SensorResponse:
    repo = DeviceRepository(db)
    service = SensorService(repo)

    try:
        sensor = service.create_sensor(
            sensor_type=request.type,
            display_name=request.display_name,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return SensorResponse(
        id=sensor.id,
        device_type=sensor.device_type,
        display_name=sensor.display_name,
        default_config=sensor.default_config,
    )