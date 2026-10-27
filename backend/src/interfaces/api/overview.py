from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.automation.service import AutomationService
from application.overview.dto import LocationOverviewDto
from application.overview.facade import (
    LocationOverviewFacade,
    OverviewNotFoundError,
)
from infrastructure.db import get_db
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)


router = APIRouter(
    prefix="/api/locations",
    tags=["overview"],
)


def get_overview_facade(
    db: Session = Depends(get_db),
) -> LocationOverviewFacade:
    repo = AutomationRepository(db)

    return LocationOverviewFacade(
        repo=repo,
        automation_service=AutomationService(repo),
    )


@router.get(
    "/{location_id}/overview",
    response_model=LocationOverviewDto,
)
def get_location_overview(
    location_id: UUID,
    facade: LocationOverviewFacade = Depends(
        get_overview_facade
    ),
) -> LocationOverviewDto:
    try:
        return facade.get_overview(location_id)

    except OverviewNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
