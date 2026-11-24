import inspect
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import application.commands.service as command_service_module
import application.readings.service as reading_service_module
from application.alerts.subscribers import (
    AlertPersistenceSubscriber,
    ThresholdSubscriber,
)
from application.commands.dto import CommandRequestDto
from application.commands.service import CommandService
from application.readings.service import ReadingIngest
from domain.events.bus import EventBus
from domain.events.events import (
    ActuatorStateChanged,
    CommandFailed,
    ReadingCreated,
    ThresholdCrossed,
)
from domain.sensors.reading import Reading


# ---------- Fakes (no database needed) ----------

class FakeAlertRepo:
    def __init__(self):
        self.rows = []

    def add(self, **fields):
        self.rows.append(fields)
        return SimpleNamespace(**fields)


class FakeZoneLookup:
    def __init__(self, zones):
        self._zones = zones          # {zone_id: low_threshold}

    def get_zone_by_id(self, zone_id):
        low = self._zones.get(zone_id)
        if low is None:
            return None
        return SimpleNamespace(id=zone_id, moisture_threshold_low=low)


def build_bus(zones=None):
    """Same wiring as build_event_bus(), but with fake repositories."""
    bus = EventBus()
    alert_repo = FakeAlertRepo()

    thresholds = ThresholdSubscriber(bus, FakeZoneLookup(zones or {}))
    alerts = AlertPersistenceSubscriber(alert_repo)

    bus.subscribe(ReadingCreated, thresholds.on_reading)
    bus.subscribe(ThresholdCrossed, alerts.on_threshold)
    bus.subscribe(CommandFailed, alerts.on_command_failed)
    bus.subscribe(ActuatorStateChanged, alerts.on_state_changed)

    return bus, alert_repo


def moisture_event(value, zone_id=None, location_id=None):
    return ReadingCreated(
        device_id=uuid4(),
        value=value,
        unit="vwc",
        source="simulation",
        recorded_at=datetime.now(timezone.utc),
        location_id=location_id,
        zone_id=zone_id,
    )


# ---------- EventBus ----------

def test_bus_calls_subscriber_for_its_event_type_only():
    bus = EventBus()
    received = []
    bus.subscribe(ReadingCreated, received.append)

    bus.publish(moisture_event(0.4))
    bus.publish(CommandFailed(uuid4(), None, None, "stop_pump", "boom"))

    assert len(received) == 1
    assert isinstance(received[0], ReadingCreated)


def test_broken_subscriber_does_not_break_publisher():
    bus = EventBus()
    received = []

    def broken(event):
        raise RuntimeError("subscriber crashed")

    bus.subscribe(ReadingCreated, broken)
    bus.subscribe(ReadingCreated, received.append)

    bus.publish(moisture_event(0.4))   # must not raise

    assert len(received) == 1


# ---------- Subscribers ----------

def test_low_moisture_publishes_alert():
    zone_id, location_id = uuid4(), uuid4()
    bus, alert_repo = build_bus({zone_id: 0.3})

    bus.publish(moisture_event(0.2, zone_id=zone_id, location_id=location_id))

    assert len(alert_repo.rows) == 1
    alert = alert_repo.rows[0]
    assert alert["severity"] == "warning"
    assert alert["event_type"] == "threshold.crossed"
    assert alert["zone_id"] == zone_id            # copied from the device
    assert alert["location_id"] == location_id


def test_moisture_above_threshold_creates_no_alert():
    zone_id = uuid4()
    bus, alert_repo = build_bus({zone_id: 0.3})

    bus.publish(moisture_event(0.5, zone_id=zone_id))

    assert alert_repo.rows == []


def test_unassigned_device_reading_creates_no_threshold_alert():
    bus, alert_repo = build_bus()

    bus.publish(moisture_event(0.1, zone_id=None))   # no zone → no threshold

    assert alert_repo.rows == []


def test_command_failed_alert_copies_zone_id():
    zone_id, location_id = uuid4(), uuid4()
    bus, alert_repo = build_bus()

    bus.publish(CommandFailed(uuid4(), location_id, zone_id,
                              "stop_pump", "Max run time exceeded"))

    alert = alert_repo.rows[0]
    assert alert["severity"] == "warning"
    assert alert["event_type"] == "command.failed"
    assert alert["zone_id"] == zone_id
    assert alert["location_id"] == location_id


