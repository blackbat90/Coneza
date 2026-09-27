# Gemeinsame Zusammenarbeit: Codex / Gemini

Stand: 2026-09-23. Gemeinsamer lokaler Arbeitsbaum: C:/Workplace/Coneza/Coneza.

## Verbindliche Arbeitsvereinbarung

- Vor Änderungen aktuellen Dateistand und Git-Diff prüfen; fremde Änderungen erhalten. Keine konkurrierende Umsetzung desselben Pakets.
- Jeder Schritt hat einen Jira-Schlüssel, Quellen, Prüfkriterien, passende Tests und fokussierte lokale Commits. Bestehende passende Epics wiederverwenden; sinnvolle fremde Zuordnungen erhalten.
- Keine pauschalen Commits des Arbeitsbaums, kein Umschreiben der Historie, kein Produktionsdeployment und keine Steuerung realer Anlagen.
- Jira-Aufgabenorganisation, Fortschrittskommentare und Commit-Verknüpfung sind autorisiert. Zugangsdaten nie in Dokumente oder Ausgaben übernehmen.
- Diese Datei ist eine gemeinsame Übergabemöglichkeit. Es besteht keine direkte Verbindung zu Gemini; ob Gemini sie gelesen hat, ist unbekannt.

## Aktive Zuständigkeiten

| Agent | Paket | Dateien | Status |
|---|---|---|---|
| Codex | EEP-76: signed Q-Rücklesung; Epic EEP-38 | edge/phoenix_eza/controller.py; tests/test_phoenix_signed_config.py; COLLABORATION.md | Abgeschlossen: Commit 967745e; keine aktive Codebearbeitung |
| Gemini | Unbekannt | Unbekannt; bestehende Änderungen gelten als zu erhalten | Keine bestätigte Abstimmung |

Codex beansprucht in diesem Zyklus keine anderen Implementierungsdateien. Andere Codex-Aufgabe im Projekt ist laut App-Status inaktiv; Gemini-Aktivität ist dadurch nicht feststellbar.

## Bisherige Arbeit und Grenzen

- 2026-09-21: Offline-Analyse ohne erfundene 2500-kW-Anlage/100%-Konsens; kritische Reviews und fehlende Daten blockieren Freigabe, Deployment und wartende Aufträge; keine KI-Zertifizierung im Audit. 14 gezielte isolierte Tests bestanden. Diese Änderungen sind noch uncommittet und mit dem vorherigen lokalen Arbeitsstand verschränkt; nicht pauschal mitcommitten.
- Signed-Q-Korrektur stammt ebenfalls aus diesem Codex-Zyklus. controller.py war vor dieser Korrektur unverändert; sein aktueller Diff enthält ausschließlich die signed-Dekodierung. Deshalb lässt sich dieses Paket sicher isolieren.
- Confluence-Inventur: CONFLUENCE_REQUIREMENTS.md, Stand 2026-09-21. 4 Spaces/35 Seiten inventarisiert, 30 Produktseiten textuell gelesen. Whiteboards, Bildanhänge und Norm-PDF bleiben inhaltlich offen. Keine vollständige Anforderungsabdeckung behaupten.
- 2026-09-23: Jira-Backlog erneut live gelesen; passende bestehende Hierarchie EEP-38 -> EEP-40/EEP-48 bleibt bestehen. Neues Bug-Ticket EEP-76 unter EEP-38 erstellt: https://easy-eza.atlassian.net/browse/EEP-76.

## Priorisierter Folge-Backlog (noch nicht beansprucht)

1. Audit-/Freigabekorrekturen isolieren und nachvollziehbar committen; Quellen: EEP-34, Edge Cases 23199745. Eine verlässliche Trennung vom vorherigen Gemini-Stand ist erforderlich.
2. TAB-Anwendung reparieren: backend/main.py fragt configurations/config_json ab; das Schema enthält eza_configurations/parameters_json. Quelle: Architecture and Features 1933313, EEP-40. Vorschlag für Prüfkriterien: richtigen Entwurf aktualisieren, Quellenversion dokumentieren, alte Freigabe verwerfen, keine angenommenen DSO-Werte als bestätigt behandeln.
3. EEP-48: Konfigurationsimport/-export für Backup und Wiederverwendung. Vorschlag: versioniertes Format, strikte Validierung, Import als neuer ungeprüfter Entwurf; keine übernommene Deployment-Freigabe.
4. EEP-23/EEP-34: nachvollziehbare Dokumentquellen, Komponenten-/Portzuordnung und geführte Inbetriebnahme. Der bestehende Code deckt nur Teile ab.
5. Edge Cases 23199745: Offline-Nutzung sowie wöchentliche Backups/Reset; local_buffer.py ist bisher nicht im Heartbeat eingebunden. Puffergröße 50.000, BESS 95% und Timeout 5s sind Implementierungsannahmen, keine belegten Anforderungen der gelesenen Seiten.
6. Quellenabdeckung vervollständigen: drei Whiteboards, Bildanhänge und VDE-PDF. Registerkarte in Confluence und lokaler Simulator unterscheiden sich; keine Hardware-Kompatibilität allein aus Simulation ableiten.

