import re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FILE_PATH = 'backend/templates/index.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

print("Read file, length:", len(content))

# 1. Add Wizard CSS styles before </style>
wizard_css = """
        /* ======================================================== */
        /* Multi-Step Wizard Component Styling                       */
        /* ======================================================== */
        .wizard-stepper {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1rem 1.25rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        }
        .wizard-step-node {
            position: relative;
            z-index: 3;
            display: flex;
            flex-direction: column;
            align-items: center;
            cursor: pointer;
            flex: 1;
            user-select: none;
            transition: all 0.2s ease;
        }
        .wizard-step-node:hover .wizard-node-circle:not(.active) {
            border-color: #0284c7;
            color: #0284c7;
            transform: scale(1.05);
        }
        .wizard-node-circle {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: #f8fafc;
            color: #64748b;
            font-weight: 700;
            font-size: 0.9rem;
            border: 2px solid #cbd5e1;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.25s ease;
        }
        .wizard-step-node.active .wizard-node-circle {
            background: #0284c7;
            color: #ffffff;
            border-color: #0284c7;
            box-shadow: 0 0 0 4px rgba(2, 132, 199, 0.25);
        }
        .wizard-step-node.completed .wizard-node-circle {
            background: #10b981;
            color: #ffffff;
            border-color: #10b981;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
        }
        .wizard-node-title {
            font-size: 0.82rem;
            font-weight: 600;
            color: #64748b;
            margin-top: 0.4rem;
            text-align: center;
            transition: color 0.2s ease;
        }
        .wizard-step-node.active .wizard-node-title {
            color: #0284c7;
            font-weight: 800;
        }
        .wizard-step-node.completed .wizard-node-title {
            color: #0f172a;
            font-weight: 700;
        }
        .wizard-node-sub {
            font-size: 0.7rem;
            color: #94a3b8;
            text-align: center;
        }
        .wizard-step-panel {
            animation: fadeInStep 0.25s ease-in-out;
        }
        @keyframes fadeInStep {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }
"""

if 'Multi-Step Wizard Component Styling' not in content:
    content = content.replace('    </style>', wizard_css + '\n    </style>', 1)
    print("Added Wizard CSS to <style>")
else:
    print("Wizard CSS already present in <style>")

# 2. Extract and replace the modal block
# Find start of plantQuestionnaireModal
modal_start_token = '<div class="modal-backdrop" id="plantQuestionnaireModal"'
modal_end_token = '<!-- Dedicated Fullscreen SLD Viewer & Zoom Modal'

start_idx = content.find(modal_start_token)
end_idx = content.find(modal_end_token)
assert start_idx != -1, "Could not find modal start"
assert end_idx != -1, "Could not find modal end"

# Let's inspect the exact lines between start_idx and end_idx
old_modal_html = content[start_idx:end_idx]
print(f"Old modal html length: {len(old_modal_html)}")

