# Demostración: procesamiento de pedido

Todas las tareas son simulaciones locales: no realizan cobros, envíos ni reservas reales.
La definición está en `pedido.json` y las entradas en `inputs/pedido-*.json`.

| Entrada | Resultado | Pago | Esperas aproximadas |
| --- | --- | --- | --- |
| pedido-exitoso.json | SUCCEEDED | Primer intento | Wait 3 s |
| pedido-invalido.json | FAILED / PedidoInvalido | No se ejecuta | Ninguna |
| pedido-recuperable.json | SUCCEEDED | Dos PaymentTimeout y éxito al tercer intento | Retry 2 + 4 s; Wait 3 s |
| pedido-definitivo.json | FAILED / PagoFallido | Cuatro PaymentTimeout; Catch → ErrorDePago | Retry 2 + 4 + 8 s |

`MaxAttempts: 3` permite tres reintentos además del intento inicial. Catch recibe
Error y Cause; el historial de ProcesarPago conserva la causa original. La tarea
`task:demo_procesar_pago` agrega simulación sin alterar `task:procesar_pago` existente.
VerificarStock inicializa el contador por ejecución, aislado mediante ContextVar.
Stock insuficiente genera un error de tarea; los cuatro inputs incluidos tienen stock.

## Ejecución rápida

Desde la raíz, con el entorno Python del proyecto:

```powershell
.\.venv\Scripts\python.exe backend\demo_pedido.py exitoso
.\.venv\Scripts\python.exe backend\demo_pedido.py invalido
.\.venv\Scripts\python.exe backend\demo_pedido.py recuperable
.\.venv\Scripts\python.exe backend\demo_pedido.py definitivo
```

Estos comandos ejecutan en memoria, con esperas reales, sin guardar historial en PostgreSQL.

## Demostración con API y frontend

1. Reinicia FastAPI para cargar las nuevas tareas.
2. Abre Crear workflow, escribe un nombre y pega `pedido.json` en Definición JSON.
3. Guarda y ejecuta cuatro veces, pegando cada input en el formulario de ejecución.
4. Consulta el diagrama y los eventos en el detalle de cada ejecución. En los casos
   recuperable y definitivo aparecerán eventos RETRYING. En el definitivo se visita
   ErrorDePago; no se ejecutan las ramas Parallel ni Wait.

El output exitoso es una lista: primero la factura simulada, luego la confirmación
de correo. Parallel conserva el orden de sus ramas, aunque se ejecuten concurrentemente.

Pruebas sin esperas reales:

```powershell
.\.venv\Scripts\python.exe -B backend\test_order_demo.py
```
