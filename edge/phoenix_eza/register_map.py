"""
Phoenix Contact EZA-Regler (Power Generation Plant Controller) Register Map
Conforms to VDE-AR-N 4110 / VDE-AR-N 4120 industrial standard Modbus TCP interface.
Typically running on Phoenix Contact PLCnext Control (AXC F 2152 / AXC 3050 / SOL-SC-PCU / SOL-SA-PCU).
"""

from typing import Dict, Any

# Holding Registers (Function Code 03 / 06 / 16) - Configuration and Setpoints
# Base 0 indexing for Modbus TCP wire protocol, address labels indicate 4xxxx standard notation
HOLDING_REGISTERS = {
    # System Identification & Heartbeat (40001 - 40010)
    "REG_SYSTEM_STATUS": 0,          # 1=System Enabled, 0=Disabled / Standby
    "REG_HEARTBEAT_TIMEOUT_SEC": 1,   # Telecontrol heartbeat watchdog timeout
    "REG_HEARTBEAT_COUNTER": 2,       # Incremented by host/edge to prove liveness
    "REG_GRID_VOLTAGE_NOMINAL": 3,    # Un in Volts (e.g. 20000 V for MV or 400 V for LV)
    "REG_GRID_FREQUENCY_NOMINAL": 4,  # Fn in 0.01 Hz (e.g. 5000 = 50.00 Hz)
    "REG_RATED_ACTIVE_POWER_KW": 5,   # P_r in kW
    "REG_RATED_APPARENT_POWER_KVA": 6,# S_r in kVA

    # Active Power Regulation (40101 - 40120)
    "REG_P_CONTROL_MODE": 100,        # 0=Direct Setpoint (kW), 1=Normalized (0.1%), 2=Scheduler
    "REG_P_SETPOINT_KW": 101,         # Target Active Power Setpoint in kW
    "REG_P_SETPOINT_PERCENT": 102,    # Target Active Power in 0.1% (1000 = 100.0%)
    "REG_P_MAX_FEED_IN_LIMIT_KW": 103,# Grid operator maximal allowed active feed-in (P_AV)
    "REG_P_RAMP_RATE_KW_PER_SEC": 104,# Max allowable power ramp gradient (kW/s)
    "REG_P_FREQUENCY_DROOP_EN": 105,  # 1=Enable P(f) primary response, 0=Disable

    # Reactive Power Regulation (40201 - 40250)
    "REG_Q_CONTROL_MODE": 200,        # 0=cos(phi) fixed, 1=Q(U) curve, 2=Q fixed (kvar), 3=cos(phi)(P)
    "REG_COS_PHI_SETPOINT": 201,      # Scaled by 1000: 1000 = 1.000, 950 = 0.950
    "REG_COS_PHI_EXCITATION": 202,    # 0=Overexcited (inductive), 1=Underexcited (capacitive)
    "REG_Q_SETPOINT_KVAR": 203,       # Fixed Q setpoint in kvar (signed int16)
    "REG_Q_MAX_INDUCTIVE_KVAR": 204,  # Maximum inductive reactive power capability
    "REG_Q_MAX_CAPACITIVE_KVAR": 205, # Maximum capacitive reactive power capability
    "REG_Q_U_TIME_CONSTANT_SEC": 206, # PT1 smoothing filter for Q(U) response

    # Q(U) Characteristic Curve Breakpoints (40220 - 40235)
    # 4 Breakpoints: (U1, Q1), (U2, Q2), (U3, Q3), (U4, Q4)
    # Voltage in 0.1% Un (e.g. 900 = 90.0% Un), Q in 0.1% Qmax (-1000..+1000)
    "REG_QU_U1": 220,                 # Typically 930 (93.0% Un)
    "REG_QU_Q1": 221,                 # Typically +1000 (+100.0% capacitive)
    "REG_QU_U2": 222,                 # Typically 970 (97.0% Un)
    "REG_QU_Q2": 223,                 # Typically 0 (deadband start)
    "REG_QU_U3": 224,                 # Typically 1030 (103.0% Un)
    "REG_QU_Q3": 225,                 # Typically 0 (deadband end)
    "REG_QU_U4": 226,                 # Typically 1070 (107.0% Un)
    "REG_QU_Q4": 227,                 # Typically -1000 (-100.0% inductive)

    # Frequency-Dependent Active Power P(f) Parameters (40301 - 40310)
    "REG_PF_OVERFREQ_START": 300,     # In 0.01 Hz (e.g. 5020 = 50.20 Hz)
    "REG_PF_OVERFREQ_DROOP": 301,     # Droop s in 0.1% (e.g. 40 = 4.0% droop)
    "REG_PF_UNDERFREQ_START": 302,    # In 0.01 Hz (e.g. 4980 = 49.80 Hz)
    "REG_PF_UNDERFREQ_DROOP": 303,    # Droop s in 0.1% (e.g. 40 = 4.0% droop)

    # Grid Protection & Decoupling Relays (40401 - 40415)
    "REG_PROT_U_MAX_PERCENT": 400,    # U> threshold in 0.1% Un (e.g. 1100 = 110%)
    "REG_PROT_U_MAX_TRIP_MS": 401,    # U> trip delay in ms (e.g. 100 ms)
    "REG_PROT_U_MIN_PERCENT": 402,    # U< threshold in 0.1% Un (e.g. 800 = 80%)
    "REG_PROT_U_MIN_TRIP_MS": 403,    # U< trip delay in ms (e.g. 3000 ms)
    "REG_PROT_F_MAX_HZ": 404,         # f> threshold in 0.01 Hz (e.g. 5150 = 51.50 Hz)
    "REG_PROT_F_MIN_HZ": 405,         # f< threshold in 0.01 Hz (e.g. 4750 = 47.50 Hz)

    # Circuit Breaker & Safety Commands (40501)
    "REG_CMD_CIRCUIT_BREAKER": 500,   # 1=Close Breaker, 2=Open/Trip Breaker, 0=None
    "REG_CMD_RESET_ALARMS": 501,      # 1=Reset latched alarms
}

