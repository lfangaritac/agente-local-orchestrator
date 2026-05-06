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
import subprocess
import sys
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
}


def _run_python_script(args: list[str], timeout: int = 180) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )

    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
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


TOOL_HANDLERS = {
    "orchestrator_preflight": orchestrator_preflight,
    "select_agent_model": select_agent_model,
    "build_handoff_package": build_handoff_package,
    "run_diagnostic_flow": run_diagnostic_flow,
    "show_latest_run": show_latest_run,
    "run_opencode_from_handoff": run_opencode_from_handoff,
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
