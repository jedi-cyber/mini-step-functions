import asyncio
import unittest
from unittest.mock import patch

from app.engine.engine import WorkflowEngine
from app.states.parallel import ParallelBranchError
from app.tasks.registry import TASK_REGISTRY


def parallel(branches):
    return {"StartAt": "P", "States": {
        "P": {"Type": "Parallel", "Branches": branches, "Next": "Fin"},
        "Fin": {"Type": "Succeed"}}}


def branch(resource):
    return {"StartAt": "T", "States": {
        "T": {"Type": "Task", "Resource": resource, "End": True}}}


class ParallelTest(unittest.IsolatedAsyncioTestCase):
    async def test_concurrency_order_and_isolation(self):
        ready = asyncio.Event()
        async def first(data):
            data["nested"]["id"] = 2
            await asyncio.wait_for(ready.wait(), 2)
            return data
        async def second(data):
            ready.set()
            return data
        original = {"nested": {"id": 1}}
        with patch.dict(TASK_REGISTRY, {"task:first": first, "task:second": second}):
            result = await WorkflowEngine().execute_async(
                parallel([branch("task:first"), branch("task:second")]), original)
        self.assertEqual(result["output"], [{"nested": {"id": 2}}, original])
        self.assertEqual(original, {"nested": {"id": 1}})

    async def test_failure_waits_for_remaining_branch(self):
        completed = []
        async def bad(data):
            raise ValueError("broken")
        async def good(data):
            await asyncio.sleep(0)
            completed.append(True)
            return data
        with patch.dict(TASK_REGISTRY, {"task:bad": bad, "task:good": good}):
            with self.assertRaisesRegex(ParallelBranchError, "broken"):
                await WorkflowEngine().execute_async(parallel([branch("task:bad"), branch("task:good")]), {})
        self.assertEqual(completed, [True])

    async def test_fail_state(self):
        failed = {"StartAt": "F", "States": {"F": {"Type": "Fail", "Error": "No"}}}
        with self.assertRaisesRegex(ParallelBranchError, "No"):
            await WorkflowEngine().execute_async(parallel([failed]), {})

    async def test_nested_parallel_end(self):
        leaf = {"StartAt": "A", "States": {"A": {"Type": "Pass", "Result": 3, "End": True}}}
        nested = {"StartAt": "B", "States": {"B": {"Type": "Parallel", "Branches": [leaf], "End": True}}}
        result = await WorkflowEngine().execute_async(parallel([nested]), {})
        self.assertEqual(result["output"], [[3]])

    async def test_invalid_branches_and_end(self):
        for branches in (None, [], {}, [{}]):
            with self.assertRaises(ValueError):
                await WorkflowEngine().execute_async(parallel(branches), {})
        invalid = {"StartAt": "A", "States": {"A": {"Type": "Pass", "End": True, "Next": "A"}}}
        with self.assertRaises(ValueError):
            await WorkflowEngine().execute_async(parallel([invalid]), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
