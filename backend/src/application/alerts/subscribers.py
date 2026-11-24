from sqlalchemy.orm import Session

from domain.events.bus import EventBus
from domain.events.events import (
    ActuatorStateChanged,
    CommandFailed,
    ReadingCreated,
    ThresholdCrossed,
)
from infrastructure.persistence.alert_repository import AlertRepository
from infrastructure.persistence.location_repository import LocationRepository


class ThresholdSubscriber:
    """Rule: a moisture reading below the zone's low threshold → ThresholdCrossed."""

    def __init__(self, bus: EventBus, zone_lookup):
        self._bus = bus
        self._zones = zone_lookup

    def on_reading(self, event: ReadingCreated) -> None:
        if event.unit != "vwc" or event.zone_id is None:
            return   # not a moisture reading, or device has no zone → no threshold

        zone = self._zones.get_zone_by_id(event.zone_id)
        if zone is None:
            return

        low = float(zone.moisture_threshold_low)
        if event.value < low:
            self._bus.publish(
                ThresholdCrossed(
                    device_id=event.device_id,
                    location_id=event.location_id,
                    zone_id=event.zone_id,
                    moisture=event.value,
                    threshold=low,
                )
            )


class AlertPersistenceSubscriber:
    """Saves an alerts row for important events."""

    def __init__(self, alert_repo):
        self._repo = alert_repo

    def on_threshold(self, event: ThresholdCrossed) -> None:
        self._repo.add(
            device_id=event.device_id,
            location_id=event.location_id,
            zone_id=event.zone_id,
            severity="warning",
            message=f"Moisture {event.moisture:.2f} below zone low {event.threshold:.2f}",
            event_type=event.event_type,
        )

    def on_command_failed(self, event: CommandFailed) -> None:
        self._repo.add(
            device_id=event.device_id,
            location_id=event.location_id,
            zone_id=event.zone_id,
            severity="warning",
            message=f"Command {event.command_type} failed: {event.error_message}",
            event_type=event.event_type,
        )

    def on_state_changed(self, event: ActuatorStateChanged) -> None:
        if event.new_state != "error":
            return   # only entering "error" is worth an alert

        self._repo.add(
            device_id=event.device_id,
            location_id=event.location_id,
            zone_id=event.zone_id,
            severity="critical",
            message="Actuator entered error",
            event_type="state.changed",
        )


def build_event_bus(db: Session) -> EventBus:
    """Composition root: one bus per request, with all subscribers attached."""
    bus = EventBus()

    thresholds = ThresholdSubscriber(bus, LocationRepository(db))
    alerts = AlertPersistenceSubscriber(AlertRepository(db))

    bus.subscribe(ReadingCreated, thresholds.on_reading)
    bus.subscribe(ThresholdCrossed, alerts.on_threshold)
    bus.subscribe(CommandFailed, alerts.on_command_failed)
    bus.subscribe(ActuatorStateChanged, alerts.on_state_changed)

    return bus