<?php require __DIR__ . '/includes/layout.php'; page_start('Ejecuciones'); ?>
<a class="btn btn-outline-secondary mb-3" href="executions.php">Actualizar</a>
<?php try { $items = api_all('executions'); ?>
<?php if (!$items): ?><div class="alert alert-info">Todavía no hay ejecuciones.</div><?php else: ?>
<div class="table-responsive"><table class="table table-hover align-middle"><thead><tr><th>ID</th><th>Workflow</th><th>Estado</th><th>Estado actual</th><th>Inicio (UTC)</th><th>Detalle</th></tr></thead><tbody>
<?php foreach ($items as $item): ?><tr><td><?= h($item->id) ?></td><td><a href="workflow-view.php?id=<?= h($item->workflow_id) ?>">#<?= h($item->workflow_id) ?></a></td><td><?php status_badge($item->status); ?></td><td><?= h($item->current_state) ?></td><td><?= h($item->started_at) ?></td><td><a href="execution-view.php?id=<?= h($item->id) ?>">Ver historial</a></td></tr><?php endforeach; ?>
</tbody></table></div><?php endif; ?>
<?php } catch (Throwable $e) { show_error($e); } page_end();
