from app.engine.engine import WorkflowEngine


workflow_definition = {
    "StartAt": "Inicio",
    "States": {
        "Inicio": {
            "Type": "Pass",
            "Next": "Final"
        },

        "Final": {
            "Type": "Succeed"
        }
    }
}


input_data = {
    "cliente": "Jedidias",
    "pedido_id": 1001,
    "total": 250
}


engine = WorkflowEngine()

result = engine.execute(
    workflow_definition,
    input_data
)

print()
print("Resultado final:")
print(result)