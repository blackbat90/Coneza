# -*- coding: utf-8 -*-
"""
Integrates:
1. Reliable plant selection update for the Histogram & Energy Flow.
2. Day-by-Day (Tagesweise) Histogram navigation with Left (‹) and Right (›) arrows directly on the histogram.
3. 24h hourly profile for any selected day from the 30-day history with full telemetry.
4. Synchronization when a plant is selected in the Hero dropdown, plant cards, or plant detail modal.
"""

with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. ADD CSS FOR ARROWS & TODAY PILL
old_css_anchor = ".energy-flow-histogram-svg {"
new_css = """        /* Direct Histogram Day-by-Day Navigation Arrows (Links & Rechts) */
        .hist-nav-arrow {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            width: 34px;
            height: 48px;
            background: rgba(8, 21, 34, 0.88);
            border: 1.5px solid rgba(37, 199, 201, 0.45);
            color: #38bdf8;
            border-radius: 8px;
            font-size: 1.85rem;
            font-weight: 700;
            line-height: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 15;
            backdrop-filter: blur(6px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.55);
            padding: 0;
            user-select: none;
            outline: none;
        }
        .hist-nav-arrow:hover:not(:disabled) {
            background: rgba(37, 199, 201, 0.28);
            border-color: #25c7c9;
            color: #ffffff;
            box-shadow: 0 0 18px rgba(37, 199, 201, 0.6);
            transform: translateY(-50%) scale(1.1);
        }
        .hist-nav-arrow:active:not(:disabled) {
            transform: translateY(-50%) scale(0.96);
        }
        .hist-nav-arrow:disabled {
            opacity: 0.2;
            cursor: not-allowed;
            border-color: rgba(255, 255, 255, 0.1);
            color: #64748b;
            box-shadow: none;
        }
        .hist-nav-arrow-left {
            left: 8px;
        }
        .hist-nav-arrow-right {
            right: 8px;
        }
        .btn-today-pill {
            background: rgba(2, 132, 199, 0.25);
            border: 1px solid rgba(2, 132, 199, 0.5);
            color: #38bdf8;
            font-size: 0.65rem;
            font-weight: 700;
            padding: 1px 7px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .btn-today-pill:hover {
            background: #0284c7;
            color: #ffffff;
        }

        .energy-flow-histogram-svg {"""

if ".hist-nav-arrow" not in content:
    content = content.replace(old_css_anchor, new_css, 1)

# 2. UPDATE HTML: Range pills and histogram wrap with navigation arrows
old_html_wrap = """                    <!-- View 2: Interactive 24h Energy Flow Histogram & Time-Series Graph -->
                    <div class="energy-flow-histogram-wrap" id="energyFlowHistogramWrap" style="display: none;">
                        <svg viewBox="0 0 660 215" class="energy-flow-histogram-svg" id="flowHistogramSvg" xmlns="http://www.w3.org/2000/svg">
                            <!-- Populated dynamically via renderEnergyFlowHistogram() -->
                        </svg>
                        <div id="histTooltip" class="hist-tooltip"></div>
                    </div>"""

new_html_wrap = """                    <!-- View 2: Interactive Energy Flow Histogram & Time-Series Graph mit Tages-Pfeilen -->
                    <div class="energy-flow-histogram-wrap" id="energyFlowHistogramWrap" style="display: none;">
                        <!-- Day Navigation Arrows Directly on Left and Right of Histogram -->
                        <button type="button" class="hist-nav-arrow hist-nav-arrow-left" id="btnHistArrowLeft" onclick="stepHistogramDay(-1)" title="Vorheriger Tag (1 Tag zurück)">
                            ‹
                        </button>
                        <button type="button" class="hist-nav-arrow hist-nav-arrow-right" id="btnHistArrowRight" onclick="stepHistogramDay(1)" title="Nächster Tag (1 Tag vor)">
                            ›
                        </button>

                        <svg viewBox="0 0 660 215" class="energy-flow-histogram-svg" id="flowHistogramSvg" xmlns="http://www.w3.org/2000/svg">
                            <!-- Populated dynamically via renderEnergyFlowHistogram() -->
                        </svg>
                        <div id="histTooltip" class="hist-tooltip"></div>
                    </div>"""

if "btnHistArrowLeft" not in content:
    content = content.replace(old_html_wrap, new_html_wrap, 1)

# Update pill text to emphasize Day-by-Day view
old_range_pill_btn = """                            <button type="button" class="flow-range-pill" id="btnRange24h" onclick="setHistogramTimeRange(1)">
                                Heute (24h)
                            </button>"""
