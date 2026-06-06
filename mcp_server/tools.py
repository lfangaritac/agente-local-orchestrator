"""
tools.py

Herramientas seguras del MCP local para Continue.

Estas herramientas envuelven scripts ya probados del orquestador.
No permiten comandos arbitrarios.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import argparse
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from typing import Any



ROOT = Path(__file__).resolve().parents[1]

# Local, unversioned session state (used only when user opts-in via MCP tools).
STATE_DIR = ROOT / ".orchestrator_state"
ACTIVE_PROJECT_PATH = STATE_DIR / "active_project.json"

# Active project state schema (gitignored):
# {
#   "project_id": "...",
#   "set_at": "...",
#   "note": "...",
#   "last_event": {
#      "updated_at": "...",
#      "source": "run_general_instruction_flow|ingest_orchestrator_transfer|set_active_project",
#      "mode": "plan|dispatch_if_safe",
#      "instruction": "...",
#      "status": "...",
#      "next_frontier": "...",
#      "next_question": "...",
#      "handoff_json_path": "...",
#      "run_id": "..."
#   }
# }


os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")



ALLOWED_TOOLS = {
    "orchestrator_preflight",
    "semantic_context_gate",
    "project_context_indexer",
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
    "operational_status",
    "resolve_target_project",
    "enable_target_project",
    "plan_general_instruction",
    "run_general_instruction_flow",
    "get_active_project",

    "set_active_project",
    "init_project_onboarding_scaffold",
    "sync_active_last_event_to_project_docs",
    "ingest_orchestrator_transfer",
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


def _now_iso() -> str:
    # ISO-8601 without timezone math (good enough for local audit trails)
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _read_json_file(path: Path) -> dict[str, Any] | None:
    try:
        if not path.exists() or not path.is_file():
            return None
        if path.stat().st_size > 256_000:
            return None
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _write_json_file(path: Path, payload: dict[str, Any]) -> tuple[bool, str | None]:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return True, None
    except Exception as exc:
        return False, str(exc)


def _update_active_project_state(*, project_id: str, note: str | None = None, last_event_patch: dict[str, Any] | None = None) -> dict[str, Any]:
    """Actualiza el estado del proyecto activo (gitignored) con merge best-effort.

    Restricciones:
    - Solo escribe dentro de `.orchestrator_state/`.
    - Mantiene compatibilidad con el esquema anterior (project_id/set_at/note).
    """

    pid = (project_id or "").strip()
    if not pid:
        return {"ok": False, "status": "error", "error": "project_id es obligatorio."}

    current = _read_json_file(ACTIVE_PROJECT_PATH) or {}
    if not isinstance(current, dict):
        current = {}

    now = _now_iso()

    # If project_id changes, reset set_at.
    if str(current.get("project_id") or "").strip() != pid:
        current["project_id"] = pid
        current["set_at"] = now

    if note is not None:
        current["note"] = note or None

    if last_event_patch is not None:
        last_event = current.get("last_event")
        if not isinstance(last_event, dict):
            last_event = {}
        # Always bump updated_at.
        last_event["updated_at"] = now
        for k, v in last_event_patch.items():
            if v is None:
                continue
            last_event[k] = v
        current["last_event"] = last_event

    ok, err = _write_json_file(ACTIVE_PROJECT_PATH, current)
    if not ok:
        return {"ok": False, "status": "error", "error": f"No se pudo escribir active_project.json: {err}"}

    return {"ok": True, "status": "ok", "active_project": current, "path": str(ACTIVE_PROJECT_PATH)}



# --- Orchestrator Transfer (Shell Bridge) ingestion ---

ORCHESTRATOR_TRANSFER_MODE = "orchestrator_transfer"
ORCHESTRATOR_TRANSFER_JSON_GLOB = "orchestrator_transfer_*.json"
ORCHESTRATOR_TRANSFER_ALLOWED_CHANNELS_DEFAULT = ["shell_bridge", "replit_agent_chat"]


def _parse_iso_datetime(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        # Supports '2026-05-17T01:22:36+00:00'
        return datetime.fromisoformat(raw)
    except Exception:
        return None


def _safe_preview_text(value: Any, limit: int = 160) -> str:
    txt = str(value or "").strip().replace("\r\n", "\n")
    if len(txt) <= limit:
        return txt
    return txt[:limit] + "...<truncated>"


def _validate_orchestrator_transfer_handoff(payload: dict[str, Any], *, allowed_channels: list[str]) -> tuple[bool, str | None]:
    mode = str(payload.get("mode") or "").strip()
    if mode != ORCHESTRATOR_TRANSFER_MODE:
        return False, f"handoff.mode inválido: '{mode}'"

    channel = str(payload.get("channel") or "").strip()
    if channel not in allowed_channels:
        return False, f"handoff.channel no permitido: '{channel}'"

    ts = payload.get("timestamp")
    if not isinstance(ts, str) or not ts.strip():
        return False, "handoff.timestamp faltante o inválido"

    instruction = payload.get("instruction")
    if not isinstance(instruction, str) or not instruction.strip():
        return False, "handoff.instruction faltante o inválido"

    return True, None


def _collect_orchestrator_transfer_candidates(
    *,
    handoff_dir: Path,
    allowed_channels: list[str],
    max_candidates: int,
) -> list[dict[str, Any]]:
    if not handoff_dir.exists() or not handoff_dir.is_dir():
        return []

    files = sorted(handoff_dir.glob(ORCHESTRATOR_TRANSFER_JSON_GLOB), key=lambda p: p.name)
    if max_candidates > 0:
        files = files[-max_candidates:]

    candidates: list[dict[str, Any]] = []

    for path in files:
        data = _read_json_file(path)
        if not isinstance(data, dict):
            continue

        ok, _err = _validate_orchestrator_transfer_handoff(data, allowed_channels=allowed_channels)
        if not ok:
            continue

        ts_dt = _parse_iso_datetime(data.get("timestamp"))
        mtime = path.stat().st_mtime
        recency_epoch = ts_dt.timestamp() if ts_dt else float(mtime)
        candidates.append(
            {
                "path": str(path),
                "mtime": float(mtime),
                "timestamp": str(data.get("timestamp") or ""),
                "recency_epoch": float(recency_epoch),
                "recency_basis": "timestamp" if ts_dt else "mtime",
                "channel": str(data.get("channel") or ""),
                "intent": str(data.get("intent") or ""),
                "project_id": ((data.get("project") or {}) if isinstance(data.get("project"), dict) else {}).get("project_id"),
                "workspace_path": ((data.get("workspace") or {}) if isinstance(data.get("workspace"), dict) else {}).get("path"),
                "instruction_preview": _safe_preview_text(data.get("instruction")),
            }
        )

    # Newest last in this sort order
    candidates.sort(key=lambda c: (c.get("recency_epoch", 0.0), c.get("mtime", 0.0), str(c.get("path") or "")))
    return candidates


def ingest_orchestrator_transfer(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Ingesta un handoff `orchestrator_transfer_*.json` y lo convierte en un Plan interno.

    Objetivo:
    - Evitar copy/paste manual en Continue.
    - Plan-only: NO despacha Build, NO activa Replit Agent.

    Restricciones:
    - Solo lectura sobre el proyecto objetivo (lee JSON del handoff).
    - Puede escribir solo el estado de sesión local en `.orchestrator_state/` (gitignored) para soportar "retomar".
    """

    arguments = arguments or {}

    # Inputs
    handoff_json_path_raw = str(arguments.get("handoff_json_path") or "").strip()
    handoff_dir_raw = str(arguments.get("handoff_dir") or "").strip()
    workspace_path_raw = str(arguments.get("workspace_path") or "").strip()
    project_query = str(arguments.get("project_query") or "").strip()

    allowed_channels = arguments.get("allowed_channels")
    if isinstance(allowed_channels, list) and all(isinstance(x, str) for x in allowed_channels):
        allowed_channels_list = [x.strip() for x in allowed_channels if x.strip()]
    else:
        allowed_channels_list = ORCHESTRATOR_TRANSFER_ALLOWED_CHANNELS_DEFAULT

    max_candidates = int(arguments.get("max_candidates") or 50)
    max_candidates = max(1, min(max_candidates, 200))

    set_active = bool(arguments.get("set_active_project", True))

    # Forwarded flags to general flow
    include_git = bool(arguments.get("include_git", True))
    include_orchestrator_status = bool(arguments.get("include_orchestrator_status", True))
    include_preflight = bool(arguments.get("include_preflight", True))
    include_semantic_context_gate = bool(arguments.get("include_semantic_context_gate", True))

    start = time.perf_counter()

    # 1) Locate handoff JSON
    selected_path: Path | None = None
    candidates: list[dict[str, Any]] = []

    if handoff_json_path_raw:
        selected_path = Path(handoff_json_path_raw).expanduser()
    else:
        # Infer workspace_path if not provided
        if not workspace_path_raw and project_query:
            res = resolve_target_project({"project_query": project_query, "include_git": False})
            if isinstance(res, dict) and res.get("project_confirmed") and res.get("local_path"):
                workspace_path_raw = str(res.get("local_path") or "")

        if not workspace_path_raw and not project_query:
            active = _read_json_file(ACTIVE_PROJECT_PATH) or {}
            active_pid = str(active.get("project_id") or "").strip()
            if active_pid:
                project_query = active_pid
                res = resolve_target_project({"project_query": project_query, "include_git": False})
                if isinstance(res, dict) and res.get("project_confirmed") and res.get("local_path"):
                    workspace_path_raw = str(res.get("local_path") or "")

        if not workspace_path_raw and not handoff_dir_raw:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return {
                "ok": True,
                "status": "missing_inputs",
                "error": "Se requiere handoff_json_path o (workspace_path/handoff_dir) para localizar el handoff.",
                "next_frontier": "provide_handoff_path",
                "next_question": "Indica handoff_json_path o workspace_path (del proyecto donde corriste ./orquestador).",
                "elapsed_ms": elapsed_ms,
            }

        handoff_dir = Path(handoff_dir_raw).expanduser() if handoff_dir_raw else (Path(workspace_path_raw).expanduser() / "docs" / "handoffs")
        candidates = _collect_orchestrator_transfer_candidates(
            handoff_dir=handoff_dir,
            allowed_channels=allowed_channels_list,
            max_candidates=max_candidates,
        )

        if not candidates:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return {
                "ok": True,
                "status": "handoff_not_found",
                "handoff_dir": str(handoff_dir),
                "pattern": ORCHESTRATOR_TRANSFER_JSON_GLOB,
                "allowed_channels": allowed_channels_list,
                "candidates_count": 0,
                "next_frontier": "generate_handoff",
                "next_question": "No se encontró un handoff orchestrator_transfer válido. Ejecuta ./orquestador (o python scripts/orchestrator_bridge.py) en el proyecto objetivo y reintenta.",
                "elapsed_ms": elapsed_ms,
            }

        # pick most recent, but if top key ties, treat as ambiguous and ask for explicit path
        best = candidates[-1]
        if len(candidates) >= 2:
            prev = candidates[-2]
            if (
                float(best.get("recency_epoch") or 0.0) == float(prev.get("recency_epoch") or 0.0)
                and float(best.get("mtime") or 0.0) == float(prev.get("mtime") or 0.0)
            ):
                elapsed_ms = int((time.perf_counter() - start) * 1000)
                return {
                    "ok": True,
                    "status": "handoff_ambiguous",
                    "handoff_dir": str(handoff_dir),
                    "pattern": ORCHESTRATOR_TRANSFER_JSON_GLOB,
                    "allowed_channels": allowed_channels_list,
                    "candidates_count": len(candidates),
                    "candidates_preview": candidates[-5:],
                    "next_frontier": "select_handoff",
                    "next_question": "Hay múltiples handoffs igualmente recientes. Indica handoff_json_path explícito.",
                    "elapsed_ms": elapsed_ms,
                }

        selected_path = Path(str(best.get("path") or ""))

    if selected_path is None:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            "ok": True,
            "status": "handoff_not_found",
            "error": "No se pudo seleccionar handoff_json_path.",
            "elapsed_ms": elapsed_ms,
        }

    payload = _read_json_file(selected_path)
    if not isinstance(payload, dict):
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            "ok": True,
            "status": "invalid_handoff",
            "handoff_json_path": str(selected_path),
            "error": "No se pudo leer/parsear el JSON del handoff (o excede límite de tamaño).",
            "next_frontier": "regenerate_handoff",
            "elapsed_ms": elapsed_ms,
        }

    ok, err = _validate_orchestrator_transfer_handoff(payload, allowed_channels=allowed_channels_list)
    if not ok:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            "ok": True,
            "status": "invalid_handoff",
            "handoff_json_path": str(selected_path),
            "error": err or "handoff inválido",
            "next_frontier": "regenerate_handoff",
            "elapsed_ms": elapsed_ms,
        }

    instruction = str(payload.get("instruction") or "").strip()

    # Project + workspace extraction (prefer payload)
    payload_project_id = None
    if isinstance(payload.get("project"), dict):
        payload_project_id = (payload.get("project") or {}).get("project_id")

    payload_workspace_path = None
    if isinstance(payload.get("workspace"), dict):
        payload_workspace_path = (payload.get("workspace") or {}).get("path")

    project_query_from_handoff = str(payload_project_id or "").strip()
    workspace_path_from_handoff = str(payload_workspace_path or "").strip()

    effective_project_query = project_query_from_handoff or project_query
    effective_workspace_path = workspace_path_from_handoff or workspace_path_raw

    # 2) Resolve project (best-effort) and set active project
    resolution = resolve_target_project(
        {
            "project_query": effective_project_query,
            "workspace_path": effective_workspace_path,
            "include_git": include_git,
        }
    )

    active_project_set = None
    if set_active and isinstance(resolution, dict) and resolution.get("project_confirmed") is True:
        pid = str(resolution.get("project_id") or "").strip()
        if pid:
            active_project_set = set_active_project(
                {
                    "project_id": pid,
                    "note": f"ingest_orchestrator_transfer:{selected_path.name}",
                }
            )

    intent = str(payload.get("intent") or "orchestrator_transfer").strip()
    channel = str(payload.get("channel") or "").strip()

    # 3) If return_to_replit: do not activate Replit automatically; just recommend + require auth.
    if intent == "return_to_replit":
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            "ok": True,
            "status": "return_to_replit",
            "handoff": {
                "handoff_json_path": str(selected_path),
                "timestamp": payload.get("timestamp"),
                "channel": channel,
                "intent": intent,
                "instruction_preview": _safe_preview_text(instruction),
            },
            "resolution": resolution,
            "active_project_set": active_project_set,
            "instruction_normalized": instruction,
            "suggested_mode": "Plan",
            "executor_recommended": "continue",
            "escalation_decision": {"replit": "recommended", "premium": "not_required"},
            "authorizations_required": ["replit"],
            "next_frontier": "request_replit_authorization",
            "next_question": "El handoff pide volver a Replit. ¿Autorizas escalar a Replit Agent para validar/ejecutar? (No se activa automáticamente).",
            "elapsed_ms": elapsed_ms,
        }

    # 4) Normal flow: mode Plan (no dispatch)
    flow = run_general_instruction_flow(
        {
            "mode": "plan",
            "instruction": instruction,
            "project_query": effective_project_query,
            "workspace_path": effective_workspace_path,
            "include_git": include_git,
            "include_orchestrator_status": include_orchestrator_status,
            "include_preflight": include_preflight,
            "include_semantic_context_gate": include_semantic_context_gate,
        }
    )

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    plan = flow.get("plan") if isinstance(flow, dict) else None

    return {
        "ok": True,
        "status": "ok",
        "handoff": {
            "handoff_json_path": str(selected_path),
            "timestamp": payload.get("timestamp"),
            "channel": channel,
            "intent": intent,
            "instruction_preview": _safe_preview_text(instruction),
        },
        "candidates_count": len(candidates) if candidates else None,
        "candidates_preview": candidates[-5:] if candidates else None,
        "resolution": resolution,
        "active_project_set": active_project_set,
        "instruction_normalized": instruction,
        "suggested_mode": "Plan",
        "executor_recommended": (plan.get("routing") or {}).get("recommended_agent") if isinstance(plan, dict) else None,
        "escalation_decision": plan.get("escalation_decision") if isinstance(plan, dict) else None,
        "authorizations_required": plan.get("authorizations_required") if isinstance(plan, dict) else None,
        "next_frontier": plan.get("next_frontier") if isinstance(plan, dict) else None,
        "next_question": plan.get("next_question") if isinstance(plan, dict) else None,
        "flow": flow,
        "elapsed_ms": elapsed_ms,
    }


def get_active_project(_: dict[str, Any] | None = None) -> dict[str, Any]:
    """Devuelve el proyecto activo (sesión) si existe.

    Nota: esta memoria es local y efímera; vive en `.orchestrator_state/` (gitignored).
    """

    data = _read_json_file(ACTIVE_PROJECT_PATH)
    if not data:
        return {
            "ok": True,
            "status": "empty",
            "active_project": None,
            "path": str(ACTIVE_PROJECT_PATH),
        }

    # Back-compat: exponer campos base + last_event si existe.
    active_project = {
        "project_id": data.get("project_id"),
        "set_at": data.get("set_at"),
        "note": data.get("note"),
    }

    last_event = data.get("last_event")
    if isinstance(last_event, dict):
        active_project["last_event"] = {
            "updated_at": last_event.get("updated_at"),
            "source": last_event.get("source"),
            "mode": last_event.get("mode"),
            "instruction_preview": _safe_preview_text(last_event.get("instruction"), limit=180),
            "status": last_event.get("status"),
            "next_frontier": last_event.get("next_frontier"),
            "next_question_preview": _safe_preview_text(last_event.get("next_question"), limit=220),
            "handoff_json_path": last_event.get("handoff_json_path"),
            "run_id": last_event.get("run_id"),
        }

    return {
        "ok": True,
        "status": "ok",
        "active_project": active_project,
        "path": str(ACTIVE_PROJECT_PATH),
    }



