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
    if proc.poll() is not None:
        raise RuntimeError(f"Servidor MCP terminado. returncode={proc.returncode}")

    proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
    proc.stdin.flush()


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

    threading.Thread(target=reader_thread, args=(proc.stdout, stdout_lines), daemon=True).start()
    threading.Thread(target=reader_thread, args=(proc.stderr, stderr_lines), daemon=True).start()

    messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "check-opencode-run-status-test", "version": "0.1.0"}
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
                "name": "check_opencode_run_status",
                "arguments": {
                    "run_id": "20260506_171549_0e258229"
                }
            }
        }
    ]

    for msg in messages:
        send(proc, msg)
        time.sleep(0.6)

    time.sleep(3)

    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    responses = []
    for line in stdout_lines:
        try:
            responses.append(json.loads(line))
        except Exception:
            responses.append({"raw": line})

    tool_names = []
    tool_payload = None

    for response in responses:
        if response.get("id") == 2:
            tools = response.get("result", {}).get("tools", [])
            tool_names = [tool.get("name") for tool in tools]

        if response.get("id") == 3:
            tool_payload = extract_tool_payload(response)

    required_keys = {
        "ok",
        "status",
        "run_id",
        "exists",
        "opencode_registered",
        "agent_outputs_count",
        "raw_outputs_count",
        "latest_status",
        "elapsed_ms",
    }

    payload_ok = bool(tool_payload and required_keys.issubset(set(tool_payload.keys())))

    result = {
        "initialize_ok": any(r.get("id") == 1 and "result" in r for r in responses),
        "tools_list_ok": "check_opencode_run_status" in tool_names,
        "tool_call_ok": tool_payload is not None,
        "payload_shape_ok": payload_ok,
        "tool_names": tool_names,
        "tool_payload": tool_payload,
        "stderr_lines": stderr_lines,
        "server_returncode": proc.returncode,
    }

    print(json.dumps(result, ensure_ascii=True, indent=2))

    if not result["initialize_ok"] or not result["tools_list_ok"] or not result["tool_call_ok"] or not result["payload_shape_ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
