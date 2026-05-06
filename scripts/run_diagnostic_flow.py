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
- Opcionalmente invocar OpenCode real desde el handoff generado.

Modo base:
- No invoca modelos.
- No ejecuta agentes reales.
- No modifica código funcional.
- Opera como prueba semiautomática de coordinación y trazabilidad.

Modo con --with-opencode:
- Invoca OpenCode real mediante scripts/run_opencode_from_handoff.py.
- Mantiene prompt diagnóstico.
- No solicita edición de archivos ni ejecución de comandos.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import datetime
import json
import subprocess
import sys
import os

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def safe_print(value: object = "") -> None:
    text = str(value)
    try:
        print(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))


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


def run_or_exit(command: list[str], label: str) -> tuple[dict | None, str]:
    code, stdout, stderr = run_command(command)

    if stdout:
        safe_print(stdout)

    if stderr:
        safe_print(stderr)

    if code != 0:
        safe_print(f"ERROR: {label} falló con código {code}")
        sys.exit(code)

    parsed = None
    try:
        parsed = parse_json_output(stdout)
    except Exception:
        parsed = None

    return parsed, stdout


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
            "sin modificar documentación funcional."
        ),
        help="Objetivo del flujo diagnóstico.",
    )
    parser.add_argument(
        "--with-opencode",
        action="store_true",
        help="Invoca OpenCode real desde el handoff generado, en modo diagnóstico controlado.",
    )
    args = parser.parse_args()

    print_section("1. PREFLIGHT")
    preflight, _ = run_or_exit(
        [sys.executable, "scripts/orchestrator_preflight.py"],
        "orchestrator_preflight.py",
    )

    if preflight is None:
        safe_print("ERROR: No se pudo parsear JSON de preflight.")
        sys.exit(1)

    print_section("2. SELECCIÓN DE AGENTE / MODELO")
    selector, _ = run_or_exit(
        [
            sys.executable,
            "scripts/select_agent_model.py",
            "--scenario",
            args.scenario,
            "--risk",
            args.risk,
            "--volume",
            args.volume,
        ],
        "select_agent_model.py",
    )

    if selector is None:
        safe_print("ERROR: No se pudo parsear JSON de select_agent_model.py.")
        sys.exit(1)

    target_agent = selector.get("recommended_agent", "context-validator")

    print_section("3. CREACIÓN DE PAQUETE DE HANDOFF")
    build, _ = run_or_exit(
        [
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
        ],
        "build_handoff_package.py",
    )

    if build is None:
        safe_print("ERROR: No se pudo parsear JSON de build_handoff_package.py.")
        sys.exit(1)

    run_id = build["run_id"]

    print_section("4. REGISTRO DE RESULTADO DIAGNÓSTICO INICIAL")
    summary = (
        "Flujo diagnóstico semiautomático ejecutado: preflight ok, "
        f"{len(preflight.get('context_sources', []))} fuentes, "
        f"{len(preflight.get('alerts_checked', []))} alertas, "
        f"{len(preflight.get('lessons_checked', []))} lecciones; "
        f"agente recomendado {selector.get('recommended_agent')} con modelo {selector.get('recommended_model')}."
    )

    run_or_exit(
        [
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
        ],
        "record_agent_result.py",
    )

    if args.with_opencode:
        print_section("5. INVOCACIÓN REAL CONTROLADA DE OPENCODE")
        run_or_exit(
            [
                sys.executable,
                "scripts/run_opencode_from_handoff.py",
                "--run-id",
                run_id,
                "--agent",
                selector.get("recommended_agent", "context-validator"),
                "--model",
                selector.get("recommended_model", "opencode-go/qwen3.6-plus"),
            ],
            "run_opencode_from_handoff.py",
        )
    else:
        print_section("5. OPENCODE OMITIDO")
        safe_print("OpenCode no fue invocado porque no se usó --with-opencode.")

    print_section("6. VISUALIZACIÓN DEL FLUJO")
    run_or_exit(
        [
            sys.executable,
            "scripts/show_latest_run.py",
            "--run-id",
            run_id,
        ],
        "show_latest_run.py",
    )

    print_section("7. RESULTADO")
    result = {
        "status": "ok",
        "run_id": run_id,
        "project_id": args.project_id,
        "scenario": args.scenario,
        "risk": args.risk,
        "volume": args.volume,
        "recommended_agent": selector.get("recommended_agent"),
        "recommended_model": selector.get("recommended_model"),
        "with_opencode": args.with_opencode,
        "context_sources_count": len(preflight.get("context_sources", [])),
        "alerts_checked_count": len(preflight.get("alerts_checked", [])),
        "lessons_checked_count": len(preflight.get("lessons_checked", [])),
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    safe_print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()

