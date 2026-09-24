"""Selección ordenada de ramas con comparadores de tipos estrictos."""

import operator
from math import isfinite

from app.engine.json_path import path_parts, resolve_json_path


COMPARATORS = {
    "BooleanEquals": operator.eq,
    "StringEquals": operator.eq,
    "NumericEquals": operator.eq,
    "NumericGreaterThan": operator.gt,
    "NumericGreaterThanEquals": operator.ge,
    "NumericLessThan": operator.lt,
    "NumericLessThanEquals": operator.le,
}


def valid_operand(comparator, value):
    if comparator == "BooleanEquals":
        return type(value) is bool
    if comparator == "StringEquals":
        return isinstance(value, str)
    return type(value) is int or (type(value) is float and isfinite(value))


def validate_choice(state: dict, states: dict):
    choices = state.get("Choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("Choice requiere una lista Choices no vacía.")

    def validate_target(target):
        if not isinstance(target, str) or target not in states:
            raise ValueError("Choice: Next y Default deben apuntar a estados válidos.")

    validate_target(state.get("Default"))
    for rule in choices:
        if not isinstance(rule, dict):
            raise ValueError("Cada condición de Choices debe ser un diccionario.")
        path_parts(rule.get("Variable"))
        comparisons = set(rule) & COMPARATORS.keys()
        if len(comparisons) != 1 or set(rule) - {"Variable", "Next"} - COMPARATORS.keys():
            raise ValueError("Cada condición requiere exactamente un comparador soportado.")
        comparator = next(iter(comparisons))
        if not valid_operand(comparator, rule[comparator]):
            raise ValueError(f"Valor inválido para {comparator}.")
        validate_target(rule.get("Next"))


def execute_choice(state: dict, data) -> str:
    """Primera coincidencia; rutas ausentes o tipos distintos no coinciden.

    La definición debe haberse validado mediante validate_choice.
    """
    for rule in state["Choices"]:
        comparator = next(key for key in rule if key in COMPARATORS)
        value = resolve_json_path(data, rule["Variable"])
        if valid_operand(comparator, value) and COMPARATORS[comparator](
            value, rule[comparator]
        ):
            return rule["Next"]
    return state["Default"]
