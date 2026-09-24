"""Simulación local: no cobra, no envía correos ni reserva stock real."""

from contextvars import ContextVar
from app.tasks.order_tasks import procesar_pago


class PaymentTimeout(Exception):
    pass


class PaymentDeclined(Exception):
    pass


_attempts = ContextVar("demo_payment_attempts", default=None)


async def verificar_stock(data):
    if data.get("stock_disponible", True) is not True:
        raise ValueError("Stock insuficiente (simulado).")
    # Contexto propio de cada workflow; no comparte contadores entre ejecuciones.
    _attempts.set(0)
    return {**data, "stock_verificado": True}


async def procesar_pago_demo(data):
    attempts = _attempts.get()
    if attempts is None or not data.get("stock_verificado"):
        raise ValueError("La demo requiere ejecutar VerificarStock antes del pago.")
    attempts += 1
    _attempts.set(attempts)
    scenario = data.get("simulacion_pago", "exitoso")
    if scenario == "recuperable" and attempts <= 2:
        raise PaymentTimeout(f"Timeout simulado en intento {attempts}.")
    if scenario == "definitivo":
        raise PaymentTimeout(f"Servicio de pago no disponible; intento {attempts}.")
    if scenario not in {"exitoso", "recuperable", "definitivo"}:
        raise PaymentDeclined("Escenario de pago desconocido.")
    return {**procesar_pago(data), "intentos_pago": attempts}


def generar_factura(data):
    return {"pedido_id": data["pedido_id"], "factura_id": f"DEMO-{data['pedido_id']}",
            "total": data["total"], "intentos_pago": data["intentos_pago"], "simulado": True}


def enviar_correo(data):
    return {"pedido_id": data["pedido_id"], "destinatario": data.get("email", "cliente@example.com"),
            "correo_enviado": True, "simulado": True}
