from sqlalchemy import select

from app.database.connection import SessionLocal
from app.models.workflow import Workflow


def main():
    db = SessionLocal()

    try:
        stmt = select(Workflow).order_by(Workflow.id)

        workflows = db.scalars(stmt).all()

        if not workflows:
            print("No hay workflows registrados en la base de datos.")
            return

        print(f"Workflows encontrados: {len(workflows)}")
        print("-" * 50)

        for workflow in workflows:
            print(f"ID: {workflow.id}")
            print(f"Nombre: {workflow.name}")
            print(f"Descripción: {workflow.description}")
            print(f"Activo: {workflow.is_active}")
            print(f"Estado inicial: {workflow.definition.get('StartAt')}")

            states = workflow.definition.get("States", {})

            print("Estados:")

            for state_name, state_data in states.items():
                state_type = state_data.get("Type")
                print(f"  - {state_name}: {state_type}")

            print("-" * 50)

    except Exception as e:
        print("Ocurrió un error al consultar PostgreSQL:")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    main()