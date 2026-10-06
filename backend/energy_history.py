"""
Plant 30-Day Energy Flow & Telemetry Historical Recording Engine
Stores and provides historical hourly and daily generation, storage, and grid feed-in data.
Conforms to VDE-AR-N 4110 / 4120 monitoring requirements.
"""

import math
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from backend.database import get_connection

def ensure_plant_history_seeded(plant_id: str, capacity_kw: float, site_type: str = "PV"):
    """
    Ensures that at least 30 days of historical hourly telemetry records exist in SQLite
    for the specified plant. Seeds realistic physical data if missing.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check existing days count
    cursor.execute("SELECT COUNT(DISTINCT date) FROM plant_energy_history WHERE plant_id = ?", (plant_id,))
    row = cursor.fetchone()
    count = row[0] if row else 0

    if count >= 28:
        conn.close()
        return

    # Seed 30 days of historical telemetry
    now = datetime.now()
    has_bess = (site_type in ("BESS", "HYBRID"))
    is_wind = (site_type == "WIND")

    # Use deterministic seed based on plant_id so data is consistent across reloads
    random.seed(hash(plant_id) & 0xffffffff)

    rows_to_insert = []
    for day_offset in range(30, -1, -1):
        target_date = now - timedelta(days=day_offset)
        date_str = target_date.strftime("%Y-%m-%d")

        # Weather factor for the day (0.35 = overcast/rainy, 1.0 = clear sunny day)
        weather_factor = random.uniform(0.55, 1.0) if not is_wind else random.uniform(0.4, 1.2)

        for h in range(24):
            pv_energy = 0.0
            pv_peak = 0.0
            bat_charge = 0.0
            bat_discharge = 0.0

            # 1. Solar generation (hours 6 to 20)
            if 6 <= h <= 20 and not is_wind:
                sun_curve = math.sin(((h - 6) / 14.0) * math.pi)
                pv_kw = capacity_kw * sun_curve * weather_factor * random.uniform(0.92, 1.03)
                pv_energy = round(pv_kw, 2)
                pv_peak = round(pv_kw * random.uniform(1.02, 1.08), 2)
            elif is_wind:
                # Wind profiles blow 24/7 with weather shifts
                wind_factor = (math.sin(h / 3.8) * 0.3 + 0.7) * weather_factor
                pv_kw = capacity_kw * wind_factor * random.uniform(0.85, 1.1)
                pv_energy = round(pv_kw, 2)
                pv_peak = round(pv_kw * 1.05, 2)

            # 2. BESS Battery behavior
            if has_bess:
                if 10 <= h <= 14 and pv_energy > 0:
                    # Charging with surplus solar
                    bat_charge = round(min(capacity_kw * 0.18, 380.0) * weather_factor, 2)
                elif (6 <= h <= 8) or (18 <= h <= 21):
                    # Discharging to shave peak tariff / evening consumption
                    bat_discharge = round(min(capacity_kw * 0.22, 450.0) * random.uniform(0.85, 1.0), 2)

            # 3. Load / Auxiliaries (Eigenbedarf)
            load_energy = round(max(10.0, capacity_kw * 0.018 * random.uniform(0.9, 1.1)), 2)

            # 4. Net grid feed-in at NAP
            net_flow = pv_energy + bat_discharge - bat_charge - load_energy
            grid_feedin = max(0.0, round(net_flow, 2))
            grid_import = max(0.0, round(-net_flow, 2))

            # Grid voltage / frequency
            avg_u = round(20.0 * random.uniform(0.995, 1.012), 2)
            avg_f = round(50.0 + random.uniform(-0.03, 0.03), 2)

            rows_to_insert.append((
                plant_id, date_str, h, pv_energy, pv_peak,
                bat_charge, bat_discharge, load_energy,
                grid_feedin, grid_import, avg_u, avg_f
            ))

    cursor.executemany("""
        INSERT OR REPLACE INTO plant_energy_history (
            plant_id, date, hour, pv_energy_kwh, pv_peak_kw,
            bat_charge_kwh, bat_discharge_kwh, load_energy_kwh,
            grid_feedin_kwh, grid_import_kwh, avg_voltage_kv, avg_frequency_hz
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows_to_insert)

    conn.commit()
    conn.close()

