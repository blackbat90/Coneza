import re

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. ADD CSS
css_anchor = "        /* SVG Energy Flow Diagram Styles */"
new_css = """        /* Flow View Switcher (Synoptik vs 24h Histogramm) */
        .flow-view-switch-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 6px 0 8px 0;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .flow-view-pills {
            display: inline-flex;
            background: rgba(255, 255, 255, 0.05);
            padding: 2px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            gap: 2px;
        }

        .flow-view-pill {
            background: transparent;
            border: none;
            color: #94a3b8;
            font-size: 0.68rem;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        .flow-view-pill:hover {
            color: #ffffff;
            background: rgba(255, 255, 255, 0.06);
        }

        .flow-view-pill.active {
            background: rgba(37, 199, 201, 0.22);
            color: #38bdf8;
            border: 1px solid rgba(37, 199, 201, 0.45);
            box-shadow: 0 0 10px rgba(37, 199, 201, 0.15);
        }

        .flow-chart-legend {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            font-size: 0.64rem;
            color: #cbd5e1;
        }

        .legend-item {
            display: inline-flex;
            align-items: center;
            gap: 3.5px;
        }

        .legend-dot {
            width: 7px;
            height: 7px;
            border-radius: 2px;
            display: inline-block;
        }

        .legend-line {
            width: 14px;
            height: 2.5px;
            border-radius: 1px;
            display: inline-block;
        }

        /* 24h Histogram View Container */
        .energy-flow-histogram-wrap {
            width: 100%;
            margin: 10px 0 12px 0;
            position: relative;
        }

        .energy-flow-histogram-svg {
            width: 100%;
            height: auto;
            display: block;
            overflow: visible;
        }

        /* Interactive Histogram Tooltip */
        .hist-tooltip {
            position: absolute;
            pointer-events: none;
            background: rgba(6, 17, 28, 0.96);
            border: 1px solid #0ea5e9;
            border-radius: 8px;
            padding: 7px 11px;
            font-size: 0.68rem;
            color: #ffffff;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.55);
            backdrop-filter: blur(8px);
            z-index: 20;
            display: none;
            transition: opacity 0.1s ease;
            white-space: nowrap;
            line-height: 1.45;
        }

        /* SVG Energy Flow Diagram Styles */"""

assert css_anchor in content, "css_anchor not found"
content = content.replace(css_anchor, new_css, 1)

# 2. ADD HTML: View Switcher and Histogram Wrap
html_old = """                    <!-- SVG Synoptic Energy Flow Diagram -->
                    <div class="energy-flow-svg-wrap">"""

html_new = """                    <!-- View Mode Switcher: Synoptischer Fluss vs. 24h Histogramm Chart -->
                    <div class="flow-view-switch-bar">
                        <div class="flow-view-pills">
                            <button type="button" class="flow-view-pill active" id="btnFlowViewSynoptic" onclick="switchEnergyFlowView('synoptic')">
                                ⚡ Synoptischer Fluss
                            </button>
                            <button type="button" class="flow-view-pill" id="btnFlowViewHistogram" onclick="switchEnergyFlowView('histogram')">
                                📊 24h Lastgang &amp; Histogramm
                            </button>
                        </div>
                        <div class="flow-chart-legend" id="flowChartLegend" style="display: none;">
                            <span class="legend-item"><span class="legend-dot" style="background: #f59e0b;"></span> PV</span>
                            <span class="legend-item"><span class="legend-dot" style="background: #10b981;"></span> BESS Entladen</span>
                            <span class="legend-item"><span class="legend-dot" style="background: #059669;"></span> BESS Laden</span>
                            <span class="legend-item"><span class="legend-dot" style="background: #f43f5e;"></span> Last</span>
                            <span class="legend-item"><span class="legend-line" style="background: #25c7c9;"></span> NAP Netto</span>
                        </div>
                    </div>

                    <!-- View 1: SVG Synoptic Energy Flow Diagram -->
                    <div class="energy-flow-svg-wrap" id="energyFlowSvgWrap">"""

