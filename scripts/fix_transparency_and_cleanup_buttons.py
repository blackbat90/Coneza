"""
Script to:
1. Fix transparency in plantQuestionnaireModal and add CSS tokens (--surface, --form-input).
2. Remove unnecessary buttons (Jira, Confluence, and redundant quick-config buttons).
"""

html_path = "backend/templates/index.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add --surface, --text and .form-input to CSS
old_root = """            /* Semantic Theme Mappings */
            --bg-base: #fbfdff;
            --bg-surface: #ffffff;
            --bg-card: #ffffff;"""

new_root = """            /* Semantic Theme Mappings */
            --surface: #ffffff;
            --surface-card: #f8fafc;
            --text: #152235;
            --bg-base: #fbfdff;
            --bg-surface: #ffffff;
            --bg-card: #ffffff;"""

if old_root not in content:
    old_root = old_root.replace('\n', '\r\n')
    new_root = new_root.replace('\n', '\r\n')

assert old_root in content, "old_root not found"
content = content.replace(old_root, new_root, 1)

# Add .form-input to CSS
old_input = """.input-control {
            width: 100%;
            background: #ffffff;
            border: 1px solid var(--line);"""

new_input = """.form-input, .input-control {
            width: 100%;
            background: #ffffff;
            border: 1px solid var(--line);"""

if old_input not in content:
    old_input = old_input.replace('\n', '\r\n')
    new_input = new_input.replace('\n', '\r\n')

assert old_input in content, "old_input not found"
content = content.replace(old_input, new_input, 1)


# 2. Clean up Header: remove Confluence link, Jira link, and redundant 1-Klick Auto-Config button
old_header = """            <a href="https://easy-eza.atlassian.net/wiki/spaces/EEPD" target="_blank" rel="noopener" class="btn" style="background:#f0f7ff; border-color:#bae0ff; color:#0052cc; font-size:0.82rem; padding:0.45rem 0.85rem;" title="Confluence System-Dokumentation">
                📘 Confluence
            </a>
            <a href="https://easy-eza.atlassian.net/jira/your-work" target="_blank" rel="noopener" class="btn" style="background:#f0fdf4; border-color:#bbf7d0; color:#166534; font-size:0.82rem; padding:0.45rem 0.85rem;" title="Jira Board">
                🎯 Jira
            </a>
            <button class="btn" id="btnLoginHeaderBtn" onclick="openAuthModal('login')">
                🔐 Anmelden
            </button>
            <button class="btn" id="btn2faHeaderBtn" style="display: none;" onclick="open2faModal()">
                🔑 2FA
            </button>
            <button class="btn" id="btnChangePwHeaderBtn" style="display: none;" onclick="openVoluntaryChangePwModal()">
                🔒 Passwort ändern
            </button>
            <button class="btn" id="btnQuestionnaireHeader" style="display: none; background: linear-gradient(135deg, rgba(16, 185, 129, 0.18), rgba(6, 182, 212, 0.18)); border: 1.5px solid #10b981; color: #10b981; font-weight: 700;" onclick="openPlantQuestionnaireModal()">
                📋 Fragebogen (Kein SLD nötig)
            </button>
            <button class="btn" id="btnQuickConfigHeader" style="display: none; background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(59, 130, 246, 0.2)); border: 1px solid var(--cyan-accent); color: var(--cyan-accent); font-weight: 700;" onclick="openQuickConfigModal()">
                ⚡ 1-Klick Auto-Config (SLD + E.9/E.8)
            </button>"""

new_header = """            <button class="btn" id="btnLoginHeaderBtn" onclick="openAuthModal('login')">
                🔐 Anmelden
            </button>
            <button class="btn" id="btnQuestionnaireHeader" style="display: none; background: linear-gradient(135deg, rgba(16, 185, 129, 0.18), rgba(6, 182, 212, 0.18)); border: 1.5px solid #10b981; color: #10b981; font-weight: 700;" onclick="openPlantQuestionnaireModal()">
                📋 Fragebogen (Kein SLD nötig)
            </button>"""

if old_header not in content:
    old_header = old_header.replace('\n', '\r\n')
    new_header = new_header.replace('\n', '\r\n')

assert old_header in content, "old_header not found"
content = content.replace(old_header, new_header, 1)


# 3. Clean up Tab bar: remove jiraTabBtn
old_tab_bar = """            <button class="tab-btn" id="jiraTabBtn" onclick="switchTab('jiraTab', this); loadJiraTickets(); loadConfluenceDocs();">
                📋 Jira &amp; Confluence Docs (<span id="jiraTicketCount">4</span>)
            </button>"""

if old_tab_bar not in content:
    old_tab_bar = old_tab_bar.replace('\n', '\r\n')

if old_tab_bar in content:
    content = content.replace(old_tab_bar, "", 1)


