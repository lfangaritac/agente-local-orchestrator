"""
test_mcp_stdio.py

Prueba local del servidor MCP por stdio usando JSON-RPC.

Valida:
- initialize
- tools/list
- tools/call orchestrator_preflight
- tools/call select_agent_model
- tools/call run_diagnostic_flow sin OpenCode

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
    parsed = []
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
                "clientInfo": {
                    "name": "local-mcp-test",
                    "version": "0.1.0"
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        },
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "orchestrator_preflight",
                "arguments": {}
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "select_agent_model",
                "arguments": {
                    "scenario": "context-validation",
                    "risk": "medium",
                    "volume": "high"
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "run_diagnostic_flow",
                "arguments": {
                    "project_id": "orchestrator",
                    "scenario": "context-validation",
                    "risk": "medium",
                    "volume": "high",
                    "objective": "Prueba MCP stdio v0.1 sin OpenCode.",
                    "with_opencode": False
                }
            }
        }
    ]

    for msg in messages:
        send(proc, msg)
        time.sleep(0.4)

    time.sleep(2.0)

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

    responses = parse_responses(stdout_lines)

    result = {
        "stdout_response_count": len(responses),
        "stderr_lines": stderr_lines,
        "responses": responses,
        "checks": {
            "initialize_ok": any(r.get("id") == 1 and "result" in r for r in responses),
            "tools_list_ok": any(r.get("id") == 2 and "result" in r for r in responses),
            "preflight_call_ok": any(r.get("id") == 3 and "result" in r for r in responses),
            "select_agent_model_ok": any(r.get("id") == 4 and "result" in r for r in responses),
            "run_diagnostic_flow_ok": any(r.get("id") == 5 and "result" in r for r in responses),
        }
    }

    print(json.dumps(result, ensure_ascii=True, indent=2))

    failed = [name for name, ok in result["checks"].items() if not ok]
    if failed:
        print("FAILED_CHECKS:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
