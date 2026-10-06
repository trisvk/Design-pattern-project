from datetime import datetime

from application.readings.service import ReadingIngest
from infrastructure.persistence.device_repository import (
    DeviceRepository,
)
from infrastructure.persistence.reading_repository import (
    ReadingRepository,
)


class SimulationSampler:
    def __init__(
        self,
        device_repo: DeviceRepository,
        reading_repo: ReadingRepository,
        ingest: ReadingIngest,
    ):
        self._device_repo = device_repo
        self._reading_repo = reading_repo
        self._ingest = ingest

    def run_once(
        self,
        now: datetime,
    ) -> None:
        devices = (
            self._device_repo.list_tracked_sensors_rows()
        )

        for device in devices:
            protocol = device.default_config.get(
                "protocol",
                "simulation",
            )

            # Sampler must ignore MQTT devices.
            if protocol != "simulation":
                continue

            readings = self._reading_repo.list_for_device(
                device.id,
                limit=1,
            )

            if readings:
                last_reading = readings[0]

                elapsed = (
                    now - last_reading.recorded_at
                ).total_seconds()

                if (
                    elapsed
                    < device.sampling_interval_seconds
                ):
                    continue

            self._ingest.take_reading(device.id)