from uuid import UUID

from application.automation.service import AutomationService
from application.overview.dto import (
    DeviceCountsDto,
    LocationOverviewDto,
    LocationSummaryDto,
    OverviewDeviceDto,
    OverviewReadingDto,
    OverviewRecommendationDto,
    OverviewZoneDto,
)
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)


class OverviewNotFoundError(ValueError):
    pass


class LocationOverviewFacade:
    def __init__(
        self,
        repo: AutomationRepository,
        automation_service: AutomationService,
    ):
        self._repo = repo
        self._automation_service = automation_service

    def get_overview(
        self,
        location_id: UUID,
    ) -> LocationOverviewDto:
        location_data = self._repo.get_location_with_zones(
            location_id
        )

        if location_data is None:
            raise OverviewNotFoundError("Location not found")

        location, zones = location_data

        devices = self._repo.get_assigned_devices(location_id)

        latest_readings = (
            self._repo.get_latest_readings_for_devices(
                [device.id for device in devices]
            )
        )

        strategy_key = self._repo.get_strategy_key(
            location_id
        )

        recommendation = None

        if strategy_key is not None:
            result = self._automation_service.evaluate(
                location_id
            )

            recommendation = OverviewRecommendationDto(
                action=result.action,
                reason=result.reason,
            )

        zone_dtos = []

        for zone in zones:
            zone_devices = [
                device
                for device in devices
                if device.zone_id == zone.id
            ]

            device_dtos = [
                OverviewDeviceDto(
                    id=device.id,
                    device_type=device.device_type,
                    role=device.role,
                    display_name=device.display_name,
                )
                for device in zone_devices
            ]

            reading_dtos = []

            for device in zone_devices:
                reading = latest_readings.get(device.id)

                if reading is None:
                    continue

                reading_dtos.append(
                    OverviewReadingDto(
                        device_id=device.id,
                        value=float(reading.value),
                        unit=reading.unit,
                        recorded_at=reading.recorded_at,
                        tracking_enabled=device.tracking_enabled,
                        sampling_interval_seconds=(
                            device.sampling_interval_seconds
                        ),
                    )
                )

            zone_dtos.append(
                OverviewZoneDto(
                    id=zone.id,
                    name=zone.name,
                    moisture_threshold_low=float(
                        zone.moisture_threshold_low
                    ),
                    moisture_threshold_high=float(
                        zone.moisture_threshold_high
                    ),
                    devices=device_dtos,
                    latest_readings=reading_dtos,
                )
            )

        return LocationOverviewDto(
            location=LocationSummaryDto(
                id=location.id,
                name=location.name,
            ),
            device_counts=DeviceCountsDto(
                sensor=sum(
                    device.role == "sensor"
                    for device in devices
                ),
                actuator=sum(
                    device.role == "actuator"
                    for device in devices
                ),
            ),
            zones=zone_dtos,
            strategy_key=strategy_key,
            last_recommendation=recommendation,
        )
