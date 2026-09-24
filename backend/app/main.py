from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.api.workflows import router as workflows_router
from app.api.executions import router as executions_router
from app.services.workflow_service import WorkflowNotFoundError
from app.services.execution_query_service import ExecutionNotFoundError
from app.services.execution_service import InvalidWorkflowError


app = FastAPI(title="Mini Step Functions", version="0.1.0")
app.include_router(workflows_router)
app.include_router(executions_router)


@app.exception_handler(WorkflowNotFoundError)
@app.exception_handler(ExecutionNotFoundError)
async def not_found(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc):
    errors = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
    status = 400 if any(e["type"] == "json_invalid" for e in errors) else 422
    return JSONResponse(status_code=status, content={"detail": errors})


@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, exc):
    return JSONResponse(status_code=503, content={"detail": "No se pudo completar la operación de base de datos."})


@app.exception_handler(InvalidWorkflowError)
async def invalid_workflow(request: Request, exc):
    return JSONResponse(status_code=422, content={"detail": exc.errors})
