from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engine.engine import WorkflowEngine
from app.models import Workflow


class WorkflowNotFoundError(LookupError):
    """El workflow solicitado no existe."""


class WorkflowInactiveError(RuntimeError):
    """El workflow existe, pero está marcado como inactivo."""

    def __init__(self, workflow_id: int):
        self.workflow_id = workflow_id

        super().__init__(
            f"El workflow con ID {workflow_id} está inactivo "
            "y no puede ejecutarse."
        )


class WorkflowService:
    """Consulta y administra definiciones de workflows.

    El llamador administra la sesión y su transacción.

    Este servicio permite:
    - listar workflows;
    - consultar un workflow;
    - crear o actualizar workflows;
    - ejecutar directamente un workflow cuando está activo.
    """

    def __init__(self, db: Session):
        self.db = db
        self.engine = WorkflowEngine()


    # =========================================================
    # LISTAR
    # =========================================================

    def list_workflows(
        self,
        offset=0,
        limit=100
    ):
        return self.db.scalars(
            select(Workflow)
            .order_by(Workflow.id)
            .offset(offset)
            .limit(limit)
        ).all()


    # =========================================================
    # OBTENER
    # =========================================================

    def get_workflow(
        self,
        workflow_id
    ):
        workflow = self.db.get(
            Workflow,
            workflow_id
        )

        if workflow is None:
            raise WorkflowNotFoundError(
                f"No existe el workflow con ID {workflow_id}."
            )

        return workflow


    # =========================================================
    # GUARDAR
    # =========================================================

    def save_workflow(
        self,
        data,
        workflow_id=None
    ):
        # La definición se valida antes de escribir
        # cualquier cambio en PostgreSQL.
        self.engine.validate_definition(
            data["definition"]
        )

        if workflow_id is not None:
            workflow = self.get_workflow(
                workflow_id
            )
        else:
            workflow = Workflow()


        for key, value in data.items():
            setattr(
                workflow,
                key,
                value
            )


        self.db.add(
            workflow
        )

        self.db.commit()

        self.db.refresh(
            workflow
        )

        return workflow


    # =========================================================
    # EJECUTAR DIRECTAMENTE
    # =========================================================

    def execute_workflow(
        self,
        workflow_id: int,
        input_data: dict
    ) -> dict:

        workflow = self.db.scalar(
            select(Workflow).where(
                Workflow.id ==
                workflow_id
            )
        )


        if workflow is None:
            raise WorkflowNotFoundError(
                f"No existe el workflow con ID {workflow_id}."
            )


        # =====================================================
        # IMPEDIR EJECUCIÓN DE WORKFLOW INACTIVO
        # =====================================================

        if not workflow.is_active:
            raise WorkflowInactiveError(
                workflow_id
            )


        return self.engine.execute(
            workflow.definition,
            input_data
        )