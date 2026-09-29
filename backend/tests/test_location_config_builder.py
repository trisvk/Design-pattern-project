#AI created
import pytest

from domain.locations.config_builder import LocationConfigBuilder
from domain.locations.errors import ConfigurationError


def test_build_success():
    config = (
        LocationConfigBuilder()
        .with_location_name("Test Location")
        .add_zone(
            "Zone 1",
            0.2,
            0.7,
            {"watering": "08:00"},
        )
        .build()
    )

    assert config.location.name == "Test Location"
    assert len(config.zones) == 1
    assert config.zones[0].name == "Zone 1"
    assert config.zones[0].moisture_threshold_low == 0.2
    assert config.zones[0].moisture_threshold_high == 0.7


def test_build_requires_name():
    builder = (
        LocationConfigBuilder()
        .add_zone(
            "Zone 1",
            0.2,
            0.7,
        )
    )

    with pytest.raises(ConfigurationError):
        builder.build()


def test_build_requires_zones():
    builder = (
        LocationConfigBuilder()
        .with_location_name("Test Location")
    )

    with pytest.raises(ConfigurationError):
        builder.build()


@pytest.mark.parametrize(
    "low, high",
    [
        (0.7, 0.3),
        (0.5, 0.5),
        (-0.1, 0.5),
        (0.2, 1.1),
    ],
)
def test_build_rejects_invalid_thresholds(
    low: float,
    high: float,
):
    builder = (
        LocationConfigBuilder()
        .with_location_name("Test Location")
        .add_zone(
            "Zone 1",
            low,
            high,
        )
    )

    with pytest.raises(ConfigurationError):
        builder.build()