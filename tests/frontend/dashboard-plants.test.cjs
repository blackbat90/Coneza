const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

class Element {
    constructor() { this.children = []; this.style = {}; this.value = ''; this.textContent = ''; }
    append(child) { this.children.push(child); }
    before() {}
    setAttribute() {}
    replaceChildren() { this.children = []; this.value = ''; }
    add(option) { this.append(option); if (this.children.length === 1) this.value = option.value; }
    get options() { return this.children; }
    addEventListener(_, callback) { this.change = callback; }
    querySelector() { return this.target; }
}
const flatten = el => el.textContent + ' ' + el.children.map(flatten).join(' ');
test('plant selection, real zero values, stale data, races, demo and logout', async () => {
    const screen = new Element(), top = new Element(), status = new Element(), demo = new Element(), simulation = new Element();
    screen.children = [top, demo]; screen.target = top; top.target = status;
    const pending = [];
    const context = {
        document: {querySelector: () => screen, getElementById: () => simulation, createElement: () => new Element()},
        window: {}, authToken: 'test', API_BASE: '', setInterval: () => {},
        Option: function(name, value) { this.textContent = name; this.value = value; this.children = []; },
        fetch: url => new Promise(resolve => pending.push({url, resolve})),
    };
    vm.runInNewContext(fs.readFileSync('backend/static/dashboard-plants.js', 'utf8'), context);
    const panel = screen.children.at(-1);
    const api = context.window.dashboardPlants;
    api.setPlants([{id:'a', name:'Plant A'}]);
    assert.equal(pending[0].url, '/api/plants/a');
    api.setPlants([{id:'b', name:'Plant B'}]);
    const response = (name, time) => ({ok:true, json:async () => ({name, devices:[{device_id:'d', status:'ONLINE', controller_state:'RUNNING', last_heartbeat:time, telemetry:{actual_active_power_kw:0}}]})});
    pending[1].resolve(response('Plant B', new Date().toISOString()));
    await new Promise(setImmediate);
    assert.match(flatten(panel), /Plant B/);
    assert.match(flatten(panel), /0 kW/);
    assert.match(flatten(panel), /Nicht verfügbar/);
    pending[0].resolve(response('Plant A', new Date().toISOString()));
    await new Promise(setImmediate);
    assert.doesNotMatch(flatten(panel), /Plant A/);
    api.setPlants([{id:'b', name:'Plant B'}]);
    pending[2].resolve(response('Plant B', '2020-01-01T00:00:00Z'));
    await new Promise(setImmediate);
    assert.match(flatten(panel), /Keine aktuellen Messwerte/);
    assert.doesNotMatch(flatten(panel), /0 kW/);
    context.authToken = '';
    api.setPlants([]);
    assert.match(flatten(panel), /Bitte anmelden/);
    assert.doesNotMatch(flatten(panel), /Plant B/);
});
