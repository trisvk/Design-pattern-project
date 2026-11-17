from uuid import UUID

from domain.actuators.ports import ActuatorPort
from domain.commands.base import Command
from domain.commands.light import SetLightLevelCommand
from domain.commands.pump import StartPumpCommand, StopPumpCommand


class UnknownCommandError(ValueError):
    pass


COMMAND_REGISTRY: dict[str, type[Command]] = {
    cls.command_type: cls
    for cls in (StartPumpCommand, StopPumpCommand, SetLightLevelCommand)
}


def command_for(command_type: str, device_id: UUID, payload: dict) -> Command:
    cls = COMMAND_REGISTRY.get(command_type)
    if cls is None:
        raise UnknownCommandError(f"Unknown command type: {command_type}")
    return cls(device_id, payload)


class CommandInvoker:
    def run(self, command: Command, port: ActuatorPort) -> None:
        command.execute(port)