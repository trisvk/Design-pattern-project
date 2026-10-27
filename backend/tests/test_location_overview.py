from types import SimpleNamespace
from uuid import uuid4

import pytest

from application.overview.facade import (
    LocationOverviewFacade,
    OverviewNotFoundError,
)


def make_object(**kwargs):
    return SimpleNamespace(**kwargs)


def test_overview_returns_strategy_and_readings():
    location_id = uuid4()
    zone_id = uuid4()
    moisture_id = uuid4()
    light_id = uuid4()

    location = make_object(
        id=location_id,
        name="Test Greenhouse",
    )

    zone = make_object(
        id=zone_id,
        name="Zone 1",
        moisture_threshold_low=0.20,
        moisture_threshold_high=0.45,
    )

    moisture_sensor = make_object(
        id=moisture_id,
        zone_id=zone_id,
        device_type="moisture_sensor",
        role="sensor",
        display_name="Soil Sensor",
        tracking_enabled=True,
        sampling_interval_seconds=300,
    )

    light_sensor = make_object(
        id=light_id,
        zone_id=zone_id,
        device_type="light_sensor",
        role="sensor",
        display_name="Light Sensor",
        tracking_enabled=True,
        sampling_interval_seconds=300,
    )

    reading = make_object(
        value=0.35,
        unit="vwc",
        recorded_at="2026-10-27T10:00:00Z",
    )

    class FakeRepository:
        def get_location_with_zones(self, requested_id):
            assert requested_id == location_id
            return location, [zone]

        def get_assigned_devices(self, requested_id):
            assert requested_id == location_id
            return [moisture_sensor, light_sensor]

        def get_latest_readings_for_devices(self, device_ids):
            assert set(device_ids) == {moisture_id, light_id}
            return {moisture_id: reading}

        def get_strategy_key(self, requested_id):
            assert requested_id == location_id
            return "aggressive"

    class FakeAutomationService:
        def evaluate(self, requested_id):
            assert requested_id == location_id
            return make_object(
                action="irrigate",
                reason="Moisture is below the high threshold",
            )

    facade = LocationOverviewFacade(
        FakeRepository(),
        FakeAutomationService(),
    )

    overview = facade.get_overview(location_id)

    assert overview.location.name == "Test Greenhouse"
    assert overview.device_counts.sensor == 2
    assert overview.device_counts.actuator == 0
    assert len(overview.zones) == 1

    assert len(overview.zones[0].devices) == 2
    assert len(overview.zones[0].latest_readings) == 1

    assert overview.zones[0].latest_readings[0].value == 0.35
    assert overview.zones[0].latest_readings[0].tracking_enabled is True

    assert overview.strategy_key == "aggressive"
    assert overview.last_recommendation.action == "irrigate"


def test_overview_location_not_found():
    location_id = uuid4()

    class FakeRepository:
        def get_location_with_zones(self, requested_id):
            return None

    facade = LocationOverviewFacade(
        FakeRepository(),
        None,
    )

    with pytest.raises(
        OverviewNotFoundError,
        match="Location not found",
    ):
        facade.get_overview(location_id)


def test_overview_without_strategy():
    location_id = uuid4()

    location = make_object(
        id=location_id,
        name="No Strategy Location",
    )

    class FakeRepository:
        def get_location_with_zones(self, requested_id):
            return location, []

        def get_assigned_devices(self, requested_id):
            return []

        def get_latest_readings_for_devices(self, device_ids):
            return {}

        def get_strategy_key(self, requested_id):
            return None

    class FakeAutomationService:
        def evaluate(self, requested_id):
            raise AssertionError(
                "Automation should not run without a strategy"
            )

    facade = LocationOverviewFacade(
        FakeRepository(),
        FakeAutomationService(),
    )

    overview = facade.get_overview(location_id)

    assert overview.strategy_key is None
    assert overview.last_recommendation is None
    assert overview.zones == []
    assert overview.device_counts.sensor == 0
    assert overview.device_counts.actuator == 0
