import sys
import os

os.environ["CONFLUENCE_URL"] = "https://easy-eza.atlassian.net"
os.environ["CONFLUENCE_EMAIL"] = "ai@coneza.de"
os.environ["CONFLUENCE_API_TOKEN"] = "ATATT3xFfGF05_fgVzliBg1c2BDNAkiwXofBHyXLaxlcHKLtuPQliOiPRp53-VwGMWNhM4pE-5UBViz7nubtFxr2DI1hB6jDjcKI7674MAcaPRqTB0s2FW0rAF_nWgMfOMvtncV55rWozJLORUga6lG7xZxh8nbwiF6BPyYRzLBrjYF0kdMGzdc=3ECDA8D7"
os.environ["CONFLUENCE_SPACE"] = "EEPD"

sys.path.insert(0, ".")
from backend.confluence_service import confluence_service

hardware_doc_html = """
<h2>EZA-Regler &amp; VDE-AR-N 4110 Spezifikation</h2>
<p>Dokumentiert die Schnittstellen und Regelungsparameter des Coneza EZA-Portals zur Steuerung von Erzeugungsanlagen (EZ) am Mittel- und Hochspannungsnetz.</p>

<h3>1. Unterstützte Controller-Hardware</h3>
<ul>
  <li><strong>Phoenix Contact RFC 4072S:</strong> High-Performance Safety-SPS für zentrale Netzregelung nach VDE-AR-N 4110</li>
  <li><strong>Phoenix Contact AXC F 2152 / 3152:</strong> PLCnext Controller für Edge-Telemetrie und Modbus TCP Gateway</li>
</ul>

<h3>2. Kommunikationsschnittstellen &amp; Registerbelegung (Modbus TCP)</h3>
<table border="1" cellpadding="6" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background-color: #f3f4f6;">
      <th>Modbus Register</th>
      <th>Signalname</th>
      <th>Einheit</th>
      <th>Typ</th>
      <th>Funktion</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>30001</td><td>Grid_Voltage_L1_N</td><td>V</td><td>Float32</td><td>Effektivspannung Außenleiter L1</td></tr>
    <tr><td>30003</td><td>Grid_Voltage_L2_N</td><td>V</td><td>Float32</td><td>Effektivspannung Außenleiter L2</td></tr>
    <tr><td>30005</td><td>Grid_Voltage_L3_N</td><td>V</td><td>Float32</td><td>Effektivspannung Außenleiter L3</td></tr>
    <tr><td>30007</td><td>Grid_Frequency</td><td>Hz</td><td>Float32</td><td>Netzfrequenz (Nennwert 50,00 Hz)</td></tr>
    <tr><td>30009</td><td>Active_Power_P</td><td>kW</td><td>Float32</td><td>Gesamte Wirkleistung am Netzverknüpfungspunkt (NAP)</td></tr>
    <tr><td>30011</td><td>Reactive_Power_Q</td><td>kvar</td><td>Float32</td><td>Gesamte Blindleistung am NAP</td></tr>
    <tr><td>30013</td><td>Power_Factor_cosPhi</td><td>-</td><td>Float32</td><td>Leistungsfaktor cos(&phi;)</td></tr>
    <tr><td>40001</td><td>Q_Control_Mode</td><td>Enum</td><td>UInt16</td><td>0=Off, 1=Q(U), 2=cosPhi(P), 3=Q-Festwert</td></tr>
    <tr><td>40002</td><td>P_Limit_Setpoint</td><td>%</td><td>Float32</td><td>Wirkleistungsbegrenzung (0..100% P_nenn)</td></tr>
  </tbody>
</table>

<h3>3. Regelverfahren nach VDE-AR-N 4110</h3>
<ol>
  <li><strong>Q(U)-Regelung:</strong> Dynamische Blindleistungsbereitstellung zur Spannungsstützung bei Unter-/Überspannung</li>
  <li><strong>cos &phi;(P)-Regelung:</strong> Blindleistungskompensation abhängig von der aktuellen Einspeiseleistung</li>
  <li><strong>P(f)-Wirkleistungsreduktion:</strong> Überfrequenzschutz ab 50,2 Hz zur Stabilisierung des europäischen Verbundnetzes</li>
</ol>
"""

res = confluence_service.create_or_update_page(
    title="EZA-Regler & VDE-AR-N 4110 Spezifikation",
    body_html=hardware_doc_html,
    parent_id="393341"
)
print("Hardware Doc Page Result:", res)
