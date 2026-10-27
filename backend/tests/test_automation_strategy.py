from uuid import uuid4

import pytest

from domain.automation.context import LocationAutomationContext
from domain.automation.strategy import get_strategy


def make_context(
    moisture: float | None = 0.40,
) -> LocationAutomationContext:
    return LocationAutomationContext(
        location_id=uuid4(),
        zone_id=uuid4(),
        moisture=moisture,
        moisture_threshold_low=0.25,
        moisture_threshold_high=0.45,
    )


def test_conservative_waits_when_within_band():
    context = make_context(moisture=0.40)

    strategy = get_strategy("conservative")
    result = strategy.decide(context)

    assert result.action == "wait"
    assert "0.40" in result.reason


def test_aggressive_differs_on_same_context():
    context = make_context(moisture=0.40)

    conservative = get_strategy("conservative")
    aggressive = get_strategy("aggressive")

    conservative_result = conservative.decide(context)
    aggressive_result = aggressive.decide(context)

    assert conservative_result.action == "wait"
    assert aggressive_result.action == "irrigate"


def test_conservative_irrigates_below_low_threshold():
    context = make_context(moisture=0.15)

    result = get_strategy("conservative").decide(context)

    assert result.action == "irrigate"


def test_aggressive_waits_above_high_threshold():
    context = make_context(moisture=0.50)

    result = get_strategy("aggressive").decide(context)

    assert result.action == "wait"


@pytest.mark.parametrize(
    "strategy_key",
    ["conservative", "aggressive"],
)
def test_missing_moisture_returns_wait(strategy_key):
    context = make_context(moisture=None)

    result = get_strategy(strategy_key).decide(context)

    assert result.action == "wait"
    assert "No moisture sensor reading" in result.reason


def test_unknown_strategy_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unknown strategy key",
    ):
        get_strategy("unknown")
