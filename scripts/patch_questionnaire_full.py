"""
Patch script to insert the Questionnaire Modal HTML and full JavaScript logic into index.html.
"""

import os

html_path = "backend/templates/index.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# ----------------- MODAL HTML ----------------- #
target_modal_marker = """    <!-- Complete PCU Configuration Result Modal -->"""

modal_html = """    <!-- ======================================================== -->
    <!-- Interaktiver Anlagen-Fragebogen (SLD-Ersatz) Modal -->
    <!-- ======================================================== -->
    <div class="modal-backdrop" id="plantQuestionnaireModal" style="display: none; z-index: 1050;">
        <div class="modal" style="max-width: 1200px; width: 96vw; padding: 2.2rem; max-height: 94vh; overflow-y: auto; background: var(--surface); border: 1px solid var(--line); border-radius: 16px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);">
            <!-- Modal Header -->
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; border-bottom: 1px solid var(--line); padding-bottom: 1.2rem;">
                <div>
                    <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.25rem 0.75rem; border-radius: 9999px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); font-size: 0.76rem; font-weight: 700; color: #10b981; text-transform: uppercase; margin-bottom: 0.4rem;">
                        📋 Digitaler SLD-Ersatz · VDE-AR-N 4110 / 4105
                    </div>
                    <h3 style="font-size: 1.55rem; font-weight: 800; letter-spacing: -0.02em; color: var(--navy); margin-bottom: 0.3rem;">
                        Interaktiver Anlagen-Fragebogen
                    </h3>
                    <p style="color: var(--text-muted); font-size: 0.88rem; margin: 0; line-height: 1.5;">
                        Konfigurieren Sie Erzeugungs- und Speicheranlagen <strong>ohne PDF-Übersichtsschaltplan (SLD)</strong>. Wählen Sie marktübliche Standard-Komponenten oder definieren Sie eigene Custom-Geräte. Das System berechnet Netztopologie und Phoenix EZA-Reglerparameter in Echtzeit.
                    </p>
                </div>
                <button type="button" class="btn" style="padding: 0.35rem 0.75rem; font-size: 0.95rem; border-radius: 8px;" onclick="closePlantQuestionnaireModal()">✕</button>
            </div>

            <!-- Schnellvorlagen (Presets) Bar -->
            <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid var(--line); border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
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

            <!-- Error Banner -->
            <div id="questErrorBanner" style="display: none; padding: 0.85rem 1.1rem; border-radius: 8px; background: rgba(244, 63, 94, 0.15); border: 1px solid var(--rose); color: #be123c; font-size: 0.85rem; margin-bottom: 1.25rem;"></div>

            <!-- Main Questionnaire Form Grid -->
            <form id="plantQuestionnaireForm" onsubmit="handlePlantQuestionnaireSubmit(event)">
                <div style="display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 1.5rem; align-items: start;">
                    
                    <!-- LEFT COLUMN: Form Steps -->
                    <div style="display: flex; flex-direction: column; gap: 1.25rem;">

                        <!-- STEP 1: Netzanschluss (NAP) -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid var(--line); border-radius: 12px; background: var(--surface);">
                            <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1rem;">
                                <span style="display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%; background: #0284c7; color: #fff; font-size: 0.75rem; font-weight: 700;">1</span>
                                <h4 style="font-size: 1rem; font-weight: 700; margin: 0; color: var(--navy);">Netzanschluss &amp; Netzbetreiber (NAP)</h4>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                                <div style="grid-column: span 2;">
                                    <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.3rem;">Anlagenbezeichnung *</label>
                                    <input type="text" id="questPlantName" class="form-input" placeholder="z. B. Solarpark Musterpark 1.5 MWp" style="width: 100%;" required oninput="triggerQuestionnairePreviewDebounced()">
                                </div>
                                <div>
                                    <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.3rem;">Netzbetreiber (VNB) *</label>
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
                                    <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.3rem;">Netzspannungsebene (NAP) *</label>
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
                                    <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.3rem;">Vereinbarte Anschlusswirkleistung P<sub>AV</sub> (kW) *</label>
                                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                                        <input type="number" id="questPavKw" class="form-input" value="1500" min="1" step="10" style="width: 180px;" required oninput="triggerQuestionnairePreviewDebounced()">
                                        <span style="font-size: 0.85rem; color: var(--text-muted);">kW (<span id="questPavMwDisplay">1.50 MW</span> Einspeiselimit am Übergabepunkt)</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- STEP 2: Maschinentransformator (T1) -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid var(--line); border-radius: 12px; background: var(--surface);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                <div style="display: flex; align-items: center; gap: 0.6rem;">
                                    <span style="display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%; background: #7c3aed; color: #fff; font-size: 0.75rem; font-weight: 700;">2</span>
                                    <h4 style="font-size: 1rem; font-weight: 700; margin: 0; color: var(--navy);">Maschinentransformator (T1)</h4>
                                </div>
                                <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer; font-size: 0.84rem; font-weight: 600;">
                                    <input type="checkbox" id="questHasTrafo" checked onchange="onQuestTrafoToggle()">
                                    Transformator vorhanden
                                </label>
                            </div>
                            
                            <div id="questTrafoFieldsWrap">
                                <div style="margin-bottom: 0.75rem;">
                                    <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.3rem;">Marktüblicher Transformator (T1) *</label>
                                    <select id="questTrafoSelect" class="form-input" style="width: 100%;" onchange="onQuestTrafoSelectChange()">
                                        <!-- Populated via loadQuestionnaireCatalog() -->
                                    </select>
                                </div>
                                <div id="questTrafoCustomFields" style="display: none; grid-template-columns: 1fr 1fr 1fr; gap: 0.75rem; margin-top: 0.75rem; background: rgba(124, 58, 237, 0.05); padding: 0.85rem; border-radius: 8px; border: 1px dashed rgba(124, 58, 237, 0.3);">
                                    <div>
                                        <label style="font-size: 0.75rem; color: var(--text-muted); display: block;">Nennscheinleistung S<sub>rT</sub> (kVA)</label>
                                        <input type="number" id="questTrafoCustomKva" class="form-input" value="1600" step="50" style="width: 100%;" oninput="triggerQuestionnairePreviewDebounced()">
                                    </div>
                                    <div>
                                        <label style="font-size: 0.75rem; color: var(--text-muted); display: block;">Kurzschlussspannung u<sub>k</sub> (%)</label>
                                        <input type="number" id="questTrafoCustomUk" class="form-input" value="6.0" step="0.1" style="width: 100%;" oninput="triggerQuestionnairePreviewDebounced()">
                                    </div>
                                    <div>
                                        <label style="font-size: 0.75rem; color: var(--text-muted); display: block;">Schaltgruppe</label>
                                        <input type="text" id="questTrafoCustomGroup" class="form-input" value="Dyn5" style="width: 100%;" oninput="triggerQuestionnairePreviewDebounced()">
                                    </div>
                                </div>
                            </div>
                            <div id="questNoTrafoNote" style="display: none; padding: 0.75rem; background: rgba(148, 163, 184, 0.1); border-radius: 6px; font-size: 0.82rem; color: var(--text-muted);">
                                ℹ️ Kein Transformator gewählt. Erzeugungseinheiten speisen direkt in die Niederspannungsebene ein.
                            </div>
                        </div>

                        <!-- STEP 3: Erzeugungseinheiten (EZE) & Speicher -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid var(--line); border-radius: 12px; background: var(--surface);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                <div style="display: flex; align-items: center; gap: 0.6rem;">
                                    <span style="display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%; background: #10b981; color: #fff; font-size: 0.75rem; font-weight: 700;">3</span>
                                    <h4 style="font-size: 1rem; font-weight: 700; margin: 0; color: var(--navy);">Erzeugungseinheiten (EZE) &amp; Speicher</h4>
                                </div>
                                <button type="button" class="btn btn-sm btn-primary" style="font-size: 0.78rem; background: linear-gradient(135deg, #10b981, #0284c7); border: none;" onclick="addQuestionnaireComponent('PV_INVERTER')">
                                    + Komponente hinzufügen
                                </button>
                            </div>

                            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: -0.5rem; margin-bottom: 0.85rem;">
                                Wählen Sie Wechselrichter oder Speicher aus der marktüblichen Liste (z. B. Huawei, SMA, Sungrow, BYD) oder erfassen Sie ein individuelles Modell (Custom).
                            </p>

                            <!-- Dynamic List of Components -->
                            <div id="questComponentsContainer" style="display: flex; flex-direction: column; gap: 0.85rem;">
                                <!-- Populated dynamically by renderQuestionnaireComponents() -->
                            </div>
                        </div>

                        <!-- STEP 4: Messung, Schutz & Regelung -->
                        <div class="card" style="padding: 1.25rem; border: 1px solid var(--line); border-radius: 12px; background: var(--surface);">
                            <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1rem;">
                                <span style="display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%; background: #f59e0b; color: #fff; font-size: 0.75rem; font-weight: 700;">4</span>
                                <h4 style="font-size: 1rem; font-weight: 700; margin: 0; color: var(--navy);">Messung, Schutz &amp; VDE-Regelverfahren</h4>
                            </div>

                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                                <div>
                                    <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.3rem;">Zähler am Übergabepunkt (NAP) *</label>
                                    <select id="questMeterSelect" class="form-input" style="width: 100%;" onchange="onQuestMeterSelectChange()">
                                        <!-- Populated via catalog -->
                                    </select>
                                </div>
                                <div>
                                    <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.3rem;">Netz- &amp; Anlagenschutz (Schutzrelais) *</label>
                                    <select id="questProtSelect" class="form-input" style="width: 100%;" onchange="onQuestProtSelectChange()">
                                        <!-- Populated via catalog -->
                                    </select>
                                </div>
                                <div>
                                    <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.3rem;">VDE Blindleistungsverfahren *</label>
                                    <select id="questReactiveMode" class="form-input" style="width: 100%;" onchange="triggerQuestionnairePreviewDebounced()">
                                        <option value="QU" selected>Q(U) - Spannungsabhängig (Standard Mittelspannung)</option>
                                        <option value="COS_PHI">cos φ(P) - Wirkleistungsabhängige Kennlinie</option>
                                        <option value="FIXED_COS_PHI">cos φ fest (z. B. 0.95 übererregt / untererregt)</option>
                                        <option value="FIXED_Q">Fester Blindleistungssollwert Q (kvar)</option>
                                    </select>
                                </div>
                                <div>
                                    <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.3rem;">Zuweisung EZA-Regler (PCU)</label>
                                    <select id="questTargetDeviceSelect" class="form-input" style="width: 100%;">
                                        <option value="coneza-phoenix-axcf2152">Phoenix Contact AXC F 2152 (Coneza Standard EZA)</option>
                                    </select>
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
                        <div class="card" style="padding: 1.25rem; border: 1px solid var(--line); border-radius: 12px; background: var(--surface);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    <span style="font-size: 0.95rem;">⚡</span>
                                    <strong style="font-size: 0.9rem; color: var(--navy);">Digitales Single Line Diagramm (SLD)</strong>
                                </div>
                                <span style="font-size: 0.74rem; color: #10b981; font-weight: 600;">✓ Live synthetisiert</span>
                            </div>

                            <p style="font-size: 0.78rem; color: var(--text-muted); margin: 0 0 0.75rem 0;">
                                Dieses VDE-konforme Vektordiagramm ersetzt jeden manuellen PDF-Upload und wird direkt als Netzanschlussdokument hinterlegt.
                            </p>

                            <!-- SVG Preview Container -->
                            <div id="questSldSvgContainer" style="width: 100%; height: 380px; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                                <div style="font-size: 0.82rem; color: #94a3b8; text-align: center; padding: 2rem;">
                                    ⏳ Generiere SLD-Vorschau...
                                </div>
                            </div>
                        </div>

                    </div>

                </div>

                <!-- Action Bar -->
                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--line); padding-top: 1.5rem; margin-top: 1.5rem;">
                    <button type="button" class="btn" onclick="closePlantQuestionnaireModal()">Abbrechen</button>
                    <div style="display: flex; gap: 0.85rem; align-items: center;">
                        <span style="font-size: 0.82rem; color: var(--text-muted);">Alle VDE-AR-N 4110 Register werden sofort berechnet.</span>
                        <button type="submit" class="btn btn-primary" id="btnSubmitQuestionnaire" style="background: linear-gradient(135deg, #10b981, #0284c7); border: none; font-weight: 700; padding: 0.75rem 1.6rem; font-size: 0.95rem; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);">
                            🚀 Anlage erstellen &amp; VDE 4110 PCU generieren
                        </button>
                    </div>
                </div>
            </form>
        </div>
    </div>
"""

assert target_modal_marker in content, "target_modal_marker not found"
content = content.replace(target_modal_marker, modal_html + "\n\n" + target_modal_marker, 1)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: Part 2 (Modal HTML) inserted.")
