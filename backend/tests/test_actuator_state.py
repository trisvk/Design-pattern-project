import pytest

from domain.actuators.context import ActuatorContext
from domain.actuators.state import IllegalTransitionError


def test_idle_to_running_allowed():
    actuator = ActuatorContext("idle")

    actuator.transition("running")

    assert actuator.state == "running"


def test_running_to_maintenance_rejected():
    actuator = ActuatorContext("running")

    with pytest.raises(IllegalTransitionError):
        actuator.transition("maintenance")


def test_illegal_transition_does_not_change_state():
    actuator = ActuatorContext("running")

    with pytest.raises(IllegalTransitionError):
        actuator.transition("maintenance")

    assert actuator.state == "running"


def test_allowed_commands_change_with_state():
    actuator = ActuatorContext("idle")

    assert actuator.allowed_commands() == ["start_pump"]

    actuator.transition("running")

    assert actuator.allowed_commands() == ["stop_pump"]
