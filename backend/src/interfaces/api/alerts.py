from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from application.alerts.dto import AlertDto
from infrastructure.db import get_db
from infrastructure.persistence.alert_repository import AlertRepository


router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get(
    "",
    response_model=list[AlertDto],
    summary="List alerts (newest first)",
    description="Optional filters: status (active | resolved), location_id, zone_id.",
)
def list_alerts(
    status: str | None = Query(default=None, pattern="^(active|resolved)$"),
    location_id: UUID | None = Query(default=None),
    zone_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[AlertDto]:
    rows = AlertRepository(db).list_alerts(
        status=status,
        location_id=location_id,
        zone_id=zone_id,
        limit=limit,
    )
    return [AlertDto.model_validate(row) for row in rows]