new_range_pill_btn = """                            <button type="button" class="flow-range-pill" id="btnRange24h" onclick="setHistogramTimeRange(1)">
                                📅 Tag für Tag (24h)
                            </button>"""
if old_range_pill_btn in content:
    content = content.replace(old_range_pill_btn, new_range_pill_btn, 1)

# Update summary header badge to include Heute reset pill
old_summary_badge = """                            <span id="histPlantBadge" style="font-weight: 700; color: #38bdf8;">🌐 Gesamtflotte</span>
                            <span style="color: #64748b;">·</span>
                            <span id="histRangeBadge" style="color: #94a3b8;">Aufzeichnung letzte 30 Tage</span>"""
new_summary_badge = """                            <span id="histPlantBadge" style="font-weight: 700; color: #38bdf8;">🌐 Gesamtflotte</span>
                            <span style="color: #64748b;">·</span>
                            <span id="histRangeBadge" style="color: #94a3b8;">Aufzeichnung letzte 30 Tage</span>
                            <button type="button" id="btnHistJumpToday" class="btn-today-pill" onclick="jumpHistogramToToday()" style="display: none;">Heute ↺</button>"""
if old_summary_badge in content:
    content = content.replace(old_summary_badge, new_summary_badge, 1)

# 3. UPDATE OPENPLANTDETAIL to synchronize onEnergyFlowPlantChange
old_open_detail = """        async function openPlantDetail(plantId) {
            activePlantId = plantId;"""
new_open_detail = """        async function openPlantDetail(plantId) {
            activePlantId = plantId;
            try { onEnergyFlowPlantChange(plantId); } catch (e) {}"""
if old_open_detail in content and "try { onEnergyFlowPlantChange(plantId); }" not in content:
    content = content.replace(old_open_detail, new_open_detail, 1)

# 4. REWRITE EZA JAVASCRIPT BLOCK
anchor_start = '// ----------------- EZA Energy Flow & Controller Physics Engine (Plant-Selectable) ----------------- //'
anchor_end = 'function populateEnergyFlowPlantSelect()'

pos1 = content.find(anchor_start)
pos2 = content.find(anchor_end)

if pos1 == -1 or pos2 == -1:
    print(f"Error finding anchors: pos1={pos1}, pos2={pos2}")
    exit(1)

