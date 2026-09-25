(() => {
    'use strict';

    // =========================================================
    // ELEMENTOS PRINCIPALES
    // =========================================================

    const canvas = document.getElementById('workflow-canvas');

    const workflowName =
        document.getElementById('workflow-name');

    const workflowDescription =
        document.getElementById('workflow-description');

    const canvasStatus =
        document.getElementById('canvas-status');

    const emptyMessage =
        document.getElementById('canvas-empty-message');

    const propertiesEmpty =
        document.getElementById('properties-empty');

    const propertiesForm =
        document.getElementById('properties-form');

    const designerMessage =
        document.getElementById('designer-message');

    const jsonSection =
        document.getElementById('json-section');

    const workflowJson =
        document.getElementById('workflow-json');


    // =========================================================
    // PROPIEDADES
    // =========================================================

    const propertyStateName =
        document.getElementById('property-state-name');

    const propertyStateType =
        document.getElementById('property-state-type');

    const propertyStartAt =
        document.getElementById('property-start-at');

    const propertyResource =
        document.getElementById('property-resource');

    const propertySeconds =
        document.getElementById('property-seconds');

    const propertyChoiceVariable =
        document.getElementById('property-choice-variable');

    const propertyChoiceOperator =
        document.getElementById('property-choice-operator');

    const propertyChoiceValue =
        document.getElementById('property-choice-value');

    const propertyError =
        document.getElementById('property-error');

    const propertyCause =
        document.getElementById('property-cause');

    const propertyNextContainer =
        document.getElementById('property-next-container');


    // =========================================================
    // ESTADO INTERNO
    // =========================================================

    let selectedNodeId = null;

    let startNodeId = null;

    let nodeCounter = 1;


    // =========================================================
    // INICIAR DRAWFLOW
    // =========================================================

    if (typeof Drawflow === 'undefined') {
        showMessage(
            'No se pudo cargar Drawflow.',
            'danger'
        );

        return;
    }

    const editor = new Drawflow(canvas);

    editor.reroute = true;

    editor.curvature = 0.45;

    editor.reroute_curvature_start_end = 0.5;

    editor.force_first_input = false;

    editor.start();


    // =========================================================
    // EVITAR EL MENSAJE VACÍO SOBRE DRAWFLOW
    // =========================================================

    function updateCanvasStatus() {

        const data = getNodes();

        const total =
            Object.keys(data).length;

        canvasStatus.textContent =
            `${total} ${total === 1 ? 'estado' : 'estados'}`;

        if (emptyMessage) {
            if (total === 0) {
                emptyMessage.classList.remove('d-none');
            } else {
                emptyMessage.classList.add('d-none');
            }
        }
    }


    // =========================================================
    // OBTENER NODOS
    // =========================================================

    function getNodes() {

        const exported =
            editor.export();

        return (
            exported
                ?.drawflow
                ?.Home
                ?.data || {}
        );
    }


    // =========================================================
    // MENSAJES
    // =========================================================

    function showMessage(
        message,
        type = 'info'
    ) {

        designerMessage.innerHTML = '';

        const alert =
            document.createElement('div');

        alert.className =
            `alert alert-${type}`;

        alert.style.whiteSpace = 'pre-line';

        alert.textContent = message;

        designerMessage.appendChild(alert);
    }


    function clearMessage() {
        designerMessage.innerHTML = '';
    }


    // =========================================================
    // CONFIGURACIÓN POR TIPO DE ESTADO
    // =========================================================

    function getStateConfiguration(type) {

        switch (type) {

            case 'Task':

                return {
                    inputs: 1,
                    outputs: 1,
                    data: {
                        stateName: `Task${nodeCounter}`,
                        type: 'Task',
                        resource: 'task:nueva_tarea'
                    }
                };


            case 'Choice':

                return {
                    inputs: 1,

                    // output_1 = condición verdadera
                    // output_2 = Default
                    outputs: 2,

                    data: {
                        stateName: `Choice${nodeCounter}`,
                        type: 'Choice',
                        variable: '$.valor',
                        operator: 'BooleanEquals',
                        value: true
                    }
                };


            case 'Wait':

                return {
                    inputs: 1,
                    outputs: 1,

                    data: {
                        stateName: `Wait${nodeCounter}`,
                        type: 'Wait',
                        seconds: 1
                    }
                };


            case 'Pass':

                return {
                    inputs: 1,
                    outputs: 1,

                    data: {
                        stateName: `Pass${nodeCounter}`,
                        type: 'Pass'
                    }
                };


            case 'Parallel':

                return {
                    inputs: 1,
                    outputs: 1,

                    data: {
                        stateName: `Parallel${nodeCounter}`,
                        type: 'Parallel'
                    }
                };


            case 'Succeed':

                return {
                    inputs: 1,
                    outputs: 0,

                    data: {
                        stateName: `Succeed${nodeCounter}`,
                        type: 'Succeed'
                    }
                };


            case 'Fail':

                return {
                    inputs: 1,
                    outputs: 0,

                    data: {
                        stateName: `Fail${nodeCounter}`,
                        type: 'Fail',
                        error: 'WorkflowFailed',
                        cause:
                            'El workflow terminó con error.'
                    }
                };


            default:

                throw new Error(
                    `Tipo no soportado: ${type}`
                );
        }
    }


    // =========================================================
    // HTML DEL NODO
    // =========================================================

    function getNodeHtml(
        type,
        name
    ) {

        const icons = {
            Task: '⚙',
            Choice: '◇',
            Wait: '◷',
            Pass: '○',
            Parallel: '⇉',
            Succeed: '✓',
            Fail: '✕'
        };


        let outputs = '';

        if (type === 'Choice') {

            outputs = `
                <div class="choice-labels">
                    <span>Sí</span>
                    <span>Default</span>
                </div>
            `;
        }


        return `
            <div class="step-node-content">

                <div class="step-node-header">

                    <span class="step-node-icon">
                        ${icons[type] || '○'}
                    </span>

                    <span class="step-node-type">
                        ${escapeHtml(type)}
                    </span>

                </div>

                <div class="step-node-name">
                    ${escapeHtml(name)}
                </div>

                ${outputs}

            </div>
        `;
    }


    // =========================================================
    // AGREGAR NODO
    // =========================================================

    function addNode(
        type,
        x,
        y
    ) {

        const configuration =
            getStateConfiguration(type);

        const name =
            configuration.data.stateName;

        const html =
            getNodeHtml(type, name);


        const nodeId =
            editor.addNode(
                type,
                configuration.inputs,
                configuration.outputs,
                x,
                y,
                `state-${type.toLowerCase()}`,
                configuration.data,
                html
            );


        nodeCounter++;


        // Primer estado = StartAt
        if (startNodeId === null) {
            startNodeId =
                String(nodeId);
        }


        updateCanvasStatus();

        updateStartStateStyles();

        selectNode(nodeId);


        showMessage(
            `Estado "${name}" agregado.`,
            'success'
        );
    }


    // =========================================================
    // CLICK EN LOS BOTONES
    // =========================================================

    document
        .querySelectorAll(
            '[data-state-type]'
        )
        .forEach(button => {

            button.addEventListener(
                'click',
                () => {

                    const type =
                        button.dataset.stateType;


                    const total =
                        Object.keys(
                            getNodes()
                        ).length;


                    addNode(
                        type,
                        250,
                        50 + (total * 120)
                    );
                }
            );


            // =================================================
            // DRAG
            // =================================================

            button.addEventListener(
                'dragstart',
                event => {

                    event.dataTransfer.setData(
                        'state-type',
                        button.dataset.stateType
                    );

                    event.dataTransfer.effectAllowed =
                        'copy';
                }
            );
        });


    // =========================================================
    // DROP SOBRE CANVAS
    // =========================================================

    canvas.addEventListener(
        'dragover',
        event => {

            event.preventDefault();

            event.dataTransfer.dropEffect =
                'copy';
        }
    );


    canvas.addEventListener(
        'drop',
        event => {

            event.preventDefault();

            const type =
                event.dataTransfer.getData(
                    'state-type'
                );


            if (!type) {
                return;
            }


            const rect =
                canvas.getBoundingClientRect();


            const zoom =
                editor.zoom || 1;


            const x =
                (
                    event.clientX -
                    rect.left -
                    editor.canvas_x
                ) / zoom;


            const y =
                (
                    event.clientY -
                    rect.top -
                    editor.canvas_y
                ) / zoom;


            addNode(
                type,
                x,
                y
            );
        }
    );


    // =========================================================
    // SELECCIÓN DRAWFLOW
    // =========================================================

    editor.on(
        'nodeSelected',
        id => {

            selectNode(id);
        }
    );


    editor.on(
        'nodeUnselected',
        () => {

            selectedNodeId = null;

            propertiesForm.classList.add(
                'd-none'
            );

            propertiesEmpty.classList.remove(
                'd-none'
            );
        }
    );


    // =========================================================
    // SELECCIONAR NODO
    // =========================================================

    function selectNode(id) {

        selectedNodeId =
            String(id);


        const node =
            editor.getNodeFromId(id);


        if (!node) {
            return;
        }


        propertiesEmpty.classList.add(
            'd-none'
        );

        propertiesForm.classList.remove(
            'd-none'
        );


        hideSpecificProperties();


        propertyStateName.value =
            node.data.stateName || '';

        propertyStateType.value =
            node.data.type || '';

        propertyStartAt.checked =
            String(startNodeId) ===
            String(id);


        // -----------------------------------------------------
        // TASK
        // -----------------------------------------------------

        if (node.data.type === 'Task') {

            document
                .getElementById(
                    'properties-task'
                )
                .classList.remove('d-none');


            propertyResource.value =
                node.data.resource || '';
        }


        // -----------------------------------------------------
        // WAIT
        // -----------------------------------------------------

        if (node.data.type === 'Wait') {

            document
                .getElementById(
                    'properties-wait'
                )
                .classList.remove('d-none');


            propertySeconds.value =
                node.data.seconds ?? 1;
        }


        // -----------------------------------------------------
        // CHOICE
        // -----------------------------------------------------

        if (node.data.type === 'Choice') {

            document
                .getElementById(
                    'properties-choice'
                )
                .classList.remove('d-none');


            propertyChoiceVariable.value =
                node.data.variable || '';

            propertyChoiceOperator.value =
                node.data.operator ||
                'BooleanEquals';

            propertyChoiceValue.value =
                String(
                    node.data.value ?? true
                );
        }


        // -----------------------------------------------------
        // FAIL
        // -----------------------------------------------------

        if (node.data.type === 'Fail') {

            document
                .getElementById(
                    'properties-fail'
                )
                .classList.remove('d-none');


            propertyError.value =
                node.data.error || '';

            propertyCause.value =
                node.data.cause || '';
        }


        // -----------------------------------------------------
        // Ya no necesitamos el selector Next
        // porque las conexiones visuales lo generan.
        // -----------------------------------------------------

        propertyNextContainer.classList.add(
            'd-none'
        );
    }


    function hideSpecificProperties() {

        document
            .querySelectorAll(
                '.state-properties'
            )
            .forEach(element => {

                element.classList.add(
                    'd-none'
                );
            });
    }


    // =========================================================
    // ACTUALIZAR NODO
    // =========================================================

    document
        .getElementById(
            'btn-update-state'
        )
        .addEventListener(
            'click',
            updateSelectedNode
        );


    function updateSelectedNode() {

        if (!selectedNodeId) {

            showMessage(
                'Selecciona un estado.',
                'warning'
            );

            return;
        }


        const node =
            editor.getNodeFromId(
                selectedNodeId
            );


        if (!node) {
            return;
        }


        const newName =
            propertyStateName.value.trim();


        if (!newName) {

            showMessage(
                'El estado necesita un nombre.',
                'danger'
            );

            return;
        }


        // -----------------------------------------------------
        // Evitar nombres duplicados
        // -----------------------------------------------------

        const duplicated =
            Object.entries(
                getNodes()
            )
            .some(([id, candidate]) => {

                return (
                    String(id) !==
                        String(selectedNodeId) &&

                    candidate.data.stateName ===
                        newName
                );
            });


        if (duplicated) {

            showMessage(
                `Ya existe un estado "${newName}".`,
                'danger'
            );

            return;
        }


        node.data.stateName =
            newName;


        // -----------------------------------------------------
        // StartAt
        // -----------------------------------------------------

        if (propertyStartAt.checked) {

            startNodeId =
                String(selectedNodeId);
        }


        // -----------------------------------------------------
        // Task
        // -----------------------------------------------------

        if (node.data.type === 'Task') {

            node.data.resource =
                propertyResource.value.trim();
        }


        // -----------------------------------------------------
        // Wait
        // -----------------------------------------------------

        if (node.data.type === 'Wait') {

            const seconds =
                Number(
                    propertySeconds.value
                );


            if (
                Number.isNaN(seconds) ||
                seconds < 0
            ) {

                showMessage(
                    'Seconds debe ser mayor o igual a 0.',
                    'danger'
                );

                return;
            }


            node.data.seconds =
                seconds;
        }


        // -----------------------------------------------------
        // Choice
        // -----------------------------------------------------

        if (node.data.type === 'Choice') {

            node.data.variable =
                propertyChoiceVariable
                    .value
                    .trim();


            node.data.operator =
                propertyChoiceOperator.value;


            let value =
                propertyChoiceValue
                    .value
                    .trim();


            if (
                node.data.operator ===
                'BooleanEquals'
            ) {

                if (
                    value !== 'true' &&
                    value !== 'false'
                ) {

                    showMessage(
                        'BooleanEquals acepta true o false.',
                        'danger'
                    );

                    return;
                }


                value =
                    value === 'true';
            }


            if (
                node.data.operator
                    .startsWith('Numeric')
            ) {

                const numeric =
                    Number(value);


                if (
                    Number.isNaN(
                        numeric
                    )
                ) {

                    showMessage(
                        'La comparación numérica necesita un número.',
                        'danger'
                    );

                    return;
                }


                value =
                    numeric;
            }


            node.data.value =
                value;
        }


        // -----------------------------------------------------
        // Fail
        // -----------------------------------------------------

        if (node.data.type === 'Fail') {

            node.data.error =
                propertyError.value.trim() ||
                'WorkflowFailed';


            node.data.cause =
                propertyCause.value.trim() ||
                'El workflow terminó con error.';
        }


        // Actualizar datos dentro de Drawflow
        editor.updateNodeDataFromId(
            selectedNodeId,
            node.data
        );


        updateNodeHtml(
            selectedNodeId,
            node
        );


        updateStartStateStyles();

        updateJsonPreview();


        showMessage(
            `Estado "${newName}" actualizado.`,
            'success'
        );
    }


    // =========================================================
    // ACTUALIZAR HTML DEL NODO
    // =========================================================

    function updateNodeHtml(
        nodeId,
        node
    ) {

        const content =
            document.querySelector(
                `#node-${nodeId} .drawflow_content_node`
            );


        if (!content) {
            return;
        }


        content.innerHTML =
            getNodeHtml(
                node.data.type,
                node.data.stateName
            );
    }


    // =========================================================
    // START STATE
    // =========================================================

    function updateStartStateStyles() {

        document
            .querySelectorAll(
                '.drawflow-node'
            )
            .forEach(node => {

                node.classList.remove(
                    'start-state-node'
                );
            });


        if (!startNodeId) {
            return;
        }


        const startNode =
            document.getElementById(
                `node-${startNodeId}`
            );


        if (startNode) {

            startNode.classList.add(
                'start-state-node'
            );
        }
    }


    // =========================================================
    // ELIMINAR NODO
    // =========================================================

    document
        .getElementById(
            'btn-delete-state'
        )
        .addEventListener(
            'click',
            () => {

                if (!selectedNodeId) {
                    return;
                }


                const node =
                    editor.getNodeFromId(
                        selectedNodeId
                    );


                if (!node) {
                    return;
                }


                if (
                    !window.confirm(
                        `¿Eliminar "${node.data.stateName}"?`
                    )
                ) {
                    return;
                }


                const deletedId =
                    String(selectedNodeId);


                editor.removeNodeId(
                    `node-${selectedNodeId}`
                );


                if (
                    String(startNodeId) ===
                    deletedId
                ) {

                    const remaining =
                        Object.keys(
                            getNodes()
                        );


                    startNodeId =
                        remaining[0] || null;
                }


                selectedNodeId = null;


                propertiesForm.classList.add(
                    'd-none'
                );

                propertiesEmpty.classList.remove(
                    'd-none'
                );


                updateCanvasStatus();

                updateStartStateStyles();

                updateJsonPreview();


                showMessage(
                    'Estado eliminado.',
                    'warning'
                );
            }
        );


    // =========================================================
    // EVENTOS DE CONEXIONES
    // =========================================================

    editor.on(
        'connectionCreated',
        () => {

            updateJsonPreview();
        }
    );


    editor.on(
        'connectionRemoved',
        () => {

            updateJsonPreview();
        }
    );


    editor.on(
        'nodeMoved',
        () => {

            updateJsonPreview();
        }
    );


    editor.on(
        'nodeRemoved',
        () => {

            updateCanvasStatus();
        }
    );


    // =========================================================
    // ENCONTRAR DESTINO DE UNA SALIDA
    // =========================================================

    function getOutputTarget(
        node,
        outputName
    ) {

        const connections =
            node.outputs?.[outputName]
                ?.connections || [];


        if (
            connections.length === 0
        ) {
            return null;
        }


        const targetId =
            String(
                connections[0].node
            );


        const targetNode =
            editor.getNodeFromId(
                targetId
            );


        return (
            targetNode
                ?.data
                ?.stateName || null
        );
    }


    // =========================================================
    // CONVERTIR DRAWFLOW A ASL
    // =========================================================

    function buildWorkflowDefinition() {

        const nodes =
            getNodes();


        const definition = {

            StartAt: null,

            States: {}
        };


        if (
            startNodeId &&
            nodes[startNodeId]
        ) {

            definition.StartAt =
                nodes[startNodeId]
                    .data
                    .stateName;
        }


        Object
            .entries(nodes)
            .forEach(
                ([id, node]) => {

                    const data =
                        node.data;


                    const state = {
                        Type: data.type
                    };


                    // =========================================
                    // TASK
                    // =========================================

                    if (
                        data.type === 'Task'
                    ) {

                        state.Resource =
                            data.resource;


                        const next =
                            getOutputTarget(
                                node,
                                'output_1'
                            );


                        if (next) {
                            state.Next =
                                next;
                        }
                    }


                    // =========================================
                    // PASS
                    // =========================================

                    if (
                        data.type === 'Pass'
                    ) {

                        const next =
                            getOutputTarget(
                                node,
                                'output_1'
                            );


                        if (next) {
                            state.Next =
                                next;
                        }
                    }


                    // =========================================
                    // WAIT
                    // =========================================

                    if (
                        data.type === 'Wait'
                    ) {

                        state.Seconds =
                            data.seconds;


                        const next =
                            getOutputTarget(
                                node,
                                'output_1'
                            );


                        if (next) {
                            state.Next =
                                next;
                        }
                    }


                    // =========================================
                    // PARALLEL
                    // =========================================

                    if (
                        data.type ===
                        'Parallel'
                    ) {

                        state.Branches =
                            [];


                        const next =
                            getOutputTarget(
                                node,
                                'output_1'
                            );


                        if (next) {
                            state.Next =
                                next;
                        }
                    }


                    // =========================================
                    // CHOICE
                    // =========================================

                    if (
                        data.type ===
                        'Choice'
                    ) {

                        const yesTarget =
                            getOutputTarget(
                                node,
                                'output_1'
                            );


                        const defaultTarget =
                            getOutputTarget(
                                node,
                                'output_2'
                            );


                        const condition = {

                            Variable:
                                data.variable,

                            [data.operator]:
                                data.value
                        };


                        if (yesTarget) {

                            condition.Next =
                                yesTarget;
                        }


                        state.Choices = [
                            condition
                        ];


                        if (
                            defaultTarget
                        ) {

                            state.Default =
                                defaultTarget;
                        }
                    }


                    // =========================================
                    // FAIL
                    // =========================================

                    if (
                        data.type === 'Fail'
                    ) {

                        state.Error =
                            data.error;

                        state.Cause =
                            data.cause;
                    }


                    definition.States[
                        data.stateName
                    ] = state;
                }
            );


        return definition;
    }


    // =========================================================
    // JSON
    // =========================================================

    function updateJsonPreview() {

        workflowJson.value =
            JSON.stringify(
                buildWorkflowDefinition(),
                null,
                2
            );
    }


    document
        .getElementById(
            'btn-view-json'
        )
        .addEventListener(
            'click',
            () => {

                updateJsonPreview();

                jsonSection.classList.remove(
                    'd-none'
                );


                jsonSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        );


    document
        .getElementById(
            'btn-close-json'
        )
        .addEventListener(
            'click',
            () => {

                jsonSection.classList.add(
                    'd-none'
                );
            }
        );


    // =========================================================
    // VALIDACIÓN
    // =========================================================

    function validateWorkflow() {

        const definition =
            buildWorkflowDefinition();


        const errors = [];


        if (!definition.StartAt) {

            errors.push(
                'No existe un estado inicial.'
            );
        }


        const states =
            definition.States;


        if (
            Object.keys(states).length ===
            0
        ) {

            errors.push(
                'El workflow está vacío.'
            );
        }


        Object
            .entries(states)
            .forEach(
                ([name, state]) => {

                    if (
                        [
                            'Task',
                            'Pass',
                            'Wait',
                            'Parallel'
                        ].includes(
                            state.Type
                        )
                    ) {

                        if (!state.Next) {

                            errors.push(
                                `${name}: no está conectado con el siguiente estado.`
                            );
                        }
                    }


                    if (
                        state.Type ===
                        'Task' &&
                        !state.Resource
                    ) {

                        errors.push(
                            `${name}: Task necesita Resource.`
                        );
                    }


                    if (
                        state.Type ===
                        'Choice'
                    ) {

                        if (
                            !state
                                .Choices?.[0]
                                ?.Next
                        ) {

                            errors.push(
                                `${name}: conecta la salida "Sí".`
                            );
                        }


                        if (
                            !state.Default
                        ) {

                            errors.push(
                                `${name}: conecta la salida Default.`
                            );
                        }
                    }


                    if (
                        state.Type ===
                        'Parallel' &&
                        state.Branches
                            .length === 0
                    ) {

                        // Todavía no bloqueamos.
                        // Parallel se completará
                        // en una fase posterior.
                    }
                }
            );


        if (
            errors.length > 0
        ) {

            showMessage(
                'Workflow inválido:\n\n' +
                errors.join('\n'),
                'danger'
            );


            return false;
        }


        showMessage(
            'Workflow válido.',
            'success'
        );


        return true;
    }


    document
        .getElementById(
            'btn-validate-workflow'
        )
        .addEventListener(
            'click',
            validateWorkflow
        );


    // =========================================================
    // LIMPIAR
    // =========================================================

    document
        .getElementById(
            'btn-clear-canvas'
        )
        .addEventListener(
            'click',
            clearWorkflow
        );


    function clearWorkflow() {

        if (
            Object.keys(
                getNodes()
            ).length > 0
        ) {

            if (
                !window.confirm(
                    '¿Eliminar todos los estados?'
                )
            ) {
                return;
            }
        }


        editor.clear();

        startNodeId = null;

        selectedNodeId = null;

        nodeCounter = 1;


        propertiesForm.classList.add(
            'd-none'
        );

        propertiesEmpty.classList.remove(
            'd-none'
        );


        updateCanvasStatus();

        updateJsonPreview();
    }


    // =========================================================
    // NUEVO
    // =========================================================

    document
        .getElementById(
            'btn-new-workflow'
        )
        .addEventListener(
            'click',
            () => {

                if (
                    Object.keys(
                        getNodes()
                    ).length > 0
                ) {

                    if (
                        !window.confirm(
                            '¿Crear un workflow nuevo?'
                        )
                    ) {
                        return;
                    }
                }


                editor.clear();

                startNodeId = null;

                selectedNodeId = null;

                nodeCounter = 1;


                workflowName.value = '';

                workflowDescription.value =
                    '';


                updateCanvasStatus();

                updateJsonPreview();

                clearMessage();
            }
        );


    // =========================================================
    // GUARDAR
    // =========================================================

    document
        .getElementById(
            'btn-save-workflow'
        )
        .addEventListener(
            'click',
            () => {

                if (
                    !workflowName
                        .value
                        .trim()
                ) {

                    showMessage(
                        'Escribe un nombre para el workflow.',
                        'danger'
                    );

                    return;
                }


                if (
                    !validateWorkflow()
                ) {
                    return;
                }


                const modalElement =
                    document.getElementById(
                        'saveWorkflowModal'
                    );


                const modal =
                    bootstrap.Modal
                        .getOrCreateInstance(
                            modalElement
                        );


                document
                    .getElementById(
                        'save-modal-message'
                    )
                    .textContent =
                    'El workflow está listo para guardarse.';


                modal.show();
            }
        );


    document
        .getElementById(
            'btn-confirm-save'
        )
        .addEventListener(
            'click',
            () => {

                const payload = {

                    name:
                        workflowName
                            .value
                            .trim(),

                    description:
                        workflowDescription
                            .value
                            .trim(),

                    definition:
                        buildWorkflowDefinition(),

                    is_active: true
                };


                console.log(
                    'Workflow preparado:',
                    payload
                );


                document
                    .getElementById(
                        'save-modal-message'
                    )
                    .textContent =
                    'Workflow preparado. En el siguiente paso lo enviaremos a FastAPI.';
            }
        );


    // =========================================================
    // ESCAPAR HTML
    // =========================================================

    function escapeHtml(value) {

        const div =
            document.createElement(
                'div'
            );

        div.textContent =
            value ?? '';

        return div.innerHTML;
    }


    // =========================================================
    // INICIO
    // =========================================================

    updateCanvasStatus();

    updateJsonPreview();

})();