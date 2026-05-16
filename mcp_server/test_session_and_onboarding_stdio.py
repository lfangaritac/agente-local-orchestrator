"""
test_session_and_onboarding_stdio.py

Valida por stdio (JSON-RPC) las herramientas nuevas:
- get_active_project
- set_active_project
- init_project_onboarding_scaffold

No ejecuta OpenCode.
No modifica proyectos externos.
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


def reader_thread(pipe, lines: list[str]) -> None:
    for line in iter(pipe.readline, ""):
        if not line:
            break
        lines.append(line.rstrip("\n"))


def send(proc: subprocess.Popen, payload: dict) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    proc.stdin.write(raw + "\n")
    proc.stdin.flush()


def parse_responses(lines: list[str]) -> list[dict]:
    parsed: list[dict] = []
    for line in lines:
        try:
            parsed.append(json.loads(line))
        except Exception:
            parsed.append({"raw": line})
    return parsed


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

    messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "local-mcp-test", "version": "0.1.0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_active_project", "arguments": {}}},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "set_active_project", "arguments": {"project_id": "orchestrator", "note": "stdio test"}},
        },
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "get_active_project", "arguments": {}}},
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "init_project_onboarding_scaffold", "arguments": {"project_id": "data-privacy-management-d", "dry_run": False}},
        },
    ]

    for msg in messages:
        send(proc, msg)
        time.sleep(0.35)

    time.sleep(1.5)

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

    responses = parse_responses(stdout_lines)

    def has_result(msg_id: int) -> bool:
        return any(r.get("id") == msg_id and "result" in r for r in responses)

    result = {
        "stdout_response_count": len(responses),
        "stderr_lines": stderr_lines,
        "checks": {
            "initialize_ok": has_result(1),
            "get_active_project_ok": has_result(2),
            "set_active_project_ok": has_result(3),
            "get_active_project_after_set_ok": has_result(4),
            "init_onboarding_ok": has_result(5),
        },
    }

    print(json.dumps(result, ensure_ascii=True, indent=2))

    failed = [name for name, ok in result["checks"].items() if not ok]
    if failed:
        print("FAILED_CHECKS:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
