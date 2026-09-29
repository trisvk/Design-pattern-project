from uuid import UUID

from pydantic import BaseModel


class ZoneBuildRequestDto(BaseModel):
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict | None = None


class BuildLocationConfigRequestDto(BaseModel):
    location_name: str
    zones: list[ZoneBuildRequestDto]


class ZoneWriteDto(BaseModel):
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict | None = None


class LocationDto(BaseModel):
    id: UUID
    name: str


class ZoneDto(BaseModel):
    id: UUID
    location_id: UUID
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict


class LocationConfigDto(BaseModel):
    location: LocationDto
    zones: list[ZoneDto]