from domain.actuators.ports import ActuatorPort
from domain.commands.base import Command


class SetLightLevelCommand(Command):
    command_type = "set_light_level"
    target_state = "running"  

    def execute(self, port: ActuatorPort) -> None:
        level = int(self.payload.get("level", 1))
        port.apply(self.device_id, self.command_type, {"level": level})