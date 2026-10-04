"""
Market-standard component catalog for renewable energy and storage plants (VDE-AR-N 4110 / 4105).
Provides preconfigured specifications for PV inverters, BESS systems, transformers,
meters, and protection relays, plus custom component definition support.
"""

from typing import Dict, Any, List

MARKET_PV_INVERTERS: List[Dict[str, Any]] = [
    {
        "id": "huawei_sun2000_115ktl",
        "brand": "Huawei",
        "model": "SUN2000-115KTL-M2",
        "rated_active_kw": 115.0,
        "rated_apparent_kva": 125.0,
        "ac_voltage_v": 400.0,
        "efficiency_percent": 98.8,
        "mppt_count": 10,
        "interface": "Modbus TCP / RTU",
        "recommended_for": "Freiflächen- & große Dachanlagen"
    },
    {
        "id": "huawei_sun2000_100ktl",
        "brand": "Huawei",
        "model": "SUN2000-100KTL-M2",
        "rated_active_kw": 100.0,
        "rated_apparent_kva": 110.0,
        "ac_voltage_v": 400.0,
        "efficiency_percent": 98.8,
        "mppt_count": 10,
        "interface": "Modbus TCP / RTU",
        "recommended_for": "C&I Gewerbe- & Großanlagen"
    },
    {
        "id": "huawei_sun2000_330ktl",
        "brand": "Huawei",
        "model": "SUN2000-330KTL-H1",
        "rated_active_kw": 330.0,
        "rated_apparent_kva": 330.0,
        "ac_voltage_v": 800.0,
        "efficiency_percent": 99.0,
        "mppt_count": 6,
        "interface": "Modbus TCP (SmartLogger)",
        "recommended_for": "Utility-Scale Freiflächenparks (800V)"
    },
    {
        "id": "sma_peak3_150",
        "brand": "SMA",
        "model": "Sunny Highpower PEAK3 (SHP 150-20)",
        "rated_active_kw": 150.0,
        "rated_apparent_kva": 150.0,
        "ac_voltage_v": 400.0,
        "efficiency_percent": 98.8,
        "mppt_count": 1,
        "interface": "Modbus TCP / SunSpec",
        "recommended_for": "Dezentrale Großanlagen mit String-Sammlern"
    },
    {
        "id": "sma_core2_110",
        "brand": "SMA",
        "model": "Sunny Tripower CORE2 (STP 110-60)",
        "rated_active_kw": 110.0,
        "rated_apparent_kva": 110.0,
        "ac_voltage_v": 400.0,
        "efficiency_percent": 98.6,
        "mppt_count": 12,
        "interface": "Modbus TCP / Speedwire",
        "recommended_for": "Gewerbedächer & Parkplatz-PV"
    },
    {
        "id": "sma_core1_50",
        "brand": "SMA",
        "model": "Sunny Tripower CORE1 (STP 50-41)",
        "rated_active_kw": 50.0,
        "rated_apparent_kva": 50.0,
        "ac_voltage_v": 400.0,
        "efficiency_percent": 98.1,
        "mppt_count": 6,
        "interface": "Modbus TCP / Speedwire",
        "recommended_for": "Mittelgroße C&I Dachanlagen"
    },
    {
        "id": "sungrow_sg125hx",
        "brand": "Sungrow",
        "model": "SG125HX",
        "rated_active_kw": 125.0,
        "rated_apparent_kva": 125.0,
        "ac_voltage_v": 400.0,
        "efficiency_percent": 98.7,
        "mppt_count": 12,
        "interface": "Modbus TCP / RS485",
        "recommended_for": "Standard C&I und Freiflächen"
    },
    {
        "id": "sungrow_sg350hx",
        "brand": "Sungrow",
        "model": "SG350HX",
        "rated_active_kw": 352.0,
        "rated_apparent_kva": 352.0,
        "ac_voltage_v": 800.0,
        "efficiency_percent": 99.0,
        "mppt_count": 14,
        "interface": "Modbus TCP",
        "recommended_for": "Große Solarparks (800V AC)"
    },
    {
        "id": "kaco_blueplanet_125",
        "brand": "Kaco",
        "model": "blueplanet 125 TL3",
        "rated_active_kw": 125.0,
        "rated_apparent_kva": 125.0,
        "ac_voltage_v": 400.0,
        "efficiency_percent": 98.6,
        "mppt_count": 1,
        "interface": "Modbus TCP / SunSpec",
        "recommended_for": "Freifläche & Industrie"
    },
    {
        "id": "solaredge_se100k",
        "brand": "SolarEdge",
        "model": "SE100K Synergy",
        "rated_active_kw": 100.0,
        "rated_apparent_kva": 100.0,
        "ac_voltage_v": 400.0,
        "efficiency_percent": 98.3,
        "mppt_count": 3,
        "interface": "Modbus TCP / SunSpec",
        "recommended_for": "Dachanlagen mit Verschattungsoptimierung"
    },
    {
        "id": "fronius_tauro_100",
        "brand": "Fronius",
        "model": "Tauro ECO 100-3-D",
        "rated_active_kw": 100.0,
        "rated_apparent_kva": 100.0,
        "ac_voltage_v": 400.0,
        "efficiency_percent": 98.5,
        "mppt_count": 1,
        "interface": "Modbus TCP / Solar.web",
        "recommended_for": "Robuste Outdoor C&I Anlagen"
    },
    {
        "id": "solinteg_mht_50k",
        "brand": "Solinteg",
        "model": "Integrid MHT-50K",
        "rated_active_kw": 50.0,
        "rated_apparent_kva": 50.0,
        "ac_voltage_v": 400.0,
        "efficiency_percent": 98.4,
        "mppt_count": 4,
        "interface": "Modbus RTU / TCP",
        "recommended_for": "Hybrid PV & Batterieeinbindung"
    }
]

