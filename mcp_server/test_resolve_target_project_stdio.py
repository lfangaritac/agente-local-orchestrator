from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import threading
import time


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp_server" / "server.py"


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


def _is_allowed_recommendation(value: str) -> bool:
    return value in {"not_required", "optional", "recommended", "required"}


def main() -> None:
    # Usar un projects_root temporal para forzar clone_required=true (sin tocar proyectos reales).
    with tempfile.TemporaryDirectory(prefix="agente_projects_root_") as tmp_root:
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
                    "clientInfo": {"name": "resolve-target-project-test", "version": "0.1.0"},
                },
            },
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            # Caso: proyecto no confirmado (sin inputs)
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "resolve_target_project",
                    "arguments": {},
                },
            },
            # Caso: no encontrado
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "resolve_target_project",
                    "arguments": {"project_query": "__definitely_not_a_project__"},
                },
            },
            # Caso: resolver por workspace_path=orquestador (repo git existente)
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "resolve_target_project",
                    "arguments": {"workspace_path": str(ROOT), "include_git": True},
                },
            },
            # Caso: resolver por alias (si existe en registry) pero forzar clone_required
            {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "resolve_target_project",
                    "arguments": {
                        "project_query": "dpm",
                        "projects_root": tmp_root,
                        "include_git": False,
                    },
                },
            },
        ]

        try:
            for msg in messages:
                send(proc, msg, stderr_lines)
                time.sleep(0.7)

            time.sleep(2.8)

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

            if response.get("id") in {3, 4, 5, 6}:
                payload = extract_tool_payload(response)
                if payload is not None:
                    payloads[int(response["id"])] = payload

        # Assertions mínimas
        tools_list_ok = "resolve_target_project" in tool_names

        # id=3: missing project info => project_not_confirmed
        p3 = payloads.get(3) or {}
        case_no_confirm_ok = (
            p3.get("project_not_confirmed") is True
            and p3.get("next_frontier") == "confirm_project"
            and isinstance(p3.get("next_question"), str)
        )

        # id=4: not found => project_not_confirmed
        p4 = payloads.get(4) or {}
        case_not_found_ok = (
            p4.get("project_not_confirmed") is True
            and p4.get("next_frontier") == "confirm_project"
        )

        # id=5: orchestrator repo should confirm
        p5 = payloads.get(5) or {}
        git_info = p5.get("git") if isinstance(p5.get("git"), dict) else {}
        case_workspace_orchestrator_ok = (
            p5.get("project_confirmed") is True
            and p5.get("project_id") == "orchestrator"
            and p5.get("git_repo_exists") is True
            and isinstance(git_info.get("branch"), str)
        )

        # id=6: dpm with tmp projects_root should suggest clone_required when registry contains it
        p6 = payloads.get(6) or {}
        case_dpm_clone_required_ok = True
        if p6.get("project_confirmed") is True:
            case_dpm_clone_required_ok = (
                p6.get("project_id") == "data-privacy-management-d"
                and p6.get("clone_required") is True
                and p6.get("next_frontier") == "prepare_workspace"
            )

        # Anti-sesgo: recommendations must be from allowed set (no 'never')
        def _check_escalation(payload: dict) -> bool:
            esc = payload.get("escalation_decision")
            if not isinstance(esc, dict):
                return False
            return _is_allowed_recommendation(str(esc.get("replit"))) and _is_allowed_recommendation(
                str(esc.get("premium"))
            )

        anti_bias_ok = all(_check_escalation(p) for p in payloads.values() if isinstance(p, dict))

        result = {
            "initialize_ok": any(r.get("id") == 1 and "result" in r for r in responses),
            "tools_list_ok": tools_list_ok,
            "case_no_confirm_ok": case_no_confirm_ok,
            "case_not_found_ok": case_not_found_ok,
            "case_workspace_orchestrator_ok": case_workspace_orchestrator_ok,
            "case_dpm_clone_required_ok": case_dpm_clone_required_ok,
            "anti_bias_ok": anti_bias_ok,
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
                "initialize_ok": result["initialize_ok"],
                "tools_list_ok": result["tools_list_ok"],
                "case_no_confirm_ok": result["case_no_confirm_ok"],
                "case_not_found_ok": result["case_not_found_ok"],
                "case_workspace_orchestrator_ok": result["case_workspace_orchestrator_ok"],
                "case_dpm_clone_required_ok": result["case_dpm_clone_required_ok"],
                "anti_bias_ok": result["anti_bias_ok"],
            }.items()
            if not ok
        ]

        if failed:
            print("FAILED_CHECKS:", ", ".join(failed))
            sys.exit(1)


if __name__ == "__main__":
    main()
