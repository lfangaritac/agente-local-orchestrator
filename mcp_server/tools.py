"""
tools.py

Herramientas seguras del MCP local para Continue.

Estas herramientas envuelven scripts ya probados del orquestador.
No permiten comandos arbitrarios.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


ALLOWED_TOOLS = {
    "orchestrator_preflight",
    "select_agent_model",
    "build_handoff_package",
    "run_diagnostic_flow",
    "show_latest_run",
    "run_opencode_from_handoff",
    "start_opencode_from_handoff_async",
    "get_run_status",
    "check_opencode_run_status",
    "run_health_check",
    "verify_master_files",
    "create_and_dispatch_opencode_handoff",
}


def _run_python_script(args: list[str], timeout: int = 180, max_output_chars: int = 24576) -> dict[str, Any]:
    import time as _time
    start = _time.perf_counter()
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    elapsed_ms = int((_time.perf_counter() - start) * 1000)

    def _truncate(text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        return text[:limit] + f"\n... [truncated: {len(text)} chars total]"

    stdout_raw = completed.stdout or ""
    stderr_raw = completed.stderr or ""

    return {
        "returncode": completed.returncode,
        "stdout": _truncate(stdout_raw, max_output_chars),
        "stderr": _truncate(stderr_raw, max_output_chars),
        "stdout_bytes": len(stdout_raw.encode("utf-8", errors="replace")),
        "stderr_bytes": len(stderr_raw.encode("utf-8", errors="replace")),
        "stdout_truncated": len(stdout_raw) > max_output_chars,
        "stderr_truncated": len(stderr_raw) > max_output_chars,
        "elapsed_ms": elapsed_ms,
        "ok": completed.returncode == 0,
    }


def _json_or_text(output: str) -> Any:
    output = output.strip()
    if not output:
        return ""
    try:
        return json.loads(output)
    except Exception:
        return output


def orchestrator_preflight(_: dict[str, Any] | None = None) -> dict[str, Any]:
    result = _run_python_script(["scripts/orchestrator_preflight.py"])
    return {
        **result,
        "parsed": _json_or_text(result.get("stdout", "")),
    }


def select_agent_model(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    arguments = arguments or {}

    command = [
        "scripts/select_agent_model.py",
        "--scenario",
        str(arguments.get("scenario", "context-validation")),
        "--risk",
        str(arguments.get("risk", "medium")),
        "--volume",
        str(arguments.get("volume", "medium")),
    ]

    if arguments.get("user_premium") is True:
        command.append("--user-premium")

    result = _run_python_script(command)
    return {
        **result,
        "parsed": _json_or_text(result.get("stdout", "")),
    }


def build_handoff_package(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    arguments = arguments or {}

    objective = arguments.get("objective")
    if not objective:
        return {
            "ok": False,
            "returncode": 2,
            "stdout": "",
            "stderr": "objective es obligatorio.",
        }

    command = [
        "scripts/build_handoff_package.py",
        "--project-id",
        str(arguments.get("project_id", "orchestrator")),
        "--source-agent",
        str(arguments.get("source_agent", "continue")),
        "--target-agent",
        str(arguments.get("target_agent", "context-validator")),
        "--scenario",
        str(arguments.get("scenario", "context-validation")),
        "--risk",
        str(arguments.get("risk", "medium")),
        "--volume",
        str(arguments.get("volume", "high")),
        "--objective",
        str(objective),
    ]

    result = _run_python_script(command)
    return {
        **result,
        "parsed": _json_or_text(result.get("stdout", "")),
    }


def run_diagnostic_flow(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    arguments = arguments or {}

    command = [
        "scripts/run_diagnostic_flow.py",
        "--project-id",
        str(arguments.get("project_id", "orchestrator")),
        "--scenario",
        str(arguments.get("scenario", "context-validation")),
        "--risk",
        str(arguments.get("risk", "medium")),
        "--volume",
        str(arguments.get("volume", "high")),
        "--objective",
        str(arguments.get("objective", "Flujo diagnóstico MCP v0.1.")),
    ]

    if arguments.get("with_opencode") is True:
        command.append("--with-opencode")

    result = _run_python_script(command, timeout=300)
    return {
        **result,
        "parsed": _json_or_text(result.get("stdout", "")),
    }


def show_latest_run(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    arguments = arguments or {}

    command = ["scripts/show_latest_run.py"]
    run_id = arguments.get("run_id")
    if run_id:
        command.extend(["--run-id", str(run_id)])

    return _run_python_script(command)


def run_opencode_from_handoff(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    arguments = arguments or {}

    run_id = arguments.get("run_id")
    if not run_id:
        return {
            "ok": False,
            "returncode": 2,
            "stdout": "",
            "stderr": "run_id es obligatorio.",
        }

    command = [
        "scripts/run_opencode_from_handoff.py",
        "--run-id",
        str(run_id),
        "--agent",
        str(arguments.get("agent", "context-validator")),
        "--model",
        str(arguments.get("model", "opencode-go/qwen3.6-plus")),
    ]

    prompt = arguments.get("prompt")
    if prompt:
        command.extend(["--prompt", str(prompt)])

    return _run_python_script(command, timeout=300)


def start_opencode_from_handoff_async(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    arguments = arguments or {}

    run_id = arguments.get("run_id")
    if not run_id:
        return {
            "ok": False,
            "returncode": 2,
            "stdout": "",
            "stderr": "run_id es obligatorio.",
        }

    command = [
        "scripts/start_opencode_from_handoff_async.py",
        "--run-id",
        str(run_id),
        "--agent",
        str(arguments.get("agent", "context-validator")),
        "--model",
        str(arguments.get("model", "opencode-go/qwen3.6-plus")),
    ]

    prompt = arguments.get("prompt")
    if prompt:
        command.extend(["--prompt", str(prompt)])

    result = _run_python_script(command, timeout=30)
    return {
        **result,
        "parsed": _json_or_text(result.get("stdout", "")),
    }


def get_run_status(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    arguments = arguments or {}

    command = ["scripts/get_run_status.py"]

    run_id = arguments.get("run_id")
    if run_id:
        command.extend(["--run-id", str(run_id)])

    result = _run_python_script(command, timeout=60)
    return {
        **result,
        "parsed": _json_or_text(result.get("stdout", "")),
    }


def _read_text_prefix(path: Path, max_chars: int = 8192) -> str:
    try:
        if not path.exists() or not path.is_file():
            return ""
        with path.open("r", encoding="utf-8", errors="replace") as f:
            return f.read(max_chars)
    except Exception:
        return ""


def _find_first_status(obj: Any, max_depth: int = 4) -> str | None:
    if max_depth < 0:
        return None

    if isinstance(obj, dict):
        status = obj.get("status")
        if isinstance(status, str) and status.strip():
            return status.strip()
        for v in obj.values():
            found = _find_first_status(v, max_depth=max_depth - 1)
            if found:
                return found
        return None

    if isinstance(obj, list):
        for v in obj:
            found = _find_first_status(v, max_depth=max_depth - 1)
            if found:
                return found
        return None

    return None


def check_opencode_run_status(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Devuelve un estado compact-first de un run sin leer raw_outputs completos.

    Diseñada para evitar timeouts en Continue:
    - cuenta archivos, no los carga;
    - no lee TRACE/RUN_SUMMARY completos (solo prefijos cortos para status).
    """

    arguments = arguments or {}
    run_id = arguments.get("run_id")
    if not run_id:
        return {
            "ok": False,
            "status": "error",
            "error": "run_id es obligatorio.",
        }

    start = time.perf_counter()

    run_dir = ROOT / "docs" / "agent_runs" / str(run_id)
    agent_outputs_dir = run_dir / "agent_outputs"
    raw_outputs_dir = run_dir / "raw_outputs"

    exists = bool(run_dir.exists() and run_dir.is_dir())

    agent_outputs = sorted(agent_outputs_dir.glob("*.json")) if agent_outputs_dir.exists() else []
    raw_outputs = sorted(raw_outputs_dir.glob("*.json")) if raw_outputs_dir.exists() else []

    opencode_outputs = [p for p in agent_outputs if "_opencode" in p.name]
    opencode_raw_outputs = [p for p in raw_outputs if "_opencode_raw" in p.name]
    opencode_registered = bool(opencode_outputs and opencode_raw_outputs)

    latest_status: str | None = None

    # 1) Preferir RUN_SUMMARY (prefijo corto) para no leer archivos enormes.
    summary_prefix = _read_text_prefix(run_dir / "RUN_SUMMARY.md", max_chars=12000)
    if summary_prefix:
        m = re.search(r"[ÚU]ltimo\s+estado\s+registrado:\s*`([^`]+)`", summary_prefix)
        if m:
            latest_status = m.group(1).strip()

    # 2) Fallback: leer el último agent_output (JSON) por mtime, con límite de tamaño.
    if latest_status is None and agent_outputs:
        try:
            latest_file = max(agent_outputs, key=lambda p: p.stat().st_mtime)
            if latest_file.stat().st_size <= 1_000_000:
                data = json.loads(latest_file.read_text(encoding="utf-8", errors="replace"))
                latest_status = _find_first_status(data)
        except Exception:
            latest_status = None

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    return {
        "ok": True,
        "status": "ok" if exists else "not_found",
        "run_id": str(run_id),
        "exists": exists,
        "opencode_registered": opencode_registered,
        "agent_outputs_count": len(agent_outputs),
        "raw_outputs_count": len(raw_outputs),
        "latest_status": latest_status,
        "elapsed_ms": elapsed_ms,
        "error": None,
    }