MARKET_BESS_SYSTEMS: List[Dict[str, Any]] = [
    {
        "id": "byd_battery_box_c130",
        "brand": "BYD",
        "model": "Commercial Battery-Box C130",
        "capacity_kwh": 130.0,
        "rated_active_kw": 100.0,
        "rated_apparent_kva": 100.0,
        "cell_chemistry": "LFP (Lithium-Eisenphosphat)",
        "ac_voltage_v": 400.0,
        "c_rate": 0.77,
        "interface": "Modbus TCP / CAN",
        "recommended_for": "Gewerbespeicher & Peak-Shaving"
    },
    {
        "id": "byd_mc_cube_2500",
        "brand": "BYD",
        "model": "MC Cube Commercial 2.5 MWh",
        "capacity_kwh": 2500.0,
        "rated_active_kw": 1250.0,
        "rated_apparent_kva": 1250.0,
        "cell_chemistry": "Blade LFP (Liquid Cooled)",
        "ac_voltage_v": 690.0,
        "c_rate": 0.5,
        "interface": "Modbus TCP / IEC 60870-5-104",
        "recommended_for": "Großspeicher & Netzdienstleistungen"
    },
    {
        "id": "tesla_megapack_2xl",
        "brand": "Tesla",
        "model": "Megapack 2XL",
        "capacity_kwh": 3916.0,
        "rated_active_kw": 1929.0,
        "rated_apparent_kva": 1929.0,
        "cell_chemistry": "LFP",
        "ac_voltage_v": 480.0,
        "c_rate": 0.5,
        "interface": "Modbus TCP / DNP3",
        "recommended_for": "Utility-Scale Netzanbindung"
    },
    {
        "id": "sungrow_powertitan_2752",
        "brand": "Sungrow",
        "model": "PowerTitan ST2752UX",
        "capacity_kwh": 2752.0,
        "rated_active_kw": 1375.0,
        "rated_apparent_kva": 1375.0,
        "cell_chemistry": "LFP Liquid Cooling",
        "ac_voltage_v": 690.0,
        "c_rate": 0.5,
        "interface": "Modbus TCP / IEC 104",
        "recommended_for": "PV+BESS Hybridparks"
    },
    {
        "id": "catl_enerone_3700",
        "brand": "CATL",
        "model": "EnerOne Liquid-Cooling 3.7 MWh",
        "capacity_kwh": 3727.0,
        "rated_active_kw": 1860.0,
        "rated_apparent_kva": 1860.0,
        "cell_chemistry": "LFP",
        "ac_voltage_v": 690.0,
        "c_rate": 0.5,
        "interface": "Modbus TCP",
        "recommended_for": "Großspeicherprojekte"
    },
    {
        "id": "intilion_scalebloc_68",
        "brand": "Intilion",
        "model": "scalebloc 68 kWh",
        "capacity_kwh": 68.0,
        "rated_active_kw": 60.0,
        "rated_apparent_kva": 60.0,
        "cell_chemistry": "LFP",
        "ac_voltage_v": 400.0,
        "c_rate": 0.88,
        "interface": "Modbus TCP",
        "recommended_for": "Kompakte Industrie- & Gewerbespeicher"
    }
]

