import unittest
from unittest.mock import AsyncMock, patch

from app.engine.engine import WorkflowEngine
from app.tasks.registry import TASK_REGISTRY
from app.tasks.testing_tasks import PaymentTimeout, payment_timeout, payment_after_failures


def definition(attempts=3, catch=False):
    task = {"Type": "Task", "Resource": "task:test_retry", "Next": "Fin",
            "Retry": [{"ErrorEquals": ["PaymentTimeout"], "IntervalSeconds": 2,
                       "MaxAttempts": attempts, "BackoffRate": 2}]}
    if catch:
        task["Catch"] = [{"ErrorEquals": ["States.ALL"], "Next": "Manejar"}]
    return {"StartAt": "Pago", "States": {
        "Pago": task, "Fin": {"Type": "Succeed"},
        "Manejar": {"Type": "Pass", "Next": "Fin"}}}


class RetryTest(unittest.IsolatedAsyncioTestCase):
    async def test_backoff_then_success(self):
        with patch.dict(TASK_REGISTRY, {"task:test_retry": payment_after_failures(3)}):
            with patch("app.engine.engine.asyncio.sleep", new_callable=AsyncMock) as sleep:
                result = await WorkflowEngine().execute_async(definition(), {"id": 1})
                self.assertEqual([c.args[0] for c in sleep.await_args_list], [2, 4, 8])
                self.assertTrue(result["output"]["pago_procesado"])

    async def test_exhaustion_and_catch(self):
        for catch in (False, True):
            with patch.dict(TASK_REGISTRY, {"task:test_retry": payment_timeout}):
                with patch("app.engine.engine.asyncio.sleep", new_callable=AsyncMock) as sleep:
                    if catch:
                        result = await WorkflowEngine().execute_async(definition(2, True), {})
                        self.assertEqual(result["output"]["Error"], "PaymentTimeout")
                    else:
                        with self.assertRaises(PaymentTimeout):
                            await WorkflowEngine().execute_async(definition(2), {})
                    self.assertEqual(sleep.await_count, 2)

    async def test_zero_attempts_and_nonmatching_error(self):
        for d in (definition(0, True), definition(3, True)):
            d["States"]["Pago"]["Retry"][0]["ErrorEquals"] = ["OtherError"]
            with patch.dict(TASK_REGISTRY, {"task:test_retry": payment_timeout}):
                with patch("app.engine.engine.asyncio.sleep", new_callable=AsyncMock) as sleep:
                    await WorkflowEngine().execute_async(d, {})
                    sleep.assert_not_awaited()

    async def test_invalid_policy(self):
        for key, value in (("ErrorEquals", []), ("MaxAttempts", -1),
                           ("MaxAttempts", True), ("IntervalSeconds", -1),
                           ("BackoffRate", float("inf"))):
            d = definition()
            d["States"]["Pago"]["Retry"][0][key] = value
            with patch.dict(TASK_REGISTRY, {"task:test_retry": payment_timeout}):
                with self.assertRaises(ValueError):
                    await WorkflowEngine().execute_async(d, {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
