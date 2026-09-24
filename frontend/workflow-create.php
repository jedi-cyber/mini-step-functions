<?php
require __DIR__ . '/includes/layout.php';
$name = is_string($_POST['name'] ?? null) ? $_POST['name'] : '';
$description = is_string($_POST['description'] ?? null) ? $_POST['description'] : '';
$definition = is_string($_POST['definition'] ?? null) ? $_POST['definition'] : '{
  "StartAt": "Inicio",
  "States": {
    "Inicio": {"Type": "Pass", "Next": "Final"},
    "Final": {"Type": "Succeed"}
  }
}';
$error = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    try {
        check_csrf();
        $created = api_request('POST', 'workflows', ['name'=>trim($name), 'description'=>$description,
            'definition'=>json_object($definition), 'is_active'=>isset($_POST['is_active'])]);
        header('Location: workflow-view.php?id=' . (int) $created->id, true, 303); exit;
    } catch (Throwable $e) { $error = $e; }
}
page_start('Crear workflow'); if ($error) { show_error($error); }
?>
<form method="post"><?php csrf_field(); ?>
<div class="mb-3"><label for="name" class="form-label">Nombre</label><input class="form-control" id="name" name="name" maxlength="150" required value="<?= h($name) ?>"></div>
<div class="mb-3"><label for="description" class="form-label">Descripción</label><textarea class="form-control" id="description" name="description" rows="2"><?= h($description) ?></textarea></div>
<div class="mb-3"><label for="definition" class="form-label">Definición JSON</label><textarea class="form-control font-monospace" id="definition" name="definition" rows="16" required spellcheck="false"><?= h($definition) ?></textarea></div>
<div class="form-check mb-3"><input class="form-check-input" type="checkbox" id="is_active" name="is_active" <?= $_SERVER['REQUEST_METHOD'] !== 'POST' || isset($_POST['is_active']) ? 'checked' : '' ?>><label class="form-check-label" for="is_active">Activo</label></div>
<button class="btn btn-primary">Guardar workflow</button> <a class="btn btn-outline-secondary" href="workflows.php">Cancelar</a></form>
<?php page_end();
