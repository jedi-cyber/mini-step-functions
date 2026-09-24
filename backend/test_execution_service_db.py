"""Pruebas PostgreSQL aisladas mediante una transacción externa y savepoints."""

import unittest
from unittest.mock import patch

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.database.connection import engine
from app.models import Execution, ExecutionEvent, Workflow
from app.services.execution_service import ExecutionService
from app.tasks.registry import TASK_REGISTRY
from app.tasks.testing_tasks import payment_timeout, payment_after_failures, PaymentTimeout
from test_engine_retry import definition
from unittest.mock import AsyncMock


class ExecutionPersistenceTest(unittest.TestCase):
    def test_parallel_history_and_failure(self):
        from app.states.parallel import ParallelBranchError
        for failed in (False, True):
            branches = [
                {"StartAt": "A", "States": {"A": {"Type": "Pass", "Result": 1, "End": True}}},
                {"StartAt": "B", "States": {"B": (
                    {"Type": "Fail", "Error": "BranchFailed"} if failed else
                    {"Type": "Pass", "Result": 2, "End": True}
                )}},
            ]
            workflow_id = self.create_workflow({
                "Inicio": {"Type": "Parallel", "Branches": branches, "End": True}
            })
            if failed:
                with self.assertRaises(ParallelBranchError):
                    self.service.execute_workflow(workflow_id, {})
            else:
                self.service.execute_workflow(workflow_id, {})
            with self.sessions() as db:
                execution = db.scalar(select(Execution).where(Execution.workflow_id == workflow_id))
                self.assertEqual(execution.status, "FAILED" if failed else "SUCCEEDED")
                self.assertEqual(execution.current_state, "Inicio")
                self.assertEqual([e.event_order for e in execution.events], [1, 2, 3])
                self.assertEqual([e.state_name for e in execution.events], ["Inicio", "A", "B"])
                self.assertEqual(execution.events[0].status, execution.status)
                self.assertTrue(all(e.finished_at for e in execution.events))
                if not failed:
                    self.assertEqual(execution.output, [1, 2])

    def test_retry_history(self):
        for mode in ("success", "catch", "failed"):
            d = definition(2, mode == "catch")
            states = d["States"]
            states["Inicio"] = states.pop("Pago")
            workflow_id = self.create_workflow(states)
            task = payment_after_failures(2) if mode == "success" else payment_timeout
            with patch.dict(TASK_REGISTRY, {"task:test_retry": task}):
                with patch("app.engine.engine.asyncio.sleep", new_callable=AsyncMock):
                    if mode == "failed":
                        with self.assertRaises(PaymentTimeout):
                            self.service.execute_workflow(workflow_id, {"id": 1})
                    else:
                        self.service.execute_workflow(workflow_id, {"id": 1})
            with self.sessions() as db:
                execution = db.scalar(select(Execution).where(Execution.workflow_id == workflow_id))
                self.assertEqual(execution.status, "FAILED" if mode == "failed" else "SUCCEEDED")
                events = execution.events
                self.assertEqual([e.status for e in events[:2]], ["RETRYING", "RETRYING"])
                self.assertEqual([e.retry_attempt for e in events[:3]], [0, 1, 2])
                self.assertEqual(events[2].status, "SUCCEEDED" if mode == "success" else "FAILED")
                self.assertEqual([e.event_order for e in events], list(range(1, len(events) + 1)))
                self.assertEqual(events[0].error, "PaymentTimeout")
                self.assertTrue(all(e.finished_at is not None for e in events))
                if mode == "catch":
                    self.assertEqual(events[3].state_name, "Manejar")
                    self.assertEqual(events[3].input["Error"], "PaymentTimeout")

    def setUp(self):
        self.connection = engine.connect()
        self.addCleanup(self.connection.close)
        self.transaction = self.connection.begin()
        self.addCleanup(self.transaction.rollback)
        self.sessions = sessionmaker(bind=self.connection, join_transaction_mode="create_savepoint")
        self.service = ExecutionService(self.sessions)

    def create_workflow(self, states):
        with self.sessions() as db:
            workflow = Workflow(name="Prueba persistencia", definition={"StartAt": "Inicio", "States": states})
            db.add(workflow)
            db.commit()
            return workflow.id

    def test_success_and_event_snapshots(self):
        workflow_id = self.create_workflow({
            "Inicio": {"Type": "Pass", "Result": {"nuevo": 2}, "Next": "Fin"},
            "Fin": {"Type": "Succeed"},
        })
        result = self.service.execute_workflow(workflow_id, {"original": 1})
        with self.sessions() as db:
            execution = db.get(Execution, result["execution_id"])
            self.assertEqual(execution.status, "SUCCEEDED")
            self.assertEqual(execution.input, {"original": 1})
            self.assertEqual(execution.output, {"nuevo": 2})
            self.assertEqual(execution.current_state, "Fin")
            self.assertLessEqual(execution.started_at, execution.finished_at)
            events = execution.events
            self.assertEqual([e.event_order for e in events], [1, 2])
            self.assertEqual([e.state_type for e in events], ["Pass", "Succeed"])
            self.assertEqual(events[0].input, {"original": 1})
            self.assertEqual(events[1].input, {"nuevo": 2})
            for event in events:
                self.assertEqual(event.status, "SUCCEEDED")
                self.assertEqual(event.output, {"nuevo": 2})
                self.assertIsNone(event.error)
                self.assertLessEqual(event.started_at, event.finished_at)

    def test_fail_state(self):
        workflow_id = self.create_workflow({"Inicio": {
            "Type": "Fail", "Error": "Rechazado", "Cause": "Pedido inválido"
        }})
        result = self.service.execute_workflow(workflow_id, {"id": 1})
        with self.sessions() as db:
            execution = db.get(Execution, result["execution_id"])
            self.assertEqual(execution.status, "FAILED")
            self.assertEqual(execution.output, {"id": 1})
            self.assertEqual(execution.error, "Rechazado")
            self.assertIsNotNone(execution.finished_at)
            self.assertEqual(execution.events[0].status, "FAILED")
            self.assertEqual(execution.events[0].cause, "Pedido inválido")

    def test_running_visible_and_task_error(self):
        def broken_task(data):
            with self.sessions() as db:
                execution = db.scalar(select(Execution).where(Execution.workflow_id == workflow_id))
                self.assertEqual(execution.status, "RUNNING")
                self.assertEqual(execution.current_state, "Inicio")
                self.assertIsNone(execution.finished_at)
                self.assertEqual(execution.events[0].status, "RUNNING")
            data["nested"]["value"] = 99
            raise ValueError("Error de tarea")

        workflow_id = self.create_workflow({
            "Inicio": {"Type": "Task", "Resource": "task:test", "Next": "Fin"},
            "Fin": {"Type": "Succeed"},
        })
        with patch.dict(TASK_REGISTRY, {"task:test": broken_task}):
            with self.assertRaisesRegex(ValueError, "Error de tarea"):
                self.service.execute_workflow(workflow_id, {"nested": {"value": 1}})
        with self.sessions() as db:
            execution = db.scalar(select(Execution).where(Execution.workflow_id == workflow_id))
            self.assertEqual(execution.status, "FAILED")
            self.assertIsNotNone(execution.finished_at)
            self.assertEqual(len(execution.events), 1)
            event = execution.events[0]
            self.assertEqual(event.input, {"nested": {"value": 1}})
            self.assertEqual(event.status, "FAILED")
            self.assertEqual(event.error, "ValueError")
            self.assertIsNotNone(event.finished_at)


if __name__ == "__main__":
    unittest.main(verbosity=2)