# Input Registers (Function Code 04) - Real-time Measurements & Telemetry
INPUT_REGISTERS = {
    # Live Measurement Values (30001 - 30020)
    "REG_ACTUAL_ACTIVE_POWER_KW": 0,    # Actual P in kW (signed)
    "REG_ACTUAL_REACTIVE_POWER_KVAR": 1,# Actual Q in kvar (signed)
    "REG_ACTUAL_APPARENT_POWER_KVA": 2, # Actual S in kVA
    "REG_ACTUAL_COS_PHI": 3,            # Actual cos(phi) scaled x1000
    "REG_ACTUAL_VOLTAGE_L12_VOLTS": 4,  # Actual U_L12 (V)
    "REG_ACTUAL_VOLTAGE_L23_VOLTS": 5,  # Actual U_L23 (V)
    "REG_ACTUAL_VOLTAGE_L31_VOLTS": 6,  # Actual U_L31 (V)
    "REG_ACTUAL_FREQUENCY_HZ": 7,       # Frequency in 0.01 Hz (e.g. 5002 = 50.02 Hz)
    
    # Operational Status & Diagnostics (30030 - 30040)
    "REG_CONTROLLER_STATE": 30,         # 0=Init, 1=Normal / Regulating, 2=Curtailed, 3=Tripped/Alarm
    "REG_BREAKER_STATE": 31,            # 0=Open, 1=Closed, 2=Tripped
    "REG_ACTIVE_CONTROL_MODE": 32,      # Currently executed Q control mode
    "REG_CURTAILMENT_ACTIVE": 33,       # 1=Grid operator curtailment in effect, 0=None
    "REG_ALARM_CODE_BITMASK": 34,       # Bit 0: Overvoltage, Bit 1: Undervoltage, Bit 2: Overfreq, Bit 3: Comm Lost
}

Q_MODES_DESCRIPTION = {
    0: "cos(phi) fixed power factor",
    1: "Q(U) voltage-dependent reactive power curve",
    2: "Q fixed reactive power (kvar)",
    3: "cos(phi)(P) power-dependent power factor curve"
}

def get_holding_register_address(name: str) -> int:
    if name not in HOLDING_REGISTERS:
        raise KeyError(f"Unknown holding register: {name}")
    return HOLDING_REGISTERS[name]

def get_input_register_address(name: str) -> int:
    if name not in INPUT_REGISTERS:
        raise KeyError(f"Unknown input register: {name}")
    return INPUT_REGISTERS[name]
