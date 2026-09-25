const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const vm = require('node:vm');

// Ejecuta el script real y sus eventos con adaptadores mínimos de DOM/Drawflow.
// No sustituye una comprobación visual en navegador.
function designer() {
    class Element {
        constructor() {
            this.value = ''; this.checked = false; this.children = [];
            this.style = {}; this.dataset = {}; this.events = {};
            this.classList = {add() {}, remove() {}, toggle() {}};
        }
        set innerHTML(value) { this.children = []; this.html = value; }
        get innerHTML() { return this.html || ''; }
        appendChild(child) { this.children.push(child); }
        addEventListener(name, handler) { this.events[name] = handler; }
        scrollIntoView() {}
    }
    const elements = new Map();
    const element = id => {
        if (!elements.has(id)) elements.set(id, new Element());
        return elements.get(id);
    };
    const buttons = ['Task', 'Succeed', 'Fail'].map(type => {
        const button = new Element(); button.dataset.stateType = type; return button;
    });
    let editor;
    class Drawflow {
        constructor() { editor = this; this.nodes = {}; this.events = {}; this.counter = 0; }
        start() {}
        on(name, handler) { this.events[name] = handler; }
        export() { return structuredClone({drawflow: {Home: {data: this.nodes}}}); }
        getNodeFromId(id) { return structuredClone(this.nodes[id]); }
        updateNodeDataFromId(id, data) { this.nodes[id].data = structuredClone(data); }
        addNode(type, inputs, outputs, x, y, css, data) {
            const id = ++this.counter;
            this.nodes[id] = {id, data: structuredClone(data), outputs: {}};
            for (let i = 1; i <= outputs; i++) this.nodes[id].outputs[`output_${i}`] = {connections: []};
            return id;
        }
        removeNodeId(id) {
            const key = id.replace('node-', ''); delete this.nodes[key];
            this.events.nodeRemoved(key);
        }
    }
    vm.runInNewContext(readFileSync(`${__dirname}/designer.js`, 'utf8'), {
        document: {
            getElementById: element,
            querySelectorAll: selector => selector === '[data-state-type]' ? buttons : [],
            querySelector: () => null,
            createElement: () => new Element()
        }, Drawflow, window: {confirm: () => true}, console
    });
    const click = id => element(id).events.click();
    const select = id => editor.events.nodeSelected(String(id));
    const preview = () => { click('btn-view-json'); return JSON.parse(element('workflow-json').value); };
    const rename = (id, name) => { select(id); element('property-state-name').value = name; click('btn-update-state'); };
    buttons[0].events.click(); rename(1, 'ProcesarPago');
    buttons[1].events.click(); rename(2, 'Succeed');
    buttons[2].events.click(); rename(3, 'ErrorPago');
    editor.nodes[1].outputs.output_1.connections.push({node: '2'});
    select(1);
    element('property-resource').value = 'task:demo_procesar_pago';
    element('property-retry-enabled').checked = true;
    element('property-retry-max-attempts').value = '2';
    element('property-retry-interval').value = '0.25';
    element('property-retry-backoff').value = '2';
    element('property-catch-enabled').checked = true;
    element('property-catch-next').value = 'ErrorPago';
    click('btn-update-state');
    return {editor, element, click, select, preview, rename};
}

test('ProcesarPago exporta éxito, Retry y Catch compatibles con el motor', () => {
    const ui = designer();
    const definition = ui.preview();
    assert.equal(definition.StartAt, 'ProcesarPago');
    assert.deepEqual(definition.States.ProcesarPago, {
        Type: 'Task', Resource: 'task:demo_procesar_pago', Next: 'Succeed',
        Retry: [{ErrorEquals: ['States.ALL'], IntervalSeconds: 0.25, MaxAttempts: 2, BackoffRate: 2}],
        Catch: [{ErrorEquals: ['States.ALL'], Next: 'ErrorPago'}]
    });
    assert.equal(ui.click('btn-validate-workflow'), true);
});

test('Renombrar el destino actualiza Catch.Next', () => {
    const ui = designer();
    ui.rename(3, 'PagoRechazado');
    assert.equal(ui.preview().States.ProcesarPago.Catch[0].Next, 'PagoRechazado');
    assert.equal(ui.click('btn-validate-workflow'), true);
});

for (const mode of ['botón', 'Drawflow']) {
    test(`Eliminar destino mediante ${mode} limpia Catch y conserva Retry`, () => {
        const ui = designer();
        if (mode === 'botón') { ui.select(3); ui.click('btn-delete-state'); }
        else ui.editor.removeNodeId('node-3');
        const payment = ui.preview().States.ProcesarPago;
        assert.equal(payment.Catch, undefined);
        assert.equal(payment.Retry[0].MaxAttempts, 2);
        assert.equal(ui.editor.nodes[1].data.catchEnabled, false);
        assert.equal(ui.editor.nodes[1].data.catchNext, '');
        assert.equal(ui.click('btn-validate-workflow'), true);
    });
}

for (const [field, value] of [
    ['property-retry-max-attempts', '-1'], ['property-retry-max-attempts', '1.5'],
    ['property-retry-interval', '-1'], ['property-retry-interval', 'Infinity'],
    ['property-retry-backoff', '0.5'], ['property-retry-backoff', 'NaN'],
    ['property-catch-next', 'ProcesarPago'], ['property-catch-next', 'NoExiste'],
    ['property-catch-next', ''], ['property-resource', 'task:no_existe']
]) {
    test(`Rechazar ${field}=${value} no modifica el nodo ni sus referencias`, () => {
        const ui = designer();
        const before = ui.editor.export();
        ui.element('property-state-name').value = 'NuevoNombre';
        ui.element(field).value = value;
        ui.click('btn-update-state');
        assert.deepEqual(ui.editor.export(), before);
    });
}

test('Retry admite cero intentos y cero intervalo', () => {
    const ui = designer();
    ui.element('property-retry-max-attempts').value = '0';
    ui.element('property-retry-interval').value = '0';
    ui.element('property-retry-backoff').value = '1';
    ui.click('btn-update-state');
    assert.deepEqual(ui.preview().States.ProcesarPago.Retry[0], {
        ErrorEquals: ['States.ALL'], MaxAttempts: 0, IntervalSeconds: 0, BackoffRate: 1
    });
});
