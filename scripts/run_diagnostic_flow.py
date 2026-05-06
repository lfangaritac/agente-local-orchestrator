"""
run_diagnostic_flow.py

Ejecuta una mini-orquestación semiautomática diagnóstica de punta a punta.

Objetivo:
- Ejecutar preflight transversal.
- Seleccionar agente/modelo.
- Crear paquete de handoff con fuentes, alertas y lecciones.
- Registrar un resultado diagnóstico inicial.
- Generar RUN_SUMMARY.md y TRACE.md.
- Mostrar el último flujo al usuario.

Este script no invoca modelos, no modifica código funcional y no ejecuta acciones de agentes reales.
Opera como prueba semiautomática de coordinación y trazabilidad.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import datetime
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str]) -> tuple[int, str, str]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.returncode, completed.stdout, completed.stderr


def parse_json_output(output: str) -> dict:
    return json.loads(output)


def print_section(title: str) -> None:
    print("")
    print("=" * 80)
    print(title)
    print("=" * 80)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-id",
        default="orchestrator",
        help="Identificador del proyecto objetivo. Por defecto: orchestrator.",
    )
    parser.add_argument(
        "--scenario",
        default="context-validation",
        help="Escenario de routing. Por defecto: context-validation.",
    )
    parser.add_argument(
        "--risk",
        default="medium",
        help="Nivel de riesgo. Por defecto: medium.",
    )
    parser.add_argument(
        "--volume",
        default="high",
        help="Volumen de información. Por defecto: high.",
    )
    parser.add_argument(
        "--objective",
        default=(
            "Flujo diagnóstico semiautomático: ejecutar preflight, seleccionar agente/modelo, "
            "crear paquete de handoff, registrar resultado inicial y mostrar trazabilidad visible "
            "sin invocar modelos ni modificar documentación funcional."
        ),
        help="Objetivo del flujo diagnóstico.",
    )
    args = parser.parse_args()

    print_section("1. PREFLIGHT")
    preflight_code, preflight_out, preflight_err = run_command([
        sys.executable,
        "scripts/orchestrator_preflight.py",
    ])

    if preflight_out:
        print(preflight_out)
    if preflight_err:
        print(preflight_err)

    if preflight_code != 0:
        print(f"ERROR: orchestrator_preflight.py falló con código {preflight_code}")
        sys.exit(preflight_code)

    preflight = parse_json_output(preflight_out)

    print_section("2. SELECCIÓN DE AGENTE / MODELO")
    selector_code, selector_out, selector_err = run_command([
        sys.executable,
        "scripts/select_agent_model.py",
        "--scenario",
        args.scenario,
        "--risk",
        args.risk,
        "--volume",
        args.volume,
    ])

    if selector_out:
        print(selector_out)
    if selector_err:
        print(selector_err)

    if selector_code != 0:
        print(f"ERROR: select_agent_model.py falló con código {selector_code}")
        sys.exit(selector_code)

    selector = parse_json_output(selector_out)

    target_agent = selector.get("recommended_agent", "context-validator")

    print_section("3. CREACIÓN DE PAQUETE DE HANDOFF")
    build_code, build_out, build_err = run_command([
        sys.executable,
        "scripts/build_handoff_package.py",
        "--project-id",
        args.project_id,
        "--source-agent",
        "user",
        "--target-agent",
        target_agent,
        "--scenario",
        args.scenario,
        "--risk",
        args.risk,
        "--volume",
        args.volume,
        "--objective",
        args.objective,
    ])

    if build_out:
        print(build_out)
    if build_err:
        print(build_err)

    if build_code != 0:
        print(f"ERROR: build_handoff_package.py falló con código {build_code}")
        sys.exit(build_code)

    build = parse_json_output(build_out)
    run_id = build["run_id"]

    print_section("4. REGISTRO DE RESULTADO DIAGNÓSTICO")
    summary = (
        "Flujo diagnóstico semiautomático ejecutado: preflight ok, "
        f"{len(preflight.get('context_sources', []))} fuentes, "
        f"{len(preflight.get('alerts_checked', []))} alertas, "
        f"{len(preflight.get('lessons_checked', []))} lecciones; "
        f"agente recomendado {selector.get('recommended_agent')} con modelo {selector.get('recommended_model')}."
    )

    record_code, record_out, record_err = run_command([
        sys.executable,
        "scripts/record_agent_result.py",
        "--run-id",
        run_id,
        "--agent",
        "orchestrator-diagnostic-flow",
        "--status",
        "diagnostic",
        "--summary",
        summary,
    ])

    if record_out:
        print(record_out)
    if record_err:
        print(record_err)

    if record_code != 0:
        print(f"ERROR: record_agent_result.py falló con código {record_code}")
        sys.exit(record_code)

    print_section("5. VISUALIZACIÓN DEL FLUJO")
    show_code, show_out, show_err = run_command([
        sys.executable,
        "scripts/show_latest_run.py",
        "--run-id",
        run_id,
    ])

    if show_out:
        print(show_out)
    if show_err:
        print(show_err)

    if show_code != 0:
        print(f"ERROR: show_latest_run.py falló con código {show_code}")
        sys.exit(show_code)

    print_section("6. RESULTADO")
    result = {
        "status": "ok",
        "run_id": run_id,
        "project_id": args.project_id,
        "scenario": args.scenario,
        "risk": args.risk,
        "volume": args.volume,
        "recommended_agent": selector.get("recommended_agent"),
        "recommended_model": selector.get("recommended_model"),
        "context_sources_count": len(preflight.get("context_sources", [])),
        "alerts_checked_count": len(preflight.get("alerts_checked", [])),
        "lessons_checked_count": len(preflight.get("lessons_checked", [])),
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