MARKET_WIND_TURBINES: List[Dict[str, Any]] = [
    {
        "id": "enercon_e138_ep3",
        "brand": "Enercon",
        "model": "E-138 EP3 E2 (3.5 MW)",
        "rated_active_kw": 3500.0,
        "rated_apparent_kva": 3850.0,
        "ac_voltage_v": 690.0,
        "rotor_diameter_m": 138.0,
        "interface": "Modbus TCP / IEC 61400-25",
        "recommended_for": "Binnenland- & Schwachwindstandorte"
    },
    {
        "id": "enercon_e115_ep3",
        "brand": "Enercon",
        "model": "E-115 EP3 E3 (3.0 MW)",
        "rated_active_kw": 2990.0,
        "rated_apparent_kva": 3200.0,
        "ac_voltage_v": 690.0,
        "rotor_diameter_m": 115.0,
        "interface": "Modbus TCP / IEC 61400-25",
        "recommended_for": "Standard Windparks Mittelgebirge"
    },
    {
        "id": "vestas_v150_42",
        "brand": "Vestas",
        "model": "V150-4.2 MW EnVentus",
        "rated_active_kw": 4200.0,
        "rated_apparent_kva": 4500.0,
        "ac_voltage_v": 720.0,
        "rotor_diameter_m": 150.0,
        "interface": "Modbus TCP / OPC UA",
        "recommended_for": "Große Onshore Megawatt-Windparks"
    },
    {
        "id": "vestas_v117_345",
        "brand": "Vestas",
        "model": "V117-3.45 MW",
        "rated_active_kw": 3450.0,
        "rated_apparent_kva": 3650.0,
        "ac_voltage_v": 690.0,
        "rotor_diameter_m": 117.0,
        "interface": "Modbus TCP / OPC UA",
        "recommended_for": "Starkwind- und Küstenstandorte"
    },
    {
        "id": "nordex_n149_45",
        "brand": "Nordex",
        "model": "N149/4.0-4.5 Delta4000",
        "rated_active_kw": 4500.0,
        "rated_apparent_kva": 4800.0,
        "ac_voltage_v": 660.0,
        "rotor_diameter_m": 149.0,
        "interface": "Modbus TCP / IEC 60870-5-104",
        "recommended_for": "Große Megawatt-Windparks"
    },
    {
        "id": "siemens_gamesa_sg34_132",
        "brand": "Siemens Gamesa",
        "model": "SG 3.4-132",
        "rated_active_kw": 3400.0,
        "rated_apparent_kva": 3600.0,
        "ac_voltage_v": 690.0,
        "rotor_diameter_m": 132.0,
        "interface": "Modbus TCP",
        "recommended_for": "Mittlere bis hohe Windgeschwindigkeiten"
    }
]

MARKET_DIESEL_GENSETS: List[Dict[str, Any]] = [
    {
        "id": "mtu_16v4000_ds2500",
        "brand": "MTU / Rolls-Royce",
        "model": "16V4000 DS2500 (2.0 MW)",
        "rated_active_kw": 2000.0,
        "rated_apparent_kva": 2500.0,
        "ac_voltage_v": 400.0,
        "fuel_type": "Diesel / HVO100",
        "interface": "Modbus RTU / TCP (MTU ADEC)",
        "recommended_for": "Netzersatz- & Spitzenlastaggregat"
    },
    {
        "id": "mtu_12v4000_ds1750",
        "brand": "MTU / Rolls-Royce",
        "model": "12V4000 DS1750 (1.4 MW)",
        "rated_active_kw": 1400.0,
        "rated_apparent_kva": 1750.0,
        "ac_voltage_v": 400.0,
        "fuel_type": "Diesel / HVO100",
        "interface": "Modbus RTU / TCP",
        "recommended_for": "Kritische Infrastruktur & Microgrids"
    },
    {
        "id": "cat_3516b",
        "brand": "Caterpillar (CAT)",
        "model": "CAT 3516B-HD (1.6 MW)",
        "rated_active_kw": 1600.0,
        "rated_apparent_kva": 2000.0,
        "ac_voltage_v": 400.0,
        "fuel_type": "Diesel",
        "interface": "Modbus TCP (EMCP 4.2)",
        "recommended_for": "Industrie- & Inselnetzbetrieb"
    },
    {
        "id": "cat_c32",
        "brand": "Caterpillar (CAT)",
        "model": "CAT C32 ACERT (1.0 MW)",
        "rated_active_kw": 1000.0,
        "rated_apparent_kva": 1250.0,
        "ac_voltage_v": 400.0,
        "fuel_type": "Diesel",
        "interface": "Modbus TCP (EMCP 4.2)",
        "recommended_for": "Kompaktes Notstromaggregat"
    },
    {
        "id": "cummins_qsk60",
        "brand": "Cummins",
        "model": "QSK60-G4 (1.8 MW)",
        "rated_active_kw": 1800.0,
        "rated_apparent_kva": 2250.0,
        "ac_voltage_v": 400.0,
        "fuel_type": "Diesel",
        "interface": "Modbus TCP (PowerCommand)",
        "recommended_for": "Großflächige Notstromversorgung"
    },
    {
        "id": "jenbacher_jms420",
        "brand": "INNIO Jenbacher",
        "model": "JMS 420 (BHKW / Erdgas 1.5 MW)",
        "rated_active_kw": 1500.0,
        "rated_apparent_kva": 1875.0,
        "ac_voltage_v": 400.0,
        "fuel_type": "Erdgas / Biogas",
        "interface": "Modbus TCP / DIA.NE",
        "recommended_for": "Kraft-Wärme-Kopplung (KWK) & Dauerbetrieb"
    }
]

