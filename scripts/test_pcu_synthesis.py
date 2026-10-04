import json
import os
from typing import Dict, Any, List, Tuple

def test_synthesis():
    extracted = {
        "active_power_kw": 2500.0,
        "grid_voltage_v": 20000.0,
        "apparent_power_kva": 2631.6,
        "transformer_uk_percent": 6.0,
        "feed_in_limit_kw": 2400.0,
        "reactive_mode": "Q(U)",
        "grid_operator": "Netze BW GmbH (EnBW)",
        "nap": "Umspannwerk EnBW / Übergabestation 20kV",
        "plant_name": "Solar & BESS Park EnBW (NAP 20kV)"
    }
    
    active_kw = float(extracted.get("active_power_kw") or 2500.0)
    voltage_v = float(extracted.get("grid_voltage_v") or 20000.0)
    apparent_kva = float(extracted.get("apparent_power_kva") or round(active_kw / 0.95, 1))
    feed_in_limit_kw = float(extracted.get("feed_in_limit_kw") or active_kw)
    reactive_mode_str = str(extracted.get("reactive_mode") or "Q(U)")
    q_mode_code = 1 if "Q(U)" in reactive_mode_str or "qu" in reactive_mode_str.lower() else (0 if "cos" in reactive_mode_str.lower() else 2)
    cos_phi = float(extracted.get("cos_phi") or 1.0)
    
    recommended_config = {
        "rated_active_power_kw": active_kw,
        "rated_apparent_power_kva": apparent_kva,
        "grid_voltage_nominal_volts": voltage_v,
        "p_max_feed_in_limit_kw": feed_in_limit_kw,
        "p_setpoint_kw": feed_in_limit_kw,
        "p_ramp_rate_kw_per_sec": 100.0,
        "q_control_mode": q_mode_code,
        "cos_phi_setpoint": cos_phi,
        "q_setpoint_kvar": 0.0,
        "q_u_curve": {
            "u1_percent": 93.0, "q1_percent": 100.0,
            "u2_percent": 97.0, "q2_percent": 0.0,
            "u3_percent": 103.0, "q3_percent": 0.0,
            "u4_percent": 107.0, "q4_percent": -100.0
        },
        "p_f_droop": {
            "overfreq_start_hz": 50.2,
            "overfreq_droop_percent": 4.0,
            "underfreq_start_hz": 49.8,
            "underfreq_droop_percent": 4.0
        },
        "protection": {
            "u_max_percent": 110.0,
            "u_max_trip_ms": 100.0,
            "u_min_percent": 80.0,
            "u_min_trip_ms": 3000.0,
            "f_max_hz": 51.5,
            "f_min_hz": 47.5
        }
    }
    
    print("Synthesized Recommended Config successfully!")
    print("Keys in recommended_config:", list(recommended_config.keys()))

test_synthesis()
