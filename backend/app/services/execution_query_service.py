from sqlalchemy import select
from app.models import Execution, ExecutionEvent


class ExecutionNotFoundError(LookupError):
    pass


class ExecutionQueryService:
    def __init__(self, db):
        self.db = db

    def list_executions(self, offset=0, limit=100):
        return self.db.scalars(select(Execution).order_by(Execution.id.desc()).offset(offset).limit(limit)).all()

    def get_execution(self, execution_id):
        execution = self.db.get(Execution, execution_id)
        if execution is None:
            raise ExecutionNotFoundError(f"No existe la ejecución {execution_id}.")
        return execution

    def events(self, execution_id, offset=0, limit=100):
        self.get_execution(execution_id)
        return self.db.scalars(select(ExecutionEvent).where(
            ExecutionEvent.execution_id == execution_id
        ).order_by(ExecutionEvent.event_order).offset(offset).limit(limit)).all()
