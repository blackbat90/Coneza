"""
Generator for realistic sample grid interconnection documents:
- E8: Technical Datasheet of Generation Plant and Battery Storage (VDE-AR-N 4110)
- E9: Grid Operator (DSO) Commissioning Protocol & Setpoints (VDE-AR-N 4110)
- SLD: Single Line Diagram / Electrical Schematic Drawing
"""

import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle

OUTPUT_DIR = os.path.dirname(__file__)

def generate_e8_datasheet():
    filename = os.path.join(OUTPUT_DIR, "sample_E8_datasheet.pdf")
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        "SubTitleStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#475569"),
        spaceAfter=20
    )

    story.append(Paragraph("VDE-AR-N 4110: Anhang E - Formular E.8", title_style))
    story.append(Paragraph("<b>Datenblatt einer Erzeugungsanlage / eines Speichers - Mittelspannung</b>", styles["Heading2"]))
    story.append(Paragraph("Projekt: Photovoltaik- und Großspeicherpark Donau-Solar GmbH | Aktenzeichen: EZA-2026-9812", subtitle_style))
    story.append(Spacer(1, 10))

    data = [
        ["Parameter", "Bezeichnung / Wert", "Einheit / Bemerkung"],
        ["Anlagenart", "Kombinierte PV-Freiflächenanlage + BESS", "Solar + LiFePO4 Speicher"],
        ["Installierte Wirkleistung (P_inst)", "2500.0", "kW"],
        ["Maximale Wirkleistung (P_max)", "2500.0", "kW"],
        ["Bemessungsscheinleistung (S_r)", "2750.0", "kVA"],
        ["Nennspannung der Anlage (U_n)", "20000", "V (20.0 kV Mittelspannung)"],
        ["Wechselrichter-Typ", "Phoenix / SMA Central Inverters", "10x Einheiten je 250 kW"],
        ["Speicherkapazität (BESS)", "1000.0", "kWh (LFP Batterie)"],
        ["Max. Lade-/Entladeleistung", "500.0", "kW"],
        ["Maschinentransformator (T1)", "3150.0", "kVA Nennleistung"],
        ["Trafo Kurzschlussspannung (u_k)", "6.0", "%"],
        ["Vektorgruppe Trafo", "Dyn5", "Sternpunkt geerdet"],
        ["Regler-Fabrikat / Typ", "Phoenix Contact EZA-Regler", "PLCnext Control / SOL-SC-PCU"],
        ["EZA-Regler Schnittstelle", "Modbus TCP (Port 502 / 5502)", "Ethernet Lichtwellenleiter"],
    ]

    t = Table(data, colWidths=[6*cm, 6.5*cm, 4.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(t)
    doc.build(story)
    print(f"Generated {filename}")

def generate_e9_commissioning():
    filename = os.path.join(OUTPUT_DIR, "sample_E9_commissioning.pdf")
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=12
    )

    story.append(Paragraph("VDE-AR-N 4110: Anhang E - Formular E.9", title_style))
    story.append(Paragraph("<b>Netzbetreiber-Abfragebogen und Inbetriebsetzungsprotokoll</b>", styles["Heading2"]))
    story.append(Paragraph("Netzbetreiber: Bayernwerk Netz GmbH | Netzanschlusspunkt: UW Donau Zelle 10", styles["Normal"]))
    story.append(Spacer(1, 15))

    data = [
        ["Netzvorgabe / Kriterium", "Vorgabewert Netzbetreiber", "Erläuterung / Normbezug"],
        ["Netznennspannung (U_n)", "20.0 kV", "Mittelspannung 50 Hz"],
        ["Max. Einspeiseleistung (P_AV)", "2400.0 kW", "Netzkapazitätsgrenze (Drosselung erforderlich)"],
        ["Blindleistungs-Regelverfahren", "Q(U)-Kennlinie", "VDE-AR-N 4110 Ziffer 10.2.2"],
        ["Q(U) Stützpunkt U1 / Q1", "U1 = 93.0 % U_n | Q1 = +100.0 % Q_max", "Maximal kapazitive Stützung"],
        ["Q(U) Stützpunkt U2 / Q2", "U2 = 97.0 % U_n | Q2 = 0.0 %", "Totband Beginn"],
        ["Q(U) Stützpunkt U3 / Q3", "U3 = 103.0 % U_n | Q3 = 0.0 %", "Totband Ende"],
        ["Q(U) Stützpunkt U4 / Q4", "U4 = 107.0 % U_n | Q4 = -100.0 % Q_max", "Maximal induktive Senkung"],
        ["Wirkleistungsgradient", "100 kW / Sekunde", "Maximale Rampenrate"],
        ["Frequenzabhängige Wirkleistung P(f)", "s = 4.0 %, f_start = 50.20 Hz", "Überfrequenz-Drosselung"],
        ["Spannungssteigerungsschutz U>", "110.0 % U_n, Auslösezeit 100 ms", "Entkupplungsschutz Q-U-Schutz"],
        ["Unterspannungsschutz U<", "80.0 % U_n, Auslösezeit 3000 ms", "Dynamische Netzstützung (FRT)"],
        ["EZA-Regelungsprotokoll", "Phoenix Contact EZA Modbus TCP", "VDE-zertifizierter EZA-Regler"],
    ]

    t = Table(data, colWidths=[6.5*cm, 5.5*cm, 5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0369a1")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#bae6fd")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f0f9ff")]),
    ]))
    story.append(t)
    doc.build(story)
    print(f"Generated {filename}")

