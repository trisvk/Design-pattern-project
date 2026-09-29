from uuid import UUID

from application.locations.dto import (
    BuildLocationConfigRequestDto,
    LocationConfigDto,
    LocationDto,
    ZoneDto,
    ZoneWriteDto,
)
from application.locations.mappers import location_config_to_dto
from domain.locations.config_builder import LocationConfigBuilder
from domain.locations.errors import ConfigurationError
from infrastructure.persistence.location_repository import LocationRepository


class LocationConfigService:
    def __init__(self, repo: LocationRepository):
        self._repo = repo

    def build_and_save(
        self,
        request: BuildLocationConfigRequestDto,
    ) -> LocationConfigDto:
        builder = LocationConfigBuilder().with_location_name(
            request.location_name
        )

        for zone in request.zones:
            builder.add_zone(
                name=zone.name,
                moisture_threshold_low=zone.moisture_threshold_low,
                moisture_threshold_high=zone.moisture_threshold_high,
                schedule=zone.schedule,
            )

        config = builder.build()
        location_row, zone_rows = self._repo.save_config(config)

        return location_config_to_dto(location_row, zone_rows)

    def list_locations(self) -> list[LocationDto]:
        return [
            LocationDto(id=row.id, name=row.name)
            for row in self._repo.list_locations()
        ]

    def get_config(self, location_id: UUID) -> LocationConfigDto | None:
        result = self._repo.get_config(location_id)

        if result is None:
            return None

        location_row, zone_rows = result
        return location_config_to_dto(location_row, zone_rows)

    def delete_location(self, location_id: UUID) -> bool:
        return self._repo.delete_location(location_id)

    @staticmethod
    def _validate_zone(request: ZoneWriteDto) -> None:
        if not request.name.strip():
            raise ConfigurationError("Zone name cannot be empty")

        if not 0 <= request.moisture_threshold_low <= 1:
            raise ConfigurationError(
                "Moisture threshold low must be between 0 and 1"
            )

        if not 0 <= request.moisture_threshold_high <= 1:
            raise ConfigurationError(
                "Moisture threshold high must be between 0 and 1"
            )

        if request.moisture_threshold_low >= request.moisture_threshold_high:
            raise ConfigurationError(
                "Moisture threshold low must be lower than high"
            )

    def add_zone(
        self,
        location_id: UUID,
        request: ZoneWriteDto,
    ) -> ZoneDto | None:
        self._validate_zone(request)

        row = self._repo.add_zone(
            location_id,
            name=request.name.strip(),
            moisture_threshold_low=request.moisture_threshold_low,
            moisture_threshold_high=request.moisture_threshold_high,
            schedule=request.schedule or {},
        )

        if row is None:
            return None

        return ZoneDto(
            id=row.id,
            location_id=row.location_id,
            name=row.name,
            moisture_threshold_low=float(row.moisture_threshold_low),
            moisture_threshold_high=float(row.moisture_threshold_high),
            schedule=row.schedule,
        )

    def update_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
        request: ZoneWriteDto,
    ) -> ZoneDto | None:
        self._validate_zone(request)

        zone = self._repo.get_zone(location_id, zone_id)

        if zone is None:
            return None

        row = self._repo.update_zone(
            zone,
            name=request.name.strip(),
            moisture_threshold_low=request.moisture_threshold_low,
            moisture_threshold_high=request.moisture_threshold_high,
            schedule=request.schedule or {},
        )

        return ZoneDto(
            id=row.id,
            location_id=row.location_id,
            name=row.name,
            moisture_threshold_low=float(row.moisture_threshold_low),
            moisture_threshold_high=float(row.moisture_threshold_high),
            schedule=row.schedule,
        )

    def delete_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> bool | None:
        zone = self._repo.get_zone(location_id, zone_id)

        if zone is None:
            return None

        if self._repo.count_zones(location_id) <= 1:
            raise ConfigurationError(
                "Cannot delete the last zone"
            )

        self._repo.delete_zone(zone)
        return True