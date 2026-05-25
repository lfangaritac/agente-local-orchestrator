from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
import sys
import threading
import time


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp_server" / "server.py"
STATE_DIR = ROOT / ".orchestrator_state"


def reader_thread(pipe, lines: list[str]) -> None:
    for line in iter(pipe.readline, ""):
        if not line:
            break
        lines.append(line.rstrip("\n"))


def send(proc: subprocess.Popen, payload: dict, stderr_lines: list[str]) -> None:
    if proc.poll() is not None:
        raise RuntimeError(
            "El servidor MCP terminó antes de recibir el mensaje. "
            f"returncode={proc.returncode}. stderr={stderr_lines}"
        )

    raw = json.dumps(payload, ensure_ascii=False)

    try:
        proc.stdin.write(raw + "\n")
        proc.stdin.flush()
    except OSError as exc:
        raise RuntimeError(
            "No se pudo escribir en stdin del servidor MCP. "
            f"returncode={proc.poll()}. stderr={stderr_lines}"
        ) from exc


def parse_responses(stdout_lines: list[str]) -> list[dict]:
    responses: list[dict] = []
    for line in stdout_lines:
        try:
            responses.append(json.loads(line))
        except Exception:
            responses.append({"raw": line})
    return responses


def extract_tool_payload(response: dict | None) -> dict | None:
    if not response:
        return None
    result = response.get("result", {})
    content = result.get("content", [])
    if not content:
        return None
    text = content[0].get("text", "")
    try:
        return json.loads(text)
    except Exception:
        return None


def _run(cmd: list[str], cwd: Path) -> None:
    completed = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}. stderr={completed.stderr} stdout={completed.stdout}")


