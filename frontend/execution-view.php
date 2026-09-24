<?php require __DIR__ . '/includes/layout.php'; page_start('Detalle de ejecución');
require __DIR__ . '/includes/diagram.php';
try { $id = page_id(); $execution = api_request('GET', 'executions/' . $id);
$events = api_all('executions/' . $id . '/events');
try {
    $workflow = api_request('GET', 'workflows/' . $execution->workflow_id);
    workflow_diagram($workflow->definition, $events, $execution);
} catch (Throwable $diagramError) { show_error($diagramError); }
?>
<div class="d-flex gap-3 align-items-center mb-3"><strong>#<?= h($execution->id) ?></strong><?php status_badge($execution->status); ?><a class="btn btn-sm btn-outline-secondary" href="execution-view.php?id=<?= $id ?>">Actualizar</a></div>
<p>Workflow: <a href="workflow-view.php?id=<?= h($execution->workflow_id) ?>">#<?= h($execution->workflow_id) ?></a> · Estado actual: <?= h($execution->current_state) ?></p>
<p class="text-secondary">Inicio (UTC): <?= h($execution->started_at) ?> · Fin (UTC): <?= h($execution->finished_at ?? 'En curso') ?></p>
<?php if ($execution->error): ?><div class="alert alert-danger text-break"><?= h($execution->error) ?></div><?php endif; ?>
<div class="row"><section class="col-md-6"><h2 class="h5">Input</h2><pre class="json-panel"><?= h(pretty($execution->input)) ?></pre></section><section class="col-md-6"><h2 class="h5">Output</h2><pre class="json-panel"><?= h(pretty($execution->output)) ?></pre></section></div>
<h2 class="h4 mt-4">Historial de estados</h2>
<?php if (!$events): ?><p>Aún no hay eventos registrados.</p><?php endif; ?>
<?php foreach ($events as $event): ?>
<details class="card mb-2"><summary class="card-header"><strong>#<?= h($event->event_order) ?> <?= h($event->state_name) ?></strong> · <?= h($event->state_type) ?> · <?php status_badge($event->status); ?> · Reintento <?= h($event->retry_attempt) ?></summary>
<div class="card-body"><p class="text-secondary">Inicio (UTC): <?= h($event->started_at) ?> · Fin (UTC): <?= h($event->finished_at ?? 'En curso') ?></p>
<?php if ($event->error || $event->cause): ?><div class="alert alert-danger text-break"><?= h($event->error) ?><br><?= h($event->cause) ?></div><?php endif; ?>
<h3 class="h6">Input</h3><pre class="json-panel"><?= h(pretty($event->input)) ?></pre><h3 class="h6">Output</h3><pre class="json-panel"><?= h(pretty($event->output)) ?></pre></div></details>
<?php endforeach; } catch (Throwable $e) { show_error($e); } page_end();