# Create the new Wizard HTML structure
new_modal_html = """<div class="modal-backdrop" id="plantQuestionnaireModal" style="display: none; z-index: 1050; background: rgba(11, 23, 40, 0.65); backdrop-filter: blur(8px);">
        <div class="modal" style="max-width: 1240px; width: 96vw; padding: 2.2rem; max-height: 94vh; overflow-y: auto; background: #ffffff !important; color: #152235 !important; border: 1px solid #cbd5e1; border-radius: 18px; box-shadow: 0 25px 60px rgba(0, 0, 0, 0.35);">
            <!-- Modal Header -->
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; border-bottom: 1px solid var(--line); padding-bottom: 1.2rem;">
                <div>
                    <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.25rem 0.75rem; border-radius: 9999px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); font-size: 0.76rem; font-weight: 700; color: #10b981; text-transform: uppercase; margin-bottom: 0.4rem;">
                        🧙‍♂️ Schritt-für-Schritt Anlagen-Wizard · VDE-AR-N 4110 / 4120
                    </div>
                    <h3 style="font-size: 1.55rem; font-weight: 800; letter-spacing: -0.02em; color: var(--navy); margin-bottom: 0.3rem;">
                        Anlagen-Konfigurations-Wizard
                    </h3>
                    <p style="color: var(--text-muted); font-size: 0.88rem; margin: 0; line-height: 1.5;">
                        Konfigurieren Sie Erzeugungs- und Speicheranlagen <strong>Schritt für Schritt ohne SLD</strong>. Wählen Sie marktübliche Standard-Komponenten oder Custom-Geräte mit Live-Vektorschaltplan und automatischer Phoenix Contact EZA-Reglerberechnung.
                    </p>
                </div>
                <button type="button" class="btn" style="padding: 0.35rem 0.75rem; font-size: 0.95rem; border-radius: 8px;" onclick="closePlantQuestionnaireModal()">✕</button>
            </div>

            <!-- Schnellvorlagen (Presets) Bar -->
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 1.25rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                    <span style="font-size: 0.82rem; font-weight: 700; color: var(--navy);">🚀 Muster-Vorlagen:</span>
                    <button type="button" class="btn btn-sm" style="font-size: 0.78rem; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); color: var(--cyan-accent); font-weight: 600;" onclick="loadQuestionnairePreset('preset_pv_1500kw')">
                        ☀️ 1.5 MW Solarpark (Huawei)
                    </button>
                    <button type="button" class="btn btn-sm" style="font-size: 0.78rem; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #10b981; font-weight: 600;" onclick="loadQuestionnairePreset('preset_hybrid_bess_2500kwh')">
                        🔋 2.5 MWh PV+BESS (SMA+BYD)
                    </button>
                    <button type="button" class="btn btn-sm" style="font-size: 0.78rem; background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.4); color: #a855f7; font-weight: 600;" onclick="loadQuestionnairePreset('preset_commercial_pv_400v')">
                        🏢 450 kW C&I Dach (SMA)
                    </button>
                </div>
                <button type="button" class="btn btn-sm" style="font-size: 0.76rem; color: var(--text-muted);" onclick="resetQuestionnaireForm()">
                    🔄 Formular leeren
                </button>
            </div>

            <!-- Wizard Stepper Navigation -->
            <div class="wizard-stepper">
                <div style="display: flex; align-items: center; justify-content: space-between; position: relative;">
                    <!-- Track line behind nodes -->
                    <div style="position: absolute; top: 19px; left: 8%; right: 8%; height: 3px; background: #e2e8f0; z-index: 1; border-radius: 2px;"></div>
                    <!-- Dynamic Progress Line -->
                    <div id="wizardProgressLine" style="position: absolute; top: 19px; left: 8%; width: 0%; height: 3px; background: linear-gradient(90deg, #0284c7, #10b981); z-index: 2; border-radius: 2px; transition: width 0.35s ease;"></div>

                    <!-- Step 1 Node -->
                    <div class="wizard-step-node active" id="wizardNode1" onclick="goToWizardStep(1)">
                        <div class="wizard-node-circle" id="wizardCircle1">1</div>
                        <div class="wizard-node-title" id="wizardTitle1">1. Netzanschluss</div>
                        <div class="wizard-node-sub">NAP &amp; Leistung</div>
                    </div>

                    <!-- Step 2 Node -->
                    <div class="wizard-step-node" id="wizardNode2" onclick="goToWizardStep(2)">
                        <div class="wizard-node-circle" id="wizardCircle2">2</div>
                        <div class="wizard-node-title" id="wizardTitle2">2. Transformator</div>
                        <div class="wizard-node-sub">T1 &amp; Nennwerte</div>
                    </div>

                    <!-- Step 3 Node -->
                    <div class="wizard-step-node" id="wizardNode3" onclick="goToWizardStep(3)">
                        <div class="wizard-node-circle" id="wizardCircle3">3</div>
                        <div class="wizard-node-title" id="wizardTitle3">3. Erzeugung (EZE)</div>
                        <div class="wizard-node-sub">PV, BESS, Wind, Diesel</div>
                    </div>

                    <!-- Step 4 Node -->
                    <div class="wizard-step-node" id="wizardNode4" onclick="goToWizardStep(4)">
                        <div class="wizard-node-circle" id="wizardCircle4">4</div>
                        <div class="wizard-node-title" id="wizardTitle4">4. Messung &amp; Schutz</div>
                        <div class="wizard-node-sub">Zähler, Relais &amp; VDE</div>
                    </div>

                    <!-- Step 5 Node -->
                    <div class="wizard-step-node" id="wizardNode5" onclick="goToWizardStep(5)">
                        <div class="wizard-node-circle" id="wizardCircle5">5</div>
                        <div class="wizard-node-title" id="wizardTitle5">5. Prüfung &amp; Abschluss</div>
                        <div class="wizard-node-sub">Übersicht &amp; PCU Gen</div>
                    </div>
                </div>
            </div>

            <!-- Error Banner -->
            <div id="questErrorBanner" style="display: none; padding: 0.85rem 1.1rem; border-radius: 8px; background: rgba(244, 63, 94, 0.15); border: 1px solid var(--rose); color: #be123c; font-size: 0.85rem; margin-bottom: 1.25rem;"></div>

            <!-- Main Questionnaire Form Grid -->
            <form id="plantQuestionnaireForm" onsubmit="handlePlantQuestionnaireSubmit(event)">
                <div style="display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 1.5rem; align-items: start;">
                    
                    <!-- LEFT COLUMN: Step Panels -->
                    <div style="display: flex; flex-direction: column; gap: 1.25rem;">

                        <!-- STEP 1 PANEL: Netzanschluss (NAP) -->
                        <div id="wizardStep1" class="wizard-step-panel">
                            <div class="card" style="padding: 1.4rem; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.1rem; padding-bottom: 0.75rem; border-bottom: 1px solid #f1f5f9;">
                                    <div style="display: flex; align-items: center; gap: 0.6rem;">
                                        <span style="display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: #0284c7; color: #fff; font-size: 0.8rem; font-weight: 700;">1</span>
                                        <div>
                                            <h4 style="font-size: 1.05rem; font-weight: 700; margin: 0; color: var(--navy);">Schritt 1: Netzanschluss &amp; Netzbetreiber (NAP)</h4>
                                            <div style="font-size: 0.74rem; color: var(--text-muted);">Grunddaten und vereinbarte Anschlusswirkleistung am Übergabepunkt</div>
                                        </div>
                                    </div>
                                    <span style="font-size: 0.74rem; font-weight: 700; color: #0284c7; background: rgba(2, 132, 199, 0.1); padding: 0.2rem 0.6rem; border-radius: 9999px;">Schritt 1 von 5</span>
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                                    <div style="grid-column: span 2;">
                                        <label style="font-size: 0.82rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.35rem;">Anlagenbezeichnung *</label>
                                        <input type="text" id="questPlantName" class="form-input" placeholder="z. B. Solarpark Musterpark 1.5 MWp" style="width: 100%; font-size: 0.95rem;" required oninput="triggerQuestionnairePreviewDebounced()">
                                    </div>
                                    <div>
                                        <label style="font-size: 0.82rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.35rem;">Netzbetreiber (VNB) *</label>
                                        <select id="questGridOperatorSelect" class="form-input" style="width: 100%;" onchange="onQuestVnbChange()">
                                            <option value="Netze BW GmbH (EnBW)">Netze BW GmbH (EnBW)</option>
                                            <option value="Bayernwerk Netz GmbH (E.ON)">Bayernwerk Netz GmbH (E.ON)</option>
                                            <option value="E.DIS Netz GmbH (E.ON)">E.DIS Netz GmbH (E.ON)</option>
                                            <option value="Westnetz GmbH (E.ON)">Westnetz GmbH (E.ON)</option>
                                            <option value="Avacon Netz GmbH (E.ON)">Avacon Netz GmbH (E.ON)</option>
                                            <option value="Mitteldeutsche Netzgesellschaft Strom mbH (MITNETZ STROM)">MITNETZ STROM</option>
                                            <option value="Syna GmbH (Süwag)">Syna GmbH (Süwag)</option>
                                            <option value="Stromnetz Berlin GmbH">Stromnetz Berlin GmbH</option>
                                            <option value="TenneT TSO GmbH (Übertragungsnetz)">TenneT TSO GmbH</option>
                                            <option value="__custom__">➕ Anderer Netzbetreiber (Freitext)...</option>
                                        </select>
                                        <input type="text" id="questGridOperatorCustom" class="form-input" placeholder="Netzbetreiber Name eingeben" style="width: 100%; margin-top: 0.4rem; display: none;" oninput="triggerQuestionnairePreviewDebounced()">
                                    </div>
                                    <div>
                                        <label style="font-size: 0.82rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.35rem;">Netzspannungsebene (NAP) *</label>
                                        <select id="questVoltageSelect" class="form-input" style="width: 100%;" onchange="onQuestVoltageChange()">
                                            <option value="20.0" selected>20 kV (Mittelspannung - Standard)</option>
                                            <option value="10.0">10 kV (Mittelspannung)</option>
                                            <option value="30.0">30 kV (Mittelspannung)</option>
                                            <option value="0.4">0.4 kV (400 V Niederspannung)</option>
                                            <option value="__custom__">Custom Spannungsebene...</option>
                                        </select>
                                        <div id="questVoltageCustomWrap" style="display: none; margin-top: 0.4rem;">
                                            <input type="number" id="questVoltageCustom" class="form-input" placeholder="Spannung in kV (z.B. 15)" step="0.1" style="width: 100%;" oninput="triggerQuestionnairePreviewDebounced()">
                                        </div>
                                    </div>
                                    <div style="grid-column: span 2;">
                                        <label style="font-size: 0.82rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.35rem;">Vereinbarte Anschlusswirkleistung P<sub>AV</sub> (kW) *</label>
                                        <div style="display: flex; gap: 0.5rem; align-items: center;">
                                            <input type="number" id="questPavKw" class="form-input" value="1500" min="1" step="10" style="width: 180px; font-weight: 700; font-family: var(--font-mono);" required oninput="triggerQuestionnairePreviewDebounced()">
                                            <span style="font-size: 0.85rem; color: var(--text-muted);">kW (<span id="questPavMwDisplay" style="font-weight: 700; color: #0284c7;">1.50 MW</span> Einspeiselimit am Übergabepunkt)</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- STEP 2 PANEL: Maschinentransformator (T1) -->
                        <div id="wizardStep2" class="wizard-step-panel" style="display: none;">
                            <div class="card" style="padding: 1.4rem; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.1rem; padding-bottom: 0.75rem; border-bottom: 1px solid #f1f5f9;">
                                    <div style="display: flex; align-items: center; gap: 0.6rem;">
                                        <span style="display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: #7c3aed; color: #fff; font-size: 0.8rem; font-weight: 700;">2</span>
                                        <div>
                                            <h4 style="font-size: 1.05rem; font-weight: 700; margin: 0; color: var(--navy);">Schritt 2: Maschinentransformator (T1)</h4>
                                            <div style="font-size: 0.74rem; color: var(--text-muted);">Mittelspannungs-Transformator oder direkte Niederspannungseinspeisung</div>
                                        </div>
                                    </div>
                                    <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer; font-size: 0.84rem; font-weight: 700; color: #7c3aed; background: rgba(124, 58, 237, 0.08); padding: 0.3rem 0.75rem; border-radius: 8px;">
                                        <input type="checkbox" id="questHasTrafo" checked onchange="onQuestTrafoToggle()">
                                        Transformator vorhanden
                                    </label>
                                </div>
                                
                                <div id="questTrafoFieldsWrap">
                                    <div style="margin-bottom: 0.85rem;">
                                        <label style="font-size: 0.82rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.35rem;">Marktüblicher Transformator (T1) *</label>
                                        <select id="questTrafoSelect" class="form-input" style="width: 100%;" onchange="onQuestTrafoSelectChange()">
                                            <!-- Populated via loadQuestionnaireCatalog() -->
                                        </select>
                                    </div>
                                    <div id="questTrafoCustomFields" style="display: none; grid-template-columns: 1fr 1fr 1fr; gap: 0.75rem; margin-top: 0.85rem; background: rgba(124, 58, 237, 0.05); padding: 0.95rem; border-radius: 8px; border: 1px dashed rgba(124, 58, 237, 0.3);">
                                        <div>
                                            <label style="font-size: 0.75rem; color: var(--text-muted); display: block; margin-bottom: 0.25rem;">Nennscheinleistung S<sub>rT</sub> (kVA)</label>
                                            <input type="number" id="questTrafoCustomKva" class="form-input" value="1600" step="50" style="width: 100%; font-family: var(--font-mono);" oninput="triggerQuestionnairePreviewDebounced()">
                                        </div>
                                        <div>
                                            <label style="font-size: 0.75rem; color: var(--text-muted); display: block; margin-bottom: 0.25rem;">Kurzschlussspannung u<sub>k</sub> (%)</label>
                                            <input type="number" id="questTrafoCustomUk" class="form-input" value="6.0" step="0.1" style="width: 100%; font-family: var(--font-mono);" oninput="triggerQuestionnairePreviewDebounced()">
                                        </div>
                                        <div>
                                            <label style="font-size: 0.75rem; color: var(--text-muted); display: block; margin-bottom: 0.25rem;">Schaltgruppe</label>
                                            <input type="text" id="questTrafoCustomGroup" class="form-input" value="Dyn5" style="width: 100%; font-family: var(--font-mono);" oninput="triggerQuestionnairePreviewDebounced()">
                                        </div>
                                    </div>
                                </div>
                                <div id="questNoTrafoNote" style="display: none; padding: 0.85rem; background: rgba(148, 163, 184, 0.1); border-radius: 8px; font-size: 0.84rem; color: var(--text-muted); line-height: 1.45;">
                                    ℹ️ <b>Kein Transformator gewählt:</b> Erzeugungseinheiten speisen direkt in die 400 V Niederspannungsebene ein.
                                </div>
                            </div>
                        </div>

                        <!-- STEP 3 PANEL: Erzeugungseinheiten (EZE), Speicher & Teilnehmermessung -->
                        <div id="wizardStep3" class="wizard-step-panel" style="display: none;">
                            <div class="card" style="padding: 1.4rem; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 1px solid #f1f5f9; flex-wrap: wrap; gap: 0.6rem;">
                                    <div style="display: flex; align-items: center; gap: 0.6rem;">
                                        <span style="display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: #10b981; color: #fff; font-size: 0.8rem; font-weight: 700;">3</span>
                                        <div>
                                            <h4 style="font-size: 1.05rem; font-weight: 700; margin: 0; color: var(--navy);">Schritt 3: Erzeugungseinheiten (EZE) &amp; Teilnehmermessung</h4>
                                            <div style="font-size: 0.74rem; color: #10b981; font-weight: 600;">VDE-AR-N 4110 / 4120 konform für gemischte Erzeugung &amp; Unterzähler</div>
                                        </div>
                                    </div>
                                    <div style="display: flex; gap: 0.35rem; align-items: center; flex-wrap: wrap;">
                                        <button type="button" class="btn btn-sm btn-primary" style="font-size: 0.76rem; background: linear-gradient(135deg, #0284c7, #0ea5e9); border: none;" onclick="addQuestionnaireComponent('PV_INVERTER')">
                                            + ☀️ PV
                                        </button>
                                        <button type="button" class="btn btn-sm" style="font-size: 0.76rem; background: #ecfdf5; color: #047857; border: 1px solid #10b981; font-weight: 700;" onclick="addQuestionnaireComponent('BESS')">
                                            + 🔋 BESS
                                        </button>
                                        <button type="button" class="btn btn-sm" style="font-size: 0.76rem; background: #ecfeff; color: #0e7490; border: 1px solid #06b6d4; font-weight: 700;" onclick="addQuestionnaireComponent('WIND_TURBINE')">
                                            + 🌀 Wind
                                        </button>
                                        <button type="button" class="btn btn-sm" style="font-size: 0.76rem; background: #fffbeb; color: #b45309; border: 1px solid #f59e0b; font-weight: 700;" onclick="addQuestionnaireComponent('DIESEL_GEN')">
                                            + ⛽ Diesel/BHKW
                                        </button>
                                        <button type="button" class="btn btn-sm" style="font-size: 0.76rem; background: #f5f3ff; color: #6d28d9; border: 1px solid #8b5cf6; font-weight: 700;" onclick="addQuestionnaireComponent('CUSTOM_EZE')">
                                            + ⚡ EZE
                                        </button>
                                    </div>
                                </div>

                                <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.95rem; line-height: 1.45;">
                                    Definieren Sie alle Erzeugungseinheiten am Standort. Jeder Teilnehmer kann optional mit einer <b>eigenen Erzeugungsmessung (Unterzähler am Abgang)</b> zusätzlich zum NAP-Zähler ausgestattet werden.
                                </p>

                                <!-- Dynamic List of Components -->
                                <div id="questComponentsContainer" style="display: flex; flex-direction: column; gap: 0.85rem;">
                                    <!-- Populated dynamically by renderQuestionnaireComponents() -->
                                </div>
                            </div>
                        </div>

                        <!-- STEP 4 PANEL: Messung, Schutz & Regelung -->
                        <div id="wizardStep4" class="wizard-step-panel" style="display: none;">
                            <div class="card" style="padding: 1.4rem; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.1rem; padding-bottom: 0.75rem; border-bottom: 1px solid #f1f5f9;">
                                    <div style="display: flex; align-items: center; gap: 0.6rem;">
                                        <span style="display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: #f59e0b; color: #fff; font-size: 0.8rem; font-weight: 700;">4</span>
                                        <div>
                                            <h4 style="font-size: 1.05rem; font-weight: 700; margin: 0; color: var(--navy);">Schritt 4: Messung, Schutz &amp; VDE-Regelverfahren</h4>
                                            <div style="font-size: 0.74rem; color: var(--text-muted);">NAP Übergabezähler, Schutzrelais und Blindleistungskennlinie</div>
                                        </div>
                                    </div>
                                    <span style="font-size: 0.74rem; font-weight: 700; color: #f59e0b; background: rgba(245, 158, 11, 0.1); padding: 0.2rem 0.6rem; border-radius: 9999px;">Schritt 4 von 5</span>
                                </div>

                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                                    <div>
                                        <label style="font-size: 0.82rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.35rem;">Zähler am Übergabepunkt (NAP) *</label>
                                        <select id="questMeterSelect" class="form-input" style="width: 100%;" onchange="onQuestMeterSelectChange()">
                                            <!-- Populated via catalog -->
                                        </select>
                                    </div>
                                    <div>
                                        <label style="font-size: 0.82rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.35rem;">Netz- &amp; Anlagenschutz (Schutzrelais) *</label>
                                        <select id="questProtSelect" class="form-input" style="width: 100%;" onchange="onQuestProtSelectChange()">
                                            <!-- Populated via catalog -->
                                        </select>
                                    </div>
                                    <div>
                                        <label style="font-size: 0.82rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.35rem;">VDE Blindleistungsverfahren *</label>
                                        <select id="questReactiveMode" class="form-input" style="width: 100%;" onchange="triggerQuestionnairePreviewDebounced()">
                                            <option value="QU" selected>Q(U) - Spannungsabhängig (Standard Mittelspannung)</option>
                                            <option value="COS_PHI">cos φ(P) - Wirkleistungsabhängige Kennlinie</option>
                                            <option value="FIXED_COS_PHI">cos φ fest (z. B. 0.95 übererregt / untererregt)</option>
                                            <option value="FIXED_Q">Fester Blindleistungssollwert Q (kvar)</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label style="font-size: 0.82rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.35rem;">Zuweisung EZA-Regler (PCU)</label>
                                        <select id="questTargetDeviceSelect" class="form-input" style="width: 100%;">
                                            <option value="coneza-phoenix-axcf2152">Phoenix Contact AXC F 2152 (Coneza Standard EZA)</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- STEP 5 PANEL: Prüfung, Vorab-Check & Abschluss -->
                        <div id="wizardStep5" class="wizard-step-panel" style="display: none;">
                            <div class="card" style="padding: 1.4rem; border: 1.5px solid #10b981; border-radius: 12px; background: #ffffff; box-shadow: 0 4px 14px rgba(16,185,129,0.08);">
                                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.1rem; padding-bottom: 0.75rem; border-bottom: 1px solid #ecfdf5;">
                                    <div style="display: flex; align-items: center; gap: 0.6rem;">
                                        <span style="display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 50%; background: #10b981; color: #fff; font-size: 0.85rem; font-weight: 700;">✓</span>
                                        <div>
                                            <h4 style="font-size: 1.1rem; font-weight: 800; margin: 0; color: var(--navy);">Schritt 5: Anlagenübersicht &amp; Vorab-Validierung</h4>
                                            <div style="font-size: 0.75rem; color: #059669; font-weight: 600;">Alle Parameter geprüft · Bereit zur PCU-Reglersynthese</div>
                                        </div>
                                    </div>
                                    <span style="font-size: 0.74rem; font-weight: 700; color: #10b981; background: rgba(16, 185, 129, 0.12); padding: 0.25rem 0.65rem; border-radius: 9999px;">Abschlussprüfung</span>
                                </div>

                                <!-- Dynamic Summary Content -->
                                <div id="wizardSummaryContent" style="display: flex; flex-direction: column; gap: 0.85rem; margin-bottom: 1.1rem;">
                                    <!-- Populated via updateWizardSummary() -->
                                </div>

                                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 0.85rem 1.1rem; display: flex; align-items: center; gap: 0.75rem;">
                                    <span style="font-size: 1.4rem;">⚡</span>
                                    <div style="font-size: 0.82rem; color: #065f46; line-height: 1.45;">
                                        <b>VDE-AR-N 4110 / 4120 Synthese:</b> Nach Klick auf <i>"Anlage erstellen &amp; VDE 4110 PCU generieren"</i> wird die Anlage in der Coneza Plattform registriert, alle Modbus-Registertabellen berechnet und die Reglerkonfiguration für den Phoenix Contact AXC F 2152 erzeugt.
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>

                    <!-- RIGHT COLUMN: Realtime Live Calculation & Vector SLD Preview -->
                    <div style="position: sticky; top: 1rem; display: flex; flex-direction: column; gap: 1.25rem;">
                        
                        <!-- Realtime Calculated Metrics -->
                        <div class="card" style="padding: 1.25rem; border: 1.5px solid rgba(16, 185, 129, 0.35); border-radius: 12px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(2, 132, 199, 0.05));">
                            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #10b981; margin-bottom: 0.75rem; letter-spacing: 0.04em;">
                                📊 Berechnete Anlagenparameter
                            </div>

                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 0.75rem;">
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
                            </div>

                            <!-- Trafo loading bar -->
                            <div style="margin-top: 0.85rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: var(--text-muted); margin-bottom: 0.25rem;">
                                    <span>Trafo Dimensionierung:</span>
                                    <span id="questTrafoStatusText">Optimal</span>
                                </div>
                                <div style="width: 100%; height: 6px; background: rgba(148, 163, 184, 0.2); border-radius: 3px; overflow: hidden;">
                                    <div id="questTrafoBar" style="width: 80%; height: 100%; background: #10b981; transition: width 0.3s, background 0.3s;"></div>
                                </div>
                            </div>
                        </div>

                        <!-- Live Vector SLD Preview Card -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    <span style="font-size: 0.95rem;">⚡</span>
                                    <strong style="font-size: 0.9rem; color: var(--navy);">Digitales Single Line Diagramm (SLD)</strong>
                                    <span style="font-size: 0.74rem; color: #10b981; font-weight: 600;">✓ Live</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 0.4rem;">
                                    <button type="button" class="btn btn-sm btn-primary" onclick="openSldFullscreenModal()" style="font-size: 0.78rem; font-weight: 700; padding: 0.3rem 0.8rem; background: linear-gradient(135deg, #0284c7, #0ea5e9); border: none; box-shadow: 0 2px 6px rgba(2,132,199,0.35); display: inline-flex; align-items: center; gap: 0.35rem; cursor: pointer;" title="In maximaler Auflösung und Vollbild mit stufenlosem Zoom öffnen">
                                        🔍 Großansicht &amp; Zoom
                                    </button>
                                    <button type="button" class="btn btn-sm" onclick="downloadCurrentSldSvg()" style="font-size: 0.75rem; padding: 0.3rem 0.55rem;" title="SLD als Vektor-SVG herunterladen">
                                        💾 SVG
                                    </button>
                                </div>
                            </div>

                            <p style="font-size: 0.78rem; color: var(--text-muted); margin: 0 0 0.75rem 0;">
                                VDE-konformes Vektordiagramm. Klicken Sie auf die Vorschau oder auf <b>Großansicht</b>, um das Diagramm bildschirmfüllend zu vergrößern und stufenlos zu zoomen.
                            </p>

                            <!-- SVG Preview Container with Click-to-Enlarge -->
                            <div id="questSldSvgContainer" onclick="openSldFullscreenModal()" style="width: 100%; height: 420px; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; overflow: hidden; display: flex; align-items: center; justify-content: center; position: relative; cursor: pointer; transition: all 0.2s ease;" title="Klicken für Großansicht &amp; interaktiven Zoom" onmouseover="this.style.borderColor='#0284c7'; this.style.boxShadow='0 0 14px rgba(2,132,199,0.22)';" onmouseout="this.style.borderColor='#cbd5e1'; this.style.boxShadow='none';">
                                <div style="font-size: 0.82rem; color: #94a3b8; text-align: center; padding: 2rem;">
                                    ⏳ Generiere SLD-Vorschau...
                                </div>
                                <div style="position: absolute; bottom: 10px; right: 10px; background: rgba(15, 23, 42, 0.82); color: #ffffff; padding: 4px 10px; border-radius: 6px; font-size: 0.72rem; font-weight: 600; display: flex; align-items: center; gap: 4px; pointer-events: none; backdrop-filter: blur(4px); box-shadow: 0 2px 6px rgba(0,0,0,0.2);">
                                    🔍 Klicken für Großansicht
                                </div>
                            </div>
                        </div>

                    </div>

                </div>

                <!-- Action Bar with Wizard Step Controls -->
                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--line); padding-top: 1.25rem; margin-top: 1.5rem; flex-wrap: wrap; gap: 1rem;">
                    <div>
                        <button type="button" class="btn" onclick="closePlantQuestionnaireModal()" style="color: var(--text-muted);">
                            ✕ Abbrechen
                        </button>
                    </div>
                    <div style="display: flex; gap: 0.75rem; align-items: center;">
                        <span id="wizardStepCounter" style="font-size: 0.84rem; font-weight: 700; color: var(--navy); margin-right: 0.35rem;">
                            Schritt 1 von 5
                        </span>
                        <button type="button" class="btn" id="btnWizardPrev" onclick="wizardPrevStep()" style="display: none; padding: 0.65rem 1.25rem; font-weight: 600; border: 1px solid #cbd5e1; background: #ffffff;">
                            ← Zurück
                        </button>
                        <button type="button" class="btn btn-primary" id="btnWizardNext" onclick="wizardNextStep()" style="padding: 0.65rem 1.45rem; font-weight: 700; background: linear-gradient(135deg, #0284c7, #0ea5e9); border: none; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);">
                            Weiter: Transformator (T1) →
                        </button>
                        <button type="submit" class="btn btn-primary" id="btnSubmitQuestionnaire" style="display: none; background: linear-gradient(135deg, #10b981, #0284c7); border: none; font-weight: 700; padding: 0.75rem 1.6rem; font-size: 0.95rem; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);">
                            🚀 Anlage erstellen &amp; VDE 4110 PCU generieren
                        </button>
                    </div>
                </div>
            </form>
        </div>
    </div>\n\n"""

