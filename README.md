# Mini Step Functions

## Descripción

Mini Step Functions es un simulador académico inspirado en AWS Step Functions.
Permite definir máquinas de estados, ejecutarlas con datos JSON y consultar su
historial. **No es AWS Step Functions real** ni utiliza servicios de AWS.

## Objetivo

Simular la ejecución de workflows para estudiar transiciones, decisiones,
esperas, ramas paralelas, reintentos y manejo de errores, con una interfaz visual
y persistencia en PostgreSQL.

## Características

- Creación visual mediante Drawflow y creación mediante JSON.
- Estados Task, Choice, Wait, Pass, Parallel, Succeed y Fail.
- Retry y Catch en estados Task.
- Validación de definiciones y Resources registrados antes de ejecutar.
- Workflows activos/inactivos: el backend rechaza los inactivos con HTTP 409
  antes de crear una ejecución.
- Historial de ejecuciones y eventos por estado, con inputs, outputs, errores,
  fechas e intentos de reintento.
- Diagramas Mermaid, incluyendo ramas Parallel y estados del historial.
- Persistencia de workflows, ejecuciones y eventos en PostgreSQL.

Parallel se configura mediante JSON. Su botón está deshabilitado en el diseñador
porque este todavía no permite construir las Branches anidadas.

## Arquitectura

```text
Frontend PHP + Bootstrap + Drawflow + Mermaid
                    ↓ HTTP / JSON
                 FastAPI
                    ↓
           Servicios de aplicación
              ↙             ↘
      WorkflowEngine     SQLAlchemy
                             ↓
                         PostgreSQL
```

PHP consume la API y no accede directamente a PostgreSQL. FastAPI valida las
solicitudes y utiliza los servicios para consultar workflows y ejecutarlos.
El WorkflowEngine interpreta los estados e invoca tareas locales del
TASK_REGISTRY. El servicio de ejecución persiste los resultados y los eventos
que recibe del motor; el motor no depende directamente de SQLAlchemy.

## Tecnologías

Python, FastAPI, SQLAlchemy, psycopg, PostgreSQL, PHP, JavaScript, Drawflow,
Mermaid y Bootstrap.

## Requisitos

- Python: entorno verificado con Python 3.12 y las dependencias del repositorio.
- PHP 8 con extensión cURL; verificado con PHP 8.3.33.
- PostgreSQL iniciado y cliente `psql` disponible para la configuración inicial.
- Navegador con JavaScript y conexión a Internet para cargar Drawflow y Mermaid
  desde CDN. Bootstrap se incluye localmente en `frontend/vendor/`.
- Node.js para ejecutar las pruebas JavaScript; no es necesario para servir PHP.

## Configuración

Desde la raíz del repositorio, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
```

`requirements-dev.txt` incluye las dependencias de la aplicación y las de pruebas.
Para instalar únicamente las de la aplicación, usar `backend\requirements.txt`.

Crear un archivo `.env` en la raíz con la conexión local:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:TU_PASSWORD@localhost:5432/mini_step_functions
```

Sustituir `TU_PASSWORD` por la contraseña de tu instalación; no publicar
credenciales reales. `.env` está excluido de Git. El backend también permite
proporcionar `DATABASE_URL` como variable de entorno.

## Base de datos

El archivo [backend/app/database/mini_step_functions.sql](backend/app/database/mini_step_functions.sql)
crea la base de datos, las tablas `workflows`, `executions` y `execution_events`,
índices, un trigger, una vista de resumen y un workflow inicial.

**El script contiene `DROP DATABASE IF EXISTS mini_step_functions`: elimina la
base existente y sus datos.** Ejecutarlo solo para inicializar o reiniciar una
base de desarrollo cuyos datos se puedan descartar. Si ya está configurada,
omitir este paso al iniciar la aplicación.

Desde la raíz:

```powershell
psql -h localhost -U postgres -d postgres -f backend/app/database/mini_step_functions.sql
```

Usar `psql`: el script incluye `\connect`. Requiere permisos para crear la base;
el usuario configurado en el script es `postgres`.

## Backend

En una terminal PowerShell, desde la raíz:

```powershell
cd backend
..\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

También puede iniciarse sin activar el entorno:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

- Dirección base de la API: `http://127.0.0.1:8000`.
- Swagger: `http://127.0.0.1:8000/docs`.

| Método | Ruta | Función |
| --- | --- | --- |
| GET | `/api/workflows` | Listar workflows |
| POST | `/api/workflows` | Crear un workflow |
| GET | `/api/workflows/{id}` | Consultar un workflow |
| PUT | `/api/workflows/{id}` | Actualizar un workflow |
| POST | `/api/workflows/{id}/execute` | Ejecutar con un cuerpo `{"input": {}}` |
| GET | `/api/executions` | Listar ejecuciones |
| GET | `/api/executions/{id}` | Consultar una ejecución |
| GET | `/api/executions/{id}/events` | Consultar sus eventos |

Las listas aceptan `offset` y `limit`. La solicitud de ejecución espera hasta que
el workflow termine. Consultar `status` en la respuesta: HTTP 200 puede contener
una ejecución terminada en FAILED. Una definición inválida devuelve HTTP 422;
un workflow inactivo devuelve HTTP 409 y no genera una ejecución.

## Frontend

Con Laragon, iniciar el servidor web con PHP y acceder al directorio `frontend`
del proyecto; con la instalación habitual de este repositorio:
`http://localhost/mini-step-functions/frontend/`.
Si se utiliza un virtual host, configurar su raíz en `frontend`.

Alternativa con el servidor integrado de PHP, en otra terminal desde la raíz:

```powershell
$env:FASTAPI_URL = "http://127.0.0.1:8000"
php -S 127.0.0.1:8080 -t frontend
```

