"""Espera cooperativa con duración fija en segundos."""

import asyncio
from math import isfinite


def validate_wait(state: dict):
    seconds = state.get("Seconds")
    if type(seconds) not in (int, float) or seconds < 0:
        raise ValueError("Wait requiere Seconds numérico y >= 0.")
    if type(seconds) is float and not isfinite(seconds):
        raise ValueError("Seconds debe ser finito.")
    if any(key in state for key in ("Timestamp", "SecondsPath", "TimestampPath")):
        raise ValueError("Wait solo soporta Seconds en esta versión.")


async def execute_wait(state: dict) -> str:
    validate_wait(state)
    await asyncio.sleep(state["Seconds"])
    return state.get("Next")
