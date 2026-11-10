from abc import ABC, abstractmethod
from uuid import UUID


class ActuatorPort(ABC):
    @abstractmethod
    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        ...
class PolicyViolationError(Exception):
    """Raised by a decorator when a policy blocks apply()."""

    def __init__(self, policy: str, message: str):
        super().__init__(message)
        self.policy = policy      # e.g. "maxRunTime"
        self.message = message    # e.g. "Max run time exceeded"