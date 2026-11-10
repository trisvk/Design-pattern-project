from datetime import datetime, timedelta, timezone
from typing import Callable
from uuid import UUID

from domain.actuators.ports import ActuatorPort, PolicyViolationError


class MaxRunTimeActuatorDecorator(ActuatorPort):
    POLICY = "maxRunTime"

    def __init__(
        self,
        inner: ActuatorPort,
        state_repo,
        max_run_time: timedelta = timedelta(minutes=30),
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ):
        self._inner = inner
        self._state_repo = state_repo
        self._max_run_time = max_run_time
        self._clock = clock

    def apply(self, device_id: UUID, command: str, payload: dict) -> None:
        snapshot = self._state_repo.get_state_with_timestamp(device_id)

        if snapshot is not None:
            state, updated_at = snapshot
            if state == "running" and self._clock() - updated_at >= self._max_run_time:
                raise PolicyViolationError(self.POLICY, "Max run time exceeded")

        self._inner.apply(device_id, command, payload)