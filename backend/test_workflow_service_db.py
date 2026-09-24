"""Integración PostgreSQL -> servicio -> motor, con rollback al terminar."""

import json
import unittest

from app.database.connection import SessionLocal
from app.models import Workflow
from app.services.workflow_service import WorkflowNotFoundError, WorkflowService


class WorkflowServiceDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.addCleanup(self.db.close)
        self.addCleanup(self.db.rollback)
        workflow = Workflow(
            name="Prueba de integración Pass -> Succeed",
            definition={
                "StartAt": "Inicio",
                "States": {
                    "Inicio": {"Type": "Pass", "Next": "Final"},
                    "Final": {"Type": "Succeed"},
                },
            },
        )
        self.db.add(workflow)
        self.db.flush()
        self.workflow_id = workflow.id
        # Obliga al servicio a cargar la definición desde PostgreSQL.
        self.db.expunge_all()
        self.service = WorkflowService(self.db)

    def test_execute_stored_workflow(self):
        input_data = {"cliente": "Jedidias", "pedido_id": 1001, "total": 250}
        result = self.service.execute_workflow(self.workflow_id, input_data)
        self.assertEqual(result, {
            "status": "SUCCEEDED",
            "output": input_data,
            "last_state": "Final",
        })
        print("Resultado final:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    def test_missing_workflow(self):
        # El ID generado deja de existir al revertir la inserción temporal.
        self.db.rollback()
        with self.assertRaises(WorkflowNotFoundError):
            self.service.execute_workflow(self.workflow_id, {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