# 4. Clean up Tab 1 Action bar: remove redundant Express-Konfiguration button
old_tab1_bar = """                    <button class="btn" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.15)); border: 1.5px solid #10b981; color: #10b981; font-weight: 700;" onclick="openPlantQuestionnaireModal()">📋 Fragebogen (Kein SLD nötig)</button>
                    <button class="btn" style="background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(59, 130, 246, 0.15)); border: 1px solid var(--cyan-accent); color: var(--cyan-accent); font-weight: 700;" onclick="openQuickConfigModal()">⚡ SLD + E.9/E.8 Express-Konfiguration</button>"""

new_tab1_bar = """                    <button class="btn" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.15)); border: 1.5px solid #10b981; color: #10b981; font-weight: 700;" onclick="openPlantQuestionnaireModal()">📋 Fragebogen (Kein SLD nötig)</button>"""

if old_tab1_bar not in content:
    old_tab1_bar = old_tab1_bar.replace('\n', '\r\n')
    new_tab1_bar = new_tab1_bar.replace('\n', '\r\n')

if old_tab1_bar in content:
    content = content.replace(old_tab1_bar, new_tab1_bar, 1)


# 5. Remove Confluence Ideas button in TAB-Vorkonfiguration box
old_conf_btn = """                            <button class="btn" onclick="openConfluenceIdeasModal()" style="font-size: 0.82rem;">
                                📚 Confluence-Wissen &amp; KI-Aufgaben
                            </button>"""

if old_conf_btn not in content:
    old_conf_btn = old_conf_btn.replace('\n', '\r\n')

if old_conf_btn in content:
    content = content.replace(old_conf_btn, "", 1)


# 6. Fix plantQuestionnaireModal solid styling (No transparency!)
old_modal_start = """    <div class="modal-backdrop" id="plantQuestionnaireModal" style="display: none; z-index: 1050;">
        <div class="modal" style="max-width: 1200px; width: 96vw; padding: 2.2rem; max-height: 94vh; overflow-y: auto; background: var(--surface); border: 1px solid var(--line); border-radius: 16px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);">"""

new_modal_start = """    <div class="modal-backdrop" id="plantQuestionnaireModal" style="display: none; z-index: 1050; background: rgba(11, 23, 40, 0.65); backdrop-filter: blur(8px);">
        <div class="modal" style="max-width: 1200px; width: 96vw; padding: 2.2rem; max-height: 94vh; overflow-y: auto; background: #ffffff !important; color: #152235 !important; border: 1px solid #cbd5e1; border-radius: 18px; box-shadow: 0 25px 60px rgba(0, 0, 0, 0.35);">"""

if old_modal_start not in content:
    old_modal_start = old_modal_start.replace('\n', '\r\n')
    new_modal_start = new_modal_start.replace('\n', '\r\n')

assert old_modal_start in content, "old_modal_start not found"
content = content.replace(old_modal_start, new_modal_start, 1)


# 7. Fix Presets bar in modal (solid light background)
old_presets_bar = """            <!-- Schnellvorlagen (Presets) Bar -->
            <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid var(--line); border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;">"""

new_presets_bar = """            <!-- Schnellvorlagen (Presets) Bar -->
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;">"""

if old_presets_bar not in content:
    old_presets_bar = old_presets_bar.replace('\n', '\r\n')
    new_presets_bar = new_presets_bar.replace('\n', '\r\n')

assert old_presets_bar in content, "old_presets_bar not found"
content = content.replace(old_presets_bar, new_presets_bar, 1)


# 8. Fix cards in questionnaire modal (replace background: var(--surface) with solid white and clean border)
# Step 1 card
old_card1 = """<!-- STEP 1: Netzanschluss (NAP) -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid var(--line); border-radius: 12px; background: var(--surface);">"""
new_card1 = """<!-- STEP 1: Netzanschluss (NAP) -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">"""

# Step 2 card
old_card2 = """<!-- STEP 2: Maschinentransformator (T1) -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid var(--line); border-radius: 12px; background: var(--surface);">"""
new_card2 = """<!-- STEP 2: Maschinentransformator (T1) -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">"""

# Step 3 card
old_card3 = """<!-- STEP 3: Erzeugungseinheiten (EZE) & Speicher -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid var(--line); border-radius: 12px; background: var(--surface);">"""
new_card3 = """<!-- STEP 3: Erzeugungseinheiten (EZE) & Speicher -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">"""

# Step 4 card
old_card4 = """<!-- STEP 4: Messung, Schutz & Regelung -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid var(--line); border-radius: 12px; background: var(--surface);">"""
new_card4 = """<!-- STEP 4: Messung, Schutz & Regelung -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">"""

# Right column SLD preview card
old_card_sld = """<!-- Live Vector SLD Preview Card -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid var(--line); border-radius: 12px; background: var(--surface);">"""
new_card_sld = """<!-- Live Vector SLD Preview Card -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">"""