MARKET_OTHER_EZE: List[Dict[str, Any]] = [
    {
        "id": "hydro_kaplan_500",
        "brand": "Voith / Andritz",
        "model": "Kaplan-Rohrturbine 500 kW",
        "rated_active_kw": 500.0,
        "rated_apparent_kva": 550.0,
        "ac_voltage_v": 400.0,
        "source": "Wasserkraft (Hydro)",
        "interface": "Modbus TCP",
        "recommended_for": "Laufwasserkraftwerk"
    },
    {
        "id": "biomass_wood_800",
        "brand": "Spanner Re² / Burkhardt",
        "model": "Holzvergaser BHKW 800 kW",
        "rated_active_kw": 800.0,
        "rated_apparent_kva": 900.0,
        "ac_voltage_v": 400.0,
        "source": "Biomasse / Holzpellets",
        "interface": "Modbus TCP",
        "recommended_for": "Grundlastfähige regenerative Einspeisung"
    }
]

MARKET_TRANSFORMERS: List[Dict[str, Any]] = [
    {"id": "trafo_630", "name": "630 kVA (20 kV / 400 V)", "rated_kva": 630.0, "primary_kv": 20.0, "secondary_v": 400.0, "uk_percent": 4.0, "vector_group": "Dyn5"},
    {"id": "trafo_800", "name": "800 kVA (20 kV / 400 V)", "rated_kva": 800.0, "primary_kv": 20.0, "secondary_v": 400.0, "uk_percent": 6.0, "vector_group": "Dyn5"},
    {"id": "trafo_1000", "name": "1000 kVA (20 kV / 400 V)", "rated_kva": 1000.0, "primary_kv": 20.0, "secondary_v": 400.0, "uk_percent": 6.0, "vector_group": "Dyn5"},
    {"id": "trafo_1250", "name": "1250 kVA (20 kV / 400 V)", "rated_kva": 1250.0, "primary_kv": 20.0, "secondary_v": 400.0, "uk_percent": 6.0, "vector_group": "Dyn5"},
    {"id": "trafo_1600", "name": "1600 kVA (20 kV / 400 V)", "rated_kva": 1600.0, "primary_kv": 20.0, "secondary_v": 400.0, "uk_percent": 6.0, "vector_group": "Dyn5"},
    {"id": "trafo_2000", "name": "2000 kVA (20 kV / 400 V)", "rated_kva": 2000.0, "primary_kv": 20.0, "secondary_v": 400.0, "uk_percent": 6.0, "vector_group": "Dyn5"},
    {"id": "trafo_2500", "name": "2500 kVA (20 kV / 400 V)", "rated_kva": 2500.0, "primary_kv": 20.0, "secondary_v": 400.0, "uk_percent": 6.0, "vector_group": "Dyn5"},
    {"id": "trafo_3150", "name": "3150 kVA (20 kV / 690 V)", "rated_kva": 3150.0, "primary_kv": 20.0, "secondary_v": 690.0, "uk_percent": 6.0, "vector_group": "Dyn11"},
    {"id": "trafo_4000", "name": "4000 kVA (20 kV / 800 V)", "rated_kva": 4000.0, "primary_kv": 20.0, "secondary_v": 800.0, "uk_percent": 6.0, "vector_group": "Dyn11"},
    {"id": "trafo_5000", "name": "5000 kVA (20 kV / 800 V)", "rated_kva": 5000.0, "primary_kv": 20.0, "secondary_v": 800.0, "uk_percent": 6.0, "vector_group": "Dyn11"}
]

