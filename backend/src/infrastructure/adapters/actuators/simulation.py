from uuid import UUID

from domain.actuators.ports import ActuatorPort


class SimulationActuatorAdapter(ActuatorPort):
    def __init__(self):
        self.commands: list[dict] = []

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        self.commands.append(
            {
                "device_id": device_id,
                "command": command,
                "payload": payload,
            }
        )