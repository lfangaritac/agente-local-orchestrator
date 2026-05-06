"""
show_latest_run.py

Muestra un resumen visible del último flujo semiautomático del orquestador.

Objetivo:
- Identificar el paquete de handoff más reciente.
- Mostrar run_id, proyecto, agente destino, riesgo, volumen, fuentes, alertas y lecciones.
- Mostrar RUN_SUMMARY.md y TRACE.md si existen.
- No modifica archivos.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import json


ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "docs" / "agent_queue" / "inbox"
RUNS = ROOT / "docs" / "agent_runs"


def latest_json() -> Path | None:
    files = sorted(INBOX.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def print_section(title: str) -> None:
    print("")
    print("=" * 80)
    print(title)
    print("=" * 80)


def print_list(title: str, values: list[str]) -> None:
    print("")
    print(title)
    if not values:
        print("- Ninguno")
        return
    for item in values:
        print(f"- {item}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    if args.run_id:
        matches = list(INBOX.glob(f"{args.run_id}.json"))
        package_path = matches[0] if matches else None
    else:
        package_path = latest_json()

    if not package_path:
        print("No se encontraron paquetes de handoff en docs/agent_queue/inbox.")
        return

    package = load_json(package_path)
    run_id = package.get("run_id", package_path.stem)
    run_dir = RUNS / run_id

    print_section("ULTIMO FLUJO / PAQUETE DE HANDOFF")
    print(f"run_id: {run_id}")
    print(f"package: {package_path.relative_to(ROOT)}")
    print(f"project_id: {package.get('project_id', '')}")
    print(f"source_agent: {package.get('source_agent', '')}")
    print(f"target_agent: {package.get('target_agent', '')}")
    print(f"scenario: {package.get('scenario', '')}")
    print(f"risk_level: {package.get('risk_level', '')}")
    print(f"information_volume: {package.get('information_volume', '')}")
    print(f"preflight_status: {package.get('preflight_status', '')}")
    print(f"status: {package.get('status', '')}")

    print_section("OBJETIVO")
    print(package.get("objective", ""))

    print_section("CONTEXTO, ALERTAS Y LECCIONES")
    print(f"context_sources_count: {len(package.get('context_sources', []))}")
    print(f"alerts_checked_count: {len(package.get('alerts_checked', []))}")
    print(f"lessons_checked_count: {len(package.get('lessons_checked', []))}")

    print_list("Fuentes de contexto", package.get("context_sources", []))
    print_list("Alertas consultadas", package.get("alerts_checked", []))
    print_list("Lecciones consultadas", package.get("lessons_checked", []))
    print_list("Fuentes faltantes", package.get("missing_files", []))

    summary_path = run_dir / "RUN_SUMMARY.md"
    trace_path = run_dir / "TRACE.md"

    print_section("RUN_SUMMARY.md")
    if summary_path.exists():
        print(summary_path.read_text(encoding="utf-8"))
    else:
        print("No existe RUN_SUMMARY.md para este run.")

    print_section("TRACE.md")
    if trace_path.exists():
        print(trace_path.read_text(encoding="utf-8"))
    else:
        print("No existe TRACE.md para este run.")

    print_section("RUTAS")
    print(f"run_dir: {run_dir}")
    print(f"summary: {summary_path}")
    print(f"trace: {trace_path}")


if __name__ == "__main__":
    main()
