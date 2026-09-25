<?php
declare(strict_types=1);

require_once __DIR__ . '/python-client.php';

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);

    echo json_encode([
        'success' => false,
        'message' => 'Método no permitido.'
    ]);

    exit;
}

try {

    $raw = file_get_contents('php://input');

    if ($raw === false || trim($raw) === '') {
        throw new RuntimeException(
            'No se recibió información del workflow.'
        );
    }

    $payload = json_decode(
        $raw,
        true,
        512,
        JSON_THROW_ON_ERROR
    );

    if (!is_array($payload)) {
        throw new RuntimeException(
            'El contenido recibido no es válido.'
        );
    }

    // =====================================================
    // VALIDACIONES BÁSICAS
    // =====================================================

    $name = trim(
        (string)($payload['name'] ?? '')
    );

    if ($name === '') {
        throw new RuntimeException(
            'El workflow necesita un nombre.'
        );
    }

    $definition =
        $payload['definition'] ?? null;

    if (!is_array($definition)) {
        throw new RuntimeException(
            'La definición del workflow no es válida.'
        );
    }

    if (
        empty($definition['StartAt']) ||
        empty($definition['States'])
    ) {
        throw new RuntimeException(
            'La definición necesita StartAt y States.'
        );
    }

    // =====================================================
    // PAYLOAD PARA FASTAPI
    // =====================================================

    $apiPayload = [
        'name' => $name,

        'description' =>
            trim(
                (string)(
                    $payload['description'] ?? ''
                )
            ),

        'definition' => $definition,

        'is_active' =>
            isset($payload['is_active'])
                ? (bool)$payload['is_active']
                : true
    ];

    // =====================================================
    // ENVIAR A FASTAPI
    // =====================================================

    $workflow = api_request(
        'POST',
        'workflows',
        $apiPayload
    );

    // =====================================================
    // RESPUESTA
    // =====================================================

    http_response_code(201);

    echo json_encode(
        [
            'success' => true,
            'message' =>
                'Workflow guardado correctamente.',

            'workflow' => $workflow
        ],
        JSON_UNESCAPED_UNICODE |
        JSON_UNESCAPED_SLASHES
    );

} catch (JsonException $e) {

    http_response_code(400);

    echo json_encode([
        'success' => false,
        'message' =>
            'El JSON recibido no es válido: ' .
            $e->getMessage()
    ]);

} catch (ApiException $e) {

    $status = $e->getCode();

    if (
        !is_int($status) ||
        $status < 400 ||
        $status > 599
    ) {
        $status = 500;
    }

    http_response_code($status);

    echo json_encode([
        'success' => false,
        'message' => $e->getMessage()
    ]);

} catch (Throwable $e) {

    http_response_code(500);

    echo json_encode([
        'success' => false,
        'message' => $e->getMessage()
    ]);
}