## Übergabe

Vor dem nächsten Arbeitspaket Status hier aktualisieren und Dateiinhalte erneut prüfen. Nicht automatisch annehmen, dass ein Jira-Backlogstatus den lokalen Implementierungsstand wiedergibt. Die komplette Testsuite ist nicht verifiziert.

## Ergebnis des Zyklus 2026-09-23 / EEP-76

- Driver-only-Test: `python -m unittest tests.test_phoenix_signed_config -v` — 1 Test bestanden. Er prüft alle vier Q-Punkte und den Q-Sollwert mit -32768, -100, -1, 0, 1, 32767 sowie Q4=-100%; U-Punkte bleiben unverändert. Modbus-Netzwerkzugriffe sind im Test verboten.
- Gegenprobe: Derselbe Test mit controller.py aus HEAD schlägt erwartungsgemäß fehl (1 Assertion-Fehler, keine Ausführungsfehler). Damit erkennt der Test die konkrete Regression.
- Fokussierter Commit vorgesehen: `EEP-76 fix signed reactive-power configuration readback`, ausschließlich controller.py und test_phoenix_signed_config.py.
- Commit NICHT erstellt. `git add` scheiterte an `.git/index.lock: Permission denied`; zwei Berechtigungsanfragen erteilten keinen Dateisystem-Schreibzugriff. Kein Umgehen der Beschränkung, kein Push. Git-Index blieb unverändert.
- Fortsetzung: Nach tatsächlich erteiltem Git-Schreibzugriff Dateien erneut vergleichen, Test ausführen, genau diese beiden Dateien committen und Commit-ID im Jira-Ticket dokumentieren. Andere lokale Änderungen nicht übernehmen. Testüberschneidung mit dem noch uncommitteten test_safety_regressions.py später beim Isolieren des Audit-Pakets bereinigen.

## Aktives Paket EEP-77: Docker-Simulator (2026-09-23)

Codex beansprucht ausschließlich neue Dateien: edge/simulator_service.py, docker/Dockerfile.simulator, docker/Dockerfile.simulator.dockerignore, docker/requirements.simulator.txt, docker/compose.simulator.yml, tests/test_simulator_service.py, SIMULATOR_DOCKER.md. Gemeinsame Koordinationsdatei wird aktualisiert. Keine fremden Implementierungsdateien ändern.
Ticket: https://easy-eza.atlassian.net/browse/EEP-77, Epic EEP-38. Quelle: ausdrücklicher Nutzerauftrag plus EEP-24 / Confluence Dev. Approach 4096001. Zielgerät: Ubuntu IPC; SSH-Adresse noch offen. Docker ist in dieser Windows-Arbeitsumgebung nicht verfügbar. Image-Build und dauerhafte Portal-Erreichbarkeit erst nach tatsächlicher Prüfung melden.

## Aktualisierung EEP-76 / EEP-77

- Git-Schreibblocker durch genehmigte Befehlseskalation gelöst. EEP-76 fokussiert committed: 967745e (controller.py und eigenständiger signed-Q-Test). Vorherige Blockerangaben sind historisch.
- EEP-77: Simulator-Service, selektiver Docker-Buildkontext, Compose-Datei und Anleitung implementiert. Controller ausschließlich 127.0.0.1:5502 innerhalb des Containers; feste Simulator-ID-Präfixprüfung; Portalname SIMULATION. Kein Host-Port veröffentlicht, kein physischer PLC-Zugriff.
- Verifikation: `python -m unittest tests.test_simulator_service tests.test_phoenix_signed_config -v` — 5 Tests bestanden. Echte lokale Modbus-Verbindung mit Mock-Portal für Registrierung, Telemetrie und simulierten Konfigurationsauftrag. Shutdown und falsche Konfiguration geprüft.
- Benutzer wünscht Betrieb auf Ubuntu IPC im lokalen Netz. Das ist über ausgehendes HTTPS möglich. SSH-IP/Benutzer noch nicht genannt; Docker ist hier nicht installiert. Deshalb kein Image-Build, kein Containerstart auf IPC und keine tatsächliche Portalregistrierung behaupten.
- EEP-77 Implementierung abgeschlossen; Deployment wartet auf erreichbaren Docker-Host. Dateien freigegeben nach Commit. Fremde Änderungen weiterhin uncommittet erhalten.

