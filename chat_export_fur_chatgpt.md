# Coneza - Projektstatus & Chat-Briefing für ChatGPT

## 1. Was ist Coneza?
Coneza ist eine hochmoderne Softwareplattform zur automatisierten Konformitätsprüfung und Steuerung von dezentralen Energieerzeugungsanlagen (PV-Freiflächen, Batteriespeicher BESS, Wind- und Hybridparks) nach den deutschen Netzanschlussrichtlinien **VDE-AR-N 4110** (Mittelspannung) und **VDE-AR-N 4120** (Hochspannung).

---

## 2. Aktueller Entwicklungsstand & durchgeführte Arbeiten

### A. Hybrid Multi-Model Engine (Dual-AI: Gemini 3.7 Flash + OpenAI GPT-4o)
- **Modell-Integration:** Direktes Zusammenspiel von Google Gemini und OpenAI GPT-4o.
- **Cross-Evaluation (Bidirektionales Peer-Review):** Beide KI-Modelle extrahieren parallel Parameter aus Netzanschlussdokumenten (E.8, E.9, Netzverträge) und prüfen/kritisieren anschließend gegenseitig ihre Ergebnisse anhand von VDE-AR-N 4110 Kriterien.
- **Konsens-Arbitrierung:** Automatische Berechnung eines quantitativen Konsens-Scores (z. B. 100%). Bei Abweichungen greift ein deterministisches Regelwerk zur Sicherheitsabsicherung.
- **Dateien:**
  - `backend/hybrid_analyzer.py`
  - `tests/test_hybrid_analyzer.py`

### B. Universelle Hardware-Unterstützung (Alle gängigen Hersteller)
Eine modulare Treiber-Architektur mit 16 industriellen Geräteprofilen:
1. **Wechselrichter & BESS:**
   - **SMA:** Sunny Tripower Core1/Core2, Peak3 (SunSpec Modbus TCP)
   - **Huawei:** SUN2000 Serie, SmartLogger 3000 (SunSpec Modbus TCP)
   - **Sungrow:** SG- und SH-Commercial Serien (SunSpec Modbus)
   - **Fronius:** Symo & Tauro Commercial (SunSpec Modbus TCP)
   - **SolarEdge:** Commercial SE30K–SE100K (SunSpec Modbus TCP)
   - **Kostal:** PIKO CI 30/50/60 (SunSpec Modbus)
   - **KACO new energy:** blueplanet 50.0–165 TL3 (SunSpec Modbus)
   *Features:* Wirkleistungsbegrenzung P(f), Blindleistungskennlinien Q(U), cos phi, 4-Quadranten-Betrieb, BESS Lade-/Entlademanagement.
2. **Smart Meter & Netzanalysatoren:**
   - **Janitza Electronics:** UMG 96RM, UMG 604, UMG 509/512 (Modbus TCP, IEEE-754 32-Bit Float Big-Endian)
   - **Schneider Electric:** PowerLogic PM5000 / PM8000
   - **Siemens:** SENTRON PAC3200 / PAC4200
   - **Phoenix Contact:** EMpro EEM-MA370
   - **Eastron:** SDM630 Modbus V2
   *Features:* 4-Quadranten-Messung am Netzverknüpfungspunkt (PCC), Oberschwingungsanalyse THD.
3. **EZA-Regler (VDE-AR-N 4110):**
   - **Phoenix Contact:** PLCnext SOL-SC-PCU
   - **WAGO:** PFC200 (750-8212 / Edge Controller)
   - **meteocontrol:** blue'Log XC
   - **Bachmann Electronic:** M1 Controller
   *Features:* VDE-AR-N 4110 Parkregelung, Schleifentest, Notabschaltung.
4. **Dateien:**
   - `edge/drivers/base.py` (Abstrakte Treiber-Klasse)
   - `edge/drivers/models.py` (Telemetrie- & Sollwert-Modelle)
   - `edge/drivers/inverters/sunspec.py` (SunSpec Inverter Driver)
   - `edge/drivers/meters/janitza.py` (Janitza UMG Meter Driver)
   - `edge/drivers/meters/schneider.py` (Schneider PowerLogic Driver)
   - `edge/drivers/eza_controllers/wago.py` (WAGO PFC200 Driver)
   - `edge/drivers/registry.py` (Geräteregister & Auto-Probe Scanner)
   - `tests/test_device_drivers.py`

### C. Live Device Probing & Auto-Discovery
- Neuer API-Endpunkt `POST /api/devices/probe`: Scannt IP-Adresse, Port und Modbus Slave-ID, misst Netzwerk-Latenz und identifiziert Herstellersignaturen.
- Neuer API-Endpunkt `GET /api/devices/catalog`: Liefert alle 16 Geräteprofile.
- Dashboard-Modale in `backend/templates/index.html` für Hardware-Katalog und Live-Scan.

### D. Test-Status
- Alle 38 Unit-Tests (Authentifizierung, Hybrid Analyzer, Gerätetreiber, EZA-Simulator, Jira-Integration) wurden erfolgreich ausgeführt (`Ran 38 tests - OK`).

---

## 3. Anweisung für ChatGPT
ChatGPT soll diesen Projektstand als Grundlage nehmen, um weitere Fragen, Code-Reviews oder Aufgaben für Coneza zu beantworten.
