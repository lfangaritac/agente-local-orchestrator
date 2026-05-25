from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
import sys
import threading
import time
import uuid


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp_server" / "server.py"

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


def wait_for_response_id(stdout_lines: list[str], message_id: int, timeout_s: float = 20.0) -> dict | None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        for r in parse_responses(stdout_lines):
            if r.get("id") == message_id:
                return r
        time.sleep(0.05)
    return None



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


def _create_healthy_run() -> str:
    """Crea un run mínimo 'healthy' (run_dir + TRACE + RUN_SUMMARY + agent_outputs).

    Se usa para que el test sea auto-contenido y no dependa de run_ids hardcodeados
    (los runs están gitignored por política).
    """

    run_id = f"healthcheck_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "record_agent_result.py"),
            "--run-id",
            run_id,
            "--agent",
            "healthcheck-test-agent",
            "--status",
            "diagnostic",
            "--summary",
            "Synthetic agent output for MCP run_health_check stdio test.",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    assert completed.returncode == 0, f"No se pudo crear run healthy. rc={completed.returncode} stderr={completed.stderr}"

    return run_id


def _cleanup_run(run_id: str) -> None:
    try:
        run_dir = ROOT / "docs" / "agent_runs" / run_id
        if run_dir.exists():
            shutil.rmtree(run_dir, ignore_errors=True)
    except Exception:
        pass


def main() -> None:
    run_existente = _create_healthy_run()

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

    try:


        # initialize + tools/list
        send(
            proc,
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
            stderr_lines,
        )
        send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, stderr_lines)
        send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}, stderr_lines)

        tools_list_resp = wait_for_response_id(stdout_lines, 2, timeout_s=10)
        tool_names = [t.get("name") for t in (tools_list_resp or {}).get("result", {}).get("tools", [])]

        # run_health_check: existente
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "run_health_check", "arguments": {"run_id": run_existente, "stale_minutes": 15}},
            },
            stderr_lines,
        )
        resp_existente = wait_for_response_id(stdout_lines, 3, timeout_s=20)

        # run_health_check: inexistente
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "run_health_check", "arguments": {"run_id": RUN_INEXISTENTE, "stale_minutes": 15}},
            },
            stderr_lines,
        )
        resp_inexistente = wait_for_response_id(stdout_lines, 4, timeout_s=20)

        payload_existente = extract_tool_payload(resp_existente)
        payload_inexistente = extract_tool_payload(resp_inexistente)

    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

        _cleanup_run(run_existente)


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
        and payload_existente.get("run_id") == run_existente
        and payload_existente.get("health_status") == "healthy"
        and payload_existente.get("exists") is True
    )






    content_ok_inexistente = bool(
        payload_inexistente
        and payload_inexistente.get("run_id") == RUN_INEXISTENTE
        and payload_inexistente.get("health_status") == "missing"
        and payload_inexistente.get("exists") is False
    )

    result = {
        "initialize_ok": bool(wait_for_response_id(stdout_lines, 1, timeout_s=2) is not None),
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
