from application.commands.dto import CommandLogDto, CommandRequestDto
from application.devices.family_service import ActuatorNotFoundError
from domain.actuators.context import ActuatorContext
from domain.actuators.ports import PolicyViolationError
from domain.commands.invoker import CommandInvoker, command_for
from interfaces.api.actuators import build_actuator_port


class CommandService:
    def __init__(self, state_repo, command_log_repo, execution_log_repo,
                 invoker: CommandInvoker | None = None):
        self._state_repo = state_repo
        self._command_log = command_log_repo
        self._execution_log = execution_log_repo
        self._invoker = invoker or CommandInvoker()

    def submit(self, request: CommandRequestDto) -> CommandLogDto:
        # 404: missing device or not an actuator
        if not self._state_repo.actuator_exists(request.device_id):
            raise ActuatorNotFoundError("Actuator not found")

        # 400: unknown type → raises UnknownCommandError, no row written
        command = command_for(request.command_type, request.device_id, request.payload)

        # 1. Guard (Phase 8 State)
        context = ActuatorContext(self._state_repo.get_state(request.device_id) or "idle")

        if command.command_type not in context.allowed_commands():
            return self._log(command, "rejected",
                             f"'{command.command_type}' is not allowed when state is '{context.state}'")

        # 2. Decorated port (Phase 9 stack)
        port = build_actuator_port(self._state_repo, self._execution_log)
        try:
            self._invoker.run(command, port)
        except PolicyViolationError as exc:
            return self._log(command, "failed", exc.message)
        except Exception as exc:
            return self._log(command, "failed", str(exc))

        # 3. State update, only if target differs
        if command.target_state and command.target_state != context.state:
            context.transition(command.target_state)
            self._state_repo.save_state(command.device_id, context.state)

        # 4. Log success
        return self._log(command, "success", None)

    def list_history(self, limit: int = 50) -> list[CommandLogDto]:
        return [CommandLogDto.model_validate(r) for r in self._command_log.list_recent(limit)]

    def _log(self, command, status: str, error: str | None) -> CommandLogDto:
        row = self._command_log.add(command.device_id, command.command_type,
                                    command.payload, status, error)
        return CommandLogDto.model_validate(row)