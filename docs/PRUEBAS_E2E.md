# Comprobaciones de extremo a extremo — fase 6

Fecha: 25 de septiembre de 2026.

## Resultado ejecutado

- Backend: **62 pruebas aprobadas**, sin fallos ni pruebas omitidas.
- JavaScript: **19 pruebas aprobadas** (15 del diseñador y 4 del generador Mermaid).
- PHP 8.3.33: **12 archivos sin errores de sintaxis**.
- Se utilizó PostgreSQL configurado mediante `DATABASE_URL`. No se ejecutó el script
  de creación de la base de datos ni se cambió su esquema.
- Las pruebas de API utilizan FastAPI TestClient y sesiones PostgreSQL con
  transacción externa/savepoints. Los registros de esas pruebas se revierten al
  terminar; no deben aparecer como una demostración persistente en el frontend.

Esto verifica motor, API y persistencia mediante pruebas de integración. **No se
ha ejecutado una sesión completa en navegador PHP → FastAPI → PostgreSQL.**
Los adaptadores de DOM/Drawflow utilizados en las pruebas JavaScript no comprueban
el dibujo real, la carga de bibliotecas externas ni el arrastre del navegador.
Las comprobaciones manuales de esta guía permanecen pendientes, incluida la
revisión visual de Retry/Catch de la fase 3.

La suite emitió dos avisos no bloqueantes: deprecación de `httpx` en TestClient y
un `ResourceWarning` de conexión psycopg abierta al finalizar. Se registran aquí;
no se modificaron dependencias ni pruebas para ocultarlos.

## Repetir las pruebas

Desde la raíz, en PowerShell:

```powershell
cd backend
..\.venv\Scripts\python.exe -m unittest discover -v
cd ..
node --test frontend/js/designer.test.cjs frontend/js/workflow.test.cjs
Get-ChildItem frontend -Recurse -Filter *.php | ForEach-Object { php -l $_.FullName }
```

PHP debe estar disponible en PATH. En el entorno revisado se utilizó
`C:\laragon\bin\php\php-8.3.33-Win32-vs16-x64\php.exe`.
Las pruebas requieren las dependencias Python del proyecto, PostgreSQL accesible
y al menos un workflow almacenado para `test_database_queries.py`.

## Preparar la comprobación manual

Con la base de datos existente configurada, iniciar el backend en una terminal:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

En otra terminal, desde la raíz:

```powershell
$env:FASTAPI_URL = "http://127.0.0.1:8000"
php -S 127.0.0.1:8080 -t frontend
```

PHP necesita cURL. Abrir `http://127.0.0.1:8080` y, para peticiones manuales,
`http://127.0.0.1:8000/docs`. Anotar los ID devueltos al crear workflows y ejecutar.
Estas acciones manuales sí dejan workflows, ejecuciones y eventos almacenados.

## Matriz de los 17 casos

La columna automática identifica las pruebas aprobadas; la última describe una
comprobación manual pendiente y su resultado esperado.

