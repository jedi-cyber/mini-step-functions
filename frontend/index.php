<?php
require __DIR__ . '/includes/layout.php';
page_start('Dashboard');
try {
    $workflows = api_all('workflows');
    $executions = api_all('executions');
    $counts = ['Workflows'=>count($workflows), 'Ejecuciones'=>count($executions),
        'Exitosas'=>count(array_filter($executions, fn($e)=>$e->status === 'SUCCEEDED')),
        'Fallidas'=>count(array_filter($executions, fn($e)=>$e->status === 'FAILED'))]; ?>
    <div class="row g-3 mb-4">
    <?php foreach ($counts as $label=>$count): ?>
    <div class="col-6 col-lg-3"><div class="card h-100"><div class="card-body"><p class="text-secondary"><?= h($label) ?></p><p class="display-5 mb-0"><?= $count ?></p></div></div></div>
    <?php endforeach; ?></div>
    <a class="btn btn-primary" href="workflow-create.php">Crear workflow</a>
    <a class="btn btn-outline-secondary" href="executions.php">Ver ejecuciones</a>
    <p class="text-secondary mt-3">Los contadores se actualizan al recargar esta página.</p>
<?php } catch (Throwable $e) { show_error($e); } page_end();
