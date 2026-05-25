"""
test_create_and_dispatch_opencode_handoff_stdio.py

Prueba local del servidor MCP por stdio para la herramienta
create_and_dispatch_opencode_handoff.

Valida:
- initialize
- tools/list incluye create_and_dispatch_opencode_handoff
- tools/call con authorization_granted=false devuelve waiting_authorization
- tools/call con authorization_granted=true devuelve dispatched
- Se crean handoff_json, handoff_md, TRACE.md y RUN_SUMMARY.md
- Se devuelve run_id y next_tool=check_opencode_run_status

No conecta Continue todavía.
No ejecuta comandos arbitrarios.
"""

from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
import threading
import time


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp_server" / "server.py"
INBOX = ROOT / "docs" / "agent_queue" / "inbox"
RUNS = ROOT / "docs" / "agent_runs"


def reader_thread(pipe, lines: list[str]) -> None:
    try:
        for line in iter(pipe.readline, ""):
            if not line:
                break
            lines.append(line.rstrip("\n"))
    except Exception as exc:
        lines.append(f"READER_ERROR: {exc}")


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


def wait_for_response_id(stdout_lines: list[str], message_id: int, timeout_s: float = 25.0) -> dict | None:
    """Espera (poll) hasta que llegue una respuesta con id específico.

    Importante: create_and_dispatch_opencode_handoff ejecuta pre-gates (quick checks)
    que pueden tardar varios segundos; este helper evita flakiness por sleeps fijos.
    """

    deadline = time.time() + timeout_s

    while time.time() < deadline:
        for r in parse_responses(stdout_lines):
            if r.get("id") == message_id:
                return r
        time.sleep(0.05)

    return None



def extract_tool_result(response: dict | None) -> dict | None:
    if not response:
        return None
    content = response.get("result", {}).get("content", [])
    if not content:
        return None
    text = content[0].get("text", "")
    try:
        outer = json.loads(text)
        parsed = outer.get("parsed")
        if isinstance(parsed, dict):
            return parsed
        return outer
    except Exception:
        return None


