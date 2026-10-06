from uuid import UUID

from application.readings.dto import ReadingDto
from domain.sensors.ports import SensorPort
from domain.sensors.reading import Reading
from infrastructure.adapters.sensors.simulation import (
    SimulationSensorAdapter,
)
from infrastructure.persistence.device_repository import (
    DeviceRepository,
)
from infrastructure.persistence.reading_repository import (
    ReadingRepository,
)


class ReadingIngest:
    def __init__(
        self,
        device_repo: DeviceRepository,
        reading_repo: ReadingRepository,
    ):
        self._device_repo = device_repo
        self._reading_repo = reading_repo

    def take_reading(
        self,
        device_id: UUID,
    ) -> ReadingDto:
        device_row = self._device_repo.get_device_row(
            device_id
        )

        if device_row is None:
            raise LookupError("Device not found")

        device = self._device_repo._row_to_device(
            device_row
        )

        protocol = device.default_config.get(
            "protocol",
            "simulation",
        )

        port: SensorPort

        if protocol == "simulation":
            port = SimulationSensorAdapter()
        else:
            raise ValueError(
                f"Protocol '{protocol}' does not support "
                "one-shot reads"
            )

        reading = port.read(device)

        return self.record(
            device_id,
            reading,
        )

    def record(
        self,
        device_id: UUID,
        reading: Reading,
    ) -> ReadingDto:
        device_row = self._device_repo.get_device_row(
            device_id
        )

        if device_row is None:
            raise LookupError("Device not found")

        if reading.device_id != device_id:
            raise ValueError(
                "Reading device_id does not match"
            )

        saved = self._reading_repo.insert(reading)

        return self._to_dto(saved)

    def list_readings(
        self,
        device_id: UUID,
        limit: int = 20,
    ) -> list[ReadingDto]:
        device = self._device_repo.get_device_row(
            device_id
        )

        if device is None:
            raise LookupError("Device not found")

        readings = self._reading_repo.list_for_device(
            device_id,
            limit,
        )

        return [
            self._to_dto(reading)
            for reading in readings
        ]

    @staticmethod
    def _to_dto(
        reading: Reading,
    ) -> ReadingDto:
        return ReadingDto(
            device_id=reading.device_id,
            value=reading.value,
            unit=reading.unit,
            source=reading.source,
            recorded_at=reading.recorded_at,
        )