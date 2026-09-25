<?php

require __DIR__ . '/includes/layout.php';

page_start('Diseñador de Workflow');

?>

<!-- Drawflow -->
<link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/drawflow@0.0.60/dist/drawflow.min.css"
>

<!-- Estilos propios -->
<link rel="stylesheet" href="css/designer.css">

<div class="workflow-designer">

    <!-- ===================================================== -->
    <!-- BARRA SUPERIOR -->
    <!-- ===================================================== -->

    <div class="designer-toolbar mb-3">

        <div>
            <h2 class="h5 mb-1">Workflow Studio</h2>

            <p class="text-secondary mb-0">
                Construye visualmente una máquina de estados.
            </p>
        </div>

        <div class="designer-actions">

            <button
                type="button"
                class="btn btn-outline-secondary"
                id="btn-new-workflow"
            >
                Nuevo
            </button>

            <button
                type="button"
                class="btn btn-outline-primary"
                id="btn-validate-workflow"
            >
                Validar
            </button>

            <button
                type="button"
                class="btn btn-outline-dark"
                id="btn-view-json"
            >
                Ver JSON
            </button>

            <button
                type="button"
                class="btn btn-primary"
                id="btn-save-workflow"
            >
                Guardar
            </button>

        </div>

    </div>


    <!-- ===================================================== -->
    <!-- INFORMACIÓN DEL WORKFLOW -->
    <!-- ===================================================== -->

    <div class="card mb-3">

        <div class="card-body">

            <div class="row g-3">

                <div class="col-md-5">

                    <label
                        for="workflow-name"
                        class="form-label"
                    >
                        Nombre del workflow
                    </label>

                    <input
                        type="text"
                        class="form-control"
                        id="workflow-name"
                        maxlength="150"
                        placeholder="Ejemplo: Procesamiento de pedido"
                    >

                </div>

                <div class="col-md-7">

                    <label
                        for="workflow-description"
                        class="form-label"
                    >
                        Descripción
                    </label>

                    <input
                        type="text"
                        class="form-control"
                        id="workflow-description"
                        placeholder="Describe brevemente el proceso"
                    >

                </div>

            </div>

        </div>

    </div>


    <!-- ===================================================== -->
    <!-- ÁREA PRINCIPAL -->
    <!-- ===================================================== -->

    <div class="designer-layout">


        <!-- ================================================= -->
        <!-- PANEL IZQUIERDO: ESTADOS -->
        <!-- ================================================= -->

        <aside class="designer-sidebar">

            <h3 class="h6 mb-3">
                Estados
            </h3>

            <p class="small text-secondary">
                Agrega los bloques al workflow.
            </p>


            <div class="state-list">


                <!-- TASK -->

                <button
                    type="button"
                    class="state-item"
                    data-state-type="Task"
                    draggable="true"
                >

                    <span class="state-icon">
                        ⚙
                    </span>

                    <span>
                        <strong>Task</strong>

                        <small>
                            Ejecuta una tarea
                        </small>
                    </span>

                </button>


                <!-- CHOICE -->

                <button
                    type="button"
                    class="state-item"
                    data-state-type="Choice"
                    draggable="true"
                >

                    <span class="state-icon">
                        ◇
                    </span>

                    <span>
                        <strong>Choice</strong>

                        <small>
                            Evalúa una condición
                        </small>
                    </span>

                </button>


                <!-- WAIT -->

                <button
                    type="button"
                    class="state-item"
                    data-state-type="Wait"
                    draggable="true"
                >

                    <span class="state-icon">
                        ◷
                    </span>

                    <span>
                        <strong>Wait</strong>

                        <small>
                            Espera un tiempo
                        </small>
                    </span>

                </button>


                <!-- PASS -->

                <button
                    type="button"
                    class="state-item"
                    data-state-type="Pass"
                    draggable="true"
                >

                    <span class="state-icon">
                        ○
                    </span>

                    <span>
                        <strong>Pass</strong>

                        <small>
                            Continúa sin tarea externa
                        </small>
                    </span>

                </button>


                <!-- PARALLEL -->

                <button
                    type="button"
                    class="state-item"
                    data-state-type="Parallel"
                    draggable="true"
                >

                    <span class="state-icon">
                        ⇉
                    </span>

                    <span>
                        <strong>Parallel</strong>

                        <small>
                            Ejecuta ramas paralelas
                        </small>
                    </span>

                </button>


                <!-- SUCCEED -->

                <button
                    type="button"
                    class="state-item"
                    data-state-type="Succeed"
                    draggable="true"
                >

                    <span class="state-icon">
                        ✓
                    </span>

                    <span>
                        <strong>Succeed</strong>

                        <small>
                            Final exitoso
                        </small>
                    </span>

                </button>


                <!-- FAIL -->

                <button
                    type="button"
                    class="state-item"
                    data-state-type="Fail"
                    draggable="true"
                >

                    <span class="state-icon">
                        ✕
                    </span>

                    <span>
                        <strong>Fail</strong>

                        <small>
                            Final con error
                        </small>
                    </span>

                </button>


            </div>

        </aside>


        <!-- ================================================= -->
        <!-- CENTRO: LIENZO -->
        <!-- ================================================= -->

        <section class="designer-canvas-container">

            <div class="canvas-header">

                <div>

                    <strong>
                        Lienzo
                    </strong>

                    <span
                        class="text-secondary small ms-2"
                        id="canvas-status"
                    >
                        0 estados
                    </span>

                </div>

                <button
                    type="button"
                    class="btn btn-sm btn-outline-danger"
                    id="btn-clear-canvas"
                >
                    Limpiar
                </button>

            </div>


            <div
                id="workflow-canvas"
                class="workflow-canvas"
            >

                <div
                    id="canvas-empty-message"
                    class="canvas-empty-message"
                >

                    <div class="display-6 mb-3">
                        +
                    </div>

                    <p class="mb-1">
                        El workflow está vacío.
                    </p>

                    <small class="text-secondary">
                        Selecciona un estado del panel izquierdo.
                    </small>

                </div>

            </div>

        </section>


        <!-- ================================================= -->
        <!-- PANEL DERECHO: PROPIEDADES -->
        <!-- ================================================= -->

        <aside class="properties-panel">

            <h3 class="h6 mb-3">
                Propiedades
            </h3>


            <!-- SIN SELECCIÓN -->

            <div
                id="properties-empty"
                class="text-secondary small"
            >

                Selecciona un estado del lienzo para editar sus propiedades.

            </div>


            <!-- FORMULARIO PROPIEDADES -->

            <div
                id="properties-form"
                class="d-none"
            >


                <!-- ID INTERNO -->

                <input
                    type="hidden"
                    id="property-state-id"
                >


                <!-- NOMBRE -->

                <div class="mb-3">

                    <label
                        for="property-state-name"
                        class="form-label"
                    >
                        Nombre
                    </label>

                    <input
                        type="text"
                        id="property-state-name"
                        class="form-control"
                    >

                </div>


                <!-- TYPE -->

                <div class="mb-3">

                    <label
                        for="property-state-type"
                        class="form-label"
                    >
                        Tipo
                    </label>

                    <input
                        type="text"
                        id="property-state-type"
                        class="form-control"
                        readonly
                    >

                </div>


                <!-- STARTAT -->

                <div class="form-check mb-3">

                    <input
                        class="form-check-input"
                        type="checkbox"
                        id="property-start-at"
                    >

                    <label
                        class="form-check-label"
                        for="property-start-at"
                    >
                        Estado inicial
                    </label>

                </div>


                <!-- ================================================= -->
                <!-- TASK -->
                <!-- ================================================= -->

                <div
                    id="properties-task"
                    class="state-properties d-none"
                >

                    <div class="mb-3">

                        <label
                            for="property-resource"
                            class="form-label"
                        >
                            Resource
                        </label>

                        <input
                            type="text"
                            class="form-control font-monospace"
                            id="property-resource"
                            placeholder="task:validar_pedido"
                        >

                    </div>

                </div>


                <!-- ================================================= -->
                <!-- WAIT -->
                <!-- ================================================= -->

                <div
                    id="properties-wait"
                    class="state-properties d-none"
                >

                    <div class="mb-3">

                        <label
                            for="property-seconds"
                            class="form-label"
                        >
                            Seconds
                        </label>

                        <input
                            type="number"
                            class="form-control"
                            id="property-seconds"
                            min="0"
                            value="1"
                        >

                    </div>

                </div>


                <!-- ================================================= -->
                <!-- CHOICE -->
                <!-- ================================================= -->

                <div
                    id="properties-choice"
                    class="state-properties d-none"
                >

                    <div class="mb-3">

                        <label
                            for="property-choice-variable"
                            class="form-label"
                        >
                            Variable
                        </label>

                        <input
                            type="text"
                            class="form-control font-monospace"
                            id="property-choice-variable"
                            placeholder="$.pedido_valido"
                        >

                    </div>


                    <div class="mb-3">

                        <label
                            for="property-choice-operator"
                            class="form-label"
                        >
                            Operador
                        </label>

                        <select
                            id="property-choice-operator"
                            class="form-select"
                        >

                            <option value="BooleanEquals">
                                BooleanEquals
                            </option>

                            <option value="StringEquals">
                                StringEquals
                            </option>

                            <option value="NumericEquals">
                                NumericEquals
                            </option>

                            <option value="NumericGreaterThan">
                                NumericGreaterThan
                            </option>

                            <option value="NumericGreaterThanEquals">
                                NumericGreaterThanEquals
                            </option>

                            <option value="NumericLessThan">
                                NumericLessThan
                            </option>

                            <option value="NumericLessThanEquals">
                                NumericLessThanEquals
                            </option>

                        </select>

                    </div>


                    <div class="mb-3">

                        <label
                            for="property-choice-value"
                            class="form-label"
                        >
                            Valor
                        </label>

                        <input
                            type="text"
                            class="form-control"
                            id="property-choice-value"
                            placeholder="true"
                        >

                    </div>

                </div>


                <!-- ================================================= -->
                <!-- FAIL -->
                <!-- ================================================= -->

                <div
                    id="properties-fail"
                    class="state-properties d-none"
                >

                    <div class="mb-3">

                        <label
                            for="property-error"
                            class="form-label"
                        >
                            Error
                        </label>

                        <input
                            type="text"
                            class="form-control"
                            id="property-error"
                            placeholder="WorkflowFailed"
                        >

                    </div>


                    <div class="mb-3">

                        <label
                            for="property-cause"
                            class="form-label"
                        >
                            Cause
                        </label>

                        <textarea
                            class="form-control"
                            id="property-cause"
                            rows="3"
                        ></textarea>

                    </div>

                </div>


                <!-- ================================================= -->
                <!-- NEXT -->
                <!-- ================================================= -->

                <div
                    id="property-next-container"
                    class="mb-3"
                >

                    <label
                        for="property-next"
                        class="form-label"
                    >
                        Next
                    </label>

                    <select
                        id="property-next"
                        class="form-select"
                    >

                        <option value="">
                            Sin seleccionar
                        </option>

                    </select>

                </div>


                <!-- ================================================= -->
                <!-- BOTONES -->
                <!-- ================================================= -->

                <div class="d-grid gap-2">

                    <button
                        type="button"
                        class="btn btn-primary"
                        id="btn-update-state"
                    >
                        Actualizar estado
                    </button>

                    <button
                        type="button"
                        class="btn btn-outline-danger"
                        id="btn-delete-state"
                    >
                        Eliminar estado
                    </button>

                </div>


            </div>

        </aside>


    </div>


    <!-- ===================================================== -->
    <!-- MENSAJES -->
    <!-- ===================================================== -->

    <div
        id="designer-message"
        class="mt-3"
        aria-live="polite"
    ></div>


    <!-- ===================================================== -->
    <!-- JSON -->
    <!-- ===================================================== -->

    <div
        class="card mt-4 d-none"
        id="json-section"
    >

        <div class="card-header d-flex justify-content-between align-items-center">

            <strong>
                Definición JSON
            </strong>

            <button
                type="button"
                class="btn btn-sm btn-outline-secondary"
                id="btn-close-json"
            >
                Cerrar
            </button>

        </div>


        <div class="card-body">

            <textarea
                id="workflow-json"
                class="form-control font-monospace"
                rows="20"
                readonly
            ></textarea>

        </div>

    </div>