def main() -> None:
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

        # 1) initialize + tools/list
    send(
        proc,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "create-and-dispatch-test", "version": "0.1.0"},
            },
        },
        stderr_lines,
    )
    send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, stderr_lines)
    send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}, stderr_lines)

    init_resp = wait_for_response_id(stdout_lines, 1, timeout_s=10)
    tools_list_resp = wait_for_response_id(stdout_lines, 2, timeout_s=10)

    tool_names: list[str] = []
    if tools_list_resp:
        tools = tools_list_resp.get("result", {}).get("tools", [])
        tool_names = [tool.get("name") for tool in tools]

    # 2) tools/call (sin autorización)
    send(
        proc,
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "create_and_dispatch_opencode_handoff",
                "arguments": {
                    "project_id": "orchestrator",
                    "objective": "Prueba MCP stdio de create_and_dispatch_opencode_handoff sin autorización.",
                    "target_agent": "builder",
                    "model": "opencode-go/kimi-k2.6",
                    "risk_level": "medium",
                    "scenario": "implementation",
                    "requires_authorization": True,
                    "authorization_granted": False,
                    "allowed_files": ["scripts/test.py"],
                    "validation_commands": ["python -m py_compile scripts/test.py"],
                    "auto_approve_permissions": False,
                    "build_authorized": False,
                    "user_authorized_build": False,
                },
            },
        },
        stderr_lines,
    )
    call_unauthorized_resp = wait_for_response_id(stdout_lines, 3, timeout_s=35)

    # 3) tools/call (con autorización)
    send(
        proc,
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "create_and_dispatch_opencode_handoff",
                "arguments": {
                    "project_id": "orchestrator",
                    "objective": "Prueba MCP stdio de create_and_dispatch_opencode_handoff con autorización.",
                    "target_agent": "builder",
                    "model": "opencode-go/kimi-k2.6",
                    "risk_level": "medium",
                    "scenario": "implementation",
                    "requires_authorization": True,
                    "authorization_granted": True,
                    "allowed_files": ["scripts/test.py"],
                    "validation_commands": ["python -m py_compile scripts/test.py"],
                    "auto_approve_permissions": False,
                    "build_authorized": False,
                    "user_authorized_build": False,
                },
            },
        },
        stderr_lines,
    )
    call_authorized_resp = wait_for_response_id(stdout_lines, 4, timeout_s=35)

    # Cleanup server process
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    call_unauthorized_result = extract_tool_result(call_unauthorized_resp)
    call_authorized_result = extract_tool_result(call_authorized_resp)


    # Verificar archivos creados en disco
    unauthorized_run_id = call_unauthorized_result.get("run_id") if call_unauthorized_result else None
    authorized_run_id = call_authorized_result.get("run_id") if call_authorized_result else None

    unauthorized_files_ok = False
    authorized_files_ok = False

    if unauthorized_run_id:
        json_exists = (INBOX / f"{unauthorized_run_id}.json").exists()
        md_exists = (INBOX / f"{unauthorized_run_id}.md").exists()
        trace_exists = (RUNS / unauthorized_run_id / "TRACE.md").exists()
        summary_exists = (RUNS / unauthorized_run_id / "RUN_SUMMARY.md").exists()
        unauthorized_files_ok = json_exists and md_exists and trace_exists and summary_exists

    if authorized_run_id:
        json_exists = (INBOX / f"{authorized_run_id}.json").exists()
        md_exists = (INBOX / f"{authorized_run_id}.md").exists()
        trace_exists = (RUNS / authorized_run_id / "TRACE.md").exists()
        summary_exists = (RUNS / authorized_run_id / "RUN_SUMMARY.md").exists()
        authorized_files_ok = json_exists and md_exists and trace_exists and summary_exists

    result = {
        "initialize_ok": bool(init_resp and "result" in init_resp),
        "tools_list_ok": "create_and_dispatch_opencode_handoff" in tool_names,
        "tool_names": tool_names,
        "call_unauthorized_ok": call_unauthorized_result is not None,
        "call_authorized_ok": call_authorized_result is not None,
        "unauthorized_status": call_unauthorized_result.get("status") if call_unauthorized_result else None,
        "authorized_status": call_authorized_result.get("status") if call_authorized_result else None,
        "unauthorized_run_id": unauthorized_run_id,
        "authorized_run_id": authorized_run_id,
        "unauthorized_files_ok": unauthorized_files_ok,
        "authorized_files_ok": authorized_files_ok,
        "unauthorized_next_tool": call_unauthorized_result.get("next_tool") if call_unauthorized_result else None,
        "authorized_next_tool": call_authorized_result.get("next_tool") if call_authorized_result else None,
        "stdout_lines_count": len(stdout_lines),
        "stderr_lines": stderr_lines,
        "server_returncode": proc.returncode,
    }

    print(json.dumps(result, ensure_ascii=True, indent=2))

    failed = [
        name for name, ok in {
            "initialize_ok": result["initialize_ok"],
            "tools_list_ok": result["tools_list_ok"],
            "call_unauthorized_ok": result["call_unauthorized_ok"],
            "call_authorized_ok": result["call_authorized_ok"],
            "unauthorized_waiting": result["unauthorized_status"] == "waiting_authorization",
            "authorized_dispatched": result["authorized_status"] == "dispatched",
            "unauthorized_files_ok": result["unauthorized_files_ok"],
            "authorized_files_ok": result["authorized_files_ok"],
            "unauthorized_next_tool": result["unauthorized_next_tool"] == "check_opencode_run_status",
            "authorized_next_tool": result["authorized_next_tool"] == "check_opencode_run_status",
        }.items()
        if not ok
    ]

    if failed:
        print("FAILED_CHECKS:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
