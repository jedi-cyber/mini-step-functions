-- ============================================================
-- MINI STEP FUNCTIONS
-- Base de datos para simulador inspirado en AWS Step Functions
-- PostgreSQL
-- ============================================================
--
-- RECOMENDACIÓN:
-- Ejecutar este archivo con psql:
--
--   psql -U postgres -f mini_step_functions.sql
--
-- El script crea la base de datos y luego se conecta a ella
-- mediante el comando \connect de psql.
--
-- ============================================================


-- ============================================================
-- 1. CREAR BASE DE DATOS
-- ============================================================

DROP DATABASE IF EXISTS mini_step_functions;

CREATE DATABASE mini_step_functions
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    TEMPLATE = template0;

\connect mini_step_functions;


-- ============================================================
-- 2. FUNCIÓN PARA ACTUALIZAR updated_at AUTOMÁTICAMENTE
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 3. TABLA: workflows
-- Guarda la definición de cada máquina de estados.
-- La definición del workflow se almacena como JSONB.
-- ============================================================

CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,

    name VARCHAR(150) NOT NULL,

    description TEXT,

    definition JSONB NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_workflow_definition_object
        CHECK (jsonb_typeof(definition) = 'object'),

    CONSTRAINT chk_workflow_start_at
        CHECK (definition ? 'StartAt'),

    CONSTRAINT chk_workflow_states
        CHECK (definition ? 'States')
);


-- Trigger para actualizar updated_at.
CREATE TRIGGER trg_workflows_updated_at
BEFORE UPDATE ON workflows
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- 4. TABLA: executions
-- Registra cada ejecución de un workflow.
-- ============================================================

CREATE TABLE executions (
    id SERIAL PRIMARY KEY,

    workflow_id INTEGER NOT NULL,

    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',

    input JSONB NOT NULL DEFAULT '{}'::jsonb,

    output JSONB,

    error TEXT,

    current_state VARCHAR(150),

    started_at TIMESTAMP,

    finished_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_execution_workflow
        FOREIGN KEY (workflow_id)
        REFERENCES workflows(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_execution_status
        CHECK (
            status IN (
                'PENDING',
                'RUNNING',
                'SUCCEEDED',
                'FAILED',
                'ABORTED',
                'TIMED_OUT'
            )
        ),

    CONSTRAINT chk_execution_input_json
        CHECK (
            jsonb_typeof(input) IN (
                'object',
                'array',
                'string',
                'number',
                'boolean',
                'null'
            )
        )
);


-- ============================================================
-- 5. TABLA: execution_events
-- Guarda el historial de estados visitados durante una ejecución.
-- Permite reconstruir paso a paso lo ocurrido.
-- ============================================================

CREATE TABLE execution_events (
    id BIGSERIAL PRIMARY KEY,

    execution_id INTEGER NOT NULL,

    event_order INTEGER NOT NULL,

    state_name VARCHAR(150),

    state_type VARCHAR(50),

    status VARCHAR(30) NOT NULL,

    input JSONB,

    output JSONB,

    error TEXT,

    cause TEXT,

    retry_attempt INTEGER NOT NULL DEFAULT 0,

    started_at TIMESTAMP,

    finished_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_event_execution
        FOREIGN KEY (execution_id)
        REFERENCES executions(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_event_status
        CHECK (
            status IN (
                'PENDING',
                'RUNNING',
                'SUCCEEDED',
                'FAILED',
                'RETRYING',
                'WAITING',
                'SKIPPED'
            )
        ),

    CONSTRAINT chk_retry_attempt
        CHECK (retry_attempt >= 0),

    CONSTRAINT uq_execution_event_order
        UNIQUE (execution_id, event_order)
);


-- ============================================================
-- 6. ÍNDICES
-- Mejoran las consultas más frecuentes.
-- ============================================================

CREATE INDEX idx_workflows_name
    ON workflows(name);

CREATE INDEX idx_workflows_is_active
    ON workflows(is_active);

CREATE INDEX idx_workflows_definition_gin
    ON workflows
    USING GIN(definition);

CREATE INDEX idx_executions_workflow_id
    ON executions(workflow_id);

CREATE INDEX idx_executions_status
    ON executions(status);

CREATE INDEX idx_executions_created_at
    ON executions(created_at DESC);

CREATE INDEX idx_execution_events_execution_id
    ON execution_events(execution_id);

CREATE INDEX idx_execution_events_state_name
    ON execution_events(state_name);

CREATE INDEX idx_execution_events_status
    ON execution_events(status);

CREATE INDEX idx_execution_events_order
    ON execution_events(execution_id, event_order);


-- ============================================================
-- 7. WORKFLOW DE PRUEBA
--
-- Equivalente conceptual:
--
-- Inicio (Pass)
--      |
--      v
-- ValidarPedido (Task)
--      |
--      v
-- ¿PedidoValido? (Choice)
--      |               |
--     Sí              No
--      |               |
--      v               v
-- ProcesarPago       Rechazado
--      |
--      v
-- EsperarConfirmacion
--      |
--      v
-- Completado
--
-- ============================================================

INSERT INTO workflows (
    name,
    description,
    definition
)
VALUES (
    'Procesamiento de pedido',
    'Workflow de prueba para el simulador Mini Step Functions.',
    '{
        "Comment": "Flujo de procesamiento de un pedido",
        "StartAt": "Inicio",
        "States": {
            "Inicio": {
                "Type": "Pass",
                "Next": "ValidarPedido"
            },
            "ValidarPedido": {
                "Type": "Task",
                "Resource": "task:validar_pedido",
                "Next": "PedidoValido"
            },
            "PedidoValido": {
                "Type": "Choice",
                "Choices": [
                    {
                        "Variable": "$.pedido_valido",
                        "BooleanEquals": true,
                        "Next": "ProcesarPago"
                    }
                ],
                "Default": "PedidoRechazado"
            },
            "ProcesarPago": {
                "Type": "Task",
                "Resource": "task:procesar_pago",
                "Next": "EsperarConfirmacion"
            },
            "EsperarConfirmacion": {
                "Type": "Wait",
                "Seconds": 3,
                "Next": "PedidoCompletado"
            },
            "PedidoCompletado": {
                "Type": "Succeed"
            },
            "PedidoRechazado": {
                "Type": "Fail",
                "Error": "PedidoInvalido",
                "Cause": "El pedido no pudo validarse"
            }
        }
    }'::jsonb
);


-- ============================================================
-- 8. VISTAS ÚTILES
-- ============================================================

-- Resume las ejecuciones junto con el workflow al que pertenecen.
CREATE VIEW execution_summary AS
SELECT
    e.id AS execution_id,
    e.workflow_id,
    w.name AS workflow_name,
    e.status,
    e.current_state,
    e.started_at,
    e.finished_at,
    e.created_at
FROM executions e
INNER JOIN workflows w
    ON w.id = e.workflow_id;


-- ============================================================
-- 9. CONSULTAS DE COMPROBACIÓN
-- ============================================================

-- Ver workflows:
-- SELECT * FROM workflows;

-- Ver el estado inicial:
-- SELECT definition->>'StartAt'
-- FROM workflows;

-- Ver todos los estados:
-- SELECT definition->'States'
-- FROM workflows;

-- Ver ejecuciones:
-- SELECT * FROM executions;

-- Ver historial:
-- SELECT *
-- FROM execution_events
-- ORDER BY execution_id, event_order;

-- Ver resumen:
-- SELECT * FROM execution_summary;


-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================
