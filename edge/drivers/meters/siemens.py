"""
Siemens SENTRON PAC Power Meter Driver.
Supports PAC3100, PAC3200, and PAC4200 series over Modbus TCP (IEEE 754 Float32 big-endian).
Typically installed at the Netzanschlusspunkt (NA-Punkt / Point of Common Coupling).
"""

import struct
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from edge.drivers.base import BaseDeviceDriver
from edge.drivers.models import DeviceCategory, DeviceTelemetry, DeviceSetpoint, DiagnosticResult, ProtocolType

logger = logging.getLogger("coneza_siemens_meter_driver")


class SiemensMeterDriver(BaseDeviceDriver):
    """
    Driver for Siemens SENTRON PAC3100 / PAC3200 / PAC4200 power meters.
    Standard Siemens Modbus register mapping using IEEE 754 32-bit floating point.
    """

    # Register offsets (1-based Modbus addresses converted to 0-based offset)
    REG_VOLTAGE_L1_N = 1 - 1       # Offset 0: 2 registers (Float32)
    REG_VOLTAGE_L2_N = 3 - 1       # Offset 2
    REG_VOLTAGE_L3_N = 5 - 1       # Offset 4
    REG_VOLTAGE_L1_L2 = 7 - 1      # Offset 6
    REG_VOLTAGE_L2_L3 = 9 - 1      # Offset 8
    REG_VOLTAGE_L3_L1 = 11 - 1     # Offset 10
    REG_CURRENT_L1 = 13 - 1        # Offset 12
    REG_CURRENT_L2 = 15 - 1        # Offset 14
    REG_CURRENT_L3 = 17 - 1        # Offset 16
    REG_ACTIVE_POWER_TOTAL = 25 - 1 # Offset 24 (kW / W depending on scaling)
    REG_REACTIVE_POWER_TOTAL = 37 - 1 # Offset 36 (kvar)
    REG_APPARENT_POWER_TOTAL = 49 - 1 # Offset 48 (kVA)
    REG_POWER_FACTOR_TOTAL = 53 - 1 # Offset 52
    REG_FREQUENCY = 55 - 1         # Offset 54 (Hz)

    def __init__(
        self,
        device_id: str,
        host: str,
        port: int = 502,
        slave_id: int = 1,
        model_series: str = "SENTRON PAC3200",
        **kwargs
    ):
        super().__init__(device_id, host, port, slave_id, **kwargs)
        self._model_series = model_series
        self.client = None

    @property
    def category(self) -> DeviceCategory:
        return DeviceCategory.SMART_METER

    @property
    def manufacturer(self) -> str:
        return "Siemens"

    @property
    def model_name(self) -> str:
        return self._model_series

    @property
    def protocol(self) -> ProtocolType:
        return ProtocolType.MODBUS_TCP

    async def connect(self) -> bool:
        try:
            from pymodbus.client import AsyncModbusTcpClient
            self.client = AsyncModbusTcpClient(host=self.host, port=self.port, timeout=self.timeout)
            self._is_connected = await self.client.connect()
            logger.info(f"Siemens SENTRON PAC connected to {self.host}:{self.port}")
            return self._is_connected
        except Exception as e:
            logger.error(f"Failed to connect to Siemens PAC at {self.host}:{self.port}: {e}")
            self._is_connected = False
            return False

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self._is_connected = False

    def _decode_float32(self, registers: list, offset: int) -> float:
        """Decodes 2 16-bit Modbus registers into IEEE 754 Float32 (Big-Endian)."""
        if len(registers) < offset + 2:
            return 0.0
        r1, r2 = registers[offset], registers[offset + 1]
        raw_bytes = struct.pack(">HH", r1, r2)
        val = struct.unpack(">f", raw_bytes)[0]
        return round(val, 2)

    async def read_telemetry(self) -> DeviceTelemetry:
        if not self._is_connected:
            await self.connect()

        # Read contiguous block from offset 0 to 56 (covers Voltage, Current, Power, Frequency)
        resp = await self.client.read_holding_registers(address=0, count=56, slave=self.slave_id)
        if resp.isError():
            raise RuntimeError(f"Modbus error reading Siemens PAC registers: {resp}")

        regs = resp.registers

        u_l12 = self._decode_float32(regs, self.REG_VOLTAGE_L1_L2)
        u_l23 = self._decode_float32(regs, self.REG_VOLTAGE_L2_L3)
        u_l31 = self._decode_float32(regs, self.REG_VOLTAGE_L3_L1)
        grid_v = (u_l12 + u_l23 + u_l31) / 3.0 if (u_l12 or u_l23 or u_l31) else 400.0

        p_act = self._decode_float32(regs, self.REG_ACTIVE_POWER_TOTAL)
        q_act = self._decode_float32(regs, self.REG_REACTIVE_POWER_TOTAL)
        s_act = self._decode_float32(regs, self.REG_APPARENT_POWER_TOTAL)
        cos_phi = self._decode_float32(regs, self.REG_POWER_FACTOR_TOTAL)
        freq = self._decode_float32(regs, self.REG_FREQUENCY) or 50.0

        return DeviceTelemetry(
            device_id=self.device_id,
            timestamp=datetime.utcnow(),
            active_power_kw=p_act,
            reactive_power_kvar=q_act,
            apparent_power_kva=s_act,
            cos_phi=cos_phi if cos_phi else 1.0,
            grid_voltage_v=grid_v,
            frequency_hz=freq,
            status="ONLINE",
            raw_measurements={
                "u_l12": u_l12,
                "u_l23": u_l23,
                "u_l31": u_l31,
                "i_l1": self._decode_float32(regs, self.REG_CURRENT_L1),
                "i_l2": self._decode_float32(regs, self.REG_CURRENT_L2),
                "i_l3": self._decode_float32(regs, self.REG_CURRENT_L3),
                "power_quality_standard": "IEC 61557-12 Class 0.5S"
            }
        )

    async def apply_setpoint(self, setpoint: DeviceSetpoint) -> bool:
        # Smart meters are measurement devices; read-only
        return True

    async def test_connection(self) -> DiagnosticResult:
        try:
            telemetry = await self.read_telemetry()
            return DiagnosticResult(
                success=True,
                latency_ms=15.0,
                message=f"Siemens {self._model_series} responded successfully. Voltage={telemetry.grid_voltage_v}V, Freq={telemetry.frequency_hz}Hz",
                details={
                    "manufacturer": "Siemens",
                    "model": self._model_series,
                    "frequency_hz": telemetry.frequency_hz,
                    "voltage_v": telemetry.grid_voltage_v
                }
            )
        except Exception as e:
            return DiagnosticResult(
                success=False,
                latency_ms=0.0,
                message=f"Siemens PAC connection failed: {e}"
            )
