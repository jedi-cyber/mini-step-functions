"""Ejecuta la demo en memoria, sin insertar ni modificar datos PostgreSQL."""
import argparse
import json
from pathlib import Path
from app.engine.engine import WorkflowEngine


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("escenario", choices=["exitoso", "invalido", "recuperable", "definitivo"])
    args = parser.parse_args()
    examples = Path(__file__).resolve().parents[1] / "examples"
    definition = json.loads((examples / "pedido.json").read_text(encoding="utf-8"))
    data = json.loads((examples / "inputs" / f"pedido-{args.escenario}.json").read_text(encoding="utf-8"))
    print(json.dumps(WorkflowEngine().execute(definition, data), indent=2, ensure_ascii=False))
