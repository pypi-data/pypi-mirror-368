"""Models for MyLightSystems API Client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass
class Auth:
    """Auth model."""

    token: str


@dataclass
class Profile:
    """Profile model."""

    id: int
    grid_type: str
    tenant: str
    city: str
    country: str
    postal_code: str
    address: str


@dataclass
class Device:
    """Device model."""

    id: str
    name: str
    device_type_name: str
    type: str
    type_id: str


@dataclass
class BatteryDevice(Device):
    """Represent a battery."""

    state: bool
    capacity: int


@dataclass
class RelayDevice(Device):
    """Represent a relay."""

    state: bool
    master_id: str
    master_type: str


@dataclass
class CounterDevice(Device):
    """Represent a counter."""

    state: bool
    phase: int
    master_id: str
    master_type: str


@dataclass
class CompositeCounterDevice(Device):
    """Represent a composite counter."""

    master_id: str
    master_type: str
    children: dict[str, int]


@dataclass
class VirtualDevice(Device):
    """Represent a virtual."""

    state: bool


@dataclass
class EthernetDevice(Device):
    """Represent an ethernet device."""

    master_id: str
    master_type: str


@dataclass
class MasterDevice(Device):
    """Represent a master."""

    state: bool
    report_period: int


@dataclass
class Measure:
    """Represent a measure."""

    type: str
    value: float
    unit: str


@dataclass
class SensorMeasure:
    """Represent a sensor measure."""

    type: str | None
    value: float
    unit: str | None
    date: datetime


@dataclass
class SensorState:
    """Represent a sensor state."""

    sensor_id: str
    measure: SensorMeasure


@dataclass
class DeviceState:
    """Represent a device state."""

    device_id: str
    report_period: int
    state: bool
    sensor_states: list[SensorState]


@dataclass
class SwitchState:
    """Represent the state of the switch."""

    state: bool
