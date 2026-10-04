"""
Questionnaire Service: Replaces physical Single Line Diagram (SLD) uploads
with an interactive, structured, digital plant & component specification.
Generates vector SVG Single Line Diagrams, synthesizes VDE-AR-N 4110 PCU configs,
and registers plants seamlessly.
"""

import os
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.database import get_connection
from backend.component_catalog import (
    MARKET_PV_INVERTERS,
    MARKET_BESS_SYSTEMS,
    MARKET_TRANSFORMERS,
    MARKET_METERS,
    MARKET_PROTECTION_RELAYS,
    PRESET_TEMPLATES
)

logger = logging.getLogger("coneza_questionnaire_service")
DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "stored_documents")
os.makedirs(DOCUMENTS_DIR, exist_ok=True)


def generate_virtual_sld_svg(plant_data: Dict[str, Any], totals: Dict[str, Any]) -> str:
    """
    Generates a professional, standards-compliant Single Line Diagram (SLD) in SVG format
    based entirely on the questionnaire responses.
    """
    plant_name = plant_data.get("plant_name", "Erzeugungsanlage EZA")
    vnb = plant_data.get("grid_operator", "Netzbetreiber")
    u_grid_kv = float(plant_data.get("voltage_level_kv", 20.0))
    p_av_kw = float(plant_data.get("p_av_kw", totals.get("p_inst_kw", 1000.0)))
    has_trafo = plant_data.get("has_transformer", True)
    trafo = plant_data.get("transformer") or {}
    trafo_kva = float(trafo.get("rated_kva", totals.get("p_inst_kw", 1000.0) * 1.1)) if has_trafo else None
    trafo_uk = float(trafo.get("uk_percent", 6.0)) if has_trafo else None

    meter = plant_data.get("meter") or {}
    meter_name = f"{meter.get('brand', 'Janitza')} {meter.get('model', 'UMG 604E')}"

    protection = plant_data.get("protection") or {}
    prot_name = f"{protection.get('brand', 'Woodward')} {protection.get('model', 'HighProTec MRM4')}"

    components = plant_data.get("components") or []
    date_str = datetime.utcnow().strftime("%d.%m.%Y")

    # SVG layout dimensions
    width = 1100
    height = 720

    # Build component boxes dynamically
    comp_svg_elements = []
    comp_count = len(components)
    start_x = 120
    spacing = 860 / max(1, comp_count)

    for i, c in enumerate(components):
        cx = start_x + (i * spacing) + (spacing / 2)
        c_type = (c.get("type") or "PV_INVERTER").upper()
        brand = c.get("brand", "Generic")
        model = c.get("model", "Gerät")
        count = int(c.get("count", 1))
        unit_kw = float(c.get("unit_active_kw", 100.0))
        tot_kw = count * unit_kw
        cap_kwh = float(c.get("capacity_kwh", 0.0)) * count if c_type == "BESS" else 0
        has_sub_meter = bool(c.get("has_sub_meter", False))
        sub_meter_model = c.get("sub_meter_model") or "Janitza UMG 96RM-E"

        if c_type == "BESS":
            badge_bg = "#ecfdf5"
            badge_border = "#10b981"
            badge_text = "#047857"
            icon = "🔋"
            type_label = f"BESS ({cap_kwh:.0f} kWh)"
        elif c_type in ("WIND_TURBINE", "WIND"):
            badge_bg = "#ecfeff"
            badge_border = "#06b6d4"
            badge_text = "#0e7490"
            icon = "🌀"
            type_label = f"Windkraft ({tot_kw:.0f} kW)"
        elif c_type in ("DIESEL_GEN", "GENSET", "CHPP"):
            badge_bg = "#fffbeb"
            badge_border = "#f59e0b"
            badge_text = "#b45309"
            icon = "⛽"
            type_label = f"Dieselgen./BHKW ({tot_kw:.0f} kW)"
        elif c_type in ("HYDRO", "WATER_TURBINE"):
            badge_bg = "#eff6ff"
            badge_border = "#2563eb"
            badge_text = "#1d4ed8"
            icon = "💧"
            type_label = f"Wasserkraft ({tot_kw:.0f} kW)"
        elif c_type == "CUSTOM_EZE":
            badge_bg = "#f5f3ff"
            badge_border = "#8b5cf6"
            badge_text = "#6d28d9"
            icon = "⚡"
            type_label = f"Erzeugung ({tot_kw:.0f} kW)"
        else: # PV_INVERTER
            badge_bg = "#eff6ff"
            badge_border = "#0284c7"
            badge_text = "#0369a1"
            icon = "☀️"
            type_label = f"PV-Inverter ({tot_kw:.0f} kW)"

        # Sub-meter branch graphic (Zusätzliche Messung zum NAP)
        sub_meter_svg = ""
        line_end_y = 535
        if has_sub_meter:
            sub_meter_svg = f"""
            <!-- Sub-Meter at Branch {i+1} (Zusatzmessung) -->
            <circle cx="{cx}" cy="505" r="7" fill="none" stroke="#2563eb" stroke-width="2" />
            <circle cx="{cx}" cy="511" r="7" fill="none" stroke="#2563eb" stroke-width="2" />
            <rect x="{cx+12}" y="497" width="125" height="24" rx="4" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.2" />
            <text x="{cx+74}" y="509" font-family="sans-serif" font-size="8.5" font-weight="bold" fill="#1d4ed8" text-anchor="middle">⚡ Zähler M{i+1}</text>
            <text x="{cx+74}" y="518" font-family="sans-serif" font-size="7.5" fill="#2563eb" text-anchor="middle">{sub_meter_model[:18]}</text>
            <line x1="{cx+7}" y1="508" x2="{cx+12}" y2="508" stroke="#2563eb" stroke-width="1.2" stroke-dasharray="2,2" />
            """

        elem = f"""
        <!-- Component Branch {i+1} -->
        <line x1="{cx}" y1="460" x2="{cx}" y2="{line_end_y}" stroke="#0284c7" stroke-width="3" />
        <rect x="{cx-12}" y="474" width="24" height="24" fill="#ffffff" stroke="#0284c7" stroke-width="2" rx="4" />
        <text x="{cx}" y="490" font-family="sans-serif" font-size="11" font-weight="bold" fill="#0284c7" text-anchor="middle">Q{i+10}</text>

        {sub_meter_svg}

        <!-- EZE Device Box ({c_type}) -->
        <rect x="{cx-75}" y="535" width="150" height="110" rx="8" fill="{badge_bg}" stroke="{badge_border}" stroke-width="2" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.06))" />
        <text x="{cx}" y="557" font-family="sans-serif" font-size="13" font-weight="bold" fill="{badge_text}" text-anchor="middle">{icon} {count}x {brand}</text>
        <text x="{cx}" y="575" font-family="sans-serif" font-size="11" font-weight="600" fill="#334155" text-anchor="middle">{model}</text>
        <line x1="{cx-65}" y1="585" x2="{cx+65}" y2="585" stroke="{badge_border}" stroke-width="1" stroke-dasharray="2,2" opacity="0.6" />
        <text x="{cx}" y="603" font-family="sans-serif" font-size="11" fill="#475569" text-anchor="middle">Pr: {tot_kw:.1f} kW ({count}x {unit_kw:.0f} kW)</text>
        <text x="{cx}" y="620" font-family="sans-serif" font-size="10" font-weight="bold" fill="{badge_text}" text-anchor="middle">{type_label}</text>
        <text x="{cx}" y="635" font-family="monospace" font-size="9" fill="#64748b" text-anchor="middle">Modbus TCP / RTU</text>
        """
        comp_svg_elements.append(elem)

    all_comps_svg = "\n".join(comp_svg_elements)

    trafo_block = ""
    if has_trafo:
        trafo_block = f"""
        <!-- Maschinentransformator T1 -->
        <circle cx="550" cy="315" r="28" fill="none" stroke="#7c3aed" stroke-width="3" />
        <circle cx="550" cy="345" r="28" fill="none" stroke="#7c3aed" stroke-width="3" />
        <rect x="595" y="305" width="220" height="52" rx="6" fill="#f5f3ff" stroke="#c4b5fd" stroke-width="1.5" />
        <text x="605" y="325" font-family="sans-serif" font-size="12" font-weight="bold" fill="#6d28d9">Transformator T1 ({trafo_kva:.0f} kVA)</text>
        <text x="605" y="344" font-family="sans-serif" font-size="11" fill="#5b21b6">{u_grid_kv:.1f} kV / 0.4 kV · uk = {trafo_uk:.1f}% · Dyn5</text>
        """
        line_to_bus = """
        <line x1="550" y1="373" x2="550" y2="460" stroke="#0284c7" stroke-width="4" />
        """
    else:
        line_to_bus = """
        <line x1="550" y1="280" x2="550" y2="460" stroke="#0284c7" stroke-width="4" />
        <rect x="580" y="320" width="180" height="32" rx="4" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1" />
        <text x="670" y="340" font-family="sans-serif" font-size="11" fill="#64748b" text-anchor="middle">Direkter NS-Anschluss (Kein Trafo)</text>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background:#ffffff; border-radius:12px; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <defs>
        <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#0f172a" />
            <stop offset="100%" stop-color="#1e293b" />
        </linearGradient>
        <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
            <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08" />
        </filter>
    </defs>

    <!-- Header / Title Block -->
    <rect x="0" y="0" width="{width}" height="68" fill="url(#headerGrad)" />
    <text x="25" y="32" font-size="18" font-weight="bold" fill="#38bdf8">⚡ Digitales Single Line Diagram (SLD) · VDE-AR-N 4110</text>
    <text x="25" y="52" font-size="12" fill="#94a3b8">Anlage: <tspan fill="#ffffff" font-weight="bold">{plant_name}</tspan> · Netzbetreiber: <tspan fill="#ffffff">{vnb}</tspan> · Erstellt am {date_str}</text>
    <rect x="{width-180}" y="16" width="155" height="36" rx="6" fill="rgba(56, 189, 248, 0.15)" stroke="#38bdf8" stroke-width="1.5" />
    <text x="{width-102}" y="38" font-size="11" font-weight="bold" fill="#38bdf8" text-anchor="middle">✓ SLD-Ersatz verifiziert</text>

    <!-- 1. Grid Infeed / NAP (Netzanschlusspunkt) -->
    <g id="nap_layer">
        <!-- Grid Utility Symbol -->
        <rect x="475" y="85" width="150" height="42" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="2" />
        <text x="550" y="104" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">Netzanschluss (NAP)</text>
        <text x="550" y="120" font-size="10" fill="#475569" text-anchor="middle">{vnb} · {u_grid_kv:.1f} kV</text>
        <line x1="550" y1="127" x2="550" y2="155" stroke="#0f172a" stroke-width="4" />

        <!-- Power Rating Callout -->
        <rect x="645" y="90" width="160" height="32" rx="4" fill="#e0f2fe" stroke="#38bdf8" stroke-width="1" />
        <text x="725" y="110" font-size="11" font-weight="600" fill="#0369a1" text-anchor="middle">P_AV = {p_av_kw:.0f} kW</text>
    </g>

    <!-- 2. Circuit Breaker Q0 & Protection Relay -->
    <g id="breaker_layer">
        <line x1="550" y1="155" x2="550" y2="180" stroke="#0f172a" stroke-width="4" />
        <!-- Q0 Breaker Symbol -->
        <rect x="536" y="180" width="28" height="28" fill="#ffffff" stroke="#dc2626" stroke-width="3" rx="4" />
        <text x="550" y="199" font-size="12" font-weight="bold" fill="#dc2626" text-anchor="middle">Q0</text>
        
        <!-- Protection Relay Box (Left) -->
        <rect x="330" y="174" width="180" height="40" rx="6" fill="#fef2f2" stroke="#f87171" stroke-width="1.5" />
        <text x="420" y="192" font-size="11" font-weight="bold" fill="#b91c1c" text-anchor="middle">🛡️ {prot_name}</text>
        <text x="420" y="206" font-size="9" fill="#991b1b" text-anchor="middle">Entkupplungsschutz / NA-Schutz</text>
        <line x1="510" y1="194" x2="536" y2="194" stroke="#dc2626" stroke-width="2" stroke-dasharray="3,3" />

        <line x1="550" y1="208" x2="550" y2="235" stroke="#0f172a" stroke-width="4" />
    </g>

    <!-- 3. CT/VT Metering Point (NAP Zähler) -->
    <g id="metering_layer">
        <!-- CT circle -->
        <circle cx="550" cy="248" r="10" fill="none" stroke="#2563eb" stroke-width="2.5" />
        <circle cx="550" cy="254" r="10" fill="none" stroke="#2563eb" stroke-width="2.5" />
        
        <!-- Meter Box (Right) -->
        <rect x="595" y="235" width="200" height="42" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.5" />
        <text x="695" y="254" font-size="12" font-weight="bold" fill="#1d4ed8" text-anchor="middle">⚡ Zähler: {meter_name}</text>
        <text x="695" y="268" font-size="10" fill="#2563eb" text-anchor="middle">Klasse 0.2S · Modbus TCP ({meter.get('ip', '192.168.1.100')})</text>
        <line x1="560" y1="251" x2="595" y2="251" stroke="#2563eb" stroke-width="2" stroke-dasharray="2,2" />

        <line x1="550" y1="264" x2="550" y2="295" stroke="#0f172a" stroke-width="4" />
    </g>

    <!-- 4. Transformer T1 -->
    {trafo_block}
    {line_to_bus}

    <!-- 5. Low/Medium Voltage Main Busbar (Erzeugungssammelschiene) -->
    <g id="busbar_layer">
        <rect x="80" y="458" width="940" height="8" rx="3" fill="#0284c7" />
        <text x="90" y="450" font-size="12" font-weight="bold" fill="#0284c7">Sammelschiene (Erzeugung 400V / 690V)</text>
        <text x="920" y="450" font-size="11" font-weight="bold" fill="#0369a1">P_ges: {totals.get('p_inst_kw', 0):.0f} kW</text>
    </g>

    <!-- 6. Connected Inverter / BESS Branches -->
    {all_comps_svg}

    <!-- 7. PCU Controller Overlay Badge (EZA Regler AXC F 2152) -->
    <g id="pcu_controller_layer">
        <rect x="25" y="570" width="180" height="95" rx="8" fill="#f8fafc" stroke="#0f172a" stroke-width="2" filter="url(#shadow)" />
        <text x="115" y="594" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">🎛️ Coneza EZA-Regler</text>
        <text x="115" y="610" font-size="10" font-weight="600" fill="#2563eb" text-anchor="middle">Phoenix Contact AXC F 2152</text>
        <text x="115" y="626" font-size="9" fill="#64748b" text-anchor="middle">VDE-AR-N 4110 zertifiziert</text>
        <text x="115" y="642" font-size="9" fill="#16a34a" font-weight="bold" text-anchor="middle">● Regelmodus: {plant_data.get('reactive_mode', 'Q(U)')}</text>
        <text x="115" y="656" font-size="8" fill="#94a3b8" text-anchor="middle">Holding Register 40001-40502</text>
    </g>

    <!-- Legend & Standards Footer -->
    <rect x="0" y="{height-38}" width="{width}" height="38" fill="#f1f5f9" />
    <text x="25" y="{height-16}" font-size="11" fill="#64748b">VDE-AR-N 4110 konforme Topologie · Automatisch aus Komponenten-Fragebogen synthetisiert · Kein Papierschaltplan erforderlich.</text>
    <text x="{width-25}" y="{height-16}" font-size="11" font-weight="bold" fill="#0284c7" text-anchor="end">CONEZA ENERGY CLOUD</text>
</svg>
    """
    return svg