def test_unassigned_device_alert_leaves_ids_null():
    bus, alert_repo = build_bus()

    bus.publish(CommandFailed(uuid4(), None, None,
                              "stop_pump", "Max run time exceeded"))

    alert = alert_repo.rows[0]
    assert alert["zone_id"] is None
    assert alert["location_id"] is None


def test_actuator_entering_error_creates_critical_alert():
    bus, alert_repo = build_bus()

    bus.publish(ActuatorStateChanged(uuid4(), None, None, "running", "error"))
    bus.publish(ActuatorStateChanged(uuid4(), None, None, "idle", "running"))   # ignored

    assert len(alert_repo.rows) == 1
    alert = alert_repo.rows[0]
    assert alert["severity"] == "critical"
    assert alert["event_type"] == "state.changed"
    assert alert["message"] == "Actuator entered error"


# ---------- Publisher: ReadingIngest ----------

class FakeDeviceRepo:
    def __init__(self, tracking_enabled, zone_id=None, location_id=None):
        self._row = SimpleNamespace(
            tracking_enabled=tracking_enabled,
            zone_id=zone_id,
            location_id=location_id,
        )

    def get_device_row(self, device_id):
        return self._row


class FakeReadingRepo:
    def __init__(self):
        self.inserted = []

    def insert(self, reading):
        self.inserted.append(reading)
        return reading


def make_reading(device_id):
    return Reading(
        device_id=device_id,
        value=0.35,
        unit="vwc",
        source="simulation",
        recorded_at=datetime.now(timezone.utc),
    )


def test_ingest_with_tracking_on_publishes_reading_created():
    zone_id = uuid4()
    bus = EventBus()
    published = []
    bus.subscribe(ReadingCreated, published.append)
    readings = FakeReadingRepo()
    ingest = ReadingIngest(FakeDeviceRepo(True, zone_id=zone_id), readings, bus)

    device_id = uuid4()
    ingest.record(device_id, make_reading(device_id))

    assert len(readings.inserted) == 1
    assert len(published) == 1
    assert published[0].device_id == device_id
    assert published[0].zone_id == zone_id


def test_ingest_with_tracking_off_stores_but_does_not_publish():
    bus = EventBus()
    published = []
    bus.subscribe(ReadingCreated, published.append)
    readings = FakeReadingRepo()
    ingest = ReadingIngest(FakeDeviceRepo(False), readings, bus)

    device_id = uuid4()
    ingest.record(device_id, make_reading(device_id))

    assert len(readings.inserted) == 1     # row still stored
    assert published == []                 # but no event


# ---------- Publisher: CommandService ----------

class FakeStateRepo:
    def __init__(self, state, minutes_in_state=0):
        self.state = state
        self.updated_at = datetime.now(timezone.utc) - timedelta(minutes=minutes_in_state)

    def actuator_exists(self, device_id):
        return True

    def get_state(self, device_id):
        return self.state

    def get_state_with_timestamp(self, device_id):
        return (self.state, self.updated_at)

    def save_state(self, device_id, state):
        self.state = state


class FakeCommandLog:
    def add(self, device_id, command_type, payload, status, error_message):
        return SimpleNamespace(
            id=uuid4(), device_id=device_id, command_type=command_type,
            payload=payload, status=status, error_message=error_message,
            created_at=datetime.now(timezone.utc),
        )


class FakeExecutionLog:
    def add(self, *args):
        pass


def test_failed_command_publishes_command_failed_with_zone():
    zone_id = uuid4()
    bus = EventBus()
    published = []
    bus.subscribe(CommandFailed, published.append)

    service = CommandService(
        FakeStateRepo("running", minutes_in_state=31),
        FakeCommandLog(),
        FakeExecutionLog(),
        device_repo=FakeDeviceRepo(True, zone_id=zone_id),
        event_bus=bus,
    )

    result = service.submit(
        CommandRequestDto(command_type="stop_pump", device_id=uuid4())
    )

    assert result.status == "failed"
    assert len(published) == 1
    assert published[0].error_message == "Max run time exceeded"
    assert published[0].zone_id == zone_id


# ---------- Architecture rule ----------

def test_publisher_does_not_import_alert_repository():
    for module in (reading_service_module, command_service_module):
        source = inspect.getsource(module)
        assert "AlertRepository" not in source
        assert "alert_repository" not in source
