"""
VNB TAB-Preset Engine for Coneza.
Preconfigured Technical Connection Rules (TAB Mittelspannung nach VDE-AR-N 4110)
for major German Distribution System Operators (DSOs / VNB).
Directly implements Confluence Requirement: 'Preconfigure TAB from network operators'.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class VnbTabProfile(BaseModel):
    dso_id: str
    dso_name: str
    region: str
    grid_voltage_level: str = "Mittelspannung (10 kV - 30 kV)"
    vde_standard: str = "VDE-AR-N 4110:2018-11"
    description: str
    q_control_mode: int = 1  # 1 = Q(U), 2 = cosPhi(P), 3 = Q-Festwert
    q_u_curve: Dict[str, float]
    p_f_droop: Dict[str, Any]
    protection: Dict[str, Any]
    telemetry_protocol: str = "IEC 60870-5-104 / Modbus TCP"
    curtailment_steps_percent: List[int] = [100, 60, 30, 0]
    special_requirements: List[str] = Field(default_factory=list)


# Predefined profiles derived from German DSO TAB Mittelspannung rules
VNB_TAB_PRESETS: Dict[str, VnbTabProfile] = {
    "bayernwerk": VnbTabProfile(
        dso_id="bayernwerk",
        dso_name="Bayernwerk Netz GmbH",
        region="Bayern",
        description="Standard TAB Mittelspannung Bayernwerk. Dynamische Q(U)-Regelung mit symmetrischem Totband und schneller Frequenzstützung P(f).",
        q_control_mode=1,
        q_u_curve={
            "u1_percent": 92.0, "q1_percent": 33.0,
            "u2_percent": 97.0, "q2_percent": 0.0,
            "u3_percent": 103.0, "q3_percent": 0.0,
            "u4_percent": 108.0, "q4_percent": -33.0
        },
        p_f_droop={
            "overfreq_start_hz": 50.20,
            "overfreq_droop_percent": 5.0,
            "underfreq_start_hz": 49.80,
            "underfreq_droop_percent": 5.0
        },
        protection={
            "u_max_percent": 115.0,
            "u_max_trip_ms": 100,
            "u_min_percent": 80.0,
            "u_min_trip_ms": 150,
            "f_max_hz": 51.5,
            "f_min_hz": 47.5
        },
        telemetry_protocol="IEC 60870-5-104 (DNP3 Gateway optional)",
        curtailment_steps_percent=[100, 60, 30, 0],
        special_requirements=[
            "Prüfprotokoll nach VDE-AR-N 4110 Anhang E.11 erforderlich",
            "Notaus-Schleifentest vierteljährlich vorgeschrieben",
            "Automatische cos(phi) Umschaltung bei Ausfall der Q(U) Kennlinie"
        ]
    ),
    "netze_bw": VnbTabProfile(
        dso_id="netze_bw",
        dso_name="Netze BW GmbH",
        region="Baden-Württemberg",
        description="TAB Mittelspannung Netze BW. Präzise Spannungsblindleistungsstatik mit Schutzentkupplungsprüfung U>> und erweiterter Wirkleistungsrampe.",
        q_control_mode=1,
        q_u_curve={
            "u1_percent": 93.0, "q1_percent": 33.0,
            "u2_percent": 97.0, "q2_percent": 0.0,
            "u3_percent": 103.0, "q3_percent": 0.0,
            "u4_percent": 107.0, "q4_percent": -33.0
        },
        p_f_droop={
            "overfreq_start_hz": 50.20,
            "overfreq_droop_percent": 4.0,
            "underfreq_start_hz": 49.80,
            "underfreq_droop_percent": 4.0
        },
        protection={
            "u_max_percent": 115.0,
            "u_max_trip_ms": 100,
            "u_min_percent": 80.0,
            "u_min_trip_ms": 150,
            "f_max_hz": 51.5,
            "f_min_hz": 47.5
        },
        telemetry_protocol="IEC 60870-5-104 & Modbus TCP",
        curtailment_steps_percent=[100, 60, 30, 0],
        special_requirements=[
            "Einspeisemanagement gemäß § 9 EEG mit Rückmeldung der Istdaten im 1-Sekunden-Takt",
            "Schutzauslösung über galvanisch getrennten Binärkontakt"
        ]
    ),
    "westnetz": VnbTabProfile(
        dso_id="westnetz",
        dso_name="Westnetz GmbH",
        region="Nordrhein-Westfalen / Rheinland-Pfalz / Niedersachsen",
        description="Westnetz TAB Mittelspannung. Flexible Blindleistungsbetriebsarten (wahlweise Q(U) oder cosPhi(P)) und P_AV Begrenzung am Netzanschlusspunkt.",
        q_control_mode=1,
        q_u_curve={
            "u1_percent": 94.0, "q1_percent": 32.8,
            "u2_percent": 98.0, "q2_percent": 0.0,
            "u3_percent": 102.0, "q3_percent": 0.0,
            "u4_percent": 106.0, "q4_percent": -32.8
        },
        p_f_droop={
            "overfreq_start_hz": 50.20,
            "overfreq_droop_percent": 5.0,
            "underfreq_start_hz": 49.80,
            "underfreq_droop_percent": 5.0
        },
        protection={
            "u_max_percent": 112.0,
            "u_max_trip_ms": 100,
            "u_min_percent": 85.0,
            "u_min_trip_ms": 200,
            "f_max_hz": 51.5,
            "f_min_hz": 47.5
        },
        telemetry_protocol="IEC 60870-5-104 / Modbus TCP",
        curtailment_steps_percent=[100, 60, 30, 0],
        special_requirements=[
            "Wirkleistungsgradient maximal 10% P_nenn / Minute bei Wiederzuschaltung",
            "PCC Netzanalyse nach EN 50160 Klasse A"
        ]
    ),
    "edis": VnbTabProfile(
        dso_id="edis",
        dso_name="E.DIS Netz GmbH",
        region="Brandenburg / Mecklenburg-Vorpommern",
        description="E.DIS TAB Mittelspannung. Optimiert für Regionen mit extrem hohem Anteil erneuerbarer Energien. Dynamische Netzstützung und schneller P(f)-Gradient.",
        q_control_mode=1,
        q_u_curve={
            "u1_percent": 90.0, "q1_percent": 33.0,
            "u2_percent": 96.0, "q2_percent": 0.0,
            "u3_percent": 104.0, "q3_percent": 0.0,
            "u4_percent": 110.0, "q4_percent": -33.0
        },
        p_f_droop={
            "overfreq_start_hz": 50.20,
            "overfreq_droop_percent": 4.0,
            "underfreq_start_hz": 49.80,
            "underfreq_droop_percent": 4.0
        },
        protection={
            "u_max_percent": 115.0,
            "u_max_trip_ms": 100,
            "u_min_percent": 75.0,
            "u_min_trip_ms": 150,
            "f_max_hz": 51.5,
            "f_min_hz": 47.5
        },
        telemetry_protocol="IEC 60870-5-104",
        curtailment_steps_percent=[100, 60, 30, 0],
        special_requirements=[
            "Erhöhte Robustheit gegen Spannungstrichter (FRT / Fault Ride Through)",
            "Speicher (BESS) Vorrangaufladung vor Drosselung der Wechselrichter"
        ]
    ),
    "mitnetz": VnbTabProfile(
        dso_id="mitnetz",
        dso_name="Mitteldeutsche Netzgesellschaft Strom mbH (MITNETZ)",
        region="Sachsen / Sachsen-Anhalt / Thüringen / Brandenburg",
        description="MITNETZ STROM TAB. Verbindliche Q(U)-Vorgabe mit Festwert-Fallback und digitaler Fernwirkschnittstelle.",
        q_control_mode=1,
        q_u_curve={
            "u1_percent": 92.0, "q1_percent": 33.0,
            "u2_percent": 97.0, "q2_percent": 0.0,
            "u3_percent": 103.0, "q3_percent": 0.0,
            "u4_percent": 108.0, "q4_percent": -33.0
        },
        p_f_droop={
            "overfreq_start_hz": 50.20,
            "overfreq_droop_percent": 5.0,
            "underfreq_start_hz": 49.80,
            "underfreq_droop_percent": 5.0
        },
        protection={
            "u_max_percent": 115.0,
            "u_max_trip_ms": 100,
            "u_min_percent": 80.0,
            "u_min_trip_ms": 150,
            "f_max_hz": 51.5,
            "f_min_hz": 47.5
        },
        telemetry_protocol="IEC 60870-5-104",
        curtailment_steps_percent=[100, 60, 30, 0],
        special_requirements=[
            "Fernwirktelegramm Bestätigung innerhalb von 500 ms",
            "Registrierung im MITNETZ Einspeiser-Portal"
        ]
    ),
    "stromnetz_berlin": VnbTabProfile(
        dso_id="stromnetz_berlin",
        dso_name="Stromnetz Berlin GmbH",
        region="Berlin",
        description="TAB Mittelspannung Stromnetz Berlin. Städtisches Kabelnetz mit hoher Leitungskapazität; ständige induktive Blindleistungsbereitstellung zur Spannungsabsenkung.",
        q_control_mode=1,
        q_u_curve={
            "u1_percent": 95.0, "q1_percent": 25.0,
            "u2_percent": 99.0, "q2_percent": 0.0,
            "u3_percent": 101.0, "q3_percent": 0.0,
            "u4_percent": 105.0, "q4_percent": -33.0
        },
        p_f_droop={
            "overfreq_start_hz": 50.20,
            "overfreq_droop_percent": 5.0,
            "underfreq_start_hz": 49.80,
            "underfreq_droop_percent": 5.0
        },
        protection={
            "u_max_percent": 110.0,
            "u_max_trip_ms": 100,
            "u_min_percent": 85.0,
            "u_min_trip_ms": 200,
            "f_max_hz": 51.5,
            "f_min_hz": 47.5
        },
        telemetry_protocol="IEC 60870-5-104 & Modbus TCP",
        curtailment_steps_percent=[100, 60, 30, 0],
        special_requirements=[
            "Kabelkapazitätskompensation bei Schwachlast",
            "Redundante Not-Aus-Abschaltung per Lichtwellenleiter"
        ]
    )
}


class TabPresetEngine:
    """Manages VNB TAB profiles and applies them directly to EZA configuration drafts."""

    def __init__(self):
        self.presets = VNB_TAB_PRESETS

    def list_presets(self) -> List[Dict[str, Any]]:
        return [p.model_dump() for p in self.presets.values()]

    def get_preset(self, dso_id: str) -> Optional[VnbTabProfile]:
        return self.presets.get(dso_id.lower().strip())

    def apply_preset_to_config(self, base_config: Dict[str, Any], dso_id: str) -> Dict[str, Any]:
        """Merges DSO TAB specific parameters into an existing EZA configuration."""
        preset = self.get_preset(dso_id)
        if not preset:
            raise ValueError(f"Unknown DSO ID: {dso_id}")

        cfg = dict(base_config)
        cfg["dso_id"] = preset.dso_id
        cfg["dso_name"] = preset.dso_name
        cfg["q_control_mode"] = preset.q_control_mode
        cfg["q_u_curve"] = preset.q_u_curve
        cfg["p_f_droop"] = preset.p_f_droop
        cfg["protection"] = preset.protection
        cfg["applied_tab_standard"] = f"{preset.dso_name} ({preset.vde_standard})"

        return cfg


# Global singleton instance
tab_preset_engine = TabPresetEngine()