- EEP-77 Paket committed: 80c358b. IPC-Adresse vom Nutzer bestätigt: 192.168.8.186, SSH-Benutzer root. SSH erreichbar; Banner Debian OpenSSH. Betriebssystem/Docker und Schlüsselzugang werden vor Installation geprüft.

## EEP-77 Fortsetzung: Offline-Image-Build

IPC ist Debian 12 ARM64, nicht Ubuntu. Docker läuft nach autorisierter Umstellung ausschließlich von IPv4-iptables auf legacy; IPv6 unverändert. Kernel 6.1.118 hat weder NF_TABLES noch IP_NF_RAW. Bridge-Build/Container-Netzwerk scheitert an fehlendem raw-Filter. Keine Schutzfunktion deaktivieren. Codex beansprucht zusätzlich docker/Dockerfile.simulator-offline und dessen .dockerignore sowie die Docker-Anleitung. Offline-Build verwendet vorab geladene Wheels und network=none. Dauerhafte Portalverbindung bleibt bis zur unterstützten Laufzeit offen.

Codex erweitert EEP-77 um Portal-UDS-Transport: edge/backend_client.py (unverändert gegenüber HEAD vor Bearbeitung), edge/simulator_service.py, edge/portal_tunnel.py, deploy/coneza-portal-tunnel.service, docker/compose.simulator-isolated.yml und zugehörige Tests. Container bleibt network=none; ein unprivilegierter Host-Dienst verbindet ausschließlich coneza.de:443. TLS bleibt Ende-zu-Ende verifiziert. Keine Firewall-Schutzfunktion deaktivieren.

## EEP-77 Ergebnis: IPC-Simulator online

2026-09-23: ARM64-Image e307cc022046b8c04e96ad29859c6f3bcd55570ad3b4c6488caabd2f52688b03 auf Debian-IPC 192.168.8.186 gebaut. Container coneza-simulator-eza-simulator-1 healthy, network=none, UID10001, read-only. Unprivilegierter lokaler Unix-Socket-Relay zu festem coneza.de:443; TLS-Ende-zu-Ende-Prüfung bleibt aktiv. Registrierung und wiederholte Heartbeats HTTP200; Portalgerät coneza-sim-ipc-186 / SIMULATION - IPC 192.168.8.186 virtual EZA. Keine physische PLC angesprochen. 9 lokale Tests bestanden; vorheriges Basisimage zusätzlich mit 4 Integrationstests direkt auf IPC geprüft. Keine vollständige Suite behaupten. Boot-Verhalten noch nicht durch Neustart geprüft.

Frühere Statusangaben „kein Build/keine Registrierung“ sind damit überholt. Konfiguration/Abhängigkeiten wurden nur in getrennten simulator-spezifischen Verzeichnissen auf IPC abgelegt; keine lokalen Zugangsdaten mitkopiert. EEP-77-Dateien nach fokussiertem Commit freigeben. Dokumentation: SIMULATOR_DOCKER.md.

## Aktuelle Übergabe nach Betriebsprüfung

EEP-77: Installation und gezielte Tests abgeschlossen; nur Git-/Jira-Abschluss läuft. Alle beanspruchten Implementierungsdateien sind anschließend freigegeben. Erneute SSH-Prüfung bestätigt healthy und fortlaufende HTTP-200-Heartbeats. Andere Codex-Aufgabe inaktiv; Gemini-Zustand unbekannt. Fremde Änderungen bleiben erhalten. Kein weiteres Paket begonnen.

## Lokale Simulator-Weboberfl�che (Nutzerauftrag)
Codex beansprucht simulator_web.py, simulator_web_relay.py, zugeh�rigen Dienst und Tests sowie Simulator-Service, Dockerdateien und Anleitung. Nur lesender LAN-Zugang zu simulierten Messwerten und Einstellungen. Keine PLC-Zugriffe. Keine konkurrierende Codex-Arbeit festgestellt.

Lokale Weboberfl�che EEP-77 abgeschlossen: http://192.168.8.186/ im Browser gepr�ft, ONLINE und synthetische Messwerte sichtbar. 13 Tests bestanden. Schreibgesch�tzt, LAN-Bindung nur 192.168.8.186:80, isolierter Container unver�ndert network=none. Neuer unprivilegierter Hostdienst mit ausschlie�lich CAP_NET_BIND_SERVICE. Image 24d4dfab81056cfa0da9ea58ba4471976e63bdfaed3ca5186999aafc5622dabb. Autostart eingerichtet, Reboot nicht getestet. Dateien nach fokussiertem Commit freigegeben; fremde �nderungen erhalten.

