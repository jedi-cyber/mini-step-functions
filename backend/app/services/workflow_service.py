from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engine.engine import WorkflowEngine
from app.models import Workflow


class WorkflowNotFoundError(LookupError):
    """El workflow solicitado no existe."""


class WorkflowService:
    """Consulta definiciones y delega su ejecución al motor.

    El llamador administra la sesión y su transacción. Este servicio no
    crea registros de ejecución ni confirma cambios en la base de datos.
    """

    def __init__(self, db: Session):
        self.db = db
        self.engine = WorkflowEngine()

    def list_workflows(self, offset=0, limit=100):
        return self.db.scalars(select(Workflow).order_by(Workflow.id).offset(offset).limit(limit)).all()

    def get_workflow(self, workflow_id):
        workflow = self.db.get(Workflow, workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError(f"No existe el workflow con ID {workflow_id}.")
        return workflow

    def save_workflow(self, data, workflow_id=None):
        self.engine.validate_definition(data["definition"])
        workflow = self.get_workflow(workflow_id) if workflow_id is not None else Workflow()
        for key, value in data.items():
            setattr(workflow, key, value)
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def execute_workflow(self, workflow_id: int, input_data: dict) -> dict:
        workflow = self.db.scalar(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        if workflow is None:
            raise WorkflowNotFoundError(
                f"No existe el workflow con ID {workflow_id}."
            )
        return self.engine.execute(workflow.definition, input_data)