def _write_registry_fixture(path: Path) -> None:
    content = """# PROJECT_REGISTRY.md

## Propósito

Registro maestro de proyectos objetivo habilitados en el orquestador local.

## Proyectos registrados

### existing-proj

project_id: existing-proj
nombre_canónico: Existing Project
alias_permitidos: exist, alpha
ruta_local:
repositorio_remoto: https://github.com/example/existing
origen: local
environment_type: local
repo_url: https://github.com/example/existing
replit_workspace_path:
replit_join_url:
local_path: null
stack_detectado: unknown
documentación_principal:
código_fuente_relevante:
estado_sincronización: unknown
alertas_críticas:
lecciones_locales:
último_análisis:
responsable: unknown
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    base = STATE_DIR / "_tmp_enablement_test"
    registry_path = base / "PROJECT_REGISTRY.md"
    docs_projects_root = base / "docs" / "projects"

    workspace = base / "workspaceA"
    workspace.mkdir(parents=True, exist_ok=True)

    # Fixture registry (in gitignored state dir)
    _write_registry_fixture(registry_path)

    # Create local git repo to test remote mismatch
    if not (workspace / ".git").exists():
        _run(["git", "init"], cwd=workspace)
        _run(["git", "remote", "add", "origin", "https://github.com/example/repoA"], cwd=workspace)

    proc = subprocess.Popen(
        [sys.executable, str(SERVER)],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    t_out = threading.Thread(target=reader_thread, args=(proc.stdout, stdout_lines), daemon=True)
    t_err = threading.Thread(target=reader_thread, args=(proc.stderr, stderr_lines), daemon=True)
    t_out.start()
    t_err.start()

    messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "enable-target-project-test", "version": "0.1.0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        # Plan: proyecto nuevo con local_path inexistente
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "enable_target_project",
                "arguments": {
                    "mode": "plan",
                    "project_id": "new-proj",
                    "nombre_canónico": "New Project",
                    "aliases": ["np"],
                    "repo_url": "https://github.com/example/new-proj",
                    "local_path": str(base / "missing_local"),
                    "environment_type": "local",
                    "test_mode": True,
                    "registry_path": str(registry_path),
                    "docs_projects_root": str(docs_projects_root),
                },
            },
        },
        # Apply sin confirm
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "enable_target_project",
                "arguments": {
                    "mode": "apply",
                    "project_id": "new-proj",
                    "confirm": False,
                    "test_mode": True,
                    "registry_path": str(registry_path),
                    "docs_projects_root": str(docs_projects_root),
                },
            },
        },
        # Apply confirmado
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "enable_target_project",
                "arguments": {
                    "mode": "apply",
                    "project_id": "new-proj",
                    "confirm": True,
                    "nombre_canónico": "New Project",
                    "aliases": ["np"],
                    "repo_url": "https://github.com/example/new-proj",
                    "local_path": str(base / "missing_local"),
                    "environment_type": "local",
                    "test_mode": True,
                    "registry_path": str(registry_path),
                    "docs_projects_root": str(docs_projects_root),
                },
            },
        },
        # Idempotencia: aplicar dos veces
        {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "enable_target_project",
                "arguments": {
                    "mode": "apply",
                    "project_id": "new-proj",
                    "confirm": True,
                    "test_mode": True,
                    "registry_path": str(registry_path),
                    "docs_projects_root": str(docs_projects_root),
                },
            },
        },
        # Alias colisionado
        {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "enable_target_project",
                "arguments": {
                    "mode": "plan",
                    "project_id": "other-proj",
                    "aliases": ["alpha"],
                    "test_mode": True,
                    "registry_path": str(registry_path),
                    "docs_projects_root": str(docs_projects_root),
                },
            },
        },
        # Mismatch repo_url vs remote origin
        {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "enable_target_project",
                "arguments": {
                    "mode": "plan",
                    "project_id": "mismatch-proj",
                    "repo_url": "https://github.com/example/Different",
                    "local_path": str(workspace),
                    "environment_type": "local",
                    "test_mode": True,
                    "registry_path": str(registry_path),
                    "docs_projects_root": str(docs_projects_root),
                },
            },
        },
    ]

    try:
        for msg in messages:
            send(proc, msg, stderr_lines)
            time.sleep(0.7)

        time.sleep(2.4)

    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    responses = parse_responses(stdout_lines)

    tool_names: list[str] = []
    payloads: dict[int, dict] = {}

    for response in responses:
        if response.get("id") == 2:
            tools = response.get("result", {}).get("tools", [])
            tool_names = [tool.get("name") for tool in tools]

        if response.get("id") in {3, 4, 5, 6, 7, 8}:
            payload = extract_tool_payload(response)
            if payload is not None:
                payloads[int(response["id"])] = payload

    # Assertions
    tools_list_ok = "enable_target_project" in tool_names

    p3 = payloads.get(3) or {}
    case_plan_ok = (
        p3.get("status") in {"plan_ready", "plan_blocked"}
        and p3.get("mode") == "plan"
        and p3.get("project_id") == "new-proj"
        and isinstance(p3.get("registry", {}).get("entry_markdown"), str)
    )

    p4 = payloads.get(4) or {}
    case_apply_requires_confirm_ok = p4.get("status") == "confirmation_required"

    p5 = payloads.get(5) or {}
    scaffold_created = p5.get("scaffold", {}).get("created")
    case_apply_confirmed_ok = (
        p5.get("status") == "applied"
        and p5.get("registry", {}).get("changed") is True
        and isinstance(scaffold_created, list)
        and len(scaffold_created) > 5
    )

    # Idempotencia: registry no cambia en segundo apply
    p6 = payloads.get(6) or {}
    case_idempotent_ok = (
        p6.get("status") == "applied"
        and p6.get("registry", {}).get("changed") in {False, None}
        and isinstance(p6.get("scaffold", {}).get("skipped"), list)
    )

    p7 = payloads.get(7) or {}
    case_alias_collision_ok = p7.get("status") == "alias_collision"

    p8 = payloads.get(8) or {}
    case_mismatch_ok = (
        p8.get("status") == "plan_blocked"
        and p8.get("safe_to_apply") is False
        and isinstance(p8.get("mismatch"), dict)
    )

    # Verify registry file actually got entry once
    reg_text = registry_path.read_text(encoding="utf-8", errors="replace")
    registry_once_ok = reg_text.count("### new-proj") == 1

    # Verify scaffold exists (docs/projects/new-proj/*)
    docs_dir = docs_projects_root / "new-proj"
    scaffold_exists_ok = docs_dir.exists() and (docs_dir / "PROJECT_PROFILE.md").exists()

    result = {
        "tools_list_ok": tools_list_ok,
        "case_plan_ok": case_plan_ok,
        "case_apply_requires_confirm_ok": case_apply_requires_confirm_ok,
        "case_apply_confirmed_ok": case_apply_confirmed_ok,
        "case_idempotent_ok": case_idempotent_ok,
        "case_alias_collision_ok": case_alias_collision_ok,
        "case_mismatch_ok": case_mismatch_ok,
        "registry_once_ok": registry_once_ok,
        "scaffold_exists_ok": scaffold_exists_ok,
        "tool_names": tool_names,
        "payloads": payloads,
        "stderr_lines": stderr_lines,
        "server_returncode": proc.returncode,
        "stdout_lines_count": len(stdout_lines),
    }

    print(json.dumps(result, ensure_ascii=True, indent=2))

    failed = [
        name
        for name, ok in {
            "tools_list_ok": result["tools_list_ok"],
            "case_plan_ok": result["case_plan_ok"],
            "case_apply_requires_confirm_ok": result["case_apply_requires_confirm_ok"],
            "case_apply_confirmed_ok": result["case_apply_confirmed_ok"],
            "case_idempotent_ok": result["case_idempotent_ok"],
            "case_alias_collision_ok": result["case_alias_collision_ok"],
            "case_mismatch_ok": result["case_mismatch_ok"],
            "registry_once_ok": result["registry_once_ok"],
            "scaffold_exists_ok": result["scaffold_exists_ok"],
        }.items()
        if not ok
    ]

    # Cleanup (best-effort)
    try:
        shutil.rmtree(base)
    except Exception:
        pass

    if failed:
        print("FAILED_CHECKS:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
