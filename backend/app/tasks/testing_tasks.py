"""Simuladores para pruebas; crear una instancia por ejecución de prueba."""


class PaymentTimeout(Exception):
    pass


def payment_timeout(data):
    raise PaymentTimeout("Tiempo de pago agotado (simulado).")


def payment_after_failures(failures=2):
    attempts = 0

    def task(data):
        nonlocal attempts
        attempts += 1
        if attempts <= failures:
            return payment_timeout(data)
        return {**data, "pago_procesado": True}

    return task
