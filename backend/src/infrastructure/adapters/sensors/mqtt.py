from datetime import datetime, timezone

from domain.devices.entity import Device
from domain.sensors.reading import Reading


class MqttSensorAdapter:
    def translate(
        self,
        device: Device,
        payload: dict,
    ) -> Reading:
        return Reading(
            device_id=device.id,
            value=float(payload["value"]),
            unit=str(payload["unit"]),
            source="mqtt",
            recorded_at=datetime.now(timezone.utc),
        )