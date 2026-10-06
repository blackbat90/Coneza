import re

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. ADD CSS for Range Selector Pills and History Summary Header
old_css_anchor = "        /* 24h Histogram View Container */"
new_css = """        .flow-range-pills {
            display: inline-flex;
            background: rgba(255, 255, 255, 0.05);
            padding: 2px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            gap: 2px;
        }

        .flow-range-pill {
            background: transparent;
            border: none;
            color: #94a3b8;
            font-size: 0.65rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .flow-range-pill:hover {
            color: #ffffff;
            background: rgba(255, 255, 255, 0.08);
        }

        .flow-range-pill.active {
            background: #0284c7;
            color: #ffffff;
            box-shadow: 0 0 8px rgba(2, 132, 199, 0.4);
        }

        /* 24h Histogram View Container */"""

assert old_css_anchor in content, "old_css_anchor not found"
content = content.replace(old_css_anchor, new_css, 1)

# 2. UPDATE HTML: View Switcher Bar with 30-Day Range Selector and Summary Bar
old_switch_bar = """                    <!-- View Mode Switcher: Synoptischer Fluss vs. 24h Histogramm Chart -->
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
                    </div>"""

new_switch_bar = """                    <!-- View Mode Switcher: Synoptischer Fluss vs. 30-Tage Historie & Histogramm -->
                    <div class="flow-view-switch-bar">
                        <div class="flow-view-pills">
                            <button type="button" class="flow-view-pill active" id="btnFlowViewSynoptic" onclick="switchEnergyFlowView('synoptic')">
                                ⚡ Synoptischer Fluss
                            </button>
                            <button type="button" class="flow-view-pill" id="btnFlowViewHistogram" onclick="switchEnergyFlowView('histogram')">
                                📊 Histogramm &amp; Historie
                            </button>
                        </div>

                        <!-- 30-Day / 7-Day / 24h Time Range Selector -->
                        <div class="flow-range-pills" id="flowRangePills" style="display: none;">
                            <button type="button" class="flow-range-pill" id="btnRange24h" onclick="setHistogramTimeRange(1)">
                                Heute (24h)
                            </button>
                            <button type="button" class="flow-range-pill" id="btnRange7d" onclick="setHistogramTimeRange(7)">
                                7 Tage
                            </button>
                            <button type="button" class="flow-range-pill active" id="btnRange30d" onclick="setHistogramTimeRange(30)">
                                30 Tage Historie
                            </button>
                        </div>

                        <div class="flow-chart-legend" id="flowChartLegend" style="display: none;">
                            <span class="legend-item"><span class="legend-dot" style="background: #f59e0b;"></span> PV</span>
                            <span class="legend-item"><span class="legend-dot" style="background: #10b981;"></span> BESS</span>
                            <span class="legend-item"><span class="legend-dot" style="background: #f43f5e;"></span> Last</span>
                            <span class="legend-item"><span class="legend-line" style="background: #25c7c9;"></span> NAP</span>
                        </div>
                    </div>

                    <!-- 30-Day Plant Telemetry Summary Banner -->
                    <div id="histSummaryHeader" style="display: none; justify-content: space-between; align-items: center; background: rgba(8, 21, 34, 0.75); border: 1px solid rgba(37, 199, 201, 0.22); border-radius: 8px; padding: 5px 10px; margin-bottom: 6px; font-size: 0.68rem;">
                        <div style="display: flex; align-items: center; gap: 0.45rem;">
                            <span id="histPlantBadge" style="font-weight: 700; color: #38bdf8;">🌐 Gesamtflotte</span>
                            <span style="color: #64748b;">·</span>
                            <span id="histRangeBadge" style="color: #94a3b8;">Aufzeichnung letzte 30 Tage</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.75rem; font-family: var(--font-mono);">
                            <span>☀️ PV: <strong id="histSummaryPv" style="color: #fbbf24;">-- MWh</strong></span>
                            <span>🌐 Einspeisung: <strong id="histSummaryGrid" style="color: #25c7c9;">-- MWh</strong></span>
                            <span>🔋 BESS: <strong id="histSummaryBat" style="color: #34d399;">-- MWh</strong></span>
                        </div>
                    </div>"""

assert old_switch_bar in content, "old_switch_bar not found"
content = content.replace(old_switch_bar, new_switch_bar, 1)

# 3. UPDATE JAVASCRIPT: switchEnergyFlowView, setHistogramTimeRange, and renderEnergyFlowHistogram
old_js_block = """        let activeFlowView = "synoptic"; // "synoptic" | "histogram"

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

        function renderEnergyFlowHistogram() {"""

