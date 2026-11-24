from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.persistence.models import AlertRow


class AlertRepository:
    def __init__(self, db: Session):
        self._db = db

    def add(
        self,
        *,
        device_id: UUID | None,
        location_id: UUID | None,
        zone_id: UUID | None,
        severity: str,
        message: str,
        event_type: str,
    ) -> AlertRow:
        row = AlertRow(
            device_id=device_id,
            location_id=location_id,
            zone_id=zone_id,
            severity=severity,
            message=message,
            event_type=event_type,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def list_alerts(
        self,
        *,
        status: str | None = None,
        location_id: UUID | None = None,
        zone_id: UUID | None = None,
        limit: int = 50,
    ) -> list[AlertRow]:
        stmt = select(AlertRow)

        if status is not None:
            stmt = stmt.where(AlertRow.status == status)
        if location_id is not None:
            stmt = stmt.where(AlertRow.location_id == location_id)
        if zone_id is not None:
            stmt = stmt.where(AlertRow.zone_id == zone_id)

        stmt = stmt.order_by(AlertRow.created_at.desc()).limit(limit)
        return list(self._db.scalars(stmt))