import datetime
from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.persistence.models import (
    ActuatorStateRow,
    DeviceRow,
)


class ActuatorStateRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_state(self, device_id: UUID) -> str | None:
        stmt = (
            select(ActuatorStateRow.state)
            .join(
                DeviceRow,
                ActuatorStateRow.device_id == DeviceRow.id,
            )
            .where(
                DeviceRow.id == device_id,
                DeviceRow.role == "actuator",
            )
        )

        return self._db.scalar(stmt)

    def get_states(self, device_ids: list[UUID]) -> dict[UUID, str]:
        if not device_ids:
            return {}

        stmt = (
            select(
                ActuatorStateRow.device_id,
                ActuatorStateRow.state,
            )
            .join(
                DeviceRow,
                ActuatorStateRow.device_id == DeviceRow.id,
            )
            .where(
                DeviceRow.id.in_(device_ids),
                DeviceRow.role == "actuator",
            )
        )

        return dict(self._db.execute(stmt).all())

    def actuator_exists(self, device_id: UUID) -> bool:
        stmt = select(DeviceRow.id).where(
            DeviceRow.id == device_id,
            DeviceRow.role == "actuator",
        )

        return self._db.scalar(stmt) is not None

    def save_state(self, device_id: UUID, state: str) -> None:
        row = self._db.get(ActuatorStateRow, device_id)

        if row is None:
            row = ActuatorStateRow(
                device_id=device_id,
                state=state,
            )
            self._db.add(row)
        else:
            row.state = state

        self._db.commit()

    def get_state_with_timestamp(self, device_id: UUID) -> tuple[str, datetime] | None:
        row = self._db.get(ActuatorStateRow, device_id)
        return None if row is None else (row.state, row.updated_at)
