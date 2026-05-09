from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
import threading
import time


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp_server" / "server.py"

FIXTURE_RUN_ID = "TEST_RUN_STATUS_FIXTURE"


def ensure_fixture_run(run_id: str = FIXTURE_RUN_ID) -> str:
    """Crea un run mínimo en disco para que el test no dependa de evidencia versionada."""

    runs_dir = ROOT / "docs" / "agent_runs" / run_id
    inbox_dir = ROOT / "docs" / "agent_queue" / "inbox"

    (runs_dir / "agent_outputs").mkdir(parents=True, exist_ok=True)
    (runs_dir / "raw_outputs").mkdir(parents=True, exist_ok=True)
    (runs_dir / "background").mkdir(parents=True, exist_ok=True)
    inbox_dir.mkdir(parents=True, exist_ok=True)

    # Handoff mínimo
    (inbox_dir / f"{run_id}.json").write_text("{}\n", encoding="utf-8")
    (inbox_dir / f"{run_id}.md").write_text(f"# HANDOFF {run_id}\n", encoding="utf-8")

    # Evidencia mínima para status/trace
    (runs_dir / "RUN_SUMMARY.md").write_text(
        "# RUN_SUMMARY\n\n## Estado general\nÚltimo estado registrado: `diagnostic`\n",
        encoding="utf-8",
    )
    (runs_dir / "TRACE.md").write_text(
        f"# TRACE — {run_id}\n\n## 2026-05-09T00:00:00 — context-validator\n- status: `diagnostic`\n",
        encoding="utf-8",
    )

    # Un output de OpenCode mínimo
    (runs_dir / "agent_outputs" / "2026-05-09T00-00-00_context-validator_opencode.json").write_text(
        '{"status":"diagnostic"}\n',
        encoding="utf-8",
    )
    (runs_dir / "raw_outputs" / "2026-05-09T00-00-00_context-validator_opencode_raw.json").write_text(
        '{"status":"diagnostic"}\n',
        encoding="utf-8",
    )

    return run_id


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


def main() -> None:
    run_id = ensure_fixture_run()

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
                    "name": "get-run-status-test",
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
                "name": "get_run_status",
                "arguments": {
                    "run_id": run_id
                }
            }
        }
    ]

    try:
        for msg in messages:
            send(proc, msg, stderr_lines)
            time.sleep(0.7)

        time.sleep(3)

    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    responses = parse_responses(stdout_lines)

    tool_names = []
    get_run_status_result = None

    for response in responses:
        if response.get("id") == 2:
            tools = response.get("result", {}).get("tools", [])
            tool_names = [tool.get("name") for tool in tools]

        if response.get("id") == 3:
            get_run_status_result = response.get("result")

    result = {
        "initialize_ok": any(r.get("id") == 1 and "result" in r for r in responses),
        "tools_list_ok": "get_run_status" in tool_names,
        "get_run_status_call_ok": get_run_status_result is not None,
        "tool_names": tool_names,
        "get_run_status_result": get_run_status_result,
        "stdout_lines_count": len(stdout_lines),
        "stderr_lines": stderr_lines,
        "server_returncode": proc.returncode,
    }

    print(json.dumps(result, ensure_ascii=True, indent=2))

    failed = [
        name for name, ok in {
            "initialize_ok": result["initialize_ok"],
            "tools_list_ok": result["tools_list_ok"],
            "get_run_status_call_ok": result["get_run_status_call_ok"],
        }.items()
        if not ok
    ]

    if failed:
        print("FAILED_CHECKS:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
