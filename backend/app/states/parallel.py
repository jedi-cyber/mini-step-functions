import asyncio
from copy import deepcopy


class ParallelBranchError(RuntimeError):
    """Una rama falló; incluye su índice, error y causa."""


async def execute_parallel(state, data, observer=None):
    from app.engine.engine import WorkflowEngine

    async def run_branch(index, definition):
        child = observer.fork() if observer is not None else None
        try:
            result = await WorkflowEngine(child)._execute_nested(definition, deepcopy(data))
        except Exception as exc:
            if child is not None and child.event is not None:
                child.state_finished(None, "FAILED", type(exc).__name__, str(exc))
            raise ParallelBranchError(f"Rama {index}: {type(exc).__name__}: {exc}") from exc
        if result["status"] != "SUCCEEDED":
            raise ParallelBranchError(f"Rama {index}: {result.get('error')}: {result.get('cause')}")
        return result["output"]

    # Espera también a las ramas restantes si una falla; mantiene orden de entrada.
    results = await asyncio.gather(
        *(run_branch(index, branch) for index, branch in enumerate(state["Branches"])),
        return_exceptions=True,
    )
    for result in results:
        if isinstance(result, BaseException):
            raise result
    return results
