import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FILE_PATH = 'backend/templates/index.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

print("Original length:", len(content))

# 1. Update HTML in .screen-top
old_screen_top = """                        <div style="display: flex; align-items: center; gap: 0.65rem;">
                            <select id="flowSimSelect" onchange="setFlowSimulationMode(this.value)" class="sim-mode-select" title="Betriebs- und Simulationsmodus">
                                <option value="normal">☀️ Tagbetrieb (PV 2,2 MW + BESS Laden)</option>
                                <option value="peak">🔋 Spitzenlast (BESS Entladung + PV)</option>
                                <option value="curtail">⚠️ Wirkleistungsreduktion 50% (DSO)</option>
                                <option value="qu_boost">⚡ Q(U)-Spannungsstützung (+280 kvar)</option>
                            </select>
                            <span class="status">● ONLINE · REGELT</span>
                        </div>"""

new_screen_top = """                        <div style="display: flex; align-items: center; gap: 0.65rem; flex-wrap: wrap;">
                            <div style="display: flex; align-items: center; gap: 0.35rem;">
                                <label for="flowPlantSelect" style="font-size: 0.74rem; color: #94a3b8; font-weight: 600;">Anlage:</label>
                                <select id="flowPlantSelect" onchange="onEnergyFlowPlantChange(this.value)" class="sim-mode-select" style="min-width: 190px; max-width: 270px; font-weight: 700; color: #38bdf8; background: #0c1a2c; border: 1.5px solid #0284c7;" title="Erzeugungsanlage für Energiefluss und Regelung auswählen">
                                    <option value="ALL">🌐 Alle Standorte / Gesamtflotte</option>
                                </select>
                            </div>
                            <select id="flowSimSelect" onchange="setFlowSimulationMode(this.value)" class="sim-mode-select" title="Betriebs- und Simulationsmodus">
                                <option value="normal">☀️ Tagbetrieb (Volllast + BESS)</option>
                                <option value="peak">🔋 Spitzenlast (BESS Entladung)</option>
                                <option value="curtail">⚠️ Abregelung 50% (DSO)</option>
                                <option value="qu_boost">⚡ Q(U)-Spannungsstützung</option>
                            </select>
                            <span class="status" id="flowStatusBadge">● ONLINE · REGELT</span>
                        </div>"""

assert old_screen_top in content, "Could not find old_screen_top"
content = content.replace(old_screen_top, new_screen_top, 1)
print("Updated .screen-top with flowPlantSelect dropdown!")

# 2. Add IDs to SVG elements for dynamic plant updates
old_node_solar = """                            <!-- NODE 1: Solar (PV) -->
                            <g class="flow-node" id="nodeSolar">
                                <rect x="12" y="16" width="145" height="68" rx="10" fill="#0b1c2d" stroke="#f59e0b" stroke-width="1.8" />
                                <text x="24" y="38" fill="#fbbf24" font-size="12" font-weight="700">☀️ Solar PV</text>"""

new_node_solar = """                            <!-- NODE 1: Solar (PV) -->
                            <g class="flow-node" id="nodeSolar">
                                <rect x="12" y="16" width="145" height="68" rx="10" fill="#0b1c2d" stroke="#f59e0b" stroke-width="1.8" />
                                <text x="24" y="38" fill="#fbbf24" font-size="12" font-weight="700" id="flowNode1Title">☀️ Solar PV</text>"""

assert old_node_solar in content, "Could not find old_node_solar"
content = content.replace(old_node_solar, new_node_solar, 1)

old_node_eza = """                            <!-- NODE 3: Zentraler EZA-Regler (Sammelschiene) -->
                            <g class="flow-node" id="nodeEza">
                                <rect x="242" y="56" width="175" height="88" rx="12" fill="url(#gradEza)" stroke="#25c7c9" stroke-width="2.2" filter="url(#glowCyan)" />
                                <text x="254" y="78" fill="#25c7c9" font-size="12" font-weight="800">⚡ Phoenix Contact EZA</text>
                                <text x="254" y="93" fill="#94a3b8" font-size="9.5">AXC F 2152 · VDE 4110</text>"""

new_node_eza = """                            <!-- NODE 3: Zentraler EZA-Regler (Sammelschiene) -->
                            <g class="flow-node" id="nodeEza">
                                <rect x="242" y="56" width="175" height="88" rx="12" fill="url(#gradEza)" stroke="#25c7c9" stroke-width="2.2" filter="url(#glowCyan)" />
                                <text x="254" y="78" fill="#25c7c9" font-size="12" font-weight="800" id="flowEzaTitle">⚡ Phoenix Contact EZA</text>
                                <text x="254" y="93" fill="#94a3b8" font-size="9.5" id="flowEzaSub">AXC F 2152 · VDE 4110</text>"""

assert old_node_eza in content, "Could not find old_node_eza"
content = content.replace(old_node_eza, new_node_eza, 1)

old_node_grid = """                            <!-- NODE 5: Netzanschlusspunkt (NAP 20 kV) -->
                            <g class="flow-node" id="nodeGrid">
                                <rect x="500" y="56" width="148" height="88" rx="12" fill="url(#gradGrid)" stroke="#38bdf8" stroke-width="2.2" filter="url(#glowCyan)" />
                                <text x="512" y="78" fill="#38bdf8" font-size="12" font-weight="800">🌐 Netz (NAP 20 kV)</text>
                                <text x="512" y="93" fill="#94a3b8" font-size="9.5">Bayernwerk 20 kV MS</text>"""

new_node_grid = """                            <!-- NODE 5: Netzanschlusspunkt (NAP 20 kV) -->
                            <g class="flow-node" id="nodeGrid">
                                <rect x="500" y="56" width="148" height="88" rx="12" fill="url(#gradGrid)" stroke="#38bdf8" stroke-width="2.2" filter="url(#glowCyan)" />
                                <text x="512" y="78" fill="#38bdf8" font-size="12" font-weight="800" id="flowNapTitle">🌐 Netz (NAP 20 kV)</text>
                                <text x="512" y="93" fill="#94a3b8" font-size="9.5" id="flowNapSub">Bayernwerk 20 kV MS</text>"""

assert old_node_grid in content, "Could not find old_node_grid"
content = content.replace(old_node_grid, new_node_grid, 1)

old_net_header = """                    <!-- 1. NETZWERK-PARAMETER (Netz- und Anschlussparameter) -->
                    <div class="flow-section-header">
                        <span>🌐 Netzwerk-Parameter (NAP / Mittelspannung)</span>
                        <span style="font-family: var(--font-mono); font-size: 0.65rem; color: #10b981;">3-phasig 20 kV</span>
                    </div>"""

new_net_header = """                    <!-- 1. NETZWERK-PARAMETER (Netz- und Anschlussparameter) -->
                    <div class="flow-section-header">
                        <span>🌐 Netzwerk-Parameter (NAP / <span id="flowNetLevelName">Mittelspannung</span>)</span>
                        <span style="font-family: var(--font-mono); font-size: 0.65rem; color: #10b981;" id="flowNetVoltageHeader">3-phasig 20 kV</span>
                    </div>"""

assert old_net_header in content, "Could not find old_net_header"
content = content.replace(old_net_header, new_net_header, 1)

# 3. Add "⚡ Im Energiefluss anzeigen" button into each plant card in loadPlants()
old_card_buttons = """                        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--line); padding-top: 0.95rem; margin-top: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
                            <button class="btn btn-primary" style="padding: 0.5rem 1.1rem; font-size: 0.84rem;" onclick="openPlantDetail('${p.id}')">
                                🔍 Details & Geräte öffnen
                            </button>"""

new_card_buttons = """                        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--line); padding-top: 0.95rem; margin-top: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
                            <div style="display: flex; gap: 0.45rem; align-items: center;">
                                <button class="btn btn-primary" style="padding: 0.5rem 1rem; font-size: 0.84rem;" onclick="openPlantDetail('${p.id}')">
                                    🔍 Details & Geräte
                                </button>
                                <button type="button" class="btn btn-sm" style="font-size: 0.78rem; background: rgba(37, 199, 201, 0.12); color: #0284c7; border: 1px solid rgba(2, 132, 199, 0.35); font-weight: 700; padding: 0.48rem 0.75rem;" onclick="selectPlantForEnergyFlow('${p.id}')" title="Diese Anlage im interaktiven Energiefluss &amp; Regelungs-Monitor anzeigen">
                                    ⚡ Energiefluss
                                </button>
                            </div>"""

assert old_card_buttons in content, "Could not find old_card_buttons"
content = content.replace(old_card_buttons, new_card_buttons, 1)

# 4. In loadPlants(): call populateEnergyFlowPlantSelect()
old_load_plants_grid = """                // Render plant cards
                const grid = document.getElementById("plantsGrid");"""

new_load_plants_grid = """                // Populate energy flow plant select
                populateEnergyFlowPlantSelect();

                // Render plant cards
                const grid = document.getElementById("plantsGrid");"""

assert old_load_plants_grid in content, "Could not find old_load_plants_grid"
content = content.replace(old_load_plants_grid, new_load_plants_grid, 1)

# 5. Replace and enhance the EZA Energy Flow Physics Engine functions
old_flow_physics_start = "        // ----------------- EZA Energy Flow & Controller Physics Engine -----------------"
assert old_flow_physics_start in content, "Could not find old_flow_physics_start"

physics_block_end = "        // Initialize on page load: check auth without bypassing admin password"
assert physics_block_end in content, "Could not find physics_block_end"

start_p = content.find(old_flow_physics_start)
end_p = content.find(physics_block_end)

new_physics_code = """        // ----------------- EZA Energy Flow & Controller Physics Engine (Plant-Selectable) ----------------- //
        let flowSimulationMode = "normal"; // "normal" | "peak" | "curtail" | "qu_boost"
        let selectedFlowPlantId = "ALL";
        
        let flowBaseline = {
            name: "Gesamtflotte (Alle Standorte)",
            capacity_kw: 2200.0,
            voltage_kv: 20.0,
            grid_operator: "Bayernwerk Netz GmbH",
            site_type: "HYBRID",
            status: "ONLINE_REGULATING"
        };

        let flowState = {
            P_pv: 2180.0,
            P_bat: -320.0, // Negative = charging, positive = discharging
            P_load: 42.0,
            battery_soc: 84.0,
            U_grid: 20.12, // kV
            f_grid: 50.02, // Hz
            P_setpoint_percent: 100.0,
            Q_act: 45.0, // kvar
            cos_phi: 0.999
        };

        function populateEnergyFlowPlantSelect() {
            const select = document.getElementById("flowPlantSelect");
            if (!select) return;
            const currentVal = selectedFlowPlantId || select.value || "ALL";

            select.innerHTML = "";
            const totalCapKw = cachedPlants.reduce((acc, p) => acc + (Number(p.installed_capacity_kw) || 0), 0);
            
            const allOpt = document.createElement("option");
            allOpt.value = "ALL";
            const fleetCapText = totalCapKw > 0 ? `${(totalCapKw/1000).toFixed(2)} MWp` : "Flotte";
            allOpt.textContent = `🌐 Gesamtflotte (${cachedPlants.length} Standorte · ${fleetCapText})`;
            select.appendChild(allOpt);

            cachedPlants.forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.id;
                let icon = "☀️";
                if (p.site_type === "BESS") icon = "🔋";
                else if (p.site_type === "WIND") icon = "🌀";
                else if (p.site_type === "HYBRID") icon = "⚡";
                const cap = p.installed_capacity_kw ? `${p.installed_capacity_kw} kW` : "N/A";
                const vnb = p.grid_operator || "VNB";
                opt.textContent = `${icon} ${p.name} (${cap} · ${vnb})`;
                select.appendChild(opt);
            });

            if (cachedPlants.some(p => p.id === currentVal)) {
                select.value = currentVal;
            } else {
                select.value = "ALL";
            }
        }

        function onEnergyFlowPlantChange(plantId) {
            selectedFlowPlantId = plantId;
            const select = document.getElementById("flowPlantSelect");
            if (select && select.value !== plantId) select.value = plantId;

            if (plantId === "ALL" || !cachedPlants || cachedPlants.length === 0) {
                const totalCapKw = (cachedPlants || []).reduce((acc, p) => acc + (Number(p.installed_capacity_kw) || 0), 0);
                flowBaseline = {
                    name: "Gesamtflotte (Alle Standorte)",
                    capacity_kw: totalCapKw > 0 ? totalCapKw : 2200.0,
                    voltage_kv: 20.0,
                    grid_operator: "Verteilnetz (Flotte)",
                    site_type: "HYBRID",
                    status: "ONLINE_REGULATING"
                };
            } else {
                const plant = cachedPlants.find(p => p.id === plantId);
                if (plant) {
                    let vKv = 20.0;
                    const vStr = String(plant.voltage_level || "").toLowerCase();
                    if (vStr.includes("10")) vKv = 10.0;
                    else if (vStr.includes("30")) vKv = 30.0;
                    else if (vStr.includes("0.4") || vStr.includes("400")) vKv = 0.40;
                    else if (vStr.includes("110")) vKv = 110.0;
                    else vKv = 20.0;

                    flowBaseline = {
                        name: plant.name,
                        capacity_kw: Number(plant.installed_capacity_kw) || 1500.0,
                        voltage_kv: vKv,
                        grid_operator: plant.grid_operator || "Verteilnetzbetreiber",
                        site_type: plant.site_type || "PV",
                        status: plant.status || "ONLINE_REGULATING"
                    };
                }
            }

            // Recalculate simulation state based on baseline
            applySimulationModeToState(flowSimulationMode);
            updateEnergyFlowUI();
        }

        function selectPlantForEnergyFlow(plantId) {
            onEnergyFlowPlantChange(plantId);

            const card = document.querySelector(".controller-card");
            if (card) {
                card.scrollIntoView({ behavior: "smooth", block: "center" });
                card.style.transition = "box-shadow 0.3s ease, border-color 0.3s ease";
                card.style.borderColor = "#25c7c9";
                card.style.boxShadow = "0 0 30px rgba(37, 199, 201, 0.45)";
                setTimeout(() => {
                    card.style.boxShadow = "";
                    card.style.borderColor = "";
                }, 2000);
            }
        }

        function setFlowSimulationMode(mode) {
            flowSimulationMode = mode;
            applySimulationModeToState(mode);
            updateEnergyFlowUI();
        }

        function applySimulationModeToState(mode) {
            const cap = flowBaseline.capacity_kw;
            const uNom = flowBaseline.voltage_kv;
            const hasBess = flowBaseline.site_type === "BESS" || flowBaseline.site_type === "HYBRID";

            if (mode === "normal") {
                flowState.P_pv = cap * 0.95;
                flowState.P_bat = hasBess ? (-1 * Math.min(cap * 0.15, 320)) : 0.0;
                flowState.P_load = Math.max(10, Math.round(cap * 0.02));
                flowState.battery_soc = 84.0;
                flowState.U_grid = uNom * 1.006;
                flowState.f_grid = 50.02;
                flowState.P_setpoint_percent = 100.0;
                flowState.Q_act = Math.round(cap * 0.02);
            } else if (mode === "peak") {
                flowState.P_pv = cap * 0.70;
                flowState.P_bat = hasBess ? Math.min(cap * 0.30, 650) : 0.0;
                flowState.P_load = Math.max(10, Math.round(cap * 0.02));
                flowState.battery_soc = 62.0;
                flowState.U_grid = uNom * 1.004;
                flowState.f_grid = 49.98;
                flowState.P_setpoint_percent = 100.0;
                flowState.Q_act = -1 * Math.round(cap * 0.01);
            } else if (mode === "curtail") {
                flowState.P_pv = cap * 0.50; // Curtailment by DSO
                flowState.P_bat = 0.0;
                flowState.P_load = Math.max(10, Math.round(cap * 0.02));
                flowState.battery_soc = 85.0;
                flowState.U_grid = uNom * 1.009;
                flowState.f_grid = 50.15;
                flowState.P_setpoint_percent = 50.0;
                flowState.Q_act = Math.round(cap * 0.04);
            } else if (mode === "qu_boost") {
                flowState.P_pv = cap * 0.90;
                flowState.P_bat = hasBess ? -50.0 : 0.0;
                flowState.P_load = Math.max(10, Math.round(cap * 0.02));
                flowState.battery_soc = 86.0;
                flowState.U_grid = uNom * 0.9725; // Under-voltage
                flowState.f_grid = 50.01;
                flowState.P_setpoint_percent = 100.0;
                flowState.Q_act = Math.round(cap * 0.15); // Capacitive boost
            }
        }

        function tickEnergyFlowPhysics() {
            // Natural micro-fluctuations (subtle industrial telemetry jitter)
            const dF = (Math.random() * 0.02 - 0.01);
            const uNom = flowBaseline.voltage_kv;
            const dU = (Math.random() * 0.02 - 0.01) * (uNom / 20.0);
            const cap = flowBaseline.capacity_kw;
            const dPv = (Math.random() * 0.008 - 0.004) * cap;

            flowState.f_grid = Math.max(49.85, Math.min(50.25, flowState.f_grid + dF));
            flowState.U_grid = Math.max(uNom * 0.94, Math.min(uNom * 1.06, flowState.U_grid + dU));
            flowState.P_pv = Math.max(0, flowState.P_pv + dPv);

            // Battery SoC micro-drift
            if (flowState.P_bat < 0) {
                flowState.battery_soc = Math.min(99.9, flowState.battery_soc + 0.02);
            } else if (flowState.P_bat > 0) {
                flowState.battery_soc = Math.max(10.0, flowState.battery_soc - 0.03);
            }

            // Automatic Q(U) characteristic curve behavior (VDE-AR-N 4110)
            const uRatio = flowState.U_grid / uNom;
            if (uRatio < 0.97) {
                flowState.Q_act = Math.min(Math.round(cap * 0.33), Math.round(flowState.Q_act + (0.97 - uRatio) * (cap * 0.4)));
            } else if (uRatio > 1.03) {
                flowState.Q_act = Math.max(-1 * Math.round(cap * 0.33), Math.round(flowState.Q_act - (uRatio - 1.03) * (cap * 0.4)));
            }

            updateEnergyFlowUI();
        }

        function updateEnergyFlowUI() {
            const uNom = flowBaseline.voltage_kv;
            const cap = flowBaseline.capacity_kw;
            const hasBess = flowBaseline.site_type === "BESS" || flowBaseline.site_type === "HYBRID";

            // Net bus calculation
            const P_net = Math.max(0, flowState.P_pv + flowState.P_bat - flowState.P_load);
            const S_net = Math.sqrt(Math.pow(P_net, 2) + Math.pow(flowState.Q_act, 2));
            const I_net = (S_net > 0 && flowState.U_grid > 0) ? (S_net / (Math.sqrt(3) * flowState.U_grid)) : 0;
            const pf = S_net > 0 ? (P_net / S_net) : 1.0;

            // 1. Update SVG Titles and Nodes
            const elNode1Title = document.getElementById("flowNode1Title");
            if (elNode1Title) {
                if (flowBaseline.site_type === "WIND") elNode1Title.textContent = "🌀 Windkraft";
                else if (flowBaseline.site_type === "BESS") elNode1Title.textContent = "🔋 Speicher (EZE)";
                else elNode1Title.textContent = "☀️ Solar PV";
            }

            const elPpv = document.getElementById("flowPpv");
            if (elPpv) elPpv.textContent = `+${Math.round(flowState.P_pv).toLocaleString('de-DE')} kW`;

            const elPbat = document.getElementById("flowPbat");
            if (elPbat) {
                if (!hasBess) {
                    elPbat.textContent = "0 kW";
                } else {
                    const sign = flowState.P_bat > 0 ? "+" : (flowState.P_bat < 0 ? "-" : "±");
                    elPbat.textContent = `${sign}${Math.abs(Math.round(flowState.P_bat)).toLocaleString('de-DE')} kW`;
                }
            }

            const elSoc = document.getElementById("flowSoc");
            if (elSoc) {
                if (!hasBess) {
                    elSoc.textContent = "Kein BESS · Standby";
                } else {
                    const modeLabel = flowState.P_bat < 0 ? "Laden" : (flowState.P_bat > 0 ? "Entladen" : "Standby");
                    elSoc.textContent = `SoC: ${flowState.battery_soc.toFixed(0)}% · ${modeLabel}`;
                }
            }

            const elEzaTitle = document.getElementById("flowEzaTitle");
            if (elEzaTitle) {
                elEzaTitle.textContent = selectedFlowPlantId === "ALL" ? "⚡ Flotte EZA-Verbund" : `⚡ ${flowBaseline.name.slice(0, 22)}`;
            }

            const elPbus = document.getElementById("flowPbus");
            if (elPbus) elPbus.textContent = `${Math.round(P_net).toLocaleString('de-DE')} kW`;

            const elPload = document.getElementById("flowPload");
            if (elPload) elPload.textContent = `-${Math.round(flowState.P_load)} kW · Hilfsbetriebe`;

            const elNapTitle = document.getElementById("flowNapTitle");
            if (elNapTitle) {
                elNapTitle.textContent = `🌐 Netz (NAP ${uNom >= 1 ? `${uNom} kV` : `${Math.round(uNom*1000)} V`})`;
            }

            const elNapSub = document.getElementById("flowNapSub");
            if (elNapSub) {
                elNapSub.textContent = (flowBaseline.grid_operator || "VNB").slice(0, 24);
            }

            const elPgrid = document.getElementById("flowPgrid");
            if (elPgrid) elPgrid.textContent = `${Math.round(P_net).toLocaleString('de-DE')} kW`;

            // Battery flow path animation direction
            const pathBat = document.getElementById("pathBatteryFlow");
            if (pathBat) {
                if (!hasBess) {
                    pathBat.style.opacity = "0.2";
                } else {
                    pathBat.style.opacity = "1";
                    pathBat.className.baseVal = flowState.P_bat > 0 ? "flow-line flow-line-bat-discharge" : "flow-line flow-line-bat-charge";
                }
            }

            // Status Badge
            const statusBadge = document.getElementById("flowStatusBadge");
            if (statusBadge) {
                if (flowBaseline.status === "COMMISSIONING") {
                    statusBadge.textContent = "● INBETRIEBNAHME";
                    statusBadge.style.color = "#0ea5e9";
                } else if (flowBaseline.status === "MAINTENANCE") {
                    statusBadge.textContent = "● WARTUNG";
                    statusBadge.style.color = "#f59e0b";
                } else {
                    statusBadge.textContent = "● ONLINE · REGELT";
                    statusBadge.style.color = "#10b981";
                }
            }

            // 2. Network Parameters Section
            const elNetLevelName = document.getElementById("flowNetLevelName");
            if (elNetLevelName) {
                elNetLevelName.textContent = uNom < 1 ? "Niederspannung (NS)" : (uNom >= 110 ? "Hochspannung (HS)" : "Mittelspannung (MS)");
            }

            const elNetVoltageHeader = document.getElementById("flowNetVoltageHeader");
            if (elNetVoltageHeader) {
                elNetVoltageHeader.textContent = `3-phasig ${uNom >= 1 ? `${uNom} kV` : `${Math.round(uNom*1000)} V`}`;
            }

            const elNetU = document.getElementById("flowNetU");
            if (elNetU) {
                elNetU.textContent = uNom >= 1 ? `${flowState.U_grid.toFixed(2)} kV` : `${Math.round(flowState.U_grid * 1000)} V`;
            }

            const elNetUPercent = document.getElementById("flowNetUPercent");
            if (elNetUPercent) {
                elNetUPercent.textContent = `${((flowState.U_grid / uNom) * 100).toFixed(1)}% U_n · L12/23/31`;
            }

            const elNetF = document.getElementById("flowNetF");
            if (elNetF) elNetF.textContent = `${flowState.f_grid.toFixed(2)} Hz`;

            const elNetFDelta = document.getElementById("flowNetFDelta");
            if (elNetFDelta) {
                const deltaF = flowState.f_grid - 50.0;
                const sign = deltaF >= 0 ? "+" : "";
                elNetFDelta.textContent = `Δf: ${sign}${deltaF.toFixed(2)} Hz · ${Math.abs(deltaF) < 0.1 ? 'Stabil' : 'Regelung aktiv'}`;
            }

            const elNetI = document.getElementById("flowNetI");
            if (elNetI) elNetI.textContent = `${I_net.toFixed(1)} A`;

            const elNetISub = document.getElementById("flowNetISub");
            if (elNetISub) elNetISub.textContent = `I_L1: ${I_net.toFixed(1)}A · I_L2: ${(I_net * 0.998).toFixed(1)}A`;

            const elNetS = document.getElementById("flowNetS");
            if (elNetS) elNetS.textContent = `${Math.round(S_net).toLocaleString('de-DE')} kVA`;

            const elNetSSub = document.getElementById("flowNetSSub");
            if (elNetSSub) {
                elNetSSub.textContent = `P: ${Math.round(P_net)} kW · Q: ${flowState.Q_act >= 0 ? '+' : ''}${Math.round(flowState.Q_act)} kvar`;
            }

            // 3. Control Parameters Section
            const elCtrlPAct = document.getElementById("flowCtrlPAct");
            if (elCtrlPAct) elCtrlPAct.textContent = `${Math.round(P_net).toLocaleString('de-DE')} kW`;

            const elCtrlPSet = document.getElementById("flowCtrlPSet");
            if (elCtrlPSet) {
                const pSetKw = Math.round(cap * flowState.P_setpoint_percent / 100);
                if (flowState.P_setpoint_percent < 100) {
                    elCtrlPSet.textContent = `Soll: ${flowState.P_setpoint_percent}% (${pSetKw.toLocaleString('de-DE')} kW)`;
                } else {
                    elCtrlPSet.textContent = `Soll: ${Math.round(cap).toLocaleString('de-DE')} kW (P_AV 100%)`;
                }
            }

            const elCtrlPBadge = document.getElementById("flowCtrlPBadge");
            if (elCtrlPBadge) {
                if (flowState.P_setpoint_percent < 100) {
                    elCtrlPBadge.textContent = `Abregelung ${flowState.P_setpoint_percent}%`;
                    elCtrlPBadge.className = "badge badge-danger";
                } else {
                    elCtrlPBadge.textContent = "P_AV 100%";
                    elCtrlPBadge.className = "badge badge-online";
                }
            }

            const elCtrlQAct = document.getElementById("flowCtrlQAct");
            if (elCtrlQAct) {
                const sign = flowState.Q_act >= 0 ? "+" : "";
                elCtrlQAct.textContent = `${sign}${Math.round(flowState.Q_act)} kvar`;
            }

            const elCtrlQMode = document.getElementById("flowCtrlQMode");
            if (elCtrlQMode) {
                const uRatio = flowState.U_grid / uNom;
                if (uRatio >= 0.97 && uRatio <= 1.03) {
                    elCtrlQMode.textContent = "Totband 97-103% Un (Regler stabil)";
                } else if (uRatio < 0.97) {
                    elCtrlQMode.textContent = "Q(U) kapazitiv stützend (+Q)";
                } else {
                    elCtrlQMode.textContent = "Q(U) induktiv dämpfend (-Q)";
                }
            }

            const elCtrlQBadge = document.getElementById("flowCtrlQBadge");
            if (elCtrlQBadge) {
                const uRatio = flowState.U_grid / uNom;
                if (uRatio >= 0.97 && uRatio <= 1.03) {
                    elCtrlQBadge.textContent = "Q(U)";
                    elCtrlQBadge.className = "badge badge-super";
                } else {
                    elCtrlQBadge.textContent = "Q(U) DYNAMISCH";
                    elCtrlQBadge.className = "badge badge-engineer";
                }
            }

            const elCtrlFAct = document.getElementById("flowCtrlFAct");
            if (elCtrlFAct) elCtrlFAct.textContent = `${flowState.f_grid.toFixed(2)} Hz`;

            const elCtrlPFAct = document.getElementById("flowCtrlPFAct");
            if (elCtrlPFAct) elCtrlPFAct.textContent = `${pf.toFixed(3)} ${isInductive ? 'ind' : 'kap'}`;
        }
\n"""

content = content[:start_p] + new_physics_code + content[end_p:]
print("Replaced physics code with plant-selectable engine successfully!")

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"File updated! New length: {len(content)}")
