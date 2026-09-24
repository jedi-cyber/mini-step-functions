from fastapi import Depends
from app.database.connection import get_db
from app.services.workflow_service import WorkflowService
from app.services.execution_service import ExecutionService
from app.services.execution_query_service import ExecutionQueryService


def workflow_service(db=Depends(get_db)):
    return WorkflowService(db)


def execution_queries(db=Depends(get_db)):
    return ExecutionQueryService(db)


def execution_service():
    return ExecutionService()
