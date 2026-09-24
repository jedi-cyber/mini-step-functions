<?php
require __DIR__ . '/includes/layout.php';
require __DIR__ . '/includes/diagram.php';
$workflow = null; $error = null;
$input = is_string($_POST['input'] ?? null) ? $_POST['input'] : '{}';
try {
    $id = page_id();
    $workflow = api_request('GET', 'workflows/' . $id);
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        check_csrf();
        set_time_limit(310);
        $result = api_request('POST', 'workflows/' . $id . '/execute', ['input'=>json_object($input)]);
        header('Location: execution-view.php?id=' . (int) $result->execution_id, true, 303); exit;
    }
} catch (Throwable $e) { $error = $e; }
page_start($workflow ? $workflow->name : 'Workflow');
if ($error) { show_error($error); }
if ($workflow): ?>
<p><?= h($workflow->description) ?></p><p class="text-secondary">ID <?= h($workflow->id) ?> · <?= $workflow->is_active ? 'Activo' : 'Inactivo' ?></p>
<h2 class="h5">Definición JSON</h2><pre class="json-panel"><?= h(pretty($workflow->definition)) ?></pre>
<?php workflow_diagram($workflow->definition); ?>
<h2 class="h5 mt-4">Ejecutar workflow</h2><p>Introduce los datos de entrada. La solicitud esperará hasta que termine la ejecución.</p>
<form method="post"><?php csrf_field(); ?><label for="input" class="form-label">Input JSON</label>
<textarea id="input" name="input" class="form-control font-monospace mb-3" rows="7" required spellcheck="false"><?= h($input) ?></textarea>
<button class="btn btn-primary">Ejecutar</button> <a class="btn btn-outline-secondary" href="executions.php">Ver ejecuciones</a></form>
<?php endif; page_end();
