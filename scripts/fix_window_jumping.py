import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FILE_PATH = 'backend/templates/index.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

print("Original length:", len(content))

# 1. Fix .hero-banner align-items: start (prevent cross-column vertical jumping)
old_hero_grid = """            display: grid;
            grid-template-columns: 0.85fr 1.15fr;
            gap: 2.2rem;
            align-items: center;
            color: #ffffff;"""

new_hero_grid = """            display: grid;
            grid-template-columns: 0.85fr 1.15fr;
            gap: 2.2rem;
            align-items: start;
            color: #ffffff;"""

assert old_hero_grid in content, "Could not find old_hero_grid"
content = content.replace(old_hero_grid, new_hero_grid, 1)
print("Updated .hero-banner align-items to 'start'!")

# 2. Fix .controller-screen and .screen-top styles to prevent height jumps
old_screen_css = """        .controller-screen {
            background: #06111c;
            border-radius: 14px;
            padding: 14px 16px;
            border: 1px solid rgba(37, 199, 201, 0.22);
        }

        .screen-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #aec2d3;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            flex-wrap: wrap;
            gap: 0.5rem;
        }"""

new_screen_css = """        .controller-screen {
            background: #06111c;
            border-radius: 14px;
            padding: 14px 16px;
            border: 1px solid rgba(37, 199, 201, 0.22);
            min-height: 485px;
        }

        .screen-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #aec2d3;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            flex-wrap: nowrap;
            gap: 0.6rem;
            min-height: 40px;
        }"""

assert old_screen_css in content, "Could not find old_screen_css"
content = content.replace(old_screen_css, new_screen_css, 1)
print("Updated .controller-screen and .screen-top CSS to prevent height shifts!")

# 3. Fix .screen-top inner HTML and dropdown widths
old_screen_top_html = """                        <div style="display: flex; align-items: center; gap: 0.65rem; flex-wrap: wrap;">
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

new_screen_top_html = """                        <div style="display: flex; align-items: center; gap: 0.55rem; flex-shrink: 0;">
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
                        </div>"""

assert old_screen_top_html in content, "Could not find old_screen_top_html"
content = content.replace(old_screen_top_html, new_screen_top_html, 1)
print("Updated .screen-top HTML with fixed dropdown widths!")

# 4. Fix selectPlantForEnergyFlow to remove intrusive scrollIntoView jumping
old_select_plant_js = """        function selectPlantForEnergyFlow(plantId) {
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
        }"""

new_select_plant_js = """        function selectPlantForEnergyFlow(plantId) {
            onEnergyFlowPlantChange(plantId);

            const card = document.querySelector(".controller-card");
            if (card) {
                // Only scroll if card is currently out of view, using gentle nearest block to prevent window jumping
                const rect = card.getBoundingClientRect();
                if (rect.top < 0 || rect.bottom > window.innerHeight) {
                    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
                }
                card.style.transition = "box-shadow 0.3s ease, border-color 0.3s ease";
                card.style.borderColor = "#25c7c9";
                card.style.boxShadow = "0 0 30px rgba(37, 199, 201, 0.45)";
                setTimeout(() => {
                    card.style.boxShadow = "";
                    card.style.borderColor = "";
                }, 1800);
            }
        }"""

assert old_select_plant_js in content, "Could not find old_select_plant_js"
content = content.replace(old_select_plant_js, new_select_plant_js, 1)
print("Updated selectPlantForEnergyFlow JS to eliminate window jumping!")

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("File updated successfully! New length:", len(content))
