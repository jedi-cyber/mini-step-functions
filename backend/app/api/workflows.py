from fastapi import APIRouter, Depends, Query
from app.api.dependencies import workflow_service, execution_service
from app.schemas.workflow import WorkflowWrite, WorkflowRead
from app.schemas.execution import ExecuteRequest, ExecuteResult


router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.get("", response_model=list[WorkflowRead])
def list_workflows(offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), service=Depends(workflow_service)):
    return service.list_workflows(offset, limit)


@router.get("/{id}", response_model=WorkflowRead)
def get_workflow(id: int, service=Depends(workflow_service)):
    return service.get_workflow(id)


@router.post("", response_model=WorkflowRead, status_code=201)
def create_workflow(body: WorkflowWrite, service=Depends(workflow_service)):
    return service.save_workflow(body.model_dump())


@router.put("/{id}", response_model=WorkflowRead)
def update_workflow(id: int, body: WorkflowWrite, service=Depends(workflow_service)):
    return service.save_workflow(body.model_dump(), id)


@router.post("/{id}/execute", response_model=ExecuteResult)
def execute_workflow(id: int, body: ExecuteRequest, service=Depends(execution_service)):
    # FastAPI ejecuta endpoints síncronos en su pool de hilos.
    return service.execute_for_api(id, body.input)
