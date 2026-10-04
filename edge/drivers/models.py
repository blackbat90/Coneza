"""
Standardized Data Models for Universal Inverter, Smart Meter, and EZA Regulator Drivers.
Conforms to VDE-AR-N 4110 / 4120 grid interconnection standards and SunSpec Modbus specifications.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class DeviceCategory(str, Enum):
    INVERTER = "INVERTER"            # PV / Hybrid / Battery Inverters (SMA, Huawei, Sungrow, Fronius, SolarEdge, etc.)
    SMART_METER = "SMART_METER"      # Grid Measurement / Power Quality Analyzers (Janitza, Schneider, Siemens, etc.)
    EZA_CONTROLLER = "EZA_CONTROLLER"# Power Plant Controllers (Phoenix Contact, WAGO, meteocontrol, Bachmann, etc.)


class ProtocolType(str, Enum):
    MODBUS_TCP = "MODBUS_TCP"
    MODBUS_RTU = "MODBUS_RTU"
    SUNSPEC = "SUNSPEC"
    IEC_60870_5_104 = "IEC_60870_5_104"
    REST_API = "REST_API"


class DeviceTelemetry(BaseModel):
    """Normalized real-time electrical telemetry across any manufacturer."""
    device_id: str
    timestamp: str
    is_online: bool = True

    # Three-Phase Voltages (V)
    u_l1_n_volts: Optional[float] = None
    u_l2_n_volts: Optional[float] = None
    u_l3_n_volts: Optional[float] = None
    u_l1_l2_volts: Optional[float] = None
    u_l2_l3_volts: Optional[float] = None
    u_l3_l1_volts: Optional[float] = None
    u_avg_volts: Optional[float] = None

    # Three-Phase Currents (A)
    i_l1_amps: Optional[float] = None
    i_l2_amps: Optional[float] = None
    i_l3_amps: Optional[float] = None
    i_total_amps: Optional[float] = None

    # Power Measurements
    p_active_kw: float = 0.0          # Active power (+ = feed-in / generation, - = consumption)
    q_reactive_kvar: float = 0.0      # Reactive power (+ = capacitive, - = inductive)
    s_apparent_kva: float = 0.0       # Apparent power
    power_factor: float = 1.0         # cos(phi)
    frequency_hz: float = 50.0        # Grid frequency

    # Energy Counters (kWh / kvarh)
    energy_active_export_kwh: Optional[float] = None
    energy_active_import_kwh: Optional[float] = None

    # Inverter / Storage Specifics
    dc_power_kw: Optional[float] = None
    dc_voltage_v: Optional[float] = None
    battery_soc_percent: Optional[float] = None
    operating_state: str = "NORMAL"   # STANDBY, RUNNING, FAULT, CURTAILED

    # Power Quality & Alarms
    thd_u_percent: Optional[float] = None
    thd_i_percent: Optional[float] = None
    active_alarms: List[str] = Field(default_factory=list)


class DeviceSetpoint(BaseModel):
    """Standardized setpoint commands sent to Inverters or EZA Controllers."""
    # Active Power Curtailment
    p_limit_kw: Optional[float] = None
    p_limit_percent: Optional[float] = None  # 0.0 - 100.0%
    p_ramp_rate_kw_per_sec: Optional[float] = 100.0

    # Reactive Power Control
    q_mode: int = 1  # 0=cosPhi, 1=Q(U), 2=Fixed Q, 3=cosPhi(P)
    cos_phi_setpoint: Optional[float] = 1.0
    q_setpoint_kvar: Optional[float] = 0.0

    # Q(U) Curve Breakpoints (U in % Un, Q in % Qmax)
    qu_u1_percent: Optional[float] = 93.0
    qu_q1_percent: Optional[float] = 100.0
    qu_u2_percent: Optional[float] = 97.0
    qu_q2_percent: Optional[float] = 0.0
    qu_u3_percent: Optional[float] = 103.0
    qu_q3_percent: Optional[float] = 0.0
    qu_u4_percent: Optional[float] = 107.0
    qu_q4_percent: Optional[float] = -100.0

    # Grid Protection
    trip_breaker: Optional[bool] = False
    reset_alarms: Optional[bool] = False


class DiagnosticResult(BaseModel):
    success: bool
    latency_ms: float
    detected_manufacturer: Optional[str] = None
    detected_model: Optional[str] = None
    detected_serial: Optional[str] = None
    protocol: ProtocolType = ProtocolType.MODBUS_TCP
    message: str = ""
    raw_probe_data: Dict[str, Any] = Field(default_factory=dict)


class SupportedDeviceSpec(BaseModel):
    category: DeviceCategory
    manufacturer: str
    model: str
    protocols: List[ProtocolType]
    default_port: int = 502
    default_slave_id: int = 1
    description: str
    features: List[str]
