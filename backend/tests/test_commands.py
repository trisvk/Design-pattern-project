from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from application.commands.dto import CommandRequestDto
from application.commands.service import CommandService
from application.devices.family_service import ActuatorNotFoundError
from domain.commands.invoker import UnknownCommandError



class FakeStateRepo:
    def __init__(self, state, minutes_in_state=0, is_actuator=True):
        self.state = state
        self.updated_at = datetime.now(timezone.utc) - timedelta(minutes=minutes_in_state)
        self.is_actuator = is_actuator
        self.saved = []

    def actuator_exists(self, device_id):
        return self.is_actuator

    def get_state(self, device_id):
        return self.state

    def get_state_with_timestamp(self, device_id):
        return (self.state, self.updated_at)

    def save_state(self, device_id, state):
        self.state = state
        self.saved.append(state)


class FakeCommandLog:
    def __init__(self):
        self.rows = []

    def add(self, device_id, command_type, payload, status, error_message):
        row = SimpleNamespace(
            id=uuid4(),
            device_id=device_id,
            command_type=command_type,
            payload=payload,
            status=status,
            error_message=error_message,
            created_at=datetime.now(timezone.utc),
        )
        self.rows.append(row)
        return row


class FakeExecutionLog:
    def __init__(self):
        self.rows = []

    def add(self, device_id, success, policy_applied, message):
        self.rows.append(
            {"success": success, "policy_applied": policy_applied, "message": message}
        )


def make_service(state, minutes_in_state=0, is_actuator=True):
    states = FakeStateRepo(state, minutes_in_state, is_actuator)
    command_log = FakeCommandLog()
    execution_log = FakeExecutionLog()
    service = CommandService(states, command_log, execution_log)
    return service, states, command_log, execution_log


def request(command_type, payload=None):
    return CommandRequestDto(
        command_type=command_type,
        device_id=uuid4(),
        payload=payload or {},
    )


# ---------- Required tests ----------

def test_illegal_command_rejected_logged():
    service, states, command_log, execution_log = make_service("idle")

    result = service.submit(request("stop_pump"))

    assert result.status == "rejected"
    assert states.state == "idle"          # state unchanged
    assert states.saved == []              # nothing written to actuator_states
    assert len(command_log.rows) == 1      # rejected row still logged
    assert execution_log.rows == []        # decorated port never reached


def test_start_pump_transitions_to_running():
    service, states, command_log, execution_log = make_service("idle")

    result = service.submit(request("start_pump"))

    assert result.status == "success"
    assert states.state == "running"
    assert states.saved == ["running"]
    assert command_log.rows[0].status == "success"
    assert execution_log.rows[0]["success"] is True   # went through Phase 9 stack


# ---------- Extra tests ----------

def test_max_runtime_block_is_logged_as_failed():
    service, states, command_log, execution_log = make_service(
        "running", minutes_in_state=31
    )

    result = service.submit(request("stop_pump"))

    assert result.status == "failed"
    assert result.error_message == "Max run time exceeded"
    assert states.state == "running"       # state unchanged
    assert states.saved == []
    assert execution_log.rows[0]["policy_applied"] == ["maxRunTime", "logging"]


def test_set_light_level_on_running_light_does_not_transition():
    service, states, command_log, _ = make_service("running")

    result = service.submit(request("set_light_level", {"level": 5}))

    assert result.status == "success"
    assert states.state == "running"
    assert states.saved == []              # target == current -> no save


def test_unknown_command_raises_and_writes_no_row():
    service, _, command_log, _ = make_service("idle")

    with pytest.raises(UnknownCommandError):
        service.submit(request("fly"))

    assert command_log.rows == []


def test_non_actuator_is_not_found():
    service, _, command_log, _ = make_service("idle", is_actuator=False)

    with pytest.raises(ActuatorNotFoundError):
        service.submit(request("start_pump"))

    assert command_log.rows == []
