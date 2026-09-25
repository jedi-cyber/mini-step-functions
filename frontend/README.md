# Frontend PHP

Requiere PHP 8 con extensión cURL y FastAPI iniciado. No accede directamente a PostgreSQL.

Desde la raíz del proyecto:

```powershell
$env:FASTAPI_URL = "http://127.0.0.1:8000"
php -S 127.0.0.1:8080 -t frontend
```

Abre http://127.0.0.1:8080. Bootstrap se sirve desde `vendor/bootstrap/`.
Drawflow y Mermaid se cargan desde CDN y requieren conexión a Internet.

En otra terminal, desde backend:

```powershell
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Crear: nombre, descripción y definición JSON. Ejecutar: input como objeto JSON.
Los errores de validación se muestran sin borrar el formulario. Una ejecución finalizada
redirige a su historial, incluso si terminó en FAILED. No se reintentan automáticamente
las solicitudes POST. Si una ejecución tarda más de 300 segundos, consulta la lista de
ejecuciones antes de repetirla. La API puede continuar ejecutándola.

Las listas y contadores recorren las páginas de la API (500 registros por consulta).
La información se actualiza al recargar; no constituye una instantánea transaccional.

Comprobación manual: crear el ejemplo Pass → Succeed, ejecutarlo con {}, abrir el historial,
verificar los dos eventos y los contadores. Probar JSON mal formado, un Next inexistente,
un ID inexistente y detener FastAPI para comprobar los mensajes de error.