content = content[:start_idx] + new_modal_html + content[end_idx:]
print("Replaced modal HTML successfully!")

# 3. Add Wizard JavaScript Logic
wizard_js = """
        // ========================================================================= //
        // Wizard State & Step Management Logic                                      //
        // ========================================================================= //
        let currentWizardStep = 1;
        const TOTAL_WIZARD_STEPS = 5;

        function updateWizardStepperUI() {
            for (let i = 1; i <= TOTAL_WIZARD_STEPS; i++) {
                const node = document.getElementById(`wizardNode${i}`);
                const circle = document.getElementById(`wizardCircle${i}`);
                const title = document.getElementById(`wizardTitle${i}`);
                const panel = document.getElementById(`wizardStep${i}`);

                if (panel) {
                    panel.style.display = (i === currentWizardStep) ? "block" : "none";
                }

                if (node && circle && title) {
                    node.classList.remove("active", "completed");
                    if (i === currentWizardStep) {
                        node.classList.add("active");
                        circle.style.background = "#0284c7";
                        circle.style.color = "#ffffff";
                        circle.style.borderColor = "#0284c7";
                        circle.style.boxShadow = "0 0 0 4px rgba(2, 132, 199, 0.25)";
                        circle.innerHTML = `${i}`;
                        title.style.color = "#0284c7";
                        title.style.fontWeight = "800";
                    } else if (i < currentWizardStep) {
                        node.classList.add("completed");
                        circle.style.background = "#10b981";
                        circle.style.color = "#ffffff";
                        circle.style.borderColor = "#10b981";
                        circle.style.boxShadow = "0 0 0 3px rgba(16, 185, 129, 0.2)";
                        circle.innerHTML = "✓";
                        title.style.color = "#0f172a";
                        title.style.fontWeight = "700";
                    } else {
                        circle.style.background = "#f8fafc";
                        circle.style.color = "#64748b";
                        circle.style.borderColor = "#cbd5e1";
                        circle.style.boxShadow = "none";
                        circle.innerHTML = `${i}`;
                        title.style.color = "#64748b";
                        title.style.fontWeight = "600";
                    }
                }
            }

            // Progress line width
            const progressLine = document.getElementById("wizardProgressLine");
            if (progressLine) {
                const percent = ((currentWizardStep - 1) / (TOTAL_WIZARD_STEPS - 1)) * 84;
                progressLine.style.width = `${percent}%`;
            }

            // Bottom Buttons
            const btnPrev = document.getElementById("btnWizardPrev");
            const btnNext = document.getElementById("btnWizardNext");
            const btnSubmit = document.getElementById("btnSubmitQuestionnaire");
            const counter = document.getElementById("wizardStepCounter");

            if (counter) counter.innerText = `Schritt ${currentWizardStep} von ${TOTAL_WIZARD_STEPS}`;

            if (btnPrev) {
                btnPrev.style.display = (currentWizardStep > 1) ? "inline-flex" : "none";
            }

            if (btnNext) {
                if (currentWizardStep < TOTAL_WIZARD_STEPS) {
                    btnNext.style.display = "inline-flex";
                    const nextLabels = [
                        "",
                        "Weiter: Transformator (T1) →",
                        "Weiter: Erzeuger & Speicher (EZE) →",
                        "Weiter: Messung & Schutz →",
                        "Weiter: Prüfung & Zusammenfassung →"
                    ];
                    btnNext.innerText = nextLabels[currentWizardStep] || "Weiter →";
                } else {
                    btnNext.style.display = "none";
                }
            }

            if (btnSubmit) {
                btnSubmit.style.display = (currentWizardStep === TOTAL_WIZARD_STEPS) ? "inline-flex" : "none";
            }

            // Populate Step 5 Summary
            if (currentWizardStep === TOTAL_WIZARD_STEPS) {
                updateWizardSummary();
            }
        }

        function validateWizardStep(step) {
            const errBanner = document.getElementById("questErrorBanner");
            if (errBanner) errBanner.style.display = "none";

            if (step === 1) {
                const nameInput = document.getElementById("questPlantName");
                const plantName = nameInput ? nameInput.value.trim() : "";
                if (!plantName) {
                    if (errBanner) {
                        errBanner.innerText = "Bitte geben Sie eine Anlagenbezeichnung ein (z. B. Solarpark Musterpark).";
                        errBanner.style.display = "block";
                    }
                    if (nameInput) nameInput.focus();
                    return false;
                }
                const pavInput = document.getElementById("questPavKw");
                const pav = parseFloat(pavInput ? pavInput.value : 0);
                if (!pav || pav <= 0) {
                    if (errBanner) {
                        errBanner.innerText = "Bitte geben Sie eine gültige Anschlusswirkleistung P_AV in kW ein.";
                        errBanner.style.display = "block";
                    }
                    if (pavInput) pavInput.focus();
                    return false;
                }
            } else if (step === 2) {
                const hasTrafo = document.getElementById("questHasTrafo")?.checked;
                if (hasTrafo) {
                    const trafoSel = document.getElementById("questTrafoSelect")?.value;
                    if (trafoSel === "__custom__") {
                        const kva = parseFloat(document.getElementById("questTrafoCustomKva")?.value || 0);
                        if (kva <= 0) {
                            if (errBanner) {
                                errBanner.innerText = "Bitte geben Sie eine gültige Nennscheinleistung S_rT für den Custom-Trafo ein.";
                                errBanner.style.display = "block";
                            }
                            return false;
                        }
                    }
                }
            } else if (step === 3) {
                if (!questComponents || questComponents.length === 0) {
                    if (errBanner) {
                        errBanner.innerText = "Bitte fügen Sie mindestens eine Erzeugungseinheit (PV, BESS, Wind oder Generator) hinzu.";
                        errBanner.style.display = "block";
                    }
                    return false;
                }
            }
            return true;
        }

        function goToWizardStep(stepNumber) {
            if (stepNumber < 1 || stepNumber > TOTAL_WIZARD_STEPS) return;
            
            // If advancing forward, validate current step
            if (stepNumber > currentWizardStep) {
                if (!validateWizardStep(currentWizardStep)) {
                    return;
                }
            }

            currentWizardStep = stepNumber;
            updateWizardStepperUI();
            triggerQuestionnairePreviewDebounced();

            const modalContent = document.querySelector("#plantQuestionnaireModal .modal");
            if (modalContent) modalContent.scrollTop = 0;
        }

        function wizardNextStep() {
            if (!validateWizardStep(currentWizardStep)) return;
            if (currentWizardStep < TOTAL_WIZARD_STEPS) {
                currentWizardStep++;
                updateWizardStepperUI();
                triggerQuestionnairePreviewDebounced();
                const modalContent = document.querySelector("#plantQuestionnaireModal .modal");
                if (modalContent) modalContent.scrollTop = 0;
            }
        }

        function wizardPrevStep() {
            if (currentWizardStep > 1) {
                currentWizardStep--;
                updateWizardStepperUI();
                triggerQuestionnairePreviewDebounced();
                const modalContent = document.querySelector("#plantQuestionnaireModal .modal");
                if (modalContent) modalContent.scrollTop = 0;
            }
        }

        function updateWizardSummary() {
            const container = document.getElementById("wizardSummaryContent");
            if (!container) return;

            const plantName = document.getElementById("questPlantName").value.trim() || "Unbenannte Anlage";
            const vnbSel = document.getElementById("questGridOperatorSelect").value;
            const vnb = vnbSel === "__custom__" ? (document.getElementById("questGridOperatorCustom").value.trim() || "Anderer VNB") : vnbSel;
            const voltSel = document.getElementById("questVoltageSelect").value;
            const voltKv = voltSel === "__custom__" ? (document.getElementById("questVoltageCustom").value || "20.0") : voltSel;
            const pavKw = parseFloat(document.getElementById("questPavKw").value) || 0;
            
            const hasTrafo = document.getElementById("questHasTrafo").checked;
            let trafoText = "Direktspeisung Niederspannung (Kein Trafo)";
            if (hasTrafo) {
                const trafoSel = document.getElementById("questTrafoSelect").value;
                if (trafoSel === "__custom__") {
                    const kva = document.getElementById("questTrafoCustomKva").value || 1600;
                    const uk = document.getElementById("questTrafoCustomUk").value || 6.0;
                    const grp = document.getElementById("questTrafoCustomGroup").value || "Dyn5";
                    trafoText = `Custom Trafo ${kva} kVA (uk ${uk}%, ${grp})`;
                } else {
                    const foundTrafo = (questCatalog?.transformers || []).find(t => t.id === trafoSel);
                    trafoText = foundTrafo ? `${foundTrafo.brand} ${foundTrafo.model} (${foundTrafo.rated_kva} kVA, ${foundTrafo.vector_group})` : trafoSel;
                }
            }

            const meterSel = document.getElementById("questMeterSelect")?.value;
            const foundMeter = (questCatalog?.meters || []).find(m => m.id === meterSel);
            const meterText = foundMeter ? `${foundMeter.brand} ${foundMeter.model}` : (meterSel || "Janitza UMG 604E");

            const protSel = document.getElementById("questProtSelect")?.value;
            const foundProt = (questCatalog?.protection_relays || []).find(p => p.id === protSel);
            const protText = foundProt ? `${foundProt.brand} ${foundProt.model}` : (protSel || "Woodward HighProTec MRM4");

            const reactiveMode = document.getElementById("questReactiveMode")?.value || "QU";
            const reactiveText = {
                "QU": "Q(U) - Spannungsabhängig",
                "COS_PHI": "cos φ(P) - Wirkleistungsabhängig",
                "FIXED_COS_PHI": "cos φ fest",
                "FIXED_Q": "Fester Blindleistungssollwert Q"
            }[reactiveMode] || reactiveMode;

            const pInstKw = questComponents.reduce((acc, c) => acc + (c.unit_active_kw * c.count), 0);
            const sInstKva = questComponents.reduce((acc, c) => acc + (c.unit_apparent_kva * c.count), 0);
            const totalBessKwh = questComponents.filter(c => c.type === 'BESS').reduce((acc, c) => acc + (c.capacity_kwh * c.count), 0);

            let compSummaryHtml = "";
            if (questComponents.length === 0) {
                compSummaryHtml = '<div style="color:#f43f5e; font-size:0.82rem;">Keine Komponenten konfiguriert!</div>';
            } else {
                compSummaryHtml = questComponents.map((c, i) => {
                    const typeLabels = {
                        'PV_INVERTER': '☀️ PV-Wechselrichter',
                        'BESS': '🔋 Batteriespeicher (BESS)',
                        'WIND_TURBINE': '🌀 Windkraftanlage',
                        'DIESEL_GEN': '⛽ Dieselaggregat / BHKW',
                        'CUSTOM_EZE': '⚡ Erzeugungseinheit (Custom)'
                    };
                    const label = typeLabels[c.type] || c.type;
                    const subMeterText = c.has_sub_meter ? ` · <span style="color:#047857; font-weight:700;">✓ Unterzähler (${c.sub_meter_model || 'Messung'})</span>` : '';
                    return `
                        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:0.6rem 0.85rem; font-size:0.82rem; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <b>${label}</b>: ${c.count}x ${c.brand || ''} ${c.model || ''}
                                <div style="font-size:0.74rem; color:#64748b;">${c.unit_active_kw} kW / ${(c.unit_apparent_kva || c.unit_active_kw*1.05).toFixed(1)} kVA pro Einheit${subMeterText}</div>
                            </div>
                            <div style="font-weight:700; color:#0284c7; font-family:var(--font-mono);">
                                ${(c.unit_active_kw * c.count).toFixed(0)} kW gesamt
                            </div>
                        </div>
                    `;
                }).join('');
            }

            container.innerHTML = `
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem 1rem;">
                        <div style="font-size: 0.72rem; color: #64748b; font-weight: 600; text-transform: uppercase;">1. Netzanschluss (NAP)</div>
                        <div style="font-size: 0.95rem; font-weight: 700; color: var(--navy); margin-top: 0.2rem;">${escapeHtml(plantName)}</div>
                        <div style="font-size: 0.8rem; color: #475569; margin-top: 0.25rem;">
                            VNB: <b>${escapeHtml(vnb)}</b><br>
                            Spannung: <b>${voltKv} kV</b> · P<sub>AV</sub>: <b>${pavKw.toLocaleString('de-DE')} kW</b> (${(pavKw/1000).toFixed(2)} MW)
                        </div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem 1rem;">
                        <div style="font-size: 0.72rem; color: #64748b; font-weight: 600; text-transform: uppercase;">2. Maschinentransformator</div>
                        <div style="font-size: 0.9rem; font-weight: 700; color: var(--navy); margin-top: 0.2rem;">${hasTrafo ? '✓ Transformator aktiv' : 'Kein Trafo (NS Direkt)'}</div>
                        <div style="font-size: 0.8rem; color: #475569; margin-top: 0.25rem;">
                            ${escapeHtml(trafoText)}
                        </div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem 1rem;">
                        <div style="font-size: 0.72rem; color: #64748b; font-weight: 600; text-transform: uppercase;">3. Messung & Schutz</div>
                        <div style="font-size: 0.82rem; color: #475569; margin-top: 0.3rem; line-height: 1.45;">
                            NAP Zähler: <b>${escapeHtml(meterText)}</b><br>
                            Schutzrelais: <b>${escapeHtml(protText)}</b>
                        </div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem 1rem;">
                        <div style="font-size: 0.72rem; color: #64748b; font-weight: 600; text-transform: uppercase;">4. Regelung & Steuerung</div>
                        <div style="font-size: 0.82rem; color: #475569; margin-top: 0.3rem; line-height: 1.45;">
                            Verfahren: <b>${reactiveText}</b><br>
                            EZA-Regler: <b>Phoenix Contact AXC F 2152</b>
                        </div>
                    </div>
                </div>

                <div style="margin-top: 0.25rem;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #334155; margin-bottom: 0.4rem; display: flex; justify-content: space-between;">
                        <span>Erzeugungseinheiten (${questComponents.length} Positionen):</span>
                        <span>P<sub>inst</sub>: ${pInstKw.toFixed(0)} kW | S<sub>inst</sub>: ${sInstKva.toFixed(0)} kVA ${totalBessKwh > 0 ? `| BESS: ${totalBessKwh} kWh` : ''}</span>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 0.4rem;">
                        ${compSummaryHtml}
                    </div>
                </div>
            `;
        }
"""

