from abc import ABC, abstractmethod

from domain.automation.context import (
    LocationAutomationContext,
    Recommendation,
)


class AutomationStrategy(ABC):
    key: str

    @abstractmethod
    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        pass


class ConservativeMoistureStrategy(AutomationStrategy):
    key = "conservative"

    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        if context.moisture is None:
            return Recommendation(
                action="wait",
                reason="No moisture sensor reading in this zone",
            )

        if context.moisture < context.moisture_threshold_low:
            return Recommendation(
                action="irrigate",
                reason=(
                    f"Moisture {context.moisture:.2f} is below "
                    f"the low threshold {context.moisture_threshold_low:.2f}"
                ),
            )

        return Recommendation(
            action="wait",
            reason=(
                f"Moisture {context.moisture:.2f} is within or above "
                f"the conservative threshold "
                f"{context.moisture_threshold_low:.2f}"
            ),
        )


class AggressiveMoistureStrategy(AutomationStrategy):
    key = "aggressive"

    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        if context.moisture is None:
            return Recommendation(
                action="wait",
                reason="No moisture sensor reading in this zone",
            )

        if context.moisture < context.moisture_threshold_high:
            return Recommendation(
                action="irrigate",
                reason=(
                    f"Moisture {context.moisture:.2f} is below "
                    f"the high threshold {context.moisture_threshold_high:.2f}"
                ),
            )

        return Recommendation(
            action="wait",
            reason=(
                f"Moisture {context.moisture:.2f} is at or above "
                f"the aggressive threshold "
                f"{context.moisture_threshold_high:.2f}"
            ),
        )


_STRATEGIES: dict[str, AutomationStrategy] = {
    "conservative": ConservativeMoistureStrategy(),
    "aggressive": AggressiveMoistureStrategy(),
}


def get_strategy(key: str) -> AutomationStrategy:
    try:
        return _STRATEGIES[key]
    except KeyError:
        raise ValueError(f"Unknown strategy key: {key}")