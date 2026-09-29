from uuid import UUID

from pydantic import BaseModel

from domain.devices.entity import Device


class DeviceDto(BaseModel):
    id: UUID
    device_type: str
    role: str
    device_family: str
    display_name: str | None
    default_config: dict

class AssignZoneRequestDto(BaseModel):
    zone_id: UUID | None