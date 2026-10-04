"""
Test Suite for Phoenix Contact EZA Controller Modbus Driver & Simulator
"""

import asyncio
import unittest
from edge.phoenix_eza.simulator import PhoenixEZASimulator
from edge.phoenix_eza.controller import PhoenixEZAControllerClient
from edge.phoenix_eza.register_map import HOLDING_REGISTERS

class TestPhoenixEZAModbus(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Start local simulator on port 5510 for isolation
        self.port = 5510
        self.sim = PhoenixEZASimulator(host="127.0.0.1", port=self.port)
        await self.sim.start()
        self.client = PhoenixEZAControllerClient(host="127.0.0.1", port=self.port)

    async def asyncTearDown(self):
        await self.client.close()
        await self.sim.stop()

    async def test_controller_connectivity_and_telemetry(self):
        conn = await self.client.test_connection()
        self.assertTrue(conn["connected"])
        self.assertEqual(conn["controller_state"], "ONLINE_REGULATING")

        telemetry = await self.client.read_telemetry()
        self.assertEqual(telemetry["controller_state_text"], "ONLINE_REGULATING")
        self.assertEqual(telemetry["breaker_state_text"], "CLOSED")
        self.assertAlmostEqual(telemetry["grid_frequency_hz"], 50.01, places=1)
        self.assertGreater(telemetry["grid_voltage_l12_volts"], 19000)

    async def test_holding_registers_read_and_apply_config(self):
        config_payload = {
            "rated_active_power_kw": 2500,
            "rated_apparent_power_kva": 2750,
            "grid_voltage_nominal_volts": 20000,
            "p_max_feed_in_limit_kw": 2400,
            "p_setpoint_kw": 2400,
            "p_ramp_rate_kw_per_sec": 80,
            "q_control_mode": 1, # Q(U) curve
            "q_u_curve": {
                "u1_percent": 93.0, "q1_percent": 100.0,
                "u2_percent": 97.0, "q2_percent": 0.0,
                "u3_percent": 103.0, "q3_percent": 0.0,
                "u4_percent": 107.0, "q4_percent": -100.0,
            },
            "p_f_droop": {
                "overfreq_start_hz": 50.20,
                "overfreq_droop_percent": 4.0,
            },
            "protection": {
                "u_max_percent": 110.0,
                "u_max_trip_ms": 100,
                "u_min_percent": 80.0,
                "u_min_trip_ms": 3000,
            }
        }

        # Apply configuration with atomic read-back verification
        result = await self.client.apply_configuration(config_payload, verify=True)
        self.assertTrue(result["success"])
        self.assertGreater(result["registers_updated"], 10)
        self.assertTrue(all(item["matched"] for item in result["verification_log"]))

        # Verify holding registers on the simulator
        active_config = await self.client.read_active_configuration()
        self.assertEqual(active_config["p_max_feed_in_limit_kw"], 2400)
        self.assertEqual(active_config["p_setpoint_kw"], 2400)
        self.assertEqual(active_config["q_control_mode"], 1)
        self.assertEqual(active_config["q_u_curve"]["u1_percent"], 93.0)
        self.assertEqual(active_config["q_u_curve"]["q1_percent"], 100.0)

    async def test_emergency_trip(self):
        # Send emergency trip command (value 2 to REG_CMD_CIRCUIT_BREAKER)
        await self.client.write_holding_register(HOLDING_REGISTERS["REG_CMD_CIRCUIT_BREAKER"], 2)
        telemetry = await self.client.read_telemetry()
        self.assertEqual(telemetry["breaker_state_text"], "OPEN")
        self.assertEqual(telemetry["actual_active_power_kw"], 0)

if __name__ == "__main__":
    unittest.main()
