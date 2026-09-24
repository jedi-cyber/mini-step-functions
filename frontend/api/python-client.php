<?php
declare(strict_types=1);

final class ApiException extends RuntimeException {}

function api_request(string $method, string $path, ?array $body = null): mixed
{
    if (!function_exists('curl_init')) {
        throw new ApiException('PHP necesita la extensión cURL para conectar con la API.');
    }
    $base = rtrim(getenv('FASTAPI_URL') ?: 'http://127.0.0.1:8000', '/');
    $handle = curl_init($base . '/api/' . ltrim($path, '/'));
    $headers = ['Accept: application/json'];
    $options = [CURLOPT_RETURNTRANSFER => true, CURLOPT_CUSTOMREQUEST => $method,
        CURLOPT_CONNECTTIMEOUT => 5, CURLOPT_TIMEOUT => 300];
    if ($body !== null) {
        $headers[] = 'Content-Type: application/json';
        $options[CURLOPT_POSTFIELDS] = json_encode($body, JSON_THROW_ON_ERROR);
    }
    $options[CURLOPT_HTTPHEADER] = $headers;
    curl_setopt_array($handle, $options);
    $raw = curl_exec($handle);
    $status = (int) curl_getinfo($handle, CURLINFO_HTTP_CODE);
    $error = curl_errno($handle);
    curl_close($handle);
    if ($raw === false) {
        throw new ApiException($error === CURLE_OPERATION_TIMEDOUT
            ? 'La solicitud agotó el tiempo de espera. Revisa Ejecuciones antes de volver a ejecutar: puede seguir en curso.'
            : 'No se pudo conectar con FastAPI. Comprueba que el backend esté iniciado.');
    }
    try {
        // Mantiene la diferencia entre objetos {} y listas [] de las definiciones.
        $data = json_decode($raw, false, 512, JSON_THROW_ON_ERROR);
    } catch (JsonException $e) {
        throw new ApiException('La API devolvió una respuesta que no es JSON.', $status);
    }
    if ($status < 200 || $status >= 300) {
        $detail = $data->detail ?? 'La API no pudo completar la solicitud.';
        if (is_array($detail)) {
            $detail = implode("\n", array_map(static function ($item): string {
                $location = $item->path ?? implode('.', $item->loc ?? []);
                return $location . ': ' . ($item->message ?? $item->msg ?? 'Error de validación');
            }, $detail));
        }
        throw new ApiException(is_string($detail) ? $detail : 'Error de API.', $status);
    }
    return $data;
}

function api_all(string $path): array
{
    $items = [];
    for ($offset = 0; ; $offset += 500) {
        $batch = api_request('GET', $path . '?offset=' . $offset . '&limit=500');
        if (!is_array($batch)) {
            throw new ApiException('La API no devolvió una lista.');
        }
        $items = array_merge($items, $batch);
        if (count($batch) < 500) {
            return $items;
        }
    }
}
