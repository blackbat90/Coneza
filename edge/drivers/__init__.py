"""
Universal Device Drivers for Inverters, Smart Meters, and EZA Regulators.
"""

from edge.drivers.models import (
    DeviceCategory, ProtocolType, DeviceTelemetry, DeviceSetpoint,
    DiagnosticResult, SupportedDeviceSpec
)
from edge.drivers.base import BaseDeviceDriver
from edge.drivers.inverters.sunspec import SunSpecInverterDriver
from edge.drivers.meters.janitza import JanitzaMeterDriver
from edge.drivers.meters.schneider import SchneiderMeterDriver
from edge.drivers.eza_controllers.wago import WagoEzaDriver
from edge.drivers.registry import device_registry, SUPPORTED_HARDWARE_CATALOG

__all__ = [
    "DeviceCategory",
    "ProtocolType",
    "DeviceTelemetry",
    "DeviceSetpoint",
    "DiagnosticResult",
    "SupportedDeviceSpec",
    "BaseDeviceDriver",
    "SunSpecInverterDriver",
    "JanitzaMeterDriver",
    "SchneiderMeterDriver",
    "WagoEzaDriver",
    "device_registry",
    "SUPPORTED_HARDWARE_CATALOG",
]
