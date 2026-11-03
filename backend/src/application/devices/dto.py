from uuid import UUID

from pydantic import BaseModel, Field


class DeviceDto(BaseModel):
    id: UUID
    device_type: str
    role: str
    device_family: str
    display_name: str | None
    default_config: dict

    state: str | None = None
    allowed_commands: list[str] = Field(default_factory=list)


class AssignZoneRequestDto(BaseModel):
    zone_id: UUID | None
