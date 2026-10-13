from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.automation.dto import (
    RecommendationDto,
    StrategyRequestDto,
)
from application.automation.service import (
    AutomationNotFoundError,
    AutomationService,
)
from domain.automation.strategy import get_strategy
from infrastructure.db import get_db
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)


router = APIRouter(
    prefix="/api/locations",
    tags=["automation"],
)


def get_automation_service(
    db: Session = Depends(get_db),
) -> AutomationService:
    return AutomationService(
        AutomationRepository(db)
    )


@router.put(
    "/{location_id}/automation",
    status_code=200,
)
def set_strategy(
    location_id: UUID,
    request: StrategyRequestDto,
    service: AutomationService = Depends(
        get_automation_service
    ),
):
    try:
        service.set_strategy(
            location_id,
            request.strategy_key,
        )

        return {
            "location_id": location_id,
            "strategy_key": request.strategy_key,
        }

    except AutomationNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/{location_id}/automation/evaluate",
    response_model=RecommendationDto,
)
def evaluate(
    location_id: UUID,
    service: AutomationService = Depends(
        get_automation_service
    ),
) -> RecommendationDto:
    try:
        return service.evaluate(location_id)

    except AutomationNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc