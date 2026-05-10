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

    QUEUE_INBOX.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)

    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    def _is_disallowed_allowed_file(path: str) -> bool:
        p = path.strip().replace("\\", "/").lower()
        disallowed_prefixes = [
            ".env",
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
        f"- model: `{args.model}`\n\n"
        "## Objective\n\n"
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

    trace_path.write_text(
        f"# TRACE — {run_id}\n\n"
        f"## Inicio — create_and_dispatch_opencode_handoff\n\n"
        f"- run_id: {run_id}\n"
        f"- timestamp: {package['timestamp']}\n"
        f"- status: created\n"
        f"- authorization: {auth_status}\n"
        f"- auto_approve_permissions: {auto_approve_permissions}\n"
        f"- build_authorized: {build_authorized}\n"
        f"- user_authorized_build: {user_authorized_build}\n"
        f"- guardrail_error: {guardrail_error}\n",
        encoding="utf-8",
    )

    summary_path.write_text(
        f"# RUN_SUMMARY — {run_id}\n\n"
        f"- status: created\n"
        f"- project_id: {args.project_id}\n"
        f"- target_agent: {args.target_agent}\n"
        f"- model: {args.model}\n"
        f"- authorization: {auth_status}\n"
        f"- auto_approve_permissions: {auto_approve_permissions}\n"
        f"- build_authorized: {build_authorized}\n"
        f"- user_authorized_build: {user_authorized_build}\n",
        encoding="utf-8",
    )

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
