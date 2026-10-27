from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LocationSummaryDto(BaseModel):
    id: UUID
    name: str


class DeviceCountsDto(BaseModel):
    sensor: int
    actuator: int


class OverviewDeviceDto(BaseModel):
    id: UUID
    device_type: str
    role: str
    display_name: str | None


class OverviewReadingDto(BaseModel):
    device_id: UUID
    value: float
    unit: str
    recorded_at: datetime
    tracking_enabled: bool
    sampling_interval_seconds: int


class OverviewZoneDto(BaseModel):
    id: UUID
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    devices: list[OverviewDeviceDto] = Field(default_factory=list)
    latest_readings: list[OverviewReadingDto] = Field(default_factory=list)


class OverviewRecommendationDto(BaseModel):
    action: str
    reason: str


class LocationOverviewDto(BaseModel):
    location: LocationSummaryDto
    device_counts: DeviceCountsDto
    zones: list[OverviewZoneDto] = Field(default_factory=list)
    strategy_key: str | None = None
    last_recommendation: OverviewRecommendationDto | None = None