new_js_block = """        let activeFlowView = "synoptic"; // "synoptic" | "histogram"
        let selectedHistDays = 30; // 1 | 7 | 30
        let cachedEnergyHistoryData = null;

        function setHistogramTimeRange(days) {
            selectedHistDays = days;
            const btn24 = document.getElementById("btnRange24h");
            const btn7 = document.getElementById("btnRange7d");
            const btn30 = document.getElementById("btnRange30d");

            if (btn24) btn24.classList.toggle("active", days === 1);
            if (btn7) btn7.classList.toggle("active", days === 7);
            if (btn30) btn30.classList.toggle("active", days === 30);

            const rangeBadge = document.getElementById("histRangeBadge");
            if (rangeBadge) {
                if (days === 1) rangeBadge.textContent = "Heute (24-Stunden Lastgang)";
                else if (days === 7) rangeBadge.textContent = "Aufzeichnung letzte 7 Tage";
                else rangeBadge.textContent = "Aufzeichnung letzte 30 Tage";
            }

            renderEnergyFlowHistogram();
        }

        function switchEnergyFlowView(viewName) {
            activeFlowView = viewName;
            const btnSyn = document.getElementById("btnFlowViewSynoptic");
            const btnHist = document.getElementById("btnFlowViewHistogram");
            const wrapSyn = document.getElementById("energyFlowSvgWrap");
            const wrapHist = document.getElementById("energyFlowHistogramWrap");
            const legend = document.getElementById("flowChartLegend");
            const rangePills = document.getElementById("flowRangePills");
            const summaryHeader = document.getElementById("histSummaryHeader");

            if (viewName === "histogram") {
                if (btnSyn) btnSyn.classList.remove("active");
                if (btnHist) btnHist.classList.add("active");
                if (wrapSyn) wrapSyn.style.display = "none";
                if (wrapHist) wrapHist.style.display = "block";
                if (legend) legend.style.display = "flex";
                if (rangePills) rangePills.style.display = "inline-flex";
                if (summaryHeader) summaryHeader.style.display = "flex";
                renderEnergyFlowHistogram();
            } else {
                if (btnSyn) btnSyn.classList.add("active");
                if (btnHist) btnHist.classList.remove("active");
                if (wrapSyn) wrapSyn.style.display = "block";
                if (wrapHist) wrapHist.style.display = "none";
                if (legend) legend.style.display = "none";
                if (rangePills) rangePills.style.display = "none";
                if (summaryHeader) summaryHeader.style.display = "none";
            }
        }

        async function renderEnergyFlowHistogram() {"""

assert old_js_block in content, "old_js_block not found"
content = content.replace(old_js_block, new_js_block, 1)

# Now update the complete body of renderEnergyFlowHistogram()
old_render_func_pattern = r'async function renderEnergyFlowHistogram\(\) \{[\s\S]*?function showHistTooltip'

