"""
Universal Device Driver Registry & Auto-Discovery Prober.
Coordinates Inverters, Smart Meters, and EZA Controllers across all major manufacturers.
"""

import time
import logging
from typing import Dict, Any, List, Optional

from edge.drivers.models import DeviceCategory, ProtocolType, SupportedDeviceSpec, DiagnosticResult
from edge.drivers.base import BaseDeviceDriver
from edge.drivers.inverters.sunspec import SunSpecInverterDriver
from edge.drivers.meters.janitza import JanitzaMeterDriver
from edge.drivers.meters.schneider import SchneiderMeterDriver
from edge.drivers.meters.siemens import SiemensMeterDriver
from edge.drivers.eza_controllers.wago import WagoEzaDriver

logger = logging.getLogger("coneza_device_registry")

# Comprehensive Hardware Support Catalog
SUPPORTED_HARDWARE_CATALOG: List[SupportedDeviceSpec] = [
    # ----------------- Inverters & BESS ----------------- #
    SupportedDeviceSpec(
        category=DeviceCategory.INVERTER,
        manufacturer="SMA Solar Technology",
        model="Sunny Tripower (STP / Core1 / Core2) & Sunny Central",
        protocols=[ProtocolType.SUNSPEC, ProtocolType.MODBUS_TCP],
        default_port=502,
        default_slave_id=126,
        description="Commercial PV & central inverters with SunSpec Model 103 and DER curtailment control.",
        features=["SunSpec Compliant", "Active Power Curtailment", "Q(U) & cos(phi) Regulation", "Speedwire Bridge"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.INVERTER,
        manufacturer="Huawei",
        model="SUN2000 Series (50KTL - 330KTL) & SmartLogger 3000",
        protocols=[ProtocolType.SUNSPEC, ProtocolType.MODBUS_TCP],
        default_port=502,
        default_slave_id=1,
        description="High-efficiency commercial string inverters and park controllers.",
        features=["SunSpec Model 103", "SmartLogger Modbus Gateway", "Dynamic Grid Feed-in Curtailment"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.INVERTER,
        manufacturer="Sungrow",
        model="SG & SH Commercial Series (SG33CX - SG350HX)",
        protocols=[ProtocolType.SUNSPEC, ProtocolType.MODBUS_TCP],
        default_port=502,
        default_slave_id=1,
        description="Utility-scale & commercial PV and hybrid battery inverters.",
        features=["SunSpec DER Control", "Battery Energy Storage System (BESS) Support", "Fast Ramp Gradient"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.INVERTER,
        manufacturer="Fronius",
        model="Symo, Eco, and Tauro Commercial",
        protocols=[ProtocolType.SUNSPEC, ProtocolType.MODBUS_TCP, ProtocolType.REST_API],
        default_port=502,
        default_slave_id=1,
        description="Austrian commercial three-phase inverters with integrated SunSpec Datamanager.",
        features=["SunSpec Float32 / Int16", "Solar.API Telemetry", "Dynamic Peak Manager"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.INVERTER,
        manufacturer="SolarEdge",
        model="Commercial Three-Phase (SE30K - SE100K)",
        protocols=[ProtocolType.SUNSPEC, ProtocolType.MODBUS_TCP],
        default_port=502,
        default_slave_id=1,
        description="Optimizer-based commercial solar inverters with StorEdge interface.",
        features=["SunSpec Alliance Compliant", "Module-Level Telemetry", "Power Limiting & Reactive Power"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.INVERTER,
        manufacturer="Kostal",
        model="PLENTICORE Commercial & PIKO CI",
        protocols=[ProtocolType.SUNSPEC, ProtocolType.MODBUS_TCP],
        default_port=502,
        default_slave_id=71,
        description="German commercial solar & storage inverters with Modbus TCP SunSpec interface.",
        features=["SunSpec Model 103", "BESS DC-Coupling", "Smart Communication Board"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.INVERTER,
        manufacturer="Solinteg",
        model="INTEG M Series (MHT-50K..MHT-75K)",
        protocols=[ProtocolType.SUNSPEC, ProtocolType.MODBUS_TCP],
        default_port=502,
        default_slave_id=1,
        description="Commercial three-phase hybrid PV inverters (up to 75 kW) with fast response and flexible battery integration.",
        features=["SunSpec Compliant", "Integrated DC-Switch", "High-Voltage Battery Port", "Dynamic Feed-in Curtailment"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.INVERTER,
        manufacturer="BYD",
        model="Battery-Box Commercial / Battery-Max Lite (200 kW BESS)",
        protocols=[ProtocolType.SUNSPEC, ProtocolType.MODBUS_TCP],
        default_port=502,
        default_slave_id=1,
        description="High-voltage commercial & industrial lithium-iron-phosphate (LFP) Battery Energy Storage System (BESS).",
        features=["Dynamic Peak Shaving", "Active & Reactive Power Control", "BMS State-of-Charge (SoC) Telemetry", "Fast Ramp Rate"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.INVERTER,
        manufacturer="Universal SunSpec",
        model="Generic SunSpec Alliance (GoodWe, Delta, KACO, etc.)",
        protocols=[ProtocolType.SUNSPEC],
        default_port=502,
        default_slave_id=1,
        description="Standardized SunSpec driver compatible with >90% of global industrial inverters.",
        features=["Auto-Discovery Header", "Standard Models 1, 101, 103, 120-123", "Universal Scale Factors"]
    ),

    # ----------------- Smart Meters & Grid Analyzers ----------------- #
    SupportedDeviceSpec(
        category=DeviceCategory.SMART_METER,
        manufacturer="Janitza Electronics",
        model="UMG 96RM, UMG 604, UMG 509, UMG 512",
        protocols=[ProtocolType.MODBUS_TCP, ProtocolType.MODBUS_RTU],
        default_port=502,
        default_slave_id=1,
        description="Leading German power quality analyzers for Point of Common Coupling (NAP) measurement.",
        features=["Class A / Class S Accuracy", "Harmonics / THD Analysis", "Float32 Real-Time Big-Endian", "VDE-AR-N 4110 Certified"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.SMART_METER,
        manufacturer="Schneider Electric",
        model="PowerLogic PM5100, PM5300, PM5500, PM8000, ION7400",
        protocols=[ProtocolType.MODBUS_TCP, ProtocolType.MODBUS_RTU],
        default_port=502,
        default_slave_id=1,
        description="Revenue-grade energy meters and high-accuracy disturbance recorders.",
        features=["IEC 61557-12 Precision", "High-Speed Capture", "Standard 3000 Series Modbus Map"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.SMART_METER,
        manufacturer="Siemens",
        model="SENTRON PAC3100, PAC3200, PAC4200",
        protocols=[ProtocolType.MODBUS_TCP],
        default_port=502,
        default_slave_id=1,
        description="Industrial multifunction power meters for low and medium-voltage switchgear.",
        features=["Integrated Ethernet Port", "Active & Reactive Power Accuracy Class 0.5S", "Limit Monitoring"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.SMART_METER,
        manufacturer="Phoenix Contact",
        model="EMpro Series (EEM-MA600, MA370)",
        protocols=[ProtocolType.MODBUS_TCP, ProtocolType.REST_API],
        default_port=502,
        default_slave_id=1,
        description="Modern web-enabled energy measurement devices.",
        features=["Web-Based Management", "Direct PLCnext Integration", "Modbus TCP Process Image"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.SMART_METER,
        manufacturer="Eastron / ABB",
        model="SDM630 / ABB M4M, B23",
        protocols=[ProtocolType.MODBUS_TCP, ProtocolType.MODBUS_RTU],
        default_port=502,
        default_slave_id=1,
        description="Compact DIN-rail mid-certified submeters and sub-distribution analyzers.",
        features=["MID B+D Certified", "Bi-directional Metering (Import/Export)", "High Cost-Efficiency"]
    ),

    # ----------------- EZA Power Plant Controllers ----------------- #
    SupportedDeviceSpec(
        category=DeviceCategory.EZA_CONTROLLER,
        manufacturer="Phoenix Contact",
        model="PLCnext Control (AXC F 2152 / 3152 / SOL-SC-PCU)",
        protocols=[ProtocolType.MODBUS_TCP, ProtocolType.IEC_60870_5_104],
        default_port=502,
        default_slave_id=1,
        description="Fully certified German Power Plant Controller according to VDE-AR-N 4110 / 4120.",
        features=["VDE Component Certificate", "Direct Modbus TCP Map (40001..40501)", "IEC 60870-5-104 Telecontrol", "Hot-Standby Redundancy"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.EZA_CONTROLLER,
        manufacturer="WAGO Kontakttechnik",
        model="PFC200 (750-8212 / 8216) & Edge Controller",
        protocols=[ProtocolType.MODBUS_TCP, ProtocolType.IEC_60870_5_104],
        default_port=502,
        default_slave_id=1,
        description="Modular PLC controller with certified VDE-AR-N 4110 / 4120 power plant control library.",
        features=["Codesys / e!COCKPIT Engine", "Telecontrol IEC 60870-5-101/104", "Configurable Q(U) & P(f) Blocks"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.EZA_CONTROLLER,
        manufacturer="meteocontrol",
        model="blue'Log XC / X-Series Power Plant Controller",
        protocols=[ProtocolType.MODBUS_TCP, ProtocolType.IEC_60870_5_104],
        default_port=502,
        default_slave_id=1,
        description="Turnkey power plant controller with integrated monitoring and grid operator interfaces.",
        features=["VDE Certified Controller", "Direct Inverter Closed-Loop Control", "Integrated Telecontrol Gateway"]
    ),
    SupportedDeviceSpec(
        category=DeviceCategory.EZA_CONTROLLER,
        manufacturer="Bachmann electronic",
        model="M1 Controller & Bluecom Grid Gateway",
        protocols=[ProtocolType.MODBUS_TCP, ProtocolType.IEC_60870_5_104],
        default_port=502,
        default_slave_id=1,
        description="High-reliability industrial PLC platform for utility-scale solar and wind parks.",
        features=["Extreme Environmental Hardening", "Sub-Cycle Q Response", "IEC 61400-25 & 61850"]
    ),
]


class DeviceRegistry:
    """Manages drivers and automated probing across all supported hardware."""

    @staticmethod
    def get_catalog() -> List[SupportedDeviceSpec]:
        return SUPPORTED_HARDWARE_CATALOG

    @staticmethod
    def create_driver(
        device_id: str,
        category: str,
        manufacturer: str,
        model: str,
        host: str,
        port: int = 502,
        slave_id: int = 1,
        **kwargs
    ) -> BaseDeviceDriver:
        """Instantiates appropriate driver instance according to category and manufacturer."""
        cat_upper = category.upper()
        mfg_lower = manufacturer.lower()

        if "janitza" in mfg_lower:
            return JanitzaMeterDriver(device_id=device_id, host=host, port=port, slave_id=slave_id, model_series=model, **kwargs)
        elif "schneider" in mfg_lower:
            return SchneiderMeterDriver(device_id=device_id, host=host, port=port, slave_id=slave_id, model_series=model, **kwargs)
        elif "siemens" in mfg_lower:
            return SiemensMeterDriver(device_id=device_id, host=host, port=port, slave_id=slave_id, model_series=model, **kwargs)
        elif "wago" in mfg_lower:
            return WagoEzaDriver(device_id=device_id, host=host, port=port, slave_id=slave_id, model_series=model, **kwargs)
        elif cat_upper in ("INVERTER", "BESS") or any(brand in mfg_lower for brand in ["sma", "huawei", "sungrow", "fronius", "solaredge", "kostal", "solinteg", "byd", "sunspec"]):
            return SunSpecInverterDriver(device_id=device_id, host=host, port=port, slave_id=slave_id, inverter_brand=manufacturer, **kwargs)
        else:
            # Default to SunSpec driver or Janitza based on category
            if cat_upper == "SMART_METER":
                return JanitzaMeterDriver(device_id=device_id, host=host, port=port, slave_id=slave_id, model_series=model, **kwargs)
            return SunSpecInverterDriver(device_id=device_id, host=host, port=port, slave_id=slave_id, inverter_brand=manufacturer, **kwargs)

    @staticmethod
    async def probe_device(host: str, port: int = 502, slave_id: int = 1) -> DiagnosticResult:
        """
        Actively probes an IP/port/slave_id to automatically identify whether the device
        is a SunSpec Inverter, Janitza Meter, Schneider Meter, Siemens Meter, or WAGO Controller.
        """
        start = time.time()

        # Probe 1: SunSpec Inverter (Check 40000 or 50000 for 'SunS')
        sunspec_driver = SunSpecInverterDriver(device_id="probe_temp", host=host, port=port, slave_id=slave_id)
        res_suns = await sunspec_driver.test_connection()
        if res_suns.success:
            return res_suns

        # Probe 2: Siemens SENTRON PAC Meter (Address 1 / 55)
        siemens_driver = SiemensMeterDriver(device_id="probe_temp", host=host, port=port, slave_id=slave_id)
        res_siemens = await siemens_driver.test_connection()
        if res_siemens.success:
            return res_siemens

        # Probe 2: Janitza Power Quality Meter (Address 19028 / 800)
        janitza_driver = JanitzaMeterDriver(device_id="probe_temp", host=host, port=port, slave_id=slave_id)
        res_jan = await janitza_driver.test_connection()
        if res_jan.success:
            return res_jan

        # Probe 3: Schneider Electric Meter (Address 3109 / 3000)
        schneider_driver = SchneiderMeterDriver(device_id="probe_temp", host=host, port=port, slave_id=slave_id)
        res_sch = await schneider_driver.test_connection()
        if res_sch.success:
            return res_sch

        # Probe 4: WAGO EZA Controller (Address 0)
        wago_driver = WagoEzaDriver(device_id="probe_temp", host=host, port=port, slave_id=slave_id)
        res_wago = await wago_driver.test_connection()
        if res_wago.success:
            return res_wago

        latency = round((time.time() - start) * 1000.0, 1)
        return DiagnosticResult(
            success=False,
            latency_ms=latency,
            message=f"No recognized SunSpec, Janitza, Schneider, or WAGO device signature found at {host}:{port} (slave {slave_id})."
        )


device_registry = DeviceRegistry()
