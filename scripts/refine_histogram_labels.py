with open('backend/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Y-axis label and plant name in SVG
old_svg_header = """                <!-- Zero Axis (0 kWh / kW) -->
                <line x1="${xStart}" y1="${yZero}" x2="${xEnd}" y2="${yZero}" stroke="rgba(255, 255, 255, 0.22)" stroke-width="1.2" stroke-dasharray="3 3" />
                <text x="${xStart - 6}" y="${yZero + 3}" fill="#94a3b8" font-size="8.5" font-family="'JetBrains Mono', monospace" text-anchor="end">0</text>

                <!-- +Max Gridline -->
                <line x1="${xStart}" y1="${yZero - hPosMax}" x2="${xEnd}" y2="${yZero - hPosMax}" stroke="rgba(37, 199, 201, 0.12)" stroke-width="1" stroke-dasharray="2 4" />
                <text x="${xStart - 6}" y="${yZero - hPosMax + 4}" fill="#38bdf8" font-size="8" font-family="'JetBrains Mono', monospace" text-anchor="end">${days === 1 ? '+Max kW' : '+Max kWh'}</text>"""

new_svg_header = """                <!-- Plant Identification Tag inside SVG -->
                <text x="${xStart}" y="10" fill="#38bdf8" font-size="8.5" font-weight="800" font-family="'JetBrains Mono', monospace">📍 ${plantName} (P_inst: ${cap >= 1000 ? (cap/1000).toFixed(2) + ' MWp' : Math.round(cap) + ' kW'})</text>

                <!-- Zero Axis (0 kWh / kW) -->
                <line x1="${xStart}" y1="${yZero}" x2="${xEnd}" y2="${yZero}" stroke="rgba(255, 255, 255, 0.22)" stroke-width="1.2" stroke-dasharray="3 3" />
                <text x="${xStart - 6}" y="${yZero + 3}" fill="#94a3b8" font-size="8.5" font-family="'JetBrains Mono', monospace" text-anchor="end">0</text>

                <!-- +Max Gridline with exact numeric scale -->
                <line x1="${xStart}" y1="${yZero - hPosMax}" x2="${xEnd}" y2="${yZero - hPosMax}" stroke="rgba(37, 199, 201, 0.12)" stroke-width="1" stroke-dasharray="2 4" />
                <text x="${xStart - 6}" y="${yZero - hPosMax + 4}" fill="#38bdf8" font-size="8" font-family="'JetBrains Mono', monospace" text-anchor="end">${days === 1 ? '+' + Math.round(maxPosKw).toLocaleString('de-DE') + 'k' : (maxDailyPv >= 1000 ? '+' + (maxDailyPv/1000).toFixed(1) + 'MWh' : '+' + Math.round(maxDailyPv).toLocaleString('de-DE') + 'kWh')}</text>"""

assert old_svg_header in content, "old_svg_header not found"
content = content.replace(old_svg_header, new_svg_header, 1)

with open('backend/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied SVG histogram numeric labeling refinement.")
