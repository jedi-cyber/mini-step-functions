import unittest
from copy import deepcopy

from app.engine.engine import WorkflowEngine


class WorkflowEngineTest(unittest.TestCase):
    def setUp(self):
        self.engine = WorkflowEngine()
        self.definition = {
            "StartAt": "Inicio",
            "States": {
                "Inicio": {"Type": "Pass", "Next": "Final"},
                "Final": {"Type": "Succeed"},
            },
        }

    def test_pass_preserves_input(self):
        data = {"pedido": {"id": 1}}
        original = deepcopy(data)
        result = self.engine.execute(self.definition, data)
        self.assertEqual(result, {
            "status": "SUCCEEDED", "output": original, "last_state": "Final"
        })
        self.assertEqual(data, original)

    def test_result_replaces_data_and_survives_another_pass(self):
        for value in ({"ok": True}, None, False, 0, "", []):
            with self.subTest(result=value):
                definition = deepcopy(self.definition)
                definition["States"]["Inicio"].update(Result=value, Next="Otro")
                definition["States"]["Otro"] = {"Type": "Pass", "Next": "Final"}
                original_definition = deepcopy(definition)
                data = {"original": True}
                result = self.engine.execute(definition, data)
                self.assertEqual(result["output"], value)
                self.assertEqual(data, {"original": True})
                self.assertEqual(definition, original_definition)

    def test_succeed_directly(self):
        result = self.engine.execute({
            "StartAt": "Fin", "States": {"Fin": {"Type": "Succeed"}}
        }, {})
        self.assertEqual(result["status"], "SUCCEEDED")

    def test_fail_returns_error_and_cause(self):
        self.definition["States"]["Final"] = {
            "Type": "Fail", "Error": "PedidoInvalido", "Cause": "Falta id"
        }
        self.assertEqual(self.engine.execute(self.definition, {}), {
            "status": "FAILED", "error": "PedidoInvalido",
            "cause": "Falta id", "last_state": "Final",
        })

    def test_fail_defaults(self):
        self.definition["States"]["Final"] = {"Type": "Fail"}
        result = self.engine.execute(self.definition, {})
        self.assertEqual(result["error"], "WorkflowFailed")
        self.assertTrue(result["cause"])

    def test_invalid_definitions(self):
        cases = [
            (None, "definition"),
            ({}, "States"),
            ({"States": []}, "States"),
            ({"States": {}}, "States"),
            ({"States": {"A": {"Type": "Succeed"}}}, "StartAt"),
            ({"StartAt": [], "States": {"A": {}}}, "StartAt"),
            ({"StartAt": "Missing", "States": {"A": {}}}, "no existe"),
            ({"StartAt": "A", "States": {"A": None}}, "diccionario"),
            ({"StartAt": "A", "States": {"A": {}}}, "Type"),
            ({"StartAt": "A", "States": {"A": {"Type": ""}}}, "Type"),
            ({"StartAt": "A", "States": {"A": {"Type": "Pass"}}}, "Next"),
        ]
        for definition, message in cases:
            with self.subTest(definition=definition):
                with self.assertRaisesRegex(ValueError, message):
                    self.engine.execute(definition, {})

    def test_invalid_next(self):
        for target in ("Missing", None, [], 42, ""):
            with self.subTest(target=target):
                self.definition["States"]["Inicio"]["Next"] = target
                with self.assertRaisesRegex(ValueError, "Next"):
                    self.engine.execute(self.definition, {})

    def test_invalid_input(self):
        with self.assertRaisesRegex(ValueError, "input_data"):
            self.engine.execute(self.definition, [])

    def test_unsupported_states(self):
        for state_type in ("Map",):
            with self.subTest(state_type=state_type):
                definition = {
                    "StartAt": "A", "States": {"A": {"Type": state_type}}
                }
                with self.assertRaisesRegex(ValueError, "no soportado"):
                    self.engine.execute(definition, {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
