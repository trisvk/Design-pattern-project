from application.commands.dto import CommandLogDto, CommandRequestDto
from application.devices.family_service import ActuatorNotFoundError
from domain.actuators.context import ActuatorContext
from domain.actuators.ports import PolicyViolationError
from domain.commands.invoker import CommandInvoker, command_for
from domain.events.events import ActuatorStateChanged, CommandFailed
from interfaces.api.actuators import build_actuator_port


class CommandService:
    def __init__(self, state_repo, command_log_repo, execution_log_repo,
                 invoker: CommandInvoker | None = None,
                 device_repo=None, event_bus=None):
        self._state_repo = state_repo
        self._command_log = command_log_repo
        self._execution_log = execution_log_repo
        self._invoker = invoker or CommandInvoker()
        self._device_repo = device_repo
        self._event_bus = event_bus

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
            result = self._log(command, "failed", exc.message)
            self._publish_failed(command, exc.message)
            return result
        except Exception as exc:
            result = self._log(command, "failed", str(exc))
            self._publish_failed(command, str(exc))
            return result

        # 3. State update, only if target differs
        if command.target_state and command.target_state != context.state:
            old_state = context.state
            context.transition(command.target_state)
            self._state_repo.save_state(command.device_id, context.state)
            self._publish_state_changed(command, old_state, context.state)

        # 4. Log success
        return self._log(command, "success", None)

    def list_history(self, limit: int = 50) -> list[CommandLogDto]:
        return [CommandLogDto.model_validate(r) for r in self._command_log.list_recent(limit)]

    def _log(self, command, status: str, error: str | None) -> CommandLogDto:
        row = self._command_log.add(command.device_id, command.command_type,
                                    command.payload, status, error)
        return CommandLogDto.model_validate(row)

    # ---------- Phase 11: publish events ----------

    def _device_ids(self, device_id):
        if self._device_repo is None:
            return None, None
        row = self._device_repo.get_device_row(device_id)
        return (row.location_id, row.zone_id) if row else (None, None)

    def _publish_failed(self, command, error: str) -> None:
        if self._event_bus is None:
            return
        location_id, zone_id = self._device_ids(command.device_id)
        self._event_bus.publish(CommandFailed(
            device_id=command.device_id, location_id=location_id, zone_id=zone_id,
            command_type=command.command_type, error_message=error,
        ))

    def _publish_state_changed(self, command, old: str, new: str) -> None:
        if self._event_bus is None:
            return
        location_id, zone_id = self._device_ids(command.device_id)
        self._event_bus.publish(ActuatorStateChanged(
            device_id=command.device_id, location_id=location_id, zone_id=zone_id,
            old_state=old, new_state=new,
        ))