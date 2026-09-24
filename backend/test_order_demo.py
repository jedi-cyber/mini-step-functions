import asyncio
import json
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from app.engine.engine import WorkflowEngine


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class OrderDemoTest(unittest.IsolatedAsyncioTestCase):
    async def test_scenarios(self):
        definition = json.loads((EXAMPLES / "pedido.json").read_text(encoding="utf-8"))
        for scenario, status, delays in (
            ("exitoso", "SUCCEEDED", [3]), ("invalido", "FAILED", []),
            ("recuperable", "SUCCEEDED", [2, 4, 3]), ("definitivo", "FAILED", [2, 4, 8])
        ):
            with self.subTest(scenario=scenario):
                data = json.loads((EXAMPLES / "inputs" / f"pedido-{scenario}.json").read_text())
                with patch("asyncio.sleep", new_callable=AsyncMock) as sleep:
                    result = await WorkflowEngine().execute_async(definition, data)
                self.assertEqual(result["status"], status)
                self.assertEqual([c.args[0] for c in sleep.await_args_list], delays)
                if status == "SUCCEEDED":
                    self.assertEqual(result["last_state"], "PedidoCompletado")
                    self.assertEqual(len(result["output"]), 2)
                    self.assertEqual(result["output"][0]["intentos_pago"], 3 if scenario == "recuperable" else 1)
                    self.assertTrue(result["output"][1]["correo_enviado"])
                else:
                    self.assertEqual(result["error"], "PedidoInvalido" if scenario == "invalido" else "PagoFallido")

    async def test_concurrent_executions_keep_independent_attempts(self):
        definition = json.loads((EXAMPLES / "pedido.json").read_text())
        data = json.loads((EXAMPLES / "inputs/pedido-recuperable.json").read_text())
        with patch("asyncio.sleep", new_callable=AsyncMock):
            results = await asyncio.gather(*(WorkflowEngine().execute_async(definition, data) for _ in range(3)))
        self.assertEqual([r["output"][0]["intentos_pago"] for r in results], [3, 3, 3])


if __name__ == "__main__":
    unittest.main(verbosity=2)
