/* Conversión pura: nunca modifica la definición recibida. */
(function (root) {
    'use strict';
    const statuses = ['PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED', 'RETRYING', 'WAITING'];
    const palette = ['#e2e8f0', '#bfdbfe', '#bbf7d0', '#fecaca', '#fde68a', '#ddd6fe'];
    // Entidades Mermaid: ningún nombre del usuario se utiliza como sintaxis o ID.
    const label = value => Array.from(String(value)).map(c => /[a-zA-Z0-9 _.-]/.test(c) ? c : `#${c.codePointAt(0)};`).join('');

    function buildWorkflowDiagram(definition, events = [], execution = null) {
        const lines = ['flowchart TD'], nodes = [], warnings = [];
        let counter = 0;
        const id = () => `n${counter++}`;
        const edge = (from, to, text) => {
            if (to) lines.push(`${from} -->${text ? `|"${label(text)}"|` : ''} ${to}`);
        };
        function scope(def, title) {
            if (!def || !def.States || !def.StartAt) throw new Error('Definición incompleta');
            const map = new Map(), exits = [];
            for (const [name, state] of Object.entries(def.States)) {
                const node = {id: id(), name, type: state.Type, state};
                map.set(name, node); nodes.push(node);
            }
            const start = id();
            lines.push(`${start}(["${label(title)}"])`);
            edge(start, map.get(def.StartAt)?.id);
            for (const node of map.values()) {
                const {state, name} = node;
                const text = label(`${name} · ${state.Type}`);
                lines.push(state.Type === 'Choice' ? `${node.id}{"${text}"}`
                    : ['Succeed', 'Fail'].includes(state.Type) ? `${node.id}(["${text}"])`
                    : `${node.id}["${text}"]`);
                let tail = node.id;
                if (state.Type === 'Parallel') {
                    tail = id(); lines.push(`${tail}(("Unión"))`);
                    (state.Branches || []).forEach((branch, index) => {
                        const group = id();
                        lines.push(`subgraph ${group}["Rama ${index + 1}"]`);
                        const nested = scope(branch, `Inicio rama ${index + 1}`);
                        lines.push('end'); edge(node.id, nested.start);
                        nested.exits.forEach(exit => edge(exit, tail));
                    });
                }
                if (state.Type === 'Choice') {
                    (state.Choices || []).forEach(rule => {
                        const comparator = Object.keys(rule).find(key => !['Variable', 'Next'].includes(key));
                        edge(node.id, map.get(rule.Next)?.id, `${rule.Variable} ${comparator} ${JSON.stringify(rule[comparator])}`);
                    });
                    edge(node.id, map.get(state.Default)?.id, 'Default');
                } else if (state.Next) edge(tail, map.get(state.Next)?.id);
                else if (state.Type !== 'Fail' && (state.End || state.Type === 'Succeed')) exits.push(tail);
                (state.Catch || []).forEach(rule => edge(node.id, map.get(rule.Next)?.id, `Catch ${rule.ErrorEquals.join(', ')}`));
            }
            return {start, exits};
        }
        scope(definition, 'StartAt');
        const groups = new Map();
        nodes.forEach(node => {
            const key = JSON.stringify([node.name, node.type]);
            if (!groups.has(key)) groups.set(key, []);
            groups.get(key).push(node);
        });
        const ordered = [...events].sort((a, b) => a.event_order - b.event_order);
        nodes.forEach(node => {
            const group = groups.get(JSON.stringify([node.name, node.type]));
            const matches = ordered.filter(e => e.state_name === node.name && e.state_type === node.type);
            let status = 'PENDING';
            if (group.length > 1 && matches.length) {
                warnings.push(`No se puede atribuir el historial de "${node.name}" a una rama concreta; se muestra sin colorear.`);
            } else if (matches.length) {
                const latest = matches[matches.length - 1];
                status = latest.status;
                if (status === 'RUNNING' && node.type === 'Wait') status = 'WAITING';
            } else if (execution?.status === 'RUNNING' && execution.current_state === node.name && group.length === 1) {
                status = node.type === 'Wait' ? 'WAITING' : 'RUNNING';
            }
            if (!statuses.includes(status)) status = 'PENDING';
            lines.push(`class ${node.id} ${status};`);
        });
        statuses.forEach((status, index) => lines.push(`classDef ${status} fill:${palette[index]},stroke:#334155,color:#0f172a,stroke-width:2px;`));
        return {source: lines.join('\n'), warnings: [...new Set(warnings)]};
    }
    root.buildWorkflowDiagram = buildWorkflowDiagram;
    if (typeof module !== 'undefined') module.exports = {buildWorkflowDiagram};
    if (typeof document === 'undefined') return;
    document.addEventListener('DOMContentLoaded', async () => {
        for (const container of document.querySelectorAll('[data-workflow-diagram]')) {
            const output = container.querySelector('[data-diagram-output]');
            try {
                const payload = JSON.parse(container.querySelector('script[type="application/json"]').textContent);
                const built = buildWorkflowDiagram(payload.definition, payload.events, payload.execution);
                container.querySelector('[data-diagram-source]').textContent = built.source;
                container.querySelector('[data-diagram-warning]').textContent = built.warnings.join(' ');
                const {default: mermaid} = await import('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs');
                mermaid.initialize({startOnLoad: false, securityLevel: 'strict', flowchart: {htmlLabels: false}});
                output.textContent = built.source;
                await mermaid.run({nodes: [output]});
            } catch (error) {
                output.textContent = 'No se pudo dibujar el workflow. Comprueba la conexión al CDN. Puedes consultar la definición y el historial.';
                output.classList.add('alert', 'alert-warning');
            }
        }
    });
})(typeof globalThis !== 'undefined' ? globalThis : this);
