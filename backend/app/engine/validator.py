"""Validación sin efectos secundarios; las rutas identifican cada error."""

from app.tasks.registry import resolve_task, TaskResourceError
from app.states.choice import validate_choice
from app.states.wait import validate_wait
from app.engine.retry import validate_policies


class WorkflowValidationError(TaskResourceError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("; ".join(f"{e['path']}: {e['message']}" for e in errors))


def validate_workflow(definition) -> list[dict[str, str]]:
    errors = []

    def add(path, message):
        errors.append({"path": path, "message": message})

    def check(path, function, *args):
        try:
            function(*args)
        except ValueError as exc:
            add(path, str(exc))

    def visit(value, path):
        if not isinstance(value, dict):
            add(path, "definition debe ser un diccionario.")
            return
        states = value.get("States")
        start = value.get("StartAt")
        if not isinstance(start, str) or not start:
            add(path + ".StartAt", "StartAt es requerido y debe ser un nombre no vacío.")
        if not isinstance(states, dict) or not states:
            add(path + ".States", "States debe ser un diccionario no vacío.")
            return
        if isinstance(start, str) and start and start not in states:
            add(path + ".StartAt", f"El estado inicial '{start}' no existe en States.")
        for name, state in states.items():
            here = f"{path}.States[{name!r}]"
            if not isinstance(name, str) or not name:
                add(here, "El nombre del estado debe ser texto no vacío.")
            if not isinstance(state, dict):
                add(here, "El estado debe ser un diccionario.")
                continue
            kind = state.get("Type")
            if not isinstance(kind, str) or not kind:
                add(here + ".Type", "Type es requerido.")
            elif kind not in {"Pass", "Task", "Choice", "Wait", "Parallel", "Succeed", "Fail"}:
                add(here + ".Type", f"Type no soportado: {kind}.")
            if "End" in state and state["End"] is not True:
                add(here + ".End", "End debe ser true.")
            if "End" in state and "Next" in state:
                add(here, "End y Next son mutuamente excluyentes.")
            if "Next" in state:
                target = state["Next"]
                if not isinstance(target, str) or target not in states:
                    add(here + ".Next", "Next debe apuntar a un estado existente en esta rama.")
            if kind in ("Pass", "Task", "Wait", "Parallel") and "Next" not in state and state.get("End") is not True:
                add(here, "El estado requiere Next o End: true.")
            if kind in ("Succeed", "Fail") and "Next" in state:
                add(here + ".Next", "Un estado terminal no puede tener Next.")
            if kind == "Choice":
                if "End" in state or "Next" in state:
                    add(here, "Choice usa Choices y Default, no End ni Next.")
                choices = state.get("Choices")
                if not isinstance(choices, list) or not choices:
                    add(here + ".Choices", "Choices debe ser una lista no vacía.")
                else:
                    for i, rule in enumerate(choices):
                        check(f"{here}.Choices[{i}]", validate_choice,
                              {"Choices": [rule], "Default": name}, states)
                default = state.get("Default")
                if not isinstance(default, str) or default not in states:
                    add(here + ".Default", "Default debe apuntar a un estado existente.")
            if kind == "Task":
                check(here + ".Resource", resolve_task, state.get("Resource"))
                for policy in ("Retry", "Catch"):
                    rules = state.get(policy, [])
                    if not isinstance(rules, list):
                        add(here + "." + policy, "Debe ser una lista.")
                    else:
                        for i, rule in enumerate(rules):
                            check(f"{here}.{policy}[{i}]", validate_policies, {policy: [rule]}, states)
            if kind == "Wait":
                check(here + ".Seconds", validate_wait, state)
            if kind == "Parallel":
                branches = state.get("Branches")
                if not isinstance(branches, list) or not branches:
                    add(here + ".Branches", "Branches debe ser una lista no vacía.")
                else:
                    for i, branch in enumerate(branches):
                        visit(branch, f"{here}.Branches[{i}]")
    visit(definition, "definition")
    return errors


def require_valid_workflow(definition):
    errors = validate_workflow(definition)
    if errors:
        raise WorkflowValidationError(errors)