for oc, nc in [(old_card1, new_card1), (old_card2, new_card2), (old_card3, new_card3), (old_card4, new_card4), (old_card_sld, new_card_sld)]:
    if oc not in content:
        oc = oc.replace('\n', '\r\n')
        nc = nc.replace('\n', '\r\n')
    assert oc in content, f"card not found: {oc[:40]}"
    content = content.replace(oc, nc, 1)


# 9. Fix Right column KPI metric tiles (replace dark rgba(15, 23, 42, 0.6) with solid crisp white)
old_metrics = """                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 0.75rem;">
                                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid var(--line); border-radius: 8px; padding: 0.75rem;">
                                    <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">Installierte Leistung P<sub>inst</sub></div>
                                    <div style="font-size: 1.3rem; font-weight: 800; color: #38bdf8; font-family: var(--font-mono);" id="questKpiPinst">0.0 kW</div>
                                    <div style="font-size: 0.72rem; color: var(--text-muted);" id="questKpiPinstMw">0.00 MWp</div>
                                </div>
                                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid var(--line); border-radius: 8px; padding: 0.75rem;">
                                    <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">Scheinleistung S<sub>inst</sub></div>
                                    <div style="font-size: 1.3rem; font-weight: 800; color: #818cf8; font-family: var(--font-mono);" id="questKpiSinst">0.0 kVA</div>
                                    <div style="font-size: 0.72rem; color: var(--text-muted);" id="questKpiSinstMva">0.00 MVA</div>
                                </div>
                            </div>

                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid var(--line); border-radius: 8px; padding: 0.75rem;">
                                    <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">BESS Speicherkapazität</div>
                                    <div style="font-size: 1.15rem; font-weight: 800; color: #34d399; font-family: var(--font-mono);" id="questKpiBess">0 kWh</div>
                                </div>
                                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid var(--line); border-radius: 8px; padding: 0.75rem;">
                                    <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">Trafo-Auslastung</div>
                                    <div style="font-size: 1.15rem; font-weight: 800; color: #f59e0b; font-family: var(--font-mono);" id="questKpiTrafoLoad">0.0 %</div>
                                </div>
                            </div>"""

new_metrics = """                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 0.75rem;">
                                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                                    <div style="font-size: 0.72rem; color: #64748b; text-transform: uppercase; font-weight: 600;">Installierte Leistung P<sub>inst</sub></div>
                                    <div style="font-size: 1.3rem; font-weight: 800; color: #0284c7; font-family: var(--font-mono);" id="questKpiPinst">0.0 kW</div>
                                    <div style="font-size: 0.72rem; color: #64748b;" id="questKpiPinstMw">0.00 MWp</div>
                                </div>
                                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                                    <div style="font-size: 0.72rem; color: #64748b; text-transform: uppercase; font-weight: 600;">Scheinleistung S<sub>inst</sub></div>
                                    <div style="font-size: 1.3rem; font-weight: 800; color: #6366f1; font-family: var(--font-mono);" id="questKpiSinst">0.0 kVA</div>
                                    <div style="font-size: 0.72rem; color: #64748b;" id="questKpiSinstMva">0.00 MVA</div>
                                </div>
                            </div>

                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                                    <div style="font-size: 0.72rem; color: #64748b; text-transform: uppercase; font-weight: 600;">BESS Speicherkapazität</div>
                                    <div style="font-size: 1.15rem; font-weight: 800; color: #059669; font-family: var(--font-mono);" id="questKpiBess">0 kWh</div>
                                </div>
                                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                                    <div style="font-size: 0.72rem; color: #64748b; text-transform: uppercase; font-weight: 600;">Trafo-Auslastung</div>
                                    <div style="font-size: 1.15rem; font-weight: 800; color: #d97706; font-family: var(--font-mono);" id="questKpiTrafoLoad">0.0 %</div>
                                </div>
                            </div>"""

if old_metrics not in content:
    old_metrics = old_metrics.replace('\n', '\r\n')
    new_metrics = new_metrics.replace('\n', '\r\n')

assert old_metrics in content, "old_metrics not found"
content = content.replace(old_metrics, new_metrics, 1)


# 10. Fix component card background in renderQuestionnaireComponents() in JS
old_comp_bg = """card.style.background = comp.type === 'BESS' ? 'rgba(16, 185, 129, 0.05)' : 'rgba(2, 132, 199, 0.05)';"""
new_comp_bg = """card.style.background = comp.type === 'BESS' ? '#f0fdf4' : '#f0f9ff';
                card.style.color = '#152235';"""

if old_comp_bg not in content:
    old_comp_bg = old_comp_bg.replace('\n', '\r\n')
    new_comp_bg = new_comp_bg.replace('\n', '\r\n')

if old_comp_bg in content:
    content = content.replace(old_comp_bg, new_comp_bg, 1)

# Write updated file
with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: Transparency fixed and unnecessary buttons removed.")
