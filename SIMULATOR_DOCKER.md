# Coneza Docker EZA simulator â€” EEP-77

Runs the project's in-memory Modbus simulator and portal gateway together. It is a test device, not Phoenix PCU software, a hardware-compatible replacement, or certified grid-control equipment.

## Run on the Ubuntu IPC

Requires Docker Engine with Compose v2 and this working tree (these new files may not yet be available on GitHub). Copy only the files listed by docker/Dockerfile.simulator plus the Compose and ignore files; do not transfer .env, jira_config.json, databases or other credentials.

From the project directory:

```bash
export CONEZA_BACKEND_URL=https://coneza.de/portal
export SIMULATOR_DEVICE_ID=coneza-sim-01
export SIMULATOR_NAME="Ubuntu IPC virtual EZA"
docker compose -f docker/compose.simulator.yml up -d --build
docker compose -f docker/compose.simulator.yml logs --tail=100 -f
```

The backend URL must be the base serving `/api/devices/register` and `/api/devices/{id}/heartbeat`. Confirm the deployment's reverse-proxy path if registration returns 404. No PLC IP or port is needed.

In the portal device list, look for **SIMULATION - Ubuntu IPC virtual EZA**, ID **coneza-sim-01**. Heartbeats are sent every 10 seconds. Registration is automatic; assign this device to a test plant using the portal's existing device assignment UI. Use a different `coneza-sim-...` ID for each simulator and never reuse a physical gateway ID.

No host ports are published. The simulated Modbus server binds only to container loopback. EZA_CONTROLLER_HOST/PORT are deliberately ignored. Portal deployments execute against this virtual controller only, and return read-back results. Existing portal approval rules still apply. This does not bypass blocked or missing audits.

## Scope and limits

- Existing simulator supplies synthetic power, voltage, frequency and controller status using the project's register map. It implements Modbus register reads/writes; exact Phoenix firmware behavior, protection timing and certified control performance are not established.
- Configuration is in memory and resets on container recreation/restart. A healthy container indicates the local Modbus listener is reachable, not that portal registration succeeded; check logs and the portal's last heartbeat.
- The gateway uses the existing portal registration protocol. No new authentication scheme or public control endpoint is introduced.
- Docker build and live portal appearance must be verified on an accessible Docker host before this is described as deployed. The development workstation currently has no Docker command installed.

Stop the test device:

```bash
docker compose -f docker/compose.simulator.yml down
```

The portal may retain its device record and eventually show it offline. Stop does not delete any portal data.

## Verified IPC deployment (EEP-77, 2026-09-23)

Host `192.168.8.186` is Debian 12 on ARM64 (kernel 6.1.118), not Ubuntu. Its kernel lacks NF_TABLES and IP_NF_RAW. The authorized IPv4 iptables-legacy selection lets Docker start, but bridge networking still cannot create its raw filtering rules. IPv6 was not changed and no Docker filtering protection was disabled.

The deployed image is `coneza-eza-simulator:isolated`, ID `sha256:e307cc022046b8c04e96ad29859c6f3bcd55570ad3b4c6488caabd2f52688b03`. It was built locally on the IPC with `Dockerfile.simulator-offline` using predownloaded ARM64-compatible wheels and `--network=none`. To reproduce: download wheels from requirements.simulator.txt into docker/wheels, then build with that Dockerfile. The wheel directory is an input artifact, not committed source.

Active deployment: `/opt/coneza-simulator/isolated-eep77/docker/compose.simulator-isolated.yml`, Compose project `coneza-simulator`. The container uses network=none, non-root UID/GID 10001, read-only root filesystem, no capabilities and no published ports. A read-only bind mount provides a Unix socket. The unprivileged `coneza-portal-tunnel.service` relays this socket only to fixed destination coneza.de:443; the container still validates HTTPS certificates end-to-end. It is not a general network proxy and accepts no requested upstream address.

Verified: container healthy; portal registration HTTP 200; repeated heartbeat HTTP 200. Portal device ID: `coneza-sim-ipc-186`; name: **SIMULATION - IPC 192.168.8.186 virtual EZA**. No physical PLC access or configuration performed. No portal plant assignment was changed.

```bash
# On the IPC: status and logs
sudo docker compose -p coneza-simulator -f /opt/coneza-simulator/isolated-eep77/docker/compose.simulator-isolated.yml ps
sudo docker logs --tail=30 coneza-simulator-eza-simulator-1
sudo systemctl status coneza-portal-tunnel.service

# Stop the simulator only
sudo docker compose -p coneza-simulator -f /opt/coneza-simulator/isolated-eep77/docker/compose.simulator-isolated.yml stop
```

The image uses in-memory simulated settings and must not be represented as Phoenix PCU firmware or certified EZA control. Existing portal approval restrictions apply. Visual portal login/plant assignment and physical PCU compatibility were not tested.

## Lokale Weboberfläche (EEP-77)

Auf dem IPC erreichbar unter http://192.168.8.186/ (HTTP, Port 80, nur diese LAN-Adresse). Schreibgeschützte Anzeige von Portalstatus, synthetischen Messwerten und aktueller Konfiguration; Aktualisierung alle 5 Sekunden. Konfigurationsänderungen bleiben im Portal. Keine Anmeldung: Geräte im erreichbaren lokalen Netz können die Simulationswerte lesen. Keine Geheimnisse, Fehlermeldungsdetails oder Hostverwaltung werden angeboten.

Der Container bleibt network=none und nutzt für die Oberfläche ausschließlich /run/coneza-simulator-web/web.sock. Der Hostdienst coneza-simulator-web leitet nur zu diesem Socket weiter, erhält keine Docker-Socket-Rechte und bindet nicht an die PLC-Netzwerkadresse. deploy/coneza-simulator-web.conf erzeugt das Socketverzeichnis mit UID/GID 10001 beim Boot. Installieren mit systemd-tmpfiles --create und dem gleichnamigen systemd-Dienst. Compose verwendet nun coneza-eza-simulator:local-web; das vorherige Image :isolated bleibt als Rückfall verfügbar.

Verifiziert: 13 gezielte lokale Tests; echte Browseransicht mit ONLINE und Messwerten auf dem IPC. Der Dienst ist für Autostart aktiviert, ein vollständiger IPC-Neustart wurde nicht getestet. Physische PLC unverändert.

## EEP-77 separate Modbus TCP LAN endpoints

Explicitly authorized endpoints: 192.168.8.186:5502 -> simulator only; 192.168.8.186:502 -> physical 192.168.1.10:502. These are transparent TCP relays, including write functions. No internet/router forwarding or firewall disabling. Bind address is the IPC LAN address only; clients with network access can send Modbus commands. Container stays network=none; simulator traffic enters through a fixed Unix socket. This does not prove full Phoenix firmware/register compatibility.

Service: coneza-modbus-access. Files: /opt/coneza-modbus-access. Compose uses existing base file plus docker/compose.modbus-access.yml in that directory. Image is a layer on the previously deployed local-web image, deliberately excluding unrelated local controller/simulator edits. To disable both listeners: systemctl stop coneza-modbus-access.

Verified: two relay tests passed; simulator LAN FC03 read succeeded, container healthy. Physical target TCP connection refused from IPC; forwarding listener runs but real PCU access is NOT operational until its Modbus TCP server is available. No physical writes performed. Existing coneza-phoenix-gateway service unchanged. Autostart enabled, reboot not tested.