new_eza_js = """// ----------------- EZA Energy Flow & Controller Physics Engine (Plant-Selectable) ----------------- //
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

        let activeFlowView = "synoptic"; // "synoptic" | "histogram"
        let selectedHistDays = 30; // 1 | 7 | 30
        let cachedEnergyHistoryData = null;
        let histSelectedDateOffset = 0; // 0 = today, 1 = yesterday, ... up to 30
        let histAvailableDates = []; // List of YYYY-MM-DD from backend
        let histCurrentDateStr = null;

        function setHistogramTimeRange(days) {
            selectedHistDays = days;
            const btn24 = document.getElementById("btnRange24h");
            const btn7 = document.getElementById("btnRange7d");
            const btn30 = document.getElementById("btnRange30d");

            if (btn24) btn24.classList.toggle("active", days === 1);
            if (btn7) btn7.classList.toggle("active", days === 7);
            if (btn30) btn30.classList.toggle("active", days === 30);

            updateDayNavigationArrows();
            renderEnergyFlowHistogram();
        }

        function stepHistogramDay(step) {
            // step = -1 -> 1 day back into past (increase offset)
            // step = +1 -> 1 day forward toward today (decrease offset)
            if (selectedHistDays !== 1) {
                selectedHistDays = 1;
                const btn24 = document.getElementById("btnRange24h");
                const btn7 = document.getElementById("btnRange7d");
                const btn30 = document.getElementById("btnRange30d");
                if (btn24) btn24.classList.add("active");
                if (btn7) btn7.classList.remove("active");
                if (btn30) btn30.classList.remove("active");
            }

            if (step < 0) {
                histSelectedDateOffset = Math.min(30, histSelectedDateOffset + 1);
            } else {
                histSelectedDateOffset = Math.max(0, histSelectedDateOffset - 1);
            }

            updateDayNavigationArrows();
            renderEnergyFlowHistogram();
        }

        function jumpHistogramToToday() {
            histSelectedDateOffset = 0;
            updateDayNavigationArrows();
            renderEnergyFlowHistogram();
        }

        function drillIntoHistogramDay(dateStr) {
            if (!dateStr) return;
            selectedHistDays = 1;
            const btn24 = document.getElementById("btnRange24h");
            const btn7 = document.getElementById("btnRange7d");
            const btn30 = document.getElementById("btnRange30d");
            if (btn24) btn24.classList.add("active");
            if (btn7) btn7.classList.remove("active");
            if (btn30) btn30.classList.remove("active");

            // Find offset from today
            if (histAvailableDates && histAvailableDates.length > 0) {
                const idx = histAvailableDates.indexOf(dateStr);
                if (idx !== -1) {
                    histSelectedDateOffset = Math.max(0, histAvailableDates.length - 1 - idx);
                }
            }
            histCurrentDateStr = dateStr;
            updateDayNavigationArrows();
            renderEnergyFlowHistogram();
        }

        function updateDayNavigationArrows() {
            const btnLeft = document.getElementById("btnHistArrowLeft");
            const btnRight = document.getElementById("btnHistArrowRight");
            const btnJump = document.getElementById("btnHistJumpToday");

            if (btnLeft) {
                btnLeft.disabled = (histSelectedDateOffset >= 30);
                btnLeft.style.opacity = (selectedHistDays === 1) ? "1" : "0.75";
                btnLeft.title = `Vorheriger Tag (${histSelectedDateOffset + 1} Tage zurück)`;
            }
            if (btnRight) {
                btnRight.disabled = (histSelectedDateOffset <= 0);
                btnRight.style.opacity = (selectedHistDays === 1) ? "1" : "0.75";
                btnRight.title = histSelectedDateOffset > 0 ? "Nächster Tag (Vorwärts)" : "Bereits auf aktuellem Tag (Heute)";
            }
            if (btnJump) {
                btnJump.style.display = (selectedHistDays === 1 && histSelectedDateOffset > 0) ? "inline-block" : "none";
            }
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
                updateDayNavigationArrows();
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

        function drawEnergyFlowHistogramSvg(histData, days, plantId) {
            const svg = document.getElementById("flowHistogramSvg");
            if (!svg) return;

            try {
                const cap = histData ? (Number(histData.installed_capacity_kw) || 2200.0) : ((flowBaseline && flowBaseline.capacity_kw) || 2200.0);
                const plantName = histData ? (histData.plant_name || "Anlage") : ((flowBaseline && flowBaseline.name) || "Gesamtflotte");
                const siteType = histData ? histData.site_type : ((flowBaseline && flowBaseline.site_type) || "HYBRID");
                const hasBess = (siteType === "BESS" || siteType === "HYBRID");

                // Update Summary Header Badge & Plant Tag
                const plantBadge = document.getElementById("histPlantBadge");
                if (plantBadge) plantBadge.textContent = `📍 ${plantName} (${(cap/1000).toFixed(2)} MWp)`;

                const rangeBadge = document.getElementById("histRangeBadge");
                if (rangeBadge) {
                    if (days === 1) {
                        const dateLabel = (histData && histData.selected_date_label) ? histData.selected_date_label : (histSelectedDateOffset === 0 ? "Heute (24-Stunden Lastgang)" : `Tag -${histSelectedDateOffset}`);
                        rangeBadge.textContent = `📅 ${dateLabel}`;
                    } else if (days === 7) {
                        rangeBadge.textContent = "Aufzeichnung letzte 7 Tage";
                    } else {
                        rangeBadge.textContent = "Aufzeichnung letzte 30 Tage";
                    }
                }

                // Update Summary KPIs (for days === 1, use that day's totals; for 7/30d use range totals)
                const elPv = document.getElementById("histSummaryPv");
                const elGrid = document.getElementById("histSummaryGrid");
                const elBat = document.getElementById("histSummaryBat");

                if (days === 1 && histData && histData.day_summary) {
                    if (elPv) elPv.textContent = `${Number(histData.day_summary.total_pv_kwh || 0).toLocaleString('de-DE')} kWh`;
                    if (elGrid) elGrid.textContent = `${Number(histData.day_summary.total_grid_feedin_kwh || 0).toLocaleString('de-DE')} kWh`;
                    if (elBat) elBat.textContent = `${Number(histData.day_summary.total_bat_throughput_kwh || 0).toLocaleString('de-DE')} kWh`;
                } else if (histData && histData.summary) {
                    if (elPv) elPv.textContent = `${Number(histData.summary.total_pv_mwh || 0).toLocaleString('de-DE')} MWh`;
                    if (elGrid) elGrid.textContent = `${Number(histData.summary.total_grid_feedin_mwh || 0).toLocaleString('de-DE')} MWh`;
                    if (elBat) elBat.textContent = `${Number(histData.summary.total_bat_throughput_mwh || 0).toLocaleString('de-DE')} MWh`;
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
                let maxScaleLabel = "+2.200 kW";

                if (days === 1) {
                    // ==================== 1 DAY (24-STUNDEN LASTGANG FÜR GEWÄHLTEN TAG) ====================
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
                    maxScaleLabel = `+${Math.round(maxPosKw).toLocaleString('de-DE')} kW`;

                    const colW = xPlotW / 24; // 25px
                    const barW = 16;
                    const isTodayView = (!histData || histData.is_today || histSelectedDateOffset === 0);
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

                    // Current Time Marker (Only shown on Today)
                    if (isTodayView) {
                        const xNow = xStart + currentHour * colW + colW / 2;
                        barsHtml += `
                            <line x1="${xNow}" y1="18" x2="${xNow}" y2="194" stroke="#0ea5e9" stroke-width="1.8" stroke-dasharray="3 3" />
                            <rect x="${xNow - 28}" y="12" width="56" height="15" rx="4" fill="#0284c7" />
                            <text x="${xNow}" y="22.5" fill="#ffffff" font-size="7.8" font-weight="800" font-family="'JetBrains Mono', monospace" text-anchor="middle">JETZT · ${currentHour}:00</text>
                        `;
                    } else {
                        // Tag-Badge oben links im Diagramm
                        const dateBadgeText = (histData && histData.selected_date_label) ? histData.selected_date_label : `Tag -${histSelectedDateOffset}`;
                        barsHtml += `
                            <rect x="${xStart}" y="14" width="160" height="17" rx="4" fill="rgba(2, 132, 199, 0.3)" stroke="#0284c7" stroke-width="1" />
                            <text x="${xStart + 8}" y="25.5" fill="#38bdf8" font-size="8.2" font-weight="800" font-family="'JetBrains Mono', monospace">📅 ${dateBadgeText}</text>
                        `;
                    }

                } else {
                    // ==================== 7 TAGE oder 30 TAGE HISTORIE ====================
                    let series = (histData && histData.daily_series) ? histData.daily_series : [];
                    if (series.length === 0) {
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

                    if (days === 7 && series.length > 7) {
                        series = series.slice(-7);
                    }

                    const n = series.length;
                    const colW = xPlotW / n;
                    const barW = Math.max(5, Math.min(28, colW * 0.72));

                    const maxDailyPv = Math.max(...series.map(s => Number(s.pv_kwh) || 0), cap * 5.0, 100);
                    const maxDailyNeg = Math.max(...series.map(s => (Number(s.load_kwh) || 0) + (Number(s.bat_charge_kwh) || 0)), cap * 1.5, 30);
                    maxScaleLabel = maxDailyPv >= 1000 ? `+${(maxDailyPv/1000).toFixed(1)} MWh` : `+${Math.round(maxDailyPv).toLocaleString('de-DE')} kWh`;

                    series.forEach((pt, idx) => {
                        const pvKwh = Number(pt.pv_kwh) || 0;
                        const batDis = Number(pt.bat_discharge_kwh) || 0;
                        const batChg = Number(pt.bat_charge_kwh) || 0;
                        const loadKwh = Number(pt.load_kwh) || 0;
                        const gridKwh = Number(pt.grid_feedin_kwh) || 0;

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

                        // Overlay tooltip + click to drill into 24h day-view
                        const dateTitle = pt.date ? `Datum: ${pt.date}` : pt.label;
                        overlayHtml += `
                            <rect x="${xStart + idx * colW}" y="12" width="${colW}" height="182" fill="transparent" class="hist-col-hover"
                                  style="cursor: pointer;"
                                  onclick="drillIntoHistogramDay('${pt.date}')"
                                  onmouseenter="showHistDailyTooltip(event, '${dateTitle}', ${pvKwh}, ${batDis}, ${batChg}, ${loadKwh}, ${gridKwh})"
                                  onmousemove="moveHistTooltip(event)"
                                  onmouseleave="hideHistTooltip()" />
                        `;

                        // Selective labels
                        const step = days === 7 ? 1 : Math.ceil(n / 6);
                        if (idx % step === 0 || idx === n - 1) {
                            xLabelsHtml += `<text x="${xCenter}" y="206" fill="#64748b" font-size="8" font-family="'JetBrains Mono', monospace" text-anchor="middle">${pt.label}</text>`;
                        }
                    });
                }

                // Gridlines & Axis labels
                const dayTagText = (days === 1 && histData && histData.selected_date_label) ? ` · ${histData.selected_date_label}` : '';
                const gridLines = `
                    <!-- Background & Border -->
                    <rect x="0" y="0" width="${wTotal}" height="${hTotal}" rx="10" fill="#071320" />
                    
                    <!-- Plant Identification Tag inside SVG -->
                    <text x="${xStart}" y="10" fill="#38bdf8" font-size="8.5" font-weight="800" font-family="'JetBrains Mono', monospace">📍 ${plantName}${dayTagText} (P_inst: ${cap >= 1000 ? (cap/1000).toFixed(2) + ' MWp' : Math.round(cap) + ' kW'})</text>

                    <!-- Zero Axis (0 kWh / kW) -->
                    <line x1="${xStart}" y1="${yZero}" x2="${xEnd}" y2="${yZero}" stroke="rgba(255, 255, 255, 0.22)" stroke-width="1.2" stroke-dasharray="3 3" />
                    <text x="${xStart - 6}" y="${yZero + 3}" fill="#94a3b8" font-size="8.5" font-family="'JetBrains Mono', monospace" text-anchor="end">0</text>

                    <!-- +Max Gridline with exact numeric scale -->
                    <line x1="${xStart}" y1="${yZero - hPosMax}" x2="${xEnd}" y2="${yZero - hPosMax}" stroke="rgba(37, 199, 201, 0.12)" stroke-width="1" stroke-dasharray="2 4" />
                    <text x="${xStart - 6}" y="${yZero - hPosMax + 4}" fill="#38bdf8" font-size="8" font-family="'JetBrains Mono', monospace" text-anchor="end">${maxScaleLabel}</text>

                    <!-- +50% Gridline -->
                    <line x1="${xStart}" y1="${yZero - hPosMax * 0.5}" x2="${xEnd}" y2="${yZero - hPosMax * 0.5}" stroke="rgba(255, 255, 255, 0.06)" stroke-width="1" stroke-dasharray="2 4" />
                    
                    <!-- Negative Gridline -->
                    <line x1="${xStart}" y1="${yZero + hNegMax}" x2="${xEnd}" y2="${yZero + hNegMax}" stroke="rgba(244, 63, 94, 0.15)" stroke-width="1" stroke-dasharray="2 4" />
                    <text x="${xStart - 6}" y="${yZero + hNegMax + 4}" fill="#f43f5e" font-size="8" font-family="'JetBrains Mono', monospace" text-anchor="end">-Last</text>

                    <!-- X-Axis Labels -->
                    ${xLabelsHtml}
                `;

                // Net NAP Line
                const napPolyline = napPoints.length > 0 ? `
                    <polyline points="${napPoints.join(' ')}" fill="none" stroke="#25c7c9" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" filter="url(#glowCyan)" />
                ` : '';

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
            } catch (err) {
                console.error("Error drawing energy flow histogram:", err);
            }
        }

        async function renderEnergyFlowHistogram() {
            const svg = document.getElementById("flowHistogramSvg");
            if (!svg) return;

            const plantId = selectedFlowPlantId || "ALL";
            const days = selectedHistDays || 30;

            // Compute target date string if browsing day-by-day
            let targetDate = null;
            if (days === 1) {
                if (histAvailableDates && histAvailableDates.length > 0) {
                    const idx = Math.max(0, histAvailableDates.length - 1 - histSelectedDateOffset);
                    targetDate = histAvailableDates[idx];
                }
            }

            // 1. Instant-render cached or baseline state so user never sees a blank screen
            if (cachedEnergyHistoryData && cachedEnergyHistoryData.plant_id === plantId && cachedEnergyHistoryData.days === days && (!targetDate || cachedEnergyHistoryData.selected_date === targetDate)) {
                drawEnergyFlowHistogramSvg(cachedEnergyHistoryData, days, plantId);
            } else {
                drawEnergyFlowHistogramSvg(null, days, plantId);
            }

            // 2. Fetch live telemetry history asynchronously from backend
            try {
                const headers = (typeof authToken !== "undefined" && authToken) ? { "Authorization": `Bearer ${authToken}` } : {};
                let fetchUrl = `${API_BASE}/api/plants/${encodeURIComponent(plantId)}/energy-history?days=${days}`;
                if (days === 1 && targetDate) {
                    fetchUrl += `&date=${encodeURIComponent(targetDate)}`;
                }

                const res = await fetch(fetchUrl, { headers: headers });
                if (res.ok) {
                    const data = await res.json();
                    cachedEnergyHistoryData = data;
                    if (data.available_dates && data.available_dates.length > 0) {
                        histAvailableDates = data.available_dates;
                    }
                    if (data.selected_date) {
                        histCurrentDateStr = data.selected_date;
                    }

                    updateDayNavigationArrows();

                    // Re-render with freshly received telemetry data
                    if ((selectedFlowPlantId || "ALL") === plantId && selectedHistDays === days) {
                        drawEnergyFlowHistogramSvg(data, days, plantId);
                    }
                }
            } catch (err) {
                console.warn("Could not fetch energy history from backend:", err);
            }
        }

        function showHistDailyTooltip(event, dateLabel, pvKwh, batDisKwh, batChgKwh, loadKwh, gridKwh) {
            const tip = document.getElementById("histTooltip");
            if (!tip) return;

            tip.innerHTML = `
                <div style="font-weight: 800; color: #38bdf8; margin-bottom: 3px; font-family: var(--font-mono); border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 2px;">📅 ${dateLabel} <span style="font-size: 0.65rem; color:#94a3b8; font-weight: normal;">(Klick für 24h)</span></div>
                <div style="display: flex; justify-content: space-between; gap: 14px;"><span style="color:#fbbf24;">☀️ Solar PV Ertrag:</span> <strong>+${pvKwh.toLocaleString('de-DE')} kWh</strong></div>
                <div style="display: flex; justify-content: space-between; gap: 14px;"><span style="color:#10b981;">🔋 BESS Entladung:</span> <strong>+${batDisKwh.toLocaleString('de-DE')} kWh</strong></div>
                <div style="display: flex; justify-content: space-between; gap: 14px;"><span style="color:#059669;">🔋 BESS Ladung:</span> <strong>-${batChgKwh.toLocaleString('de-DE')} kWh</strong></div>
                <div style="display: flex; justify-content: space-between; gap: 14px;"><span style="color:#f43f5e;">🏢 Eigenbedarf Last:</span> <strong>-${loadKwh.toLocaleString('de-DE')} kWh</strong></div>
                <div style="display: flex; justify-content: space-between; gap: 14px; border-top: 1px dashed rgba(255,255,255,0.15); margin-top: 3px; padding-top: 2px;"><span style="color:#25c7c9; font-weight:700;">🌐 Netzeinspeisung NAP:</span> <strong style="color:#25c7c9;">${gridKwh.toLocaleString('de-DE')} kWh</strong></div>
            `;
            tip.style.display = "block";
            moveHistTooltip(event);
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

        """