| # | Caso | Cobertura automática ejecutada | Comprobación manual y resultado esperado |
| --- | --- | --- | --- |
| 1 | Crear mediante JSON | `test_api.test_crud_execute_events` | En `workflow-create.php`, pegar `examples/pedido.json`, indicar nombre y guardar. Redirige al detalle y conserva la definición. |
| 2 | Crear mediante Drawflow | `designer.test.cjs`: creación por eventos y exportación | En `workflow-designer.php`, agregar Pass y Succeed, conectarlos, validar y guardar. El detalle debe conservar ambos estados y su conexión. |
| 3 | Guardar en PostgreSQL | `test_api`, `test_workflow_service_db`, `test_execution_service_db` | Recargar la lista y consultar el ID creado mediante API y SQL; nombre y definición deben coincidir. |
| 4 | Consultar workflow | `test_api.test_crud_execute_events`, `test_database_queries` | `GET /api/workflows/{id}` devuelve 200 con el workflow guardado. |
| 5 | Ejecutar workflow | `test_api.test_crud_execute_events` | Ejecutar Pass → Succeed con `{"referencia":"E2E"}`. Obtener SUCCEEDED y redirección al detalle de ejecución. |
| 6 | Consultar Execution | `test_api.test_crud_execute_events`, `test_execution_service_db` | `GET /api/executions/{id}` devuelve el workflow correcto, input, output, estado final y fechas. |
| 7 | Consultar execution_events | `test_api.test_crud_execute_events`, `test_execution_service_db` | `GET /api/executions/{id}/events` devuelve los eventos ordenados. Pass → Succeed debe producir dos eventos terminados. |
| 8 | Visualizar Mermaid | `workflow.test.cjs`: definición, ramas, estilos y eventos | Abrir el detalle de workflow y ejecución; comprobar diagrama legible, estados, conexiones y marcas de ejecución, sin errores de consola. |
| 9 | Retry | `test_engine_retry`, `test_order_demo`, `test_execution_service_db`, `designer.test.cjs` | Ejecutar pedido con `inputs/pedido-recuperable.json`: dos eventos RETRYING y éxito al tercer intento, con esperas 2 y 4 s. |
| 10 | Catch | Mismas suites de Retry | Ejecutar pedido con `inputs/pedido-definitivo.json`: tras tres reintentos, visitar ErrorDePago y terminar FAILED/PagoFallido; no ejecutar Parallel ni Wait. |
| 11 | Choice | `test_engine_choice`, `test_examples` | Ejecutar `aprobacion.json` con `{"aprobado":true}` y `{"aprobado":false}`; visitar Aprobada y Rechazada respectivamente. |
| 12 | Wait | `test_engine_wait`, `test_order_demo` | Pedido exitoso pasa por EsperarConfirmacion y espera 3 s antes de PedidoCompletado. |
| 13 | Fail | `test_engine_core`, `test_execution_service_db`, `test_examples` | Aprobación falsa termina FAILED con Error SolicitudRechazada y su Cause; el historial sigue disponible. |
| 14 | Succeed | `test_engine_core`, `test_api`, `test_examples` | Aprobación verdadera termina SUCCEEDED y conserva el input en output. |
| 15 | Workflow inactivo | `test_api.test_inactive_workflow_cannot_execute` y prueba de desactivación/reactivación | Crear desmarcando Activo; el detalle muestra Inactivo y no ofrece Ejecutar. POST manual a `/api/workflows/{id}/execute` con `{"input":{}}` devuelve 409. SQL debe mostrar cero ejecuciones para ese nuevo workflow. |
| 16 | Resource desconocido | `test_engine_tasks.test_missing_or_unknown_resource` | POST `/api/workflows` con el payload de abajo devuelve 422 e identifica Resource. El motor no ejecuta la tarea desconocida. |
| 17 | Definición inválida | `test_validator`, `test_api.test_validation_list_on_create_update_and_execute` | Crear o actualizar usando StartAt inexistente devuelve 422 con errores. JSON mal formado enviado directamente a API devuelve 400. Una actualización inválida conserva el workflow anterior. |

Para el caso 16, usar este cuerpo en Swagger:

```json
{
  "name": "E2E Resource desconocido",
  "definition": {
    "StartAt": "Tarea",
    "States": {
      "Tarea": {"Type": "Task", "Resource": "task:no_existe", "End": true}
    }
  }
}
```

Para el caso 17, usar:

```json
{
  "name": "E2E definición inválida",
  "definition": {
    "StartAt": "NoExiste",
    "States": {"Fin": {"Type": "Succeed"}}
  }
}
```

Consultas de solo lectura para los casos 3, 6, 7 y 15; reemplazar los ID de ejemplo
por los devueltos en la sesión manual:

```sql
SELECT id, name, is_active, definition FROM workflows WHERE id = 123;
SELECT * FROM executions WHERE workflow_id = 123 ORDER BY id;
SELECT * FROM execution_events WHERE execution_id = 456 ORDER BY event_order;
SELECT count(*) FROM executions WHERE workflow_id = 123;
```

## Recorrido visual Retry/Catch pendiente

1. Crear Task `ProcesarPago`, Succeed `Fin` y Fail `ErrorPago` en Drawflow.
2. Conectar la salida de ProcesarPago con Fin. Seleccionar
   `task:procesar_pago` como Resource.
3. Habilitar Retry: IntervalSeconds 1, MaxAttempts 2, BackoffRate 2.
   Habilitar Catch hacia ErrorPago y actualizar el nodo.
4. Ver JSON: Retry y Catch deben contener `ErrorEquals: ["States.ALL"]`;
   Task debe tener `Next: "Fin"` y Catch `Next: "ErrorPago"`.
5. Renombrar ErrorPago a PagoRechazado. Comprobar que Catch.Next cambia.
6. Intentar actualizar el Task cambiando el nombre y poniendo MaxAttempts -1.
   Debe aparecer un error y el JSON anterior debe conservarse completo.
7. Eliminar el destino con el botón y repetir con los controles de Drawflow.
   Catch debe desactivarse y desaparecer del JSON; Retry debe conservarse.
8. Recrear el destino y Catch, guardar y ejecutar con `{}`: la tarea falla,
   reintenta y toma Catch. Con `{"pedido_id":1001,"total":250,"pedido_valido":true}`
   debe ir por la salida de éxito hacia Fin.

El diseñador ofrece `States.ALL`; las reglas con nombres de error específicos,
como PaymentTimeout en el demo de pedido, se definen mediante JSON.