</div>


<!-- ========================================================= -->
<!-- MODAL GUARDAR -->
<!-- ========================================================= -->

<div
    class="modal fade"
    id="saveWorkflowModal"
    tabindex="-1"
    aria-hidden="true"
>

    <div class="modal-dialog">

        <div class="modal-content">

            <div class="modal-header">

                <h2 class="modal-title fs-5">
                    Guardar workflow
                </h2>

                <button
                    type="button"
                    class="btn-close"
                    data-bs-dismiss="modal"
                    aria-label="Cerrar"
                ></button>

            </div>


            <div class="modal-body">

                <p>
                    El workflow se enviará al backend de Mini Step Functions.
                </p>

                <div
                    id="save-modal-message"
                    class="small"
                ></div>

            </div>


            <div class="modal-footer">

                <button
                    type="button"
                    class="btn btn-secondary"
                    data-bs-dismiss="modal"
                >
                    Cancelar
                </button>

                <button
                    type="button"
                    class="btn btn-primary"
                    id="btn-confirm-save"
                >
                    Confirmar
                </button>

            </div>

        </div>

    </div>

</div>


<!-- Bootstrap JS para el modal -->
<script
    src="vendor/bootstrap/bootstrap.bundle.min.js"
></script>

<script
    src="https://cdn.jsdelivr.net/npm/drawflow@0.0.60/dist/drawflow.min.js"
></script>

<!-- Lógica del diseñador -->
<script
    src="js/designer.js"
    defer
></script>

<?php

page_end();

?>