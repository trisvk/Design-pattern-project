from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.readings.dto import ReadingDto
from application.readings.service import ReadingIngest
from application.sensor_service import SensorService
from infrastructure.db import get_db
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.reading_repository import ReadingRepository


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

def get_reading_ingest(
    db: Session = Depends(get_db),
) -> ReadingIngest:
    return ReadingIngest(DeviceRepository(db), ReadingRepository(db))


@router.post(
    "/{device_id}/read",
    response_model=ReadingDto,
)
def take_reading(
    device_id: UUID,
    ingest: ReadingIngest = Depends(get_reading_ingest),
) -> ReadingDto:
    try:
        return ingest.take_reading(device_id)

    except LookupError:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.get(
    "/{device_id}/readings",
    response_model=list[ReadingDto],
)
def list_readings(
    device_id: UUID,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    ingest: ReadingIngest = Depends(get_reading_ingest),
) -> list[ReadingDto]:
    try:
        return ingest.list_readings(
            device_id,
            limit,
        )

    except LookupError:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )