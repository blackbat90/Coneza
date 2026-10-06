import re

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update .hero-banner CSS to 1fr 1fr, align-items: stretch, and add .hero-left-col + compliance styling
old_hero_css = """        /* Hero / Overview Banner matching Coneza.de */
        .hero-banner {
            background: linear-gradient(135deg, #091522 0%, #0d2842 56%, #06445d 100%);
            border: 1px solid rgba(37, 199, 201, 0.25);
            border-radius: 20px;
            padding: 2.2rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 16px 45px rgba(11, 23, 40, 0.12);
            display: grid;
            grid-template-columns: 0.85fr 1.15fr;
            gap: 2.2rem;
            align-items: start;
            color: #ffffff;
        }"""

new_hero_css = """        /* Hero / Overview Banner matching Coneza.de */
        .hero-banner {
            background: linear-gradient(135deg, #091522 0%, #0d2842 56%, #06445d 100%);
            border: 1px solid rgba(37, 199, 201, 0.25);
            border-radius: 20px;
            padding: 2.2rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 16px 45px rgba(11, 23, 40, 0.12);
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2.2rem;
            align-items: stretch;
            color: #ffffff;
        }

        .hero-left-col {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
        }

        .hero-compliance-bar {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.65rem;
            background: rgba(8, 21, 34, 0.65);
            border: 1px solid rgba(37, 199, 201, 0.2);
            border-radius: 12px;
            padding: 0.75rem 0.9rem;
            backdrop-filter: blur(8px);
            margin-top: 1.25rem;
        }

        .hero-compliance-item {
            display: flex;
            align-items: center;
            gap: 0.55rem;
        }

        .hero-compliance-icon {
            font-size: 1.1rem;
            background: rgba(37, 199, 201, 0.12);
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            border: 1px solid rgba(37, 199, 201, 0.25);
            flex-shrink: 0;
        }

        .hero-compliance-title {
            font-size: 0.75rem;
            font-weight: 700;
            color: #ecfeff;
            line-height: 1.2;
        }

        .hero-compliance-desc {
            font-size: 0.66rem;
            color: #94a3b8;
            line-height: 1.2;
        }"""

assert old_hero_css in content, "old_hero_css not found"
content = content.replace(old_hero_css, new_hero_css)

# 2. Update .hero-banner HTML structure for left column
old_left_html = """        <!-- Hero Overview matching Coneza.de -->
        <section class="hero-banner">
            <div>
                <div class="eyebrow">EZA-Regler für moderne Energieanlagen</div>
                <h1>Netzkonform. <span style="color:var(--cyan-accent)">Präzise.</span> Zukunftssicher.</h1>
                <p>Coneza verbindet Erzeugungsanlagen (PV, Wind, BESS) und Netzanschlusspunkt zu einem intelligenten Regelungssystem nach VDE-AR-N 4110 / 4120 – vollautomatische Dokumentenanalyse, Modbus TCP Inbetriebnahme und Flottensteuerung.</p>
                <div style="display: flex; gap: 0.85rem; flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="openPlantQuestionnaireModal()" style="background: linear-gradient(135deg, #10b981, #0ea5e9); border:none; box-shadow: 0 4px 14px rgba(16,185,129,0.35); font-weight:700;">
                        🧙‍♂️ Anlage anlegen (Schritt-für-Schritt Wizard)
                    </button>
                    <button class="btn" onclick="switchTab('geminiTab', document.querySelectorAll('.tab-btn')[2])">
                        ✨ Gemini Netzprüfung starten
                    </button>
                    <button class="btn" onclick="switchTab('docsTab', document.querySelectorAll('.tab-btn')[1])">
                        📄 Dokumente hochladen (E.8 / E.9 / SLD)
                    </button>
                </div>
            </div>"""

new_left_html = """        <!-- Hero Overview matching Coneza.de -->
        <section class="hero-banner">
            <div class="hero-left-col">
                <div>
                    <div class="eyebrow">EZA-Regler für moderne Energieanlagen</div>
                    <h1>Netzkonform. <span style="color:var(--cyan-accent)">Präzise.</span> Zukunftssicher.</h1>
                    <p style="margin-bottom: 1.25rem;">Coneza verbindet Erzeugungsanlagen (PV, Wind, BESS) und Netzanschlusspunkt zu einem intelligenten Regelungssystem nach VDE-AR-N 4110 / 4120 – vollautomatische Dokumentenanalyse, Modbus TCP Inbetriebnahme und Flottensteuerung.</p>
                    <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1rem;">
                        <button class="btn btn-primary" onclick="openPlantQuestionnaireModal()" style="background: linear-gradient(135deg, #10b981, #0ea5e9); border:none; box-shadow: 0 4px 14px rgba(16,185,129,0.35); font-weight:700;">
                            🧙‍♂️ Anlage anlegen (Schritt-für-Schritt Wizard)
                        </button>
                        <button class="btn" onclick="switchTab('geminiTab', document.querySelectorAll('.tab-btn')[2])">
                            ✨ Gemini Netzprüfung starten
                        </button>
                        <button class="btn" onclick="switchTab('docsTab', document.querySelectorAll('.tab-btn')[1])">
                            📄 Dokumente hochladen (E.8 / E.9 / SLD)
                        </button>
                    </div>
                </div>

                <!-- Symmetrical Feature & Standard Badges to balance left column with console card -->
                <div class="hero-compliance-bar">
                    <div class="hero-compliance-item">
                        <span class="hero-compliance-icon">🛡️</span>
                        <div>
                            <div class="hero-compliance-title">VDE-AR-N 4110</div>
                            <div class="hero-compliance-desc">Zertifizierte EZA-Regelung</div>
                        </div>
                    </div>
                    <div class="hero-compliance-item">
                        <span class="hero-compliance-icon">⚡</span>
                        <div>
                            <div class="hero-compliance-title">Phoenix Contact</div>
                            <div class="hero-compliance-desc">PCU &amp; AXC F 2152 PLC</div>
                        </div>
                    </div>
                    <div class="hero-compliance-item">
                        <span class="hero-compliance-icon">🤖</span>
                        <div>
                            <div class="hero-compliance-title">KI-Validierung</div>
                            <div class="hero-compliance-desc">E.8 / E.9 &amp; SLD Audit</div>
                        </div>
                    </div>
                </div>
            </div>"""

