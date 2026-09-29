from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from domain.locations.entity import LocationConfig
from infrastructure.persistence.models import (
    DeviceRow,
    LocationRow,
    ZoneRow,
)


class LocationRepository:
    def __init__(self, db: Session):
        self._db = db

    def save_config(
        self,
        config: LocationConfig,
    ) -> tuple[LocationRow, list[ZoneRow]]:
        try:
            location_row = LocationRow(
                name=config.location.name,
            )

            self._db.add(location_row)

            # Get the location ID before creating zones,
            # but do not commit yet.
            self._db.flush()

            zone_rows = [
                ZoneRow(
                    location_id=location_row.id,
                    name=zone.name,
                    moisture_threshold_low=zone.moisture_threshold_low,
                    moisture_threshold_high=zone.moisture_threshold_high,
                    schedule=zone.schedule,
                )
                for zone in config.zones
            ]

            self._db.add_all(zone_rows)

            # One commit for location + all zones.
            self._db.commit()

            self._db.refresh(location_row)

            for zone_row in zone_rows:
                self._db.refresh(zone_row)

            return location_row, zone_rows

        except Exception:
            self._db.rollback()
            raise

    def get_config(
        self,
        location_id: UUID,
    ) -> tuple[LocationRow, list[ZoneRow]] | None:
        location_row = self._db.get(
            LocationRow,
            location_id,
        )

        if location_row is None:
            return None

        statement = select(ZoneRow).where(
            ZoneRow.location_id == location_id
        )

        zone_rows = list(
            self._db.scalars(statement).all()
        )

        return location_row, zone_rows

    def list_locations(
        self,
    ) -> list[LocationRow]:
        statement = select(LocationRow).order_by(
            LocationRow.created_at
        )

        return list(
            self._db.scalars(statement).all()
        )

    def delete_location(
        self,
        location_id: UUID,
    ) -> bool:
        location = self._db.get(
            LocationRow,
            location_id,
        )

        if location is None:
            return False

        # Clear both IDs from assigned devices first.
        self._db.execute(
            update(DeviceRow)
            .where(
                DeviceRow.location_id == location_id
            )
            .values(
                location_id=None,
                zone_id=None,
            )
        )

        # Zones are deleted by ON DELETE CASCADE.
        self._db.delete(location)
        self._db.commit()

        return True

    def add_zone(
        self,
        location_id: UUID,
        *,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict,
    ) -> ZoneRow | None:
        location = self._db.get(
            LocationRow,
            location_id,
        )

        if location is None:
            return None

        zone = ZoneRow(
            location_id=location_id,
            name=name,
            moisture_threshold_low=moisture_threshold_low,
            moisture_threshold_high=moisture_threshold_high,
            schedule=schedule,
        )

        self._db.add(zone)
        self._db.commit()
        self._db.refresh(zone)

        return zone

    def get_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> ZoneRow | None:
        statement = select(ZoneRow).where(
            ZoneRow.id == zone_id,
            ZoneRow.location_id == location_id,
        )

        return self._db.scalar(statement)

    def get_zone_by_id(
        self,
        zone_id: UUID,
    ) -> ZoneRow | None:
        return self._db.get(
            ZoneRow,
            zone_id,
        )

    def update_zone(
        self,
        zone: ZoneRow,
        *,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict,
    ) -> ZoneRow:
        zone.name = name
        zone.moisture_threshold_low = (
            moisture_threshold_low
        )
        zone.moisture_threshold_high = (
            moisture_threshold_high
        )
        zone.schedule = schedule

        self._db.commit()
        self._db.refresh(zone)

        return zone

    def count_zones(
        self,
        location_id: UUID,
    ) -> int:
        statement = select(ZoneRow).where(
            ZoneRow.location_id == location_id
        )

        return len(
            list(self._db.scalars(statement).all())
        )

    def delete_zone(
        self,
        zone: ZoneRow,
    ) -> None:
        # ON DELETE SET NULL clears zone_id,
        # but the requirement says location_id
        # must also become NULL.
        self._db.execute(
            update(DeviceRow)
            .where(
                DeviceRow.zone_id == zone.id
            )
            .values(
                zone_id=None,
                location_id=None,
            )
        )

        self._db.delete(zone)
        self._db.commit()
