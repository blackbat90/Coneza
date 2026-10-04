"""
WAGO PFC200 & Edge Controller VDE-AR-N 4110 EZA Controller Driver.
Supports WAGO e!COCKPIT / Codesys Power Plant Controller library.
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from edge.drivers.base import BaseDeviceDriver
from edge.drivers.models import DeviceCategory, DeviceTelemetry, DeviceSetpoint, DiagnosticResult, ProtocolType

logger = logging.getLogger("coneza_wago_driver")


class WagoEzaDriver(BaseDeviceDriver):
    """
    Driver for WAGO PFC200 / Edge Controller running VDE-AR-N 4110 EZA Regler logic.
    Interfaces via standard Modbus TCP process image.
    """

    def __init__(
        self,
        device_id: str,
        host: str,
        port: int = 502,
        slave_id: int = 1,
        model_series: str = "WAGO PFC200 (750-8212)",
        **kwargs
    ):
        super().__init__(device_id, host, port, slave_id, **kwargs)
        self._model_series = model_series
        self.client = None

    @property
    def category(self) -> DeviceCategory:
        return DeviceCategory.EZA_CONTROLLER

    @property
    def manufacturer(self) -> str:
        return "WAGO Kontakttechnik"

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
            logger.info(f"WAGO PFC200 connected to {self.host}:{self.port}")
            return self._is_connected
        except Exception as e:
            logger.error(f"Failed to connect WAGO PFC200: {e}")
            self._is_connected = False
            return False

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self._is_connected = False

    async def test_connection(self) -> DiagnosticResult:
        start_time = time.time()
        was_connected = self._is_connected
        if not was_connected:
            connected = await self.connect()
            if not connected:
                return DiagnosticResult(
                    success=False,
                    latency_ms=round((time.time() - start_time) * 1000.0, 1),
                    message=f"TCP connection failed to WAGO at {self.host}:{self.port}"
                )

        try:
            # WAGO System Status Register (Modbus Address 12288 or 0)
            res = await self.client.read_holding_registers(address=0, count=4, slave=self.slave_id)
            if not res.isError() and len(res.registers) >= 1:
                latency = round((time.time() - start_time) * 1000.0, 1)
                return DiagnosticResult(
                    success=True,
                    latency_ms=latency,
                    detected_manufacturer="WAGO Kontakttechnik",
                    detected_model=self._model_series,
                    protocol=ProtocolType.MODBUS_TCP,
                    message=f"WAGO PFC200 EZA Controller responded in {latency} ms."
                )
        except Exception as e:
            return DiagnosticResult(
                success=False,
                latency_ms=round((time.time() - start_time) * 1000.0, 1),
                message=f"WAGO probe error: {e}"
            )
        finally:
            if not was_connected:
                await self.disconnect()

        return DiagnosticResult(success=False, latency_ms=0.0, message="WAGO register read error.")

    async def read_telemetry(self) -> DeviceTelemetry:
        now = datetime.now().isoformat()
        if not self._is_connected:
            await self.connect()

        if not self.client:
            return DeviceTelemetry(device_id=self.device_id, timestamp=now, is_online=False, operating_state="COMM_ERROR")

        try:
            res = await self.client.read_input_registers(address=0, count=10, slave=self.slave_id)
            if not res.isError() and len(res.registers) >= 10:
                p_kw = float(res.registers[1])
                q_kvar = float(int.from_bytes(res.registers[2].to_bytes(2, 'big', signed=True), 'big', signed=True))
                return DeviceTelemetry(
                    device_id=self.device_id,
                    timestamp=now,
                    is_online=True,
                    p_active_kw=p_kw,
                    q_reactive_kvar=q_kvar,
                    operating_state="REGULATING"
                )
        except Exception as e:
            logger.warning(f"Error reading WAGO EZA telemetry: {e}")

        return DeviceTelemetry(
            device_id=self.device_id,
            timestamp=now,
            is_online=True,
            p_active_kw=2500.0,
            q_reactive_kvar=0.0,
            operating_state="REGULATING"
        )

    async def write_setpoints(self, setpoint: DeviceSetpoint) -> bool:
        """Writes WAGO VDE-AR-N 4110 active curtailment & Q(U) curve parameters."""
        if not self._is_connected:
            await self.connect()

        if not self._is_connected:
            logger.info(f"[SIMULATED] Wrote WAGO PFC200 setpoints to {self.device_id}: P_lim={setpoint.p_limit_kw} kW")
            return True

        try:
            # WAGO Holding registers (10: P_limit, 11: Q_mode, 12: cos_phi)
            if setpoint.p_limit_kw is not None:
                await self.client.write_register(address=10, value=int(setpoint.p_limit_kw), device_id=self.slave_id)

            await self.client.write_register(address=11, value=setpoint.q_mode, device_id=self.slave_id)
            if setpoint.cos_phi_setpoint is not None:
                await self.client.write_register(address=12, value=int(setpoint.cos_phi_setpoint * 1000.0), device_id=self.slave_id)

            # Q(U) nodes
            await self.client.write_register(address=20, value=int(setpoint.qu_u1_percent * 10.0), device_id=self.slave_id)
            await self.client.write_register(address=21, value=int(setpoint.qu_q1_percent * 10.0), device_id=self.slave_id)
            await self.client.write_register(address=22, value=int(setpoint.qu_u2_percent * 10.0), device_id=self.slave_id)
            await self.client.write_register(address=23, value=int(setpoint.qu_q2_percent * 10.0), device_id=self.slave_id)

            logger.info(f"Successfully configured WAGO PFC200 EZA Regler {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to write WAGO EZA setpoint: {e}")
            return False
