"""
coneza Multi-Device Simulator & Telemetry Sync for IPC
Simulates:
- 2x Solinteg MHT-75K Inverters (75 kW rated each, 100 kW total PV generation)
- 1x BYD Battery-Box Commercial (200 kW BESS)
- 1x Siemens SENTRON PAC3200 (NA-Punkt Grid Meter)
Runs lightweight Modbus TCP server listeners on ports 5020-5023
and synchronizes registration & live telemetry heartbeats with the Coneza Portal.
"""

import asyncio
import logging
import math
import os
import signal
import struct
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

import httpx

logger = logging.getLogger("coneza_plant_devices")

PLANT_ID = os.getenv("PLANT_ID", "plant-enbw-hybrid-01")
BACKEND_URL = os.getenv("CONEZA_BACKEND_URL", "https://coneza.de/portal").rstrip("/")
PORTAL_SOCKET = os.getenv("PORTAL_SOCKET", "/run/coneza-portal/portal.sock" if os.path.exists("/run/coneza-portal/portal.sock") else None)


def pack_float32(val: float) -> List[int]:
    """Packs float32 into two 16-bit big-endian Modbus registers."""
    raw = struct.pack(">f", float(val))
    return list(struct.unpack(">HH", raw))


class ModbusDeviceSimulator:
    """Lightweight standalone Modbus TCP server simulating an industrial energy device."""

    def __init__(self, name: str, port: int, unit_id: int = 1):
        self.name = name
        self.port = port
        self.unit_id = unit_id
        self.holding_registers: Dict[int, int] = {i: 0 for i in range(120)}
        self.server: Optional[asyncio.Server] = None
        self.active_writers: set = set()
        self.is_running = False

    def set_float32(self, reg_offset: int, val: float):
        regs = pack_float32(val)
        self.holding_registers[reg_offset] = regs[0]
        self.holding_registers[reg_offset + 1] = regs[1]

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.active_writers.add(writer)
        try:
            while self.is_running:
                mbap = await reader.read(7)
                if not mbap or len(mbap) < 7:
                    break
                trans_id, proto_id, pdu_len, unit_id = struct.unpack(">HHHB", mbap)
                if proto_id != 0:
                    continue
                pdu = await reader.read(pdu_len - 1)
                if not pdu:
                    break

                func_code = pdu[0]
                # FC 03 (Read Holding) or FC 04 (Read Input)
                if func_code in (0x03, 0x04):
                    start_addr, count = struct.unpack(">HH", pdu[1:5])
                    values = [self.holding_registers.get(a, 0) for a in range(start_addr, start_addr + count)]
                    payload = struct.pack(f">B{count}H", count * 2, *values)
                    resp_pdu = bytes([func_code]) + payload
                # FC 06 (Write Single Holding)
                elif func_code == 0x06:
                    reg_addr, val = struct.unpack(">HH", pdu[1:5])
                    self.holding_registers[reg_addr] = val
                    resp_pdu = pdu[:5]
                # FC 16 (Write Multiple Holding)
                elif func_code == 0x10:
                    start_addr, count, byte_count = struct.unpack(">HHB", pdu[1:6])
                    vals = struct.unpack(f">{count}H", pdu[6:6 + byte_count])
                    for i, v in enumerate(vals):
                        self.holding_registers[start_addr + i] = v
                    resp_pdu = bytes([0x10]) + struct.pack(">HH", start_addr, count)
                else:
                    resp_pdu = bytes([func_code | 0x80, 0x01])  # Illegal function

                resp_mbap = struct.pack(">HHHB", trans_id, 0, len(resp_pdu) + 1, unit_id)
                writer.write(resp_mbap + resp_pdu)
                await writer.drain()
        except Exception:
            pass
        finally:
            self.active_writers.discard(writer)
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def start(self, host: str = "0.0.0.0"):
        self.is_running = True
        self.server = await asyncio.start_server(self.handle_client, host, self.port)
        logger.info("Modbus server for '%s' listening on %s:%d", self.name, host, self.port)

    async def stop(self):
        self.is_running = False
        for w in list(self.active_writers):
            try:
                w.close()
            except Exception:
                pass
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Modbus server for '%s' stopped", self.name)


