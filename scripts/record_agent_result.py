"""
record_agent_result.py

Registra manual o semiautomáticamente el resultado de un agente.

Objetivo:
- Guardar salida estructurada del agente.
- Actualizar TRACE.md.
- Actualizar RUN_SUMMARY.md visible para el usuario.
- Mantener trazabilidad de pasos sin invocar modelos.

Uso:
python scripts/record_agent_result.py --run-id <run_id> --agent opencode --status diagnostic --summary "..."
"""

from __future__ import annotations

from pathlib import Path
import argparse
import datetime
import json


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "docs" / "agent_runs"
OUTBOX = ROOT / "docs" / "agent_queue" / "outbox"


def load_json_files(outputs_dir: Path) -> list[dict]:
    results = []
    if not outputs_dir.exists():
        return results

    for path in sorted(outputs_dir.glob("*.json")):
        try:
            results.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            results.append({
                "agent": path.stem,
                "status": "unreadable",
                "summary": f"No se pudo leer {path.name}",
                "timestamp": "",
            })
    return results


def write_run_summary(run_dir: Path, run_id: str) -> None:
    outputs_dir = run_dir / "agent_outputs"
    results = load_json_files(outputs_dir)

    summary_path = run_dir / "RUN_SUMMARY.md"

    lines = [
        "# RUN_SUMMARY",
        "",
        f"- run_id: `{run_id}`",
        f"- updated_at: `{datetime.datetime.now().isoformat(timespec='seconds')}`",
        f"- total_agent_outputs: `{len(results)}`",
        "",
        "## Estado general",
        "",
    ]

    if not results:
        lines.append("Sin resultados de agentes registrados todavía.")
    else:
        last_status = results[-1].get("status", "unknown")
        lines.append(f"Último estado registrado: `{last_status}`")

    lines.extend([
        "",
        "## Resultados por agente",
        "",
    ])

    for idx, item in enumerate(results, start=1):
        lines.extend([
            f"### {idx}. {item.get('agent', 'unknown')}",
            "",
            f"- timestamp: `{item.get('timestamp', '')}`",
            f"- status: `{item.get('status', 'unknown')}`",
            f"- summary: {item.get('summary', '')}",
            "",
        ])

    lines.extend([
        "## Transparencia del proceso",
        "",
        "Este resumen permite revisar qué agente intervino, qué estado reportó y cuál fue el aporte registrado.",
        "",
        "Para mayor detalle, revisar `TRACE.md` y los archivos en `agent_outputs/`.",
        "",
    ])

    summary_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--status", default="diagnostic")
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    run_dir = RUNS / args.run_id
    outputs_dir = run_dir / "agent_outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    result = {
        "run_id": args.run_id,
        "timestamp": timestamp,
        "agent": args.agent,
        "status": args.status,
        "summary": args.summary,
    }

    result_path = outputs_dir / f"{timestamp.replace(':', '-')}_{args.agent}.json"
    result_path.write_text(json.dumps(result, ensure_ascii=True, indent=2), encoding="utf-8")

    trace_path = run_dir / "TRACE.md"
    with trace_path.open("a", encoding="utf-8") as f:
        f.write(f"\n## {timestamp} — {args.agent}\n\n")
        f.write(f"- status: `{args.status}`\n")
        f.write(f"- summary: {args.summary}\n")

    write_run_summary(run_dir, args.run_id)

    print(json.dumps({
        "status": "recorded",
        "result_path": str(result_path),
        "trace_path": str(trace_path),
        "run_summary_path": str(run_dir / "RUN_SUMMARY.md"),
    }, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
