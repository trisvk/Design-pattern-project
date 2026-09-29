from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.devices.entity import Device
from domain.sensor import Sensor
from infrastructure.persistence.models import DeviceRow


class DeviceRepository:
    def __init__(self, db: Session):
        self._db = db

    def save_sensor(self, sensor: Sensor) -> Sensor:
        row = DeviceRow(
            device_type=sensor.device_type,
            role="sensor",
            display_name=sensor.display_name,
            default_config=sensor.default_config,
        )

        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)

        return Sensor(
            id=row.id,
            device_type=row.device_type,
            display_name=row.display_name,
            default_config=row.default_config,
        )

    def list_sensors(self) -> list[Sensor]:
        statement = select(DeviceRow).where(
            DeviceRow.role == "sensor"
        )

        rows = self._db.scalars(statement).all()

        return [
            Sensor(
                id=row.id,
                device_type=row.device_type,
                display_name=row.display_name,
                default_config=row.default_config,
            )
            for row in rows
        ]

    def save_device(self, device: Device) -> Device:
        row = self._device_to_row(device)

        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)

        return self._row_to_device(row)

    def save_devices(self, devices: list[Device]) -> list[Device]:
        rows = [
            self._device_to_row(device)
            for device in devices
        ]

        self._db.add_all(rows)
        self._db.commit()

        for row in rows:
            self._db.refresh(row)

        return [
            self._row_to_device(row)
            for row in rows
        ]

    def list_devices(
        self,
        *,
        device_family: str | None = None,
        role: str | None = None,
    ) -> list[Device]:
        statement = select(DeviceRow)

        if device_family is not None:
            statement = statement.where(
                DeviceRow.device_family == device_family
            )

        if role is not None:
            statement = statement.where(
                DeviceRow.role == role
            )

        rows = self._db.scalars(statement).all()

        return [
            self._row_to_device(row)
            for row in rows
        ]


    @staticmethod
    def _device_to_row(device: Device) -> DeviceRow:
        return DeviceRow(
            device_type=device.device_type,
            role=device.role,
            device_family=device.device_family,
            display_name=device.display_name,
            default_config=device.default_config,
        )

    @staticmethod
    def _row_to_device(row: DeviceRow) -> Device:
        return Device(
            id=row.id,
            device_type=row.device_type,
            role=row.role,
            device_family=row.device_family,
            display_name=row.display_name,
            default_config=row.default_config,
        )

    def get_device_row(self, device_id: UUID,) -> DeviceRow | None:
        return self._db.get(DeviceRow, device_id)

    def assign_zone(self, device_row: DeviceRow, zone_id: UUID | None, location_id: UUID | None) -> None:
        device_row.zone_id = zone_id
        device_row.location_id = location_id
        self._db.commit()

    def list_devices_in_zone(self, location_id: UUID, zone_id: UUID,) -> list[Device]:
        statement = select(DeviceRow).where(
            DeviceRow.location_id == location_id,
            DeviceRow.zone_id == zone_id,
        )

        rows = self._db.scalars(statement).all()

        return [
            self._row_to_device(row)
            for row in rows
        ]