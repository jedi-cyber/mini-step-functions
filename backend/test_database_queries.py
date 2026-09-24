"""Prueba de lectura de PostgreSQL; no crea ni modifica registros."""

import unittest

from sqlalchemy import select, text

from app.database.connection import SessionLocal
from app.models import Execution, ExecutionEvent, Workflow


class DatabaseQueriesTest(unittest.TestCase):
    def test_stored_workflow_and_execution_tables(self):
        with SessionLocal() as db:
            db.execute(text("SET TRANSACTION READ ONLY"))

            workflow = db.scalar(select(Workflow).order_by(Workflow.id).limit(1))
            self.assertIsNotNone(
                workflow,
                "Se necesita al menos un workflow almacenado para esta prueba.",
            )
            self.assertIsInstance(workflow.definition, dict)
            print(f"Workflow consultado: id={workflow.id}; definition es dict")

            executions = db.scalars(
                select(Execution).order_by(Execution.id).limit(5)
            ).all()
            events = db.scalars(
                select(ExecutionEvent)
                .order_by(ExecutionEvent.execution_id, ExecutionEvent.event_order)
                .limit(5)
            ).all()

            for execution in executions:
                self.assertIsInstance(execution, Execution)
                self.assertEqual(execution.workflow.id, execution.workflow_id)
            for event in events:
                self.assertIsInstance(event, ExecutionEvent)
                self.assertEqual(event.execution.id, event.execution_id)

            print(f"Consulta executions OK: {len(executions)} filas (limite 5)")
            print(f"Consulta execution_events OK: {len(events)} filas (limite 5)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
