<?php
function workflow_diagram(object $definition, array $events = [], ?object $execution = null): void { ?>
<section class="card mb-4" data-workflow-diagram>
<div class="card-body"><h2 class="h5">Diagrama del workflow</h2>
<div class="d-flex flex-wrap gap-2 mb-3 diagram-legend">
<?php foreach (['PENDING','RUNNING','SUCCEEDED','FAILED','RETRYING','WAITING'] as $status): ?>
<span class="diagram-status <?= h($status) ?>"><?= h($status) ?></span>
<?php endforeach; ?></div>
<div class="diagram-output" data-diagram-output role="img" aria-label="Diagrama de estados del workflow">Cargando diagrama…</div>
<noscript>Activa JavaScript para ver el diagrama.</noscript>
<p class="text-secondary mt-2" data-diagram-warning></p>
<?php if ($execution): ?><p class="small text-secondary">Se utiliza la definición actual del workflow y los eventos disponibles al cargar la página. Actualiza para ver cambios. Si la definición se editó después de ejecutar, puede diferir del historial.</p><?php endif; ?>
<details><summary>Código Mermaid</summary><pre class="json-panel mt-2" data-diagram-source></pre></details>
<script type="application/json"><?= json_encode(['definition'=>$definition, 'events'=>$events, 'execution'=>$execution], JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_THROW_ON_ERROR) ?></script>
</div></section><script src="js/workflow.js" defer></script>
<?php }
