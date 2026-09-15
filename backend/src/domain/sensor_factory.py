from abc import ABC, abstractmethod

from domain.sensor import Sensor


class SensorCreator(ABC):
    @abstractmethod
    def create_sensor(
        self,
        display_name: str | None = None,
    ) -> Sensor:
        ...


class MoistureSensorCreator(SensorCreator):
    def create_sensor(
        self,
        display_name: str | None = None,
    ) -> Sensor:
        return Sensor(
            id=None,
            device_type="moisture_sensor",
            display_name=display_name,
            default_config={
                "unit": "%",
                "threshold": 30,
                "interval": 60,
            },
        )


class LightSensorCreator(SensorCreator):
    def create_sensor(
        self,
        display_name: str | None = None,
    ) -> Sensor:
        return Sensor(
            id=None,
            device_type="light_sensor",
            display_name=display_name,
            default_config={
                "unit": "lux",
                "threshold": 300,
                "interval": 30,
            },
        )


_CREATORS: dict[str, SensorCreator] = {
    "moisture": MoistureSensorCreator(),
    "light": LightSensorCreator(),
}


def get_creator(sensor_type: str) -> SensorCreator:
    try:
        return _CREATORS[sensor_type]
    except KeyError:
        raise ValueError(f"Unknown sensor type: {sensor_type}")