import unittest
from unittest.mock import Mock, patch

from app.engine.engine import WorkflowEngine
from app.tasks.order_tasks import procesar_pago, validar_pedido
from app.tasks.registry import TASK_REGISTRY, TaskResourceError


class TaskStateTest(unittest.TestCase):
    def setUp(self):
        self.definition = {
            "StartAt": "Validar",
            "States": {
                "Validar": {"Type": "Task", "Resource": "task:validar_pedido", "Next": "Pagar"},
                "Pagar": {"Type": "Task", "Resource": "task:procesar_pago", "Next": "Fin"},
                "Fin": {"Type": "Succeed"},
            },
        }
        self.engine = WorkflowEngine()

    def test_order_tasks_chain(self):
        data = {"pedido_id": 1001, "total": 250}
        result = self.engine.execute(self.definition, data)
        self.assertEqual(result, {
            "status": "SUCCEEDED", "last_state": "Fin",
            "output": {**data, "pedido_valido": True,
                       "pago_procesado": True, "pago_estado": "APROBADO"},
        })
        self.assertEqual(data, {"pedido_id": 1001, "total": 250})

    def test_missing_or_unknown_resource(self):
        for resource in (None, "", [], 42, "task:desconocida"):
            with self.subTest(resource=resource):
                self.definition["States"]["Validar"]["Resource"] = resource
                with self.assertRaises(TaskResourceError):
                    self.engine.execute(self.definition, {})
        del self.definition["States"]["Validar"]["Resource"]
        with self.assertRaises(TaskResourceError):
            self.engine.execute(self.definition, {})

    def test_next_validated_before_task_runs(self):
        task = Mock()
        with patch.dict(TASK_REGISTRY, {"task:validar_pedido": task}):
            for target in (None, "Missing", [], ""):
                self.definition["States"]["Validar"]["Next"] = target
                with self.assertRaisesRegex(ValueError, "Next"):
                    self.engine.execute(self.definition, {})
            del self.definition["States"]["Validar"]["Next"]
            with self.assertRaisesRegex(ValueError, "Next"):
                self.engine.execute(self.definition, {})
        task.assert_not_called()

    def test_output_replaces_input_including_null(self):
        for output in (None, {"nuevo": True}, 0):
            with self.subTest(output=output):
                task = Mock(return_value=output)
                self.definition["States"]["Validar"]["Next"] = "Fin"
                with patch.dict(TASK_REGISTRY, {"task:validar_pedido": task}):
                    result = self.engine.execute(self.definition, {"entrada": 1})
                task.assert_called_once_with({"entrada": 1})
                self.assertEqual(result["output"], output)

    def test_task_exception_stops_execution_without_retry(self):
        task = Mock(side_effect=ValueError("Fallo de tarea"))
        payment = Mock()
        with patch.dict(TASK_REGISTRY, {
            "task:validar_pedido": task, "task:procesar_pago": payment
        }):
            with self.assertRaisesRegex(ValueError, "Fallo de tarea"):
                self.engine.execute(self.definition, {})
        task.assert_called_once()
        payment.assert_not_called()

    def test_invalid_orders(self):
        for data in ({}, {"pedido_id": True, "total": 5},
                     {"pedido_id": 1, "total": -1},
                     {"pedido_id": 1, "total": "250"},
                     {"pedido_id": 1, "total": float("inf")}):
            with self.subTest(data=data):
                self.assertFalse(validar_pedido(data)["pedido_valido"])
                with self.assertRaises(ValueError):
                    procesar_pago(data)

    def test_demo_tasks_require_dictionary(self):
        for task in (validar_pedido, procesar_pago):
            with self.assertRaises(ValueError):
                task(None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
