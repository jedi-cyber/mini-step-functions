from app.tasks.order_tasks import procesar_pago, validar_pedido
from app.tasks.order_demo import verificar_stock, procesar_pago_demo, generar_factura, enviar_correo


class TaskResourceError(ValueError):
    """Resource ausente, inválido o no registrado."""


TASK_REGISTRY = {
    "task:verificar_stock": verificar_stock,
    "task:demo_procesar_pago": procesar_pago_demo,
    "task:generar_factura": generar_factura,
    "task:enviar_correo": enviar_correo,
    "task:validar_pedido": validar_pedido,
    "task:procesar_pago": procesar_pago,
}


def resolve_task(resource):
    if not isinstance(resource, str) or not resource:
        raise TaskResourceError("Task requiere un Resource de texto no vacío.")
    if resource not in TASK_REGISTRY:
        raise TaskResourceError(f"Resource no registrado: '{resource}'.")
    return TASK_REGISTRY[resource]
