"""EEP-76: driver-only regressions; no service imports, .env, database or sockets."""
import unittest
from unittest.mock import patch
from edge.phoenix_eza.controller import PhoenixEZAControllerClient


class SignedConfigurationTests(unittest.IsolatedAsyncioTestCase):
    async def test_round_trip_all_q_points_and_signed_boundaries(self):
        client = PhoenixEZAControllerClient()
        registers = {}

        async def write(address, value):
            registers[address] = value & 0xffff

        async def read(address, count):
            return [registers.get(a, 0) for a in range(address, address + count)]

        with patch.object(client, "write_holding_register", side_effect=write), patch.object(
            client, "read_holding_registers", side_effect=read
        ), patch.object(client, "_execute_modbus_request", side_effect=AssertionError("Network forbidden")):
            for value in (-32768, -100, -1, 0, 1, 32767):
                config = {"q_setpoint_kvar": value, "q_u_curve": {
                    **{f"q{i}_percent": value / 10 for i in range(1, 5)},
                    **{f"u{i}_percent": 100 for i in range(1, 5)},
                }}
                await client.apply_configuration(config)
                actual = await client.read_active_configuration()
                self.assertEqual(actual["q_setpoint_kvar"], value)
                self.assertEqual(actual["q_u_curve"], config["q_u_curve"])
            await client.apply_configuration({"q_u_curve": {"q4_percent": -100}})
            self.assertEqual((await client.read_active_configuration())["q_u_curve"]["q4_percent"], -100)
