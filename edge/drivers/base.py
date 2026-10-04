"""
Abstract Base Driver for Inverters, Smart Meters, and EZA Power Plant Controllers.
"""

import abc
import time
import logging
from typing import Dict, Any, Optional
from edge.drivers.models import DeviceCategory, DeviceTelemetry, DeviceSetpoint, DiagnosticResult, ProtocolType

logger = logging.getLogger("coneza_device_driver")


class BaseDeviceDriver(abc.ABC):
    """
    Abstract base class providing standard connection lifecycle, telemetry reading,
    setpoint dispatching, and diagnostic probing across any grid hardware.
    """

    def __init__(
        self,
        device_id: str,
        host: str,
        port: int = 502,
        slave_id: int = 1,
        timeout: float = 3.0,
        **kwargs
    ):
        self.device_id = device_id
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.timeout = timeout
        self.extra_config = kwargs
        self._is_connected = False

    @property
    @abc.abstractmethod
    def category(self) -> DeviceCategory:
        """Returns INVERTER, SMART_METER, or EZA_CONTROLLER."""
        pass

    @property
    @abc.abstractmethod
    def manufacturer(self) -> str:
        """Manufacturer name (e.g. SMA, Huawei, Janitza, Phoenix Contact)."""
        pass

    @property
    @abc.abstractmethod
    def model_name(self) -> str:
        """Model series (e.g. SUN2000, UMG 96RM, PLCnext SOL-SC-PCU)."""
        pass

    @property
    def protocol(self) -> ProtocolType:
        return ProtocolType.MODBUS_TCP

    @abc.abstractmethod
    async def connect(self) -> bool:
        """Establishes connection to the target device."""
        pass

    @abc.abstractmethod
    async def disconnect(self) -> None:
        """Closes connection cleanly."""
        pass

    def is_connected(self) -> bool:
        return self._is_connected

    @abc.abstractmethod
    async def read_telemetry(self) -> DeviceTelemetry:
        """Reads standardized electrical telemetry from the device."""
        pass

    @abc.abstractmethod
    async def write_setpoints(self, setpoint: DeviceSetpoint) -> bool:
        """Writes active/reactive power setpoints or regulation parameters."""
        pass

    @abc.abstractmethod
    async def test_connection(self) -> DiagnosticResult:
        """Performs a diagnostic probe to verify responsiveness and identify the unit."""
        pass