# Insert wizard JS right before `async function openPlantQuestionnaireModal()`
target_func = "async function openPlantQuestionnaireModal()"
assert target_func in content, "Could not find openPlantQuestionnaireModal"

content = content.replace(target_func, wizard_js + "\n        " + target_func, 1)
print("Added Wizard JavaScript functions!")

# Update openPlantQuestionnaireModal to initialize wizard step 1
old_open_code = """            modal.style.display = "flex";
        }"""
new_open_code = """            modal.style.display = "flex";
            currentWizardStep = 1;
            updateWizardStepperUI();
        }"""
content = content.replace(old_open_code, new_open_code, 1)
print("Updated openPlantQuestionnaireModal to reset step to 1!")

# Update loadQuestionnairePreset and resetQuestionnaireForm to reset step to 1
old_load_code = """            renderQuestionnaireComponents();
            triggerQuestionnairePreviewDebounced();
        }

        function resetQuestionnaireForm() {"""

new_load_code = """            renderQuestionnaireComponents();
            triggerQuestionnairePreviewDebounced();
            currentWizardStep = 1;
            updateWizardStepperUI();
        }

        function resetQuestionnaireForm() {"""

content = content.replace(old_load_code, new_load_code, 1)

old_reset_code = """            questComponents = [];
            addQuestionnaireComponent('PV_INVERTER');
        }"""

