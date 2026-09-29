#AI created
from domain.devices.family_factory import (
    EdgeHardwareFactory,
    SimulationDeviceFactory,
)


def test_simulation_factory_returns_four_devices():
    factory = SimulationDeviceFactory()

    devices = factory.create_device_set()

    assert len(devices) == 4
    assert all(device.device_family == "simulation" for device in devices)


def test_edge_factory_differs_from_simulation():
    simulation_factory = SimulationDeviceFactory()
    edge_factory = EdgeHardwareFactory()

    simulation_devices = simulation_factory.create_device_set()
    edge_devices = edge_factory.create_device_set()

    assert len(simulation_devices) == 4
    assert len(edge_devices) == 4

    assert all(
        device.device_family == "simulation"
        for device in simulation_devices
    )

    assert all(
        device.device_family == "edge"
        for device in edge_devices
    )

    assert simulation_devices != edge_devices