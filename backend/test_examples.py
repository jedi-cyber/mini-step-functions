"""Comprueba las definiciones publicadas y los resultados de los ejemplos básicos."""

import json
import unittest
from pathlib import Path

from app.engine.engine import WorkflowEngine


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def load_example(name):
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


class ExamplesTest(unittest.TestCase):
    def test_all_definitions_and_inputs_are_valid(self):
        for path in sorted(EXAMPLES.rglob("*.json")):
            with self.subTest(path=path.relative_to(EXAMPLES)):
                value = load_example(path.relative_to(EXAMPLES))
                if path.parent == EXAMPLES:
                    WorkflowEngine().validate_definition(value)
                else:
                    self.assertIsInstance(value, dict)

    def test_parallel_collects_both_branch_results(self):
        result = WorkflowEngine().execute(load_example("parallel.json"), {})
        self.assertEqual(result["status"], "SUCCEEDED")
        self.assertEqual(result["last_state"], "Completado")
        self.assertEqual(result["output"], [
            {"rama": "resumen", "completada": True},
            {"rama": "notificacion", "completada": True},
        ])

    def test_approval_routes_to_success_or_failure(self):
        definition = load_example("aprobacion.json")
        for approved in (True, False):
            with self.subTest(approved=approved):
                data = {"aprobado": approved, "solicitud_id": 1}
                result = WorkflowEngine().execute(definition, data)
                if approved:
                    self.assertEqual(result["status"], "SUCCEEDED")
                    self.assertEqual(result["last_state"], "Aprobada")
                    self.assertEqual(result["output"], data)
                else:
                    self.assertEqual(result["status"], "FAILED")
                    self.assertEqual(result["last_state"], "Rechazada")
                    self.assertEqual(result["error"], "SolicitudRechazada")


if __name__ == "__main__":
    unittest.main(verbosity=2)