MARKET_METERS: List[Dict[str, Any]] = [
    {
        "id": "janitza_umg604e",
        "brand": "Janitza",
        "model": "UMG 604E / 605",
        "type": "Class 0.2S Power Quality Analysator",
        "protocol": "Modbus TCP",
        "default_port": 502,
        "vde4110_certified": True,
        "recommended_for": "Mittelspannung NAP Übergabemessung"
    },
    {
        "id": "janitza_umg96rm",
        "brand": "Janitza",
        "model": "UMG 96RM-E",
        "type": "Multifunktionsmessgerät",
        "protocol": "Modbus TCP",
        "default_port": 502,
        "vde4110_certified": True,
        "recommended_for": "Unterverteilungen & Erzeugungsabgänge"
    },
    {
        "id": "siemens_pac3200",
        "brand": "Siemens",
        "model": "SENTRON PAC3200 / PAC4200",
        "type": "Netzmessgerät Class 0.5S",
        "protocol": "Modbus TCP / PROFINET",
        "default_port": 502,
        "vde4110_certified": True,
        "recommended_for": "Industrie- & Übergabestationen"
    },
    {
        "id": "schneider_pm5350",
        "brand": "Schneider Electric",
        "model": "PowerLogic PM5350 / ION9000",
        "type": "Hochpräzisions-Netzanalysator",
        "protocol": "Modbus TCP",
        "default_port": 502,
        "vde4110_certified": True,
        "recommended_for": "Mittel- & Hochspannungsübergabe"
    },
    {
        "id": "phoenix_empro_ma600",
        "brand": "Phoenix Contact",
        "model": "EMpro MA600",
        "type": "Energiezähler & Netzanalysator",
        "protocol": "Modbus TCP / REST",
        "default_port": 502,
        "vde4110_certified": True,
        "recommended_for": "EZA-Regler Direktanbindung"
    }
]

MARKET_PROTECTION_RELAYS: List[Dict[str, Any]] = [
    {
        "id": "ziehl_ufr1001e",
        "brand": "Ziehl",
        "model": "UFR1001E",
        "type": "Netz- und Anlagenschutz (NA-Schutz)",
        "voltage_levels": "Niederspannung & Mittelspannung",
        "certified_standards": ["VDE-AR-N 4105", "VDE-AR-N 4110"],
        "trip_time_ms": 50
    },
    {
        "id": "woodward_mrm4",
        "brand": "Woodward",
        "model": "HighProTec MRM4",
        "type": "Mittelspannungs-Spannungs- und Frequenzschutz",
        "voltage_levels": "Mittelspannung 10-30 kV",
        "certified_standards": ["VDE-AR-N 4110", "VDE-AR-N 4120"],
        "trip_time_ms": 30
    },
    {
        "id": "seg_wic1",
        "brand": "SEG Electronics",
        "model": "WIC1",
        "type": "Stromwandler-versorgter Überstromzeitschutz",
        "voltage_levels": "Mittelspannung",
        "certified_standards": ["VDE-AR-N 4110", "IEC 60255"],
        "trip_time_ms": 40
    },
    {
        "id": "sel_751",
        "brand": "Schweitzer Engineering Laboratories (SEL)",
        "model": "SEL-751 Feeder Protection Relay",
        "type": "Leitungs- und Anlagenschutzrelais",
        "voltage_levels": "Mittelspannung / Großanlagen",
        "certified_standards": ["IEEE C37", "IEC 60255", "VDE-AR-N 4110"],
        "trip_time_ms": 25
    }
]

COMMON_GRID_OPERATORS: List[str] = [
    "Netze BW GmbH (EnBW)",
    "Bayernwerk Netz GmbH (E.ON)",
    "E.DIS Netz GmbH (E.ON)",
    "Westnetz GmbH (E.ON)",
    "Avacon Netz GmbH (E.ON)",
    "Mitteldeutsche Netzgesellschaft Strom mbH (MITNETZ STROM)",
    "Syna GmbH (Süwag)",
    "Netz Leipzig GmbH",
    "Stromnetz Berlin GmbH",
    "Stromnetz Hamburg GmbH",
    "TenneT TSO GmbH (Übertragungsnetz)",
    "TransnetBW GmbH (Übertragungsnetz)",
    "50Hertz Transmission GmbH",
    "Amprion GmbH"
]

