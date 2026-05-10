"""
create_and_dispatch_opencode_handoff.py

Crea un paquete de handoff completo, lo persiste en docs/agent_queue/inbox,
inicializa TRACE.md y RUN_SUMMARY.md en docs/agent_runs/<run_id>,
y despacha OpenCode en segundo plano si está autorizado.

Este script no ejecuta comandos arbitrarios.
Solo invoca scripts probados del orquestador.
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
QUEUE_INBOX = ROOT / "docs" / "agent_queue" / "inbox"
RUNS = ROOT / "docs" / "agent_runs"

# ---------------------------------------------------------------------------
# Pre-gate: operational_status check
# ---------------------------------------------------------------------------
sys.path.insert(0, str(ROOT))
from scripts.audit_agent_artifacts import compute_operational_status  # noqa: E402
from scripts.apply_to_project import parse_registry, resolve_project  # noqa: E402
sys.path.pop(0)


def _run_pregate() -> dict:
    """Run operational-status pre-gate.

    Returns compact pre_gate dict on success.
    Exits script with error message on failure.
    """
    result_dict, _exit_code = compute_operational_status(
        include_git_status=True,
        run_quick_checks=True,
        verify_master_files=True,
    )

    build_blocked = bool(result_dict.get("build_blocked", False))
    ready_to_advance = bool(result_dict.get("ready_to_advance", False))
    overall_status = str(result_dict.get("overall_status", "error") or "error")

    if build_blocked or not ready_to_advance or overall_status != "ok":
        block_info = {
            "ok": False,
            "status": "blocked_pre_gate",
            "pre_gate": {
                "build_blocked": build_blocked,
                "ready_to_advance": ready_to_advance,
                "overall_status": overall_status,
                "blockers": result_dict.get("blockers", []),
                "runner_quick": result_dict.get("runner_quick", {}),
                "verify_master_files": result_dict.get("verify_master_files", {}),
                "git_clean": result_dict.get("git_clean"),
                "elapsed_ms": result_dict.get("elapsed_ms"),
            },
            "blockers": result_dict.get("blockers", []),
            "next_action": result_dict.get("next_action"),
        }
        print(json.dumps(block_info, ensure_ascii=False, indent=2))
        sys.exit(1)

    return {
        "build_blocked": build_blocked,
        "ready_to_advance": ready_to_advance,
        "overall_status": overall_status,
        "git_clean": result_dict.get("git_clean"),
        "runner_quick_status": result_dict.get("runner_quick", {}).get("status"),
        "master_files_status": result_dict.get("verify_master_files", {}).get("status"),
        "elapsed_ms": result_dict.get("elapsed_ms"),
    }


def _resolve_target_project(
    project_id: str,
    project_query: str | None,
    registry_path: Path,
) -> dict | None:
    """Resolve target project from PROJECT_REGISTRY.

    Returns resolved target_project dict on success, None if resolution is skipped
    (orchestrator with no --project). Exits script with error on failure.
    """
    skip_keywords = {"orchestrator", "none", ""}

    if project_query:
        query = project_query
        resolution_source = "--project flag"
    elif project_id.lower() in skip_keywords:
        return None
    else:
        query = project_id
        resolution_source = "project_id auto-resolution"

    entries, warnings = parse_registry(registry_path)
    resolve_result = resolve_project(query, entries)

    resolve_result["resolution_source"] = resolution_source
    resolve_result["query"] = query

    if warnings:
        resolve_result.setdefault("warnings", []).extend(warnings)

    if not resolve_result["ok"]:
        block_info = {
            "ok": False,
            "status": "blocked_target_project",
            "target_project": resolve_result,
            "errors": resolve_result.get("errors", []),
            "warnings": resolve_result.get("warnings", []),
        }
        print(json.dumps(block_info, ensure_ascii=False, indent=2))
        sys.exit(1)

    return resolve_result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--handoff-body", default="")
    parser.add_argument("--target-agent", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--risk-level", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--allowed-files", action="append", default=[])
    parser.add_argument("--validation-commands", action="append", default=[])
    parser.add_argument("--requires-authorization", type=str, default="false")
    parser.add_argument("--authorization-granted", type=str, default="false")
    parser.add_argument(
        "--project",
        default=None,
        help="Project ID, alias, nombre canónico o ruta a resolver desde PROJECT_REGISTRY. "
             "Si no se pasa y project_id != 'orchestrator', se intenta resolver usando project_id.",
    )
    parser.add_argument(
        "--registry-path",
        default=None,
        help="Ruta al archivo PROJECT_REGISTRY.md (default: ROOT/PROJECT_REGISTRY.md).",
    )

    # Guardrail: auto-approve de permisos (OpenCode) es peligroso.
    # Debe estar apagado por defecto y solo habilitarse con autorización explícita.
    parser.add_argument("--auto-approve-permissions", type=str, default="false")
    parser.add_argument(
        "--build-authorized",
        type=str,
        default="false",
        help="Marcador explícito: el usuario autorizó modo Build para esta ejecución (requerido si auto_approve_permissions=true).",
    )
    parser.add_argument(
        "--user-authorized-build",
        type=str,
        default="false",
        help="Señal explícita adicional: el usuario autorizó Build real con permisos autoaprobados (requerido si auto_approve_permissions=true).",
    )

    args = parser.parse_args()

    requires_auth = args.requires_authorization.lower() == "true"
    auth_granted = args.authorization_granted.lower() == "true"

    auto_approve_permissions = args.auto_approve_permissions.lower() == "true"
    build_authorized = args.build_authorized.lower() == "true"
    user_authorized_build = args.user_authorized_build.lower() == "true"

    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + os.urandom(4).hex()

    compact_pregate = _run_pregate()

    # Resolve target project BEFORE creating any artifacts.
    registry_path = (
        Path(args.registry_path).expanduser().resolve()
        if args.registry_path
        else ROOT / "PROJECT_REGISTRY.md"
    )
    target_project = _resolve_target_project(
        project_id=args.project_id,
        project_query=args.project,
        registry_path=registry_path,
    )

    QUEUE_INBOX.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)

    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    def _is_disallowed_allowed_file(path: str) -> bool:
        p = path.strip().replace("\\", "/").lower()
        disallowed_prefixes = [
            ".env",
            ".gitignore",
            ".continueignore",
            "secrets",
            "docs/agent_runs/",
            "docs/agent_queue/",
            "raw_outputs",
            "deployment",
            "deploy",
            "migrations",
            "infra",
            "infrastructure",
            "opencode.json",
            "opencode.config.example.json",
        ]
        return any(p == pref or p.startswith(pref) for pref in disallowed_prefixes)

    def _is_exact_relative_path(path: str) -> bool:
        s = path.strip().replace("\\", "/")
        if not s:
            return False
        if s.startswith("/") or ":" in s.split("/")[0]:
            return False
        if ".." in s.split("/"):
            return False
        if any(ch in s for ch in ["*", "?", "[", "]"]):
            return False
        return True

    def _normalize_path(path: str) -> str:
        p = str(path)
        p = p.strip()
        p = p.replace("\\", "/")
        while p.startswith("./"):
            p = p[2:]
        return p

    # Normalize and deduplicate allowed_files before any validation or output.
    raw_allowed = args.allowed_files or []
    normalized_allowed = [_normalize_path(f) for f in raw_allowed]
    seen: set[str] = set()
    deduped_allowed: list[str] = []
    for p in normalized_allowed:
        if p not in seen:
            seen.add(p)
            deduped_allowed.append(p)

    # Guardrails previos al dispatch.
    guardrail_error: str | None = None
    if auto_approve_permissions:
        if not build_authorized:
            guardrail_error = "auto_approve_permissions=true requiere build_authorized=true."
        elif not user_authorized_build:
            guardrail_error = "auto_approve_permissions=true requiere user_authorized_build=true."
        elif str(args.risk_level).lower().strip() != "low":
            guardrail_error = "auto_approve_permissions solo permitido con risk_level=low."
        elif not deduped_allowed:
            guardrail_error = "auto_approve_permissions requiere allowed_files no vacío."
        else:
            for f in deduped_allowed:
                if not _is_exact_relative_path(f):
                    guardrail_error = f"allowed_files debe contener rutas relativas exactas (sin wildcards): {f!r}"
                    break
                if _is_disallowed_allowed_file(f):
                    guardrail_error = f"allowed_files contiene ruta sensible/bloqueada para auto_approve_permissions: {f!r}"
                    break

    package = {
        "run_id": run_id,
        "project_id": args.project_id,
        "objective": args.objective,
        "handoff_body": args.handoff_body,
        "target_agent": args.target_agent,
        "model": args.model,
        "risk_level": args.risk_level,
        "scenario": args.scenario,
        "allowed_files": deduped_allowed,
        "validation_commands": args.validation_commands,
        "requires_authorization": requires_auth,
        "authorization_granted": auth_granted,
        "auto_approve_permissions": auto_approve_permissions,
        "build_authorized": build_authorized,
        "user_authorized_build": user_authorized_build,
        "status": "created",
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "guardrail_error": guardrail_error,
        "pre_gate": compact_pregate,
    }

    if target_project is not None:
        package["target_project"] = {
            "ok": target_project["ok"],
            "project_found": target_project["project_found"],
            "matched_by": target_project["matched_by"],
            "project": target_project["project"],
            "candidates": target_project.get("candidates", []),
            "errors": target_project.get("errors", []),
            "warnings": target_project.get("warnings", []),
            "resolution_source": target_project["resolution_source"],
            "query": target_project["query"],
        }

    json_path = QUEUE_INBOX / f"{run_id}.json"
    md_path = QUEUE_INBOX / f"{run_id}.md"

    json_path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

    allowed_files_md = "\n".join(f"- `{f}`" for f in deduped_allowed) if deduped_allowed else "- N/A"
    validation_commands_md = "\n".join(f"- `{c}`" for c in args.validation_commands) if args.validation_commands else "- N/A"

    md_content = (
        "# Handoff Package\n\n"
        f"- run_id: `{run_id}`\n"
        f"- project_id: `{args.project_id}`\n"
        f"- target_agent: `{args.target_agent}`\n"
        f"- scenario: `{args.scenario}`\n"
        f"- risk_level: `{args.risk_level}`\n"
        f"- model: `{args.model}`\n"
        f"- pre_gate_overall: `{compact_pregate['overall_status']}`\n"
        f"- pre_gate_git_clean: `{compact_pregate['git_clean']}`\n"
        f"- pre_gate_runner_quick: `{compact_pregate['runner_quick_status']}`\n"
        f"- pre_gate_master_files: `{compact_pregate['master_files_status']}`\n"
    )

    if target_project is not None:
        tp = target_project["project"] or {}
        md_content += (
            f"- target_project_id: `{tp.get('id', '')}`\n"
            f"- target_project_name: `{tp.get('name', '')}`\n"
            f"- target_project_path: `{tp.get('path', '')}`\n"
            f"- target_project_matched_by: `{target_project['matched_by']}`\n"
            f"- target_project_resolution_source: `{target_project['resolution_source']}`\n"
        )

    md_content += (
        "\n## Objective\n\n"
        f"{args.objective}\n\n"
        "## Handoff Body\n\n"
        f"{args.handoff_body}\n\n"
        "## Allowed Files\n\n"
        f"{allowed_files_md}\n\n"
        "## Validation Commands\n\n"
        f"{validation_commands_md}\n\n"
        "## Authorization\n\n"
        f"- requires_authorization: `{requires_auth}`\n"
        f"- authorization_granted: `{auth_granted}`\n\n"
        "## Permissions (guardrails)\n\n"
        f"- auto_approve_permissions: `{auto_approve_permissions}`\n"
        f"- build_authorized: `{build_authorized}`\n"
        f"- user_authorized_build: `{user_authorized_build}`\n"
        f"- guardrail_error: `{guardrail_error}`\n\n"
        "## Status\n\ncreated\n"
    )
    md_path.write_text(md_content, encoding="utf-8")

    trace_path = run_dir / "TRACE.md"
    summary_path = run_dir / "RUN_SUMMARY.md"

    auth_status = "granted" if auth_granted else ("pending" if requires_auth else "not_required")

    trace_lines = (
        f"# TRACE — {run_id}\n\n"
        f"## Inicio — create_and_dispatch_opencode_handoff\n\n"
        f"- run_id: {run_id}\n"
        f"- timestamp: {package['timestamp']}\n"
        f"- status: created\n"
        f"- authorization: {auth_status}\n"
        f"- auto_approve_permissions: {auto_approve_permissions}\n"
        f"- build_authorized: {build_authorized}\n"
        f"- user_authorized_build: {user_authorized_build}\n"
        f"- guardrail_error: {guardrail_error}\n"
        f"- pre_gate_overall: {compact_pregate['overall_status']}\n"
        f"- pre_gate_git_clean: {compact_pregate['git_clean']}\n"
        f"- pre_gate_runner_quick: {compact_pregate['runner_quick_status']}\n"
        f"- pre_gate_master_files: {compact_pregate['master_files_status']}\n"
        f"- pre_gate_elapsed_ms: {compact_pregate['elapsed_ms']}\n"
    )

    if target_project is not None:
        tp = target_project["project"] or {}
        trace_lines += (
            f"- target_project_id: {tp.get('id', '')}\n"
            f"- target_project_name: {tp.get('name', '')}\n"
            f"- target_project_path: {tp.get('path', '')}\n"
            f"- target_project_matched_by: {target_project['matched_by']}\n"
            f"- target_project_resolution_source: {target_project['resolution_source']}\n"
        )

    trace_path.write_text(trace_lines, encoding="utf-8")

    summary_lines = (
        f"# RUN_SUMMARY — {run_id}\n\n"
        f"- status: created\n"
        f"- project_id: {args.project_id}\n"
        f"- target_agent: {args.target_agent}\n"
        f"- model: {args.model}\n"
        f"- authorization: {auth_status}\n"
        f"- auto_approve_permissions: {auto_approve_permissions}\n"
        f"- build_authorized: {build_authorized}\n"
        f"- user_authorized_build: {user_authorized_build}\n"
        f"- pre_gate_overall: {compact_pregate['overall_status']}\n"
        f"- pre_gate_git_clean: {compact_pregate['git_clean']}\n"
        f"- pre_gate_runner_quick: {compact_pregate['runner_quick_status']}\n"
        f"- pre_gate_master_files: {compact_pregate['master_files_status']}\n"
        f"- pre_gate_elapsed_ms: {compact_pregate['elapsed_ms']}\n"
    )

    if target_project is not None:
        tp = target_project["project"] or {}
        summary_lines += (
            f"- target_project_id: {tp.get('id', '')}\n"
            f"- target_project_name: {tp.get('name', '')}\n"
            f"- target_project_path: {tp.get('path', '')}\n"
            f"- target_project_matched_by: {target_project['matched_by']}\n"
            f"- target_project_resolution_source: {target_project['resolution_source']}\n"
        )

    summary_path.write_text(summary_lines, encoding="utf-8")

    background_meta_path = None

    if guardrail_error:
        status = "blocked"
    elif requires_auth and not auth_granted:
        status = "waiting_authorization"
    else:
        status = "dispatched"
        background_dir = run_dir / "background"
        background_dir.mkdir(parents=True, exist_ok=True)

        timestamp_str = datetime.datetime.now().isoformat(timespec="seconds").replace(":", "-")
        stdout_path = background_dir / f"{timestamp_str}_opencode_async_stdout.log"
        stderr_path = background_dir / f"{timestamp_str}_opencode_async_stderr.log"
        background_meta_path = background_dir / f"{timestamp_str}_opencode_async_meta.json"

        env = os.environ.copy()
        env.setdefault("PYTHONUTF8", "1")
        env.setdefault("PYTHONIOENCODING", "utf-8")

        command = [
            sys.executable,
            str(ROOT / "scripts" / "run_opencode_from_handoff.py"),
            "--run-id",
            run_id,
            "--agent",
            args.target_agent,
            "--model",
            args.model,
            "--prompt",
            f"Lee el handoff {run_id} y actúa según el objetivo: {args.objective}",
        ]

        # Solo permitir skip de permisos cuando está explícitamente autorizado y guardraileado.
        if auto_approve_permissions:
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
            "status": "started",
            "run_id": run_id,
            "pid": proc.pid,
            "agent": args.target_agent,
            "model": args.model,
            "command": command,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "meta_path": str(background_meta_path),
            "started_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "auto_approve_permissions": auto_approve_permissions,
            "build_authorized": build_authorized,
            "user_authorized_build": user_authorized_build,
        }
        background_meta_path.write_text(json.dumps(meta, ensure_ascii=True, indent=2), encoding="utf-8")

    result = {
        "ok": True,
        "status": status,
        "run_id": run_id,
        "handoff_json_path": str(json_path),
        "handoff_md_path": str(md_path),
        "run_dir": str(run_dir),
        "trace_path": str(trace_path),
        "summary_path": str(summary_path),
        "background_meta_path": str(background_meta_path) if background_meta_path else None,
        "target_agent": args.target_agent,
        "model": args.model,
        "next_tool": "check_opencode_run_status",
        "auto_approve_permissions": auto_approve_permissions,
        "build_authorized": build_authorized,
        "user_authorized_build": user_authorized_build,
        "guardrail_error": guardrail_error,
        "user_message": f"Handoff '{run_id}' creado. Estado: {status}.",
    }

    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
