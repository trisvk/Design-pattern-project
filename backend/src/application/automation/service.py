from uuid import UUID

from application.automation.dto import RecommendationDto
from domain.automation.context import LocationAutomationContext
from domain.automation.strategy import get_strategy
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)


class AutomationNotFoundError(ValueError):
    pass


class AutomationService:
    def __init__(
        self,
        repo: AutomationRepository,
    ):
        self._repo = repo

    def set_strategy(
        self,
        location_id: UUID,
        strategy_key: str,
    ) -> None:
        if not self._repo.location_exists(location_id):
            raise AutomationNotFoundError(
                "Location not found"
            )


        get_strategy(strategy_key)

        self._repo.upsert_strategy(
            location_id,
            strategy_key,
        )

    def evaluate(
        self,
        location_id: UUID,
    ) -> RecommendationDto:
        if not self._repo.location_exists(location_id):
            raise AutomationNotFoundError(
                "Location not found"
            )

        strategy_key = self._repo.get_strategy_key(
            location_id
        )

        if strategy_key is None:
            raise ValueError(
                "No automation strategy configured "
                "for this location"
            )

        strategy = get_strategy(strategy_key)

        zones = self._repo.list_zones(location_id)

        if not zones:
            raise ValueError(
                "Location has no zones"
            )

        recommendations = []

        for zone in zones:
            moisture = self._repo.get_latest_moisture(
                zone.id
            )

            context = LocationAutomationContext(
                location_id=location_id,
                zone_id=zone.id,
                moisture=moisture,
                moisture_threshold_low=float(
                    zone.moisture_threshold_low
                ),
                moisture_threshold_high=float(
                    zone.moisture_threshold_high
                ),
            )

            recommendation = strategy.decide(context)
            recommendations.append(recommendation)


        irrigate = next(
            (
                recommendation
                for recommendation in recommendations
                if recommendation.action == "irrigate"
            ),
            None,
        )

        result = (
            irrigate
            if irrigate is not None
            else recommendations[0]
        )

        return RecommendationDto(
            location_id=location_id,
            strategy_key=strategy_key,
            action=result.action,
            reason=result.reason,
        )