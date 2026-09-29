from domain.locations.entity import Location, LocationConfig, Zone
from domain.locations.errors import ConfigurationError


class LocationConfigBuilder:
    def __init__(self):
        self._location_name: str | None = None
        self._zones: list[Zone] = []

    def with_location_name(self, name: str) -> "LocationConfigBuilder":
        self._location_name = name
        return self

    def add_zone(
        self,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict | None = None,
    ) -> "LocationConfigBuilder":
        self._zones.append(
            Zone(
                id=None,
                name=name,
                moisture_threshold_low=moisture_threshold_low,
                moisture_threshold_high=moisture_threshold_high,
                schedule=schedule or {},
            )
        )
        return self

    def build(self) -> LocationConfig:
        if not self._location_name or not self._location_name.strip():
            raise ConfigurationError("Location name cannot be empty")

        if not self._zones:
            raise ConfigurationError("Location must have at least one zone")

        for zone in self._zones:
            if not zone.name or not zone.name.strip():
                raise ConfigurationError("Zone name cannot be empty")

            if not 0 <= zone.moisture_threshold_low <= 1:
                raise ConfigurationError(
                    "Moisture threshold low must be between 0 and 1"
                )

            if not 0 <= zone.moisture_threshold_high <= 1:
                raise ConfigurationError(
                    "Moisture threshold high must be between 0 and 1"
                )

            if zone.moisture_threshold_low >= zone.moisture_threshold_high:
                raise ConfigurationError(
                    "Moisture threshold low must be lower than high"
                )

        return LocationConfig(
            location=Location(
                id=None,
                name=self._location_name.strip(),
            ),
            zones=tuple(self._zones),
        )