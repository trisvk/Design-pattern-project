from domain.actuators.state import (
    ALLOWED,
    COMMANDS,
    IllegalTransitionError,
)


class ActuatorContext:
    def __init__(self, state: str = "idle"):
        if state not in ALLOWED:
            raise ValueError(f"Unknown actuator state: {state}")

        self.state = state

    def transition(self, target: str) -> None:
        if target not in ALLOWED[self.state]:
            raise IllegalTransitionError(
                f"Cannot transition from {self.state} to {target}"
            )

        self.state = target

    def allowed_commands(self) -> list[str]:
        return COMMANDS[self.state].copy()