## EEP-77 Modbus LAN access
User explicitly requested both endpoints: simulator :5502 and physical PCU :502. Codex owns only new modbus_access module, service, Docker overlay and tests. Existing modified simulator/controller and physical gateway files remain untouched. Physical gateway service observed active; simulator stopped before this work.

EEP-77 endpoints installed. Simulator FC03 verified on LAN5502, healthy/network=none; physical forward LAN502 installed but target 192.168.1.10:502 refuses TCP. Two relay tests pass. No PLC writes or changes. New files released after commit; all pre-existing controller/simulator/gateway edits preserved.

## 2026-09-24 EEP-77 heartbeat status correction
Codex claims only edge/backend_client.py and tests/test_edge_heartbeat_status.py plus this coordination file. Other Codex task idle; Gemini status unknown. Baseline regression proves HTTP rejection leaves stale ONLINE (7 cases). Local-only fix; no deployment or hardware access. Existing unrelated work preserved.

EEP-77 result: rejected HTTP heartbeat now replaces stale ONLINE with HEARTBEAT_FAILED and numeric HTTP status only. Successful heartbeat recovers ONLINE; 404 registration preserved. Six focused tests passed, baseline failed in seven HTTP cases. No full-suite claim, no IPC or PLC deployment. Files released after focused commit.

## 2026-09-24 EEP-77 result delivery logging
Codex claims clean edge/backend_client.py plus new tests/test_edge_result_reporting.py. Baseline shows rejected config-result HTTP307/401/500 logged as delivered. Local-only work, controller fully mocked; unrelated modifications preserved.

Result: HTTP success is now required before logging config-result delivery. Three targeted tests pass; regression failed on three rejected response codes before fix. No automatic retry or duplicate controller execution introduced. No deployment, real hardware access or full-suite claim. Files released after commit.

## EEP-77 unexpected heartbeat failure
Codex claims clean backend_client.py and new test_edge_loop_status.py only. Other project task not loaded; Gemini unknown. Unexpected heartbeat exceptions currently leave ONLINE stale; baseline regression reproduced. Local mocked tests only.

Result: outer heartbeat exception now invalidates ONLINE with generic failure text. Five targeted tests pass; baseline failed. Cancellation propagation and loop continuation tested. No IPC/PLC access or deployment; unrelated modifications preserved. Files released after commit.

## 2026-09-25 EEP-77 job envelope validation
Live Jira EEP-77 verified under EEP-38 (simulation/config acknowledgments, source reference Dev. Approach 4096001). Codex claims clean edge/backend_client.py, tests/test_edge_job_validation.py and this file. Other project task not loaded; Gemini unknown. Baseline malformed envelopes reach mocked controller or fail with AttributeError. No hardware/network in tests. Existing modified files untouched.

Result: invalid job envelopes rejected before controller/HTTP calls; requires object, nonblank string job_id, explicit parameters object. Six targeted tests passed, including twelve malformed cases and existing successful report/heartbeat regressions. Parameter values, approval authorization and idempotency are outside this change; empty explicit objects remain accepted. Baseline failed all twelve cases (nine failures, three errors). No deployment or PLC access. Files released after commit.

## 2026-09-27 EEP-77 telemetry availability
Codex claims clean backend_client.py and new test_edge_telemetry_failure.py only. Other project tasks not loaded; Gemini unknown. Mocked baseline proves failed telemetry read still publishes controller_connected=True. No deployment/hardware access.

Result: telemetry read errors publish controller_connected=False / TELEMETRY_UNAVAILABLE with no fabricated values. Next successful read restores measured data and connectivity; portal connectivity remains separate. Seven focused tests pass, baseline regression failed. No deployment, hardware access, full-suite claim or changes to dispatch policy. Files released after commit.

## 2026-09-27 EEP-77 controller probe failure
Codex claims clean backend_client.py and new test_edge_probe_failure.py. Other tasks not loaded; Gemini unknown. Probe exceptions currently suppress entire portal heartbeat. Baseline reproduced with mocks; no hardware access.

Result: probe exceptions produce disconnected/CONNECTION_CHECK_FAILED heartbeat without exception details or fabricated telemetry. Subsequent successful probe recovers; cancellation still propagates without HTTP access. Nine targeted mocked tests pass; baseline error reproduced. No deployment or hardware access. Job dispatch policy unchanged; full suite not asserted. Files released after focused commit.
