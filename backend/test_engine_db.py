from sqlalchemy import select

from app.database.connection import SessionLocal
from app.services.workflow_service import WorkflowService
from app.models.workflow import Workflow


def main():
    db = SessionLocal()

    try:
        # Buscar el primer workflow activo
        stmt = (
            select(Workflow)
            .where(Workflow.is_active.is_(True))
            .order_by(Workflow.id)
        )

        workflow = db.scalar(stmt)

        if workflow is None:
            print("No se encontró ningún workflow activo.")
            return

        print("Workflow encontrado:")
        print(f"ID: {workflow.id}")
        print(f"Nombre: {workflow.name}")
        print(f"Estado inicial: {workflow.definition.get('StartAt')}")
        print()

        input_data = {
            "cliente": "Jedidias",
            "pedido_id": 1001,
            "total": 250
        }

        service = WorkflowService(db)

        result = service.execute_workflow(
            workflow.id,
            input_data
        )

        print()
        print("Resultado final:")
        print(result)

    except Exception as e:
        print("Ocurrió un error:")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    main()