class PlantDeviceManager:
    """Coordinates local Modbus simulations and sends periodic heartbeats to Coneza portal."""

    def __init__(self, backend_url: str = BACKEND_URL, portal_socket: Optional[str] = PORTAL_SOCKET):
        self.backend_url = backend_url
        self.portal_socket = portal_socket
        self.is_running = False

        # 1. Siemens SENTRON PAC3200 E-Meter (NA-Punkt) -> Port 5020
        self.sim_meter = ModbusDeviceSimulator("Siemens SENTRON PAC3200 (NA-Punkt)", port=5020)
        # 2. Solinteg Wechselrichter 1 (75 kW) -> Port 5021
        self.sim_inv1 = ModbusDeviceSimulator("Solinteg MHT-75K #1", port=5021)
        # 3. Solinteg Wechselrichter 2 (75 kW) -> Port 5022
        self.sim_inv2 = ModbusDeviceSimulator("Solinteg MHT-75K #2", port=5022)
        # 4. BYD Battery-Box Commercial 200 kW BESS -> Port 5023
        self.sim_bess = ModbusDeviceSimulator("BYD Battery-Box Commercial 200", port=5023)
        # 5. Netze BW GmbH (EnBW) Grid & EVU Simulation (20kV NAP) -> Port 5024
        self.sim_grid = ModbusDeviceSimulator("Netze BW GmbH (EnBW) - Grid Simulation & EVU Interconnection", port=5024)

        self._init_registers()

    def _init_registers(self):
        # Siemens PAC3200 registers:
        # Offset 0 (Addr 1): Voltage L1-N = 230.9 V, Offset 6 (Addr 7): Voltage L1-L2 = 400.0 V / 20000.0 V
        self.sim_meter.set_float32(0, 230.9)
        self.sim_meter.set_float32(2, 230.9)
        self.sim_meter.set_float32(4, 230.9)
        self.sim_meter.set_float32(6, 400.0)
        self.sim_meter.set_float32(8, 400.0)
        self.sim_meter.set_float32(10, 400.0)
        self.sim_meter.set_float32(12, 144.3)  # Current L1 (~100 kW total @ 400V)
        self.sim_meter.set_float32(14, 144.3)
        self.sim_meter.set_float32(16, 144.3)
        self.sim_meter.set_float32(24, 85.0)   # Total Active Power at NAP = 85.0 kW (100 kW PV - 15 kW BESS charge)
        self.sim_meter.set_float32(36, 0.0)    # Reactive Power = 0.0 kvar
        self.sim_meter.set_float32(48, 85.0)   # Apparent Power = 85.0 kVA
        self.sim_meter.set_float32(52, 1.00)   # cos(phi) = 1.00
        self.sim_meter.set_float32(54, 50.00)  # Frequency = 50.00 Hz

        # Solinteg Inverter 1 (50 kW current active power, 75 kW rated)
        self.sim_inv1.set_float32(0, 50.0)     # Active Power = 50.0 kW
        self.sim_inv1.set_float32(2, 0.0)      # Reactive Power = 0.0 kvar
        self.sim_inv1.set_float32(4, 400.0)    # AC Voltage = 400.0 V
        self.sim_inv1.set_float32(6, 50.00)    # Frequency = 50.00 Hz
        self.sim_inv1.set_float32(8, 75.0)     # Rated Power = 75.0 kW

        # Solinteg Inverter 2 (50 kW current active power, 75 kW rated)
        self.sim_inv2.set_float32(0, 50.0)     # Active Power = 50.0 kW
        self.sim_inv2.set_float32(2, 0.0)      # Reactive Power = 0.0 kvar
        self.sim_inv2.set_float32(4, 400.0)    # AC Voltage = 400.0 V
        self.sim_inv2.set_float32(6, 50.00)    # Frequency = 50.00 Hz
        self.sim_inv2.set_float32(8, 75.0)     # Rated Power = 75.0 kW

        # BYD BESS (200 kW rated, charging 15 kW excess PV, SoC 68%)
        self.sim_bess.set_float32(0, -15.0)    # Active Power = -15.0 kW (charging)
        self.sim_bess.set_float32(2, 68.5)     # SoC = 68.5%
        self.sim_bess.set_float32(4, 200.0)    # Rated Power = 200.0 kW
        self.sim_bess.set_float32(6, 400.0)    # Voltage = 400.0 V

        # Netze BW Grid & EVU Simulation (20 kV Medium Voltage, 50 Hz, 300 kW Capacity)
        self.sim_grid.holding_registers[0] = 1       # Interconnection Status (1=Synchronized)
        self.sim_grid.set_float32(2, 20000.0)        # Nominal Medium Voltage (20.0 kV)
        self.sim_grid.set_float32(4, 400.0)          # Low Voltage (400.0 V)
        self.sim_grid.set_float32(6, 50.00)          # Grid Frequency (50.00 Hz)
        self.sim_grid.set_float32(8, 85.0)           # Total Feed-in Active Power (85.0 kW)
        self.sim_grid.set_float32(10, 0.0)           # Total Reactive Power (0.0 kvar)
        self.sim_grid.set_float32(12, 1.00)          # Power Factor cos(phi) = 1.00
        self.sim_grid.set_float32(14, 300.0)         # Max Allowed Feed-In Limit (P_AV_max = 300.0 kW)
        self.sim_grid.set_float32(16, 100.0)         # EVU Curtailment Level (100.0%)
        self.sim_grid.holding_registers[18] = 1      # Main Grid Breaker (1=Closed)

    def _http_client(self, **kwargs):
        if self.portal_socket and os.path.exists(self.portal_socket):
            kwargs["transport"] = httpx.AsyncHTTPTransport(uds=self.portal_socket, verify=True)
            kwargs["trust_env"] = False
        return httpx.AsyncClient(**kwargs)

    async def register_devices(self):
        devices = [
            {
                "device_id": "siemens-pac-nap",
                "name": "Siemens SENTRON PAC3200 (NA-Punkt)",
                "plant_id": PLANT_ID,
                "local_ip": "192.168.8.186",
                "device_category": "SMART_METER",
                "manufacturer": "Siemens",
                "model": "SENTRON PAC3200",
                "controller_host": "192.168.8.186",
                "controller_port": 5020,
                "slave_id": 1
            },
            {
                "device_id": "solinteg-inv-01",
                "name": "Solinteg MHT-75K Wechselrichter 1 (75 kW)",
                "plant_id": PLANT_ID,
                "local_ip": "192.168.8.186",
                "device_category": "INVERTER",
                "manufacturer": "Solinteg",
                "model": "MHT-75K",
                "controller_host": "192.168.8.186",
                "controller_port": 5021,
                "slave_id": 1
            },
            {
                "device_id": "solinteg-inv-02",
                "name": "Solinteg MHT-75K Wechselrichter 2 (75 kW)",
                "plant_id": PLANT_ID,
                "local_ip": "192.168.8.186",
                "device_category": "INVERTER",
                "manufacturer": "Solinteg",
                "model": "MHT-75K",
                "controller_host": "192.168.8.186",
                "controller_port": 5022,
                "slave_id": 1
            },
            {
                "device_id": "byd-bess-01",
                "name": "BYD Battery-Box Commercial (200 kW BESS)",
                "plant_id": PLANT_ID,
                "local_ip": "192.168.8.186",
                "device_category": "INVERTER",
                "manufacturer": "BYD",
                "model": "Battery-Box Commercial 200",
                "controller_host": "192.168.8.186",
                "controller_port": 5023,
                "slave_id": 1
            },
            {
                "device_id": "grid-sim-enbw",
                "name": "Netze BW GmbH (EnBW) - Grid Simulation & EVU Interconnection",
                "plant_id": PLANT_ID,
                "local_ip": "192.168.8.186",
                "device_category": "GRID_SIMULATOR",
                "manufacturer": "Netze BW / EnBW",
                "model": "EVU-NAP-20kV-Sim",
                "controller_host": "192.168.8.186",
                "controller_port": 5024,
                "slave_id": 1
            }
        ]

        async with self._http_client(timeout=10.0) as client:
            for dev in devices:
                try:
                    resp = await client.post(f"{self.backend_url}/api/devices/register", json=dev)
                    if resp.status_code in (200, 201):
                        logger.info("Registered device %s with portal", dev["device_id"])
                    else:
                        logger.warning("Device register %s returned %s: %s", dev["device_id"], resp.status_code, resp.text)
                except Exception as e:
                    logger.error("Failed to register device %s: %e", dev["device_id"], e)

    async def send_heartbeats(self):
        now_sec = time.time()
        dynamic_freq = round(50.00 + 0.015 * math.sin(now_sec / 12.0), 3)
        dynamic_volt_mv = round(20000.0 + 35.0 * math.cos(now_sec / 18.0), 1)
        dynamic_volt_lv = round(dynamic_volt_mv / 50.0, 1)

        # Update dynamic values in simulated Modbus registers
        self.sim_grid.set_float32(2, dynamic_volt_mv)
        self.sim_grid.set_float32(4, dynamic_volt_lv)
        self.sim_grid.set_float32(6, dynamic_freq)
        self.sim_meter.set_float32(6, dynamic_volt_lv)
        self.sim_meter.set_float32(54, dynamic_freq)

        heartbeats = [
            {
                "device_id": "grid-sim-enbw",
                "local_ip": "192.168.8.186",
                "controller_connected": True,
                "controller_state": "GRID_SYNCHRONIZED",
                "telemetry": {
                    "grid_operator": "Netze BW GmbH (EnBW)",
                    "voltage_level": "MS_4110",
                    "nominal_voltage_kv": 20.0,
                    "actual_voltage_kv": round(dynamic_volt_mv / 1000.0, 2),
                    "actual_voltage_v": dynamic_volt_lv,
                    "frequency_hz": dynamic_freq,
                    "active_power_feed_in_kw": 85.0,
                    "reactive_power_kvar": 0.0,
                    "power_factor_cos_phi": 1.00,
                    "feed_in_limit_kw": 300.0,
                    "feed_in_limit_percent": 100.0,
                    "curtailment_active": False,
                    "redispatch_state": "NORMAL_OPERATION",
                    "grid_breaker_state": "CLOSED",
                    "grid_connection_point": "Umspannwerk EnBW / Übergabestation 20kV",
                    "status": "SYNCHRONIZED_STABLE"
                }
            },
            {
                "device_id": "siemens-pac-nap",
                "local_ip": "192.168.8.186",
                "controller_connected": True,
                "controller_state": "ONLINE",
                "telemetry": {
                    "active_power_kw": 85.0,
                    "reactive_power_kvar": 0.0,
                    "apparent_power_kva": 85.0,
                    "cos_phi": 1.00,
                    "grid_voltage_v": dynamic_volt_lv,
                    "grid_voltage_mv": dynamic_volt_mv,
                    "frequency_hz": dynamic_freq,
                    "role": "NA-PUNKT_GRID_METER",
                    "accuracy_class": "IEC 61557-12 Class 0.5S",
                    "grid_operator": "Netze BW GmbH (EnBW)"
                }
            },
            {
                "device_id": "solinteg-inv-01",
                "local_ip": "192.168.8.186",
                "controller_connected": True,
                "controller_state": "ONLINE_FEEDING",
                "telemetry": {
                    "active_power_kw": 50.0,
                    "rated_power_kw": 75.0,
                    "apparent_power_kva": 50.0,
                    "reactive_power_kvar": 0.0,
                    "cos_phi": 1.00,
                    "grid_voltage_v": dynamic_volt_lv,
                    "frequency_hz": dynamic_freq,
                    "curtailment_percent": 100.0,
                    "status": "RUNNING"
                }
            },
            {
                "device_id": "solinteg-inv-02",
                "local_ip": "192.168.8.186",
                "controller_connected": True,
                "controller_state": "ONLINE_FEEDING",
                "telemetry": {
                    "active_power_kw": 50.0,
                    "rated_power_kw": 75.0,
                    "apparent_power_kva": 50.0,
                    "reactive_power_kvar": 0.0,
                    "cos_phi": 1.00,
                    "grid_voltage_v": dynamic_volt_lv,
                    "frequency_hz": dynamic_freq,
                    "curtailment_percent": 100.0,
                    "status": "RUNNING"
                }
            },
            {
                "device_id": "byd-bess-01",
                "local_ip": "192.168.8.186",
                "controller_connected": True,
                "controller_state": "CHARGING_BESS",
                "telemetry": {
                    "active_power_kw": -15.0,
                    "rated_power_kw": 200.0,
                    "soc_percent": 68.5,
                    "capacity_kwh": 200.0,
                    "mode": "PEAK_SHAVING_ABSORPTION",
                    "cos_phi": 1.00,
                    "status": "CHARGING"
                }
            }
        ]

        async with self._http_client(timeout=10.0) as client:
            for hb in heartbeats:
                try:
                    resp = await client.post(f"{self.backend_url}/api/devices/{hb['device_id']}/heartbeat", json=hb)
                    if resp.status_code == 200:
                        logger.debug("Heartbeat sent for %s", hb["device_id"])
                    elif resp.status_code == 404:
                        await self.register_devices()
                except Exception as e:
                    logger.warning("Heartbeat error for %s: %s", hb["device_id"], e)

    async def run(self, stop_event: Optional[asyncio.Event] = None):
        logger.info("Starting Plant Device Simulators (Siemens, 2x Solinteg, BYD, EnBW Grid)...")
        await self.sim_meter.start()
        await self.sim_inv1.start()
        await self.sim_inv2.start()
        await self.sim_bess.start()
        await self.sim_grid.start()

        logger.info("Registering devices with Coneza Portal at %s...", self.backend_url)
        await self.register_devices()

        self.is_running = True
        stop = stop_event or asyncio.Event()
        loop = asyncio.get_running_loop()
        installed = []
        if stop_event is None:
            for signum in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(signum, stop.set)
                installed.append(signum)

        async def heartbeat_loop():
            while self.is_running:
                try:
                    await self.send_heartbeats()
                except Exception as e:
                    logger.error("Error in heartbeat loop: %s", e)
                await asyncio.sleep(10.0)

        hb_task = asyncio.create_task(heartbeat_loop())
        logger.info("Plant devices simulation active. Press Ctrl+C or send SIGTERM to stop.")

        try:
            await stop.wait()
        finally:
            logger.info("Stopping plant devices simulation...")
            self.is_running = False
            hb_task.cancel()
            try:
                await hb_task
            except asyncio.CancelledError:
                pass
            await self.sim_meter.stop()
            await self.sim_inv1.stop()
            await self.sim_inv2.stop()
            await self.sim_bess.stop()
            await self.sim_grid.stop()
            for signum in installed:
                loop.remove_signal_handler(signum)
            logger.info("Plant devices simulation stopped cleanly.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    manager = PlantDeviceManager()
    asyncio.run(manager.run())
