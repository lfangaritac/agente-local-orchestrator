from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
import threading
import time


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp_server" / "server.py"

RUN_EXISTENTE = "20260509_103815_2841ce6d"
RUN_INEXISTENTE = "00000000_missing_test"


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
                "clientInfo": {"name": "run-health-check-test", "version": "0.1.0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "run_health_check",
                "arguments": {"run_id": RUN_EXISTENTE, "stale_minutes": 15},
            },
        },
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "run_health_check",
                "arguments": {"run_id": RUN_INEXISTENTE, "stale_minutes": 15},
            },
        },
    ]

    try:
        for msg in messages:
            send(proc, msg, stderr_lines)
            time.sleep(0.7)

        time.sleep(2.5)

    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    responses = parse_responses(stdout_lines)

    tool_names: list[str] = []
    payload_existente = None
    payload_inexistente = None

    for response in responses:
        if response.get("id") == 2:
            tools = response.get("result", {}).get("tools", [])
            tool_names = [tool.get("name") for tool in tools]

        if response.get("id") == 3:
            payload_existente = extract_tool_payload(response)

        if response.get("id") == 4:
            payload_inexistente = extract_tool_payload(response)

    required_keys = {
        "ok",
        "run_id",
        "exists",
        "health_status",
        "latest_status",
        "opencode_registered",
        "agent_outputs_count",
        "raw_outputs_count",
        "background_files_count",
        "indexed_in_RUN_INDEX",
        "archive_recommended",
        "issues",
        "recommendations",
        "elapsed_ms",
    }

    shape_ok_existente = bool(payload_existente and required_keys.issubset(set(payload_existente.keys())))
    shape_ok_inexistente = bool(payload_inexistente and required_keys.issubset(set(payload_inexistente.keys())))

    content_ok_existente = bool(
        payload_existente
        and payload_existente.get("run_id") == RUN_EXISTENTE
        and payload_existente.get("health_status") == "healthy"
    )

    content_ok_inexistente = bool(
        payload_inexistente
        and payload_inexistente.get("run_id") == RUN_INEXISTENTE
        and payload_inexistente.get("health_status") == "missing"
        and payload_inexistente.get("exists") is False
    )

    result = {
        "initialize_ok": any(r.get("id") == 1 and "result" in r for r in responses),
        "tools_list_ok": "run_health_check" in tool_names,
        "payload_shape_ok": shape_ok_existente and shape_ok_inexistente,
        "payload_content_ok": content_ok_existente and content_ok_inexistente,
        "tool_names": tool_names,
        "payload_existente": payload_existente,
        "payload_inexistente": payload_inexistente,
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
            "payload_shape_ok": result["payload_shape_ok"],
            "payload_content_ok": result["payload_content_ok"],
        }.items()
        if not ok
    ]

    if failed:
        print("FAILED_CHECKS:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
