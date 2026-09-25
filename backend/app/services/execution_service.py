"""Persistencia de ejecuciones.

Cada transición del workflow se confirma por separado
para mantener disponible el historial de ejecución.
"""

import asyncio

from copy import deepcopy
from datetime import datetime, timezone

from app.database.connection import SessionLocal

from app.engine.engine import WorkflowEngine

from app.models import (
    Execution,
    ExecutionEvent,
    Workflow
)

from app.services.workflow_service import (
    WorkflowNotFoundError,
    WorkflowInactiveError
)

from app.engine.validator import (
    require_valid_workflow,
    WorkflowValidationError
)


InvalidWorkflowError = WorkflowValidationError


# =============================================================
# FECHA UTC
# =============================================================

def utcnow():
    """Devuelve UTC sin tzinfo.

    Las columnas existentes utilizan TIMESTAMP sin zona
    horaria, por lo que guardamos todos los valores en UTC.
    """

    return (
        datetime
        .now(timezone.utc)
        .replace(tzinfo=None)
    )


# =============================================================
# REGISTRADOR DE EVENTOS
# =============================================================

class ExecutionRecorder:

    def __init__(
        self,
        db,
        execution
    ):
        self.db = db

        self.execution = execution

        self.event = None

        self.counter = [0]

        self.output = deepcopy(
                execution.input
            )


    # =========================================================
    # ESTADO INICIADO
    # =========================================================

    def state_started(
        self,
        name,
        state_type,
        data,
        retry_attempt=0
    ):

        self.counter[0] += 1


        self.execution.current_state = name


        self.event = ExecutionEvent(

                execution_id=
                    self.execution.id,

                event_order=
                    self.counter[0],

                state_name=
                    name,

                state_type=
                    state_type,

                status=
                    "RUNNING",

                input=
                    deepcopy(data),

                started_at=
                    utcnow(),

                retry_attempt=
                    retry_attempt
            )


        self.db.add(
            self.event
        )

        self.db.commit()


    # =========================================================
    # ESTADO FINALIZADO
    # =========================================================

    def state_finished(
        self,
        data,
        status,
        error,
        cause
    ):

        self.execution.current_state = self.event.state_name


        self.output = deepcopy(data)


        self.event.status = status


        self.event.output =  deepcopy(data)


        self.event.error =  error


        self.event.cause =  cause


        self.event.finished_at = utcnow()


        self.db.commit()


        self.event = None


    # =========================================================
    # RAMA PARALLEL
    # =========================================================

    def fork(self):

        child = ExecutionRecorder(
                self.db,
                self.execution
            )


        child.counter = self.counter


        return child


# =============================================================
# SERVICIO DE EJECUCIONES
# =============================================================

class ExecutionService:
    """Ejecuta workflows y persiste su historial.

    Usa una sesión propia.

    execute_workflow devuelve:
    - resultado del motor;
    - execution_id.

    Las excepciones del motor se almacenan antes
    de ser propagadas o devueltas a la API.
    """


    def __init__(
        self,
        session_factory=SessionLocal
    ):

        self.session_factory = session_factory


    # =========================================================
    # ENTRADA UTILIZADA POR FASTAPI
    # =========================================================

    def execute_for_api(
        self,
        workflow_id,
        input_data
    ):

        return self.execute_workflow(
            workflow_id,
            input_data,
            raise_errors=False
        )


    # =========================================================
    # ENTRADA ASÍNCRONA
    # =========================================================

    async def execute_workflow_async(
        self,
        workflow_id: int,
        input_data: dict
    ):

        return await asyncio.to_thread(
            self.execute_workflow,
            workflow_id,
            input_data
        )


    # =========================================================
    # EJECUTAR WORKFLOW
    # =========================================================

    def execute_workflow(
        self,
        workflow_id: int,
        input_data: dict,
        *,
        raise_errors=True
    ) -> dict:

        # -----------------------------------------------------
        # Evitar ejecución síncrona dentro de un event loop
        # -----------------------------------------------------

        try:
            asyncio.get_running_loop()

        except RuntimeError:
            pass

        else:
            raise RuntimeError(
                "Usa await service.execute_workflow_async(...) "
                "dentro de un event loop."
            )


        # -----------------------------------------------------
        # Validar input
        # -----------------------------------------------------

        if not isinstance(
            input_data,
            dict
        ):

            raise ValueError(
                "input_data debe ser un diccionario."
            )


        # -----------------------------------------------------
        # Crear sesión
        # -----------------------------------------------------

        with self.session_factory() as db:

            workflow = db.get(
                    Workflow,
                    workflow_id
                )


            # =================================================
            # WORKFLOW NO EXISTE
            # =================================================

            if workflow is None:

                raise WorkflowNotFoundError(
                    f"No existe el workflow con ID {workflow_id}."
                )


            # =================================================
            # WORKFLOW INACTIVO
            #
            # IMPORTANTE:
            # esta comprobación ocurre ANTES de crear Execution.
            # =================================================

            if not workflow.is_active:

                raise WorkflowInactiveError(
                    workflow_id
                )


            # =================================================
            # COPIAR DEFINICIÓN
            # =================================================

            definition = deepcopy(
                    workflow.definition
                )


            # =================================================
            # VALIDAR DEFINICIÓN
            #
            # También ocurre antes de crear Execution.
            # =================================================

            require_valid_workflow(
                definition
            )


            start = (
                    definition.get(
                        "StartAt"
                    )

                    if isinstance(
                        definition,
                        dict
                    )

                    else None
                )


            # =================================================
            # CREAR EJECUCIÓN
            # =================================================

            execution = Execution(

                    workflow_id=
                        workflow_id,

                    status=
                        "RUNNING",

                    input=
                        deepcopy(
                            input_data
                        ),

                    current_state=
                        (
                            start

                            if isinstance(
                                start,
                                str
                            )

                            else None
                        ),

                    started_at=
                        utcnow()
                )


            db.add(
                execution
            )


            db.commit()


            execution_id = execution.id


            recorder = ExecutionRecorder(
                    db,
                    execution
                )


            # =================================================
            # EJECUTAR MOTOR
            # =================================================

            try:

                result = WorkflowEngine(
                        observer=recorder
                    ).execute(

                        definition,

                        deepcopy(
                            input_data
                        )
                    )


            # =================================================
            # ERROR DURANTE EJECUCIÓN
            # =================================================

            except Exception as exc:

                db.rollback()


                if (
                    recorder.event
                    is not None
                ):

                    recorder.state_finished(

                        None,

                        "FAILED",

                        type(exc).__name__,

                        str(exc)
                    )


                execution.status = "FAILED"


                execution.error = (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    )


                execution.output = None


                execution.finished_at = utcnow()


                db.commit()


                if not raise_errors:

                    return {

                        "execution_id":
                            execution_id,

                        "status":
                            "FAILED",

                        "error":
                            type(exc).__name__,

                        "cause":
                            str(exc),

                        "output":
                            None,

                        "last_state":
                            execution.current_state
                    }


                raise


            # =================================================
            # EJECUCIÓN FINALIZADA
            # =================================================

            execution.status = result["status"]


            execution.output = deepcopy(
                    recorder.output
                )


            execution.error = result.get(
                    "error"
                )


            execution.finished_at = utcnow()


            db.commit()


            return {

                **result,

                "execution_id":
                    execution_id
            }