def get_plant_energy_history(plant_id: str, days: int = 30) -> Dict[str, Any]:
    """
    Returns the energy flow history for a plant over 1, 7, or 30 days.
    If plant_id == 'ALL', aggregates the data across all registered plants.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Resolve plant metadata
    plant_name = "Gesamtflotte (Alle Standorte)"
    capacity_kw = 2200.0
    site_type = "HYBRID"

    if plant_id == "ALL":
        cursor.execute("SELECT id, name, installed_capacity_kw, site_type FROM plants")
        plants = cursor.fetchall()
        if plants:
            capacity_kw = sum(float(p["installed_capacity_kw"] or 0) for p in plants)
            plant_name = f"Gesamtflotte ({len(plants)} Standorte)"
            for p in plants:
                ensure_plant_history_seeded(p["id"], float(p["installed_capacity_kw"] or 1500), p["site_type"])
    else:
        cursor.execute("SELECT * FROM plants WHERE id = ?", (plant_id,))
        p = cursor.fetchone()
        if p:
            plant_name = p["name"]
            capacity_kw = float(p["installed_capacity_kw"] or 1500.0)
            site_type = p["site_type"]
            ensure_plant_history_seeded(plant_id, capacity_kw, site_type)

    now = datetime.now()
    start_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")

    # Fetch daily aggregates
    if plant_id == "ALL":
        query = """
            SELECT date,
                   SUM(pv_energy_kwh) as pv_kwh,
                   MAX(pv_peak_kw) as pv_peak_kw,
                   SUM(bat_charge_kwh) as bat_charge_kwh,
                   SUM(bat_discharge_kwh) as bat_discharge_kwh,
                   SUM(load_energy_kwh) as load_kwh,
                   SUM(grid_feedin_kwh) as grid_feedin_kwh,
                   SUM(grid_import_kwh) as grid_import_kwh
            FROM plant_energy_history
            WHERE date >= ?
            GROUP BY date
            ORDER BY date ASC
        """
        cursor.execute(query, (start_date,))
    else:
        query = """
            SELECT date,
                   SUM(pv_energy_kwh) as pv_kwh,
                   MAX(pv_peak_kw) as pv_peak_kw,
                   SUM(bat_charge_kwh) as bat_charge_kwh,
                   SUM(bat_discharge_kwh) as bat_discharge_kwh,
                   SUM(load_energy_kwh) as load_kwh,
                   SUM(grid_feedin_kwh) as grid_feedin_kwh,
                   SUM(grid_import_kwh) as grid_import_kwh
            FROM plant_energy_history
            WHERE plant_id = ? AND date >= ?
            GROUP BY date
            ORDER BY date ASC
        """
        cursor.execute(query, (plant_id, start_date))

    daily_rows = cursor.fetchall()

    # Fetch 24 hourly values for today
    today_str = now.strftime("%Y-%m-%d")
    if plant_id == "ALL":
        cursor.execute("""
            SELECT hour,
                   SUM(pv_energy_kwh) as pv_kw,
                   SUM(bat_charge_kwh) as bat_charge_kw,
                   SUM(bat_discharge_kwh) as bat_discharge_kw,
                   SUM(load_energy_kwh) as load_kw,
                   SUM(grid_feedin_kwh) as grid_feedin_kw
            FROM plant_energy_history
            WHERE date = ?
            GROUP BY hour
            ORDER BY hour ASC
        """, (today_str,))
    else:
        cursor.execute("""
            SELECT hour,
                   pv_energy_kwh as pv_kw,
                   bat_charge_kwh as bat_charge_kw,
                   bat_discharge_kwh as bat_discharge_kw,
                   load_energy_kwh as load_kw,
                   grid_feedin_kwh as grid_feedin_kw
            FROM plant_energy_history
            WHERE plant_id = ? AND date = ?
            ORDER BY hour ASC
        """, (plant_id, today_str))

    hourly_rows = cursor.fetchall()
    conn.close()

    # Format hourly today array (24 entries)
    hourly_map = {r["hour"]: dict(r) for r in hourly_rows}
    hourly_today = []
    for h in range(24):
        h_data = hourly_map.get(h, {})
        pv_val = round(float(h_data.get("pv_kw") or 0), 1)
        bat_dis = round(float(h_data.get("bat_discharge_kw") or 0), 1)
        bat_chg = round(float(h_data.get("bat_charge_kw") or 0), 1)
        load_val = round(float(h_data.get("load_kw") or 0), 1)
        nap_val = round(float(h_data.get("grid_feedin_kw") or 0), 1)
        bat_net = bat_dis - bat_chg

        hourly_today.append({
            "hour": h,
            "hour_label": f"{h:02d}:00",
            "pv_kw": pv_val,
            "bat_kw": bat_net,
            "bat_charge_kw": bat_chg,
            "bat_discharge_kw": bat_dis,
            "load_kw": load_val,
            "p_nap_kw": nap_val
        })

    # Format daily series
    daily_series = []
    total_pv_kwh = 0.0
    total_grid_kwh = 0.0
    total_bat_dis_kwh = 0.0
    total_load_kwh = 0.0

    for r in daily_rows:
        d_pv = round(float(r["pv_kwh"] or 0), 1)
        d_grid = round(float(r["grid_feedin_kwh"] or 0), 1)
        d_dis = round(float(r["bat_discharge_kwh"] or 0), 1)
        d_chg = round(float(r["bat_charge_kwh"] or 0), 1)
        d_load = round(float(r["load_kwh"] or 0), 1)
        d_peak = round(float(r["pv_peak_kw"] or 0), 1)

        total_pv_kwh += d_pv
        total_grid_kwh += d_grid
        total_bat_dis_kwh += d_dis
        total_load_kwh += d_load

        # Format label e.g. "05.10"
        try:
            d_obj = datetime.strptime(r["date"], "%Y-%m-%d")
            day_label = d_obj.strftime("%d.%m")
        except Exception:
            day_label = r["date"]

        daily_series.append({
            "date": r["date"],
            "label": day_label,
            "pv_kwh": d_pv,
            "pv_peak_kw": d_peak,
            "bat_discharge_kwh": d_dis,
            "bat_charge_kwh": d_chg,
            "load_kwh": d_load,
            "grid_feedin_kwh": d_grid
        })

    days_count = max(1, len(daily_series))

    return {
        "plant_id": plant_id,
        "plant_name": plant_name,
        "installed_capacity_kw": capacity_kw,
        "site_type": site_type,
        "days": days,
        "summary": {
            "total_pv_mwh": round(total_pv_kwh / 1000.0, 2),
            "total_pv_kwh": round(total_pv_kwh, 1),
            "total_grid_feedin_mwh": round(total_grid_kwh / 1000.0, 2),
            "total_grid_feedin_kwh": round(total_grid_kwh, 1),
            "total_bat_throughput_mwh": round(total_bat_dis_kwh / 1000.0, 2),
            "total_load_mwh": round(total_load_kwh / 1000.0, 2),
            "avg_daily_yield_kwh": round(total_pv_kwh / days_count, 1),
            "self_consumption_pct": round(min(100.0, (total_load_kwh / max(1.0, total_pv_kwh)) * 100.0), 1)
        },
        "daily_series": daily_series,
        "hourly_today": hourly_today
    }