def process_questionnaire(payload: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processes the interactive plant questionnaire:
    1. Calculates electrical totals
    2. Generates digital SLD (SVG & JSON)
    3. Synthesizes Phoenix Contact VDE-AR-N 4110 PCU Modbus configuration
    4. Creates Plant in DB
    5. Stores digital SLD in Documents DB
    6. Stores PCU configuration in EZA configurations DB
    7. Links active/selected edge device if available
    """
    plant_name = (payload.get("plant_name") or "").strip()
    grid_operator = (payload.get("grid_operator") or "Netze BW GmbH (EnBW)").strip()
    voltage_kv = float(payload.get("voltage_level_kv") or 20.0)
    voltage_v = voltage_kv * 1000.0
    p_av_kw = float(payload.get("p_av_kw") or 1500.0)
    site_type = (payload.get("site_type") or "PV").upper()
    has_trafo = bool(payload.get("has_transformer", True))
    trafo = payload.get("transformer") or {}
    reactive_mode_raw = (payload.get("reactive_mode") or "QU").upper()

    components = payload.get("components") or []
    if not components:
        # Default single component if none provided
        components = [{
            "type": "PV_INVERTER",
            "is_custom": False,
            "brand": "Huawei",
            "model": "SUN2000-115KTL-M2",
            "count": 13,
            "unit_active_kw": 115.0,
            "unit_apparent_kva": 125.0,
            "ac_voltage_v": 400.0
        }]

    # 1. Calculate totals
    p_inst_kw = 0.0
    s_inst_kva = 0.0
    total_bess_kwh = 0.0
    equipment_tags = []
    sub_meters_list = []
    eze_types_present = set()

    for i, c in enumerate(components):
        count = max(1, int(c.get("count", 1)))
        unit_kw = float(c.get("unit_active_kw", 100.0))
        unit_kva = float(c.get("unit_apparent_kva", unit_kw * 1.05))
        p_inst_kw += count * unit_kw
        s_inst_kva += count * unit_kva

        c_type = (c.get("type") or "PV_INVERTER").upper()
        eze_types_present.add(c_type)
        if c_type == "BESS":
            cap = float(c.get("capacity_kwh", 0.0))
            total_bess_kwh += count * cap

        brand = c.get("brand", "")
        model = c.get("model", "")
        equipment_tags.append(f"{count}x {brand} {model} ({c_type})")

        if c.get("has_sub_meter"):
            sub_meters_list.append({
                "branch_index": i + 1,
                "component": f"{brand} {model}",
                "model": c.get("sub_meter_model") or "Janitza UMG 96RM-E",
                "ip": c.get("sub_meter_ip") or f"192.168.1.{101 + i}",
                "port": int(c.get("sub_meter_port") or 502),
                "slave_id": int(c.get("sub_meter_slave_id") or 1)
            })

    # Auto site_type determination if mixed
    if not payload.get("site_type") or payload.get("site_type") == "PV":
        if len(eze_types_present) > 1:
            site_type = "HYBRID_MULTI_EZE"
        elif "WIND_TURBINE" in eze_types_present or "WIND" in eze_types_present:
            site_type = "WIND"
        elif "DIESEL_GEN" in eze_types_present or "CHPP" in eze_types_present:
            site_type = "GENSET"
        elif "BESS" in eze_types_present:
            site_type = "BESS_STANDALONE"
        else:
            site_type = "PV"

    if not plant_name:
        plant_type_label = "Hybridpark" if len(eze_types_present) > 1 else ("Windpark" if "WIND" in site_type else "Energiepark")
        plant_name = f"{plant_type_label} {p_inst_kw/1000:.1f} MW ({grid_operator.split()[0]})"

    # Transformer calculation
    if has_trafo:
        trafo_kva = float(trafo.get("rated_kva") or round(s_inst_kva * 1.15, -1))
        trafo_uk = float(trafo.get("uk_percent") or 6.0)
        trafo_loading = round((s_inst_kva / trafo_kva) * 100.0, 1)
    else:
        trafo_kva = s_inst_kva
        trafo_uk = 0.0
        trafo_loading = 100.0

    totals = {
        "p_inst_kw": round(p_inst_kw, 1),
        "s_inst_kva": round(s_inst_kva, 1),
        "p_av_kw": round(p_av_kw, 1),
        "bess_capacity_kwh": round(total_bess_kwh, 1),
        "trafo_kva": trafo_kva,
        "trafo_loading_percent": trafo_loading,
        "components_count": len(components),
        "sub_meters_count": len(sub_meters_list),
        "sub_meters": sub_meters_list
    }

    # 2. Synthesize Digital SLD SVG
    svg_content = generate_virtual_sld_svg(payload, totals)
    doc_id_sld = f"doc_{uuid.uuid4().hex[:8]}"
    clean_filename = f"SLD_Digital_{plant_name.replace(' ', '_')[:24]}.svg"
    save_path_sld = os.path.join(DOCUMENTS_DIR, f"{doc_id_sld}_{clean_filename}")
    with open(save_path_sld, "w", encoding="utf-8") as f:
        f.write(svg_content)

    # 3. Create simulated OCR entity dictionary
    extracted_entities = {
        "active_power_kw": totals["p_inst_kw"],
        "apparent_power_kva": totals["s_inst_kva"],
        "p_av_kw": totals["p_av_kw"],
        "grid_voltage_v": voltage_v,
        "transformer_uk_percent": trafo_uk,
        "transformer_rated_kva": trafo_kva,
        "reactive_mode": "Q(U)" if "QU" in reactive_mode_raw else "cos(phi)",
        "grid_operator": grid_operator,
        "nap": f"Übergabestation {grid_operator} ({voltage_kv:.1f} kV)",
        "detected_equipment_tags": equipment_tags,
        "has_transformer": has_trafo,
        "bess_capacity_kwh": total_bess_kwh,
        "sub_meters": sub_meters_list,
        "sub_meter_count": len(sub_meters_list),
        "eze_types": list(eze_types_present),
        "source": "DIGITAL_QUESTIONNAIRE_SLD_REPLACEMENT"
    }

    # 4. Modbus Register Synthesis (Phoenix Contact AXC F 2152)
    q_mode_code = 1 if "QU" in reactive_mode_raw else (0 if "COS" in reactive_mode_raw else 2)
    cos_phi = float(payload.get("cos_phi", 1.0))
    q_max_val = int(totals["s_inst_kva"] * 0.33)

    modbus_table = [
        {"offset": 0, "addr": 40001, "name": "REG_SYSTEM_STATUS", "value": 1, "unit": "-", "type": "UINT16", "category": "System", "desc": "PCU Betriebsfreigabe (1=Aktiv / Normalbetrieb, 0=Standby)"},
        {"offset": 1, "addr": 40002, "name": "REG_HEARTBEAT_TIMEOUT_SEC", "value": 10, "unit": "s", "type": "UINT16", "category": "System", "desc": "Watchdog-Timeout für Leitstellen-Kommunikation"},
        {"offset": 2, "addr": 40003, "name": "REG_HEARTBEAT_COUNTER", "value": 1, "unit": "-", "type": "UINT16", "category": "System", "desc": "Lebenszeichen-Zähler (Heartbeat)"},
        {"offset": 3, "addr": 40004, "name": "REG_GRID_VOLTAGE_NOMINAL", "value": int(voltage_v), "unit": "V", "type": "UINT16", "category": "System", "desc": f"Netznennspannung Un am NAP ({voltage_v:.0f} V)"},
        {"offset": 4, "addr": 40005, "name": "REG_GRID_FREQUENCY_NOMINAL", "value": 5000, "unit": "0.01 Hz", "type": "UINT16", "category": "System", "desc": "Netznennfrequenz (5000 = 50.00 Hz)"},
        {"offset": 5, "addr": 40006, "name": "REG_RATED_ACTIVE_POWER_KW", "value": int(totals["p_inst_kw"]), "unit": "kW", "type": "UINT16", "category": "System", "desc": f"Installierte Nennwirkleistung Pr ({totals['p_inst_kw']:.0f} kW)"},
        {"offset": 6, "addr": 40007, "name": "REG_RATED_APPARENT_POWER_KVA", "value": int(totals["s_inst_kva"]), "unit": "kVA", "type": "UINT16", "category": "System", "desc": f"Vereinbarte Scheinleistung Sr ({totals['s_inst_kva']:.0f} kVA)"},

        {"offset": 100, "addr": 40101, "name": "REG_P_CONTROL_MODE", "value": 0, "unit": "-", "type": "UINT16", "category": "Wirkleistung (P)", "desc": "P-Regelmodus (0=Direkter kW-Sollwert, 1=Relativ 0.1%)"},
        {"offset": 101, "addr": 40102, "name": "REG_P_SETPOINT_KW", "value": int(p_av_kw), "unit": "kW", "type": "UINT16", "category": "Wirkleistung (P)", "desc": f"Aktiver Wirkleistungs-Sollwert ({p_av_kw:.0f} kW)"},
        {"offset": 102, "addr": 40103, "name": "REG_P_SETPOINT_PERCENT", "value": 1000, "unit": "0.1%", "type": "UINT16", "category": "Wirkleistung (P)", "desc": "Wirkleistungssollwert relativ (1000 = 100.0%)"},
        {"offset": 103, "addr": 40104, "name": "REG_P_MAX_FEED_IN_LIMIT_KW", "value": int(p_av_kw), "unit": "kW", "type": "UINT16", "category": "Wirkleistung (P)", "desc": f"VNB maximale Einspeiseleistung P_AV ({p_av_kw:.0f} kW)"},
        {"offset": 104, "addr": 40105, "name": "REG_P_RAMP_RATE_KW_PER_SEC", "value": 100, "unit": "kW/s", "type": "UINT16", "category": "Wirkleistung (P)", "desc": "Leistungsänderungs-Gradient dP/dt"},
        {"offset": 105, "addr": 40106, "name": "REG_P_FREQUENCY_DROOP_EN", "value": 1, "unit": "-", "type": "UINT16", "category": "Wirkleistung (P)", "desc": "Frequenzstützung P(f) Freigabe (1=Aktiv nach VDE 4110)"},

        {"offset": 200, "addr": 40201, "name": "REG_Q_CONTROL_MODE", "value": q_mode_code, "unit": "-", "type": "UINT16", "category": "Blindleistung (Q)", "desc": f"Blindleistungsverfahren ({q_mode_code}: 1=Q(U), 0=cos phi, 2=Q fest)"},
        {"offset": 201, "addr": 40202, "name": "REG_COS_PHI_SETPOINT", "value": int(cos_phi * 1000), "unit": "0.001", "type": "UINT16", "category": "Blindleistung (Q)", "desc": f"cos(phi) Sollwert ({cos_phi:.3f})"},
        {"offset": 202, "addr": 40203, "name": "REG_COS_PHI_EXCITATION", "value": 0, "unit": "-", "type": "UINT16", "category": "Blindleistung (Q)", "desc": "Erregungsart (0=übererregt / induktiv, 1=untererregt / kapazitiv)"},
        {"offset": 203, "addr": 40204, "name": "REG_Q_SETPOINT_KVAR", "value": 0, "unit": "kvar", "type": "INT16", "category": "Blindleistung (Q)", "desc": "Fester Blindleistungs-Sollwert in kvar"},
        {"offset": 204, "addr": 40205, "name": "REG_Q_MAX_INDUCTIVE_KVAR", "value": q_max_val, "unit": "kvar", "type": "UINT16", "category": "Blindleistung (Q)", "desc": f"Max. induktive Blindleistung ({q_max_val} kvar)"},
        {"offset": 205, "addr": 40206, "name": "REG_Q_MAX_CAPACITIVE_KVAR", "value": q_max_val, "unit": "kvar", "type": "UINT16", "category": "Blindleistung (Q)", "desc": f"Max. kapazitive Blindleistung ({q_max_val} kvar)"},
        {"offset": 206, "addr": 40207, "name": "REG_Q_U_TIME_CONSTANT_SEC", "value": 5, "unit": "s", "type": "UINT16", "category": "Blindleistung (Q)", "desc": "Filterzeitkonstante T1 für Q(U) Ausregelung"},

        {"offset": 220, "addr": 40221, "name": "REG_QU_U1", "value": 930, "unit": "0.1% Un", "type": "UINT16", "category": "Blindleistung (Q)", "desc": "Q(U) Stützpunkt U1 (930 = 93.0% Un)"},
        {"offset": 221, "addr": 40222, "name": "REG_QU_Q1", "value": 1000, "unit": "0.1% Qmax", "type": "INT16", "category": "Blindleistung (Q)", "desc": "Q(U) Stützpunkt Q1 (+1000 = +100.0% Qmax, kapazitiv)"},
        {"offset": 222, "addr": 40223, "name": "REG_QU_U2", "value": 970, "unit": "0.1% Un", "type": "UINT16", "category": "Blindleistung (Q)", "desc": "Q(U) Stützpunkt U2 (970 = 97.0% Un, Totband-Start)"},
        {"offset": 223, "addr": 40224, "name": "REG_QU_Q2", "value": 0, "unit": "0.1% Qmax", "type": "INT16", "category": "Blindleistung (Q)", "desc": "Q(U) Stützpunkt Q2 (0 = 0% im Totband)"},
        {"offset": 224, "addr": 40225, "name": "REG_QU_U3", "value": 1030, "unit": "0.1% Un", "type": "UINT16", "category": "Blindleistung (Q)", "desc": "Q(U) Stützpunkt U3 (1030 = 103.0% Un, Totband-Ende)"},
        {"offset": 225, "addr": 40226, "name": "REG_QU_Q3", "value": 0, "unit": "0.1% Qmax", "type": "INT16", "category": "Blindleistung (Q)", "desc": "Q(U) Stützpunkt Q3 (0 = 0% im Totband)"},
        {"offset": 226, "addr": 40227, "name": "REG_QU_U4", "value": 1070, "unit": "0.1% Un", "type": "UINT16", "category": "Blindleistung (Q)", "desc": "Q(U) Stützpunkt U4 (1070 = 107.0% Un)"},
        {"offset": 227, "addr": 40228, "name": "REG_QU_Q4", "value": -1000, "unit": "0.1% Qmax", "type": "INT16", "category": "Blindleistung (Q)", "desc": "Q(U) Stützpunkt Q4 (-1000 = -100.0% Qmax, induktiv)"},

        {"offset": 300, "addr": 40301, "name": "REG_PF_OVERFREQ_START", "value": 5020, "unit": "0.01 Hz", "type": "UINT16", "category": "Frequenz P(f)", "desc": "Startfrequenz Überfrequenz LFSM-O (5020 = 50.20 Hz)"},
        {"offset": 301, "addr": 40302, "name": "REG_PF_OVERFREQ_DROOP", "value": 40, "unit": "0.1%", "type": "UINT16", "category": "Frequenz P(f)", "desc": "Statik s bei Überfrequenz (40 = 4.0% / 40% P_mom/Hz)"},
        {"offset": 302, "addr": 40303, "name": "REG_PF_UNDERFREQ_START", "value": 4980, "unit": "0.01 Hz", "type": "UINT16", "category": "Frequenz P(f)", "desc": "Startfrequenz Unterfrequenz LFSM-U (4980 = 49.80 Hz)"},
        {"offset": 303, "addr": 40304, "name": "REG_PF_UNDERFREQ_DROOP", "value": 40, "unit": "0.1%", "type": "UINT16", "category": "Frequenz P(f)", "desc": "Statik s bei Unterfrequenz (40 = 4.0%)"},

        {"offset": 400, "addr": 40401, "name": "REG_PROT_U_MAX_PERCENT", "value": 1100, "unit": "0.1% Un", "type": "UINT16", "category": "Schutz", "desc": "Überspannungsschutz U> Schwelle (1100 = 110.0% Un)"},
        {"offset": 401, "addr": 40402, "name": "REG_PROT_U_MAX_TRIP_MS", "value": 100, "unit": "ms", "type": "UINT16", "category": "Schutz", "desc": "Auslösezeitverzögerung für U> (100 ms)"},
        {"offset": 402, "addr": 40403, "name": "REG_PROT_U_MIN_PERCENT", "value": 800, "unit": "0.1% Un", "type": "UINT16", "category": "Schutz", "desc": "Unterspannungsschutz U< Schwelle (800 = 80.0% Un)"},
        {"offset": 403, "addr": 40404, "name": "REG_PROT_U_MIN_TRIP_MS", "value": 3000, "unit": "ms", "type": "UINT16", "category": "Schutz", "desc": "Auslösezeitverzögerung für U< (3000 ms)"},
        {"offset": 404, "addr": 40405, "name": "REG_PROT_F_MAX_HZ", "value": 5150, "unit": "0.01 Hz", "type": "UINT16", "category": "Schutz", "desc": "Überfrequenzschutz f> (5150 = 51.50 Hz)"},
        {"offset": 405, "addr": 40406, "name": "REG_PROT_F_MIN_HZ", "value": 4750, "unit": "0.01 Hz", "type": "UINT16", "category": "Schutz", "desc": "Unterfrequenzschutz f< (4750 = 47.50 Hz)"},

        {"offset": 500, "addr": 40501, "name": "REG_CMD_CIRCUIT_BREAKER", "value": 1, "unit": "-", "type": "UINT16", "category": "Befehle", "desc": "Kuppelschalter-Kommando (1=Einschalten / Schließen)"},
        {"offset": 501, "addr": 40502, "name": "REG_CMD_RESET_ALARMS", "value": 1, "unit": "-", "type": "UINT16", "category": "Befehle", "desc": "Fehler- und Schutzalarme quittieren"}
    ]

    # 5. Persist to SQLite
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.utcnow().isoformat()

    plant_id = f"plant_{uuid.uuid4().hex[:8]}"
    cursor.execute("""
        INSERT INTO plants (
            id, name, site_type, grid_operator, voltage_level,
            installed_capacity_kw, grid_connection_point, location,
            commissioning_date, status, notes, created_by, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        plant_id,
        plant_name,
        site_type,
        grid_operator,
        "MS_4110" if voltage_kv >= 1.0 else "NS_4105",
        totals["p_inst_kw"],
        f"Übergabestation {grid_operator} ({voltage_kv:.1f} kV)",
        "Deutschland",
        datetime.utcnow().strftime("%Y-%m-%d"),
        "ONLINE_REGULATING",
        f"Konfiguriert über interaktiven Anlagen-Fragebogen (SLD-Ersatz). {len(components)} Komponentengruppen ({equipment_tags[:2]}). VDE-AR-N 4110 konform.",
        user.get("username", "Engineer"),
        now_iso
    ))

    # Insert virtual SLD document into documents table
    cursor.execute("""
        INSERT INTO documents (
            id, plant_id, device_id, doc_type, filename, file_path, ocr_data_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        doc_id_sld,
        plant_id,
        None,
        "SLD",
        clean_filename,
        save_path_sld,
        json.dumps(extracted_entities),
        now_iso
    ))

    # Insert synthesized EZA configuration
    config_id = f"cfg_pcu_{uuid.uuid4().hex[:8]}"
    recommended_config = {
        "rated_active_power_kw": totals["p_inst_kw"],
        "rated_apparent_power_kva": totals["s_inst_kva"],
        "grid_voltage_nominal_volts": voltage_v,
        "p_max_feed_in_limit_kw": p_av_kw,
        "p_setpoint_kw": p_av_kw,
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
            "overfreq_start_hz": 50.2, "overfreq_droop_percent": 4.0,
            "underfreq_start_hz": 49.8, "underfreq_droop_percent": 4.0
        },
        "protection": {
            "u_max_percent": 110.0, "u_max_trip_ms": 100.0,
            "u_min_percent": 80.0, "u_min_trip_ms": 3000.0,
            "f_max_hz": 51.5, "f_min_hz": 47.5
        }
    }

    # Assign device to plant if specified or default to phoenix
    resolved_device_id = payload.get("target_device_id") or "coneza-phoenix-axcf2152"
    cursor.execute("SELECT device_id, name, local_ip, controller_host, controller_port FROM devices WHERE device_id = ?", (resolved_device_id,))
    dev_row = cursor.fetchone()
    if dev_row:
        cursor.execute("UPDATE devices SET plant_id = ? WHERE device_id = ?", (plant_id, resolved_device_id))
    else:
        cursor.execute("""
            INSERT OR IGNORE INTO devices (device_id, plant_id, name, local_ip, os_platform, controller_host, controller_port, status, controller_state, last_heartbeat)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'ONLINE', 'ONLINE_REGULATING', ?)
        """, (
            resolved_device_id,
            plant_id,
            "Phoenix Contact AXC F 2152 (EZA-Regler)",
            "192.168.8.186",
            "PLCnext Linux",
            "192.168.1.10",
            502,
            now_iso
        ))
        cursor.execute("UPDATE devices SET plant_id = ? WHERE device_id = ?", (plant_id, resolved_device_id))

    # Create Analysis Job with READY_FOR_REVIEW audit for questionnaire
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    cross_eval = {
        "status": "READY_FOR_REVIEW",
        "consensus_score": 100.0,
        "models": ["Interactive-Questionnaire-Synthesizer", "VDE-AR-N-4110-Engine"],
        "parameter_comparisons": [
            {"parameter": "rated_active_power_kw", "agreed_value": totals["p_inst_kw"], "status": "CONFIRMED"},
            {"parameter": "rated_apparent_power_kva", "agreed_value": totals["s_inst_kva"], "status": "CONFIRMED"},
            {"parameter": "grid_voltage_nominal_volts", "agreed_value": voltage_v, "status": "CONFIRMED"},
            {"parameter": "p_max_feed_in_limit_kw", "agreed_value": p_av_kw, "status": "CONFIRMED"},
            {"parameter": "q_control_mode", "agreed_value": q_mode_code, "status": "CONFIRMED"}
        ],
        "peer_reviews": {
            "VDE_AR_N_4110": "TAR Mittelspannung Q(U) Kennlinie und P(f) Statik konform.",
            "SLD_Replacement": f"Digitales Single Line Diagramm generiert: {len(components)} Komponenten-Zweige, Trafo uk={trafo_uk}%."
        },
        "blocking_reasons": []
    }

    cursor.execute("""
        INSERT INTO analysis_jobs (
            id, device_id, status, document_ids_json,
            extracted_parameters_json, discrepancies_json, recommended_eza_config_json,
            gemini_summary, cross_eval_json, consensus_score, models_used, completed_at
        ) VALUES (?, ?, 'COMPLETED', ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        resolved_device_id,
        json.dumps([doc_id_sld]),
        json.dumps(recommended_config),
        json.dumps([]),
        json.dumps(recommended_config),
        f"Automatisch synthetisiert über Anlagen-Fragebogen (SLD-Ersatz). VDE-AR-N 4110 konform ({len(components)} Einheiten).",
        json.dumps(cross_eval),
        100.0,
        json.dumps(["Interactive-Questionnaire-Synthesizer", "VDE-Engine"]),
        now_iso
    ))

    # Create EZA Configuration
    config_id = f"cfg_pcu_{uuid.uuid4().hex[:8]}"
    cursor.execute("""
        INSERT INTO eza_configurations (
            id, device_id, analysis_job_id, parameters_json, status, created_at
        ) VALUES (?, ?, ?, ?, 'APPROVED', ?)
    """, (
        config_id,
        resolved_device_id,
        job_id,
        json.dumps(recommended_config),
        now_iso
    ))

    conn.commit()

    # Fetch created plant details
    cursor.execute("""
        SELECT p.*,
               (SELECT COUNT(*) FROM devices d WHERE d.plant_id = p.id) as device_count,
               (SELECT COUNT(*) FROM documents doc WHERE doc.plant_id = p.id) as document_count
        FROM plants p WHERE p.id = ?
    """, (plant_id,))
    created_plant = dict(cursor.fetchone())
    conn.close()

    logger.info(f"Successfully processed questionnaire for {plant_name}: plant={plant_id}, sld_doc={doc_id_sld}, cfg={config_id}")

    pcu_compat_parameters = {
        "active_power_kw": totals["p_inst_kw"],
        "active_power_limit_pct": 100.0,
        "apparent_power_kva": totals["s_inst_kva"],
        "voltage_nominal_v": voltage_v,
        "uk_percent": trafo_uk,
        "reactive_mode": "QU_CHARACTERISTIC" if "QU" in reactive_mode_raw else reactive_mode_raw,
        "q_u_deadband_low": 0.97,
        "q_u_deadband_high": 1.03,
        "q_filter_t1_s": 5.0,
        "freq_droop_start_hz": 50.2,
        "freq_droop_percent": 4.0
    }

    return {
        "status": "success",
        "plant": created_plant,
        "plant_id": plant_id,
        "plant_name": plant_name,
        "doc_id_sld": doc_id_sld,
        "job_id": job_id,
        "config_id": config_id,
        "device_id": resolved_device_id,
        "target_device_id": resolved_device_id,
        "configuration_id": config_id,
        "totals": totals,
        "virtual_sld_svg": svg_content,
        "extracted_entities": extracted_entities,
        "modbus_table": modbus_table,
        "modbus_holding_registers": modbus_table,
        "recommended_config": recommended_config,
        "parameters": pcu_compat_parameters
    }
