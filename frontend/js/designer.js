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
    // PROPIEDADES GENERALES
    // =========================================================

    const propertyStateName =
        document.getElementById('property-state-name');

    const propertyStateType =
        document.getElementById('property-state-type');

    const propertyStartAt =
        document.getElementById('property-start-at');

    const propertyNextContainer =
        document.getElementById('property-next-container');


    // =========================================================
    // TASK
    // =========================================================

    const propertyResource =
        document.getElementById('property-resource');


    // =========================================================
    // RETRY
    // =========================================================

    const propertyRetryEnabled =
        document.getElementById(
            'property-retry-enabled'
        );

    const retryProperties =
        document.getElementById(
            'retry-properties'
        );

    const propertyRetryMaxAttempts =
        document.getElementById(
            'property-retry-max-attempts'
        );

    const propertyRetryInterval =
        document.getElementById(
            'property-retry-interval'
        );

    const propertyRetryBackoff =
        document.getElementById(
            'property-retry-backoff'
        );


    // =========================================================
    // CATCH
    // =========================================================

    const propertyCatchEnabled =
        document.getElementById(
            'property-catch-enabled'
        );

    const catchProperties =
        document.getElementById(
            'catch-properties'
        );

    const propertyCatchNext =
        document.getElementById(
            'property-catch-next'
        );


    // =========================================================
    // WAIT
    // =========================================================

    const propertySeconds =
        document.getElementById(
            'property-seconds'
        );


    // =========================================================
    // CHOICE
    // =========================================================

    const propertyChoiceVariable =
        document.getElementById(
            'property-choice-variable'
        );

    const propertyChoiceOperator =
        document.getElementById(
            'property-choice-operator'
        );

    const propertyChoiceValue =
        document.getElementById(
            'property-choice-value'
        );


    // =========================================================
    // FAIL
    // =========================================================

    const propertyError =
        document.getElementById(
            'property-error'
        );

    const propertyCause =
        document.getElementById(
            'property-cause'
        );


    // =========================================================
    // ESTADO INTERNO
    // =========================================================

    let selectedNodeId = null;

    let startNodeId = null;

    let nodeCounter = 1;


    // =========================================================
    // RESOURCES VÁLIDOS
    // =========================================================

    const VALID_RESOURCES = [
        'task:verificar_stock',
        'task:demo_procesar_pago',
        'task:generar_factura',
        'task:enviar_correo',
        'task:validar_pedido',
        'task:procesar_pago'
    ];


    // =========================================================
    // DRAWFLOW
    // =========================================================

    if (typeof Drawflow === 'undefined') {

        showMessage(
            'No se pudo cargar Drawflow.',
            'danger'
        );

        return;
    }


    const editor =
        new Drawflow(canvas);


    editor.reroute = true;

    editor.curvature = 0.45;

    editor.reroute_curvature_start_end =
        0.5;

    editor.force_first_input =
        false;

    editor.start();


    // =========================================================
    // UTILIDADES
    // =========================================================

    function getNodes() {

        const exported =
            editor.export();

        return (
            exported
                ?.drawflow
                ?.Home
                ?.data ||
            {}
        );
    }


    function showMessage(
        message,
        type = 'info'
    ) {

        designerMessage.innerHTML =
            '';

        const alert =
            document.createElement(
                'div'
            );

        alert.className =
            `alert alert-${type}`;

        alert.style.whiteSpace =
            'pre-line';

        alert.textContent =
            message;

        designerMessage
            .appendChild(
                alert
            );
    }


    function clearMessage() {

        designerMessage.innerHTML =
            '';
    }


    function escapeHtml(value) {

        const div =
            document.createElement(
                'div'
            );

        div.textContent =
            value ?? '';

        return div.innerHTML;
    }


    function updateCanvasStatus() {

        const nodes =
            getNodes();

        const total =
            Object.keys(nodes).length;

        canvasStatus.textContent =
            `${total} ${
                total === 1
                    ? 'estado'
                    : 'estados'
            }`;


        if (!emptyMessage) {
            return;
        }


        emptyMessage.classList.toggle(
            'd-none',
            total > 0
        );
    }


    // =========================================================
    // CONFIGURACIÓN DE ESTADOS
    // =========================================================

    function getStateConfiguration(
        type
    ) {

        switch (type) {

            case 'Task':

                return {

                    inputs: 1,

                    outputs: 1,

                    data: {

                        stateName:
                            `Task${nodeCounter}`,

                        type:
                            'Task',

                        resource:
                            'task:validar_pedido',

                        retryEnabled:
                            false,

                        retryMaxAttempts:
                            3,

                        retryIntervalSeconds:
                            1,

                        retryBackoffRate:
                            2,

                        catchEnabled:
                            false,

                        catchNext:
                            ''
                    }
                };


            case 'Choice':

                return {

                    inputs: 1,

                    outputs: 2,

                    data: {

                        stateName:
                            `Choice${nodeCounter}`,

                        type:
                            'Choice',

                        variable:
                            '$.valor',

                        operator:
                            'BooleanEquals',

                        value:
                            true
                    }
                };


            case 'Wait':

                return {

                    inputs: 1,

                    outputs: 1,

                    data: {

                        stateName:
                            `Wait${nodeCounter}`,

                        type:
                            'Wait',

                        seconds:
                            1
                    }
                };


            case 'Pass':

                return {

                    inputs: 1,

                    outputs: 1,

                    data: {

                        stateName:
                            `Pass${nodeCounter}`,

                        type:
                            'Pass'
                    }
                };


            case 'Parallel':

                return {

                    inputs: 1,

                    outputs: 1,

                    data: {

                        stateName:
                            `Parallel${nodeCounter}`,

                        type:
                            'Parallel'
                    }
                };


            case 'Succeed':

                return {

                    inputs: 1,

                    outputs: 0,

                    data: {

                        stateName:
                            `Succeed${nodeCounter}`,

                        type:
                            'Succeed'
                    }
                };


            case 'Fail':

                return {

                    inputs: 1,

                    outputs: 0,

                    data: {

                        stateName:
                            `Fail${nodeCounter}`,

                        type:
                            'Fail',

                        error:
                            'WorkflowFailed',

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


        let extra = '';


        if (
            type ===
            'Choice'
        ) {

            extra = `

                <div class="choice-labels">

                    <span>
                        Sí
                    </span>

                    <span>
                        Default
                    </span>

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


                ${extra}

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


        const html =
            getNodeHtml(
                type,
                configuration.data.stateName
            );


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


        // Primer nodo = StartAt
        if (
            startNodeId === null
        ) {

            startNodeId =
                String(nodeId);
        }


        updateCanvasStatus();

        updateStartStateStyles();

        selectNode(nodeId);


        showMessage(
            `Estado "${configuration.data.stateName}" agregado.`,
            'success'
        );
    }


    // =========================================================
    // BOTONES DEL PANEL IZQUIERDO
    // =========================================================

    document
        .querySelectorAll(
            '[data-state-type]'
        )
        .forEach(
            button => {

                button.addEventListener(
                    'click',
                    () => {

                        const type =
                            button.dataset
                                .stateType;


                        const total =
                            Object.keys(
                                getNodes()
                            ).length;


                        addNode(
                            type,
                            250,
                            50 +
                            total * 120
                        );
                    }
                );


                button.addEventListener(
                    'dragstart',
                    event => {

                        event
                            .dataTransfer
                            .setData(
                                'state-type',
                                button.dataset
                                    .stateType
                            );


                        event
                            .dataTransfer
                            .effectAllowed =
                            'copy';
                    }
                );
            }
        );


    // =========================================================
    // DRAG & DROP
    // =========================================================

    canvas.addEventListener(
        'dragover',
        event => {

            event.preventDefault();

            event.dataTransfer
                .dropEffect =
                'copy';
        }
    );


    canvas.addEventListener(
        'drop',
        event => {

            event.preventDefault();


            const type =
                event.dataTransfer
                    .getData(
                        'state-type'
                    );


            if (!type) {
                return;
            }


            const rect =
                canvas
                    .getBoundingClientRect();


            const zoom =
                editor.zoom || 1;


            const x =
                (
                    event.clientX -
                    rect.left -
                    editor.canvas_x
                ) /
                zoom;


            const y =
                (
                    event.clientY -
                    rect.top -
                    editor.canvas_y
                ) /
                zoom;


            addNode(
                type,
                x,
                y
            );
        }
    );


    // =========================================================
    // EVENTOS DRAWFLOW
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

            selectedNodeId =
                null;


            propertiesForm
                .classList
                .add(
                    'd-none'
                );


            propertiesEmpty
                .classList
                .remove(
                    'd-none'
                );
        }
    );


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

            updateJsonPreview();
        }
    );


    // =========================================================
    // MOSTRAR / OCULTAR RETRY
    // =========================================================

    propertyRetryEnabled
        .addEventListener(
            'change',
            () => {

                retryProperties
                    .classList
                    .toggle(
                        'd-none',
                        !propertyRetryEnabled
                            .checked
                    );
            }
        );


    // =========================================================
    // MOSTRAR / OCULTAR CATCH
    // =========================================================

    propertyCatchEnabled
        .addEventListener(
            'change',
            () => {

                catchProperties
                    .classList
                    .toggle(
                        'd-none',
                        !propertyCatchEnabled
                            .checked
                    );


                if (
                    propertyCatchEnabled
                        .checked
                ) {

                    populateCatchTargets(
                        propertyCatchNext
                            .value
                    );
                }
            }
        );


    // =========================================================
    // OCULTAR PROPIEDADES ESPECÍFICAS
    // =========================================================

    function hideSpecificProperties() {

        document
            .querySelectorAll(
                '.state-properties'
            )
            .forEach(
                element => {

                    element
                        .classList
                        .add(
                            'd-none'
                        );
                }
            );
    }


    // =========================================================
    // DESTINOS DE CATCH
    // =========================================================

    function populateCatchTargets(
        selectedValue = ''
    ) {

        propertyCatchNext
            .innerHTML =
            '<option value="">Selecciona un estado</option>';


        Object
            .entries(
                getNodes()
            )
            .forEach(
                ([id, node]) => {

                    // No permitir que Catch apunte
                    // al mismo Task.
                    if (
                        String(id) ===
                        String(
                            selectedNodeId
                        )
                    ) {
                        return;
                    }


                    const option =
                        document.createElement(
                            'option'
                        );


                    option.value =
                        node.data
                            .stateName;


                    option.textContent =
                        `${node.data.stateName} (${node.data.type})`;


                    if (
                        node.data.stateName ===
                        selectedValue
                    ) {

                        option.selected =
                            true;
                    }


                    propertyCatchNext
                        .appendChild(
                            option
                        );
                }
            );
    }


    // =========================================================
    // SELECCIONAR NODO
    // =========================================================

    function selectNode(id) {

        selectedNodeId =
            String(id);


        const node =
            editor
                .getNodeFromId(id);


        if (!node) {
            return;
        }


        propertiesEmpty
            .classList
            .add(
                'd-none'
            );


        propertiesForm
            .classList
            .remove(
                'd-none'
            );


        hideSpecificProperties();


        propertyStateName.value =
            node.data
                .stateName || '';


        propertyStateType.value =
            node.data
                .type || '';


        propertyStartAt.checked =
            String(startNodeId) ===
            String(id);


        // =====================================================
        // TASK
        // =====================================================

        if (
            node.data.type ===
            'Task'
        ) {

            document
                .getElementById(
                    'properties-task'
                )
                .classList
                .remove(
                    'd-none'
                );


            propertyResource.value =
                node.data.resource ||
                'task:validar_pedido';


            // -------------------------------------------------
            // RETRY
            // -------------------------------------------------

            propertyRetryEnabled
                .checked =
                node.data
                    .retryEnabled ===
                true;


            propertyRetryMaxAttempts
                .value =
                node.data
                    .retryMaxAttempts ??
                3;


            propertyRetryInterval
                .value =
                node.data
                    .retryIntervalSeconds ??
                1;


            propertyRetryBackoff
                .value =
                node.data
                    .retryBackoffRate ??
                2;


            retryProperties
                .classList
                .toggle(
                    'd-none',
                    !propertyRetryEnabled
                        .checked
                );


            // -------------------------------------------------
            // CATCH
            // -------------------------------------------------

            propertyCatchEnabled
                .checked =
                node.data
                    .catchEnabled ===
                true;


            populateCatchTargets(
                node.data
                    .catchNext ||
                ''
            );


            catchProperties
                .classList
                .toggle(
                    'd-none',
                    !propertyCatchEnabled
                        .checked
                );
        }


        // =====================================================
        // WAIT
        // =====================================================

        if (
            node.data.type ===
            'Wait'
        ) {

            document
                .getElementById(
                    'properties-wait'
                )
                .classList
                .remove(
                    'd-none'
                );


            propertySeconds.value =
                node.data
                    .seconds ??
                1;
        }


        // =====================================================
        // CHOICE
        // =====================================================

        if (
            node.data.type ===
            'Choice'
        ) {

            document
                .getElementById(
                    'properties-choice'
                )
                .classList
                .remove(
                    'd-none'
                );


            propertyChoiceVariable
                .value =
                node.data
                    .variable ||
                '$.valor';


            propertyChoiceOperator
                .value =
                node.data
                    .operator ||
                'BooleanEquals';


            propertyChoiceValue
                .value =
                String(
                    node.data
                        .value ??
                    true
                );
        }


        // =====================================================
        // FAIL
        // =====================================================

        if (
            node.data.type ===
            'Fail'
        ) {

            document
                .getElementById(
                    'properties-fail'
                )
                .classList
                .remove(
                    'd-none'
                );


            propertyError.value =
                node.data
                    .error ||
                'WorkflowFailed';


            propertyCause.value =
                node.data
                    .cause ||
                '';
        }


        // Next visual se obtiene mediante conexiones
        propertyNextContainer
            .classList
            .add(
                'd-none'
            );
    }

    // =========================================================
    // ACTUALIZAR REFERENCIAS CATCH AL RENOMBRAR UN ESTADO
    // =========================================================

    function updateCatchReferences(
        oldName,
        newName
    ) {

        if (
            !oldName ||
            !newName ||
            oldName === newName
        ) {
            return;
        }


        Object
            .entries(
                getNodes()
            )
            .forEach(
                ([id, candidate]) => {

                    if (
                        candidate.data.type !==
                        'Task'
                    ) {
                        return;
                    }


                    if (
                        candidate.data.catchNext !==
                        oldName
                    ) {
                        return;
                    }


                    const realNode =
                        editor.getNodeFromId(
                            id
                        );


                    if (!realNode) {
                        return;
                    }


                    const updatedData = {
                        ...realNode.data,

                        catchNext:
                            newName
                    };


                    editor
                        .updateNodeDataFromId(
                            id,
                            updatedData
                        );
                }
            );
    }

    // =========================================================
    // ACTUALIZAR ESTADO
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

    // =====================================================
    // COMPROBAR SELECCIÓN
    // =====================================================

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


    // =====================================================
    // CONSERVAR NOMBRE ORIGINAL
    // =====================================================

    const oldName =
        node.data.stateName;


    const newName =
        propertyStateName
            .value
            .trim();


    // =====================================================
    // VALIDAR NOMBRE
    // =====================================================

    if (!newName) {

        showMessage(
            'El estado necesita un nombre.',
            'danger'
        );

        return;
    }


    // =====================================================
    // EVITAR NOMBRES DUPLICADOS
    // =====================================================

    const duplicated =
        Object
            .entries(
                getNodes()
            )
            .some(
                ([id, candidate]) => {

                    return (
                        String(id) !==
                            String(
                                selectedNodeId
                            ) &&

                        candidate.data
                            .stateName ===
                            newName
                    );
                }
            );


    if (duplicated) {

        showMessage(
            `Ya existe un estado "${newName}".`,
            'danger'
        );

        return;
    }


    // =====================================================
    // CREAR COPIA TEMPORAL
    //
    // IMPORTANTE:
    // todavía NO modificamos Drawflow.
    // =====================================================

    const updatedData = {
        ...node.data,

        stateName:
            newName
    };


    // =====================================================
    // TASK
    // =====================================================

    if (
        node.data.type ===
        'Task'
    ) {

        // -------------------------------------------------
        // RESOURCE
        // -------------------------------------------------

        const resource =
            propertyResource
                .value
                .trim();


        if (!resource) {

            showMessage(
                'Task necesita un Resource.',
                'danger'
            );

            return;
        }


        if (
            !VALID_RESOURCES.includes(
                resource
            )
        ) {

            showMessage(
                `Resource no registrado: ${resource}.`,
                'danger'
            );

            return;
        }


        updatedData.resource =
            resource;


        // =================================================
        // RETRY
        // =================================================

        updatedData.retryEnabled =
            propertyRetryEnabled
                .checked;


        if (
            updatedData.retryEnabled
        ) {

            const maxAttempts =
                Number(
                    propertyRetryMaxAttempts
                        .value
                );


            const intervalSeconds =
                Number(
                    propertyRetryInterval
                        .value
                );


            const backoffRate =
                Number(
                    propertyRetryBackoff
                        .value
                );


            // ---------------------------------------------
            // MAX ATTEMPTS
            // ---------------------------------------------

            if (
                !Number.isInteger(
                    maxAttempts
                ) ||
                maxAttempts < 0
            ) {

                showMessage(
                    'MaxAttempts debe ser un entero mayor o igual a 0.',
                    'danger'
                );

                return;
            }


            // ---------------------------------------------
            // INTERVAL SECONDS
            // ---------------------------------------------

            if (
                !Number.isFinite(
                    intervalSeconds
                ) ||
                intervalSeconds < 0
            ) {

                showMessage(
                    'IntervalSeconds debe ser un número mayor o igual a 0.',
                    'danger'
                );

                return;
            }


            // ---------------------------------------------
            // BACKOFF RATE
            // ---------------------------------------------

            if (
                !Number.isFinite(
                    backoffRate
                ) ||
                backoffRate < 1
            ) {

                showMessage(
                    'BackoffRate debe ser un número mayor o igual a 1.',
                    'danger'
                );

                return;
            }


            // Todos los datos son válidos.
            // Ahora sí los guardamos en la copia.

            updatedData.retryMaxAttempts =
                maxAttempts;


            updatedData.retryIntervalSeconds =
                intervalSeconds;


            updatedData.retryBackoffRate =
                backoffRate;
        }


        // =================================================
        // CATCH
        // =================================================

        updatedData.catchEnabled =
            propertyCatchEnabled
                .checked;


        if (
            updatedData.catchEnabled
        ) {

            const catchNext =
                propertyCatchNext
                    .value;


            if (!catchNext) {

                showMessage(
                    'Selecciona un estado de destino para Catch.',
                    'danger'
                );

                return;
            }


            // -------------------------------------------------
            // VALIDAR QUE EL DESTINO EXISTA
            // -------------------------------------------------

            const targetExists =
                Object
                    .values(
                        getNodes()
                    )
                    .some(
                        candidate => {

                            return (
                                candidate.data
                                    .stateName ===
                                catchNext
                            );
                        }
                    );


            if (!targetExists) {

                showMessage(
                    `El estado de destino Catch "${catchNext}" no existe.`,
                    'danger'
                );

                return;
            }


            // -------------------------------------------------
            // EVITAR CATCH AL MISMO TASK
            // -------------------------------------------------

            if (
                catchNext ===
                    oldName ||
                catchNext ===
                    newName
            ) {

                showMessage(
                    'Catch no puede apuntar al mismo Task.',
                    'danger'
                );

                return;
            }


            updatedData.catchNext =
                catchNext;

        } else {

            updatedData.catchNext =
                '';
        }
    }


    // =====================================================
    // WAIT
    // =====================================================

    if (
        node.data.type ===
        'Wait'
    ) {

        const seconds =
            Number(
                propertySeconds.value
            );


        if (
            !Number.isFinite(
                seconds
            ) ||
            seconds < 0
        ) {

            showMessage(
                'Seconds debe ser mayor o igual a 0.',
                'danger'
            );

            return;
        }


        updatedData.seconds =
            seconds;
    }


    // =====================================================
    // CHOICE
    // =====================================================

    if (
        node.data.type ===
        'Choice'
    ) {

        const variable =
            propertyChoiceVariable
                .value
                .trim();


        if (!variable) {

            showMessage(
                'Choice necesita una variable.',
                'danger'
            );

            return;
        }


        const operator =
            propertyChoiceOperator
                .value;


        let value =
            propertyChoiceValue
                .value
                .trim();


        // -------------------------------------------------
        // BOOLEAN
        // -------------------------------------------------

        if (
            operator ===
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
                value ===
                'true';
        }


        // -------------------------------------------------
        // NUMERIC
        // -------------------------------------------------

        if (
            operator.startsWith(
                'Numeric'
            )
        ) {

            const numericValue =
                Number(value);


            if (
                !Number.isFinite(
                    numericValue
                )
            ) {

                showMessage(
                    'La comparación numérica necesita un número.',
                    'danger'
                );

                return;
            }


            value =
                numericValue;
        }


        updatedData.variable =
            variable;


        updatedData.operator =
            operator;


        updatedData.value =
            value;
    }


    // =====================================================
    // FAIL
    // =====================================================

    if (
        node.data.type ===
        'Fail'
    ) {

        updatedData.error =
            propertyError
                .value
                .trim() ||
            'WorkflowFailed';


        updatedData.cause =
            propertyCause
                .value
                .trim() ||
            'El workflow terminó con error.';
    }


    // =====================================================
    // TODAS LAS VALIDACIONES PASARON
    //
    // A partir de aquí SÍ modificamos Drawflow.
    // =====================================================

    editor
        .updateNodeDataFromId(
            selectedNodeId,
            updatedData
        );


    // =====================================================
    // ACTUALIZAR REFERENCIAS CATCH
    // =====================================================

    if (
        oldName !==
        newName
    ) {

        updateCatchReferences(
            oldName,
            newName
        );
    }


    // =====================================================
    // START AT
    // =====================================================

    if (
        propertyStartAt.checked
    ) {

        startNodeId =
            String(
                selectedNodeId
            );
    }


    // =====================================================
    // ACTUALIZAR HTML DEL NODO
    // =====================================================

    const updatedNode =
        editor.getNodeFromId(
            selectedNodeId
        );


    if (updatedNode) {

        updateNodeHtml(
            selectedNodeId,
            updatedNode
        );
    }


    // =====================================================
    // ACTUALIZAR INTERFAZ
    // =====================================================

    updateStartStateStyles();

    updateJsonPreview();


    // Actualizar selector Catch por si cambió algún nombre
    if (
        updatedNode &&
        updatedNode.data.type ===
        'Task'
    ) {

        populateCatchTargets(
            updatedNode.data
                .catchNext ||
            ''
        );
    }


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
            .forEach(
                node => {

                    node.classList
                        .remove(
                            'start-state-node'
                        );
                }
            );


        if (!startNodeId) {
            return;
        }


        const startNode =
            document.getElementById(
                `node-${startNodeId}`
            );


        if (startNode) {

            startNode
                .classList
                .add(
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
                    editor
                        .getNodeFromId(
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


                const deletedName =
                    node.data.stateName;


                const deletedId =
                    String(
                        selectedNodeId
                    );


                editor.removeNodeId(
                    `node-${selectedNodeId}`
                );


                // Limpiar Catch que apunte
                // al nodo eliminado.
                Object
                    .values(
                        getNodes()
                    )
                    .forEach(
                        candidate => {

                            if (
                                candidate.data
                                    .catchNext ===
                                deletedName
                            ) {

                                candidate.data
                                    .catchNext =
                                    '';

                                candidate.data
                                    .catchEnabled =
                                    false;


                                editor
                                    .updateNodeDataFromId(
                                        candidate.id,
                                        candidate.data
                                    );
                            }
                        }
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
                        remaining[0] ||
                        null;
                }


                selectedNodeId =
                    null;


                propertiesForm
                    .classList
                    .add(
                        'd-none'
                    );


                propertiesEmpty
                    .classList
                    .remove(
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
    // DESTINO DE UNA CONEXIÓN
    // =========================================================

    function getOutputTarget(
        node,
        outputName
    ) {

        const connections =
            node.outputs
                ?.[outputName]
                ?.connections ||
            [];


        if (
            connections.length === 0
        ) {

            return null;
        }


        const targetId =
            String(
                connections[0]
                    .node
            );


        const targetNode =
            editor
                .getNodeFromId(
                    targetId
                );


        return (
            targetNode
                ?.data
                ?.stateName ||
            null
        );
    }


    // =========================================================
    // CONVERTIR DRAWFLOW A WORKFLOW JSON
    // =========================================================

    function buildWorkflowDefinition() {

        const nodes =
            getNodes();


        const definition = {

            StartAt:
                null,

            States:
                {}
        };


        if (
            startNodeId &&
            nodes[startNodeId]
        ) {

            definition.StartAt =
                nodes[
                    startNodeId
                ]
                    .data
                    .stateName;
        }


        Object
            .entries(
                nodes
            )
            .forEach(
                ([id, node]) => {

                    const data =
                        node.data;


                    const state = {

                        Type:
                            data.type
                    };


                    // =================================================
                    // TASK
                    // =================================================

                    if (
                        data.type ===
                        'Task'
                    ) {

                        state.Resource =
                            data.resource;


                        // ---------------------------------------------
                        // RETRY
                        // ---------------------------------------------

                        if (
                            data.retryEnabled
                        ) {

                            state.Retry = [
                                {

                                    ErrorEquals: [
                                        'States.ALL'
                                    ],

                                    IntervalSeconds:
                                        data.retryIntervalSeconds ??
                                        1,

                                    MaxAttempts:
                                        data.retryMaxAttempts ??
                                        3,

                                    BackoffRate:
                                        data.retryBackoffRate ??
                                        2
                                }
                            ];
                        }


                        // ---------------------------------------------
                        // CATCH
                        // ---------------------------------------------

                        if (
                            data.catchEnabled &&
                            data.catchNext
                        ) {

                            state.Catch = [
                                {

                                    ErrorEquals: [
                                        'States.ALL'
                                    ],

                                    Next:
                                        data.catchNext
                                }
                            ];
                        }


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


                    // =================================================
                    // PASS
                    // =================================================

                    if (
                        data.type ===
                        'Pass'
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


                    // =================================================
                    // WAIT
                    // =================================================

                    if (
                        data.type ===
                        'Wait'
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


                    // =================================================
                    // PARALLEL
                    // =================================================

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


                    // =================================================
                    // CHOICE
                    // =================================================

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


                    // =================================================
                    // FAIL
                    // =================================================

                    if (
                        data.type ===
                        'Fail'
                    ) {

                        state.Error =
                            data.error;


                        state.Cause =
                            data.cause;
                    }


                    definition
                        .States[
                            data.stateName
                        ] =
                        state;
                }
            );


        return definition;
    }


    // =========================================================
    // JSON PREVIEW
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


                jsonSection
                    .classList
                    .remove(
                        'd-none'
                    );


                jsonSection
                    .scrollIntoView(
                        {
                            behavior:
                                'smooth',

                            block:
                                'start'
                        }
                    );
            }
        );


    document
        .getElementById(
            'btn-close-json'
        )
        .addEventListener(
            'click',
            () => {

                jsonSection
                    .classList
                    .add(
                        'd-none'
                    );
            }
        );


    // =========================================================
    // VALIDAR WORKFLOW
    // =========================================================

    function validateWorkflow() {

        const definition =
            buildWorkflowDefinition();


        const errors =
            [];


        if (
            !definition.StartAt
        ) {

            errors.push(
                'No existe un estado inicial.'
            );
        }


        const states =
            definition.States;


        if (
            Object.keys(states)
                .length ===
            0
        ) {

            errors.push(
                'El workflow está vacío.'
            );
        }


        Object
            .entries(
                states
            )
            .forEach(
                ([name, state]) => {

                    // ---------------------------------------------
                    // ESTADOS QUE REQUIEREN NEXT
                    // ---------------------------------------------

                    if (
                        [
                            'Task',
                            'Pass',
                            'Wait',
                            'Parallel'
                        ]
                            .includes(
                                state.Type
                            )
                    ) {

                        if (!state.Next) {

                            errors.push(
                                `${name}: no está conectado con el siguiente estado.`
                            );
                        }
                    }


                    // ---------------------------------------------
                    // TASK
                    // ---------------------------------------------

                    if (
                        state.Type ===
                        'Task'
                    ) {

                        if (
                            !state.Resource
                        ) {

                            errors.push(
                                `${name}: Task necesita Resource.`
                            );

                        } else if (
                            !VALID_RESOURCES
                                .includes(
                                    state.Resource
                                )
                        ) {

                            errors.push(
                                `${name}: Resource no registrado: ${state.Resource}.`
                            );
                        }


                        // -----------------------------------------
                        // RETRY
                        // -----------------------------------------

                        if (
                            state.Retry
                        ) {

                            const retry =
                                state.Retry[0];


                            if (
                                !Array.isArray(
                                    retry.ErrorEquals
                                ) ||
                                retry.ErrorEquals
                                    .length ===
                                0
                            ) {

                                errors.push(
                                    `${name}: Retry necesita ErrorEquals.`
                                );
                            }


                            if (
                                !Number.isInteger(
                                    retry.MaxAttempts
                                ) ||
                                retry.MaxAttempts <
                                0
                            ) {

                                errors.push(
                                    `${name}: MaxAttempts debe ser un entero >= 0.`
                                );
                            }


                            if (
                                !Number.isFinite(
                                    retry.IntervalSeconds
                                ) ||
                                retry.IntervalSeconds <
                                0
                            ) {

                                errors.push(
                                    `${name}: IntervalSeconds debe ser >= 0.`
                                );
                            }


                            if (
                                !Number.isFinite(
                                    retry.BackoffRate
                                ) ||
                                retry.BackoffRate <
                                1
                            ) {

                                errors.push(
                                    `${name}: BackoffRate debe ser >= 1.`
                                );
                            }
                        }


                        // -----------------------------------------
                        // CATCH
                        // -----------------------------------------

                        if (
                            state.Catch
                        ) {

                            const catchRule =
                                state.Catch[0];


                            if (
                                !catchRule.Next
                            ) {

                                errors.push(
                                    `${name}: Catch necesita un estado de destino.`
                                );

                            } else if (
                                !states[
                                    catchRule.Next
                                ]
                            ) {

                                errors.push(
                                    `${name}: Catch apunta a un estado inexistente: ${catchRule.Next}.`
                                );
                            }


                            if (
                                catchRule.Next ===
                                name
                            ) {

                                errors.push(
                                    `${name}: Catch no puede apuntar al mismo estado.`
                                );
                            }
                        }
                    }


                    // ---------------------------------------------
                    // CHOICE
                    // ---------------------------------------------

                    if (
                        state.Type ===
                        'Choice'
                    ) {

                        if (
                            !state
                                .Choices
                                ?.[0]
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


                    // ---------------------------------------------
                    // PARALLEL
                    // ---------------------------------------------

                    if (
                        state.Type ===
                        'Parallel' &&
                        state.Branches
                            .length ===
                        0
                    ) {

                        errors.push(
                            `${name}: Parallel todavía no puede configurarse desde el diseñador visual.`
                        );
                    }
                }
            );


        if (
            errors.length >
            0
        ) {

            showMessage(
                'Workflow inválido:\n\n' +
                errors.join(
                    '\n'
                ),
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
    // LIMPIAR LIENZO
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
            ).length >
            0
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


        startNodeId =
            null;

        selectedNodeId =
            null;

        nodeCounter =
            1;


        propertiesForm
            .classList
            .add(
                'd-none'
            );


        propertiesEmpty
            .classList
            .remove(
                'd-none'
            );


        updateCanvasStatus();

        updateJsonPreview();
    }


    // =========================================================
    // NUEVO WORKFLOW
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
                    ).length >
                    0
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


                startNodeId =
                    null;

                selectedNodeId =
                    null;

                nodeCounter =
                    1;


                workflowName.value =
                    '';

                workflowDescription
                    .value =
                    '';


                propertiesForm
                    .classList
                    .add(
                        'd-none'
                    );


                propertiesEmpty
                    .classList
                    .remove(
                        'd-none'
                    );


                updateCanvasStatus();

                updateJsonPreview();

                clearMessage();
            }
        );


    // =========================================================
    // GUARDAR WORKFLOW
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


    // =========================================================
    // CONFIRMAR GUARDADO
    // =========================================================

    document
        .getElementById(
            'btn-confirm-save'
        )
        .addEventListener(
            'click',
            async () => {

                if (
                    !validateWorkflow()
                ) {

                    return;
                }


                const button =
                    document.getElementById(
                        'btn-confirm-save'
                    );


                const message =
                    document.getElementById(
                        'save-modal-message'
                    );


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

                    is_active:
                        true
                };


                button.disabled =
                    true;


                const originalText =
                    button.textContent;


                button.textContent =
                    'Guardando...';


                message.className =
                    'small text-secondary';


                message.textContent =
                    'Enviando workflow al servidor...';


                try {

                    const response =
                        await fetch(
                            'api/workflow-save.php',
                            {

                                method:
                                    'POST',

                                headers: {

                                    'Content-Type':
                                        'application/json',

                                    'Accept':
                                        'application/json'
                                },

                                body:
                                    JSON.stringify(
                                        payload
                                    )
                            }
                        );


                    let result;


                    try {

                        result =
                            await response
                                .json();

                    } catch {

                        throw new Error(
                            'El servidor devolvió una respuesta inválida.'
                        );
                    }


                    if (
                        !response.ok ||
                        !result.success
                    ) {

                        throw new Error(
                            result.message ||
                            'No se pudo guardar el workflow.'
                        );
                    }


                    const workflow =
                        result.workflow;


                    message.className =
                        'small text-success';


                    message.textContent =
                        `Workflow guardado correctamente. ID: ${workflow.id}`;


                    showMessage(
                        `Workflow "${workflow.name}" guardado correctamente.`,
                        'success'
                    );


                    const modalElement =
                        document.getElementById(
                            'saveWorkflowModal'
                        );


                    const modal =
                        bootstrap.Modal
                            .getInstance(
                                modalElement
                            );


                    setTimeout(
                        () => {

                            if (modal) {

                                modal.hide();
                            }


                            window.location.href =
                                `workflow-view.php?id=${workflow.id}`;
                        },
                        700
                    );


                } catch (error) {

                    console.error(
                        'Error guardando workflow:',
                        error
                    );


                    message.className =
                        'small text-danger';


                    message.textContent =
                        error.message;


                    showMessage(
                        `No se pudo guardar el workflow:\n${error.message}`,
                        'danger'
                    );


                } finally {

                    button.disabled =
                        false;


                    button.textContent =
                        originalText;
                }
            }
        );


    // =========================================================
    // INICIO
    // =========================================================

    updateCanvasStatus();

    updateStartStateStyles();

    updateJsonPreview();

})();