Abrir `http://127.0.0.1:8080`. Si `php` no está en PATH, utilizar la ruta al
ejecutable de PHP de Laragon. La extensión cURL debe estar habilitada.
`FASTAPI_URL` es opcional cuando el backend usa `http://127.0.0.1:8000`;
debe estar disponible en el proceso PHP si se cambia esa dirección.

## Uso

1. Abrir el diseñador visual y asignar un nombre al workflow.
2. Agregar estados y conectar sus salidas; el primer nodo es el inicio por defecto.
3. Seleccionar cada estado, configurar sus propiedades y pulsar Actualizar.
   En Task, elegir un Resource registrado y habilitar Retry/Catch si corresponde.
4. Validar el workflow y revisar el JSON generado.
5. Guardar y confirmar; se abrirá el detalle del workflow.
6. Introducir un objeto JSON y ejecutar el workflow activo.
7. Consultar el estado final, el historial de eventos y el diagrama de ejecución.

Para crear mediante JSON, abrir **Crear workflow**, pegar una definición completa,
indicar nombre y estado Activo y guardar. Esta vía permite definir Parallel.

El diseñador genera `ErrorEquals: ["States.ALL"]` para Retry y Catch. Para reglas
por errores específicos, utilizar JSON. Catch no puede apuntar al mismo Task en
el diseñador; al renombrar o eliminar su destino, las referencias se actualizan
o se desactivan respectivamente.

## Ejemplo: procesamiento de pedido

La definición completa está en [examples/pedido.json](examples/pedido.json).
Todos sus Resources existen en [TASK_REGISTRY](backend/app/tasks/registry.py).

```text
Inicio → ValidarPedido → PedidoValido
                          ├─ no → PedidoRechazado (Fail)
                          └─ sí → VerificarStock → ProcesarPago (Retry)
                                                   ├─ Catch → ErrorDePago (Fail)
                                                   └─ éxito → CompletarPedido (Parallel)
                                                               ├─ GenerarFactura
                                                               └─ EnviarCorreo
                                                             ↓
                                                    EsperarConfirmacion
                                                             ↓
                                                    PedidoCompletado (Succeed)
```

Crear el workflow pegando ese JSON y ejecutar con los inputs siguientes:

| Input | Resultado esperado |
| --- | --- |
| [pedido-exitoso.json](examples/inputs/pedido-exitoso.json) | SUCCEEDED en el primer intento de pago; Wait de 3 segundos |
| [pedido-recuperable.json](examples/inputs/pedido-recuperable.json) | Dos errores PaymentTimeout, esperas de 2 y 4 segundos y éxito al tercer intento |
| [pedido-definitivo.json](examples/inputs/pedido-definitivo.json) | Agota tres reintentos, toma Catch hacia ErrorDePago y termina FAILED |
| [pedido-invalido.json](examples/inputs/pedido-invalido.json) | Choice conduce a PedidoRechazado; termina FAILED sin procesar el pago |

`MaxAttempts` cuenta reintentos además del intento inicial. La salida exitosa
contiene los resultados de factura y correo en el orden declarado de las ramas.
Las tareas son simulaciones locales; no cobran ni envían correos reales.

También puede ejecutarse el demo en memoria desde la raíz, sin guardar historial:

```powershell
.\.venv\Scripts\python.exe backend\demo_pedido.py recuperable
```

Más detalles en [examples/PEDIDO.md](examples/PEDIDO.md). Otros ejemplos:
[Parallel](examples/parallel.json), con input `{}`, y
[aprobación](examples/aprobacion.json), con `{"aprobado": true}` o
`{"aprobado": false}`.

## Pruebas

Con PostgreSQL configurado y el entorno activado, desde `backend`:

```powershell
python -m unittest discover -v
```

Sin activar el entorno, usar `..\.venv\Scripts\python.exe` en lugar de `python`.
La suite incluye pruebas del motor, API, validación, ejemplos y persistencia.
La prueba de consultas requiere al menos un workflow almacenado, como el que
inserta el script SQL inicial.

Desde la raíz, las pruebas JavaScript se ejecutan con:

```powershell
node --test frontend/js/designer.test.cjs frontend/js/workflow.test.cjs
```

La última verificación completó **62 pruebas backend y 19 JavaScript**.
La matriz de cobertura, los avisos observados y las comprobaciones manuales
pendientes están en [docs/PRUEBAS_E2E.md](docs/PRUEBAS_E2E.md).
Las pruebas JavaScript usan adaptadores de DOM/Drawflow; no sustituyen una
verificación visual en navegador.

## Limitaciones

- Es un simulador académico, no una implementación completa de AWS Step Functions
  ni de Amazon States Language.
- No usa servicios AWS reales ni implementa IAM, Lambda real, CloudWatch, S3 o SQS.
- No incluye autenticación ni autorización de usuarios; está destinado a una
  demostración local.
- Parallel se crea mediante JSON; no existe un editor visual de Branches anidadas.
- Retry/Catch se implementan para Task. Las tareas disponibles son funciones
  locales registradas, no funciones Lambda remotas.
- Las ejecuciones ocurren dentro del proceso del backend; no hay un servicio de
  trabajos duradero ni reanudación automática tras reiniciar el proceso.
- PHP espera hasta 300 segundos por la API. Si agota ese plazo, consultar el
  historial antes de repetir la ejecución, porque puede seguir en curso.
- El historial y los diagramas se actualizan al recargar. El diagrama utiliza la
  definición actual del workflow, que puede diferir de la utilizada por una
  ejecución anterior si después se editó.
- Drawflow y Mermaid requieren acceso a sus CDN. La revisión visual completa en
  navegador permanece pendiente según la guía de pruebas.