assert html_old in content, "html_old not found"
content = content.replace(html_old, html_new, 1)

# And right after </svg>\n                    </div> for SVG diagram, add the histogram container
svg_end_old = """                                <text x="512" y="134" fill="#34d399" font-size="10">Einspeisung Netto</text>
                            </g>
                        </svg>
                    </div>"""

svg_end_new = """                                <text x="512" y="134" fill="#34d399" font-size="10">Einspeisung Netto</text>
                            </g>
                        </svg>
                    </div>

                    <!-- View 2: Interactive 24h Energy Flow Histogram & Time-Series Graph -->
                    <div class="energy-flow-histogram-wrap" id="energyFlowHistogramWrap" style="display: none;">
                        <svg viewBox="0 0 660 215" class="energy-flow-histogram-svg" id="flowHistogramSvg" xmlns="http://www.w3.org/2000/svg">
                            <!-- Populated dynamically via renderEnergyFlowHistogram() -->
                        </svg>
                        <div id="histTooltip" class="hist-tooltip"></div>
                    </div>"""

assert svg_end_old in content, "svg_end_old not found"
content = content.replace(svg_end_old, svg_end_new, 1)

# 3. ADD JAVASCRIPT: switchEnergyFlowView and renderEnergyFlowHistogram
js_anchor = "        let flowSimulationMode = \"normal\";"
new_js_code = """        let activeFlowView = "synoptic"; // "synoptic" | "histogram"

        function switchEnergyFlowView(viewName) {
            activeFlowView = viewName;
            const btnSyn = document.getElementById("btnFlowViewSynoptic");
            const btnHist = document.getElementById("btnFlowViewHistogram");
            const wrapSyn = document.getElementById("energyFlowSvgWrap");
            const wrapHist = document.getElementById("energyFlowHistogramWrap");
            const legend = document.getElementById("flowChartLegend");

            if (viewName === "histogram") {
                if (btnSyn) btnSyn.classList.remove("active");
                if (btnHist) btnHist.classList.add("active");
                if (wrapSyn) wrapSyn.style.display = "none";
                if (wrapHist) wrapHist.style.display = "block";
                if (legend) legend.style.display = "flex";
                renderEnergyFlowHistogram();
            } else {
                if (btnSyn) btnSyn.classList.add("active");
                if (btnHist) btnHist.classList.remove("active");
                if (wrapSyn) wrapSyn.style.display = "block";
                if (wrapHist) wrapHist.style.display = "none";
                if (legend) legend.style.display = "none";
            }
        }

        function renderEnergyFlowHistogram() {
            const svg = document.getElementById("flowHistogramSvg");
            if (!svg) return;

            const cap = flowBaseline.capacity_kw || 2200.0;
            const mode = flowSimulationMode;
            const hasBess = flowBaseline.site_type === "BESS" || flowBaseline.site_type === "HYBRID";

            const wTotal = 660;
            const hTotal = 215;
            const xStart = 48;
            const xEnd = 648;
            const xPlotW = xEnd - xStart; // 600px
            const yZero = 152;
            const hPosMax = 125;
            const hNegMax = 32;

            const maxPosKw = Math.max(cap * 1.05, 50);
            const maxNegKw = hasBess ? Math.max(cap * 0.28, 20) : Math.max(cap * 0.08, 10);

            const colW = xPlotW / 24; // 25px per hour
            const barW = 16;
            const currentHour = new Date().getHours() || 14;

            let napPoints = [];
            let barsHtml = "";
            let overlayHtml = "";
            let dailyPvKwh = 0;
            let dailyNapKwh = 0;

            for (let h = 0; h < 24; h++) {
                // 1. Solar generation profile (bell curve peaking at 13:00)
                let pvKw = 0;
                if (h >= 6 && h <= 20) {
                    let sFactor = Math.sin(((h - 6) / 14) * Math.PI);
                    if (mode === "curtail" && h >= 11 && h <= 15) {
                        sFactor = Math.min(sFactor, 0.5); // 50% DSO curtailment
                    }
                    pvKw = Math.round(cap * sFactor * (0.94 + 0.04 * Math.sin(h * 0.8)));
                }

                // 2. BESS Battery
                let batKw = 0;
                if (hasBess) {
                    if (h >= 10 && h <= 14) {
                        // Charging (negative)
                        batKw = -1 * Math.round(Math.min(cap * 0.16, 350));
                    } else if ((h >= 6 && h <= 8) || (h >= 18 && h <= 21)) {
                        // Discharging (positive)
                        batKw = Math.round(Math.min(cap * (mode === "peak" ? 0.28 : 0.18), 500));
                    }
                }

                // 3. Load / Auxiliaries (negative)
                const loadKw = Math.max(12, Math.round(cap * 0.02));

                // 4. Net grid feed-in at NAP
                const pNap = Math.max(0, pvKw + batKw - loadKw);

                dailyPvKwh += pvKw;
                dailyNapKwh += pNap;

                // SVG coordinates
                const xBar = xStart + h * colW + (colW - barW) / 2;
                const xCenter = xStart + h * colW + colW / 2;

                // Positive bars (PV & BESS Discharge)
                const hPv = (pvKw / maxPosKw) * hPosMax;
                const yPv = yZero - hPv;

                const hBatDis = batKw > 0 ? ((batKw / maxPosKw) * hPosMax) : 0;
                const yBatDis = yPv - hBatDis;

                // Negative bars (BESS Charge & Load)
                const hBatChg = batKw < 0 ? ((Math.abs(batKw) / maxNegKw) * hNegMax) : 0;
                const hLoad = (loadKw / maxNegKw) * hNegMax;
                const yLoad = yZero + hBatChg;

                // NAP curve point
                const yNap = yZero - (pNap / maxPosKw) * hPosMax;
                napPoints.push(`${xCenter.toFixed(1)},${yNap.toFixed(1)}`);

                // SVG Bars
                // Solar PV Bar
                if (hPv > 0.5) {
                    barsHtml += `<rect x="${xBar}" y="${yPv}" width="${barW}" height="${hPv}" rx="3" fill="#f59e0b" fill-opacity="0.85" />`;
                }
                // BESS Discharge Bar
                if (hBatDis > 0.5) {
                    barsHtml += `<rect x="${xBar}" y="${yBatDis}" width="${barW}" height="${hBatDis}" rx="2" fill="#10b981" />`;
                }
                // BESS Charge Bar (downward)
                if (hBatChg > 0.5) {
                    barsHtml += `<rect x="${xBar}" y="${yZero}" width="${barW}" height="${hBatChg}" rx="2" fill="#059669" />`;
                }
                // Load Bar (downward)
                if (hLoad > 0.5) {
                    barsHtml += `<rect x="${xBar}" y="${yLoad}" width="${barW}" height="${hLoad}" rx="2" fill="#f43f5e" fill-opacity="0.8" />`;
                }

                // Interactive column overlay for hover tooltip
                const hourLabel = `${h.toString().padStart(2, '0')}:00`;
                const nextHourLabel = `${((h + 1) % 24).toString().padStart(2, '0')}:00`;
                overlayHtml += `
                    <rect x="${xStart + h * colW}" y="12" width="${colW}" height="182" fill="transparent" class="hist-col-hover"
                          style="cursor: pointer;"
                          onmouseenter="showHistTooltip(event, '${hourLabel} - ${nextHourLabel}', ${pvKw}, ${batKw}, ${loadKw}, ${pNap})"
                          onmousemove="moveHistTooltip(event)"
                          onmouseleave="hideHistTooltip()" />
                `;
            }

            // Grid lines and labels
            const gridLines = `
                <!-- Background & Border -->
                <rect x="0" y="0" width="${wTotal}" height="${hTotal}" rx="10" fill="#071320" />
                
                <!-- Zero Axis (Sammelschiene 0 kW) -->
                <line x1="${xStart}" y1="${yZero}" x2="${xEnd}" y2="${yZero}" stroke="rgba(255, 255, 255, 0.22)" stroke-width="1.2" stroke-dasharray="3 3" />
                <text x="${xStart - 6}" y="${yZero + 3}" fill="#94a3b8" font-size="8.5" font-family="'JetBrains Mono', monospace" text-anchor="end">0 kW</text>

                <!-- +100% Capacity Gridline -->
                <line x1="${xStart}" y1="${yZero - hPosMax}" x2="${xEnd}" y2="${yZero - hPosMax}" stroke="rgba(37, 199, 201, 0.12)" stroke-width="1" stroke-dasharray="2 4" />
                <text x="${xStart - 6}" y="${yZero - hPosMax + 4}" fill="#38bdf8" font-size="8" font-family="'JetBrains Mono', monospace" text-anchor="end">+${Math.round(cap)}k</text>

                <!-- +50% Capacity Gridline -->
                <line x1="${xStart}" y1="${yZero - hPosMax * 0.5}" x2="${xEnd}" y2="${yZero - hPosMax * 0.5}" stroke="rgba(255, 255, 255, 0.06)" stroke-width="1" stroke-dasharray="2 4" />
                <text x="${xStart - 6}" y="${yZero - hPosMax * 0.5 + 4}" fill="#64748b" font-size="8" font-family="'JetBrains Mono', monospace" text-anchor="end">+${Math.round(cap * 0.5)}k</text>

                <!-- Negative -Load/Charge Gridline -->
                <line x1="${xStart}" y1="${yZero + hNegMax}" x2="${xEnd}" y2="${yZero + hNegMax}" stroke="rgba(244, 63, 94, 0.15)" stroke-width="1" stroke-dasharray="2 4" />
                <text x="${xStart - 6}" y="${yZero + hNegMax + 4}" fill="#f43f5e" font-size="8" font-family="'JetBrains Mono', monospace" text-anchor="end">-${Math.round(maxNegKw)}k</text>

                <!-- X-Axis Hour Labels -->
                <text x="${xStart + 0 * colW + colW/2}" y="206" fill="#64748b" font-size="8.5" font-family="'JetBrains Mono', monospace" text-anchor="middle">00:00</text>
                <text x="${xStart + 4 * colW + colW/2}" y="206" fill="#64748b" font-size="8.5" font-family="'JetBrains Mono', monospace" text-anchor="middle">04:00</text>
                <text x="${xStart + 8 * colW + colW/2}" y="206" fill="#64748b" font-size="8.5" font-family="'JetBrains Mono', monospace" text-anchor="middle">08:00</text>
                <text x="${xStart + 12 * colW + colW/2}" y="206" fill="#64748b" font-size="8.5" font-family="'JetBrains Mono', monospace" text-anchor="middle">12:00</text>
                <text x="${xStart + 16 * colW + colW/2}" y="206" fill="#64748b" font-size="8.5" font-family="'JetBrains Mono', monospace" text-anchor="middle">16:00</text>
                <text x="${xStart + 20 * colW + colW/2}" y="206" fill="#64748b" font-size="8.5" font-family="'JetBrains Mono', monospace" text-anchor="middle">20:00</text>
                <text x="${xStart + 23 * colW + colW/2}" y="206" fill="#64748b" font-size="8.5" font-family="'JetBrains Mono', monospace" text-anchor="middle">23:00</text>
            `;

            // Current Time Marker (Jetzt)
            const xNow = xStart + currentHour * colW + colW / 2;
            const nowMarker = `
                <line x1="${xNow}" y1="18" x2="${xNow}" y2="194" stroke="#0ea5e9" stroke-width="1.8" stroke-dasharray="3 3" />
                <rect x="${xNow - 28}" y="12" width="56" height="15" rx="4" fill="#0284c7" />
                <text x="${xNow}" y="22.5" fill="#ffffff" font-size="7.8" font-weight="800" font-family="'JetBrains Mono', monospace" text-anchor="middle">JETZT · ${currentHour}:00</text>
            `;

            // Net NAP Line
            const napPolyline = `
                <polyline points="${napPoints.join(' ')}" fill="none" stroke="#25c7c9" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" filter="url(#glowCyan)" />
            `;

            svg.innerHTML = `
                <defs>
                    <filter id="glowCyan" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="2.5" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                </defs>
                ${gridLines}
                ${barsHtml}
                ${napPolyline}
                ${nowMarker}
                ${overlayHtml}
            `;
        }

        function showHistTooltip(event, timeRange, pvKw, batKw, loadKw, pNap) {
            const tip = document.getElementById("histTooltip");
            if (!tip) return;
            const batText = batKw > 0 ? `+${batKw.toLocaleString('de-DE')} kW (Entladung)` : (batKw < 0 ? `${batKw.toLocaleString('de-DE')} kW (Ladung)` : '0 kW');
            const batColor = batKw > 0 ? '#10b981' : (batKw < 0 ? '#059669' : '#94a3b8');

            tip.innerHTML = `
                <div style="font-weight: 800; color: #38bdf8; margin-bottom: 3px; font-family: var(--font-mono); border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 2px;">🕒 ${timeRange}</div>
                <div style="display: flex; justify-content: space-between; gap: 12px;"><span style="color:#fbbf24;">☀️ Solar PV:</span> <strong>+${pvKw.toLocaleString('de-DE')} kW</strong></div>
                <div style="display: flex; justify-content: space-between; gap: 12px;"><span style="color:${batColor};">🔋 BESS Speicher:</span> <strong>${batText}</strong></div>
                <div style="display: flex; justify-content: space-between; gap: 12px;"><span style="color:#f43f5e;">🏢 Last Eigenbedarf:</span> <strong>-${loadKw.toLocaleString('de-DE')} kW</strong></div>
                <div style="display: flex; justify-content: space-between; gap: 12px; border-top: 1px dashed rgba(255,255,255,0.15); margin-top: 3px; padding-top: 2px;"><span style="color:#25c7c9; font-weight:700;">🌐 Netzeinspeisung NAP:</span> <strong style="color:#25c7c9;">${pNap.toLocaleString('de-DE')} kW</strong></div>
            `;
            tip.style.display = "block";
            moveHistTooltip(event);
        }

        function moveHistTooltip(event) {
            const tip = document.getElementById("histTooltip");
            const wrap = document.getElementById("energyFlowHistogramWrap");
            if (!tip || !wrap) return;
            const wrapRect = wrap.getBoundingClientRect();
            let x = event.clientX - wrapRect.left + 12;
            let y = event.clientY - wrapRect.top - 10;
            if (x + 190 > wrapRect.width) x = event.clientX - wrapRect.left - 200;
            if (y < 0) y = 10;
            tip.style.left = `${Math.max(5, x)}px`;
            tip.style.top = `${Math.max(5, y)}px`;
        }

        function hideHistTooltip() {
            const tip = document.getElementById("histTooltip");
            if (tip) tip.style.display = "none";
        }

        let flowSimulationMode = "normal";"""

assert js_anchor in content, "js_anchor not found"
content = content.replace(js_anchor, new_js_code, 1)

# 4. Trigger histogram update when plant or simulation mode changes
old_onchange = "            applySimulationModeToState(flowSimulationMode);\n            updateEnergyFlowUI();"
new_onchange = """            applySimulationModeToState(flowSimulationMode);
            updateEnergyFlowUI();
            if (activeFlowView === "histogram") renderEnergyFlowHistogram();"""

assert old_onchange in content, "old_onchange not found"
content = content.replace(old_onchange, new_onchange, 1)

old_setsim = "            applySimulationModeToState(mode);\n            updateEnergyFlowUI();"
new_setsim = """            applySimulationModeToState(mode);
            updateEnergyFlowUI();
            if (activeFlowView === "histogram") renderEnergyFlowHistogram();"""

assert old_setsim in content, "old_setsim not found"
content = content.replace(old_setsim, new_setsim, 1)

with open('backend/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully integrated interactive 24h Energy Flow Histogram Chart into Hero Banner!")
