"""Tareas de demostración; no realizan cobros ni llamadas externas."""

from math import isfinite


def validar_pedido(data: dict) -> dict:
    """Un pedido válido tiene ID entero positivo y total finito positivo."""
    if not isinstance(data, dict):
        raise ValueError("validar_pedido requiere un diccionario.")
    pedido_id = data.get("pedido_id")
    total = data.get("total")
    valido = (
        type(pedido_id) is int and pedido_id > 0
        and type(total) in (int, float) and total > 0
        and (type(total) is int or isfinite(total))
    )
    return {**data, "pedido_valido": valido}


def procesar_pago(data: dict) -> dict:
    """Simula un pago aprobado para un pedido previamente validado."""
    validated = validar_pedido(data)
    if data.get("pedido_valido") is not True or not validated["pedido_valido"]:
        raise ValueError("No se puede procesar el pago de un pedido no validado.")
    return {**data, "pago_procesado": True, "pago_estado": "APROBADO"}
