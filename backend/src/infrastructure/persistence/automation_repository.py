from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.persistence.models import (
    AutomationRuleRow,
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)


class AutomationRepository:
    def __init__(self, db: Session):
        self._db = db

    def location_exists(
        self,
        location_id: UUID,
    ) -> bool:
        return self._db.get(
            LocationRow,
            location_id,
        ) is not None

    def get_strategy_key(
        self,
        location_id: UUID,
    ) -> str | None:
        statement = select(
            AutomationRuleRow.strategy_key
        ).where(
            AutomationRuleRow.location_id == location_id
        )

        return self._db.scalar(statement)

    def upsert_strategy(
        self,
        location_id: UUID,
        strategy_key: str,
    ) -> None:
        statement = select(
            AutomationRuleRow
        ).where(
            AutomationRuleRow.location_id == location_id
        )

        rule = self._db.scalar(statement)

        if rule is None:
            rule = AutomationRuleRow(
                location_id=location_id,
                strategy_key=strategy_key,
            )
            self._db.add(rule)
        else:
            rule.strategy_key = strategy_key

        self._db.commit()

    def list_zones(
        self,
        location_id: UUID,
    ) -> list[ZoneRow]:
        statement = (
            select(ZoneRow)
            .where(
                ZoneRow.location_id == location_id
            )
            .order_by(ZoneRow.id)
        )

        return list(
            self._db.scalars(statement).all()
        )

    def get_latest_moisture(
        self,
        zone_id: UUID,
    ) -> float | None:
        statement = (
            select(ReadingRow.value)
            .join(
                DeviceRow,
                ReadingRow.device_id == DeviceRow.id,
            )
            .where(
                DeviceRow.zone_id == zone_id,
                DeviceRow.role == "sensor",
                DeviceRow.device_type == "moisture_sensor",
            )
            .order_by(
                ReadingRow.recorded_at.desc()
            )
            .limit(1)
        )

        value = self._db.scalar(statement)

        if value is None:
            return None

        return float(value)