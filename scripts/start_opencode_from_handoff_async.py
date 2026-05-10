"""
start_opencode_from_handoff_async.py

Lanza OpenCode desde un handoff existente en segundo plano.

Objetivo:
- Evitar que Continue/MCP espere toda la ejecución de OpenCode.
- Devolver inmediatamente run_id, status y ruta de logs.
- Permitir que Continue consulte luego show_latest_run.

Este script no ejecuta comandos arbitrarios. Solo invoca:
python scripts/run_opencode_from_handoff.py --run-id <run_id>
"""

from __future__ import annotations

from pathlib import Path
import argparse
import datetime
import json
import os
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "docs" / "agent_runs"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--agent", default="context-validator")
    parser.add_argument("--model", default="opencode-go/qwen3.6-plus")
    parser.add_argument(
        "--auto-approve-permissions",
        action="store_true",
        help="Si se indica, pasa el flag de auto-aprobación de permisos a run_opencode_from_handoff (requiere guardrails en el paquete).",
    )
    parser.add_argument(
        "--prompt",
        default=(
            "Lee el archivo de handoff adjunto. Actúa en modo diagnóstico. "
            "No modifiques archivos. No ejecutes comandos. "
            "Responde con un JSON corto con estas claves: status, agent, model, file_read, summary, next_action."
        ),
    )
    args = parser.parse_args()

    run_dir = RUNS / args.run_id
    if not run_dir.exists():
        print(json.dumps({
            "ok": False,
            "status": "error",
            "run_id": args.run_id,
            "error": "run_id no existe en docs/agent_runs.",
        }, ensure_ascii=True, indent=2))
        sys.exit(1)

    background_dir = run_dir / "background"
    background_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().isoformat(timespec="seconds").replace(":", "-")
    stdout_path = background_dir / f"{timestamp}_opencode_async_stdout.log"
    stderr_path = background_dir / f"{timestamp}_opencode_async_stderr.log"
    meta_path = background_dir / f"{timestamp}_opencode_async_meta.json"

    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")

    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_opencode_from_handoff.py"),
        "--run-id",
        args.run_id,
        "--agent",
        args.agent,
        "--model",
        args.model,
        "--prompt",
        args.prompt,
    ]

    if args.auto_approve_permissions:
        command.append("--auto-approve-permissions")

    stdout_file = stdout_path.open("w", encoding="utf-8", errors="replace")
    stderr_file = stderr_path.open("w", encoding="utf-8", errors="replace")

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

    proc = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=stdout_file,
        stderr=stderr_file,
        stdin=subprocess.DEVNULL,
        env=env,
        text=True,
        creationflags=creationflags,
    )

    meta = {
        "ok": True,
        "auto_approve_permissions": bool(args.auto_approve_permissions),
        "status": "started",
        "run_id": args.run_id,
        "pid": proc.pid,
        "agent": args.agent,
        "model": args.model,
        "command": command,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "meta_path": str(meta_path),
        "started_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "next_action": "Consultar run_health_check/check_opencode_run_status luego de unos segundos para verificar si OpenCode registró resultado.",
    }

    meta_path.write_text(json.dumps(meta, ensure_ascii=True, indent=2), encoding="utf-8")

    print(json.dumps(meta, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