def set_active_project(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Establece el proyecto activo (sesión) para soportar 'retomar'/'volver'.

    Restricciones:
    - Solo escribe dentro de `.orchestrator_state/` (gitignored).
    - No modifica proyectos externos.
    """

    arguments = arguments or {}
    project_id = (arguments.get("project_id") or "").strip()
    if not project_id:
        return {"ok": False, "status": "error", "error": "project_id es obligatorio."}

    note = (arguments.get("note") or "").strip() or None

    # Registrar un last_event mínimo para apoyar 'retomar'.
    return _update_active_project_state(
        project_id=project_id,
        note=note,
        last_event_patch={
            "source": "set_active_project",
            "mode": None,
            "instruction": None,
            "status": None,
            "next_frontier": None,
            "next_question": None,
            "handoff_json_path": None,
            "run_id": None,
        },
    )



def orchestrator_preflight(_: dict[str, Any] | None = None) -> dict[str, Any]:

    result = _run_python_script(["scripts/orchestrator_preflight.py"])
    return {
        **result,
        "parsed": _json_or_text(result.get("stdout", "")),
    }


def semantic_context_gate(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    arguments = arguments or {}

    project_id = str(arguments.get("project_id") or "").strip()
    instruction = str(arguments.get("instruction") or "").strip()
    max_results = int(arguments.get("max_results") or 8)

    if not project_id:
        return {"ok": False, "status": "error", "error": "project_id es obligatorio."}
    if not instruction:
        return {"ok": False, "status": "error", "error": "instruction es obligatorio."}

    result = _run_python_script(
        [
            "scripts/semantic_context_gate.py",
            "--project",
            project_id,
            "--instruction",
            instruction,
            "--max-results",
            str(max_results),
            "--output",
            "json",
        ],
        timeout=90,
        max_output_chars=32768,
    )
    parsed = _json_or_text(result.get("stdout", ""))
    return {
        **result,
        # returncode=2 is a valid gate decision (blocked_*), not a tool crash.
        "ok": result.get("returncode") in {0, 2},
        "parsed": parsed,
    }


def project_context_indexer(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    arguments = arguments or {}

    project_id = str(arguments.get("project_id") or "").strip()
    apply = bool(arguments.get("apply", False))
    if not project_id:
        return {"ok": False, "status": "error", "error": "project_id es obligatorio."}

    command = [
        "scripts/project_context_indexer.py",
        "--project",
        project_id,
        "--output",
        "json",
    ]
    if apply:
        command.append("--apply")

    result = _run_python_script(command, timeout=120, max_output_chars=32768)
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

    project_id = str(arguments.get("project_id", "orchestrator")).strip() or "orchestrator"

    # Guardrail operativo: no despachar handoffs de ejecución si falta el onboarding canónico.
    # (No crea scaffold automáticamente; solo recomienda la acción.)
    if project_id != "orchestrator":
        onboarding = _probe_project_onboarding(project_id)
        if onboarding.get("status") in {"missing", "partial"}:
            missing_files = onboarding.get("missing") if isinstance(onboarding.get("missing"), list) else []
            return {
                "ok": True,
                "status": "onboarding_required",
                "project_id": project_id,
                "missing_files": missing_files,
                "onboarding": onboarding,
                "recommended_next_tool_call": {
                    "tool": "init_project_onboarding_scaffold",
                    "arguments": {"project_id": project_id, "dry_run": False},
                },
                "next_frontier": "init_onboarding_scaffold",
            }

    command = [
        "scripts/create_and_dispatch_opencode_handoff.py",
        "--project-id",
        project_id,
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

    if arguments.get("user_authorized_build") is True:
        command.extend(["--user-authorized-build", "true"])

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


def _redact_remote_url(url: str) -> str:
    """Redacta userinfo/tokens embebidos en URLs remotas.

    Ejemplos a proteger:
    - https://<token>@github.com/org/repo.git
    - https://user:pass@host/path
    """

    u = (url or "").strip()
    if not u:
        return ""

    # Redactar userinfo en URLs tipo scheme://userinfo@host
    u = re.sub(r"(https?://)([^/@\s]+)@", r"\1<redacted>@", u, flags=re.IGNORECASE)
    return u


def _normalize_repo_url(url: str) -> str:
    u = _redact_remote_url(url).strip()
    if u.endswith(".git"):
        u = u[: -len(".git")]
    return u.rstrip("/").lower()


def _run_git(args: list[str], cwd: Path, timeout: int = 12) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        out = (completed.stdout or "").strip()
        err = (completed.stderr or "").strip()
        if completed.returncode != 0:
            return False, (err or out)
        return True, out
    except Exception as exc:
        return False, str(exc)


def _git_probe_repo(path: Path) -> dict[str, Any]:
    """Devuelve info Git compacta (read-only)."""

    info: dict[str, Any] = {
        "ok": False,
        "path": str(path),
        "is_git_repo": False,
        "branch": None,
        "last_commit": None,
        "working_tree": {"clean": None},
        "remote_origin": None,
        "errors": [],
    }

    git_dir = path / ".git"
    if not (git_dir.exists() and git_dir.is_dir()):
        info["errors"].append("no_git_dir")
        return info

    info["is_git_repo"] = True

    ok, branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], path)
    if ok:
        info["branch"] = branch
    else:
        info["errors"].append(f"branch_error:{branch}")

    ok, last_commit = _run_git(["log", "-1", "--oneline"], path)
    if ok:
        info["last_commit"] = last_commit
    else:
        info["errors"].append(f"log_error:{last_commit}")

    ok, porcelain = _run_git(["status", "--porcelain"], path)
    if ok:
        info["working_tree"]["clean"] = (porcelain.strip() == "")
    else:
        info["errors"].append(f"status_error:{porcelain}")

    ok, remote = _run_git(["remote", "get-url", "origin"], path)
    if ok:
        info["remote_origin"] = _redact_remote_url(remote)
    else:
        # No es error crítico: repos sin remote origin.
        info["remote_origin"] = None

    info["ok"] = True
    return info


def _parse_registry_entries(registry_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse mínimo del PROJECT_REGISTRY.md.

    Nota: evita dependencia/import de scripts/ porque no es un paquete Python.
    """

    if not registry_path.exists():
        return [], [f"registry_not_found:{registry_path}"]

    content = registry_path.read_text(encoding="utf-8", errors="replace")
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    warnings: list[str] = []

    for raw in content.splitlines():
        stripped = raw.strip()
        if not stripped:
            if current:
                entries.append(current)
                current = {}
            continue

        if stripped.startswith("#") or stripped.startswith("|"):
            continue

        m = re.match(r"^-?\s*(.+?):\s*(.*)$", stripped)
        if not m:
            continue

        key = m.group(1).strip()
        value = m.group(2).strip()

        # Parsear solo campos relevantes.
        if key == "project_id":
            current[key] = value
        elif key == "nombre_canónico":
            current[key] = value
        elif key == "alias_permitidos":
            current[key] = [a.strip() for a in value.split(",") if a.strip()]
        elif key in {"repositorio_remoto", "repo_url", "local_path", "ruta_local", "environment_type", "origen"}:
            current[key] = value

    if current:
        entries.append(current)

    if not entries:
        warnings.append("registry_empty")

    return entries, warnings


def _resolve_by_query(query: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    q = (query or "").strip()
    ql = q.lower()

    # 1) project_id exact
    for e in entries:
        pid = (e.get("project_id") or "").strip()
        if pid and pid.lower() == ql:
            return {"ok": True, "project_found": True, "matched_by": "project_id", "entry": e, "candidates": []}

    # 2) alias exact
    alias_matches = []
    for e in entries:
        aliases = e.get("alias_permitidos") or []
        if any(a.lower() == ql for a in aliases):
            alias_matches.append(e)

    if len(alias_matches) == 1:
        return {"ok": True, "project_found": True, "matched_by": "alias", "entry": alias_matches[0], "candidates": []}

    if len(alias_matches) > 1:
        return {
            "ok": False,
            "project_found": False,
            "matched_by": "alias",
            "entry": None,
            "candidates": alias_matches,
            "error": f"ambiguous alias '{q}' matches {len(alias_matches)} projects",
        }

    # 3) nombre_canónico exact
    for e in entries:
        name = (e.get("nombre_canónico") or "").strip()
        if name and name.lower() == ql:
            return {"ok": True, "project_found": True, "matched_by": "nombre_canonico", "entry": e, "candidates": []}

    return {"ok": False, "project_found": False, "matched_by": None, "entry": None, "candidates": [], "error": f"no match for '{q}'"}


def _resolve_by_workspace_path(workspace_path: Path, entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Inferencia best-effort desde un workspace local (read-only)."""

    # 0) Orquestador: si el workspace es el repo actual, es seguro confirmarlo.
    try:
        if workspace_path.resolve() == ROOT.resolve():
            return {
                "ok": True,
                "project_found": True,
                "matched_by": "workspace_path_orchestrator_root",
                "entry": {
                    "project_id": "orchestrator",
                    "nombre_canónico": "agente-local-orchestrator",
                    "alias_permitidos": ["orchestrator"],
                    "repo_url": "",
                    "environment_type": "local",
                    "local_path": str(ROOT),
                },
                "candidates": [],
            }
    except Exception:
        pass

    # 1) Match directo por local_path/ruta_local si está en registry
    try:
        ws = workspace_path.expanduser().resolve()
    except Exception:
        ws = workspace_path

    direct_matches = []
    for e in entries:
        for k in ("local_path", "ruta_local"):
            raw = (e.get(k) or "").strip()
            if not raw or raw.lower() in {"null", "none", "n/a"}:
                continue
            try:
                if Path(raw).expanduser().resolve() == ws:
                    direct_matches.append(e)
            except Exception:
                continue

    if len(direct_matches) == 1:
        return {"ok": True, "project_found": True, "matched_by": "local_path", "entry": direct_matches[0], "candidates": []}

    if len(direct_matches) > 1:
        return {
            "ok": False,
            "project_found": False,
            "matched_by": "local_path",
            "entry": None,
            "candidates": direct_matches,
            "error": f"ambiguous local_path matches {len(direct_matches)} projects",
        }

    # 2) Match por git remote origin
    git_info = _git_probe_repo(ws)
    origin = (git_info.get("remote_origin") or "").strip()
    if origin:
        origin_norm = _normalize_repo_url(origin)
        remote_matches = []
        for e in entries:
            repo_url = (e.get("repo_url") or e.get("repositorio_remoto") or "").strip()
            if not repo_url:
                continue
            if _normalize_repo_url(repo_url) == origin_norm:
                remote_matches.append(e)

        if len(remote_matches) == 1:
            return {"ok": True, "project_found": True, "matched_by": "git_remote_repo_url", "entry": remote_matches[0], "candidates": []}

        if len(remote_matches) > 1:
            return {
                "ok": False,
                "project_found": False,
                "matched_by": "git_remote_repo_url",
                "entry": None,
                "candidates": remote_matches,
                "error": f"ambiguous repo_url matches {len(remote_matches)} projects",
            }

    # No se pudo inferir contra registry.
    return {
        "ok": True,
        "project_found": False,
        "matched_by": "workspace_path",
        "entry": None,
        "candidates": [],
        "workspace_git": git_info,
    }


def resolve_target_project(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Resolver proyecto objetivo + preflight compacto (read-only, compact-first).

    Diseñada para operar con instrucciones generales del usuario.

    Entradas (todas opcionales):
    - project_query: project_id/alias/nombre.
    - workspace_path: ruta del workspace local para inferencia best-effort.
    - projects_root: raíz para sugerir/ubicar clones locales (solo lectura).
    - include_git: incluir probe Git compacto cuando exista repo local.

    Restricciones:
    - No clona.
    - No modifica archivos.
    - No instala dependencias.
    - No usa Replit.
    """

    arguments = arguments or {}

    project_query = (arguments.get("project_query") or "").strip()
    workspace_path_raw = (arguments.get("workspace_path") or "").strip()
    projects_root = arguments.get("projects_root")
    include_git = bool(arguments.get("include_git", True))

    registry_path = ROOT / "PROJECT_REGISTRY.md"
    entries, reg_warnings = _parse_registry_entries(registry_path)

    resolution: dict[str, Any]
    workspace_git: dict[str, Any] | None = None

    if project_query:
        resolution = _resolve_by_query(project_query, entries)
    elif workspace_path_raw:
        ws_path = Path(workspace_path_raw).expanduser()
        resolution = _resolve_by_workspace_path(ws_path, entries)
        workspace_git = resolution.get("workspace_git") if isinstance(resolution, dict) else None
    else:
        resolution = {
            "ok": True,
            "project_found": False,
            "matched_by": None,
            "entry": None,
            "candidates": [],
        }

    result: dict[str, Any] = {
        "ok": True,
        "status": "ok",
        "project_confirmed": False,
        "project_not_confirmed": False,
        "project_id": None,
        "matched_by": resolution.get("matched_by"),
        "aliases": [],
        "environment_type": None,
        "repo_url": None,
        "local_path": None,
        "suggested_local_path": None,
        "local_exists": False,
        "git_repo_exists": False,
        "clone_required": False,
        "git": None,
        "suggested_mode": "Plan",
        "executor_recommended": None,
        "risks": [],
        "authorizations_required": [],
        "escalation_decision": {
            "replit": "not_required",
            "premium": "not_required",
        },
        "next_frontier": None,
        "next_question": None,
        "warnings": reg_warnings,
    }

    # Errores de resolución: alias ambiguo o no encontrado.
    if resolution.get("ok") is False:
        candidates = resolution.get("candidates") or []

        result["project_not_confirmed"] = True
        result["status"] = "project_not_confirmed"
        result["next_frontier"] = "confirm_project"
        result["executor_recommended"] = "continue"

        if candidates:
            result["risks"].append("ambiguous_project")
            result["next_question"] = (
                "Proyecto objetivo no confirmado por ambigüedad. "
                "Indica un único project_id/alias o la ruta workspace_path."
            )
            # Compact-first: devolver como IDs/nombres si existen.
            result["candidates"] = [
                {
                    "project_id": (c.get("project_id") or "").strip(),
                    "nombre_canónico": (c.get("nombre_canónico") or "").strip(),
                }
                for c in candidates
            ][:10]
        else:
            result["risks"].append("project_not_found")
            result["next_question"] = (
                "Proyecto objetivo no confirmado: no coincide con PROJECT_REGISTRY.md. "
                "Indica un project_id/alias válido o proporciona workspace_path."
            )

        # Sin sesgo anti-Replit: si el proyecto no está resuelto, Replit puede ser opcional.
        result["escalation_decision"]["replit"] = "optional"

        if workspace_git:
            result["workspace_git"] = workspace_git

        return result

    entry = resolution.get("entry")

    if not entry:
        # No se encontró proyecto en registry. Si se pasó workspace_path, devolvemos git info como pista.
        result["project_not_confirmed"] = True
        result["status"] = "project_not_confirmed"
        result["next_frontier"] = "confirm_project"

        if workspace_git and workspace_git.get("is_git_repo"):
            result["risks"].append("workspace_not_registered")
            result["workspace_git"] = workspace_git
            result["next_question"] = "Proyecto objetivo no confirmado. Indica project_id/alias del registro, o registra este repo en PROJECT_REGISTRY.md."
        else:
            result["risks"].append("missing_project_query")
            result["next_question"] = "Proyecto objetivo no confirmado. Indica project_id/alias o proporciona workspace_path."

        # Si no hay local, Replit es opcional (no sesgo anti-Replit).
        result["escalation_decision"]["replit"] = "optional"
        result["executor_recommended"] = "continue"
        return result

    # Tenemos entrada (confirmada)
    project_id = (entry.get("project_id") or "").strip() or None
    result["project_confirmed"] = True
    result["project_id"] = project_id
    result["aliases"] = entry.get("alias_permitidos") or []

    env_type = (entry.get("environment_type") or entry.get("origen") or "").strip() or None
    result["environment_type"] = env_type

    repo_url = (entry.get("repo_url") or entry.get("repositorio_remoto") or "").strip() or None
    result["repo_url"] = _redact_remote_url(repo_url or "") or None

    # Determinar local_path preferido
    local_path_raw = (entry.get("local_path") or entry.get("ruta_local") or "").strip()
    local_path: Path | None = None
    if local_path_raw and local_path_raw.lower() not in {"null", "none", "n/a"}:
        try:
            local_path = Path(local_path_raw).expanduser()
            result["local_path"] = str(local_path)
        except Exception:
            local_path = None

    # Si no hay local_path explícito, usar prepare_project_workspace para sugerir y detectar existencia.
    if local_path is None and project_id:
        cmd = [
            "scripts/prepare_project_workspace.py",
            "--project",
            str(project_id),
            "--output",
            "json",
        ]
        if projects_root:
            cmd.extend(["--projects-root", str(projects_root)])

        pw = _run_python_script(cmd, timeout=30)
        parsed = _json_or_text(pw.get("stdout", ""))
        if isinstance(parsed, dict) and parsed.get("ok") is True:
            result["suggested_local_path"] = parsed.get("suggested_local_path")
            result["local_exists"] = bool(parsed.get("local_exists"))
            result["git_repo_exists"] = bool(parsed.get("git_repo_exists"))
            result["clone_required"] = bool(parsed.get("clone_required"))
            if parsed.get("suggested_local_path"):
                try:
                    local_path = Path(str(parsed["suggested_local_path"]))
                except Exception:
                    local_path = None
        else:
            # Si falla, dejamos best-effort.
            result["warnings"].append("prepare_project_workspace_failed")

    # Si tenemos local_path y existe, actualizar flags y hacer git probe.
    if local_path is not None:
        try:
            local_resolved = local_path.expanduser().resolve()
            result["local_path"] = str(local_resolved)
            result["local_exists"] = bool(local_resolved.exists() and local_resolved.is_dir())
            result["git_repo_exists"] = bool((local_resolved / ".git").exists())
            result["clone_required"] = bool(result["local_exists"] and not result["git_repo_exists"]) or (not result["local_exists"])
        except Exception:
            pass

    if result["clone_required"] is True:
        result["risks"].append("clone_required")
        result["next_frontier"] = "prepare_workspace"
        result["executor_recommended"] = "continue"
        # No bloquear Replit: opcional como alternativa si aporta valor.
        result["escalation_decision"]["replit"] = "optional"
        return result

    # Repo local existe y es git
    if include_git and result.get("local_path") and result.get("git_repo_exists"):
        git_info = _git_probe_repo(Path(str(result["local_path"])))
        result["git"] = git_info
        if git_info.get("working_tree", {}).get("clean") is False:
            result["risks"].append("working_tree_dirty")

    result["next_frontier"] = "local_diagnostic_ready"
    result["executor_recommended"] = "opencode:context-validator"

    # Escalamiento: por defecto no requerido; Replit/premium pueden ser opcionales según activadores.
    # En esta fase (solo resolución), no inferimos necesidad de runtime/seguridad.
    result["escalation_decision"] = {
        "replit": "optional" if env_type and "replit" in env_type.lower() else "not_required",
        "premium": "not_required",
    }

    if project_id:
        result["onboarding"] = _probe_project_onboarding(str(project_id))

    return result


# --- Project enablement (Plan-first -> Apply confirmado) ---

# Canon de campos versionados en PROJECT_REGISTRY.md.
# Nota: mantener valores en 1 línea (parsing simple).
REGISTRY_FIELD_ORDER = [
    "project_id",
    "nombre_canónico",
    "alias_permitidos",
    "ruta_local",
    "repositorio_remoto",
    "origen",
    "environment_type",
    "repo_url",
    "replit_workspace_path",
    "replit_join_url",
    "local_path",
    "stack_detectado",
    "documentación_principal",
    "código_fuente_relevante",
    "estado_sincronización",
    "alertas_críticas",
    "lecciones_locales",
    "último_análisis",
    "responsable",
]


def _is_nullish(value: Any) -> bool:
    if value is None:
        return True
    v = str(value).strip()
    if not v:
        return True
    return v.lower() in {"null", "none", "n/a", "unknown"}


def _coerce_aliases(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        parts = [str(x).strip() for x in value]
    else:
        parts = [p.strip() for p in str(value).split(",")]
    out: list[str] = []
    for a in parts:
        if not a:
            continue
        # Guardrail: aliases no deben tener espacios
        a = re.sub(r"\s+", "-", a)
        if a not in out:
            out.append(a)
    return out


def _validate_project_id(project_id: str) -> tuple[bool, str | None, str | None]:
    pid = (project_id or "").strip()
    if not pid:
        return False, "missing_project_id", None

    # Restricción conservadora: ids estables para paths.
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,63}", pid):
        suggestion = re.sub(r"[^a-zA-Z0-9._-]+", "-", pid).strip("-_.").lower()
        suggestion = re.sub(r"-+", "-", suggestion) or None
        return False, "invalid_project_id", suggestion

    return True, None, None


def _ensure_safe_test_path(path: Path) -> tuple[bool, str | None]:
    """Permite overrides solo dentro de .orchestrator_state/ (gitignored)."""

    try:
        st = STATE_DIR.resolve()
        path_r = path.resolve()
        path_r.relative_to(st)
        return True, None
    except Exception:
        return False, "unsafe_test_path_outside_state_dir"


def _parse_registry_kv_lines(lines: list[str]) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith("<!--"):
            continue
        m = re.match(r"^-?\s*(.+?):\s*(.*)$", stripped)
        if not m:
            continue
        key = m.group(1).strip()
        value = m.group(2).strip()
        if key == "alias_permitidos":
            fields[key] = _coerce_aliases(value)
        else:
            fields[key] = value
    return fields


def _parse_registry_blocks(registry_text: str) -> dict[str, Any]:
    """Parse best-effort por headings '### <id>' para patch idempotente."""

    lines = (registry_text or "").splitlines()
    blocks: list[dict[str, Any]] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("### "):
            start = i
            heading_pid = line[len("### ") :].strip()
            i += 1
            body: list[str] = []
            while i < len(lines) and not lines[i].startswith("### "):
                body.append(lines[i])
                i += 1
            end = i
            fields = _parse_registry_kv_lines(body)
            pid = str(fields.get("project_id") or heading_pid).strip()
            blocks.append(
                {
                    "project_id": pid,
                    "heading_project_id": heading_pid,
                    "start": start,
                    "end": end,
                    "fields": fields,
                }
            )
        else:
            i += 1

    return {"lines": lines, "blocks": blocks}


def _render_registry_block(project_id: str, fields: dict[str, Any]) -> list[str]:
    pid = (project_id or "").strip()

    rendered: list[str] = [f"### {pid}", ""]

    for key in REGISTRY_FIELD_ORDER:
        if key == "project_id":
            value = pid
        else:
            value = fields.get(key, "")

        if key == "alias_permitidos":
            aliases = _coerce_aliases(value)
            rendered.append(f"{key}: {', '.join(aliases)}")
            continue

        v = "" if value is None else str(value)
        rendered.append(f"{key}: {v}")

    rendered.append("")
    return rendered


def _detect_registry_collisions(*, entries: list[dict[str, Any]], project_id: str, aliases: list[str]) -> dict[str, Any]:
    pid_l = (project_id or "").strip().lower()

    pid_collision = None
    for e in entries:
        ep = str(e.get("project_id") or "").strip()
        if ep and ep.lower() == pid_l:
            pid_collision = ep
            break

    alias_collisions: list[dict[str, str]] = []
    aliases_l = {a.lower() for a in aliases if a}
    for e in entries:
        ep = str(e.get("project_id") or "").strip()
        ealiases = e.get("alias_permitidos") or []
        for a in ealiases:
            if str(a).strip().lower() in aliases_l and ep.lower() != pid_l:
                alias_collisions.append({"alias": str(a).strip(), "project_id": ep})

    seen = set()
    alias_collisions_uniq = []
    for c in alias_collisions:
        key = (c.get("alias"), c.get("project_id"))
        if key in seen:
            continue
        seen.add(key)
        alias_collisions_uniq.append(c)

    return {
        "project_id_collision": bool(pid_collision),
        "project_id_collision_with": pid_collision,
        "alias_collisions": alias_collisions_uniq,
    }


def _probe_onboarding_at(*, project_id: str, docs_projects_root: Path) -> dict[str, Any]:
    pid = (project_id or "").strip()
    if not pid:
        return {"ok": True, "status": "unknown", "missing": []}

    docs_dir = docs_projects_root / pid
    missing = [name for name in PROJECT_ONBOARDING_REQUIRED_FILES if not (docs_dir / name).exists()]

    if not docs_dir.exists():
        return {"ok": True, "status": "missing", "docs_dir": str(docs_dir), "missing": PROJECT_ONBOARDING_REQUIRED_FILES}

    if missing:
        return {"ok": True, "status": "partial", "docs_dir": str(docs_dir), "missing": missing}

    return {"ok": True, "status": "ready", "docs_dir": str(docs_dir), "missing": []}


def enable_target_project(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Habilita formalmente un proyecto nuevo/no registrado (Plan-first -> Apply confirmado)."""

    arguments = arguments or {}

    mode = str(arguments.get("mode") or "plan").strip().lower()
    if mode not in {"plan", "apply"}:
        mode = "plan"

    confirm = bool(arguments.get("confirm", False))
    set_active = bool(arguments.get("set_active_project", False))

    # Optional test-only overrides
    test_mode = bool(arguments.get("test_mode", False))
    registry_path_raw = str(arguments.get("registry_path") or "").strip()
    docs_projects_root_raw = str(arguments.get("docs_projects_root") or "").strip()

    registry_path = ROOT / "PROJECT_REGISTRY.md"
    docs_projects_root = ROOT / "docs" / "projects"

    if test_mode:
        if registry_path_raw:
            cand = Path(registry_path_raw).expanduser()
            ok, err = _ensure_safe_test_path(cand)
            if not ok:
                return {"ok": True, "status": "blocked", "error": err, "mode": mode}
            registry_path = cand

        if docs_projects_root_raw:
            cand = Path(docs_projects_root_raw).expanduser()
            ok, err = _ensure_safe_test_path(cand)
            if not ok:
                return {"ok": True, "status": "blocked", "error": err, "mode": mode}
            docs_projects_root = cand

    project_id = str(arguments.get("project_id") or "").strip()
    canonical_name = str(arguments.get("nombre_canónico") or arguments.get("nombre_canonico") or "").strip() or None

    local_path_raw = str(arguments.get("local_path") or "").strip() or str(arguments.get("workspace_path") or "").strip() or None
    repo_url_raw = str(arguments.get("repo_url") or arguments.get("repositorio_remoto") or "").strip() or None

    environment_type = str(arguments.get("environment_type") or "").strip() or None
    origen = str(arguments.get("origen") or arguments.get("origin") or "").strip() or None

    aliases = _coerce_aliases(arguments.get("aliases") or arguments.get("alias_permitidos") or [])

    ok_pid, pid_err, pid_suggestion = _validate_project_id(project_id)
    if not ok_pid:
        if pid_err == "missing_project_id":
            return {
                "ok": True,
                "status": "missing_min_info",
                "mode": mode,
                "missing_fields": ["project_id"],
                "next_frontier": "provide_project_id",
                "next_question": "Indica un único project_id (kebab-case recomendado; p.ej. my-project).",
            }

        return {
            "ok": True,
            "status": "invalid_inputs",
            "mode": mode,
            "error": pid_err,
            "project_id": project_id,
            "suggested_project_id": pid_suggestion,
            "next_frontier": "provide_valid_project_id",
            "next_question": "project_id inválido. Confirma un id válido (a-z0-9._-; sin espacios).",
        }

    existing_entries, reg_warnings = _parse_registry_entries(registry_path)
    collisions = _detect_registry_collisions(entries=existing_entries, project_id=project_id, aliases=aliases)

    if collisions.get("alias_collisions"):
        return {
            "ok": True,
            "status": "alias_collision",
            "mode": mode,
            "project_id": project_id,
            "alias_collisions": collisions.get("alias_collisions"),
            "next_frontier": "resolve_alias_collision",
            "next_question": "Alias ambiguo/colisionado. Elige aliases únicos o confirma el project_id existente.",
        }

    local_probe: dict[str, Any] = {
        "provided": bool(local_path_raw),
        "path": local_path_raw,
        "exists": False,
        "git": None,
    }

    local_path_obj: Path | None = None
    if local_path_raw:
        try:
            local_path_obj = Path(local_path_raw).expanduser().resolve()
            local_probe["path"] = str(local_path_obj)
            local_probe["exists"] = bool(local_path_obj.exists() and local_path_obj.is_dir())
        except Exception:
            local_path_obj = None
            local_probe["exists"] = False

    if local_path_obj and local_probe["exists"]:
        local_probe["git"] = _git_probe_repo(local_path_obj)

    repo_url = _redact_remote_url(repo_url_raw or "") or None

    mismatch: dict[str, Any] | None = None
    if repo_url and isinstance(local_probe.get("git"), dict) and local_probe["git"].get("is_git_repo"):
        origin_remote = str(local_probe["git"].get("remote_origin") or "").strip()
        if origin_remote and _normalize_repo_url(origin_remote) != _normalize_repo_url(repo_url):
            mismatch = {
                "type": "repo_url_vs_remote_origin_mismatch",
                "repo_url": repo_url,
                "remote_origin": origin_remote,
            }

    missing_fields: list[str] = []
    if not canonical_name:
        missing_fields.append("nombre_canónico")
    if not repo_url:
        missing_fields.append("repo_url")
    if not local_path_raw:
        missing_fields.append("local_path")
    if not environment_type:
        missing_fields.append("environment_type")

    if not origen:
        if environment_type and "replit" in environment_type.lower():
            origen = "replit"
        elif local_path_raw:
            origen = "local"
        else:
            origen = "unknown"

    proposed_fields: dict[str, Any] = {
        "project_id": project_id,
        "nombre_canónico": canonical_name or "unknown",
        "alias_permitidos": aliases,
        "ruta_local": str(local_path_obj) if (local_path_obj and local_probe.get("exists")) else "",
        "repositorio_remoto": repo_url or "",
        "origen": origen or "unknown",
        "environment_type": environment_type or "unknown",
        "repo_url": repo_url or "",
        "replit_workspace_path": "",
        "replit_join_url": "",
        "local_path": str(local_path_obj) if (local_path_obj and local_probe.get("exists")) else "null",
        "stack_detectado": "unknown",
        "documentación_principal": "",
        "código_fuente_relevante": "",
        "estado_sincronización": "unknown",
        "alertas_críticas": "",
        "lecciones_locales": "",
        "último_análisis": "",
        "responsable": "unknown",
    }

    entry_exists = bool(collisions.get("project_id_collision"))

    safe_to_apply = True
    blockers: list[str] = []

    if mismatch:
        safe_to_apply = False
        blockers.append(mismatch["type"])

    registry_preview = {
        "registry_path": str(registry_path),
        "would_create": not entry_exists,
        "would_update": entry_exists,
        "entry_markdown": "\n".join(_render_registry_block(project_id, proposed_fields)).rstrip() + "\n",
    }

    scaffold_preview = {
        "docs_projects_root": str(docs_projects_root),
        "docs_dir": str(docs_projects_root / project_id),
        "required_files": PROJECT_ONBOARDING_REQUIRED_FILES,
        "onboarding": _probe_onboarding_at(project_id=project_id, docs_projects_root=docs_projects_root),
    }

    if mode == "plan":
        status = "plan_ready" if safe_to_apply else "plan_blocked"
        next_frontier = "apply_confirmed" if safe_to_apply else "resolve_blockers"

        return {
            "ok": True,
            "status": status,
            "mode": mode,
            "project_id": project_id,
            "warnings": reg_warnings,
            "inputs": {
                "nombre_canónico": canonical_name,
                "aliases": aliases,
                "repo_url": repo_url,
                "local_path": local_probe.get("path"),
                "environment_type": environment_type,
                "origen": origen,
            },
            "missing_fields": missing_fields,
            "collisions": collisions,
            "local_probe": local_probe,
            "mismatch": mismatch,
            "safe_to_apply": safe_to_apply,
            "blockers": blockers,
            "registry": registry_preview,
            "scaffold": scaffold_preview,
            "next_frontier": next_frontier,
            "next_question": "Confirma Apply (confirm=true) para registrar y crear scaffold." if safe_to_apply else "Hay bloqueos; corrige inputs antes de Apply.",
        }

    if not confirm:
        return {
            "ok": True,
            "status": "confirmation_required",
            "mode": mode,
            "project_id": project_id,
            "safe_to_apply": safe_to_apply,
            "blockers": blockers,
            "next_frontier": "confirm_apply",
            "next_question": "Para aplicar, reintenta con confirm=true (Apply confirmado).",
        }

    if not safe_to_apply:
        return {
            "ok": True,
            "status": "blocked",
            "mode": mode,
            "project_id": project_id,
            "blockers": blockers,
            "mismatch": mismatch,
            "next_frontier": "resolve_blockers",
            "next_question": "No se aplicó: hay inconsistencias (p.ej. repo_url vs remote origin). Corrige/confirm inputs y reintenta.",
        }

    try:
        current_text = registry_path.read_text(encoding="utf-8", errors="replace") if registry_path.exists() else ""
    except Exception as exc:
        return {"ok": False, "status": "error", "mode": mode, "error": f"registry_read_failed:{exc}", "project_id": project_id}

    parsed = _parse_registry_blocks(current_text)
    lines: list[str] = parsed.get("lines") or []
    blocks_list: list[dict[str, Any]] = parsed.get("blocks") or []

    existing_block = None
    for b in blocks_list:
        if str(b.get("project_id") or "").strip().lower() == project_id.lower():
            existing_block = b
            break

    registry_action = "created"
    registry_changed = False
    conflicts: list[dict[str, Any]] = []

    if existing_block:
        registry_action = "updated"
        merged = dict(existing_block.get("fields") or {})

        merged_aliases = _coerce_aliases(merged.get("alias_permitidos") or [])
        for a in aliases:
            if a not in merged_aliases:
                merged_aliases.append(a)
        merged["alias_permitidos"] = merged_aliases

        for k, v in proposed_fields.items():
            if k == "alias_permitidos":
                continue
            existing_val = merged.get(k)
            if _is_nullish(existing_val):
                merged[k] = v
            else:
                if not _is_nullish(v) and str(existing_val).strip() != str(v).strip():
                    conflicts.append({"field": k, "existing": existing_val, "proposed": v})

        if conflicts:
            return {
                "ok": True,
                "status": "registry_conflict",
                "mode": mode,
                "project_id": project_id,
                "conflicts": conflicts[:10],
                "next_frontier": "resolve_registry_conflict",
                "next_question": "No se aplicó: el project_id ya existe con valores distintos. Resuelve manualmente o usa un nuevo project_id.",
            }

                
        new_block_lines = _render_registry_block(project_id, merged)
        start = int(existing_block.get("start") or 0)

        end = int(existing_block.get("end") or start)
        lines = lines[:start] + new_block_lines + lines[end:]
    else:
        registry_action = "created"
        new_block_lines = _render_registry_block(project_id, proposed_fields)
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend(new_block_lines)

    # Determinar cambio real sobre el texto final normalizado (evita falsos positivos
    # por diferencias solo en trailing whitespace/blank lines).
    old_text_norm = (current_text or "").rstrip() + "\n"
    new_text = "\n".join(lines).rstrip() + "\n"
    registry_changed = new_text != old_text_norm

    if registry_changed:
        try:
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            registry_path.write_text(new_text, encoding="utf-8")
        except Exception as exc:
            return {"ok": False, "status": "error", "mode": mode, "error": f"registry_write_failed:{exc}", "project_id": project_id}


    scaffold_res = init_project_onboarding_scaffold(
        {
            "project_id": project_id,
            "dry_run": False,
            "test_mode": test_mode,
            "registry_path": str(registry_path) if test_mode else "",
            "docs_projects_root": str(docs_projects_root) if test_mode else "",
        }
    )

    active_project_set = None
    if set_active:
        active_project_set = set_active_project({"project_id": project_id, "note": "enable_target_project"})

    return {
        "ok": True,
        "status": "applied",
        "mode": mode,
        "project_id": project_id,
        "registry": {
            "registry_path": str(registry_path),
            "action": registry_action,
            "changed": registry_changed,
        },
        "scaffold": scaffold_res,
        "active_project_set": active_project_set,
        "next_frontier": "project_enabled",
        "next_question": None,
    }


PROJECT_ONBOARDING_REQUIRED_FILES = [
    # Perfil + retoma (memoria operativa mínima, versionada)
    "PROJECT_PROFILE.md",
    "PROJECT_RESUME.md",
    "CURRENT_FRONTIER.md",
    "ERRORS_AND_FIXES.md",

    # Índices / auditoría / alertas (operación por referencias)
    "CONTEXT_INDEX.md",
    "SEMANTIC_TAG_INDEX.md",
    "CODE_CONTEXT_MAP.md",
    "DOCUMENTATION_AUDIT.md",
    "CRITICAL_ALERTS.md",
    "LESSONS_LOCAL.md",
    "SYNC_STATUS.md",
    "HANDOFF_LOG.md",
]



def _probe_project_onboarding(project_id: str) -> dict[str, Any]:
    pid = (project_id or "").strip()
    if not pid:
        return {"ok": True, "status": "unknown", "project_id": None, "docs_dir": None, "missing": []}

    if pid == "orchestrator":
        return {"ok": True, "status": "not_applicable", "project_id": pid, "docs_dir": None, "missing": []}

    docs_dir = ROOT / "docs" / "projects" / pid

    missing = [name for name in PROJECT_ONBOARDING_REQUIRED_FILES if not (docs_dir / name).exists()]

    if not docs_dir.exists():
        return {
            "ok": True,
            "status": "missing",
            "project_id": pid,
            "docs_dir": str(docs_dir),
            "missing": PROJECT_ONBOARDING_REQUIRED_FILES,
        }

    if missing:
        return {
            "ok": True,
            "status": "partial",
            "project_id": pid,
            "docs_dir": str(docs_dir),
            "missing": missing,
        }

    return {"ok": True, "status": "ready", "project_id": pid, "docs_dir": str(docs_dir), "missing": []}


def _extract_markdown_heading_ids(*, path: Path, prefix: str, max_ids: int = 8, max_chars: int = 24000) -> list[str]:
    """Extrae IDs desde headings tipo '### ALERT-...' de un Markdown (best-effort)."""

    txt = _read_text_prefix(path, max_chars=max_chars)
    if not txt:
        return []

    ids: list[str] = []
    # Soporta '### ALERT-GLOBAL-001 — ...'
    pat = re.compile(r"^###\s+([A-Z0-9_-]+)", flags=re.MULTILINE)
    for m in pat.finditer(txt):
        cand = (m.group(1) or "").strip()
        if cand.startswith(prefix) and cand not in ids:
            ids.append(cand)
        if len(ids) >= max_ids:
            break

    return ids


def _build_standard_project_context_pack(
    *,
    project_id: str,
    level: int,
    preview_chars: int = 900,
) -> dict[str, Any]:
    """Construye un context pack estándar (reference-based) por niveles.

    Nota: no carga evidencia pesada (runs/TRACE/raw_outputs), solo referencias + previews cortos.
    """

    pid = (project_id or "").strip()
    if not pid:
        return {"ok": True, "status": "missing_inputs", "error": "project_id_missing"}

    # Nivel permitido: 0..3 (alineado a Bloque 3). Clampear por seguridad.
    try:
        lvl = int(level)
    except Exception:
        lvl = 1
    lvl = max(0, min(lvl, 3))

    onboarding = _probe_project_onboarding(pid)
    if onboarding.get("status") in {"missing", "partial"}:
        missing = onboarding.get("missing") if isinstance(onboarding.get("missing"), list) else []
        return {
            "ok": True,
            "status": "onboarding_required",
            "project_id": pid,
            "level": lvl,
            "onboarding": onboarding,
            "missing_files": missing,
            "recommended_next_tool_call": {
                "tool": "init_project_onboarding_scaffold",
                "arguments": {"project_id": pid, "dry_run": False},
            },
        }

    # Session last_event (efímero, gitignored) si coincide con proyecto activo.
    session_last_event: dict[str, Any] | None = None
    st = _read_json_file(ACTIVE_PROJECT_PATH) or {}
    if isinstance(st, dict) and str(st.get("project_id") or "").strip() == pid:
        le = st.get("last_event")
        if isinstance(le, dict):
            session_last_event = {
                "updated_at": le.get("updated_at"),
                "source": le.get("source"),
                "mode": le.get("mode"),
                "status": le.get("status"),
                "next_frontier": le.get("next_frontier"),
                "run_id": le.get("run_id"),
                "handoff_json_path": le.get("handoff_json_path"),
                "instruction_preview": _safe_preview_text(le.get("instruction"), limit=180),
                "next_question_preview": _safe_preview_text(le.get("next_question"), limit=220),
            }

    global_alerts_path = ROOT / "docs" / "alerts" / "GLOBAL_CRITICAL_ALERTS.md"
    global_alert_ids = _extract_markdown_heading_ids(path=global_alerts_path, prefix="ALERT-", max_ids=8)

    exclusions = [
        "docs/agent_runs/**",
        "docs/agent_queue/**",
        "raw_outputs/**",
        "TRACE.md (full)",
        "RUN_SUMMARY.md (full)",
        "handoffs completos (*.md)",
    ]

    # Proyecto orquestador: no aplica carpeta docs/projects/<pid>/ como contrato de objetivo.
    if pid == "orchestrator":
        return {
            "ok": True,
            "status": "ok",
            "project_id": pid,
            "level": lvl,
            "reference_based": True,
            "onboarding": onboarding,
            "session_last_event": session_last_event,
            "alerts": {
                "global": {
                    "path": str(global_alerts_path),
                    "exists": bool(global_alerts_path.exists()),
                    "alert_ids_preview": global_alert_ids,
                }
            },
            "refs": [
                {"role": "reference_map", "path": "docs/context/REFERENCE_MAP.md"},
                {"role": "routing", "path": "MODEL_ROUTING.md"},
                {"role": "orchestration", "path": "AGENT_ORCHESTRATION.md"},
                {"role": "continue_usage", "path": "CONTINUE_USAGE_PROTOCOL.md"},
            ],
            "exclusions": exclusions,
        }

    docs_dir = ROOT / "docs" / "projects" / pid

    def _file_ref(*, name: str, role: str, include_preview: bool) -> dict[str, Any]:
        path = docs_dir / name
        preview = None
        if include_preview:
            preview = _read_text_prefix(path, max_chars=preview_chars)
            if preview:
                preview = preview.replace("\r\n", "\n").strip()
        return {
            "role": role,
            "path": str(path),
            "exists": bool(path.exists()),
            "preview": preview,
            "preview_truncated": bool(preview and len(preview) >= preview_chars),
        }

    refs: list[dict[str, Any]] = []

    # Nivel 0: retoma rápida
    if lvl >= 0:
        refs.extend(
            [
                _file_ref(name="PROJECT_RESUME.md", role="project_resume", include_preview=True),
                _file_ref(name="CURRENT_FRONTIER.md", role="current_frontier", include_preview=True),
            ]
        )

    # Nivel 1: contexto operativo default
    if lvl >= 1:
        refs.extend(
            [
                _file_ref(name="ERRORS_AND_FIXES.md", role="errors_and_fixes", include_preview=True),
                _file_ref(name="CRITICAL_ALERTS.md", role="critical_alerts_local", include_preview=True),
                _file_ref(name="LESSONS_LOCAL.md", role="lessons_local", include_preview=True),
                _file_ref(name="HANDOFF_LOG.md", role="handoff_log", include_preview=True),
                _file_ref(name="SYNC_STATUS.md", role="sync_status", include_preview=True),
            ]
        )

    # Nivel 2: evidencia referenciada (índices por proyecto + global indexes)
    if lvl >= 2:
        refs.extend(
            [
                _file_ref(name="CONTEXT_INDEX.md", role="context_index", include_preview=True),
                _file_ref(name="CODE_CONTEXT_MAP.md", role="code_context_map", include_preview=True),
                _file_ref(name="DOCUMENTATION_AUDIT.md", role="documentation_audit", include_preview=True),
            ]
        )

    indexes = {
        "reference_map": "docs/context/REFERENCE_MAP.md",
        "action_index": "docs/context/ACTION_INDEX.md",
        "decision_index": "docs/context/DECISION_INDEX.md",
        "run_index": "docs/context/RUN_INDEX.md",
        "return_index": "docs/returns/RETURN_INDEX.md",
    }

    local_alerts_path = docs_dir / "CRITICAL_ALERTS.md"
    local_alert_ids = _extract_markdown_heading_ids(path=local_alerts_path, prefix="ALERT-", max_ids=6) if local_alerts_path.exists() else []

    return {
        "ok": True,
        "status": "ok",
        "project_id": pid,
        "level": lvl,
        "reference_based": True,
        "onboarding": onboarding,
        "session_last_event": session_last_event,
        "alerts": {
            "global": {
                "path": str(global_alerts_path),
                "exists": bool(global_alerts_path.exists()),
                "alert_ids_preview": global_alert_ids,
            },
            "local": {
                "path": str(local_alerts_path),
                "exists": bool(local_alerts_path.exists()),
                "alert_ids_preview": local_alert_ids,
            },
        },
        "refs": refs,
        "global_indexes": indexes,
        "exclusions": exclusions,
        "level_3_note": (
            "Nivel 3 implica investigación profunda bajo necesidad explícita; "
            "usar compact-first y elevar a fragmentos específicos antes de abrir evidencia amplia."
        ),
    }


def _get_context_pack_ref_by_role(context_pack: dict[str, Any], role: str) -> dict[str, Any] | None:
    refs = context_pack.get("refs") if isinstance(context_pack, dict) else None
    if not isinstance(refs, list):
        return None
    for r in refs:
        if isinstance(r, dict) and str(r.get("role") or "") == role:
            return r
    return None


def _looks_like_stub_markdown(text: str | None) -> bool:
    t = (text or "").strip().lower()
    if not t:
        return True

    stub_markers = (
        "(pendiente)",
        "instruction_summary: (1 línea",
        "instruction_summary: (1 linea",
        "next_action: (1 línea",
        "next_action: (1 linea",
        "status: `unknown",
        "status: unknown",
    )
    return any(m in t for m in stub_markers)


def _parse_current_frontier_preview(preview: str | None) -> dict[str, Any]:
    t = (preview or "").replace("\r\n", "\n")
    out: dict[str, Any] = {
        "status": None,
        "blocking_threshold": None,
        "next_action": None,
        "requires_user_action": None,
    }

    def _extract(pattern: str) -> str | None:
        m = re.search(pattern, t, flags=re.IGNORECASE | re.MULTILINE)
        if not m:
            return None
        v = (m.group(1) or "").strip()
        return v or None

    out["status"] = _extract(r"^-\s*status:\s*`?([^`\n]+)`?\s*$")
    out["blocking_threshold"] = _extract(r"^-\s*blocking_threshold:\s*`?([^`\n]+)`?\s*$")
    out["next_action"] = _extract(r"^-\s*next_action:\s*(.+?)\s*$")
    out["requires_user_action"] = _extract(r"^-\s*requires_user_action:\s*(.+?)\s*$")

    return out


def _analyze_resume_from_context_pack(*, context_pack: dict[str, Any], instruction_normalized: str) -> dict[str, Any]:
    """Analiza memoria versionada (previews) para decidir si se requiere executor/handoff."""

    versioned_memory = context_pack.get("versioned_memory") if isinstance(context_pack, dict) else None
    extracts = versioned_memory.get("extracts") if isinstance(versioned_memory, dict) else None
    previews = versioned_memory.get("previews") if isinstance(versioned_memory, dict) else None

    frontier_ref = _get_context_pack_ref_by_role(context_pack, "current_frontier") or {}
    resume_ref = _get_context_pack_ref_by_role(context_pack, "project_resume") or {}

    frontier_extract = extracts.get("current_frontier") if isinstance(extracts, dict) else None
    resume_extract = extracts.get("project_resume") if isinstance(extracts, dict) else None

    frontier_preview = None
    resume_preview = None
    if isinstance(previews, dict):
        frontier_preview = previews.get("current_frontier_preview")
        resume_preview = previews.get("project_resume_preview")
    if frontier_preview is None and isinstance(frontier_ref, dict):
        frontier_preview = frontier_ref.get("preview")
    if resume_preview is None and isinstance(resume_ref, dict):
        resume_preview = resume_ref.get("preview")

    frontier = frontier_extract if isinstance(frontier_extract, dict) else _parse_current_frontier_preview(str(frontier_preview or ""))

    blocking = str(frontier.get("blocking_threshold") or "").strip().lower()
    blocked = bool(blocking and blocking not in {"none", "unknown"})

    next_action = str(frontier.get("next_action") or "").strip()

    reasons: list[str] = []
    needs_executor = False
    next_question = None

    if blocked:
        reasons.append(f"blocked_by_threshold:{blocking}")
        next_question = (
            f"Según CURRENT_FRONTIER.blocking_threshold=`{blocking}`, se requiere una decisión/autorización para avanzar. "
            "¿Autorizas/desbloqueas ese umbral?"
        )
    else:
        frontier_is_stub = not any(frontier.values()) and _looks_like_stub_markdown(str(frontier_preview or ""))
        resume_has_fields = isinstance(resume_extract, dict) and any(resume_extract.values())
        resume_is_stub = not resume_has_fields and _looks_like_stub_markdown(str(resume_preview or ""))

        if frontier_is_stub and resume_is_stub:
            needs_executor = True
            reasons.append("memory_stub")
        elif not next_action or _looks_like_stub_markdown(next_action):
            needs_executor = True
            reasons.append("missing_next_action")
        elif re.search(r"\b(context-validator|planner|debugger|builder|opencode)\b", next_action, flags=re.IGNORECASE):
            needs_executor = True
            reasons.append("next_action_mentions_executor")

    if ("siguiente frontera" in instruction_normalized) or instruction_normalized.startswith("avanza") or ("avanza con" in instruction_normalized):
        reasons.append("advance_language")

    return {
        "blocked": blocked,
        "blocking_threshold": blocking or None,
        "needs_executor": bool(needs_executor),
        "reasons": reasons,
        "next_action": next_action or None,
        "next_question": next_question,
        "frontier": frontier,
    }


def init_project_onboarding_scaffold(arguments: dict[str, Any] | None = None) -> dict[str, Any]:

    """Crea (si falta) el scaffold documental mínimo en docs/projects/<project-id>/.

    Objetivo: iniciar onboarding sin copiar chats completos ni volcar artefactos.

    Restricciones:
    - Solo escribe dentro del repo del orquestador (docs/projects/*).
    - No lee ni modifica proyectos externos.
    - No sobrescribe archivos existentes.
    """

    arguments = arguments or {}

    project_id = (arguments.get("project_id") or "").strip()
    if not project_id:
        return {"ok": False, "status": "error", "error": "project_id es obligatorio."}

    dry_run = bool(arguments.get("dry_run", False))

    # Optional test-only overrides (used by enable_target_project tests)
    test_mode = bool(arguments.get("test_mode", False))
    registry_path_raw = str(arguments.get("registry_path") or "").strip()
    docs_projects_root_raw = str(arguments.get("docs_projects_root") or "").strip()

    docs_projects_root = ROOT / "docs" / "projects"

    if test_mode and docs_projects_root_raw:
        cand = Path(docs_projects_root_raw).expanduser()
        ok, err = _ensure_safe_test_path(cand)
        if not ok:
            return {"ok": False, "status": "error", "error": err}
        docs_projects_root = cand

    docs_dir = docs_projects_root / project_id

    created: list[str] = []
    skipped: list[str] = []

    # Metadata best-effort desde registry (si existe)
    registry_path = ROOT / "PROJECT_REGISTRY.md"

    if test_mode and registry_path_raw:
        cand = Path(registry_path_raw).expanduser()
        ok, err = _ensure_safe_test_path(cand)
        if not ok:
            return {"ok": False, "status": "error", "error": err}
        registry_path = cand

    entries, _warnings = _parse_registry_entries(registry_path)

    resolved = _resolve_by_query(project_id, entries) if entries else {"ok": False}
    entry = resolved.get("entry") if isinstance(resolved, dict) else None

    nombre = (entry.get("nombre_canónico") if isinstance(entry, dict) else None) or "unknown"
    repo_url = (entry.get("repo_url") if isinstance(entry, dict) else None) or (entry.get("repositorio_remoto") if isinstance(entry, dict) else None) or ""
    repo_url = _redact_remote_url(repo_url)

    templates: dict[str, str] = {
                "PROJECT_PROFILE.md": (
            f"# PROJECT_PROFILE — {project_id}\n\n"
            f"- project_id: `{project_id}`\n"
            f"- nombre_canónico: `{nombre}`\n"
            f"- repo_url: `{repo_url or 'unknown'}`\n\n"
            "## Objetivo\n\n"
            "(Completar: descripción corta del proyecto y su propósito.)\n\n"
            "## Fuentes primarias (referencias)\n\n"
            "- `PROJECT_REGISTRY.md` (entrada del proyecto)\n"
            "- README/docs del proyecto objetivo (si existen)\n"
        ),

        "PROJECT_RESUME.md": (
            f"# PROJECT_RESUME — {project_id}\n\n"
            "Vista compacta para retomar el proyecto sin depender del chat ni de `.orchestrator_state/`.\n\n"
            "Reglas:\n"
            "- No pegar artefactos voluminosos (TRACE/RUN_SUMMARY/raw_outputs).\n"
            "- Operar por referencias: run_id + rutas + conteos + previews cortos.\n"
            "- Evidencia pesada es operacional y no se versiona por defecto (ver `.gitignore` y `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`).\n\n"
            "## 1) Qué es este proyecto\n\n"
            "- (1–3 líneas)\n\n"
            "## 2) Dónde está el repo (local/remoto)\n\n"
            "- repo_url: (referencia; no secrets)\n"
            "- local_path: (si aplica; puede vivir en PROJECT_REGISTRY.md)\n"
            "- branch: (última conocida)\n"
            "- last_commit: (hash corto + mensaje)\n\n"
            "## 3) Estado actual conocido\n\n"
            "- status_classification: `unknown|listo|parcialmente_listo|no_listo`\n"
            "- last_synced: (ver `SYNC_STATUS.md`)\n\n"
            "## 4) Frontera actual\n\n"
            "- Ver: `CURRENT_FRONTIER.md`\n\n"
            "## 5) Última decisión relevante\n\n"
            "- decision_ref: (ruta a `docs/decisions/**` o resumen 1 línea + referencia)\n\n"
            "## 6) Riesgos/alertas aplicables\n\n"
            "- Global: `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`\n"
            "- Local: `CRITICAL_ALERTS.md`\n\n"
            "## 7) Handoffs / runs / returns relevantes\n\n"
            "- Handoffs: `HANDOFF_LOG.md`\n"
            "- Runs: `docs/context/RUN_INDEX.md` + (entradas locales en `CONTEXT_INDEX.md`)\n"
            "- Returns: `docs/returns/RETURN_INDEX.md` (y archivos referenciados)\n\n"
            "## 8) Errores/fixes reutilizables\n\n"
            "- Ver: `ERRORS_AND_FIXES.md`\n\n"
            "## 9) Qué consultar antes de actuar\n\n"
            "- `PROJECT_PROFILE.md`\n"
            "- `CURRENT_FRONTIER.md`\n"
            "- `CRITICAL_ALERTS.md`\n"
            "- `LESSONS_LOCAL.md`\n"
            "- `CONTEXT_INDEX.md` + `DOCUMENTATION_AUDIT.md` + `CODE_CONTEXT_MAP.md`\n\n"
            "## 10) Qué no repetir\n\n"
            "- (errores recurrentes + referencia a fixes/lecciones; 3–7 bullets)\n"
        ),

                "CURRENT_FRONTIER.md": (
            f"# CURRENT_FRONTIER — {project_id}\n\n"
            "Semántica (obligatoria): este documento registra el punto de **cierre, continuidad o bloqueo justificado**\n"
            "tras intentar cumplir la instrucción del usuario de forma integral.\n\n"
            "No es:\n"
            "- una lista de microtareas;\n"
            "- una excusa para detener la instrucción antes de agotarla;\n"
            "- una autorización implícita de pedir microaprobaciones.\n\n"
            "Sí es:\n"
            "- un registro de hasta dónde se avanzó de forma segura;\n"
            "- qué se completó, qué falta y qué umbral impide avanzar más.\n\n"
            "Reglas:\n"
            "- No pegar dumps/logs; referenciar por `run_id`, rutas y commits.\n"
            "- Registrar solo hitos reutilizables (no cada interacción).\n\n"
            f"- last_updated: `{_now_iso()}`\n"
            "- status: `unknown|in_progress|blocked|done|superseded`\n\n"
            "## Instrucción/objetivo que se intentó agotar\n\n"
            "- instruction_summary: (1 línea; qué pidió el usuario)\n"
            "- attempted_scope: (qué se intentó hacer dentro de Plan/Build)\n\n"
            "## Resultado hasta el umbral\n\n"
            "- completed: (3–7 bullets)\n"
            "- remaining: (3–7 bullets)\n\n"
            "## Umbral que impide avanzar más (si aplica)\n\n"
            "- blocking_threshold: `none|authorization_required|risk|ambiguity|missing_min_info|secrets|db_migrations|deployment_infra|premium_replit_not_authorized|irreversible|git_conflict|out_of_scope`\n"
            "- why_blocked: (1–3 bullets; evidencia mínima por referencias)\n\n"
            "## Próxima acción recomendada (única)\n\n"
            "- next_action: (1 línea)\n"
            "- requires_user_action: (sí/no; cuál)\n"
            "- suggested_agent: (p.ej. context-validator / planner)\n"
            "- suggested_model_line: (p.ej. Go)\n\n"
            "## Referencias\n\n"
            "- decision_refs: (rutas a `docs/decisions/**`)\n"
            "- run_refs: (run_id + rutas; ver `docs/context/RUN_INDEX.md`)\n"
            "- handoff_refs: (rutas; ver `HANDOFF_LOG.md`)\n"
            "- return_refs: (rutas; ver `docs/returns/RETURN_INDEX.md`)\n"
        ),


        "ERRORS_AND_FIXES.md": (
            f"# ERRORS_AND_FIXES — {project_id}\n\n"
            "Registro compacto de errores técnicos relevantes y su fix, para evitar repetición.\n\n"
            "Reglas:\n"
            "- No pegar logs completos. Guardar solo: síntoma → causa → fix → referencia.\n"
            "- Referenciar por run_id, paths, commits y (si aplica) issue/PR.\n\n"
            "## Tabla\n\n"
            "| error_id | date | symptom | root_cause | fix_summary | refs (run_id/paths/commit) | prevention |\n"
            "|---|---|---|---|---|---|---|\n"
            "| ERR-0001 | YYYY-MM-DD | (1 línea) | (1 línea) | (1 línea) | (refs) | (1 línea) |\n"
        ),

        "CONTEXT_INDEX.md": (

            f"# CONTEXT_INDEX — {project_id}\n\n"
            "Índice de contexto por referencias (ver `docs/context/REFERENCE_BASED_CONTEXT_PROTOCOL.md`).\n\n"
            "## Documentación encontrada\n\n- (pendiente)\n\n"
            "## Índice semántico\n\n- Ver: `SEMANTIC_TAG_INDEX.md`\n\n"
            "## Decisiones relevantes\n\n- (pendiente)\n\n"
            "## Runs / evidencia\n\n- (pendiente; referenciar por run_id + rutas)\n"
        ),
        "SEMANTIC_TAG_INDEX.md": (
            f"# SEMANTIC_TAG_INDEX — {project_id}\n\n"
            "Índice canónico de etiquetas semánticas del proyecto.\n\n"
            "Reglas:\n"
            "- No pegar dumps/logs; usar rutas y referencias.\n"
            "- No duplicar documentación fuente; apuntar a ella.\n"
            "- Actualizar solo cuando un avance cambie contexto reutilizable.\n\n"
            "## Tags\n\n"
            "- (pendiente; generar/actualizar con `scripts/project_context_indexer.py`)\n"
        ),
        "CODE_CONTEXT_MAP.md": (
            f"# CODE_CONTEXT_MAP — {project_id}\n\n"
            "Mapa inicial (estructura/entrypoints/rutas).\n\n"
            "- Estructura: (pendiente)\n"
            "- Entrypoints: (pendiente)\n"
            "- Archivos sensibles: (pendiente)\n"
        ),
        "DOCUMENTATION_AUDIT.md": (
            f"# DOCUMENTATION_AUDIT — {project_id}\n\n"
            "Contraste documentación ↔ código (ver `docs/protocols/DOCUMENTATION_CODE_ALIGNMENT_PROTOCOL.md`).\n\n"
            "## Documentos vigentes\n- (pendiente)\n\n"
            "## Documentos obsoletos/incertos\n- (pendiente)\n"
        ),
        "CRITICAL_ALERTS.md": (
            f"# CRITICAL_ALERTS — {project_id}\n\n"
            "Alertas críticas locales del proyecto (ver `docs/alerts/GLOBAL_CRITICAL_ALERTS.md`).\n\n"
            "- (pendiente)\n"
        ),
        "LESSONS_LOCAL.md": (
            f"# LESSONS_LOCAL — {project_id}\n\n"
            "Lecciones locales (no confundir con `docs/lessons/GLOBAL_LESSONS_LEARNED.md`).\n\n"
            "- (pendiente)\n"
        ),
        "SYNC_STATUS.md": (
            f"# SYNC_STATUS — {project_id}\n\n"
            "Estado de sincronización (local/remoto/Replit) — sin incluir secrets.\n\n"
            f"- last_updated: `{_now_iso()}`\n"
            "- status: `unknown`\n"
        ),
        "HANDOFF_LOG.md": (
            f"# HANDOFF_LOG — {project_id}\n\n"
            "Registro de handoffs por referencias (no pegar chats completos).\n\n"
            "- (pendiente)\n"
        ),
    }

    if not dry_run:
        docs_dir.mkdir(parents=True, exist_ok=True)


    # Guardrail: evitar deriva entre la lista canónica y los templates.
    missing_templates = [name for name in PROJECT_ONBOARDING_REQUIRED_FILES if name not in templates]
    extra_templates = [name for name in templates.keys() if name not in PROJECT_ONBOARDING_REQUIRED_FILES]
    if missing_templates or extra_templates:
        return {
            "ok": False,
            "status": "error",
            "error": "scaffold_template_mismatch",
            "project_id": project_id,
            "missing_templates": missing_templates,
            "extra_templates": extra_templates,
        }

    # Crear en orden canónico, para estabilidad y trazabilidad.
    for filename in PROJECT_ONBOARDING_REQUIRED_FILES:
        content = templates[filename]
        path = docs_dir / filename
        if path.exists():
            skipped.append(str(path))
            continue
        if dry_run:
            created.append(str(path))
            continue
        path.write_text(content, encoding="utf-8")
        created.append(str(path))

    return {
        "ok": True,
        "status": "ok",
        "project_id": project_id,
        "dry_run": dry_run,
        "docs_dir": str(docs_dir),
        "created": created,
        "skipped": skipped,
        "next": "Revisar/llenar los stubs por referencias; luego ejecutar context-validator/planner según la tarea.",
    }



# --- Strategic resume sync (session last_event -> project docs) ---

AUTO_LAST_EVENT_START = "<!-- AUTO:last_event_refs:start -->"
AUTO_LAST_EVENT_END = "<!-- AUTO:last_event_refs:end -->"

# Keep blocks small and reference-based.
MAX_AUTO_BLOCK_CHARS = 1400


def _redact_possible_secrets(text: str) -> str:
    """Redacta patrones comunes de secrets en texto libre (best-effort)."""

    t = str(text or "")
    if not t:
        return ""

    # Common token formats
    t = re.sub(r"\bghp_[A-Za-z0-9]{20,}\b", "ghp_<redacted>", t)
    t = re.sub(r"\bsk-[A-Za-z0-9]{16,}\b", "sk-<redacted>", t)
    t = re.sub(r"\bAIza[0-9A-Za-z\-_]{16,}\b", "AIza<redacted>", t)

    # key=value like patterns
    t = re.sub(
        r"(?i)\b(token|api[_-]?key|secret|password)\s*[:=]\s*([^\s]+)",
        lambda m: f"{m.group(1)}=<redacted>",
        t,
    )

    return t


def _load_active_project_state() -> dict[str, Any]:
    """Carga el estado de sesión local (gitignored) sin side-effects."""

    data = _read_json_file(ACTIVE_PROJECT_PATH)
    return {
        "ok": True,
        "exists": bool(data),
        "path": str(ACTIVE_PROJECT_PATH),
        "active_project": data if isinstance(data, dict) else None,
    }


def _ensure_orchestrator_state_gitignored() -> tuple[bool, str | None]:
    """Verifica que .orchestrator_state/ esté en .gitignore."""

    try:
        gi = (ROOT / ".gitignore").read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return False, f"No se pudo leer .gitignore: {exc}"

    if ".orchestrator_state/" not in gi:
        return False, ".orchestrator_state/ no está presente en .gitignore (guardrail)"

    return True, None


def _parse_table_rows(md: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for raw in (md or "").splitlines():
        line = raw.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        # Skip header/separator rows
        if set(line.replace("|", "").strip()) <= {"-", " "}:
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if parts:
            rows.append(parts)
    return rows


def _extract_deterministic_index_matches(*, project_id: str) -> dict[str, Any]:
    """Extrae matches determinísticos por project_id explícito en filas."""

    pid = (project_id or "").strip()
    out: dict[str, Any] = {
        "project_id": pid,
        "decision_ids": [],
        "action_ids": [],
        "return_files": [],
        "linked_decisions": [],
    }

    if not pid:
        return out

    # DECISION_INDEX: detectar decisiones de escalamiento con columna target_project.
    try:
        dec = (ROOT / "docs" / "context" / "DECISION_INDEX.md").read_text(encoding="utf-8", errors="replace")
        rows = _parse_table_rows(dec)
        for r in rows:
            if any(c.strip() == pid for c in r):
                if r and r[0] and (r[0].startswith("DEC-") or r[0].startswith("ESC-")):
                    out["decision_ids"].append(r[0])
        out["decision_ids"] = out["decision_ids"][:5]
    except Exception:
        pass

    # ACTION_INDEX: no tiene columna project_id; solo capturar si pid aparece explícitamente en una fila.
    try:
        act = (ROOT / "docs" / "context" / "ACTION_INDEX.md").read_text(encoding="utf-8", errors="replace")
        rows = _parse_table_rows(act)
        for r in rows:
            if any(pid in c for c in r):
                if r and re.match(r"^ACT-\d{4}$", r[0] or ""):
                    out["action_ids"].append(r[0])
        out["action_ids"] = out["action_ids"][:5]
    except Exception:
        pass

    # RETURN_INDEX: tabla incluye target_project.
    try:
        ret = (ROOT / "docs" / "returns" / "RETURN_INDEX.md").read_text(encoding="utf-8", errors="replace")
        rows = _parse_table_rows(ret)
        for r in rows:
            if len(r) >= 3 and r[1].strip() == pid:
                return_file = (r[2] or "").strip()
                if return_file:
                    out["return_files"].append(return_file.strip("`"))
                if len(r) >= 7:
                    linked = (r[6] or "").strip()
                    if linked:
                        out["linked_decisions"].append(linked.strip("`"))
        out["return_files"] = out["return_files"][:5]
        out["linked_decisions"] = out["linked_decisions"][:5]
    except Exception:
        pass

    return out


def _extract_last_event_refs(*, active_project: dict[str, Any], project_id: str) -> dict[str, Any]:
    last_event = active_project.get("last_event") if isinstance(active_project, dict) else None
    last_event = last_event if isinstance(last_event, dict) else {}

    instruction = _redact_possible_secrets(str(last_event.get("instruction") or "").strip())
    next_q = _redact_possible_secrets(str(last_event.get("next_question") or "").strip())

    run_id = str(last_event.get("run_id") or "").strip() or None
    handoff_json_path = str(last_event.get("handoff_json_path") or "").strip() or None

    idx_matches = _extract_deterministic_index_matches(project_id=project_id)

    return {
        "project_id": project_id,
        "updated_at": str(last_event.get("updated_at") or "").strip() or None,
        "source": str(last_event.get("source") or "").strip() or None,
        "mode": str(last_event.get("mode") or "").strip() or None,
        "instruction_preview": _safe_preview_text(instruction, limit=180) if instruction else None,
        "status": str(last_event.get("status") or "").strip() or None,
        "next_frontier": str(last_event.get("next_frontier") or "").strip() or None,
        "next_question_preview": _safe_preview_text(next_q, limit=220) if next_q else None,
        "run_id": run_id,
        "handoff_json_path": handoff_json_path,
        "global_indexes": {
            "action_index": "docs/context/ACTION_INDEX.md",
            "decision_index": "docs/context/DECISION_INDEX.md",
            "run_index": "docs/context/RUN_INDEX.md",
            "return_index": "docs/returns/RETURN_INDEX.md",
        },
        "deterministic_matches": idx_matches,
    }


def _render_last_event_reference_block(*, kind: str, refs: dict[str, Any]) -> str:
    """Renderiza bloque AUTO:last_event_refs para PROJECT_RESUME o CURRENT_FRONTIER."""

    pid = refs.get("project_id") or "unknown"
    g = refs.get("global_indexes") or {}

    lines: list[str] = [AUTO_LAST_EVENT_START]

    if kind == "project_resume":
        lines.extend(
            [
                "## (AUTO) Último evento de sesión (referencias)",
                "",
                "Este bloque sincroniza **referencias** desde `.orchestrator_state/active_project.json:last_event`.",
                "- La memoria de sesión es **efímera** (gitignored).",
                "- `PROJECT_RESUME.md` y `CURRENT_FRONTIER.md` son artefactos **versionados** de retoma.",
                "- Esta sincronización NO copia evidencia completa (TRACE/RUN_SUMMARY/raw_outputs/handoffs completos).",
                "",
                f"- project_id: `{pid}`",
            ]
        )

        if refs.get("updated_at"):
            lines.append(f"- last_event.updated_at: `{refs['updated_at']}`")
        if refs.get("instruction_preview"):
            lines.append(f"- instruction_preview: {refs['instruction_preview']}")
        if refs.get("status"):
            lines.append(f"- status: `{refs['status']}`")
        if refs.get("next_frontier"):
            lines.append(f"- next_frontier: `{refs['next_frontier']}`")
        if refs.get("next_question_preview"):
            lines.append(f"- next_question_preview: {refs['next_question_preview']}")

        if refs.get("run_id"):
            rid = refs["run_id"]
            lines.append(f"- run_id: `{rid}`")
            lines.append(f"  - run_index: `{g.get('run_index')}`")
            lines.append(f"  - run_dir: `docs/agent_runs/{rid}/`")

        if refs.get("handoff_json_path"):
            lines.append(f"- handoff_json_path: `{refs['handoff_json_path']}`")

        lines.extend(
            [
                "",
                "### Índices globales (referencias)",
                f"- action_index: `{g.get('action_index')}`",
                f"- decision_index: `{g.get('decision_index')}`",
                f"- run_index: `{g.get('run_index')}`",
                f"- return_index: `{g.get('return_index')}`",
            ]
        )

        dm = refs.get("deterministic_matches") or {}
        if (dm.get("decision_ids") or dm.get("action_ids") or dm.get("return_files") or dm.get("linked_decisions")):
            lines.extend(["", "### Matches determinísticos (si existen)"])
            if dm.get("decision_ids"):
                lines.append(f"- decision_ids: {', '.join('`'+x+'`' for x in dm['decision_ids'])}")
            if dm.get("action_ids"):
                lines.append(f"- action_ids: {', '.join('`'+x+'`' for x in dm['action_ids'])}")
            if dm.get("return_files"):
                lines.append(f"- return_files: {', '.join('`'+x+'`' for x in dm['return_files'])}")
            if dm.get("linked_decisions"):
                lines.append(f"- linked_decisions: {', '.join('`'+x+'`' for x in dm['linked_decisions'])}")

    elif kind == "current_frontier":
        lines.extend(
            [
                "### (AUTO) Puntero de sesión (referencias)",
                "",
                "Este bloque NO completa campos no inferibles; solo persiste referencias compactas.",
            ]
        )

        if refs.get("next_frontier"):
            lines.append(f"- derived_next_frontier: `{refs['next_frontier']}`")
        if refs.get("status"):
            lines.append(f"- derived_status: `{refs['status']}`")
        if refs.get("next_question_preview"):
            lines.append(f"- next_question_preview: {refs['next_question_preview']}")

        if refs.get("run_id"):
            rid = refs["run_id"]
            lines.append(f"- run_refs: `docs/context/RUN_INDEX.md` + `{rid}` + `docs/agent_runs/{rid}/`")

        if refs.get("handoff_json_path"):
            lines.append(f"- handoff_refs: `{refs['handoff_json_path']}`")

        lines.extend(
            [
                "- decision_refs: `docs/context/DECISION_INDEX.md` (ver IDs si aplican)",
                "- event_refs: `docs/context/ACTION_INDEX.md` (ver ACT-* si aplican)",
                "- return_refs: `docs/returns/RETURN_INDEX.md` (ver fila por project_id si existe)",
                "",
                "Rutas exactas:",
                "- `docs/context/ACTION_INDEX.md`",
                "- `docs/context/DECISION_INDEX.md`",
                "- `docs/context/RUN_INDEX.md`",
                "- `docs/returns/RETURN_INDEX.md`",
            ]
        )

        dm = refs.get("deterministic_matches") or {}
        if dm.get("decision_ids"):
            lines.append(f"- decision_ids: {', '.join('`'+x+'`' for x in dm['decision_ids'])}")
        if dm.get("action_ids"):
            lines.append(f"- event_action_ids: {', '.join('`'+x+'`' for x in dm['action_ids'])}")
        if dm.get("return_files"):
            lines.append(f"- return_files: {', '.join('`'+x+'`' for x in dm['return_files'])}")

    else:
        lines.append(f"(ERROR) unknown block kind: {kind}")

    lines.append(AUTO_LAST_EVENT_END)

    block = "\n".join(lines).rstrip() + "\n"

    if len(block) > MAX_AUTO_BLOCK_CHARS:
        # As a last resort, truncate previews (keep refs)
        block = re.sub(r"(instruction_preview: ).+", r"\1<truncated>", block)
        block = re.sub(r"(next_question_preview: ).+", r"\1<truncated>", block)

        if len(block) > MAX_AUTO_BLOCK_CHARS:
            block = block[: MAX_AUTO_BLOCK_CHARS - 20].rstrip() + "\n...<truncated>\n" + AUTO_LAST_EVENT_END + "\n"

    return block



def _patch_markdown_autoblock(*, path: Path, new_block: str, insertion_hint: str | None, apply: bool) -> dict[str, Any]:
    """Reemplaza/inyecta el bloque AUTO:last_event_refs de forma idempotente."""

    if not path.exists() or not path.is_file():
        return {"ok": False, "status": "missing_file", "path": str(path), "error": "file_not_found"}

    try:
        original = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return {"ok": False, "status": "error", "path": str(path), "error": f"read_failed:{exc}"}

    start_i = original.find(AUTO_LAST_EVENT_START)
    end_i = original.find(AUTO_LAST_EVENT_END)

    updated = original
    changed = False

    if start_i != -1 and end_i != -1 and end_i > start_i:
        end_j = original.find("\n", end_i)
        if end_j == -1:
            end_j = len(original)
        else:
            end_j = end_j + 1
        updated = original[:start_i] + new_block + original[end_j:]
        changed = (updated != original)
    else:
        insert_at = None
        if insertion_hint:
            m = re.search(re.escape(insertion_hint), original)
            if m:
                line_end = original.find("\n", m.end())
                insert_at = len(original) if line_end == -1 else line_end + 1

        if insert_at is None:
            insert_at = len(original)
            updated = original
            if not updated.endswith("\n"):
                updated += "\n"
            updated += "\n" + new_block
        else:
            updated = original[:insert_at] + "\n" + new_block + original[insert_at:]

        changed = (updated != original)

    if not apply:
        return {
            "ok": True,
            "status": "dry_run",
            "path": str(path),
            "changed": False,
            "would_change": changed,
            "reason": "would_replace" if (start_i != -1 and end_i != -1) else "would_insert",
        }


    if not changed:
        return {
            "ok": True,
            "status": "applied",
            "path": str(path),
            "changed": False,
            "would_change": False,
            "reason": "no_change",
        }

    try:
        path.write_text(updated, encoding="utf-8")

    except Exception as exc:
        return {"ok": False, "status": "error", "path": str(path), "error": f"write_failed:{exc}"}

    return {
        "ok": True,
        "status": "applied",
        "path": str(path),
        "changed": True,
        "would_change": True,
        "reason": "replaced" if (start_i != -1 and end_i != -1) else "inserted",
    }




def sync_active_last_event_to_project_docs(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Sincroniza referencias compactas desde active_project.last_event hacia docs/projects/<project-id>.

    Principios:
    - Compact-first y reference-based (no evidencia completa).
    - Idempotente (bloques auto-gestionados por markers).
    - Dry-run por defecto; apply requiere autorización explícita.

    Restricciones:
    - No crea scaffold automáticamente.
    - No toca proyectos externos.
    """

    arguments = arguments or {}

    project_id_arg = str(arguments.get("project_id") or "").strip() or None

    dry_run = bool(arguments.get("dry_run", True))
    apply = bool(arguments.get("apply", False))

    # Guardrail against contradictory flags.
    if apply and dry_run:
        return {
            "ok": False,
            "status": "error",
            "error": "flags_ambiguous: apply=true y dry_run=true (elige uno)",
        }

    if (not apply) and (dry_run is False):
        return {
            "ok": False,
            "status": "error",
            "error": "flags_ambiguous: dry_run=false requiere apply=true",
        }

    mode = "apply" if apply else "dry_run"

    update_files = arguments.get("update_files")
    if not isinstance(update_files, list) or not update_files:
        update_files_list = ["PROJECT_RESUME", "CURRENT_FRONTIER"]
    else:
        update_files_list = [str(x).strip().upper() for x in update_files if str(x).strip()]
        allowed = {"PROJECT_RESUME", "CURRENT_FRONTIER"}
        update_files_list = [x for x in update_files_list if x in allowed]
        if not update_files_list:
            update_files_list = ["PROJECT_RESUME", "CURRENT_FRONTIER"]

    allow_orchestrator = bool(arguments.get("allow_orchestrator", False))

    # 0) Ensure .orchestrator_state is gitignored
    ok_gitignore, gitignore_err = _ensure_orchestrator_state_gitignored()
    if not ok_gitignore:
        return {"ok": False, "status": "error", "error": gitignore_err}

        # 1) Load active state
    st = _load_active_project_state()
    ap = st.get("active_project")

    if not isinstance(ap, dict):

        return {
            "ok": True,
            "status": "missing_inputs",
            "mode": mode,
            "error": "active_project_missing",
            "active_project_path": st.get("path"),
        }

    active_pid = str(ap.get("project_id") or "").strip() or None
    if not active_pid:

        return {
            "ok": True,
            "status": "missing_inputs",
            "mode": mode,
            "error": "project_id_missing",
            "active_project_path": st.get("path"),
        }

    # Guardrail: evitar escritura cruzada si el caller pasa project_id distinto del activo.
    if project_id_arg and project_id_arg != active_pid:
        return {
            "ok": False,
            "status": "error",
            "mode": mode,
            "error": "project_id_mismatch: project_id no coincide con active_project.project_id",
            "active_project": {"project_id": active_pid},
            "requested_project_id": project_id_arg,
            "next_action": {
                "tool": "set_active_project",
                "arguments": {"project_id": project_id_arg, "note": "sync_active_last_event_to_project_docs"},
            },
        }

    pid = active_pid


    if pid == "orchestrator" and not allow_orchestrator:
        return {
            "ok": True,
            "status": "not_applicable",
            "mode": mode,
            "project_id": pid,
            "reason": "project_id=orchestrator requiere allow_orchestrator=true",
        }

    last_event = ap.get("last_event")
    if not isinstance(last_event, dict) or not last_event:
        return {
            "ok": True,
            "status": "missing_inputs",
            "mode": mode,
            "project_id": pid,
            "error": "last_event_missing",
        }

    # 2) Validate project docs exist
    docs_dir = ROOT / "docs" / "projects" / pid
    resume_path = docs_dir / "PROJECT_RESUME.md"
    frontier_path = docs_dir / "CURRENT_FRONTIER.md"

    if not docs_dir.exists() or not docs_dir.is_dir():
        return {
            "ok": True,
            "status": "onboarding_required",
            "mode": mode,
            "project_id": pid,
            "docs_dir": str(docs_dir),
            "missing": ["docs/projects/<project-id>/"],
            "missing_files": ["docs/projects/<project-id>/"],
            "recommended_next_tool_call": {
                "tool": "init_project_onboarding_scaffold",
                "arguments": {"project_id": pid, "dry_run": False},
            },
        }

    missing_files = []
    if not resume_path.exists():
        missing_files.append(str(resume_path))
    if not frontier_path.exists():
        missing_files.append(str(frontier_path))

    if missing_files:
        return {
            "ok": True,
            "status": "onboarding_required",
            "mode": mode,
            "project_id": pid,
            "docs_dir": str(docs_dir),
            "missing": missing_files,
            "missing_files": missing_files,
            "recommended_next_tool_call": {
                "tool": "init_project_onboarding_scaffold",
                "arguments": {"project_id": pid, "dry_run": False},
            },
        }

    refs = _extract_last_event_refs(active_project=ap, project_id=pid)

    results: dict[str, Any] = {
        "ok": True,
        "status": "dry_run_ready" if not apply else "applied",
        "mode": mode,
        "project_id": pid,
        "active_project_path": st.get("path"),
        "docs_dir": str(docs_dir),
        "update_files": update_files_list,
        "guardrails": {
            "compact_first": True,
            "reference_based": True,
            "auto_block_markers": [AUTO_LAST_EVENT_START, AUTO_LAST_EVENT_END],
            "max_auto_block_chars": MAX_AUTO_BLOCK_CHARS,
            "orchestrator_state_gitignored": True,
        },
        "refs": {
            "last_event": {
                "updated_at": refs.get("updated_at"),
                "instruction_preview": refs.get("instruction_preview"),
                "status": refs.get("status"),
                "next_frontier": refs.get("next_frontier"),
                "next_question_preview": refs.get("next_question_preview"),
                "run_id": refs.get("run_id"),
                "handoff_json_path": refs.get("handoff_json_path"),
            },
            "global_indexes": refs.get("global_indexes"),
            "deterministic_matches": refs.get("deterministic_matches"),
        },
        "files": {},
    }

    if "PROJECT_RESUME" in update_files_list:
        block = _render_last_event_reference_block(kind="project_resume", refs=refs)
        results["files"]["PROJECT_RESUME"] = _patch_markdown_autoblock(
            path=resume_path,
            new_block=block,
            insertion_hint="## 7) Handoffs / runs / returns relevantes",
            apply=apply,
        )

    if "CURRENT_FRONTIER" in update_files_list:
        block = _render_last_event_reference_block(kind="current_frontier", refs=refs)
        results["files"]["CURRENT_FRONTIER"] = _patch_markdown_autoblock(
            path=frontier_path,
            new_block=block,
            insertion_hint="## Referencias",
            apply=apply,
        )

    would_change = False
    changed = False
    for v in (results.get("files") or {}).values():
        if isinstance(v, dict):
            would_change = would_change or bool(v.get("would_change"))
            changed = changed or bool(v.get("changed"))

    results["would_change"] = would_change
    results["changed"] = changed

    return results


def operational_status(arguments: dict[str, Any] | None = None) -> dict[str, Any]:


    """Diagnóstico operativo compact-first vía scripts/audit_agent_artifacts.py --operational-status.

    Restricciones:
    - Read-only.
    - No abre raw_outputs ni TRACE/RUN_SUMMARY completos.
    - Devuelve payload normalizado del script (sin duplicar stdout/stderr completos).
    """

    arguments = arguments or {}

    command = [
        "scripts/audit_agent_artifacts.py",
        "--operational-status",
    ]

    if arguments.get("include_git_status", True) is True:
        command.append("--include-git-status")

    if arguments.get("run_quick_checks", False) is True:
        command.append("--run-quick-checks")

    if arguments.get("verify_master_files", True) is False:
        command.append("--no-verify-master-files")

    result = _run_python_script(command, timeout=120, max_output_chars=65536)

    parsed = _json_or_text(result.get("stdout", ""))
    if isinstance(parsed, dict):
        # El script ya devuelve ok/status/overall_status/etc.
        # Preservar el ok operativo original antes de sobrescribir.
        operational_ok = bool(parsed.get("ok"))
        # Forzar ok=True para MCP cuando el JSON parseó, evitando isError por warn/error operativo.
        parsed["ok"] = True
        parsed["operational_ok"] = operational_ok
        parsed.setdefault("elapsed_ms", result.get("elapsed_ms"))
        return parsed

    # Fallback si stdout no es JSON
    stderr_raw = result.get("stderr", "")
    stderr_preview = stderr_raw
    if len(stderr_preview) > 1200:
        stderr_preview = stderr_preview[:1200] + "\n... [truncated]"

    return {
        "ok": False,
        "status": "error",
        "error": "Salida no JSON del operational status.",
        "stderr_preview": stderr_preview,
        "elapsed_ms": result.get("elapsed_ms"),
    }


def _normalize_free_text(text: str) -> str:
    """Normaliza texto libre (lower + strip + sin acentos) para heurísticas."""

    raw = (text or "").strip().lower()
    if not raw:
        return ""
    # Remover acentos: 'Evaluá' -> 'evalua'
    try:
        raw = (
            unicodedata.normalize("NFKD", raw)
            .encode("ascii", "ignore")
            .decode("ascii", errors="ignore")
        )
    except Exception:
        pass
    raw = re.sub(r"\s+", " ", raw)
    return raw


def _extract_project_query_from_instruction(norm: str) -> str | None:
    """Extrae un project_query simple desde la instrucción normalizada.

    Objetivo: permitir comandos naturales como:
    - "cambia a dpm"
    - "salta a orchestrator"
    - "trabaja en data-privacy-management-d"

    Nota: esto NO confirma el proyecto; solo propone un query para resolve_target_project.
    """

    n = (norm or "").strip().lower()
    if not n:
        return None

    patterns = [
        r"(?:cambia|cambiar|salta|saltar|ir)\s+a\s+([a-z0-9._-]+)",
        r"(?:retoma|retomar|reanuda|reanudar|resume)\s+([a-z0-9._-]+)",
        r"(?:trabaja|trabajar)\s+en\s+([a-z0-9._-]+)",
        r"(?:proyecto|project)\s+([a-z0-9._-]+)",
        r"(?:en)\s+([a-z0-9._-]+)\s*$",
    ]


    for pat in patterns:
        m = re.search(pat, n)

        if m:
            candidate = (m.group(1) or "").strip().strip(".,;:!?")
            if candidate and candidate not in {"este", "this", "activo", "active"}:
                return candidate

    return None



def _extract_project_query_for_bridge_handoff(norm: str) -> str | None:
    """Extrae project_query desde instrucciones tipo "handoff del bridge de <alias>" (best-effort)."""

    n = (norm or "").strip().lower()
    if not n:
        return None

    patterns = [
        r"handoff\s+del\s+bridge\s+de\s+([a-z0-9._-]+)",
        r"handoff\s+del\s+bridge\s+en\s+([a-z0-9._-]+)",
        r"bridge\s+de\s+([a-z0-9._-]+)",
        r"handoff\s+de\s+([a-z0-9._-]+)",
        r"en\s+([a-z0-9._-]+)\s+y\s+avanza",
    ]

    for pat in patterns:
        m = re.search(pat, n)
        if m:
            candidate = (m.group(1) or "").strip().strip(".,;:!?")
            if candidate and candidate not in {"este", "this", "proyecto", "bridge", "handoff"}:
                return candidate

    return None


def _extract_orchestrator_transfer_json_path(norm: str) -> str | None:
    """Extrae ruta a un orchestrator_transfer_*.json desde texto normalizado (best-effort)."""

    n = (norm or "").strip()
    if not n:
        return None

    win = re.search(r"([a-zA-Z]:\\[^\s\"']*orchestrator_transfer_[^\s\"']*\.json)", n)
    if win:
        return win.group(1).strip()

    unix = re.search(r"(/[^\s\"']*orchestrator_transfer_[^\s\"']*\.json)", n)
    if unix:
        return unix.group(1).strip()

    return None


def _is_bridge_handoff_request(norm: str) -> bool:
    n = (norm or "").strip().lower()
    if not n:
        return False

    triggers = [
        "procesa el ultimo handoff",
        "procesa el ultimo handoff del bridge",
        "procesa el ultimo handoff del proyecto activo",
        "continua con el ultimo handoff",
        "continua con el ultimo handoff del proyecto activo",
        "toma el handoff",
        "procesa este handoff",
        "procesa el handoff",
    ]

    if any(t in n for t in triggers):
        return True

    if "handoff" in n and "bridge" in n:
        return True

    return False


def _classify_general_instruction(instruction: str) -> dict[str, Any]:

    """Heurística ligera para instrucciones generales.

    No invoca modelos: solo enruta hacia herramientas internas/OpenCode.
    """

    norm = _normalize_free_text(instruction)

    extracted_project_query = _extract_project_query_from_instruction(norm)


    wants_active_project = ("proyecto activo" in norm) or ("active project" in norm)

    resume_keywords = (
        "retoma",
        "retomar",
        "reanuda",
        "reanud",
        "resume",
        "volver",
        "continua",
        "continuar",
        "continuemos",
    )
    resume_requested = wants_active_project or any(k in norm for k in resume_keywords)

    # Opt-in: sincronizar referencias del last_event de sesión hacia docs/projects/<project-id>/...
    sync_last_event_requested = any(
        k in norm
        for k in (
            "sincroniza",
            "sincronizar",
            "sincronizacion",
            "sync last_event",
            "sync last event",
            "actualiza referencias",
        )
    )

    # Guardrail: aplicar solo si el texto contiene un opt-in inequívoco.
    sync_last_event_apply_authorized = sync_last_event_requested and any(
        k in norm for k in ("autorizo", "autorizado", "autorizacion concedida", "concedo autorizacion")
    )

    # Intent
    intent = "unknown"
    scenario = "context-validation"

    is_advance_phrase = ("siguiente frontera" in norm) or norm.startswith("avanza") or ("avanza con" in norm)

    if _is_bridge_handoff_request(norm):
        intent = "ingest_bridge_handoff"
        scenario = "context-validation"
    elif any(k in norm for k in ("diagnostica", "diagnosticar", "diagnostico")):
        intent = "diagnose"
        scenario = "context-validation"
    elif is_advance_phrase and resume_requested:
        # Ej: "avanza con el proyecto activo" → resume + planning
        intent = "resume"
        scenario = "planning"
    elif resume_requested:
        # Incluye: "retoma dpm", "continúa donde quedamos", etc.
        intent = "resume"
        scenario = "context-validation"
    elif is_advance_phrase:
        intent = "advance"
        scenario = "planning"
    elif "prepara" in norm and ("low-risk" in norm or "bajo riesgo" in norm or "low risk" in norm):
        intent = "prepare_low_risk"
        scenario = "planning"
    elif "evalua" in norm and ("replit" in norm or "premium" in norm):
        intent = "evaluate_escalation"
        scenario = "context-validation"


    # Risk (very coarse)
    risk = "medium"
    if intent == "prepare_low_risk":
        risk = "low"

    high_triggers = (
        "seguridad",
        "security",
        "auth",
        "permisos",
        "secrets",
        "credenciales",
        "token",
        "pii",
        "datos personales",
        "migracion",
        "migration",
        "deploy",
        "deployment",
        "ci/cd",
        "arquitectura",
        "refactor transversal",
    )
    if any(k in norm for k in high_triggers):
        risk = "high"

    # Volume (very coarse)
    volume = "medium"
    if any(k in norm for k in ("end-to-end", "end to end", "punta a punta", "completo", "completa")):
        volume = "high"

    # Premium request (avoid confusing with "evaluate")
    is_evaluate_mode = intent == "evaluate_escalation"
    explicit_premium_request = False
    if not is_evaluate_mode:
        premium_patterns = ("usa premium", "use premium", "con premium", "modelo premium", "escala a premium")
        if any(p in norm for p in premium_patterns):
            explicit_premium_request = True

    # Replit triggers
    replit_trigger_keywords = (
        "replit",
        "runtime",
        "preview",
        "deploy",
        "deployment",
        "secrets",
        "variables de entorno",
        "env",
        "integracion",
        "integracion",
    )
    replit_triggered = any(k in norm for k in replit_trigger_keywords) and intent != "evaluate_escalation"

    bridge_project_query = _extract_project_query_for_bridge_handoff(norm)
    # Importante: extraer ruta desde el instruction original para preservar casing/backslashes.
    bridge_handoff_path = _extract_orchestrator_transfer_json_path(instruction)




    return {
        "instruction_normalized": norm,
        "intent": intent,
        "scenario": scenario,
        "risk": risk,
        "volume": volume,
        "explicit_premium_request": explicit_premium_request,
        "replit_triggered": replit_triggered,
        "extracted_project_query": extracted_project_query,
        "resume_requested": resume_requested,
        "wants_active_project": wants_active_project,
        "sync_last_event_requested": sync_last_event_requested,
        "sync_last_event_apply_authorized": sync_last_event_apply_authorized,


        # Bridge handoff hints (best-effort)
        "bridge_project_query": bridge_project_query,
        "bridge_handoff_json_path": bridge_handoff_path,
        "bridge_wants_active_project": ("proyecto activo" in norm) or ("active project" in norm),
    }






# --- Context pack (Bloque 3 operativo) ---------------------------------------

# Default exclusions for reference-based context packs.
# Principle: avoid dumping bulky artifacts into MCP responses by default.
CONTEXT_PACK_EXCLUSIONS_DEFAULT: dict[str, Any] = {
    "paths_or_globs": [
        "docs/agent_runs/**",
        "docs/agent_queue/**",
        "raw_outputs/**",
        "TRACE.md",
        "RUN_SUMMARY.md",
        "handoffs/**",
        "**/handoff_*.md",
        "**/handoff_*.json",
        "**/*.chat.json",
        "**/*.chat.md",
    ],
    "notes": [
        "Exclusión por defecto: artefactos voluminosos y chats completos. Usar referencias: run_id + rutas + conteos + previews mínimos.",
    ],
}


def _compact_git_ref(git_info: Any) -> dict[str, Any] | None:
    if not isinstance(git_info, dict):
        return None

    wt = git_info.get("working_tree") if isinstance(git_info.get("working_tree"), dict) else {}

    out = {
        "branch": git_info.get("branch"),
        "last_commit": git_info.get("last_commit"),
        "remote_origin": git_info.get("remote_origin"),
        "working_tree_clean": wt.get("clean"),
    }

    # Drop empty
    if not any(v is not None and v != "" for v in out.values()):
        return None
    return out


def _build_standard_context_pack(
    *,
    level: int,
    instruction: str,
    mode: str,
    classified: dict[str, Any] | None,
    project_id: str | None,
    project_query_source: str | None,
    resolution: dict[str, Any] | None,
    onboarding: dict[str, Any] | None,
    missing_files: list[str] | None,
    preflight_status: str | None,
    orchestrator_summary: dict[str, Any] | None,
    versioned_memory: dict[str, Any] | None,
    session_memory: dict[str, Any] | None,
) -> dict[str, Any]:
    """Construye un context_pack estándar (reference-based, compact-first).

    Niveles materializados en esta fase:
    - 0: mínimo operativo.
    - 1: default operativo.

    Nota: no lee artefactos voluminosos; solo referencia rutas/IDs/conteos.
    """

    try:
        lvl = int(level)
    except Exception:
        lvl = 0

    # Guardrail: por ahora solo materializamos 0/1 (2/3 quedan controlados).
    lvl = 0 if lvl < 0 else lvl
    lvl = 1 if lvl > 1 else lvl

    # Compact resolution
    resolution_compact: dict[str, Any] | None = None
    if isinstance(resolution, dict):
        git_ref = _compact_git_ref(resolution.get("git"))
        resolution_compact = {
            "matched_by": resolution.get("matched_by"),
            "environment_type": resolution.get("environment_type"),
            "local_path": resolution.get("local_path"),
            "git_ref": git_ref,
        }

    # Compact onboarding
    onboarding_compact: dict[str, Any] | None = None
    mf: list[str] = []
    if isinstance(missing_files, list):
        mf = [str(x) for x in missing_files if str(x).strip()]
    elif isinstance(onboarding, dict) and isinstance(onboarding.get("missing"), list):
        mf = [str(x) for x in (onboarding.get("missing") or []) if str(x).strip()]

    if isinstance(onboarding, dict) or mf:
        onboarding_compact = {
            "status": onboarding.get("status") if isinstance(onboarding, dict) else None,
            "docs_dir": onboarding.get("docs_dir") if isinstance(onboarding, dict) else None,
            "missing_files_count": len(mf),
            "missing_files": mf[:20],
        }

    orchestrator_compact: dict[str, Any] | None = None
    if preflight_status or orchestrator_summary:
        orchestrator_compact = {
            "preflight_status": preflight_status,
            "summary": orchestrator_summary,
        }

    # Stable references (paths only)
    orchestrator_files = [
        "AGENT_RULES.md",
        "PROJECT_CONTEXT.md",
        "MODEL_ROUTING.md",
        "SECURITY_POLICY.md",
        "CONTINUE_USAGE_PROTOCOL.md",
        "AGENT_ORCHESTRATION.md",
        "docs/AGENT_ORCHESTRATION.md",
        "docs/alerts/GLOBAL_CRITICAL_ALERTS.md",
        "docs/lessons/GLOBAL_LESSONS_LEARNED.md",
    ]

        
    pack: dict[str, Any] = {
        "status": "ok",
        "level": lvl,

        "protocol": "reference-based",
        "generated_at": _now_iso(),
        "mode": mode,
        "instruction_preview": _safe_preview_text(instruction, limit=220),
        "target": {
            "project_id": project_id,
            "project_query_source": project_query_source,
        },
        "resolution": resolution_compact,
        "onboarding": onboarding_compact,
        "orchestrator": orchestrator_compact,
        "references": {
            "orchestrator_root": str(ROOT),
            "orchestrator_files": orchestrator_files,
            "run_index": "docs/context/RUN_INDEX.md",
            "decision_index": "docs/context/DECISION_INDEX.md",
            "action_index": "docs/context/ACTION_INDEX.md",
            "return_index": "docs/returns/RETURN_INDEX.md",
            "project_docs_dir": (f"docs/projects/{project_id}/" if project_id and project_id != "orchestrator" else None),
        },
        "exclusions": CONTEXT_PACK_EXCLUSIONS_DEFAULT,
        "notes": [],
    }

    # Memoria versionada (docs/projects/<project-id>/...) y memoria de sesión (gitignored):
    # incluir solo por referencias + extractos compactos.
    if isinstance(versioned_memory, dict) and versioned_memory:
        pack["versioned_memory"] = versioned_memory
        files = versioned_memory.get("files")
        if isinstance(files, dict):
            role_by_name = {
                "PROJECT_RESUME.md": "project_resume",
                "CURRENT_FRONTIER.md": "current_frontier",
                "ERRORS_AND_FIXES.md": "errors_and_fixes",
                "CRITICAL_ALERTS.md": "critical_alerts",
                "LESSONS_LOCAL.md": "lessons_local",
                "SEMANTIC_TAG_INDEX.md": "semantic_tag_index",
                "HANDOFF_LOG.md": "handoff_log",
                "SYNC_STATUS.md": "sync_status",
            }
            refs = []
            for name, meta in files.items():
                if not isinstance(meta, dict):
                    continue
                refs.append({
                    "role": role_by_name.get(str(name), str(name)),
                    "path": meta.get("path"),
                    "exists": meta.get("exists"),
                    "size_bytes": meta.get("size_bytes"),
                })
            if refs:
                pack["refs"] = refs
    if isinstance(session_memory, dict) and session_memory:
        pack["session_memory"] = session_memory

    # Minimal note about intent/risk if available.

    if isinstance(classified, dict):
        intent = classified.get("intent")
        risk = classified.get("risk")
        if intent or risk:
            pack["notes"].append(f"intent={intent or 'unknown'}; risk={risk or 'unknown'}")

    return pack


def _stat_file_ref(path: Path) -> dict[str, Any]:
    """Metadata compacta para referencias (sin dumps)."""

    try:
        st = path.stat()
        return {
            "path": str(path),
            "exists": True,
            "size_bytes": int(st.st_size),
            "mtime": float(st.st_mtime),
        }
    except Exception:
        return {"path": str(path), "exists": False}


def _extract_frontier_fields(prefix: str) -> dict[str, Any]:
    """Extrae campos clave de CURRENT_FRONTIER.md sin parseo rígido."""

    p = str(prefix or "")

    def _grab(key: str) -> str | None:
        # soporta:
        # - key: `value`
        # - key: value
        m = re.search(rf"^\s*-\s*{re.escape(key)}\s*:\s*(.+)\s*$", p, flags=re.IGNORECASE | re.MULTILINE)
        if not m:
            return None
        raw = (m.group(1) or "").strip().strip("`")
        return raw or None

    return {
        "status": _grab("status"),
        "blocking_threshold": _grab("blocking_threshold"),
        "next_action": _grab("next_action"),
        "requires_user_action": _grab("requires_user_action"),
    }


def _extract_project_resume_fields(prefix: str) -> dict[str, Any]:
    """Extrae campos útiles de PROJECT_RESUME.md (best-effort)."""

    p = str(prefix or "")

    def _grab(key: str) -> str | None:
        m = re.search(rf"^\s*-\s*{re.escape(key)}\s*:\s*(.+)\s*$", p, flags=re.IGNORECASE | re.MULTILINE)
        if not m:
            return None
        raw = (m.group(1) or "").strip().strip("`")
        return raw or None

    # Buscar run_id en bloques auto-sync si existe.
    run_id = None
    m = re.search(r"\brun_id\s*:\s*`([^`]+)`", p, flags=re.IGNORECASE)
    if m:
        run_id = (m.group(1) or "").strip() or None

    return {
        "status_classification": _grab("status_classification"),
        "branch": _grab("branch"),
        "last_commit": _grab("last_commit"),
        "run_id": run_id,
    }


def _collect_project_versioned_memory(*, project_id: str, level: int) -> dict[str, Any] | None:
    """Construye un bloque reference-based para memoria versionada (docs/projects/<pid>/...).

    - No asume scaffold si onboarding no está listo.
    - Lee solo prefijos pequeños para extraer 2–4 campos (sin dumps).
    """

    pid = (project_id or "").strip()
    if not pid or pid == "orchestrator":
        return None

    onboarding = _probe_project_onboarding(pid)
    if onboarding.get("status") not in {"ready"}:
        return {
            "project_id": pid,
            "status": "onboarding_not_ready",
            "docs_dir": onboarding.get("docs_dir"),
            "missing_files": onboarding.get("missing") if isinstance(onboarding.get("missing"), list) else [],
        }

    docs_dir = ROOT / "docs" / "projects" / pid

    files = {
        name: _stat_file_ref(docs_dir / name)
        for name in (
            "PROJECT_RESUME.md",
            "CURRENT_FRONTIER.md",
            "ERRORS_AND_FIXES.md",
            "CRITICAL_ALERTS.md",
            "LESSONS_LOCAL.md",
            "SEMANTIC_TAG_INDEX.md",
            "HANDOFF_LOG.md",
            "SYNC_STATUS.md",
        )
    }

    extracts: dict[str, Any] = {}

    frontier_path = docs_dir / "CURRENT_FRONTIER.md"
    frontier_prefix = _read_text_prefix(frontier_path, max_chars=7000) if frontier_path.exists() else ""
    frontier_fields = _extract_frontier_fields(frontier_prefix)
    if any(v for v in frontier_fields.values()):
        extracts["current_frontier"] = frontier_fields

    resume_path = docs_dir / "PROJECT_RESUME.md"
    resume_prefix = _read_text_prefix(resume_path, max_chars=9000) if resume_path.exists() else ""
    resume_fields = _extract_project_resume_fields(resume_prefix)
    if any(v for v in resume_fields.values()):
        extracts["project_resume"] = resume_fields

    previews: dict[str, Any] | None = None
    if int(level) >= 1:
        previews = {
            "current_frontier_preview": _safe_preview_text(frontier_prefix, limit=420) if frontier_prefix else None,
            "project_resume_preview": _safe_preview_text(resume_prefix, limit=420) if resume_prefix else None,
        }

    out: dict[str, Any] = {
        "project_id": pid,
        "status": "ready",
        "docs_dir": str(docs_dir),
        "files": files,
        "extracts": extracts,
    }

    if previews:
        out["previews"] = previews

    return out


def _extract_active_last_event_compact(active_state: dict[str, Any] | None) -> dict[str, Any] | None:
    """Extrae last_event de `.orchestrator_state/active_project.json` (sin leer índices)."""

    if not isinstance(active_state, dict):
        return None

    le = active_state.get("last_event")
    if not isinstance(le, dict) or not le:
        return None

    return {
        "updated_at": le.get("updated_at"),
        "source": le.get("source"),
        "mode": le.get("mode"),
        "status": le.get("status"),
        "next_frontier": le.get("next_frontier"),
        "instruction_preview": _safe_preview_text(_redact_possible_secrets(le.get("instruction")), limit=180) if le.get("instruction") else None,
        "next_question_preview": _safe_preview_text(_redact_possible_secrets(le.get("next_question")), limit=220) if le.get("next_question") else None,
        "handoff_json_path": le.get("handoff_json_path"),
        "run_id": le.get("run_id"),
    }


def plan_general_instruction(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Plan read-only para traducir una instrucción general a la siguiente frontera segura.

    Encadena (sin ejecutar modelos por defecto):
    - operational_status (orquestador)
    - resolve_target_project
    - select_agent_model

    Output: compact-first con un `tool_plan` listo para que Continue lo ejecute.
    """

    arguments = arguments or {}

    instruction = (arguments.get("instruction") or "").strip()
    if not instruction:

        return {"ok": False, "status": "error", "error": "instruction es obligatorio."}

    project_query = (arguments.get("project_query") or "").strip()
    workspace_path = (arguments.get("workspace_path") or "").strip()

    projects_root = arguments.get("projects_root")

    include_git = bool(arguments.get("include_git", True))

    include_orchestrator_status = bool(arguments.get("include_orchestrator_status", True))
    include_preflight = bool(arguments.get("include_preflight", True))
    include_semantic_context_gate = bool(arguments.get("include_semantic_context_gate", True))


    classified = _classify_general_instruction(instruction)

    # Memoria de sesión local (gitignored): útil para “proyecto activo/retoma”, pero no sustituye
    # la memoria versionada (docs/projects/<project-id>/...).
    active_state = _read_json_file(ACTIVE_PROJECT_PATH) or {}
    active_pid = (active_state.get("project_id") or "").strip() if isinstance(active_state, dict) else ""


    # Permitir selección de proyecto con lenguaje natural en el propio `instruction`.
    # Precedencia: argumentos explícitos > extracción por heurística > retomar (sesión).
    project_query_source = "arguments" if project_query else None

    if not project_query:
        extracted = (classified.get("extracted_project_query") or "").strip()
        if extracted:
            project_query = extracted
            project_query_source = "instruction"

        # Retomar por “proyecto activo” cuando el usuario lo pide (retoma/continúa/avanza) y no dio project/workspace.
    if not project_query and not workspace_path and (
        classified.get("resume_requested") is True or classified.get("bridge_wants_active_project") is True
    ):
        if active_pid:
            project_query = active_pid
            project_query_source = "active_project"


    # Daily-use default (orchestrator-first): si no se especifica proyecto ni workspace,
    # asumimos el repo del orquestador como proyecto objetivo.
    # Esto reduce fricción para uso diario (instrucción general → acción) sin tener que
    # pasar project_query/workspace_path cada vez.
    if not project_query and not workspace_path:
        workspace_path = str(ROOT)
        project_query_source = project_query_source or "default_orchestrator_root"

    tool_plan: list[dict[str, Any]] = []




    orchestrator_ready_to_advance = True
    orchestrator_summary: dict[str, Any] | None = None

    # 0) Preflight transversal (opcional)
    preflight_parsed: dict[str, Any] | None = None
    if include_preflight:
        pf = orchestrator_preflight({})
        preflight_parsed = pf.get("parsed") if isinstance(pf.get("parsed"), dict) else None
        tool_plan.append({"tool": "orchestrator_preflight", "arguments": {}})

    # 1) Estado del orquestador (evita avanzar si el repo está sucio o faltan master files)
    orch_status: dict[str, Any] | None = None
    if include_orchestrator_status:
        orch_status = operational_status({"include_git_status": True, "run_quick_checks": False, "verify_master_files": True})
        tool_plan.append({
            "tool": "operational_status",
            "arguments": {"include_git_status": True, "run_quick_checks": False, "verify_master_files": True},
        })

        # No bloquear todo el plan por warnings (p.ej. git dirty):
        # - Hard-block solo si hay error real (master files / fallos internos).
        # - Si no está listo para avanzar, simplemente NO sugerir dispatch automático.
        if isinstance(orch_status, dict):
            orchestrator_ready_to_advance = bool(orch_status.get("ready_to_advance", True))
            orchestrator_summary = {
                "overall_status": orch_status.get("overall_status"),
                "git_clean": orch_status.get("git_clean"),
                "blockers": orch_status.get("blockers"),
                "attention": orch_status.get("attention"),
                "suggested_next_step": orch_status.get("suggested_next_step"),
                "ready_to_advance": orch_status.get("ready_to_advance"),
                "build_blocked": orch_status.get("build_blocked"),
            }

            # Bloquear solo por error real (no por warn). Los warnings se reflejan en ready_to_advance=false
            # y deben impedir dispatch automático, pero no romper la planificación.
            if orch_status.get("overall_status") == "error":
                return {
                    "ok": True,
                    "status": "blocked",
                    "blocked_by": "orchestrator_error",
                    "instruction": instruction,
                    "classified": classified,
                    "orchestrator": orchestrator_summary,
                    "tool_plan": tool_plan,
                    "next_frontier": "fix_orchestrator",
                    "next_question": "El orquestador reporta error operativo. Corrige y reintenta.",
                }

    # 2) Resolver proyecto objetivo
    resolution_args: dict[str, Any] = {
        "project_query": project_query,
        "workspace_path": workspace_path,
        "include_git": include_git,
    }
    if projects_root:
        resolution_args["projects_root"] = str(projects_root)

    resolution = resolve_target_project(resolution_args)
    tool_plan.append({"tool": "resolve_target_project", "arguments": resolution_args})

    # Si no está confirmado, devolver pregunta mínima.
    if resolution.get("project_not_confirmed") is True or resolution.get("project_confirmed") is not True:
        return {
            "ok": True,
            "status": "project_not_confirmed",
            "instruction": instruction,
            "classified": classified,
            "resolution": {
                "project_confirmed": resolution.get("project_confirmed"),
                "project_not_confirmed": resolution.get("project_not_confirmed"),
                "matched_by": resolution.get("matched_by"),
                "candidates": resolution.get("candidates", []),
                "workspace_git": resolution.get("workspace_git"),
            },
            "tool_plan": tool_plan,
            "next_frontier": "confirm_project",
            "next_question": resolution.get("next_question") or "Proyecto objetivo no confirmado.",
        }

    project_id = resolution.get("project_id")

    # 3) Si requiere preparar workspace (clone), detenerse ahí.
    if resolution.get("clone_required") is True and classified.get("intent") != "resume":
        return {
            "ok": True,
            "status": "workspace_not_ready",
            "instruction": instruction,
            "classified": classified,
            "project_id": project_id,
            "resolution": {
                "local_exists": resolution.get("local_exists"),
                "git_repo_exists": resolution.get("git_repo_exists"),
                "suggested_local_path": resolution.get("suggested_local_path"),
                "repo_url": resolution.get("repo_url"),
            },
            "tool_plan": tool_plan,
            "next_frontier": "prepare_workspace",
            "next_question": "Workspace local no está listo (clone_required=true). ¿Autorizas preparar el workspace (sin clonar automáticamente) y/o quieres proporcionar local_path existente?",
        }

    # 4) Git dirty del proyecto objetivo: bloquear antes de avanzar a ejecución.
    if "working_tree_dirty" in (resolution.get("risks") or []) and classified.get("intent") != "resume":
        return {
            "ok": True,
            "status": "blocked",
            "blocked_by": "working_tree_dirty",
            "instruction": instruction,
            "classified": classified,
            "project_id": project_id,
            "resolution": {"git": resolution.get("git")},
            "tool_plan": tool_plan,
            "next_frontier": "clean_working_tree",
            "next_question": "El working tree del proyecto objetivo no está limpio. Limpia/commit manualmente y reintenta (no se aplican stashes automáticamente).",
        }

    # 4.1) Onboarding documental/contextual (scaffold) — mínimo canónico.
    # Si el proyecto objetivo no tiene scaffold en docs/projects/<project_id>/, iniciarlo antes
    # de avanzar a ejecución o dispatch.
    onboarding = _probe_project_onboarding(str(project_id or ""))
    if onboarding.get("status") in {"missing", "partial"} and project_id and str(project_id) != "orchestrator":
        recommended_next_tool_call = {
            "tool": "init_project_onboarding_scaffold",
            "arguments": {"project_id": str(project_id), "dry_run": False},
        }
        tool_plan.append(recommended_next_tool_call)

        context_pack_level = 0

        session_memory = None

        if active_pid:
            session_memory = {
                "active_project_path": str(ACTIVE_PROJECT_PATH),
                "active_project_id": active_pid,
                "last_event": _extract_active_last_event_compact(active_state),
            }

        context_pack = _build_standard_context_pack(
            level=context_pack_level,
            instruction=instruction,
            mode="Plan",
            classified=classified,
            project_id=str(project_id) if project_id else None,
            project_query_source=project_query_source,
            resolution=(resolution if isinstance(resolution, dict) else None),
            onboarding=(onboarding if isinstance(onboarding, dict) else None),
            missing_files=onboarding.get("missing") if isinstance(onboarding.get("missing"), list) else [],
            preflight_status=preflight_parsed.get("status") if isinstance(preflight_parsed, dict) else None,
            orchestrator_summary=orchestrator_summary,
            versioned_memory=None,
            session_memory=session_memory,
        )


        return {
            "ok": True,
            "status": "onboarding_required",
            "instruction": instruction,
            "classified": classified,
            "project_id": project_id,
            "project_query_source": project_query_source,
            "context_pack_level": context_pack_level,
            "context_pack": context_pack,
            "preflight_status": preflight_parsed.get("status") if isinstance(preflight_parsed, dict) else None,
            "orchestrator": orchestrator_summary,
            "orchestrator_ready_to_advance": orchestrator_ready_to_advance,
            "resolution": {
                "matched_by": resolution.get("matched_by"),
                "environment_type": resolution.get("environment_type"),
                "local_path": resolution.get("local_path"),
                "git": resolution.get("git"),
            },
            "onboarding": onboarding,
            "missing_files": onboarding.get("missing") if isinstance(onboarding.get("missing"), list) else [],
            "tool_plan": tool_plan,
            "recommended_next_tool_call": recommended_next_tool_call,
            "next_frontier": "init_onboarding_scaffold",
            "next_question": None,
            "compact_message_for_continue": {
                "project_id": project_id,
                "intent": classified.get("intent"),
                "next_frontier": "init_onboarding_scaffold",
                "note": "Proyecto confirmado pero sin scaffold completo en docs/projects/<project-id>/; iniciar onboarding mínimo.",
            },
            "followup_scheme_template": _build_followup_scheme(run_id=None),
        }

    # 4.2) Gate semantico de contexto: no depende de memoria humana.
    # Se ejecuta despues del onboarding mínimo: si faltan índices base, la frontera correcta
    # es onboarding_required, no context_discovery.
    semantic_gate: dict[str, Any] | None = None
    semantic_gate_status: str | None = None
    if include_semantic_context_gate and project_id:
        sg_args = {"project_id": str(project_id), "instruction": instruction, "max_results": 8}
        sg = semantic_context_gate(sg_args)
        semantic_gate = sg.get("parsed") if isinstance(sg.get("parsed"), dict) else {"raw": sg.get("stdout"), "stderr": sg.get("stderr")}
        semantic_gate_status = str(semantic_gate.get("status") or "") if isinstance(semantic_gate, dict) else None
        tool_plan.append({"tool": "semantic_context_gate", "arguments": sg_args})

        if semantic_gate_status and semantic_gate_status.startswith("blocked"):
            return {
                "ok": True,
                "status": "blocked",
                "blocked_by": "semantic_context_gate",
                "instruction": instruction,
                "classified": classified,
                "project_id": project_id,
                "semantic_context_gate": semantic_gate,
                "tool_plan": tool_plan,
                "next_frontier": "context_discovery",
                "next_question": "El Semantic Context Gate no encontró contexto suficiente para avanzar con seguridad. Amplía lectura read-only o confirma una fuente contextual.",
            }

    # Construir context_pack antes del routing: las retomas lo usan para decidir si hace falta executor.
    context_level_arg = arguments.get("context_level")
    if classified.get("intent") == "resume" and classified.get("scenario") == "planning":
        default_context_pack_level = 1
    elif classified.get("intent") in {"resume", "advance"}:
        default_context_pack_level = 0
    else:
        default_context_pack_level = 1
    try:
        context_pack_level = int(context_level_arg) if context_level_arg is not None else default_context_pack_level
    except Exception:
        context_pack_level = default_context_pack_level

    versioned_memory = None
    if project_id and str(project_id) != "orchestrator":
        versioned_memory = _collect_project_versioned_memory(project_id=str(project_id), level=context_pack_level)

    session_memory = None
    # Incluir last_event solo si es relevante (coincide con proyecto actual o fue la fuente de selección).
    if active_pid and (project_query_source == "active_project" or active_pid == str(project_id)):
        session_memory = {
            "active_project_path": str(ACTIVE_PROJECT_PATH),
            "active_project_id": active_pid,
            "last_event": _extract_active_last_event_compact(active_state),
        }

    context_pack = _build_standard_context_pack(
        level=context_pack_level,
        instruction=instruction,
        mode="Plan",
        classified=classified,
        project_id=str(project_id) if project_id else None,
        project_query_source=project_query_source,
        resolution=(resolution if isinstance(resolution, dict) else None),
        onboarding=(onboarding if isinstance(onboarding, dict) else None),
        missing_files=None,
        preflight_status=preflight_parsed.get("status") if isinstance(preflight_parsed, dict) else None,
        orchestrator_summary=orchestrator_summary,
        versioned_memory=versioned_memory,
        session_memory=session_memory,
    )

    resume_analysis: dict[str, Any] | None = None
    if classified.get("intent") == "resume" and isinstance(context_pack, dict):
        resume_analysis = _analyze_resume_from_context_pack(
            context_pack=context_pack,
            instruction_normalized=str(classified.get("instruction_normalized") or ""),
        )

    # 5) Routing: seleccionar agente/modelo a partir de escenario/riesgo/volumen

    selector = select_agent_model(
        {
            "scenario": classified["scenario"],
            "risk": classified["risk"],
            "volume": classified["volume"],
            "user_premium": bool(classified.get("explicit_premium_request")),
        }
    )
    selector_parsed = selector.get("parsed") if isinstance(selector.get("parsed"), dict) else {}

    tool_plan.append({
        "tool": "select_agent_model",
        "arguments": {
            "scenario": classified["scenario"],
            "risk": classified["risk"],
            "volume": classified["volume"],
            "user_premium": bool(classified.get("explicit_premium_request")),
        },
    })

    recommended_agent = selector_parsed.get("recommended_agent")
    recommended_model = selector_parsed.get("recommended_model")
    requires_authorization = bool(selector_parsed.get("requires_authorization"))

    escalation = {
        "replit": "recommended" if classified.get("replit_triggered") else (resolution.get("escalation_decision") or {}).get("replit", "not_required"),
        "premium": "required" if classified.get("explicit_premium_request") else "not_required",
    }

    authorizations_required: list[str] = []
    if escalation.get("replit") in {"recommended", "required"}:
        authorizations_required.append("replit")

    if requires_authorization or escalation.get("premium") in {"required", "recommended"}:
        authorizations_required.append("premium")

    # 6) Próxima acción recomendada (tool call listo)
    objective = instruction
    handoff_body = (
        "Instrucción general (normalizada por MCP):\n"
        f"- instruction: {instruction}\n\n"
        "Restricciones (recordatorio):\n"
        "- Plan-only por defecto; no ejecutar comandos destructivos\n"
        "- No secrets / .env\n"
        "- No Replit/premium sin autorización\n"
    )

    # Solo sugerir dispatch automático si NO requiere autorización (no premium) y no pide Replit,
    # y el orquestador está listo para avanzar.
    safe_to_dispatch = (
        "premium" not in authorizations_required
        and "replit" not in authorizations_required
        and orchestrator_ready_to_advance
        and semantic_gate_status not in {"needs_context_review"}
    )

    recommended_next_tool_call: dict[str, Any] | None = None
    if (
        safe_to_dispatch
        and isinstance(recommended_agent, str)
        and isinstance(recommended_model, str)
        and (
            classified.get("intent") != "resume"
            or (isinstance(resume_analysis, dict) and bool(resume_analysis.get("needs_executor")))
        )
    ):

        recommended_next_tool_call = {
            "tool": "create_and_dispatch_opencode_handoff",
            "arguments": {
                "project_id": project_id or "orchestrator",
                "objective": objective,
                "handoff_body": handoff_body,
                "target_agent": recommended_agent,
                "model": recommended_model,
                "risk_level": classified["risk"],
                "scenario": classified["scenario"],
                "requires_authorization": False,
                "authorization_granted": False,
            },
        }
        tool_plan.append(recommended_next_tool_call)

    next_question = None

    if safe_to_dispatch:
        next_frontier = "dispatch_opencode"
    elif semantic_gate_status == "needs_context_review":
        next_frontier = "review_semantic_context"
        next_question = (
            "Semantic Context Gate encontró referencias relevantes. Lee las fuentes top antes de editar "
            "o despachar ejecución; luego reintenta con el contexto incorporado."
        )
    elif not orchestrator_ready_to_advance:
        next_frontier = "fix_orchestrator"
        next_question = (
            "El orquestador no está listo para avanzar (p.ej. git dirty o bloqueos operativos). "
            "Limpia/commit manualmente y reintenta, o llama plan_general_instruction con include_orchestrator_status=false."
        )
    else:
        next_frontier = "request_authorization"
        blockers = ", ".join(authorizations_required) if authorizations_required else "autorización"
        next_question = f"Se requiere {blockers} antes de despachar ejecución. ¿Autorizas? (sin autorización: solo Plan/read-only)."

    # Resume override: si la memoria versionada es suficiente, NO despachar por defecto.
    if classified.get("intent") == "resume" and isinstance(resume_analysis, dict):
        if resume_analysis.get("blocked") is True:
            next_frontier = "blocked"
            next_question = resume_analysis.get("next_question") or next_question
        elif resume_analysis.get("needs_executor") is not True:
            next_frontier = "resume_ready"
            next_question = None

    # Compact summary for Continue
    compact_message = {

        "project_id": project_id,
        "intent": classified["intent"],
        "scenario": classified["scenario"],
        "risk": classified["risk"],
        "volume": classified["volume"],
        "recommended_agent": recommended_agent,
        "recommended_model": recommended_model,
        "authorizations_required": authorizations_required,
        "next_frontier": next_frontier,
        "semantic_context_gate_status": semantic_gate_status,
    }

    return {
        "ok": True,

        "status": "ok",
        "instruction": instruction,
        "classified": classified,
        "project_id": project_id,
        "project_query_source": project_query_source,
        "context_pack_level": context_pack_level,
        "context_pack": context_pack,
        "onboarding": onboarding,
        "resume": resume_analysis,

        "preflight_status": preflight_parsed.get("status") if isinstance(preflight_parsed, dict) else None,
        "orchestrator": orchestrator_summary,
        "orchestrator_ready_to_advance": orchestrator_ready_to_advance,
        "resolution": {
            "matched_by": resolution.get("matched_by"),
            "environment_type": resolution.get("environment_type"),
            "local_path": resolution.get("local_path"),
            "git": resolution.get("git"),
        },
        "routing": {
            "recommended_agent": recommended_agent,
            "recommended_model": recommended_model,
            "requires_authorization": requires_authorization,
        },
        "escalation_decision": escalation,
        "authorizations_required": authorizations_required,
        "semantic_context_gate": semantic_gate,
        "tool_plan": tool_plan,
        "recommended_next_tool_call": recommended_next_tool_call,
        "next_frontier": next_frontier,
        "next_question": next_question,
        "compact_message_for_continue": compact_message,
        "followup_scheme_template": _build_followup_scheme(run_id=None),
    }


def _build_followup_scheme(run_id: str | None) -> dict[str, Any]:
    """Devuelve un esquema de seguimiento compact-first (no ejecuta nada)."""

    rid = run_id or "<run_id>"

    return {
        "compact_first": True,
        "run_id": run_id,
        "notes": [
            "Seguimiento recomendado (compact-first): run_health_check → check_opencode_run_status → get_run_status.",
            "Usar show_latest_run solo como fallback (preview-only) porque puede ser verboso.",
        ],
        "polling": {
            "initial_wait_seconds": 2,
            "retry_seconds": 5,
            "max_attempts": 12,
        },
        "steps": [
            {"tool": "run_health_check", "arguments": {"run_id": rid}},
            {"tool": "check_opencode_run_status", "arguments": {"run_id": rid}},
            {"tool": "get_run_status", "arguments": {"run_id": rid}},
        ],
        "fallback": [
            {
                "tool": "show_latest_run",
                "arguments": {"run_id": rid},
                "note": "preview-only; evita dumps completos salvo que el usuario lo pida",
            }
        ],
    }


def run_general_instruction_flow(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Cierra el loop: instrucción general → plan → (opcional) onboarding → dispatch controlado → seguimiento.

    - mode='plan' (default): no crea artefactos ni despacha. Solo devuelve plan + esquema de seguimiento.
    - mode='dispatch_if_safe': si la frontera es segura (sin premium/Replit/autorizaciones), ejecuta
      create_and_dispatch_opencode_handoff y devuelve run_id + followup plan compact-first.

    Onboarding:
    - Si plan_general_instruction devuelve status=onboarding_required, este flujo puede ejecutar
      init_project_onboarding_scaffold **solo** con autorización explícita:
        authorize_onboarding_scaffold_write=true

    Restricciones:
    - No usa Replit.
    - No usa premium salvo que el usuario lo autorice explícitamente mediante flags.
    - No habilita Build automático.
    """

    arguments = arguments or {}

    mode = str(arguments.get("mode") or "plan").strip().lower()
    if mode not in {"plan", "dispatch_if_safe"}:
        mode = "plan"


    authorize_onboarding_scaffold_write = bool(arguments.get("authorize_onboarding_scaffold_write", False))

    # Hands-free: si la instrucción pide procesar el último handoff del bridge,
    # enrutar internamente hacia ingest_orchestrator_transfer (Plan-only).
    instruction = str(arguments.get("instruction") or "").strip()
    classified = _classify_general_instruction(instruction)

    # Modo implícito (reducción de fricción):
    # - Si el usuario NO especifica mode, intentamos avanzar "en su integridad" sin pedir
    #   micro-orquestación manual.
    # - Mantiene Plan cuando el usuario lo marca explícitamente ("modo plan"/"solo plan").
    if "mode" not in arguments:
        norm = str(classified.get("instruction_normalized") or "")
        plan_markers = ("modo plan", "solo plan", "plan-only", "plan only")
        if any(m in norm for m in plan_markers):
            mode = "plan"
        elif classified.get("intent") in {"advance", "diagnose", "resume", "prepare_low_risk"}:
            mode = "dispatch_if_safe"


    if classified.get("intent") == "ingest_bridge_handoff":
        active_pid = None
        if classified.get("bridge_wants_active_project") is True:
            active = _read_json_file(ACTIVE_PROJECT_PATH) or {}
            active_pid = str(active.get("project_id") or "").strip() or None

        ingest_args: dict[str, Any] = {

            "handoff_json_path": str(classified.get("bridge_handoff_json_path") or "").strip(),
            "project_query": (
                str(classified.get("bridge_project_query") or "").strip()
                or str(arguments.get("project_query") or "").strip()
                or (active_pid or "")
            ),
            "workspace_path": str(arguments.get("workspace_path") or "").strip(),
            "handoff_dir": str(arguments.get("handoff_dir") or "").strip(),
            "include_git": bool(arguments.get("include_git", True)),
            "include_orchestrator_status": bool(arguments.get("include_orchestrator_status", True)),
            "include_preflight": bool(arguments.get("include_preflight", True)),
            "set_active_project": True,
        }

        # Best-effort: si se dio project_query pero no ruta, intentar inferir workspace_path.
        if (
            not ingest_args["handoff_json_path"]
            and not ingest_args["workspace_path"]
            and not ingest_args["handoff_dir"]
            and ingest_args["project_query"]
        ):
            rq = str(ingest_args["project_query"] or "").strip()
            if rq == "orchestrator":
                ingest_args["workspace_path"] = str(ROOT)
            else:
                res = resolve_target_project({"project_query": rq, "include_git": False})
                if isinstance(res, dict) and res.get("project_confirmed") is True and res.get("local_path"):
                    ingest_args["workspace_path"] = str(res.get("local_path") or "")

        if not ingest_args["handoff_json_path"] and not ingest_args["workspace_path"] and not ingest_args["handoff_dir"] and not ingest_args["project_query"]:

            return {
                "ok": True,
                "status": "missing_inputs",
                "mode": "plan",
                "instruction": instruction,
                "classified": classified,
                "next_frontier": "provide_handoff_path",
                "next_question": "Indica el proyecto (alias/project_id) o la ruta workspace_path donde corriste ./orquestador.",
            }

        ingest = ingest_orchestrator_transfer(ingest_args)

        # Best-effort: actualizar estado del proyecto activo con la última frontera.
        pid = None
        res = ingest.get("resolution") if isinstance(ingest, dict) else None
        if isinstance(res, dict) and res.get("project_confirmed") is True:
            pid = str(res.get("project_id") or "").strip() or None

        if not pid:
            aps = ingest.get("active_project_set") if isinstance(ingest, dict) else None
            if isinstance(aps, dict):
                ap = aps.get("active_project")
                if isinstance(ap, dict):
                    pid = str(ap.get("project_id") or "").strip() or None

        active_state_updated = False
        if pid:
            handoff = ingest.get("handoff") if isinstance(ingest, dict) else None
            handoff_path = handoff.get("handoff_json_path") if isinstance(handoff, dict) else None

            upd = _update_active_project_state(
                project_id=pid,
                last_event_patch={
                    "source": "run_general_instruction_flow:handsfree_bridge",
                    "mode": "plan",
                    "instruction": instruction,
                    "status": str(ingest.get("status") or "ok"),
                    "next_frontier": ingest.get("next_frontier"),
                    "next_question": ingest.get("next_question"),
                    "handoff_json_path": handoff_path,
                    "run_id": None,
                },
            )
            active_state_updated = bool(upd.get("ok"))

        return {
            "ok": True,
            "status": str(ingest.get("status") or "ok"),
            "mode": "plan",
            "routed_to": "ingest_orchestrator_transfer",
            "instruction": instruction,
            "classified": classified,
            "active_state_updated": active_state_updated,
            "ingest": ingest,
            "next_frontier": ingest.get("next_frontier"),
            "next_question": ingest.get("next_question"),
        }


    plan = plan_general_instruction(arguments)

    # Siempre devolver al menos el template de seguimiento.
    base: dict[str, Any] = {
        "ok": True,
        "status": (plan.get("status") if isinstance(plan, dict) else "ok"),
        "mode": mode,
        "plan": plan,
        "followup_scheme_template": _build_followup_scheme(run_id=None),
    }

    # Propagar context_pack/context_pack_level del plan (si existe).
    if isinstance(plan, dict):
        base["context_pack_level"] = plan.get("context_pack_level")
        base["context_pack"] = plan.get("context_pack")

    if isinstance(plan, dict) and plan.get("status") == "onboarding_required":
        mf = plan.get("missing_files")
        if not isinstance(mf, list):
            onboarding = plan.get("onboarding") if isinstance(plan.get("onboarding"), dict) else {}
            mf = onboarding.get("missing") if isinstance(onboarding.get("missing"), list) else []
        base["project_id"] = plan.get("project_id")
        base["missing_files"] = mf
        base["recommended_next_tool_call"] = plan.get("recommended_next_tool_call")
        base["next_frontier"] = plan.get("next_frontier")
        base["next_question"] = plan.get("next_question")

    # Best-effort: consolidar "proyecto activo + última frontera" para operación diaria.
    if isinstance(plan, dict):
        pid = str(plan.get("project_id") or "").strip()
        if pid:
            _update_active_project_state(
                project_id=pid,
                last_event_patch={
                    "source": "run_general_instruction_flow",
                    "mode": mode,
                    "instruction": instruction,
                    "status": plan.get("status"),
                    "next_frontier": plan.get("next_frontier"),
                    "next_question": plan.get("next_question"),
                    "handoff_json_path": None,
                    "run_id": None,
                },
            )

    # Opt-in: sincronizar referencias last_event -> docs/projects/<project-id>/ (dry_run siempre; apply solo con opt-in explícito).
    if bool(classified.get("sync_last_event_requested")) and isinstance(plan, dict):
        pid_for_sync = str(plan.get("project_id") or "").strip()
        if pid_for_sync:
            try:
                sync_preview = sync_active_last_event_to_project_docs({"project_id": pid_for_sync, "dry_run": True, "apply": False})
                base["sync_last_event"] = {"requested": True, "preview": sync_preview}
            except Exception:
                base["sync_last_event"] = {"requested": True, "preview": None, "error": "sync_preview_failed"}

            if mode == "dispatch_if_safe" and bool(classified.get("sync_last_event_apply_authorized")):
                try:
                    sync_apply = sync_active_last_event_to_project_docs({"project_id": pid_for_sync, "dry_run": False, "apply": True})
                    base["sync_last_event"]["applied"] = sync_apply
                except Exception:
                    base["sync_last_event"]["apply_error"] = "sync_apply_failed"

    if mode == "plan":
        return base



    # dispatch_if_safe
    # 0) Soportar onboarding_required con autorización explícita.
    if isinstance(plan, dict) and plan.get("status") == "onboarding_required":
        if authorize_onboarding_scaffold_write is not True:
            base["dispatch"] = {
                "attempted": False,
                "status": "onboarding_required",
                "reason": "Falta autorización explícita para crear scaffold documental (docs/projects/<project-id>/).",
            }
            base["next_frontier"] = plan.get("next_frontier")
            base["recommended_next_tool_call"] = plan.get("recommended_next_tool_call")
            base["next_question"] = (
                "Onboarding requerido. Para permitir que run_general_instruction_flow cree el scaffold mínimo en "
                "docs/projects/<project-id>/, reintenta con authorize_onboarding_scaffold_write=true. "
                "(Alternativa: llama init_project_onboarding_scaffold manualmente y luego reintenta)."
            )
            return base

        project_id = (plan.get("project_id") or "").strip()
        if not project_id or project_id == "orchestrator":
            base["dispatch"] = {
                "attempted": False,
                "status": "onboarding_required",
                "reason": "project_id inválido para onboarding (vacío o 'orchestrator').",
            }
            base["next_frontier"] = plan.get("next_frontier")
            base["recommended_next_tool_call"] = plan.get("recommended_next_tool_call")
            return base

        scaffold_result = init_project_onboarding_scaffold({"project_id": project_id, "dry_run": False})
        if scaffold_result.get("ok") is not True:
            base["dispatch"] = {
                "attempted": False,
                "status": "onboarding_scaffold_failed",
                "reason": "Falló init_project_onboarding_scaffold.",
                "result": scaffold_result,
            }
            base["next_frontier"] = "init_onboarding_scaffold"
            return base

        # Compact-first: exponer solo lo necesario (conteos + ruta)
        created = scaffold_result.get("created") if isinstance(scaffold_result, dict) else None
        skipped = scaffold_result.get("skipped") if isinstance(scaffold_result, dict) else None
        base["onboarding_scaffold"] = {
            "project_id": project_id,
            "docs_dir": scaffold_result.get("docs_dir"),
            "created_count": len(created) if isinstance(created, list) else None,
            "skipped_count": len(skipped) if isinstance(skipped, list) else None,
        }


        # Re-planificar después del scaffold, y continuar el flujo normal.
        plan = plan_general_instruction(arguments)

        base["plan"] = plan
        base["plan_refresh_summary"] = {
            "status": plan.get("status") if isinstance(plan, dict) else None,
            "next_frontier": plan.get("next_frontier") if isinstance(plan, dict) else None,
            "recommended_tool": (
                ((plan.get("recommended_next_tool_call") or {}) if isinstance(plan, dict) else {}).get("tool")
            ),
        }


    recommended = plan.get("recommended_next_tool_call") if isinstance(plan, dict) else None
    authorizations_required = plan.get("authorizations_required") if isinstance(plan, dict) else None

    # Si no hay next tool call seguro, no despachar.
    if not isinstance(recommended, dict) and isinstance(plan, dict) and plan.get("next_frontier") == "resume_ready":
        base["dispatch"] = {
            "attempted": False,
            "status": "not_required",
            "reason": "Retoma resuelta con memoria versionada/context_pack; no se requiere dispatch.",
            "authorizations_required": authorizations_required or [],
        }
        base["next_frontier"] = plan.get("next_frontier")
        base["next_question"] = plan.get("next_question")
        return base

    if not isinstance(recommended, dict):

        base["dispatch"] = {
            "attempted": False,
            "status": "not_safe_to_dispatch",
            "reason": "No hay recommended_next_tool_call seguro (requiere autorización o frontera no lista).",
            "authorizations_required": authorizations_required or [],
        }
        base["next_frontier"] = plan.get("next_frontier") if isinstance(plan, dict) else None
        base["next_question"] = plan.get("next_question") if isinstance(plan, dict) else None
        return base

    # Defensa adicional: no despachar si el plan requiere premium o Replit.
    auth_list = authorizations_required if isinstance(authorizations_required, list) else []
    if any(x in {"premium", "replit"} for x in auth_list):
        base["dispatch"] = {
            "attempted": False,
            "status": "authorization_required",
            "authorizations_required": auth_list,
            "reason": "Requiere autorización (premium y/o Replit).",
        }
        base["next_frontier"] = plan.get("next_frontier") if isinstance(plan, dict) else None
        base["next_question"] = plan.get("next_question") if isinstance(plan, dict) else None
        return base

    # En dispatch_if_safe, solo se soporta dispatch de OpenCode vía create_and_dispatch_opencode_handoff.
    next_tool = (recommended.get("tool") or "").strip()
    if next_tool != "create_and_dispatch_opencode_handoff":
        base["dispatch"] = {
            "attempted": False,
            "status": "not_dispatchable",
            "reason": f"recommended_next_tool_call.tool='{next_tool}' no es despachable por este flujo.",
        }
        base["next_frontier"] = plan.get("next_frontier") if isinstance(plan, dict) else None
        base["recommended_next_tool_call"] = recommended
        base["next_question"] = plan.get("next_question") if isinstance(plan, dict) else None
        return base

    # Intentar dispatch vía create_and_dispatch_opencode_handoff.
    rec_args = recommended.get("arguments") if isinstance(recommended.get("arguments"), dict) else {}

    dispatch_result = create_and_dispatch_opencode_handoff(rec_args)
    parsed = dispatch_result.get("parsed") if isinstance(dispatch_result, dict) else None
    parsed = parsed if isinstance(parsed, dict) else None

    run_id = parsed.get("run_id") if parsed else None

    base["dispatch"] = {
        "attempted": True,
        "tool": "create_and_dispatch_opencode_handoff",
        "arguments": rec_args,
        "result": parsed or dispatch_result,
    }

        

    if run_id:
        base["run_id"] = run_id

        base["followup_plan"] = _build_followup_scheme(run_id=str(run_id))
        # Próximo tool call directo (compact-first)
        base["recommended_next_tool_call"] = {"tool": "run_health_check", "arguments": {"run_id": str(run_id)}}

        # Persistir continuidad para "retomar" sin micro-orquestación manual.
        # Guardamos el run_id + referencia al handoff en el estado local (gitignored).
        try:
            pid = str((plan.get("project_id") if isinstance(plan, dict) else "") or "").strip()
            handoff_json_path = (parsed or {}).get("handoff_json_path") if isinstance(parsed, dict) else None
            if pid:
                _update_active_project_state(
                    project_id=pid,
                    last_event_patch={
                        "source": "run_general_instruction_flow",
                        "mode": mode,
                        "instruction": instruction,
                        "status": "dispatched",
                        "next_frontier": plan.get("next_frontier") if isinstance(plan, dict) else None,
                        "next_question": plan.get("next_question") if isinstance(plan, dict) else None,
                        "handoff_json_path": handoff_json_path,
                        "run_id": str(run_id),
                    },
                )
        except Exception:
            pass

        # Snapshot inmediato (compact-first) para reducir necesidad de llamadas MCP manuales.
        try:
            base["followup_snapshot"] = {
                "opencode": check_opencode_run_status({"run_id": str(run_id)}),
            }
        except Exception:
            base["followup_snapshot"] = None


    return base



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
    "operational_status": operational_status,
    "resolve_target_project": resolve_target_project,
    "enable_target_project": enable_target_project,

    "plan_general_instruction": plan_general_instruction,
    "run_general_instruction_flow": run_general_instruction_flow,
    "semantic_context_gate": semantic_context_gate,
    "project_context_indexer": project_context_indexer,
    "get_active_project": get_active_project,
    "set_active_project": set_active_project,
    "init_project_onboarding_scaffold": init_project_onboarding_scaffold,

    "sync_active_last_event_to_project_docs": sync_active_last_event_to_project_docs,
    "ingest_orchestrator_transfer": ingest_orchestrator_transfer,
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