assert old_left_html in content, "old_left_html not found"
content = content.replace(old_left_html, new_left_html)

# 3. Optimize .screen-top in controller card so it fits cleanly in 50% width
old_screentop = """                    <div class="screen-top">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span>⚡ EZA-Energiefluss &amp; Regelung</span>
                            <span style="color: var(--cyan-accent); font-size: 0.7rem; font-weight: 500;">(VDE-AR-N 4110)</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.55rem; flex-shrink: 0;">
                            <div style="display: flex; align-items: center; gap: 0.35rem;">
                                <label for="flowPlantSelect" style="font-size: 0.74rem; color: #94a3b8; font-weight: 600; white-space: nowrap;">Anlage:</label>
                                <select id="flowPlantSelect" onchange="onEnergyFlowPlantChange(this.value)" class="sim-mode-select" style="width: 210px; max-width: 210px; font-weight: 700; color: #38bdf8; background: #0c1a2c; border: 1.5px solid #0284c7; text-overflow: ellipsis; white-space: nowrap; overflow: hidden;" title="Erzeugungsanlage für Energiefluss und Regelung auswählen">
                                    <option value="ALL">🌐 Alle Standorte / Gesamtflotte</option>
                                </select>
                            </div>
                            <select id="flowSimSelect" onchange="setFlowSimulationMode(this.value)" class="sim-mode-select" style="width: 175px; max-width: 175px; text-overflow: ellipsis; white-space: nowrap; overflow: hidden;" title="Betriebs- und Simulationsmodus">
                                <option value="normal">☀️ Tagbetrieb (Volllast + BESS)</option>
                                <option value="peak">🔋 Spitzenlast (BESS Entladung)</option>
                                <option value="curtail">⚠️ Abregelung 50% (DSO)</option>
                                <option value="qu_boost">⚡ Q(U)-Spannungsstützung</option>
                            </select>
                            <span class="status" id="flowStatusBadge" style="white-space: nowrap; min-width: 105px; text-align: right;">● ONLINE · REGELT</span>
                        </div>
                    </div>"""

new_screentop = """                    <div class="screen-top">
                        <div style="display: flex; align-items: center; gap: 0.4rem; min-width: 0;">
                            <span style="font-weight: 800; font-size: 0.76rem; white-space: nowrap;">⚡ EZA-Energiefluss</span>
                            <span style="color: var(--cyan-accent); font-size: 0.68rem; font-weight: 600; white-space: nowrap;">(VDE 4110)</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.45rem; flex-shrink: 0;">
                            <div style="display: flex; align-items: center; gap: 0.25rem;">
                                <label for="flowPlantSelect" style="font-size: 0.72rem; color: #94a3b8; font-weight: 600; white-space: nowrap;">Anlage:</label>
                                <select id="flowPlantSelect" onchange="onEnergyFlowPlantChange(this.value)" class="sim-mode-select" style="width: 165px; max-width: 165px; font-weight: 700; color: #38bdf8; background: #0c1a2c; border: 1.5px solid #0284c7; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; padding: 2px 6px; font-size: 0.72rem;" title="Erzeugungsanlage für Energiefluss und Regelung auswählen">
                                    <option value="ALL">🌐 Alle / Flotte</option>
                                </select>
                            </div>
                            <select id="flowSimSelect" onchange="setFlowSimulationMode(this.value)" class="sim-mode-select" style="width: 145px; max-width: 145px; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; padding: 2px 6px; font-size: 0.72rem;" title="Betriebs- und Simulationsmodus">
                                <option value="normal">☀️ Tagbetrieb</option>
                                <option value="peak">🔋 Spitzenlast</option>
                                <option value="curtail">⚠️ Abregelung 50%</option>
                                <option value="qu_boost">⚡ Q(U)-Stützung</option>
                            </select>
                            <span class="status" id="flowStatusBadge" style="white-space: nowrap; font-size: 0.68rem; min-width: 95px; text-align: right;">● ONLINE · REGELT</span>
                        </div>
                    </div>"""

assert old_screentop in content, "old_screentop not found"
content = content.replace(old_screentop, new_screentop)

with open('backend/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully applied symmetrical hero layout changes.")
