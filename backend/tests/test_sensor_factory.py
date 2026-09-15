from domain.sensor_factory import (
    LightSensorCreator,
    MoistureSensorCreator,
)


def test_moisture_creator_defaults():
    creator = MoistureSensorCreator()

    sensor = creator.create_sensor()

    assert sensor.device_type == "moisture_sensor"
    assert "threshold" in sensor.default_config


def test_light_creator_defaults():
    creator = LightSensorCreator()

    sensor = creator.create_sensor()

    assert sensor.device_type == "light_sensor"
    assert sensor.default_config["unit"] != "%"