PRESET_TEMPLATES: List[Dict[str, Any]] = [
    {
        "id": "preset_pv_1500kw",
        "title": "☀️ 1.5 MW Solar-Park (Mittelspannung 20 kV)",
        "subtitle": "Klassischer Freiflächen- oder Großdach-Solarpark mit Huawei String-Wechselrichtern und Maschinentransformator.",
        "plant_name": "Solarpark Musterpark 1.5 MWp",
        "grid_operator": "Netze BW GmbH (EnBW)",
        "voltage_level_kv": 20.0,
        "p_av_kw": 1500.0,
        "site_type": "PV",
        "has_transformer": True,
        "transformer": {
            "is_custom": False,
            "catalog_id": "trafo_1600",
            "rated_kva": 1600.0,
            "primary_kv": 20.0,
            "secondary_v": 400.0,
            "uk_percent": 6.0,
            "vector_group": "Dyn5"
        },
        "components": [
            {
                "type": "PV_INVERTER",
                "is_custom": False,
                "catalog_id": "huawei_sun2000_115ktl",
                "brand": "Huawei",
                "model": "SUN2000-115KTL-M2",
                "count": 13,
                "unit_active_kw": 115.0,
                "unit_apparent_kva": 125.0,
                "ac_voltage_v": 400.0
            }
        ],
        "meter": {
            "is_custom": False,
            "catalog_id": "janitza_umg604e",
            "brand": "Janitza",
            "model": "UMG 604E",
            "ip": "192.168.1.100",
            "port": 502
        },
        "protection": {
            "is_custom": False,
            "catalog_id": "woodward_mrm4",
            "brand": "Woodward",
            "model": "HighProTec MRM4"
        },
        "reactive_mode": "QU",
        "notes": "Erzeugt über interaktiven Fragebogen. Vollständig VDE-AR-N 4110 konform vorkonfiguriert."
    },
    {
        "id": "preset_hybrid_bess_2500kwh",
        "title": "🔋 2.5 MWh PV + BESS Hybridanlage",
        "subtitle": "Zukunftssichere Hybridanlage mit 1.2 MW PV und 2.5 MWh BYD Batteriespeicher für Peak-Shaving und Netzdienstleistung.",
        "plant_name": "Hybridpark BESS EnBW 1.2MW / 2.5MWh",
        "grid_operator": "Netze BW GmbH (EnBW)",
        "voltage_level_kv": 20.0,
        "p_av_kw": 2000.0,
        "site_type": "HYBRID",
        "has_transformer": True,
        "transformer": {
            "is_custom": False,
            "catalog_id": "trafo_2500",
            "rated_kva": 2500.0,
            "primary_kv": 20.0,
            "secondary_v": 400.0,
            "uk_percent": 6.0,
            "vector_group": "Dyn5"
        },
        "components": [
            {
                "type": "PV_INVERTER",
                "is_custom": False,
                "catalog_id": "sma_peak3_150",
                "brand": "SMA",
                "model": "Sunny Highpower PEAK3 (SHP 150-20)",
                "count": 8,
                "unit_active_kw": 150.0,
                "unit_apparent_kva": 150.0,
                "ac_voltage_v": 400.0
            },
            {
                "type": "BESS",
                "is_custom": False,
                "catalog_id": "byd_mc_cube_2500",
                "brand": "BYD",
                "model": "MC Cube Commercial 2.5 MWh",
                "count": 1,
                "unit_active_kw": 1250.0,
                "unit_apparent_kva": 1250.0,
                "capacity_kwh": 2500.0,
                "ac_voltage_v": 690.0
            }
        ],
        "meter": {
            "is_custom": False,
            "catalog_id": "janitza_umg604e",
            "brand": "Janitza",
            "model": "UMG 604E",
            "ip": "192.168.1.100",
            "port": 502
        },
        "protection": {
            "is_custom": False,
            "catalog_id": "woodward_mrm4",
            "brand": "Woodward",
            "model": "HighProTec MRM4"
        },
        "reactive_mode": "QU",
        "notes": "PV+Speicher Hybridanlage. Automatisch dimensionierter Trafo und EZA-Regelung."
    },
    {
        "id": "preset_commercial_pv_400v",
        "title": "🏢 450 kW C&I Gewerbe-Dachanlage (400 V)",
        "subtitle": "Dachanlage für Gewerbe/Industrie mit Direktanschluss an die kundeneigene Niederspannung.",
        "plant_name": "Gewerbedach Süd 450 kWp",
        "grid_operator": "Bayernwerk Netz GmbH (E.ON)",
        "voltage_level_kv": 0.4,
        "p_av_kw": 450.0,
        "site_type": "PV",
        "has_transformer": False,
        "transformer": None,
        "components": [
            {
                "type": "PV_INVERTER",
                "is_custom": False,
                "catalog_id": "sma_core2_110",
                "brand": "SMA",
                "model": "Sunny Tripower CORE2 (STP 110-60)",
                "count": 4,
                "unit_active_kw": 110.0,
                "unit_apparent_kva": 110.0,
                "ac_voltage_v": 400.0,
                "has_sub_meter": False
            }
        ],
        "meter": {
            "is_custom": False,
            "catalog_id": "siemens_pac3200",
            "brand": "Siemens",
            "model": "SENTRON PAC3200",
            "ip": "192.168.10.50",
            "port": 502
        },
        "protection": {
            "is_custom": False,
            "catalog_id": "ziehl_ufr1001e",
            "brand": "Ziehl",
            "model": "UFR1001E"
        },
        "reactive_mode": "COS_PHI",
        "notes": "C&I Dachanlage mit NA-Schutz am zentralen Zählerplatz."
    },
    {
        "id": "preset_wind_4200kw",
        "title": "🌀 4.2 MW Windpark (Vestas EnVentus 20 kV)",
        "subtitle": "Utility-Scale Windkraftanlage mit eigener Mittelspannungs-Übergabestation und Erzeugungsmessung.",
        "plant_name": "Windpark Hunsrück 4.2 MW",
        "grid_operator": "Westnetz GmbH (E.ON)",
        "voltage_level_kv": 20.0,
        "p_av_kw": 4200.0,
        "site_type": "WIND",
        "has_transformer": True,
        "transformer": {
            "is_custom": False,
            "catalog_id": "trafo_5000",
            "rated_kva": 5000.0,
            "primary_kv": 20.0,
            "secondary_v": 720.0,
            "uk_percent": 6.0,
            "vector_group": "Dyn11"
        },
        "components": [
            {
                "type": "WIND_TURBINE",
                "is_custom": False,
                "catalog_id": "vestas_v150_42",
                "brand": "Vestas",
                "model": "V150-4.2 MW EnVentus",
                "count": 1,
                "unit_active_kw": 4200.0,
                "unit_apparent_kva": 4500.0,
                "ac_voltage_v": 720.0,
                "has_sub_meter": True,
                "sub_meter_model": "Janitza UMG 604E",
                "sub_meter_ip": "192.168.1.110"
            }
        ],
        "meter": {
            "is_custom": False,
            "catalog_id": "janitza_umg604e",
            "brand": "Janitza",
            "model": "UMG 604E",
            "ip": "192.168.1.100",
            "port": 502
        },
        "protection": {
            "is_custom": False,
            "catalog_id": "woodward_mrm4",
            "brand": "Woodward",
            "model": "HighProTec MRM4"
        },
        "reactive_mode": "QU",
        "notes": "4.2 MW Windkraftanlage nach VDE-AR-N 4110 mit Q(U)-Regelung und Turbinen-Teilnehmermessung."
    },
    {
        "id": "preset_microgrid_hybrid",
        "title": "⚡ Multi-EZE Hybrid: PV + BESS + Dieselgenerator (Microgrid)",
        "subtitle": "Autarkes Microgrid mit 1.0 MW PV, 2.5 MWh BYD Batteriespeicher und 1.6 MW CAT Diesel-Aggregat mit individuellen Teilnehmermessungen.",
        "plant_name": "Industriepark Hybrid Microgrid 2.6 MW",
        "grid_operator": "Netze BW GmbH (EnBW)",
        "voltage_level_kv": 20.0,
        "p_av_kw": 2500.0,
        "site_type": "HYBRID_MULTI_EZE",
        "has_transformer": True,
        "transformer": {
            "is_custom": False,
            "catalog_id": "trafo_3150",
            "rated_kva": 3150.0,
            "primary_kv": 20.0,
            "secondary_v": 400.0,
            "uk_percent": 6.0,
            "vector_group": "Dyn5"
        },
        "components": [
            {
                "type": "PV_INVERTER",
                "is_custom": False,
                "catalog_id": "huawei_sun2000_100ktl",
                "brand": "Huawei",
                "model": "SUN2000-100KTL-M2",
                "count": 10,
                "unit_active_kw": 100.0,
                "unit_apparent_kva": 110.0,
                "ac_voltage_v": 400.0,
                "has_sub_meter": True,
                "sub_meter_model": "Janitza UMG 96RM-E",
                "sub_meter_ip": "192.168.1.101"
            },
            {
                "type": "BESS",
                "is_custom": False,
                "catalog_id": "byd_mc_cube_2500",
                "brand": "BYD",
                "model": "MC Cube Commercial 2.5 MWh",
                "count": 1,
                "unit_active_kw": 1250.0,
                "unit_apparent_kva": 1250.0,
                "capacity_kwh": 2500.0,
                "ac_voltage_v": 400.0,
                "has_sub_meter": True,
                "sub_meter_model": "Janitza UMG 96RM-E",
                "sub_meter_ip": "192.168.1.102"
            },
            {
                "type": "DIESEL_GEN",
                "is_custom": False,
                "catalog_id": "cat_3516b",
                "brand": "Caterpillar (CAT)",
                "model": "CAT 3516B-HD (1.6 MW)",
                "count": 1,
                "unit_active_kw": 1600.0,
                "unit_apparent_kva": 2000.0,
                "ac_voltage_v": 400.0,
                "has_sub_meter": True,
                "sub_meter_model": "Siemens SENTRON PAC3200",
                "sub_meter_ip": "192.168.1.103"
            }
        ],
        "meter": {
            "is_custom": False,
            "catalog_id": "janitza_umg604e",
            "brand": "Janitza",
            "model": "UMG 604E",
            "ip": "192.168.1.100",
            "port": 502
        },
        "protection": {
            "is_custom": False,
            "catalog_id": "woodward_mrm4",
            "brand": "Woodward",
            "model": "HighProTec MRM4"
        },
        "reactive_mode": "QU",
        "notes": "Multi-EZE Anlage nach VDE-AR-N 4110 Abschnitt 10 mit individueller Teilnehmermessung an PV, BESS und Notstromaggregat."
    }
]

