# Coneza Docker EZA simulator — EEP-77

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
