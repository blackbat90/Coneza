"""
Patch script to insert Questionnaire JavaScript logic into index.html.
"""

import os

html_path = "backend/templates/index.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

target_marker = """        function displayPcuResult(data) {"""

js_code = """        // ========================================================
        // Interaktiver Anlagen-Fragebogen (SLD-Ersatz) Logik
        // ========================================================
        let questCatalog = null;
        let questComponents = [];
        let questPreviewDebounceTimer = null;

        async function fetchQuestionnaireCatalog() {
            if (questCatalog) return questCatalog;
            try {
                const res = await fetch(`${API_BASE}/api/questionnaire/catalog`, {
                    headers: { "Authorization": `Bearer ${authToken}` }
                });
                if (res.ok) {
                    questCatalog = await res.json();
                } else {
                    console.warn("Could not fetch questionnaire catalog, using fallbacks");
                    questCatalog = { pv_inverters: [], bess_systems: [], transformers: [], meters: [], protection_relays: [], presets: [] };
                }
            } catch (e) {
                console.error("Error fetching catalog:", e);
                questCatalog = { pv_inverters: [], bess_systems: [], transformers: [], meters: [], protection_relays: [], presets: [] };
            }
            return questCatalog;
        }

        async function openPlantQuestionnaireModal() {
            if (!authToken || !currentUser) {
                alert("Bitte melden Sie sich an, um den Anlagen-Fragebogen zu nutzen.");
                openAuthModal('login');
                return;
            }

            const modal = document.getElementById("plantQuestionnaireModal");
            const errBanner = document.getElementById("questErrorBanner");
            if (errBanner) errBanner.style.display = "none";

            await fetchQuestionnaireCatalog();
            populateQuestionnaireDropdowns();

            // Load default preset if components empty
            if (questComponents.length === 0) {
                loadQuestionnairePreset('preset_pv_1500kw');
            } else {
                renderQuestionnaireComponents();
                triggerQuestionnairePreviewDebounced();
            }

            modal.style.display = "flex";
        }

        function closePlantQuestionnaireModal() {
            const modal = document.getElementById("plantQuestionnaireModal");
            if (modal) modal.style.display = "none";
        }

        function populateQuestionnaireDropdowns() {
            if (!questCatalog) return;

            // 1. Transformers Dropdown
            const trafoSel = document.getElementById("questTrafoSelect");
            if (trafoSel) {
                trafoSel.innerHTML = "";
                (questCatalog.transformers || []).forEach(t => {
                    const opt = document.createElement("option");
                    opt.value = t.id;
                    opt.innerText = `${t.name} · uk = ${t.uk_percent}% (${t.vector_group})`;
                    trafoSel.appendChild(opt);
                });
                const optCustom = document.createElement("option");
                optCustom.value = "__custom__";
                optCustom.innerText = "🔧 Benutzerdefiniert (Custom Trafo)...";
                trafoSel.appendChild(optCustom);
            }

            // 2. Meters Dropdown
            const meterSel = document.getElementById("questMeterSelect");
            if (meterSel) {
                meterSel.innerHTML = "";
                (questCatalog.meters || []).forEach(m => {
                    const opt = document.createElement("option");
                    opt.value = m.id;
                    opt.innerText = `${m.brand} ${m.model} (${m.type})`;
                    meterSel.appendChild(opt);
                });
                const optCustom = document.createElement("option");
                optCustom.value = "__custom__";
                optCustom.innerText = "🔧 Anderer Zähler / Netzanalysator (Custom)...";
                meterSel.appendChild(optCustom);
            }

            // 3. Protection Relays Dropdown
            const protSel = document.getElementById("questProtSelect");
            if (protSel) {
                protSel.innerHTML = "";
                (questCatalog.protection_relays || []).forEach(r => {
                    const opt = document.createElement("option");
                    opt.value = r.id;
                    opt.innerText = `${r.brand} ${r.model} (${r.type})`;
                    protSel.appendChild(opt);
                });
                const optCustom = document.createElement("option");
                optCustom.value = "__custom__";
                optCustom.innerText = "🔧 Anderes Schutzrelais (Custom)...";
                protSel.appendChild(optCustom);
            }
        }

        function onQuestVnbChange() {
            const sel = document.getElementById("questGridOperatorSelect");
            const customInput = document.getElementById("questGridOperatorCustom");
            if (sel.value === "__custom__") {
                customInput.style.display = "block";
                customInput.required = true;
            } else {
                customInput.style.display = "none";
                customInput.required = false;
            }
            triggerQuestionnairePreviewDebounced();
        }

        function onQuestVoltageChange() {
            const sel = document.getElementById("questVoltageSelect");
            const customWrap = document.getElementById("questVoltageCustomWrap");
            const customInput = document.getElementById("questVoltageCustom");
            if (sel.value === "__custom__") {
                customWrap.style.display = "block";
                customInput.required = true;
            } else {
                customWrap.style.display = "none";
                customInput.required = false;
            }
            triggerQuestionnairePreviewDebounced();
        }

        function onQuestTrafoToggle() {
            const checked = document.getElementById("questHasTrafo").checked;
            const fieldsWrap = document.getElementById("questTrafoFieldsWrap");
            const note = document.getElementById("questNoTrafoNote");
            if (checked) {
                fieldsWrap.style.display = "block";
                note.style.display = "none";
            } else {
                fieldsWrap.style.display = "none";
                note.style.display = "block";
            }
            triggerQuestionnairePreviewDebounced();
        }

        function onQuestTrafoSelectChange() {
            const sel = document.getElementById("questTrafoSelect");
            const customFields = document.getElementById("questTrafoCustomFields");
            if (sel.value === "__custom__") {
                customFields.style.display = "grid";
            } else {
                customFields.style.display = "none";
            }
            triggerQuestionnairePreviewDebounced();
        }

        function onQuestMeterSelectChange() {
            triggerQuestionnairePreviewDebounced();
        }

        function onQuestProtSelectChange() {
            triggerQuestionnairePreviewDebounced();
        }

        // ----------------- Dynamic Components Management ----------------- //

        function renderQuestionnaireComponents() {
            const container = document.getElementById("questComponentsContainer");
            if (!container) return;
            container.innerHTML = "";

            if (questComponents.length === 0) {
                container.innerHTML = `<div style="padding:1.5rem; text-align:center; color:var(--text-muted); background:rgba(15,23,42,0.3); border-radius:8px;">Noch keine Komponenten hinzugefügt. Klicken Sie oben auf "+ Komponente hinzufügen".</div>`;
                return;
            }

            questComponents.forEach((comp, idx) => {
                const card = document.createElement("div");
                card.style.background = comp.type === 'BESS' ? 'rgba(16, 185, 129, 0.05)' : 'rgba(2, 132, 199, 0.05)';
                card.style.border = comp.type === 'BESS' ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(2, 132, 199, 0.3)';
                card.style.borderRadius = "10px";
                card.style.padding = "0.95rem";
                card.style.display = "flex";
                card.style.flexDirection = "column";
                card.style.gap = "0.65rem";

                // Build Model Options
                const catalogItems = comp.type === 'BESS' ? (questCatalog?.bess_systems || []) : (questCatalog?.pv_inverters || []);
                let optionsHtml = '';
                catalogItems.forEach(item => {
                    const selected = (!comp.is_custom && comp.catalog_id === item.id) ? 'selected' : '';
                    const detail = comp.type === 'BESS' ? `${item.capacity_kwh} kWh / ${item.rated_active_kw} kW` : `${item.rated_active_kw} kW`;
                    optionsHtml += `<option value="${item.id}" ${selected}>${item.brand} ${item.model} (${detail})</option>`;
                });
                optionsHtml += `<option value="__custom__" ${comp.is_custom ? 'selected' : ''}>🔧 Benutzerdefiniert (Custom ${comp.type === 'BESS' ? 'Speicher' : 'Wechselrichter'})...</option>`;

                card.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:0.5rem;">
                            <span class="badge" style="background:${comp.type === 'BESS' ? '#10b981' : '#0284c7'}; color:#fff; font-weight:700; font-size:0.75rem;">
                                ${comp.type === 'BESS' ? '🔋 BESS Batteriespeicher' : '☀️ PV-Wechselrichter'}
                            </span>
                            <span style="font-size:0.8rem; font-weight:600; color:var(--navy);">Zweig #${idx + 1}</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:0.5rem;">
                            <select class="form-input" style="padding:0.2rem 0.4rem; font-size:0.75rem;" onchange="onQuestComponentTypeChange(${idx}, this.value)">
                                <option value="PV_INVERTER" ${comp.type === 'PV_INVERTER' ? 'selected' : ''}>☀️ Photovoltaik</option>
                                <option value="BESS" ${comp.type === 'BESS' ? 'selected' : ''}>🔋 Batteriespeicher</option>
                            </select>
                            ${questComponents.length > 1 ? `<button type="button" class="btn btn-sm" style="color:#f43f5e; padding:0.2rem 0.5rem; font-size:0.85rem;" title="Komponente entfernen" onclick="removeQuestionnaireComponent(${idx})">🗑️</button>` : ''}
                        </div>
                    </div>

                    <!-- Model Selector & Count -->
                    <div style="display:grid; grid-template-columns: 2fr 1fr; gap:0.75rem; align-items:center;">
                        <div>
                            <label style="font-size:0.72rem; color:var(--text-muted); display:block; margin-bottom:0.2rem;">Modell / Typ *</label>
                            <select class="form-input" style="width:100%; font-size:0.82rem;" onchange="onQuestComponentSelectChange(${idx}, this.value)">
                                ${optionsHtml}
                            </select>
                        </div>
                        <div>
                            <label style="font-size:0.72rem; color:var(--text-muted); display:block; margin-bottom:0.2rem;">Anzahl Einheiten *</label>
                            <input type="number" class="form-input" value="${comp.count || 1}" min="1" max="500" style="width:100%; font-size:0.85rem; font-weight:bold;" oninput="onQuestComponentCountChange(${idx}, this.value)">
                        </div>
                    </div>

                    <!-- Custom Inputs if is_custom -->
                    ${comp.is_custom ? `
                        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr ${comp.type === 'BESS' ? '1fr' : ''}; gap:0.5rem; background:rgba(0,0,0,0.1); padding:0.6rem; border-radius:6px;">
                            <div>
                                <label style="font-size:0.7rem; color:var(--text-muted);">Hersteller</label>
                                <input type="text" class="form-input" value="${escapeHtml(comp.brand || '')}" placeholder="z.B. SMA" style="width:100%; font-size:0.75rem;" oninput="onQuestComponentCustomFieldChange(${idx}, 'brand', this.value)">
                            </div>
                            <div>
                                <label style="font-size:0.7rem; color:var(--text-muted);">Modellname</label>
                                <input type="text" class="form-input" value="${escapeHtml(comp.model || '')}" placeholder="z.B. Custom 100" style="width:100%; font-size:0.75rem;" oninput="onQuestComponentCustomFieldChange(${idx}, 'model', this.value)">
                            </div>
                            <div>
                                <label style="font-size:0.7rem; color:var(--text-muted);">P_nenn (kW)</label>
                                <input type="number" class="form-input" value="${comp.unit_active_kw || 100}" step="1" style="width:100%; font-size:0.75rem;" oninput="onQuestComponentCustomFieldChange(${idx}, 'unit_active_kw', this.value)">
                            </div>
                            ${comp.type === 'BESS' ? `
                            <div>
                                <label style="font-size:0.7rem; color:var(--text-muted);">Kapazität (kWh)</label>
                                <input type="number" class="form-input" value="${comp.capacity_kwh || 130}" step="1" style="width:100%; font-size:0.75rem;" oninput="onQuestComponentCustomFieldChange(${idx}, 'capacity_kwh', this.value)">
                            </div>` : ''}
                        </div>
                    ` : `
                        <div style="font-size:0.75rem; color:var(--text-muted); display:flex; gap:0.85rem; align-items:center; background:rgba(255,255,255,0.04); padding:0.4rem 0.6rem; border-radius:6px;">
                            <span>Nennleistung: <strong>${(comp.count * comp.unit_active_kw).toFixed(1)} kW</strong> (${comp.count}x ${comp.unit_active_kw} kW)</span>
                            ${comp.type === 'BESS' ? `<span>Speicher: <strong>${(comp.count * comp.capacity_kwh).toFixed(0)} kWh</strong></span>` : ''}
                            <span>Spannung: ${comp.ac_voltage_v || 400} V</span>
                        </div>
                    `}
                `;
                container.appendChild(card);
            });
        }

        function addQuestionnaireComponent(type = 'PV_INVERTER') {
            const catalogItems = type === 'BESS' ? (questCatalog?.bess_systems || []) : (questCatalog?.pv_inverters || []);
            const defaultItem = catalogItems[0] || {};

            questComponents.push({
                type: type,
                is_custom: false,
                catalog_id: defaultItem.id || 'custom',
                brand: defaultItem.brand || 'Generic',
                model: defaultItem.model || 'Inverter',
                count: 1,
                unit_active_kw: defaultItem.rated_active_kw || 100.0,
                unit_apparent_kva: defaultItem.rated_apparent_kva || 110.0,
                capacity_kwh: defaultItem.capacity_kwh || 0.0,
                ac_voltage_v: defaultItem.ac_voltage_v || 400.0
            });

            renderQuestionnaireComponents();
            triggerQuestionnairePreviewDebounced();
        }

        function removeQuestionnaireComponent(idx) {
            if (questComponents.length <= 1) return;
            questComponents.splice(idx, 1);
            renderQuestionnaireComponents();
            triggerQuestionnairePreviewDebounced();
        }

        function onQuestComponentTypeChange(idx, newType) {
            questComponents[idx].type = newType;
            const catalogItems = newType === 'BESS' ? (questCatalog?.bess_systems || []) : (questCatalog?.pv_inverters || []);
            const defaultItem = catalogItems[0] || {};
            questComponents[idx].is_custom = false;
            questComponents[idx].catalog_id = defaultItem.id || '';
            questComponents[idx].brand = defaultItem.brand || '';
            questComponents[idx].model = defaultItem.model || '';
            questComponents[idx].unit_active_kw = defaultItem.rated_active_kw || 100.0;
            questComponents[idx].unit_apparent_kva = defaultItem.rated_apparent_kva || 100.0;
            questComponents[idx].capacity_kwh = defaultItem.capacity_kwh || 0.0;
            questComponents[idx].ac_voltage_v = defaultItem.ac_voltage_v || 400.0;
            renderQuestionnaireComponents();
            triggerQuestionnairePreviewDebounced();
        }

        function onQuestComponentSelectChange(idx, catalogId) {
            if (catalogId === "__custom__") {
                questComponents[idx].is_custom = true;
                questComponents[idx].catalog_id = "__custom__";
            } else {
                questComponents[idx].is_custom = false;
                questComponents[idx].catalog_id = catalogId;
                const catalogItems = questComponents[idx].type === 'BESS' ? (questCatalog?.bess_systems || []) : (questCatalog?.pv_inverters || []);
                const found = catalogItems.find(i => i.id === catalogId);
                if (found) {
                    questComponents[idx].brand = found.brand;
                    questComponents[idx].model = found.model;
                    questComponents[idx].unit_active_kw = found.rated_active_kw;
                    questComponents[idx].unit_apparent_kva = found.rated_apparent_kva;
                    questComponents[idx].capacity_kwh = found.capacity_kwh || 0.0;
                    questComponents[idx].ac_voltage_v = found.ac_voltage_v || 400.0;
                }
            }
            renderQuestionnaireComponents();
            triggerQuestionnairePreviewDebounced();
        }

        function onQuestComponentCountChange(idx, val) {
            questComponents[idx].count = Math.max(1, parseInt(val) || 1);
            renderQuestionnaireComponents();
            triggerQuestionnairePreviewDebounced();
        }

        function onQuestComponentCustomFieldChange(idx, field, val) {
            if (field === 'unit_active_kw') {
                questComponents[idx].unit_active_kw = parseFloat(val) || 0;
                questComponents[idx].unit_apparent_kva = (parseFloat(val) || 0) * 1.05;
            } else if (field === 'capacity_kwh') {
                questComponents[idx].capacity_kwh = parseFloat(val) || 0;
            } else {
                questComponents[idx][field] = val;
            }
            triggerQuestionnairePreviewDebounced();
        }

        // ----------------- Presets & Resets ----------------- //

        function loadQuestionnairePreset(presetId) {
            if (!questCatalog || !questCatalog.presets) return;
            const p = questCatalog.presets.find(item => item.id === presetId);
            if (!p) return;

            document.getElementById("questPlantName").value = p.plant_name || "";
            
            const vnbSel = document.getElementById("questGridOperatorSelect");
            if (vnbSel) {
                let foundVnb = false;
                for (let opt of vnbSel.options) {
                    if (opt.value === p.grid_operator) {
                        opt.selected = true;
                        foundVnb = true;
                        break;
                    }
                }
                if (!foundVnb) {
                    vnbSel.value = "__custom__";
                    const customVnb = document.getElementById("questGridOperatorCustom");
                    customVnb.value = p.grid_operator;
                    customVnb.style.display = "block";
                } else {
                    document.getElementById("questGridOperatorCustom").style.display = "none";
                }
            }

            const voltSel = document.getElementById("questVoltageSelect");
            if (voltSel) {
                voltSel.value = (p.voltage_level_kv || 20.0).toString();
                document.getElementById("questVoltageCustomWrap").style.display = "none";
            }

            document.getElementById("questPavKw").value = p.p_av_kw || 1500;
            document.getElementById("questHasTrafo").checked = p.has_transformer !== false;
            onQuestTrafoToggle();

            if (p.transformer && p.transformer.catalog_id) {
                const trafoSel = document.getElementById("questTrafoSelect");
                if (trafoSel) trafoSel.value = p.transformer.catalog_id;
            }

            // Clone components
            questComponents = JSON.parse(JSON.stringify(p.components || []));
            renderQuestionnaireComponents();
            triggerQuestionnairePreviewDebounced();
        }

        function resetQuestionnaireForm() {
            document.getElementById("plantQuestionnaireForm").reset();
            questComponents = [];
            addQuestionnaireComponent('PV_INVERTER');
        }

        // ----------------- Realtime Calculations & Preview ----------------- //

        function triggerQuestionnairePreviewDebounced() {
            if (questPreviewDebounceTimer) clearTimeout(questPreviewDebounceTimer);
            questPreviewDebounceTimer = setTimeout(updateQuestionnaireCalculationsAndPreview, 250);
        }

        async function updateQuestionnaireCalculationsAndPreview() {
            // 1. Gather payload
            const plantName = document.getElementById("questPlantName").value || "Erzeugungsanlage";
            const vnbSel = document.getElementById("questGridOperatorSelect").value;
            const vnb = vnbSel === "__custom__" ? (document.getElementById("questGridOperatorCustom").value || "Netzbetreiber") : vnbSel;
            
            const voltSel = document.getElementById("questVoltageSelect").value;
            const voltKv = voltSel === "__custom__" ? (parseFloat(document.getElementById("questVoltageCustom").value) || 20.0) : parseFloat(voltSel);
            
            const pavKw = parseFloat(document.getElementById("questPavKw").value) || 1500;
            const hasTrafo = document.getElementById("questHasTrafo").checked;

            const trafoSel = document.getElementById("questTrafoSelect").value;
            let trafoObj = {};
            if (hasTrafo) {
                if (trafoSel === "__custom__") {
                    trafoObj = {
                        is_custom: true,
                        rated_kva: parseFloat(document.getElementById("questTrafoCustomKva").value) || 1600,
                        uk_percent: parseFloat(document.getElementById("questTrafoCustomUk").value) || 6.0,
                        vector_group: document.getElementById("questTrafoCustomGroup").value || "Dyn5"
                    };
                } else {
                    const foundTrafo = (questCatalog?.transformers || []).find(t => t.id === trafoSel);
                    if (foundTrafo) {
                        trafoObj = { ...foundTrafo, is_custom: false };
                    }
                }
            }

            const meterSel = document.getElementById("questMeterSelect").value;
            const foundMeter = (questCatalog?.meters || []).find(m => m.id === meterSel);

            const protSel = document.getElementById("questProtSelect").value;
            const foundProt = (questCatalog?.protection_relays || []).find(r => r.id === protSel);

            const reactiveMode = document.getElementById("questReactiveMode").value;

            // Compute local totals
            let pInstKw = 0;
            let sInstKva = 0;
            let bessKwh = 0;

            questComponents.forEach(c => {
                const count = c.count || 1;
                pInstKw += count * (c.unit_active_kw || 0);
                sInstKva += count * (c.unit_apparent_kva || (c.unit_active_kw * 1.05));
                if (c.type === 'BESS') {
                    bessKwh += count * (c.capacity_kwh || 0);
                }
            });

            const trafoKva = hasTrafo ? (trafoObj.rated_kva || (sInstKva * 1.15)) : sInstKva;
            const trafoLoadingPct = trafoKva > 0 ? (sInstKva / trafoKva * 100) : 100;

            // Update UI KPIs
            const kpiP = document.getElementById("questKpiPinst");
            if (kpiP) kpiP.innerText = `${pInstKw.toLocaleString('de-DE', { maximumFractionDigits: 1 })} kW`;
            const kpiPMw = document.getElementById("questKpiPinstMw");
            if (kpiPMw) kpiPMw.innerText = `${(pInstKw / 1000).toFixed(2)} MWp`;

            const kpiS = document.getElementById("questKpiSinst");
            if (kpiS) kpiS.innerText = `${sInstKva.toLocaleString('de-DE', { maximumFractionDigits: 1 })} kVA`;
            const kpiSMva = document.getElementById("questKpiSinstMva");
            if (kpiSMva) kpiSMva.innerText = `${(sInstKva / 1000).toFixed(2)} MVA`;

            const kpiBess = document.getElementById("questKpiBess");
            if (kpiBess) kpiBess.innerText = bessKwh > 0 ? `${bessKwh.toLocaleString('de-DE')} kWh (${(bessKwh/1000).toFixed(1)} MWh)` : "Kein Speicher";

            const kpiTrafo = document.getElementById("questKpiTrafoLoad");
            if (kpiTrafo) kpiTrafo.innerText = hasTrafo ? `${trafoLoadingPct.toFixed(1)} %` : "NS direkt (100%)";

            const trafoBar = document.getElementById("questTrafoBar");
            const trafoText = document.getElementById("questTrafoStatusText");
            if (trafoBar) {
                trafoBar.style.width = `${Math.min(100, trafoLoadingPct)}%`;
                if (trafoLoadingPct > 105) {
                    trafoBar.style.background = "#f43f5e";
                    if (trafoText) trafoText.innerText = "⚠️ Trafo überlastet (>100%)";
                } else if (trafoLoadingPct > 95) {
                    trafoBar.style.background = "#f59e0b";
                    if (trafoText) trafoText.innerText = "⚡ Volllast";
                } else {
                    trafoBar.style.background = "#10b981";
                    if (trafoText) trafoText.innerText = "✓ Optimal dimensioniert";
                }
            }

            const pavDisp = document.getElementById("questPavMwDisplay");
            if (pavDisp) pavDisp.innerText = `${(pavKw / 1000).toFixed(2)} MW`;

            // Server-side SVG Preview synthesis
            const payload = {
                plant_name: plantName,
                grid_operator: vnb,
                voltage_level_kv: voltKv,
                p_av_kw: pavKw,
                has_transformer: hasTrafo,
                transformer: trafoObj,
                components: questComponents,
                meter: foundMeter || { brand: "Janitza", model: "UMG 604E" },
                protection: foundProt || { brand: "Woodward", model: "HighProTec MRM4" },
                reactive_mode: reactiveMode
            };

            const container = document.getElementById("questSldSvgContainer");
            try {
                const res = await fetch(`${API_BASE}/api/questionnaire/preview-sld`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${authToken}`
                    },
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    const data = await res.json();
                    if (data.svg && container) {
                        container.innerHTML = data.svg;
                    }
                }
            } catch (err) {
                console.warn("Could not render SLD preview:", err);
            }
        }

        // ----------------- Submit Questionnaire Form ----------------- //

        async function handlePlantQuestionnaireSubmit(event) {
            event.preventDefault();
            const btn = document.getElementById("btnSubmitQuestionnaire");
            const errBanner = document.getElementById("questErrorBanner");
            if (errBanner) errBanner.style.display = "none";

            const plantName = document.getElementById("questPlantName").value.trim();
            if (!plantName) {
                if (errBanner) {
                    errBanner.innerText = "Bitte geben Sie einen Anlagennamen ein.";
                    errBanner.style.display = "block";
                }
                return;
            }

            const vnbSel = document.getElementById("questGridOperatorSelect").value;
            const vnb = vnbSel === "__custom__" ? document.getElementById("questGridOperatorCustom").value.trim() : vnbSel;
            const voltSel = document.getElementById("questVoltageSelect").value;
            const voltKv = voltSel === "__custom__" ? parseFloat(document.getElementById("questVoltageCustom").value) : parseFloat(voltSel);
            const pavKw = parseFloat(document.getElementById("questPavKw").value);
            const hasTrafo = document.getElementById("questHasTrafo").checked;

            const trafoSel = document.getElementById("questTrafoSelect").value;
            let trafoObj = {};
            if (hasTrafo) {
                if (trafoSel === "__custom__") {
                    trafoObj = {
                        is_custom: true,
                        rated_kva: parseFloat(document.getElementById("questTrafoCustomKva").value) || 1600,
                        uk_percent: parseFloat(document.getElementById("questTrafoCustomUk").value) || 6.0,
                        vector_group: document.getElementById("questTrafoCustomGroup").value || "Dyn5"
                    };
                } else {
                    const foundTrafo = (questCatalog?.transformers || []).find(t => t.id === trafoSel);
                    if (foundTrafo) trafoObj = { ...foundTrafo, is_custom: false };
                }
            }

            const meterSel = document.getElementById("questMeterSelect").value;
            const foundMeter = (questCatalog?.meters || []).find(m => m.id === meterSel);

            const protSel = document.getElementById("questProtSelect").value;
            const foundProt = (questCatalog?.protection_relays || []).find(r => r.id === protSel);

            const reactiveMode = document.getElementById("questReactiveMode").value;
            const targetDeviceId = document.getElementById("questTargetDeviceSelect").value;

            // Build request payload
            const payload = {
                plant_name: plantName,
                grid_operator: vnb,
                voltage_level_kv: voltKv,
                p_av_kw: pavKw,
                site_type: questComponents.some(c => c.type === 'BESS') ? (questComponents.some(c => c.type === 'PV_INVERTER') ? 'HYBRID' : 'BESS') : 'PV',
                has_transformer: hasTrafo,
                transformer: trafoObj,
                components: questComponents,
                meter: foundMeter || { brand: "Janitza", model: "UMG 604E", ip: "192.168.1.100", port: 502 },
                protection: foundProt || { brand: "Woodward", model: "HighProTec MRM4" },
                reactive_mode: reactiveMode,
                target_device_id: targetDeviceId
            };

            btn.disabled = true;
            btn.innerHTML = `<span class="spinner" style="display:inline-block; width:16px; height:16px; border:2px solid #fff; border-top-color:transparent; border-radius:50%; animation:spin 1s linear infinite; margin-right:6px; vertical-align:middle;"></span> Synthetisiere VDE-AR-N 4110 PCU...`;

            try {
                const res = await fetch(`${API_BASE}/api/plants/from-questionnaire`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${authToken}`
                    },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();

                if (res.ok) {
                    closePlantQuestionnaireModal();
                    loadPlants();
                    loadDevices();
                    // Open PCU Configuration Direct Result View
                    displayPcuResult(data);
                } else {
                    if (errBanner) {
                        errBanner.innerText = data.detail || "Fehler beim Erstellen der Anlage aus dem Fragebogen.";
                        errBanner.style.display = "block";
                    }
                }
            } catch (err) {
                if (errBanner) {
                    errBanner.innerText = `Netzwerkfehler: ${err.message}`;
                    errBanner.style.display = "block";
                }
            } finally {
                btn.disabled = false;
                btn.innerHTML = `🚀 Anlage erstellen &amp; VDE 4110 PCU generieren`;
            }
        }
"""

assert target_marker in content, "target_marker not found"
content = content.replace(target_marker, js_code + "\n\n" + target_marker, 1)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: Part 3 (JavaScript logic) inserted.")