MARKET_SUB_METERS: List[Dict[str, Any]] = [
    {
        "id": "sub_janitza_umg96rm",
        "brand": "Janitza",
        "model": "UMG 96RM-E",
        "type": "Multifunktions-Messgerät Erzeugungsabgang",
        "protocol": "Modbus TCP",
        "default_port": 502,
        "recommended_for": "Teilnehmermessung EZE (PV, Wind, BESS, Aggregat)"
    },
    {
        "id": "sub_janitza_umg604e",
        "brand": "Janitza",
        "model": "UMG 604E",
        "type": "Power Quality Analyser Class 0.2S",
        "protocol": "Modbus TCP",
        "default_port": 502,
        "recommended_for": "Hochpräzise Zwischenmessung"
    },
    {
        "id": "sub_siemens_pac3200",
        "brand": "Siemens",
        "model": "SENTRON PAC3200",
        "type": "Energiezähler Abgang",
        "protocol": "Modbus TCP",
        "default_port": 502,
        "recommended_for": "Industrie- & Abgangsüberwachung"
    },
    {
        "id": "sub_phoenix_empro",
        "brand": "Phoenix Contact",
        "model": "EMpro MA600",
        "type": "Energiezähler EZA Direktmessung",
        "protocol": "Modbus TCP",
        "default_port": 502,
        "recommended_for": "EZA Regler Teilnehmererfassung"
    },
    {
        "id": "sub_weidmueller_em500",
        "brand": "Weidmüller",
        "model": "Energy Meter EM500",
        "type": "Hutschienen-Messgerät Modbus RTU/TCP",
        "protocol": "Modbus TCP",
        "default_port": 502,
        "recommended_for": "Kompakte Unterverteilungen"
    }
]

def get_full_catalog() -> Dict[str, Any]:
    """Returns the complete market component catalog and presets."""
    return {
        "pv_inverters": MARKET_PV_INVERTERS,
        "bess_systems": MARKET_BESS_SYSTEMS,
        "wind_turbines": MARKET_WIND_TURBINES,
        "diesel_generators": MARKET_DIESEL_GENSETS,
        "other_eze": MARKET_OTHER_EZE,
        "sub_meters": MARKET_SUB_METERS,
        "transformers": MARKET_TRANSFORMERS,
        "meters": MARKET_METERS,
        "protection_relays": MARKET_PROTECTION_RELAYS,
        "grid_operators": COMMON_GRID_OPERATORS,
        "presets": PRESET_TEMPLATES
    }

