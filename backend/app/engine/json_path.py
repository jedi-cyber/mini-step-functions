"""Subconjunto JSONPath: propiedades de objetos separadas por puntos."""

import re


MISSING = object()


def path_parts(path: str) -> list[str]:
    if not isinstance(path, str) or not re.fullmatch(
        r"\$\.[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*", path
    ):
        raise ValueError("Variable debe ser una ruta simple como $.cliente.edad.")
    return path[2:].split(".")


def resolve_json_path(data, path: str):
    """Devuelve MISSING si falta una propiedad; no modifica los datos."""
    current = data
    for part in path_parts(path):
        if not isinstance(current, dict) or part not in current:
            return MISSING
        current = current[part]
    return current