def run_health_check(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Health check compacto de un run vía scripts/audit_agent_artifacts.py.

    Restricciones:
    - No abre raw_outputs completos.
    - No lee TRACE/RUN_SUMMARY completos (solo prefijos cortos, si existen).
    - No modifica evidencia ni genera archivos.

    Output: compacto-first (sin stdout/stderr completos del script).
    """

    arguments = arguments or {}

    run_id = arguments.get("run_id")
    if not run_id:
        return {
            "ok": False,
            "error": "run_id es obligatorio.",
        }

    stale_minutes = arguments.get("stale_minutes", 15)
    try:
        stale_minutes_int = int(stale_minutes)
    except Exception:
        stale_minutes_int = 15

    # Evitar valores no razonables que puedan degradar performance o semántica.
    stale_minutes_int = max(1, stale_minutes_int)

    result = _run_python_script(
        [
            "scripts/audit_agent_artifacts.py",
            "--health",
            "--run-id",
            str(run_id),
            "--stale-minutes",
            str(stale_minutes_int),
        ],
        timeout=60,
        max_output_chars=65536,
    )

    if not result.get("ok"):
        return {
            "ok": False,
            "status": "error",
            "run_id": str(run_id),
            "error": (result.get("stderr") or "Error ejecutando audit_agent_artifacts.py --health."),
            "elapsed_ms": result.get("elapsed_ms"),
        }

    parsed = _json_or_text(result.get("stdout", ""))
    if not isinstance(parsed, dict):
        preview = str(parsed)
        if len(preview) > 2000:
            preview = preview[:2000] + "\n... [truncated]"
        return {
            "ok": False,
            "status": "error",
            "run_id": str(run_id),
            "error": "Salida no JSON del health check.",
            "preview": preview,
            "elapsed_ms": result.get("elapsed_ms"),
        }

    health = parsed.get("health")
    if not isinstance(health, dict):
        return {
            "ok": False,
            "status": "error",
            "run_id": str(run_id),
            "error": "Salida JSON inesperada: falta key 'health'.",
            "elapsed_ms": result.get("elapsed_ms"),
        }

    # Normalizar output a un payload compacto y estable para Continue.
    return {
        "ok": True,
        "run_id": str(health.get("run_id") or run_id),
        "exists": bool(health.get("exists")),
        "health_status": str(health.get("health_status") or "unknown"),
        "latest_status": health.get("latest_status"),
        "opencode_registered": bool(health.get("opencode_registered")),
        "agent_outputs_count": int(health.get("agent_outputs_count") or 0),
        "raw_outputs_count": int(health.get("raw_outputs_count") or 0),
        "background_files_count": int(health.get("background_files_count") or 0),
        "indexed_in_RUN_INDEX": bool(health.get("indexed_in_RUN_INDEX")),
        "archive_recommended": bool(health.get("archive_recommended")),
        "issues": list(health.get("issues") or [])[:10],
        "recommendations": list(health.get("recommendations") or [])[:10],
        "elapsed_ms": int(health.get("elapsed_ms") or result.get("elapsed_ms") or 0),
    }


def create_and_dispatch_opencode_handoff(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    arguments = arguments or {}

    objective = arguments.get("objective")
    if not objective:
        return {
            "ok": False,
            "returncode": 2,
            "stdout": "",
            "stderr": "objective es obligatorio.",
        }

    target_agent = arguments.get("target_agent")
    if not target_agent:
        return {
            "ok": False,
            "returncode": 2,
            "stdout": "",
            "stderr": "target_agent es obligatorio.",
        }

    model = arguments.get("model")
    if not model:
        return {
            "ok": False,
            "returncode": 2,
            "stdout": "",
            "stderr": "model es obligatorio.",
        }

    command = [
        "scripts/create_and_dispatch_opencode_handoff.py",
        "--project-id",
        str(arguments.get("project_id", "orchestrator")),
        "--objective",
        str(objective),
        "--target-agent",
        str(target_agent),
        "--model",
        str(model),
        "--risk-level",
        str(arguments.get("risk_level", "medium")),
        "--scenario",
        str(arguments.get("scenario", "implementation")),
    ]

    handoff_body = arguments.get("handoff_body")
    if handoff_body:
        command.extend(["--handoff-body", str(handoff_body)])

    for f in arguments.get("allowed_files", []):
        command.extend(["--allowed-files", str(f)])

    for c in arguments.get("validation_commands", []):
        command.extend(["--validation-commands", str(c)])

    if arguments.get("requires_authorization") is True:
        command.extend(["--requires-authorization", "true"])

    if arguments.get("authorization_granted") is True:
        command.extend(["--authorization-granted", "true"])

    if arguments.get("auto_approve_permissions") is True:
        command.extend(["--auto-approve-permissions", "true"])

    if arguments.get("build_authorized") is True:
        command.extend(["--build-authorized", "true"])

    result = _run_python_script(command, timeout=60)
    parsed = _json_or_text(result.get("stdout", ""))

    # Si el script devuelve ok=false en JSON, reflejarlo en la respuesta MCP.
    if isinstance(parsed, dict) and parsed.get("ok") is False:
        return {
            "ok": False,
            "status": parsed.get("status") or "error",
            "error": parsed.get("error") or parsed.get("guardrail_error") or "create_and_dispatch_opencode_handoff bloqueado.",
            "parsed": parsed,
            "elapsed_ms": result.get("elapsed_ms"),
        }

    return {
        **result,
        "parsed": parsed,
    }


def verify_master_files(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Verifica archivos maestros con output compact-first para MCP.

    Nota: El script soporta full output por shell, pero MCP usa compact por defecto
    para minimizar payload y evitar timeouts.
    """

    arguments = arguments or {}

    mode = str(arguments.get("mode") or "compact").lower().strip()
    if mode not in {"compact", "full"}:
        mode = "compact"

    command = ["scripts/verify_master_files.py"]

    paths = arguments.get("paths")
    if paths:
        command.append("--paths")
        command.extend([str(p) for p in paths])

    if mode == "compact":
        command.append("--compact")
    else:
        command.append("--full")

    result = _run_python_script(command, timeout=60)

    if not result.get("ok"):
        return {
            "ok": False,
            "status": "error",
            "error": (result.get("stderr") or "Error ejecutando verify_master_files."),
            "elapsed_ms": result.get("elapsed_ms"),
        }

    parsed = _json_or_text(result.get("stdout", ""))

    # Compact-first: devolver el JSON del script (ya compacto) y evitar duplicar stdout.
    if isinstance(parsed, dict):
        parsed.setdefault("elapsed_ms", result.get("elapsed_ms"))
        parsed.setdefault("status", "ok")
        parsed.setdefault("mode", mode)
        return parsed

    # Fallback si stdout no es JSON (idealmente no debería pasar)
    preview = str(parsed)
    if len(preview) > 1200:
        preview = preview[:1200] + "\n... [truncated]"

    return {
        "ok": True,
        "status": "ok",
        "mode": mode,
        "elapsed_ms": result.get("elapsed_ms"),
        "truncated": True,
        "preview": preview,
    }


TOOL_HANDLERS = {
    "orchestrator_preflight": orchestrator_preflight,
    "select_agent_model": select_agent_model,
    "build_handoff_package": build_handoff_package,
    "run_diagnostic_flow": run_diagnostic_flow,
    "show_latest_run": show_latest_run,
    "run_opencode_from_handoff": run_opencode_from_handoff,
    "start_opencode_from_handoff_async": start_opencode_from_handoff_async,
    "get_run_status": get_run_status,
    "check_opencode_run_status": check_opencode_run_status,
    "run_health_check": run_health_check,
    "verify_master_files": verify_master_files,
    "create_and_dispatch_opencode_handoff": create_and_dispatch_opencode_handoff,
}


def call_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    if name not in ALLOWED_TOOLS:
        return {
            "ok": False,
            "error": f"Herramienta no permitida: {name}",
        }

    handler = TOOL_HANDLERS[name]
    return handler(arguments or {})


def self_test() -> None:
    print("Herramientas disponibles:")
    for name in sorted(ALLOWED_TOOLS):
        print(f"- {name}")

    print("\nPreflight:")
    result = orchestrator_preflight({})
    print(json.dumps({
        "ok": result.get("ok"),
        "returncode": result.get("returncode"),
        "parsed_status": (result.get("parsed") or {}).get("status") if isinstance(result.get("parsed"), dict) else None,
    }, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()




