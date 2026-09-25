<?php

require __DIR__ . '/includes/layout.php';

require __DIR__ . '/includes/diagram.php';


$workflow = null;

$error = null;


$input =
    is_string(
        $_POST['input'] ?? null
    )
        ? $_POST['input']
        : '{}';


try {

    $id =
        page_id();


    $workflow =
        api_request(
            'GET',
            'workflows/' . $id
        );


    // =========================================================
    // EJECUTAR
    // =========================================================

    if (
        $_SERVER['REQUEST_METHOD'] ===
        'POST'
    ) {

        check_csrf();


        // -----------------------------------------------------
        // Protección adicional en frontend
        //
        // La protección real sigue estando en FastAPI.
        // -----------------------------------------------------

        if (
            !$workflow->is_active
        ) {

            throw new RuntimeException(
                'Este workflow está inactivo y no puede ejecutarse.'
            );
        }


        set_time_limit(
            310
        );


        $result =
            api_request(

                'POST',

                'workflows/' .
                $id .
                '/execute',

                [
                    'input' =>
                        json_object(
                            $input
                        )
                ]
            );


        header(
            'Location: execution-view.php?id=' .
            (int)$result->execution_id,
            true,
            303
        );


        exit;
    }


} catch (Throwable $e) {

    $error =
        $e;
}


// =============================================================
// PÁGINA
// =============================================================

page_start(
    $workflow
        ? $workflow->name
        : 'Workflow'
);


if ($error) {

    show_error(
        $error
    );
}


if ($workflow):
?>


<!-- ========================================================= -->
<!-- INFORMACIÓN -->
<!-- ========================================================= -->

<p>
    <?= h($workflow->description) ?>
</p>


<p class="text-secondary">

    ID <?= h($workflow->id) ?>

    ·

    <?php if ($workflow->is_active): ?>

        <span class="text-success">
            Activo
        </span>

    <?php else: ?>

        <span class="text-danger">
            Inactivo
        </span>

    <?php endif; ?>

</p>


<!-- ========================================================= -->
<!-- DEFINICIÓN -->
<!-- ========================================================= -->

<h2 class="h5">
    Definición JSON
</h2>


<pre class="json-panel"><?= h(
    pretty(
        $workflow->definition
    )
) ?></pre>


<!-- ========================================================= -->
<!-- DIAGRAMA -->
<!-- ========================================================= -->

<?php

workflow_diagram(
    $workflow->definition
);

?>


<!-- ========================================================= -->
<!-- EJECUCIÓN -->
<!-- ========================================================= -->

<h2 class="h5 mt-4">
    Ejecutar workflow
</h2>


<?php if ($workflow->is_active): ?>


    <p>
        Introduce los datos de entrada.
        La solicitud esperará hasta que termine la ejecución.
    </p>


    <form method="post">

        <?php csrf_field(); ?>


        <label
            for="input"
            class="form-label"
        >
            Input JSON
        </label>


        <textarea
            id="input"
            name="input"
            class="form-control font-monospace mb-3"
            rows="7"
            required
            spellcheck="false"
        ><?= h($input) ?></textarea>


        <button
            type="submit"
            class="btn btn-primary"
        >
            Ejecutar
        </button>


        <a
            class="btn btn-outline-secondary"
            href="executions.php"
        >
            Ver ejecuciones
        </a>

    </form>


<?php else: ?>


    <div class="alert alert-warning">

        <strong>
            Workflow inactivo.
        </strong>

        Este workflow no puede ejecutarse
        mientras su estado sea inactivo.

    </div>


    <a
        class="btn btn-outline-secondary"
        href="executions.php"
    >
        Ver ejecuciones anteriores
    </a>


<?php endif; ?>


<?php

endif;

page_end();

?>