<?php require __DIR__ . '/includes/layout.php'; page_start('Workflows'); ?>
<a class="btn btn-primary mb-3" href="workflow-create.php">Crear workflow</a>
<?php try { $items = api_all('workflows'); ?>
<?php if (!$items): ?><div class="alert alert-info">Todavía no hay workflows.</div><?php else: ?>
<div class="table-responsive"><table class="table table-hover align-middle"><thead><tr><th>ID</th><th>Nombre</th><th>Activo</th><th>Creado</th><th>Acciones</th></tr></thead><tbody>
<?php foreach ($items as $item): ?><tr><td><?= h($item->id) ?></td><td><?= h($item->name) ?></td><td><?= $item->is_active ? 'Sí' : 'No' ?></td><td><?= h($item->created_at) ?></td><td><a href="workflow-view.php?id=<?= h($item->id) ?>">Ver / ejecutar</a></td></tr><?php endforeach; ?>
</tbody></table></div><?php endif; ?>
<?php } catch (Throwable $e) { show_error($e); } page_end();
