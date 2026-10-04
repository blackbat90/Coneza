/* Read-only plant dashboard. The demo remains explicitly separate from telemetry. */
(() => {
    const screen = document.querySelector('.controller-screen');
    const top = screen.querySelector('.screen-top');
    const demo = Array.from(screen.children).filter(child => child !== top);
    const demoDisplay = demo.map(element => element.style.display);
    const simulation = document.getElementById('flowSimSelect');
    const status = top.querySelector('.status');
    const label = document.createElement('label');
    label.textContent = 'Anlage ';
    const select = document.createElement('select');
    select.id = 'dashboardPlantSelect';
    select.className = 'sim-mode-select';
    select.setAttribute('aria-label', 'Anlage im Dashboard');
    select.style.maxWidth = '100%';
    label.append(select);
    top.before(label);
    const panel = document.createElement('div');
    panel.setAttribute('aria-live', 'polite');
    screen.append(panel);
    let generation = 0;
    let plants = [];

    function text(parent, tag, value) {
        const element = document.createElement(tag);
        element.textContent = value;
        parent.append(element);
        return element;
    }

    function measurement(telemetry, key, unit) {
        const value = telemetry[key];
        return typeof value === 'number' && Number.isFinite(value)
            ? `${value.toLocaleString('de-DE', {maximumFractionDigits: 2})} ${unit}`
            : 'Nicht verfügbar';
    }

    async function refresh() {
        const version = ++generation;
        const id = select.value;
        const isDemo = id === '__demo__';
        demo.forEach((element, index) => { element.style.display = isDemo ? demoDisplay[index] : 'none'; });
        simulation.style.display = isDemo ? '' : 'none';
        panel.hidden = isDemo;
        panel.replaceChildren();
        status.textContent = isDemo ? '● DEMO · SIMULATION' : 'ANLAGENDATEN';
        if (isDemo) return;
        if (!id || !authToken) {
            text(panel, 'p', authToken ? 'Keine Anlage verfügbar.' : 'Bitte anmelden, um eine Anlage auszuwählen.');
            return;
        }
        text(panel, 'p', 'Messwerte werden geladen …');
        try {
            const response = await fetch(`${API_BASE}/api/plants/${encodeURIComponent(id)}`, {
                headers: {Authorization: `Bearer ${authToken}`}
            });
            if (!response.ok) throw new Error('load');
            const plant = await response.json();
            if (version !== generation) return;
            panel.replaceChildren();
            text(panel, 'h3', plant.name);
            text(panel, 'p', `${plant.grid_operator || 'Netzbetreiber nicht hinterlegt'} · ${plant.grid_connection_point || 'Netzanschlusspunkt nicht hinterlegt'}`);
            text(panel, 'p', 'Zuletzt gemeldete Messwerte je Gerät · Aktualisierung alle 15 Sekunden');
            if (!(plant.devices || []).length) text(panel, 'p', 'Keine Geräte mit dieser Anlage verknüpft.');
            for (const device of plant.devices || []) {
                const box = document.createElement('section');
                box.style.cssText = 'padding:12px 0;border-top:1px solid #334155';
                panel.append(box);
                text(box, 'h4', device.name || device.device_id);
                const rawTime = device.last_heartbeat;
                const timestamp = rawTime ? Date.parse(/Z$|[+-]\d\d:\d\d$/.test(rawTime) ? rawTime : rawTime.replace(' ', 'T') + 'Z') : NaN;
                const fresh = Number.isFinite(timestamp) && Date.now() - timestamp < 90000 && Date.now() >= timestamp;
                const unavailable = /disconnect|unavailable|failed|error|unknown/i.test(device.controller_state || 'unknown');
                const usable = device.status === 'ONLINE' && !unavailable && fresh;
                const telemetry = usable ? (device.telemetry || {}) : {};
                text(box, 'p', `${usable ? 'Aktuelle Meldung' : 'Keine aktuellen Messwerte'} · ${device.device_id}`);
                text(box, 'p', `Letzte Meldung: ${Number.isFinite(timestamp) ? new Date(timestamp).toLocaleString('de-DE') : 'Nicht verfügbar'}`);
                const grid = document.createElement('div');
                grid.className = 'flow-params-grid';
                box.append(grid);
                for (const [title, key, unit] of [
                    ['Wirkleistung', 'actual_active_power_kw', 'kW'],
                    ['Blindleistung', 'actual_reactive_power_kvar', 'kvar'],
                    ['Spannung L12', 'grid_voltage_l12_volts', 'V'],
                    ['Frequenz', 'grid_frequency_hz', 'Hz']
                ]) {
                    const cell = document.createElement('div');
                    cell.className = 'flow-param-box';
                    grid.append(cell);
                    text(cell, 'div', title).className = 'flow-param-title';
                    text(cell, 'div', measurement(telemetry, key, unit)).className = 'flow-param-value';
                }
            }
        } catch (_) {
            if (version !== generation) return;
            panel.replaceChildren();
            text(panel, 'p', 'Anlagendaten konnten nicht geladen werden. Bitte erneut auswählen oder aktualisieren.');
        }
    }

    window.dashboardPlants = {
        setPlants(values) {
            const previous = select.value;
            plants = values;
            select.replaceChildren();
            for (const plant of plants) select.add(new Option(`${plant.name} (${plant.id})`, plant.id));
            if (!plants.length) select.add(new Option('Keine Anlage verfügbar', ''));
            select.add(new Option('Demo / Simulation', '__demo__'));
            if (Array.from(select.options).some(option => option.value === previous)) select.value = previous;
            else select.value = plants[0]?.id || '';
            refresh();
        }
    };
    select.addEventListener('change', refresh);
    window.dashboardPlants.setPlants([]);
    setInterval(() => { if (select.value && select.value !== '__demo__') refresh(); }, 15000);
})();