new_reset_code = """            questComponents = [];
            addQuestionnaireComponent('PV_INVERTER');
            currentWizardStep = 1;
            updateWizardStepperUI();
        }"""

content = content.replace(old_reset_code, new_reset_code, 1)
print("Updated presets and reset to reset wizard to step 1!")

# Update openCreatePlantModal so that "+ Neue Anlage" opens the Wizard!
old_create_plant = """        async function openCreatePlantModal() {
            if (!authToken || !currentUser) {
                alert("Bitte melden Sie sich an, um eine neue Energieanlage anzulegen.");
                openAuthModal('login');
                return;
            }

            if (currentUser.role !== 'SUPER_ADMIN' && currentUser.role !== 'ENGINEER') {
                alert("Berechtigung erforderlich: Nur Benutzer mit der Rolle 'ENGINEER' oder 'SUPER_ADMIN' können neue Erzeugungsanlagen registrieren. Bitte wenden Sie sich an Ihren Administrator.");
                return;
            }

            document.getElementById("createPlantErrorBanner").style.display = "none";
            document.getElementById("createPlantForm").reset();
            document.getElementById("plantGridOperator").value = "Bayernwerk Netz GmbH";

            // Populate initial device select with registered devices
            const select = document.getElementById("plantInitialDevice");
            select.innerHTML = '<option value="">-- Kein Gerät (später zuweisen) --</option>';
            try {
                const res = await fetch(`${API_BASE}/api/devices`, {
                    headers: { "Authorization": `Bearer ${authToken}` }
                });
                if (res.ok) {
                    const devices = await res.json();
                    devices.forEach(dev => {
                        const opt = document.createElement("option");
                        opt.value = dev.device_id;
                        opt.innerText = `${dev.name} (${dev.device_id}) - ${dev.local_ip}`;
                        select.appendChild(opt);
                    });
                }
            } catch (e) {
                console.warn("Could not fetch devices for plant creation:", e);
            }

            document.getElementById("createPlantModal").style.display = "flex";
        }"""