def generate_sld_schematic():
    filename = os.path.join(OUTPUT_DIR, "sample_SLD_schematic.pdf")
    # Landscape orientation for schematic drawing
    doc = SimpleDocTemplate(filename, pagesize=landscape(A4), rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
    story = []
    styles = getSampleStyleSheet()

    story.append(Paragraph("<b>ÜBERSICHTSSCHALTPLAN (SINGLE LINE DIAGRAM - SLD)</b> - Photovoltaik & Batteriespeicher Donau-Solar", styles["Heading2"]))
    story.append(Paragraph("Norm: DIN EN 61936-1 / VDE-AR-N 4110 | Zeichnungsnummer: SLD-EZA-2026-REV3", styles["Normal"]))
    story.append(Spacer(1, 10))

    # Single Line Diagram vector schematic
    d = Drawing(780, 420)
    # Background frame
    d.add(Rect(0, 0, 780, 420, fillColor=colors.HexColor("#0f172a"), strokeColor=colors.HexColor("#334155"), strokeWidth=2))

    # Grid feeder (NAP) 20 kV
    d.add(Line(50, 350, 730, 350, strokeColor=colors.HexColor("#38bdf8"), strokeWidth=3))
    d.add(String(60, 360, "20 kV Mittelspannungssammelschiene (NAP Übergabestation Bayernwerk)", fontSize=11, fillColor=colors.HexColor("#e2e8f0")))

    # Circuit Breaker Q0
    d.add(Rect(120, 290, 40, 30, fillColor=colors.HexColor("#ef4444"), strokeColor=colors.white))
    d.add(String(125, 300, "Q0", fontSize=12, fillColor=colors.white))
    d.add(Line(140, 350, 140, 320, strokeColor=colors.HexColor("#38bdf8"), strokeWidth=2))
    d.add(Line(140, 290, 140, 260, strokeColor=colors.HexColor("#38bdf8"), strokeWidth=2))
    d.add(String(170, 300, "Leistungsschalter Q0 (Hauptschalter)", fontSize=9, fillColor=colors.HexColor("#94a3b8")))

    # Transformer T1
    d.add(Circle(140, 235, 20, fillColor=None, strokeColor=colors.HexColor("#f59e0b"), strokeWidth=2))
    d.add(Circle(140, 210, 20, fillColor=None, strokeColor=colors.HexColor("#f59e0b"), strokeWidth=2))
    d.add(Line(140, 260, 140, 255, strokeColor=colors.HexColor("#38bdf8"), strokeWidth=2))
    d.add(Line(140, 190, 140, 160, strokeColor=colors.HexColor("#10b981"), strokeWidth=2))
    d.add(String(170, 220, "Transformator T1: 3150 kVA, 20 kV / 0.4 kV, uk = 6.0%", fontSize=10, fillColor=colors.HexColor("#f59e0b")))

    # Low Voltage 400 V Busbar
    d.add(Line(50, 160, 730, 160, strokeColor=colors.HexColor("#10b981"), strokeWidth=3))
    d.add(String(60, 145, "0.4 kV Niederspannungssammelschiene (Generatorfeld)", fontSize=11, fillColor=colors.HexColor("#e2e8f0")))

    # Inverter feeders WR1..WR10
    inverter_x_positions = [80, 180, 280, 380, 480, 580]
    for i, x in enumerate(inverter_x_positions):
        # Breaker
        d.add(Rect(x - 15, 100, 30, 20, fillColor=colors.HexColor("#1e293b"), strokeColor=colors.HexColor("#10b981")))
        d.add(String(x - 10, 106, f"Q{i+1}", fontSize=8, fillColor=colors.white))
        d.add(Line(x, 160, x, 120, strokeColor=colors.HexColor("#10b981"), strokeWidth=1.5))
        d.add(Line(x, 100, x, 70, strokeColor=colors.HexColor("#10b981"), strokeWidth=1.5))
        # Inverter box
        d.add(Rect(x - 25, 30, 50, 40, fillColor=colors.HexColor("#1e293b"), strokeColor=colors.HexColor("#38bdf8")))
        d.add(String(x - 20, 52, f"WR {i+1}", fontSize=9, fillColor=colors.HexColor("#38bdf8")))
        d.add(String(x - 22, 38, "250 kW", fontSize=8, fillColor=colors.HexColor("#94a3b8")))

    # Battery Storage Inverter BESS 1
    d.add(Rect(670 - 15, 100, 30, 20, fillColor=colors.HexColor("#1e293b"), strokeColor=colors.HexColor("#ec4899")))
    d.add(String(665, 106, "QB", fontSize=8, fillColor=colors.white))
    d.add(Line(670, 160, 670, 120, strokeColor=colors.HexColor("#10b981"), strokeWidth=1.5))
    d.add(Line(670, 100, 670, 70, strokeColor=colors.HexColor("#10b981"), strokeWidth=1.5))
    d.add(Rect(645, 30, 55, 40, fillColor=colors.HexColor("#831843"), strokeColor=colors.HexColor("#f472b6")))
    d.add(String(650, 52, "BESS 1", fontSize=9, fillColor=colors.white))
    d.add(String(648, 38, "500 kW", fontSize=8, fillColor=colors.HexColor("#fbcfe8")))

    # Phoenix Contact EZA Controller integration box
    d.add(Rect(520, 230, 220, 95, fillColor=colors.HexColor("#1e1b4b"), strokeColor=colors.HexColor("#6366f1"), strokeWidth=2))
    d.add(String(530, 305, "Phoenix Contact EZA-Regler", fontSize=12, fillColor=colors.HexColor("#a5b4fc")))
    d.add(String(530, 290, "PLCnext SOL-SC-PCU / VDE 4110", fontSize=9, fillColor=colors.HexColor("#c7d2fe")))
    d.add(String(530, 275, "Kommunikation: Modbus TCP (Port 5502)", fontSize=8.5, fillColor=colors.HexColor("#e0e7ff")))
    d.add(String(530, 260, "Messabgriff: Wandler NAP (U, I, P, Q)", fontSize=8.5, fillColor=colors.HexColor("#e0e7ff")))
    d.add(String(530, 245, "Regelpfad: Q(U) & P(f) Drosselung", fontSize=8.5, fillColor=colors.HexColor("#e0e7ff")))

    # Measurement tap dashed line to NAP
    d.add(Line(520, 280, 230, 280, strokeColor=colors.HexColor("#6366f1"), strokeWidth=1.5))
    d.add(Line(230, 280, 230, 350, strokeColor=colors.HexColor("#6366f1"), strokeWidth=1.5))
    d.add(Circle(230, 350, 4, fillColor=colors.HexColor("#6366f1"), strokeColor=colors.white))

    story.append(d)
    doc.build(story)
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_e8_datasheet()
    generate_e9_commissioning()
    generate_sld_schematic()
