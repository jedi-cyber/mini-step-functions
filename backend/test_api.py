import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.connection import engine, get_db
from app.api.dependencies import execution_service
from app.services.execution_service import ExecutionService
from app.models import Execution

from sqlalchemy import (select, func)

class ApiTest(unittest.TestCase):
    def test_validation_list_on_create_update_and_execute(self):
        from app.models import Workflow, Execution
        from sqlalchemy import select, func
        workflow_id = self.create()
        bad = {"StartAt": "Missing", "States": {
            "A": {"Type": "Task", "End": True},
            "B": {"Type": "Wait", "End": True}}}
        payload = {"name": "Invalid", "definition": bad}
        for method, url in (("post", "/api/workflows"), ("put", f"/api/workflows/{workflow_id}")):
            response = getattr(self.client, method)(url, json=payload)
            self.assertEqual(response.status_code, 422, response.text)
            self.assertGreaterEqual(len(response.json()["detail"]), 3)
            self.assertIn("path", response.json()["detail"][0])
        self.assertEqual(self.client.get(f"/api/workflows/{workflow_id}").json()["name"], "API test")
        # Simula una definición inválida almacenada antes de incorporar el validador.
        with self.sessions() as db:
            db.get(Workflow, workflow_id).definition = bad
            db.commit()
        response = self.client.post(f"/api/workflows/{workflow_id}/execute", json={})
        self.assertEqual(response.status_code, 422, response.text)
        self.assertGreaterEqual(len(response.json()["detail"]), 3)
        with self.sessions() as db:
            self.assertEqual(db.scalar(select(func.count()).select_from(Execution).where(Execution.workflow_id == workflow_id)), 0)

    def setUp(self):
        connection = engine.connect()
        self.addCleanup(connection.close)
        transaction = connection.begin()
        self.addCleanup(transaction.rollback)
        sessions = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")
        self.sessions = sessions
        def db_override():
            with sessions() as db:
                yield db
        app.dependency_overrides[get_db] = db_override
        app.dependency_overrides[execution_service] = lambda: ExecutionService(sessions)
        self.addCleanup(app.dependency_overrides.clear)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        self.body = {"name": "API test", "definition": {
            "StartAt": "Inicio", "States": {
                "Inicio": {"Type": "Pass", "Next": "Fin"},
                "Fin": {"Type": "Succeed"}}}}

    def create(self, body=None):
        response = self.client.post("/api/workflows", json=body or self.body)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["id"]

    def test_crud_execute_events(self):
        workflow_id = self.create()
        url = f"/api/workflows/{workflow_id}"
        self.assertEqual(self.client.get(url).json()["name"], "API test")
        self.assertEqual(self.client.get("/api/workflows").status_code, 200)
        self.body["name"] = "Updated"
        self.assertEqual(self.client.put(url, json=self.body).json()["name"], "Updated")
        response = self.client.post(url + "/execute", json={"input": {"id": 1}})
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["status"], "SUCCEEDED")
        self.assertEqual(result["output"], {"id": 1})
        execution_url = f"/api/executions/{result['execution_id']}"
        self.assertEqual(self.client.get(execution_url).json()["workflow_id"], workflow_id)
        self.assertEqual(self.client.get("/api/executions").status_code, 200)
        events = self.client.get(execution_url + "/events").json()
        self.assertEqual([e["event_order"] for e in events], [1, 2])

    def test_not_found_and_bad_requests(self):
        for path in ("/api/workflows/-1", "/api/executions/-1", "/api/executions/-1/events"):
            self.assertEqual(self.client.get(path).status_code, 404)
        self.assertEqual(self.client.put("/api/workflows/-1", json=self.body).status_code, 404)
        self.assertEqual(self.client.post("/api/workflows/-1/execute", json={}).status_code, 404)
        self.assertEqual(self.client.post("/api/workflows", content="{", headers={"Content-Type": "application/json"}).status_code, 400)
        for definition in ({}, {"StartAt": "A", "States": {"A": {"Type": "Map"}}}):
            self.assertEqual(self.client.post("/api/workflows", json={"name": "invalid", "definition": definition}).status_code, 422)
        self.assertEqual(self.client.post("/api/workflows/-1/execute", json={"input": []}).status_code, 422)

    def test_task_failure_is_persisted(self):
        body = {"name": "Failing task", "definition": {"StartAt": "Pago", "States": {
            "Pago": {"Type": "Task", "Resource": "task:procesar_pago", "End": True}}}}
        workflow_id = self.create(body)
        response = self.client.post(f"/api/workflows/{workflow_id}/execute", json={"input": {}})
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(result["error"], "ValueError")
        stored = self.client.get(f"/api/executions/{result['execution_id']}").json()
        self.assertEqual(stored["status"], "FAILED")
        self.assertIsNotNone(stored["finished_at"])

    def test_openapi(self):
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("/api/workflows/{id}/execute", response.json()["paths"])

    def test_inactive_workflow_cannot_execute(self):
        from app.models import Execution
        from sqlalchemy import select, func

        body = {
            "name": "Workflow inactivo",
            "description": "No debe poder ejecutarse.",
            "definition": {
                "StartAt": "Inicio",
                "States": {
                    "Inicio": {
                        "Type": "Pass",
                        "Next": "Fin"
                    },
                    "Fin": {
                        "Type": "Succeed"
                    }
                }
            },
            "is_active": False
        }

        workflow_id = self.create(body)

        workflow_response = self.client.get(
            f"/api/workflows/{workflow_id}"
        )

        self.assertEqual(
            workflow_response.status_code,
            200
        )

        self.assertFalse(
            workflow_response.json()["is_active"]
        )

        response = self.client.post(
            f"/api/workflows/{workflow_id}/execute",
            json={
                "input": {}
            }
        )

        self.assertEqual(
            response.status_code,
            409,
            response.text
        )

        self.assertIn(
            "inactivo",
            response.json()["detail"].lower()
        )

        # Ninguna ejecución debe haberse creado.
        with self.sessions() as db:
            total = db.scalar(
                select(func.count())
                .select_from(Execution)
                .where(
                    Execution.workflow_id ==
                    workflow_id
                )
            )

        self.assertEqual(
            total,
            0
        )

if __name__ == "__main__":
    unittest.main(verbosity=2)