new_create_plant = """        async function openCreatePlantModal() {
            // Open the new step-by-step Anlagen-Wizard directly
            return openPlantQuestionnaireModal();
        }"""

content = content.replace(old_create_plant, new_create_plant, 1)
print("Updated openCreatePlantModal to route directly to openPlantQuestionnaireModal!")

# Update header and hero buttons
content = content.replace('<button class="btn btn-primary" id="btnCreatePlantHeader" style="display: none;" onclick="openCreatePlantModal()">\n                + Neue Anlage\n            </button>',
                          '<button class="btn btn-primary" id="btnCreatePlantHeader" style="display: none;" onclick="openPlantQuestionnaireModal()">\n                🧙‍♂️ + Neue Anlage (Wizard)\n            </button>')

content = content.replace('<button class="btn btn-primary" id="btnCreatePlantInTab" onclick="openCreatePlantModal()">+ Neue Anlage anlegen</button>',
                          '<button class="btn btn-primary" id="btnCreatePlantInTab" onclick="openPlantQuestionnaireModal()">🧙‍♂️ + Neue Anlage (Wizard)</button>')

content = content.replace('📋 Schneller Fragebogen (Kein SLD nötig)',
                          '🧙‍♂️ Anlage anlegen (Schritt-für-Schritt Wizard)')

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"File updated successfully! New length: {len(content)}")
