from fastapi import APIRouter, Depends, Query
from app.api.dependencies import execution_queries
from app.schemas.execution import ExecutionRead, EventRead


router = APIRouter(prefix="/api/executions", tags=["executions"])


@router.get("", response_model=list[ExecutionRead])
def list_executions(offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), service=Depends(execution_queries)):
    return service.list_executions(offset, limit)


@router.get("/{id}", response_model=ExecutionRead)
def get_execution(id: int, service=Depends(execution_queries)):
    return service.get_execution(id)


@router.get("/{id}/events", response_model=list[EventRead])
def get_events(id: int, offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), service=Depends(execution_queries)):
    return service.events(id, offset, limit)
