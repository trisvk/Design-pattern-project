from application.devices.dto import DeviceDto
from domain.actuators.context import ActuatorContext
from domain.devices.entity import Device


def device_to_dto(
    device: Device,
    state: str | None = None,
) -> DeviceDto:
    if device.id is None:
        raise ValueError("Cannot convert an unpersisted device to DTO")

    commands = []

    if device.role == "actuator" and state is not None:
        commands = ActuatorContext(state).allowed_commands()

    return DeviceDto(
        id=device.id,
        device_type=device.device_type,
        role=device.role,
        device_family=device.device_family,
        display_name=device.display_name,
        default_config=device.default_config,
        state=state if device.role == "actuator" else None,
        allowed_commands=commands,
    )


def devices_to_dtos(
    devices: list[Device],
    states: dict | None = None,
) -> list[DeviceDto]:
    states = states or {}

    return [
        device_to_dto(
            device,
            states.get(device.id),
        )
        for device in devices
    ]
