import asyncio
import inspect
from copy import deepcopy
from app.engine.retry import matching_rule, validate_policies

from app.tasks.registry import resolve_task
from app.states.choice import execute_choice, validate_choice
from app.states.wait import execute_wait, validate_wait
from app.states.parallel import execute_parallel


class WorkflowEngine:
    def __init__(self, observer=None):
        # Observador opcional; el motor no conoce SQLAlchemy ni transacciones.
        self.observer = observer

    def _finished(self, data, status="SUCCEEDED", error=None, cause=None):
        if self.observer is not None:
            self.observer.state_finished(data, status, error, cause)

    def execute(self, definition: dict, input_data: dict):
        """Entrada síncrona para scripts; en código async usar execute_async."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.execute_async(definition, input_data))
        raise RuntimeError("Usa await engine.execute_async(...) dentro de un event loop.")

    async def execute_async(self, definition: dict, input_data: dict):
        if not isinstance(input_data, dict):
            raise ValueError("input_data debe ser un diccionario.")
        return await self._execute_nested(definition, input_data)

    def validate_definition(self, definition):
        from app.engine.validator import require_valid_workflow
        require_valid_workflow(definition)

    async def _execute_nested(self, definition, input_data):
        self.validate_definition(definition)
        current_state_name = definition["StartAt"]
        data = input_data

        while True:
            executed_state_name = current_state_name
            state = definition["States"][current_state_name]
            state_type = state["Type"]

            if self.observer is not None:
                self.observer.state_started(current_state_name, state_type, data)

            print(
                f"Ejecutando estado: {current_state_name} "
                f"({state_type})"
            )

            if state_type == "Pass":
                if "Result" in state:
                    data = state["Result"]

                next_state = state.get("Next")

                if not next_state and not state.get("End"):
                    raise ValueError(
                        f"El estado Pass '{current_state_name}' "
                        "no tiene definido Next."
                    )

                current_state_name = next_state

            elif state_type == "Task":
                task = resolve_task(state.get("Resource"))
                attempts = {}
                retry_attempt = 0
                while True:
                    try:
                        if inspect.iscoroutinefunction(task):
                            output = await task(deepcopy(data))
                        else:
                            output = await asyncio.to_thread(task, deepcopy(data))
                    except Exception as exc:
                        error, cause = type(exc).__name__, str(exc)
                        index, rule = matching_rule(state.get("Retry", []), error)
                        used = attempts.get(index, 0)
                        if rule is not None and used < rule.get("MaxAttempts", 3):
                            delay = rule.get("IntervalSeconds", 1) * rule.get("BackoffRate", 2) ** used
                            attempts[index] = used + 1
                            retry_attempt += 1
                            self._finished(None, "RETRYING", error, cause)
                            await asyncio.sleep(delay)
                            if self.observer is not None:
                                self.observer.state_started(current_state_name, "Task", data, retry_attempt)
                            continue
                        _, catcher = matching_rule(state.get("Catch", []), error)
                        if catcher is None:
                            raise
                        self._finished(None, "FAILED", error, cause)
                        data = {"Error": error, "Cause": cause}
                        current_state_name = catcher["Next"]
                        break
                    else:
                        data = output
                        self._finished(data)
                        if state.get("End"):
                            return {"status": "SUCCEEDED", "output": data, "last_state": current_state_name}
                        current_state_name = state["Next"]
                        break
                continue

            elif state_type == "Choice":
                current_state_name = execute_choice(state, data)

            elif state_type == "Wait":
                current_state_name = await execute_wait(state)

            elif state_type == "Parallel":
                data = await execute_parallel(state, data, self.observer)
                current_state_name = state.get("Next")

            elif state_type == "Succeed":
                self._finished(data)
                return {
                    "status": "SUCCEEDED",
                    "output": data,
                    "last_state": current_state_name
                }

            elif state_type == "Fail":
                self._finished(
                    data, "FAILED", state.get("Error", "WorkflowFailed"),
                    state.get("Cause", "El workflow terminó en estado Fail.")
                )
                return {
                    "status": "FAILED",
                    "error": state.get(
                        "Error",
                        "WorkflowFailed"
                    ),
                    "cause": state.get(
                        "Cause",
                        "El workflow terminó en estado Fail."
                    ),
                    "last_state": current_state_name
                }

            else:
                raise NotImplementedError(
                    f"El tipo de estado '{state_type}' "
                    "todavía no está implementado."
                )

            self._finished(data)
            if state.get("End"):
                return {"status": "SUCCEEDED", "output": data,
                        "last_state": executed_state_name}
