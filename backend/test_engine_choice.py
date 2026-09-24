import unittest
from copy import deepcopy

from app.engine.engine import WorkflowEngine
from app.engine.json_path import MISSING, resolve_json_path


class ChoiceTest(unittest.TestCase):
    def definition(self, comparator="BooleanEquals", expected=True, path="$.pedido_valido"):
        return {
            "StartAt": "Elegir",
            "States": {
                "Elegir": {
                    "Type": "Choice",
                    "Choices": [{"Variable": path, comparator: expected, "Next": "Si"}],
                    "Default": "No",
                },
                "Si": {"Type": "Succeed"},
                "No": {"Type": "Fail", "Error": "Rechazado", "Cause": "Sin coincidencias"},
            },
        }

    def test_all_comparators(self):
        cases = [
            ("BooleanEquals", True, True, False),
            ("StringEquals", "VIP", "VIP", "vip"),
            ("NumericEquals", 10, 10.0, 11),
            ("NumericGreaterThan", 10, 11, 10),
            ("NumericGreaterThanEquals", 10, 10, 9),
            ("NumericLessThan", 10, 9, 10),
            ("NumericLessThanEquals", 10, 10, 11),
        ]
        for comparator, expected, match, miss in cases:
            for value, status in ((match, "SUCCEEDED"), (miss, "FAILED")):
                with self.subTest(comparator=comparator, value=value):
                    definition = self.definition(comparator, expected, "$.pedido.total")
                    data = {"pedido": {"total": value}}
                    original = deepcopy(data)
                    result = WorkflowEngine().execute(definition, data)
                    self.assertEqual(result["status"], status)
                    self.assertEqual(data, original)
                    if status == "SUCCEEDED":
                        self.assertEqual(result["output"], data)

    def test_paths(self):
        self.assertEqual(resolve_json_path({"cliente": {"edad": 18}}, "$.cliente.edad"), 18)
        self.assertIsNone(resolve_json_path({"cliente": None}, "$.cliente"))
        for data in ({}, {"cliente": None}, {"cliente": []}):
            self.assertIs(resolve_json_path(data, "$.cliente.edad"), MISSING)
        for path in (None, "cliente.edad", "$", "$..edad", "$.items[0]", "$.x."):
            with self.assertRaises(ValueError):
                resolve_json_path({}, path)

    def test_missing_and_wrong_types_use_default(self):
        for comparator, expected, values in (
            ("BooleanEquals", True, [1, "true", None]),
            ("NumericEquals", 1, [True, "1", None]),
            ("StringEquals", "1", [1, True, None]),
        ):
            for data in [{}, *({"pedido_valido": value} for value in values)]:
                with self.subTest(comparator=comparator, data=data):
                    result = WorkflowEngine().execute(self.definition(comparator, expected), data)
                    self.assertEqual(result["last_state"], "No")

    def test_first_matching_rule_wins(self):
        definition = self.definition()
        definition["States"]["Elegir"]["Choices"].append({
            "Variable": "$.pedido_valido", "BooleanEquals": True, "Next": "No"
        })
        self.assertEqual(WorkflowEngine().execute(definition, {"pedido_valido": True})["last_state"], "Si")

    def test_invalid_choice_definitions(self):
        variants = [
            {"Default": "Missing"}, {"Default": None}, {"Choices": []},
            {"Choices": {}}, {"Choices": [None]},
        ]
        for rule in (
            {"Variable": "$.x", "BooleanEquals": True},
            {"Variable": "$.x", "BooleanEquals": True, "Next": "Missing"},
            {"Variable": "$.x", "BooleanEquals": 1, "Next": "Si"},
            {"Variable": "$.x", "NumericEquals": True, "Next": "Si"},
            {"Variable": "$.x", "StringEquals": 1, "Next": "Si"},
            {"Variable": "$.x", "Next": "Si"},
            {"Variable": "$.x", "IsPresent": True, "Next": "Si"},
            {"Variable": "$.x", "BooleanEquals": True, "StringEquals": "x", "Next": "Si"},
            {"BooleanEquals": True, "Next": "Si"},
        ):
            variants.append({"Choices": [rule]})
        for changes in variants:
            with self.subTest(changes=changes):
                definition = self.definition()
                definition["States"]["Elegir"].update(changes)
                with self.assertRaises(ValueError):
                    WorkflowEngine().execute(definition, {})

    def test_task_choice_integration(self):
        definition = self.definition()
        definition["StartAt"] = "Validar"
        definition["States"]["Validar"] = {
            "Type": "Task", "Resource": "task:validar_pedido", "Next": "Elegir"
        }
        definition["States"]["Elegir"]["Choices"][0]["Next"] = "Pagar"
        definition["States"]["Pagar"] = {
            "Type": "Task", "Resource": "task:procesar_pago", "Next": "Si"
        }
        result = WorkflowEngine().execute(definition, {"pedido_id": 1, "total": 250})
        self.assertTrue(result["output"]["pago_procesado"])
        result = WorkflowEngine().execute(definition, {"pedido_id": 1, "total": -1})
        self.assertEqual(result["error"], "Rechazado")


if __name__ == "__main__":
    unittest.main(verbosity=2)
