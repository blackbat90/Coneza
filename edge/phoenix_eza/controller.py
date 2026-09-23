"""
Phoenix Contact EZA Controller Modbus TCP Driver & Communicator
Interacts with physical Phoenix Contact PLCnext EZA-Regler or local Simulator.
Implements safe writing, read-back verification, and live telemetry polling.
"""

import asyncio
import logging
import struct
from typing import Dict, Any, List, Optional, Tuple
from edge.phoenix_eza.register_map import (
    HOLDING_REGISTERS, INPUT_REGISTERS, Q_MODES_DESCRIPTION,
    get_holding_register_address, get_input_register_address
)

logger = logging.getLogger("phoenix_eza_controller")

class PhoenixEZAControllerClient:
    """
    Client driver connecting to Phoenix Contact EZA Controller via Modbus TCP.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5502, unit_id: int = 1, timeout: float = 3.0):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self._trans_id = 0

    def _next_trans_id(self) -> int:
        self._trans_id = (self._trans_id + 1) & 0xFFFF
        return self._trans_id

    async def _execute_modbus_request(self, pdu: bytes) -> bytes:
        """Sends a Modbus TCP request ADU and returns response PDU."""
        trans_id = self._next_trans_id()
        proto_id = 0
        pdu_len = len(pdu) + 1  # includes unit_id
        mbap = struct.pack(">HHHB", trans_id, proto_id, pdu_len, self.unit_id)
        request_adu = mbap + pdu

        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port),
            timeout=self.timeout
        )

        try:
            writer.write(request_adu)
            await writer.drain()

            # Read response MBAP (7 bytes)
            resp_mbap = await asyncio.wait_for(reader.read(7), timeout=self.timeout)
            if len(resp_mbap) < 7:
                raise ConnectionError(f"Incomplete Modbus MBAP response from {self.host}:{self.port}")

            r_trans_id, r_proto_id, r_pdu_len, r_unit_id = struct.unpack(">HHHB", resp_mbap)
            resp_pdu = await asyncio.wait_for(reader.read(r_pdu_len - 1), timeout=self.timeout)

            # Check for Modbus exception (high bit set on function code)
            func_code = resp_pdu[0]
            if func_code & 0x80:
                exc_code = resp_pdu[1] if len(resp_pdu) > 1 else 0
                raise RuntimeError(f"Modbus Exception 0x{exc_code:02X} for Function 0x{func_code & 0x7F:02X}")

            return resp_pdu
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def test_connection(self) -> Dict[str, Any]:
        """Tests TCP connectivity and basic register read."""
        try:
            telemetry = await self.read_telemetry()
            return {
                "connected": True,
                "host": self.host,
                "port": self.port,
                "controller_state": telemetry.get("controller_state_text", "Unknown"),
                "actual_active_power_kw": telemetry.get("actual_active_power_kw", 0),
                "grid_voltage_volts": telemetry.get("grid_voltage_l12_volts", 0),
            }
        except Exception as e:
            return {
                "connected": False,
                "host": self.host,
                "port": self.port,
                "error": str(e)
            }

    async def read_holding_registers(self, start_addr: int, count: int) -> List[int]:
        """FC 03: Read Holding Registers."""
        pdu = bytes([0x03]) + struct.pack(">HH", start_addr, count)
        resp_pdu = await self._execute_modbus_request(pdu)
        byte_count = resp_pdu[1]
        vals = struct.unpack(f">{count}H", resp_pdu[2:2 + byte_count])
        return list(vals)

    async def read_input_registers(self, start_addr: int, count: int) -> List[int]:
        """FC 04: Read Input Registers."""
        pdu = bytes([0x04]) + struct.pack(">HH", start_addr, count)
        resp_pdu = await self._execute_modbus_request(pdu)
        byte_count = resp_pdu[1]
        vals = struct.unpack(f">{count}H", resp_pdu[2:2 + byte_count])
        return list(vals)

    async def write_holding_register(self, reg_addr: int, value: int):
        """FC 06: Write Single Holding Register."""
        pdu = bytes([0x06]) + struct.pack(">HH", reg_addr, value & 0xFFFF)
        await self._execute_modbus_request(pdu)

    async def write_multiple_holding_registers(self, start_addr: int, values: List[int]):
        """FC 16 (0x10): Write Multiple Holding Registers."""
        count = len(values)
        byte_count = count * 2
        packed_vals = struct.pack(f">{count}H", *(v & 0xFFFF for v in values))
        pdu = bytes([0x10]) + struct.pack(">HHB", start_addr, count, byte_count) + packed_vals
        await self._execute_modbus_request(pdu)

    async def read_telemetry(self) -> Dict[str, Any]:
        """Fetches live real-time operating measurements from the EZA controller."""
        # Read measurements block (0..7)
        meas_vals = await self.read_input_registers(0, 8)
        # Read status block (30..34)
        status_vals = await self.read_input_registers(30, 5)

        p_act = meas_vals[0]
        q_act = meas_vals[1]
        # Convert signed 16-bit
        if q_act > 32767:
            q_act -= 65536

        state_code = status_vals[0]
        state_map = {0: "INITIALIZING", 1: "ONLINE_REGULATING", 2: "CURTAILED", 3: "ALARM_TRIPPED"}
        breaker_code = status_vals[1]
        breaker_map = {0: "OPEN", 1: "CLOSED", 2: "FAULT_TRIPPED"}

        return {
            "actual_active_power_kw": p_act,
            "actual_reactive_power_kvar": q_act,
            "actual_apparent_power_kva": meas_vals[2],
            "actual_cos_phi": meas_vals[3] / 1000.0,
            "grid_voltage_l12_volts": meas_vals[4],
            "grid_voltage_l23_volts": meas_vals[5],
            "grid_voltage_l31_volts": meas_vals[6],
            "grid_frequency_hz": meas_vals[7] / 100.0,
            "controller_state_code": state_code,
            "controller_state_text": state_map.get(state_code, "UNKNOWN"),
            "breaker_state_code": breaker_code,
            "breaker_state_text": breaker_map.get(breaker_code, "UNKNOWN"),
            "active_control_mode_code": status_vals[2],
            "active_control_mode_text": Q_MODES_DESCRIPTION.get(status_vals[2], "Unknown"),
            "curtailment_active": bool(status_vals[3]),
            "alarm_code_bitmask": status_vals[4],
        }

    @staticmethod
    def _signed16(value: int) -> int:
        return value - 65536 if value & 0x8000 else value

    async def read_active_configuration(self) -> Dict[str, Any]:
        """Reads current setpoints and regulation curves from holding registers."""
        sys_vals = await self.read_holding_registers(0, 7)
        p_vals = await self.read_holding_registers(100, 6)
        q_vals = await self.read_holding_registers(200, 7)
        qu_curve = await self.read_holding_registers(220, 8)
        pf_vals = await self.read_holding_registers(300, 4)
        prot_vals = await self.read_holding_registers(400, 6)

        return {
            "system_status": sys_vals[0],
            "grid_voltage_nominal_volts": sys_vals[3],
            "grid_frequency_nominal_hz": sys_vals[4] / 100.0,
            "rated_active_power_kw": sys_vals[5],
            "rated_apparent_power_kva": sys_vals[6],
            "p_control_mode": p_vals[0],
            "p_setpoint_kw": p_vals[1],
            "p_max_feed_in_limit_kw": p_vals[3],
            "p_ramp_rate_kw_per_sec": p_vals[4],
            "q_control_mode": q_vals[0],
            "q_control_mode_text": Q_MODES_DESCRIPTION.get(q_vals[0], "Unknown"),
            "cos_phi_setpoint": q_vals[1] / 1000.0,
            "q_setpoint_kvar": self._signed16(q_vals[3]),
            "q_u_curve": {
                "u1_percent": qu_curve[0] / 10.0, "q1_percent": self._signed16(qu_curve[1]) / 10.0,
                "u2_percent": qu_curve[2] / 10.0, "q2_percent": self._signed16(qu_curve[3]) / 10.0,
                "u3_percent": qu_curve[4] / 10.0, "q3_percent": self._signed16(qu_curve[5]) / 10.0,
                "u4_percent": qu_curve[6] / 10.0, "q4_percent": self._signed16(qu_curve[7]) / 10.0,
            },
            "p_f_droop": {
                "overfreq_start_hz": pf_vals[0] / 100.0,
                "overfreq_droop_percent": pf_vals[1] / 10.0,
                "underfreq_start_hz": pf_vals[2] / 100.0,
                "underfreq_droop_percent": pf_vals[3] / 10.0,
            },
            "protection": {
                "u_max_percent": prot_vals[0] / 10.0,
                "u_max_trip_ms": prot_vals[1],
                "u_min_percent": prot_vals[2] / 10.0,
                "u_min_trip_ms": prot_vals[3],
                "f_max_hz": prot_vals[4] / 100.0,
                "f_min_hz": prot_vals[5] / 100.0,
            }
        }

    async def apply_configuration(self, config: Dict[str, Any], verify: bool = True) -> Dict[str, Any]:
        """
        Translates structured configuration parameters and writes to Phoenix EZA registers.
        Performs atomic read-back verification to guarantee compliance.
        """
        registers_to_write: Dict[int, int] = {}
        verification_log: List[Dict[str, Any]] = []

        # System & Ratings
        if "rated_active_power_kw" in config:
            registers_to_write[HOLDING_REGISTERS["REG_RATED_ACTIVE_POWER_KW"]] = int(config["rated_active_power_kw"])
        if "rated_apparent_power_kva" in config:
            registers_to_write[HOLDING_REGISTERS["REG_RATED_APPARENT_POWER_KVA"]] = int(config["rated_apparent_power_kva"])
        if "grid_voltage_nominal_volts" in config:
            registers_to_write[HOLDING_REGISTERS["REG_GRID_VOLTAGE_NOMINAL"]] = int(config["grid_voltage_nominal_volts"])

        # Active Power Setpoints
        if "p_max_feed_in_limit_kw" in config:
            registers_to_write[HOLDING_REGISTERS["REG_P_MAX_FEED_IN_LIMIT_KW"]] = int(config["p_max_feed_in_limit_kw"])
        if "p_setpoint_kw" in config:
            registers_to_write[HOLDING_REGISTERS["REG_P_SETPOINT_KW"]] = int(config["p_setpoint_kw"])
        if "p_ramp_rate_kw_per_sec" in config:
            registers_to_write[HOLDING_REGISTERS["REG_P_RAMP_RATE_KW_PER_SEC"]] = int(config["p_ramp_rate_kw_per_sec"])

        # Reactive Power Mode & Parameters
        if "q_control_mode" in config:
            registers_to_write[HOLDING_REGISTERS["REG_Q_CONTROL_MODE"]] = int(config["q_control_mode"])
        if "cos_phi_setpoint" in config:
            registers_to_write[HOLDING_REGISTERS["REG_COS_PHI_SETPOINT"]] = int(round(float(config["cos_phi_setpoint"]) * 1000))
        if "q_setpoint_kvar" in config:
            registers_to_write[HOLDING_REGISTERS["REG_Q_SETPOINT_KVAR"]] = int(config["q_setpoint_kvar"]) & 0xFFFF

        # Q(U) Curve Points
        qu = config.get("q_u_curve", {})
        if "u1_percent" in qu: registers_to_write[HOLDING_REGISTERS["REG_QU_U1"]] = int(round(float(qu["u1_percent"]) * 10))
        if "q1_percent" in qu: registers_to_write[HOLDING_REGISTERS["REG_QU_Q1"]] = int(round(float(qu["q1_percent"]) * 10)) & 0xFFFF
        if "u2_percent" in qu: registers_to_write[HOLDING_REGISTERS["REG_QU_U2"]] = int(round(float(qu["u2_percent"]) * 10))
        if "q2_percent" in qu: registers_to_write[HOLDING_REGISTERS["REG_QU_Q2"]] = int(round(float(qu["q2_percent"]) * 10)) & 0xFFFF
        if "u3_percent" in qu: registers_to_write[HOLDING_REGISTERS["REG_QU_U3"]] = int(round(float(qu["u3_percent"]) * 10))
        if "q3_percent" in qu: registers_to_write[HOLDING_REGISTERS["REG_QU_Q3"]] = int(round(float(qu["q3_percent"]) * 10)) & 0xFFFF
        if "u4_percent" in qu: registers_to_write[HOLDING_REGISTERS["REG_QU_U4"]] = int(round(float(qu["u4_percent"]) * 10))
        if "q4_percent" in qu: registers_to_write[HOLDING_REGISTERS["REG_QU_Q4"]] = int(round(float(qu["q4_percent"]) * 10)) & 0xFFFF

        # Frequency Control P(f)
        pf = config.get("p_f_droop", {})
        if "overfreq_start_hz" in pf:
            registers_to_write[HOLDING_REGISTERS["REG_PF_OVERFREQ_START"]] = int(round(float(pf["overfreq_start_hz"]) * 100))
        if "overfreq_droop_percent" in pf:
            registers_to_write[HOLDING_REGISTERS["REG_PF_OVERFREQ_DROOP"]] = int(round(float(pf["overfreq_droop_percent"]) * 10))

        # Protection Settings
        prot = config.get("protection", {})
        if "u_max_percent" in prot:
            registers_to_write[HOLDING_REGISTERS["REG_PROT_U_MAX_PERCENT"]] = int(round(float(prot["u_max_percent"]) * 10))
        if "u_max_trip_ms" in prot:
            registers_to_write[HOLDING_REGISTERS["REG_PROT_U_MAX_TRIP_MS"]] = int(prot["u_max_trip_ms"])
        if "u_min_percent" in prot:
            registers_to_write[HOLDING_REGISTERS["REG_PROT_U_MIN_PERCENT"]] = int(round(float(prot["u_min_percent"]) * 10))
        if "u_min_trip_ms" in prot:
            registers_to_write[HOLDING_REGISTERS["REG_PROT_U_MIN_TRIP_MS"]] = int(prot["u_min_trip_ms"])
        if "f_max_hz" in prot:
            registers_to_write[HOLDING_REGISTERS["REG_PROT_F_MAX_HZ"]] = int(round(float(prot["f_max_hz"]) * 100))
        if "f_min_hz" in prot:
            registers_to_write[HOLDING_REGISTERS["REG_PROT_F_MIN_HZ"]] = int(round(float(prot["f_min_hz"]) * 100))

        # Execute Writes
        for addr, val in registers_to_write.items():
            await self.write_holding_register(addr, val)

        # Verification step
        all_matched = True
        if verify:
            for addr, target_val in registers_to_write.items():
                read_back = (await self.read_holding_registers(addr, 1))[0]
                matched = (read_back == (target_val & 0xFFFF))
                if not matched:
                    all_matched = False
                verification_log.append({
                    "register_address": addr,
                    "target_value": target_val,
                    "read_back_value": read_back,
                    "matched": matched
                })

        return {
            "success": all_matched,
            "registers_updated": len(registers_to_write),
            "verification_verified": verify,
            "verification_log": verification_log,
            "target_host": f"{self.host}:{self.port}"
        }
