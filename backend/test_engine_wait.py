import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from app.engine.engine import WorkflowEngine


def workflow(seconds=0):
    return {
        "StartAt": "Esperar",
        "States": {
            "Esperar": {"Type": "Wait", "Seconds": seconds, "Next": "Fin"},
            "Fin": {"Type": "Succeed"},
        },
    }


class WaitTest(unittest.IsolatedAsyncioTestCase):
    async def test_seconds_and_output(self):
        for seconds in (0, 0.25, 3):
            with self.subTest(seconds=seconds):
                with patch("app.states.wait.asyncio.sleep", new_callable=AsyncMock) as sleep:
                    data = {"pedido": {"id": 1}}
                    result = await WorkflowEngine().execute_async(workflow(seconds), data)
                    sleep.assert_awaited_once_with(seconds)
                    self.assertEqual(result, {
                        "status": "SUCCEEDED", "output": data, "last_state": "Fin"
                    })
                    self.assertEqual(data, {"pedido": {"id": 1}})

    async def test_invalid_seconds_and_next(self):
        definitions = [workflow(value) for value in (
            None, True, False, "3", -1, -0.5, [], {}, float("nan"), float("inf")
        )]
        missing = workflow()
        del missing["States"]["Esperar"]["Seconds"]
        definitions.append(missing)
        for target in (None, [], "Missing"):
            definition = workflow()
            definition["States"]["Esperar"]["Next"] = target
            definitions.append(definition)
        missing_next = workflow()
        del missing_next["States"]["Esperar"]["Next"]
        definitions.append(missing_next)
        for key in ("Timestamp", "SecondsPath", "TimestampPath"):
            definition = workflow()
            definition["States"]["Esperar"][key] = "unsupported"
            definitions.append(definition)
        for definition in definitions:
            with self.subTest(definition=definition):
                with patch("app.states.wait.asyncio.sleep", new_callable=AsyncMock) as sleep:
                    with self.assertRaises(ValueError):
                        await WorkflowEngine().execute_async(definition, {})
                    sleep.assert_not_awaited()

    async def test_wait_yields_to_other_coroutines(self):
        # Con Seconds=0, asyncio.sleep debe ceder el control igualmente.
        pending = asyncio.create_task(WorkflowEngine().execute_async(workflow(), {}))
        await asyncio.sleep(0)
        self.assertFalse(pending.done())
        self.assertEqual((await pending)["status"], "SUCCEEDED")

    async def test_cancellation_interrupts_wait(self):
        pending = asyncio.create_task(WorkflowEngine().execute_async(workflow(60), {}))
        await asyncio.sleep(0)
        pending.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await pending

    async def test_sync_entry_rejects_running_loop(self):
        with self.assertRaisesRegex(RuntimeError, "execute_async"):
            WorkflowEngine().execute(workflow(), {})


class SyncWaitTest(unittest.TestCase):
    def test_existing_sync_entry(self):
        self.assertEqual(WorkflowEngine().execute(workflow(), {})["status"], "SUCCEEDED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