new_render_func = """async function renderEnergyFlowHistogram() {
            const svg = document.getElementById("flowHistogramSvg");
            if (!svg) return;

            const plantId = selectedFlowPlantId || "ALL";
            const days = selectedHistDays || 30;

            // Fetch live 30-day recorded telemetry history from backend
            let histData = null;
            try {
                const res = await fetch(`${API_BASE}/api/plants/${encodeURIComponent(plantId)}/energy-history?days=${days}`, {
                    headers: { "Authorization": `Bearer ${authToken}` }
                });
                if (res.ok) {
                    histData = await res.json();
                    cachedEnergyHistoryData = histData;
                }
            } catch (err) {
                console.warn("Could not fetch energy history from backend:", err);
            }

            // Fallback to local baseline calculation if offline
            const cap = histData ? histData.installed_capacity_kw : (flowBaseline.capacity_kw || 2200.0);
            const plantName = histData ? histData.plant_name : flowBaseline.name;
            const hasBess = histData ? (histData.site_type === "BESS" || histData.site_type === "HYBRID") : (flowBaseline.site_type === "BESS" || flowBaseline.site_type === "HYBRID");

            // Update Summary Header Badge
            const plantBadge = document.getElementById("histPlantBadge");
            if (plantBadge) plantBadge.textContent = `📍 ${plantName} (${(cap/1000).toFixed(2)} MWp)`;

            if (histData && histData.summary) {
                const elPv = document.getElementById("histSummaryPv");
                if (elPv) elPv.textContent = `${histData.summary.total_pv_mwh.toLocaleString('de-DE')} MWh`;
                const elGrid = document.getElementById("histSummaryGrid");
                if (elGrid) elGrid.textContent = `${histData.summary.total_grid_feedin_mwh.toLocaleString('de-DE')} MWh`;
                const elBat = document.getElementById("histSummaryBat");
                if (elBat) elBat.textContent = `${histData.summary.total_bat_throughput_mwh.toLocaleString('de-DE')} MWh`;
            }

            const wTotal = 660;
            const hTotal = 215;
            const xStart = 48;
            const xEnd = 648;
            const xPlotW = xEnd - xStart; // 600px
            const yZero = 152;
            const hPosMax = 125;
            const hNegMax = 32;

            let barsHtml = "";
            let overlayHtml = "";
            let napPoints = [];
            let xLabelsHtml = "";

            if (days === 1) {
                // ==================== 1 DAY (24-STUNDEN LASTGANG) ====================
                const hourly = (histData && histData.hourly_today && histData.hourly_today.length === 24)
                    ? histData.hourly_today
                    : Array.from({ length: 24 }, (_, h) => ({
                        hour: h,
                        pv_kw: (h >= 6 && h <= 20) ? Math.round(cap * Math.sin(((h - 6) / 14) * Math.PI) * 0.95) : 0,
                        bat_kw: (h >= 10 && h <= 14) ? -Math.round(cap * 0.15) : ((h >= 18 && h <= 21) ? Math.round(cap * 0.18) : 0),
                        load_kw: Math.max(10, Math.round(cap * 0.02)),
                        p_nap_kw: Math.max(0, Math.round(cap * 0.8))
                    }));

                const maxPosKw = Math.max(cap * 1.05, 50);
                const maxNegKw = hasBess ? Math.max(cap * 0.28, 20) : Math.max(cap * 0.08, 10);
                const colW = xPlotW / 24; // 25px
                const barW = 16;
                const currentHour = new Date().getHours() || 14;

                hourly.forEach(pt => {
                    const h = pt.hour;
                    const pvKw = pt.pv_kw || 0;
                    const batKw = pt.bat_kw || 0;
                    const loadKw = pt.load_kw || Math.max(10, Math.round(cap * 0.02));
                    const pNap = pt.p_nap_kw || Math.max(0, pvKw + batKw - loadKw);

                    const xBar = xStart + h * colW + (colW - barW) / 2;
                    const xCenter = xStart + h * colW + colW / 2;

                    const hPv = (pvKw / maxPosKw) * hPosMax;
                    const yPv = yZero - hPv;
                    const hBatDis = batKw > 0 ? ((batKw / maxPosKw) * hPosMax) : 0;
                    const yBatDis = yPv - hBatDis;

                    const hBatChg = batKw < 0 ? ((Math.abs(batKw) / maxNegKw) * hNegMax) : 0;
                    const hLoad = (loadKw / maxNegKw) * hNegMax;
                    const yLoad = yZero + hBatChg;

                    const yNap = yZero - (pNap / maxPosKw) * hPosMax;
                    napPoints.push(`${xCenter.toFixed(1)},${yNap.toFixed(1)}`);

                    if (hPv > 0.5) barsHtml += `<rect x="${xBar}" y="${yPv}" width="${barW}" height="${hPv}" rx="3" fill="#f59e0b" fill-opacity="0.9" />`;
                    if (hBatDis > 0.5) barsHtml += `<rect x="${xBar}" y="${yBatDis}" width="${barW}" height="${hBatDis}" rx="2" fill="#10b981" />`;
                    if (hBatChg > 0.5) barsHtml += `<rect x="${xBar}" y="${yZero}" width="${barW}" height="${hBatChg}" rx="2" fill="#059669" />`;
                    if (hLoad > 0.5) barsHtml += `<rect x="${xBar}" y="${yLoad}" width="${barW}" height="${hLoad}" rx="2" fill="#f43f5e" fill-opacity="0.85" />`;

                    const hourLabel = `${h.toString().padStart(2, '0')}:00`;
                    const nextHourLabel = `${((h + 1) % 24).toString().padStart(2, '0')}:00`;
                    overlayHtml += `
                        <rect x="${xStart + h * colW}" y="12" width="${colW}" height="182" fill="transparent" class="hist-col-hover"
                              style="cursor: pointer;"
                              onmouseenter="showHistTooltip(event, '${hourLabel} - ${nextHourLabel}', ${pvKw}, ${batKw}, ${loadKw}, ${pNap})"
                              onmousemove="moveHistTooltip(event)"
                              onmouseleave="hideHistTooltip()" />
                    `;
                });

                // X-Axis labels
                [0, 4, 8, 12, 16, 20, 23].forEach(h => {
                    const xC = xStart + h * colW + colW / 2;
                    xLabelsHtml += `<text x="${xC}" y="206" fill="#64748b" font-size="8.5" font-family="'JetBrains Mono', monospace" text-anchor="middle">${h.toString().padStart(2, '0')}:00</text>`;
                });

                // Now Marker
                const xNow = xStart + currentHour * colW + colW / 2;
                barsHtml += `
                    <line x1="${xNow}" y1="18" x2="${xNow}" y2="194" stroke="#0ea5e9" stroke-width="1.8" stroke-dasharray="3 3" />
                    <rect x="${xNow - 28}" y="12" width="56" height="15" rx="4" fill="#0284c7" />
                    <text x="${xNow}" y="22.5" fill="#ffffff" font-size="7.8" font-weight="800" font-family="'JetBrains Mono', monospace" text-anchor="middle">JETZT · ${currentHour}:00</text>
                `;

            } else {
                // ==================== 7 TAGE oder 30 TAGE HISTORIE ====================
                let series = (histData && histData.daily_series) ? histData.daily_series : [];
                if (series.length === 0) {
                    // Fallback generate mock days if needed
                    const countDays = days;
                    for (let d = countDays; d >= 0; d--) {
                        series.push({
                            date: `Day -${d}`,
                            label: `${d}d`,
                            pv_kwh: Math.round(cap * 4.2),
                            pv_peak_kw: Math.round(cap * 0.95),
                            bat_discharge_kwh: Math.round(cap * 0.6),
                            bat_charge_kwh: Math.round(cap * 0.65),
                            load_kwh: Math.round(cap * 0.15),
                            grid_feedin_kwh: Math.round(cap * 3.8)
                        });
                    }
                }

                // If days == 7, take last 7
                if (days === 7 && series.length > 7) {
                    series = series.slice(-7);
                }

                const n = series.length;
                const colW = xPlotW / n;
                const barW = Math.max(5, Math.min(28, colW * 0.72));

                const maxDailyPv = Math.max(...series.map(s => s.pv_kwh || 0), cap * 5.0, 100);
                const maxDailyNeg = Math.max(...series.map(s => (s.load_kwh || 0) + (s.bat_charge_kwh || 0)), cap * 1.5, 30);

                series.forEach((pt, idx) => {
                    const pvKwh = pt.pv_kwh || 0;
                    const batDis = pt.bat_discharge_kwh || 0;
                    const batChg = pt.bat_charge_kwh || 0;
                    const loadKwh = pt.load_kwh || 0;
                    const gridKwh = pt.grid_feedin_kwh || 0;

                    const xBar = xStart + idx * colW + (colW - barW) / 2;
                    const xCenter = xStart + idx * colW + colW / 2;

                    // Positive daily generation
                    const hPv = (pvKwh / maxDailyPv) * hPosMax;
                    const yPv = yZero - hPv;
                    const hBatDis = (batDis / maxDailyPv) * hPosMax;
                    const yBatDis = yPv - hBatDis;

                    // Negative daily consumption
                    const hBatChg = (batChg / maxDailyNeg) * hNegMax;
                    const hLoad = (loadKwh / maxDailyNeg) * hNegMax;
                    const yLoad = yZero + hBatChg;

                    const yGrid = yZero - (gridKwh / maxDailyPv) * hPosMax;
                    napPoints.push(`${xCenter.toFixed(1)},${yGrid.toFixed(1)}`);

                    if (hPv > 0.5) barsHtml += `<rect x="${xBar}" y="${yPv}" width="${barW}" height="${hPv}" rx="2" fill="#f59e0b" fill-opacity="0.88" />`;
                    if (hBatDis > 0.5) barsHtml += `<rect x="${xBar}" y="${yBatDis}" width="${barW}" height="${hBatDis}" rx="2" fill="#10b981" />`;
                    if (hBatChg > 0.5) barsHtml += `<rect x="${xBar}" y="${yZero}" width="${barW}" height="${hBatChg}" rx="2" fill="#059669" />`;
                    if (hLoad > 0.5) barsHtml += `<rect x="${xBar}" y="${yLoad}" width="${barW}" height="${hLoad}" rx="2" fill="#f43f5e" fill-opacity="0.8" />`;

                    // Overlay tooltip
                    const dateTitle = pt.date ? `Datum: ${pt.date}` : pt.label;
                    overlayHtml += `
                        <rect x="${xStart + idx * colW}" y="12" width="${colW}" height="182" fill="transparent" class="hist-col-hover"
                              style="cursor: pointer;"
                              onmouseenter="showHistDailyTooltip(event, '${dateTitle}', ${pvKwh}, ${batDis}, ${batChg}, ${loadKwh}, ${gridKwh})"
                              onmousemove="moveHistTooltip(event)"
                              onmouseleave="hideHistTooltip()" />
                    `;

                    // Selective labels (every N items to prevent crowding)
                    const step = days === 7 ? 1 : Math.ceil(n / 6);
                    if (idx % step === 0 || idx === n - 1) {
                        xLabelsHtml += `<text x="${xCenter}" y="206" fill="#64748b" font-size="8" font-family="'JetBrains Mono', monospace" text-anchor="middle">${pt.label}</text>`;
                    }
                });
            }

            // Gridlines & Axis labels
            const gridLines = `
                <!-- Background & Border -->
                <rect x="0" y="0" width="${wTotal}" height="${hTotal}" rx="10" fill="#071320" />
                
                <!-- Zero Axis (0 kWh / kW) -->
                <line x1="${xStart}" y1="${yZero}" x2="${xEnd}" y2="${yZero}" stroke="rgba(255, 255, 255, 0.22)" stroke-width="1.2" stroke-dasharray="3 3" />
                <text x="${xStart - 6}" y="${yZero + 3}" fill="#94a3b8" font-size="8.5" font-family="'JetBrains Mono', monospace" text-anchor="end">0</text>

                <!-- +Max Gridline -->
                <line x1="${xStart}" y1="${yZero - hPosMax}" x2="${xEnd}" y2="${yZero - hPosMax}" stroke="rgba(37, 199, 201, 0.12)" stroke-width="1" stroke-dasharray="2 4" />
                <text x="${xStart - 6}" y="${yZero - hPosMax + 4}" fill="#38bdf8" font-size="8" font-family="'JetBrains Mono', monospace" text-anchor="end">${days === 1 ? '+Max kW' : '+Max kWh'}</text>

                <!-- +50% Gridline -->
                <line x1="${xStart}" y1="${yZero - hPosMax * 0.5}" x2="${xEnd}" y2="${yZero - hPosMax * 0.5}" stroke="rgba(255, 255, 255, 0.06)" stroke-width="1" stroke-dasharray="2 4" />
                
                <!-- Negative Gridline -->
                <line x1="${xStart}" y1="${yZero + hNegMax}" x2="${xEnd}" y2="${yZero + hNegMax}" stroke="rgba(244, 63, 94, 0.15)" stroke-width="1" stroke-dasharray="2 4" />
                <text x="${xStart - 6}" y="${yZero + hNegMax + 4}" fill="#f43f5e" font-size="8" font-family="'JetBrains Mono', monospace" text-anchor="end">-Last</text>

                <!-- X-Axis Labels -->
                ${xLabelsHtml}
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
                ${overlayHtml}
            `;
        }

        function showHistDailyTooltip(event, dateLabel, pvKwh, batDisKwh, batChgKwh, loadKwh, gridKwh) {
            const tip = document.getElementById("histTooltip");
            if (!tip) return;

            tip.innerHTML = `
                <div style="font-weight: 800; color: #38bdf8; margin-bottom: 3px; font-family: var(--font-mono); border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 2px;">📅 ${dateLabel}</div>
                <div style="display: flex; justify-content: space-between; gap: 14px;"><span style="color:#fbbf24;">☀️ Solar PV Ertrag:</span> <strong>+${pvKwh.toLocaleString('de-DE')} kWh</strong></div>
                <div style="display: flex; justify-content: space-between; gap: 14px;"><span style="color:#10b981;">🔋 BESS Entladung:</span> <strong>+${batDisKwh.toLocaleString('de-DE')} kWh</strong></div>
                <div style="display: flex; justify-content: space-between; gap: 14px;"><span style="color:#059669;">🔋 BESS Ladung:</span> <strong>-${batChgKwh.toLocaleString('de-DE')} kWh</strong></div>
                <div style="display: flex; justify-content: space-between; gap: 14px;"><span style="color:#f43f5e;">🏢 Eigenbedarf Last:</span> <strong>-${loadKwh.toLocaleString('de-DE')} kWh</strong></div>
                <div style="display: flex; justify-content: space-between; gap: 14px; border-top: 1px dashed rgba(255,255,255,0.15); margin-top: 3px; padding-top: 2px;"><span style="color:#25c7c9; font-weight:700;">🌐 Netzeinspeisung NAP:</span> <strong style="color:#25c7c9;">${gridKwh.toLocaleString('de-DE')} kWh</strong></div>
            `;
            tip.style.display = "block";
            moveHistTooltip(event);
        }

        function showHistTooltip"""

content = re.sub(old_render_func_pattern, new_render_func, content)

with open('backend/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated Hero Banner with 30-Day Historical Telemetry Engine!")
