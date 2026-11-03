from uuid import UUID

from application.devices.dto import DeviceDto
from application.devices.mappers import devices_to_dtos
from domain.actuators.context import ActuatorContext
from domain.devices.entity import Device
from domain.devices.family_factory import get_family_factory
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from infrastructure.persistence.device_repository import DeviceRepository


class ActuatorNotFoundError(ValueError):
    pass


class DeviceFamilyService:
    def __init__(
        self,
        repo: DeviceRepository,
        state_repo: ActuatorStateRepository | None = None,
    ):
        self._repo = repo
        self._state_repo = state_repo

    def provision_family(self, family: str) -> list[Device]:
        factory = get_family_factory(family)
        devices = factory.create_device_set()
        saved = self._repo.save_devices(devices)

        if self._state_repo is not None:
            for device in saved:
                if device.role == "actuator" and device.id is not None:
                    self._state_repo.save_state(device.id, "idle")

        return saved

    def list_devices(
        self,
        *,
        device_family: str | None = None,
        role: str | None = None,
    ) -> list[Device]:
        return self._repo.list_devices(
            device_family=device_family,
            role=role,
        )

    def list_device_dtos(
        self,
        *,
        device_family: str | None = None,
        role: str | None = None,
    ) -> list[DeviceDto]:
        devices = self.list_devices(
            device_family=device_family,
            role=role,
        )

        if self._state_repo is None:
            return devices_to_dtos(devices)

        actuator_ids = [
            device.id
            for device in devices
            if device.role == "actuator" and device.id is not None
        ]

        states = self._state_repo.get_states(actuator_ids)

        return devices_to_dtos(devices, states)

    def transition_actuator(
        self,
        device_id: UUID,
        target: str,
    ) -> dict:
        if self._state_repo is None:
            raise RuntimeError("Actuator state repository is required")

        if not self._state_repo.actuator_exists(device_id):
            raise ActuatorNotFoundError("Actuator not found")

        current_state = self._state_repo.get_state(device_id)

        if current_state is None:
            current_state = "idle"

        context = ActuatorContext(current_state)

        # Validate before saving.
        context.transition(target)

        self._state_repo.save_state(device_id, context.state)

        return {
            "state": context.state,
            "allowed_commands": context.allowed_commands(),
        }
