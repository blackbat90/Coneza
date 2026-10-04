import unittest
import asyncio
from edge.drivers.models import DeviceCategory, DeviceSetpoint, ProtocolType
from edge.drivers.inverters.sunspec import SunSpecInverterDriver
from edge.drivers.meters.janitza import JanitzaMeterDriver
from edge.drivers.meters.schneider import SchneiderMeterDriver
from edge.drivers.eza_controllers.wago import WagoEzaDriver
from edge.drivers.registry import device_registry, SUPPORTED_HARDWARE_CATALOG
from backend.database import init_db, get_connection

class TestUniversalDeviceDrivers(unittest.TestCase):
    def setUp(self):
        init_db()
        from backend.main import seed_default_users
        seed_default_users()

    def test_01_hardware_catalog_completeness(self):
        """Verify catalog contains inverters, smart meters, and EZA controllers."""
        catalog = device_registry.get_catalog()
        self.assertGreaterEqual(len(catalog), 10)

        categories = {item.category for item in catalog}
        self.assertIn(DeviceCategory.INVERTER, categories)
        self.assertIn(DeviceCategory.SMART_METER, categories)
        self.assertIn(DeviceCategory.EZA_CONTROLLER, categories)

        manufacturers = [item.manufacturer for item in catalog]
        # Inverters
        self.assertTrue(any("SMA" in m for m in manufacturers))
        self.assertTrue(any("Huawei" in m for m in manufacturers))
        self.assertTrue(any("Sungrow" in m for m in manufacturers))
        self.assertTrue(any("Fronius" in m for m in manufacturers))
        self.assertTrue(any("SolarEdge" in m for m in manufacturers))
        self.assertTrue(any("Kostal" in m for m in manufacturers))
        # Meters
        self.assertTrue(any("Janitza" in m for m in manufacturers))
        self.assertTrue(any("Schneider" in m for m in manufacturers))
        self.assertTrue(any("Siemens" in m for m in manufacturers))
        # EZA Controllers
        self.assertTrue(any("Phoenix Contact" in m for m in manufacturers))
        self.assertTrue(any("WAGO" in m for m in manufacturers))
        self.assertTrue(any("meteocontrol" in m for m in manufacturers))

    def test_02_factory_driver_creation(self):
        """Test creating appropriate driver instances via registry factory."""
        # 1. Inverter
        inv_driver = device_registry.create_driver(
            device_id="inv_sma_01",
            category="INVERTER",
            manufacturer="SMA Solar Technology",
            model="Sunny Tripower Core1",
            host="192.168.1.100",
            port=502,
            slave_id=126
        )
        self.assertIsInstance(inv_driver, SunSpecInverterDriver)
        self.assertEqual(inv_driver.category, DeviceCategory.INVERTER)

        # 2. Janitza Meter
        jan_driver = device_registry.create_driver(
            device_id="meter_pcc_01",
            category="SMART_METER",
            manufacturer="Janitza Electronics",
            model="UMG 96RM",
            host="192.168.1.50",
            port=502,
            slave_id=1
        )
        self.assertIsInstance(jan_driver, JanitzaMeterDriver)
        self.assertEqual(jan_driver.category, DeviceCategory.SMART_METER)

        # 3. Schneider Meter
        sch_driver = device_registry.create_driver(
            device_id="meter_sub_01",
            category="SMART_METER",
            manufacturer="Schneider Electric",
            model="PowerLogic PM5300",
            host="192.168.1.51",
            port=502,
            slave_id=1
        )
        self.assertIsInstance(sch_driver, SchneiderMeterDriver)

        # 4. WAGO EZA Controller
        wago_driver = device_registry.create_driver(
            device_id="eza_wago_01",
            category="EZA_CONTROLLER",
            manufacturer="WAGO Kontakttechnik",
            model="PFC200",
            host="192.168.1.10",
            port=502,
            slave_id=1
        )
        self.assertIsInstance(wago_driver, WagoEzaDriver)
        self.assertEqual(wago_driver.category, DeviceCategory.EZA_CONTROLLER)

    def test_03_sunspec_scale_factors(self):
        """Verify SunSpec power-of-10 scale factor calculations."""
        driver = SunSpecInverterDriver(device_id="test", host="127.0.0.1")
        # 2500 with sf -1 -> 250.0
        self.assertEqual(driver._apply_sf(2500, -1), 250.0)
        # 25 with sf 2 -> 2500.0
        self.assertEqual(driver._apply_sf(25, 2), 2500.0)
        # Invalid / Not Implemented value 0x8000 -> 0.0
        self.assertEqual(driver._apply_sf(0x8000, 0), 0.0)

    def test_04_janitza_float32_decoding(self):
        """Verify IEEE-754 Float32 decoding for Janitza Modbus registers."""
        driver = JanitzaMeterDriver(device_id="test", host="127.0.0.1")
        # 50.0 Hz in IEEE-754 Float32: 0x4248 0x0000
        freq = driver._decode_float32(0x4248, 0x0000)
        self.assertEqual(freq, 50.0)

        # 230.0 V in IEEE-754 Float32: 0x4366 0x0000
        voltage = driver._decode_float32(0x4366, 0x0000)
        self.assertEqual(voltage, 230.0)

    def test_05_wago_setpoint_generation(self):
        """Verify WAGO EZA setpoint simulation dispatching."""
        driver = WagoEzaDriver(device_id="wago_sim", host="127.0.0.1")
        sp = DeviceSetpoint(
            p_limit_kw=2800.0,
            p_limit_percent=93.3,
            q_mode=1,
            cos_phi_setpoint=1.0,
            qu_u1_percent=93.0,
            qu_q1_percent=100.0
        )
        res = asyncio.run(driver.write_setpoints(sp))
        self.assertTrue(res)

    def test_06_database_device_columns(self):
        """Verify devices table contains category, manufacturer, model, and slave_id."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        cols = [r[1] for r in cursor.fetchall()]
        conn.close()

        self.assertIn("device_category", cols)
        self.assertIn("manufacturer", cols)
        self.assertIn("model", cols)
        self.assertIn("slave_id", cols)

    def test_07_api_catalog_endpoint(self):
        """Verify GET /api/devices/catalog returns full catalog to authenticated viewers."""
        from fastapi.testclient import TestClient
        from backend.main import app
        from backend.auth import create_access_token

        client = TestClient(app)
        token = create_access_token(user_id=1, username="admin", role="VIEWER")
        res = client.get("/api/devices/catalog", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        catalog = res.json()
        self.assertGreaterEqual(len(catalog), 10)
        self.assertTrue(any(c["manufacturer"] == "Janitza Electronics" for c in catalog))
        self.assertTrue(any("SMA" in c["manufacturer"] for c in catalog))

if __name__ == "__main__":
    unittest.main()
