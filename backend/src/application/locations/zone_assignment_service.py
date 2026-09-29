from uuid import UUID

from domain.devices.entity import Device
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.location_repository import LocationRepository


class ZoneAssignmentService:
    def __init__(
        self,
        device_repo: DeviceRepository,
        location_repo: LocationRepository,
    ):
        self._device_repo = device_repo
        self._location_repo = location_repo

    def assign(
        self,
        device_id: UUID,
        zone_id: UUID | None,
    ) -> bool:
        device = self._device_repo.get_device_row(device_id)

        if device is None:
            return False

        # null means unassign
        if zone_id is None:
            self._device_repo.assign_zone(
                device,
                zone_id=None,
                location_id=None,
            )
            return True

        zone = self._location_repo.get_zone_by_id(zone_id)

        if zone is None:
            return False

        # Copy location_id from the zone.
        self._device_repo.assign_zone(
            device,
            zone_id=zone.id,
            location_id=zone.location_id,
        )

        return True

    def list_devices(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> list[Device] | None:
        zone = self._location_repo.get_zone(
            location_id,
            zone_id,
        )

        # Also handles "zone not in this location".
        if zone is None:
            return None

        return self._device_repo.list_devices_in_zone(
            location_id,
            zone_id,
        )