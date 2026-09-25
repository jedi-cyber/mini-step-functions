<?php require __DIR__ . '/includes/layout.php'; page_start('Workflows'); ?>
<div class="d-flex gap-2 mb-3">

    <a
        class="btn btn-primary"
        href="workflow-designer.php"
    >
        Crear workflow visual
    </a>

    <a
        class="btn btn-outline-primary"
        href="workflow-create.php"
    >
        Crear desde JSON
    </a>

</div>
<?php try { $items = api_all('workflows'); ?>
<?php if (!$items): ?><div class="alert alert-info">Todavía no hay workflows.</div><?php else: ?>
<div class="table-responsive"><table class="table table-hover align-middle"><thead><tr><th>ID</th><th>Nombre</th><th>Activo</th><th>Creado</th><th>Acciones</th></tr></thead><tbody>
<?php foreach ($items as $item): ?><tr><td><?= h($item->id) ?></td><td><?= h($item->name) ?></td><td><?= $item->is_active ? 'Sí' : 'No' ?></td><td><?= h($item->created_at) ?></td><td><a href="workflow-view.php?id=<?= h($item->id) ?>">Ver / ejecutar</a></td></tr><?php endforeach; ?>
</tbody></table></div><?php endif; ?>
<?php } catch (Throwable $e) { show_error($e); } page_end();
