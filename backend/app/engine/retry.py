"""Políticas Task: primer ErrorEquals coincidente, sin coerción de tipos."""

from math import isfinite


def matching_rule(rules, error):
    for index, rule in enumerate(rules):
        if error in rule["ErrorEquals"] or "States.ALL" in rule["ErrorEquals"]:
            return index, rule
    return None, None


def validate_policies(state, states):
    for kind in ("Retry", "Catch"):
        rules = state.get(kind, [])
        if not isinstance(rules, list):
            raise ValueError(f"{kind} debe ser una lista.")
        for rule in rules:
            if not isinstance(rule, dict):
                raise ValueError(f"Cada regla {kind} debe ser un objeto.")
            errors = rule.get("ErrorEquals")
            if not isinstance(errors, list) or not errors or any(
                not isinstance(error, str) or not error for error in errors
            ):
                raise ValueError("ErrorEquals debe ser una lista de nombres de error.")
            if kind == "Catch":
                target = rule.get("Next")
                if not isinstance(target, str) or target not in states:
                    raise ValueError("Catch.Next debe apuntar a un estado válido.")
            else:
                attempts = rule.get("MaxAttempts", 3)
                if type(attempts) is not int or attempts < 0:
                    raise ValueError("MaxAttempts debe ser un entero >= 0.")
                for key, default, minimum in (("IntervalSeconds", 1, 0), ("BackoffRate", 2, 1)):
                    value = rule.get(key, default)
                    if type(value) not in (int, float) or value < minimum or (
                        type(value) is float and not isfinite(value)
                    ):
                        raise ValueError(f"{key} debe ser finito y >= {minimum}.")
