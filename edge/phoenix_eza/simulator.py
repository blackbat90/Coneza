"""
Phoenix Contact EZA-Regler Hardware-in-the-Loop (HIL) Modbus TCP Simulator
Simulates a certified Phoenix Contact PLCnext Power Plant Controller (EZA-Regler)
Conforms to VDE-AR-N 4110.
Listens on Modbus TCP (default port 5502 for unprivileged testing, or 502 for real network).
"""

import asyncio
import logging
import struct
from typing import Dict, List, Optional
from edge.phoenix_eza.register_map import HOLDING_REGISTERS, INPUT_REGISTERS

logger = logging.getLogger("phoenix_eza_simulator")

class PhoenixEZASimulator:
    """
    Simulates a Phoenix Contact EZA controller communicating over Modbus TCP.
    Maintains registers in memory, emulates plant physics, and provides
    instant feedback for commissioning tests.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 5502):
        self.host = host
        self.port = port
        self.server: Optional[asyncio.Server] = None
        self.is_running = False

        # In-memory storage for holding registers (0..999) and input registers (0..999)
        self.holding_registers: Dict[int, int] = {i: 0 for i in range(1000)}
        self.input_registers: Dict[int, int] = {i: 0 for i in range(1000)}

        self._initialize_defaults()

    def _initialize_defaults(self):
        """Pre-populate default controller state & grid parameters."""
        # System defaults
        self.holding_registers[HOLDING_REGISTERS["REG_SYSTEM_STATUS"]] = 1
        self.holding_registers[HOLDING_REGISTERS["REG_HEARTBEAT_TIMEOUT_SEC"]] = 30
        self.holding_registers[HOLDING_REGISTERS["REG_GRID_VOLTAGE_NOMINAL"]] = 20000  # 20 kV MV
        self.holding_registers[HOLDING_REGISTERS["REG_GRID_FREQUENCY_NOMINAL"]] = 5000  # 50.00 Hz
        self.holding_registers[HOLDING_REGISTERS["REG_RATED_ACTIVE_POWER_KW"]] = 2500   # 2.5 MW plant
        self.holding_registers[HOLDING_REGISTERS["REG_RATED_APPARENT_POWER_KVA"]] = 2750

        # Active power defaults
        self.holding_registers[HOLDING_REGISTERS["REG_P_CONTROL_MODE"]] = 0
        self.holding_registers[HOLDING_REGISTERS["REG_P_SETPOINT_KW"]] = 2500
        self.holding_registers[HOLDING_REGISTERS["REG_P_SETPOINT_PERCENT"]] = 1000  # 100.0%
        self.holding_registers[HOLDING_REGISTERS["REG_P_MAX_FEED_IN_LIMIT_KW"]] = 2500
        self.holding_registers[HOLDING_REGISTERS["REG_P_RAMP_RATE_KW_PER_SEC"]] = 100
        self.holding_registers[HOLDING_REGISTERS["REG_P_FREQUENCY_DROOP_EN"]] = 1

        # Reactive power Q(U) defaults
        self.holding_registers[HOLDING_REGISTERS["REG_Q_CONTROL_MODE"]] = 1  # 1 = Q(U) characteristic curve
        self.holding_registers[HOLDING_REGISTERS["REG_COS_PHI_SETPOINT"]] = 1000
        self.holding_registers[HOLDING_REGISTERS["REG_Q_SETPOINT_KVAR"]] = 0
        self.holding_registers[HOLDING_REGISTERS["REG_Q_MAX_INDUCTIVE_KVAR"]] = 1100
        self.holding_registers[HOLDING_REGISTERS["REG_Q_MAX_CAPACITIVE_KVAR"]] = 1100
        self.holding_registers[HOLDING_REGISTERS["REG_Q_U_TIME_CONSTANT_SEC"]] = 8

        # Standard Q(U) 4-point curve (VDE-AR-N 4110)
        self.holding_registers[HOLDING_REGISTERS["REG_QU_U1"]] = 930   # 93% Un
        self.holding_registers[HOLDING_REGISTERS["REG_QU_Q1"]] = 1000  # +100% Qmax (capacitive)
        self.holding_registers[HOLDING_REGISTERS["REG_QU_U2"]] = 970   # 97% Un
        self.holding_registers[HOLDING_REGISTERS["REG_QU_Q2"]] = 0     # 0%
        self.holding_registers[HOLDING_REGISTERS["REG_QU_U3"]] = 1030  # 103% Un
        self.holding_registers[HOLDING_REGISTERS["REG_QU_Q3"]] = 0     # 0%
        self.holding_registers[HOLDING_REGISTERS["REG_QU_U4"]] = 1070  # 107% Un
        self.holding_registers[HOLDING_REGISTERS["REG_QU_Q4"]] = -1000 # -100% Qmax (inductive)

        # Protection parameters
        self.holding_registers[HOLDING_REGISTERS["REG_PROT_U_MAX_PERCENT"]] = 1100
        self.holding_registers[HOLDING_REGISTERS["REG_PROT_U_MAX_TRIP_MS"]] = 100
        self.holding_registers[HOLDING_REGISTERS["REG_PROT_U_MIN_PERCENT"]] = 800
        self.holding_registers[HOLDING_REGISTERS["REG_PROT_U_MIN_TRIP_MS"]] = 3000
        self.holding_registers[HOLDING_REGISTERS["REG_PROT_F_MAX_HZ"]] = 5150
        self.holding_registers[HOLDING_REGISTERS["REG_PROT_F_MIN_HZ"]] = 4750

        # Telemetry inputs
        self.input_registers[INPUT_REGISTERS["REG_ACTUAL_ACTIVE_POWER_KW"]] = 2480
        self.input_registers[INPUT_REGISTERS["REG_ACTUAL_REACTIVE_POWER_KVAR"]] = 25
        self.input_registers[INPUT_REGISTERS["REG_ACTUAL_APPARENT_POWER_KVA"]] = 2480
        self.input_registers[INPUT_REGISTERS["REG_ACTUAL_COS_PHI"]] = 999
        self.input_registers[INPUT_REGISTERS["REG_ACTUAL_VOLTAGE_L12_VOLTS"]] = 20120
        self.input_registers[INPUT_REGISTERS["REG_ACTUAL_VOLTAGE_L23_VOLTS"]] = 20110
        self.input_registers[INPUT_REGISTERS["REG_ACTUAL_VOLTAGE_L31_VOLTS"]] = 20130
        self.input_registers[INPUT_REGISTERS["REG_ACTUAL_FREQUENCY_HZ"]] = 5001
        self.input_registers[INPUT_REGISTERS["REG_CONTROLLER_STATE"]] = 1  # Normal / Regulating
        self.input_registers[INPUT_REGISTERS["REG_BREAKER_STATE"]] = 1       # Closed
        self.input_registers[INPUT_REGISTERS["REG_ACTIVE_CONTROL_MODE"]] = 1 # Q(U)
        self.input_registers[INPUT_REGISTERS["REG_CURTAILMENT_ACTIVE"]] = 0
        self.input_registers[INPUT_REGISTERS["REG_ALARM_CODE_BITMASK"]] = 0

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Processes incoming Modbus TCP ADU packets."""
        addr = writer.get_extra_info('peername')
        logger.debug(f"Modbus client connected from {addr}")

        try:
            while self.is_running:
                # Read Modbus TCP MBAP Header (7 bytes):
                # Transaction ID (2 bytes), Protocol ID (2 bytes), Length (2 bytes), Unit ID (1 byte)
                mbap = await reader.read(7)
                if not mbap or len(mbap) < 7:
                    break

                trans_id, proto_id, pdu_len, unit_id = struct.unpack(">HHHB", mbap)
                if proto_id != 0:
                    continue  # Not Modbus protocol

                # Read remainder of PDU
                pdu = await reader.read(pdu_len - 1)
                if not pdu:
                    break

                func_code = pdu[0]
                response_pdu = self._process_function_code(func_code, pdu[1:])

                # Assemble Modbus TCP Response
                resp_len = len(response_pdu) + 1
                resp_mbap = struct.pack(">HHHB", trans_id, proto_id, resp_len, unit_id)
                writer.write(resp_mbap + response_pdu)
                await writer.drain()
        except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
            pass
        except Exception as e:
            logger.error(f"Error handling Modbus client: {e}")
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    def _process_function_code(self, func_code: int, data: bytes) -> bytes:
        """Processes Modbus standard Function Codes (03, 04, 06, 16)."""
        # FC 03: Read Holding Registers
        if func_code == 0x03:
            if len(data) < 4:
                return bytes([func_code | 0x80, 0x03])  # Illegal data value
            start_addr, count = struct.unpack(">HH", data[:4])
            byte_count = count * 2
            values = []
            for addr in range(start_addr, start_addr + count):
                val = self.holding_registers.get(addr, 0)
                # Pack as signed/unsigned 16-bit
                values.append(val & 0xFFFF)
            payload = struct.pack(f">B{count}H", byte_count, *values)
            return bytes([func_code]) + payload

        # FC 04: Read Input Registers
        elif func_code == 0x04:
            if len(data) < 4:
                return bytes([func_code | 0x80, 0x03])
            start_addr, count = struct.unpack(">HH", data[:4])
            byte_count = count * 2
            values = []
            for addr in range(start_addr, start_addr + count):
                val = self.input_registers.get(addr, 0)
                values.append(val & 0xFFFF)
            payload = struct.pack(f">B{count}H", byte_count, *values)
            return bytes([func_code]) + payload

        # FC 06: Write Single Holding Register
        elif func_code == 0x06:
            if len(data) < 4:
                return bytes([func_code | 0x80, 0x03])
            reg_addr, value = struct.unpack(">HH", data[:4])
            self.holding_registers[reg_addr] = value
            self._update_simulated_telemetry(reg_addr, value)
            return bytes([func_code]) + struct.pack(">HH", reg_addr, value)

        # FC 16 (0x10): Write Multiple Holding Registers
        elif func_code == 0x10:
            if len(data) < 5:
                return bytes([func_code | 0x80, 0x03])
            start_addr, count, byte_count = struct.unpack(">HHB", data[:5])
            val_bytes = data[5:5 + byte_count]
            vals = struct.unpack(f">{count}H", val_bytes)
            for i, val in enumerate(vals):
                reg = start_addr + i
                self.holding_registers[reg] = val
                self._update_simulated_telemetry(reg, val)
            return bytes([func_code]) + struct.pack(">HH", start_addr, count)

        else:
            # Illegal Function Code Exception
            return bytes([func_code | 0x80, 0x01])

    def _update_simulated_telemetry(self, reg_addr: int, val: int):
        """Simulates internal Phoenix EZA control loop physics."""
        # If P setpoint was written, mirror close to actual active power
        if reg_addr == HOLDING_REGISTERS["REG_P_SETPOINT_KW"]:
            self.input_registers[INPUT_REGISTERS["REG_ACTUAL_ACTIVE_POWER_KW"]] = max(0, val - 5)
            self.input_registers[INPUT_REGISTERS["REG_ACTUAL_APPARENT_POWER_KVA"]] = val
        elif reg_addr == HOLDING_REGISTERS["REG_Q_CONTROL_MODE"]:
            self.input_registers[INPUT_REGISTERS["REG_ACTIVE_CONTROL_MODE"]] = val
        elif reg_addr == HOLDING_REGISTERS["REG_CMD_CIRCUIT_BREAKER"]:
            if val == 1:
                self.input_registers[INPUT_REGISTERS["REG_BREAKER_STATE"]] = 1
            elif val == 2:
                self.input_registers[INPUT_REGISTERS["REG_BREAKER_STATE"]] = 0
                self.input_registers[INPUT_REGISTERS["REG_ACTUAL_ACTIVE_POWER_KW"]] = 0

    async def start(self):
        """Starts the simulator TCP listener."""
        self.is_running = True
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
        logger.info(f"Phoenix Contact EZA Simulator started on {self.host}:{self.port}")

    async def stop(self):
        """Stops the simulator server."""
        self.is_running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Phoenix Contact EZA Simulator stopped")

    def get_snapshot(self) -> Dict[str, Any]:
        """Returns snapshot of current registers for debugging & UI inspection."""
        return {
            "holding": {k: self.holding_registers[v] for k, v in HOLDING_REGISTERS.items()},
            "input": {k: self.input_registers[v] for k, v in INPUT_REGISTERS.items()}
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sim = PhoenixEZASimulator(host="0.0.0.0", port=5502)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(sim.start())
        print(f"Phoenix Contact EZA Controller Simulator active on port 5502. Press Ctrl+C to stop.")
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(sim.stop())
