from uuid import UUID

from domain.actuators.ports import ActuatorPort, PolicyViolationError


class LoggingActuatorDecorator(ActuatorPort):
    POLICY = "logging"

    def __init__(self, inner: ActuatorPort, log_repo):
        self._inner = inner
        self._log_repo = log_repo

    def apply(self, device_id: UUID, command: str, payload: dict) -> None:
        try:
            self._inner.apply(device_id, command, payload)
        except PolicyViolationError as exc:
            self._log_repo.add(device_id, False, [exc.policy, self.POLICY], exc.message)
            raise
        except Exception as exc:
            self._log_repo.add(device_id, False, [self.POLICY], str(exc))
            raise

        self._log_repo.add(device_id, True, [self.POLICY], None)