# 5. UPDATE onEnergyFlowPlantChange to ALWAYS update histogram and clear cached data
old_plant_change_func = """        function onEnergyFlowPlantChange(plantId) {
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
            if (activeFlowView === "histogram") renderEnergyFlowHistogram();
        }"""

new_plant_change_func = """        function onEnergyFlowPlantChange(plantId) {
            selectedFlowPlantId = plantId;
            const select = document.getElementById("flowPlantSelect");
            if (select && select.value !== plantId) select.value = plantId;

            // Clear old plant data so fresh telemetry is loaded immediately
            cachedEnergyHistoryData = null;
            histSelectedDateOffset = 0; // Reset day offset to today

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
                const plant = (cachedPlants || []).find(p => p.id === plantId);
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
                } else {
                    flowBaseline = {
                        name: `Anlage (${plantId})`,
                        capacity_kw: 2200.0,
                        voltage_kv: 20.0,
                        grid_operator: "Verteilnetzbetreiber",
                        site_type: "HYBRID",
                        status: "ONLINE_REGULATING"
                    };
                }
            }

            // Recalculate simulation state based on baseline
            applySimulationModeToState(flowSimulationMode);
            updateEnergyFlowUI();

            // ALWAYS trigger histogram update when plant changes
            renderEnergyFlowHistogram();
        }"""

# Apply JS replacement
content = content[:pos1] + new_eza_js + content[pos2:]

# Apply onEnergyFlowPlantChange replacement
if old_plant_change_func in content:
    content = content.replace(old_plant_change_func, new_plant_change_func, 1)

with open('backend/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully integrated day-by-day histogram navigation and plant selection updates! Total length: {len(content)}")
