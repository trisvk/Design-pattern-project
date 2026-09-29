from abc import ABC, abstractmethod

from domain.devices.entity import Device

from domain.sensor_factory import (
    LightSensorCreator,
    MoistureSensorCreator,
)


class DeviceFamilyFactory(ABC):
    @property
    @abstractmethod
    def family_key(self) -> str:
        ...

    @abstractmethod
    def create_device_set(self) -> list[Device]:
        ...
        

class SimulationDeviceFactory(DeviceFamilyFactory):
    @property
    def family_key(self) -> str:
        return "simulation"

    def create_device_set(self) -> list[Device]:
        moisture = MoistureSensorCreator().create_sensor()
        light = LightSensorCreator().create_sensor()

        return [
            Device(
                id=None,
                device_type=moisture.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name="Simulated moisture sensor",
                default_config={
                    **moisture.default_config,
                    "protocol": "sim",
                },
            ),
            Device(
                id=None,
                device_type=light.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name="Simulated light sensor",
                default_config={
                    **light.default_config,
                    "protocol": "sim",
                },
            ),
            Device(
                id=None,
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Simulated water pump",
                default_config={"protocol": "sim"},
            ),
            Device(
                id=None,
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Simulated grow light",
                default_config={"protocol": "sim"},
            ),
        ]


class EdgeHardwareFactory(DeviceFamilyFactory):
    @property
    def family_key(self) -> str:
        return "edge"

    def create_device_set(self) -> list[Device]:
        moisture = MoistureSensorCreator().create_sensor()
        light = LightSensorCreator().create_sensor()

        return [
            Device(
                id=None,
                device_type=moisture.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name="Edge moisture sensor",
                default_config={
                    **moisture.default_config,
                    "protocol": "gpio-stub",
                },
            ),
            Device(
                id=None,
                device_type=light.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name="Edge light sensor",
                default_config={
                    **light.default_config,
                    "protocol": "gpio-stub",
                },
            ),
            Device(
                id=None,
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge water pump",
                default_config={"protocol": "gpio-stub"},
            ),
            Device(
                id=None,
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge grow light",
                default_config={"protocol": "gpio-stub"},
            ),
        ]


_FAMILY_FACTORIES: dict[str, DeviceFamilyFactory] = {
    "simulation": SimulationDeviceFactory(),
    "edge": EdgeHardwareFactory(),
}


def get_family_factory(family: str) -> DeviceFamilyFactory:
    try:
        return _FAMILY_FACTORIES[family]
    except KeyError:
        raise ValueError(f"Unknown device family: {family}")