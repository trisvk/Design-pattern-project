from datetime import datetime, timezone

from domain.devices.entity import Device
from domain.sensors.ports import SensorPort
from domain.sensors.reading import Reading


class VendorStubSensorAdapter(SensorPort):
    def read(
        self,
        device: Device,
    ) -> Reading:
        raw_data = self._read_vendor_data(device)

        return Reading(
            device_id=device.id,
            value=float(raw_data["measurement"]),
            unit=raw_data["measurement_unit"],
            source="vendor",
            recorded_at=datetime.now(timezone.utc),
        )

    def _read_vendor_data(
        self,
        device: Device,
    ) -> dict:
        if device.device_type == "moisture_sensor":
            return {
                "measurement": 0.42,
                "measurement_unit": "vwc",
            }

        if device.device_type == "light_sensor":
            return {
                "measurement": 850,
                "measurement_unit": "lux",
            }

        raise ValueError(
            f"Unsupported sensor type: {device.device_type}"
        )