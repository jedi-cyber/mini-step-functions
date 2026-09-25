<?php
declare(strict_types=1);
require_once __DIR__ . '/../api/python-client.php';
session_start();
if (empty($_SESSION['csrf'])) {
    $_SESSION['csrf'] = bin2hex(random_bytes(32));
}
// Permite consultar el historial desde otra pestaña mientras se ejecuta un workflow.
session_write_close();
function h(mixed $value): string {
    return htmlspecialchars((string) ($value ?? ''), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
function pretty(mixed $value): string {
    return json_encode($value, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR);
}
function csrf_field(): void {
    echo '<input type="hidden" name="csrf" value="' . h($_SESSION['csrf']) . '">';
}
function check_csrf(): void {
    if (!is_string($_POST['csrf'] ?? null) || !hash_equals($_SESSION['csrf'], $_POST['csrf'])) {
        throw new RuntimeException('El formulario ha caducado. Recarga la página e inténtalo de nuevo.');
    }
}
function json_object(string $text): object {
    try { $value = json_decode($text, false, 512, JSON_THROW_ON_ERROR); }
    catch (JsonException $e) { throw new RuntimeException('JSON inválido: ' . $e->getMessage()); }
    if (!is_object($value)) { throw new RuntimeException('Introduce un objeto JSON, por ejemplo {}.'); }
    return $value;
}
function page_id(): int {
    $id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT, ['options' => ['min_range' => 1]]);
    if (!$id) { throw new RuntimeException('El ID debe ser un entero positivo.'); }
    return $id;
}
function page_start(string $title): void { ?>
<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title><?= h($title) ?> · Mini Step Functions</title>
<link href="vendor/bootstrap/bootstrap.min.css" rel="stylesheet">
<link href="css/style.css" rel="stylesheet"></head><body>
<nav class="navbar navbar-dark bg-dark"><div class="container flex-wrap gap-3">
<a class="navbar-brand" href="index.php">Mini Step Functions</a>
<div class="d-flex gap-3">
    <a class="text-white" href="index.php">
        Dashboard
    </a>

    <a class="text-white" href="workflows.php">
        Workflows
    </a>

    <a class="text-white" href="workflow-designer.php">
        Diseñador
    </a>

    <a class="text-white" href="executions.php">
        Ejecuciones
    </a>
</div>
</nav><main class="container py-4"><h1 class="h2 mb-4"><?= h($title) ?></h1>
<?php }
function page_end(): void { echo '</main></body></html>'; }
function show_error(Throwable $error): void {
    echo '<div class="alert alert-danger text-break" role="alert">' . nl2br(h($error->getMessage())) . '</div>';
}
function status_badge(string $status): void {
    $color = ['SUCCEEDED'=>'success', 'FAILED'=>'danger', 'RUNNING'=>'primary', 'RETRYING'=>'warning', 'WAITING'=>'info'][$status] ?? 'secondary';
    echo '<span class="badge bg-' . $color . '">' . h($status) . '</span>';
}
