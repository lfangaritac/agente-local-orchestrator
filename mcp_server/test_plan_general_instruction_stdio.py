from __future__ import annotations

from pathlib import Path
import json
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
                    "clientInfo": {"name": "plan-general-instruction-test", "version": "0.1.0"},
                },
            },
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            # Caso: sin proyecto (debe pedir confirmación)
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "plan_general_instruction",
                    "arguments": {
                        "instruction": "Diagnostica este proyecto.",
                        "include_orchestrator_status": False,
                        "include_preflight": False,
                    },
                },
            },
            # Caso: workspace_path=orquestador (debe recomendar dispatch Go read-only)
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "plan_general_instruction",
                    "arguments": {
                        "instruction": "Diagnostica este proyecto.",
                        "workspace_path": str(ROOT),
                        "include_git": False,
                        "include_orchestrator_status": False,
                        "include_preflight": False,
                    },
                },
            },
            # Caso: dpm con projects_root temporal para forzar clone_required
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "plan_general_instruction",
                    "arguments": {
                        "instruction": "Evalua si requiere Replit o premium.",
                        "project_query": "dpm",
                        "projects_root": tmp_root,
                        "include_git": False,
                        "include_orchestrator_status": False,
                        "include_preflight": False,
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

            if response.get("id") in {3, 4, 5}:
                payload = extract_tool_payload(response)
                if payload is not None:
                    payloads[int(response["id"])] = payload

        tools_list_ok = "plan_general_instruction" in tool_names

        p3 = payloads.get(3) or {}
        case_no_project_ok = (
            p3.get("status") == "project_not_confirmed"
            and p3.get("next_frontier") == "confirm_project"
            and isinstance(p3.get("next_question"), str)
        )

        p4 = payloads.get(4) or {}
        next_call = p4.get("recommended_next_tool_call") if isinstance(p4, dict) else None
        case_orchestrator_workspace_ok = (
            p4.get("status") == "ok"
            and p4.get("project_id") == "orchestrator"
            and isinstance(next_call, dict)
            and next_call.get("tool") == "create_and_dispatch_opencode_handoff"
        )

        # Escalamiento decisions should be from allowed set
        def _check_escalation(payload: dict) -> bool:
            esc = payload.get("escalation_decision")
            if not isinstance(esc, dict):
                return False
            return _is_allowed_recommendation(str(esc.get("replit"))) and _is_allowed_recommendation(
                str(esc.get("premium"))
            )

        anti_bias_ok = all(
            _check_escalation(p)
            for p in payloads.values()
            if isinstance(p, dict) and isinstance(p.get("escalation_decision"), dict)
        )

        p5 = payloads.get(5) or {}
        case_dpm_prepare_workspace_ok = True
        if p5.get("project_id") is not None:
            case_dpm_prepare_workspace_ok = (
                p5.get("status") == "workspace_not_ready"
                and p5.get("next_frontier") == "prepare_workspace"
            )

        result = {
            "initialize_ok": any(r.get("id") == 1 and "result" in r for r in responses),
            "tools_list_ok": tools_list_ok,
            "case_no_project_ok": case_no_project_ok,
            "case_orchestrator_workspace_ok": case_orchestrator_workspace_ok,
            "case_dpm_prepare_workspace_ok": case_dpm_prepare_workspace_ok,
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
                "case_no_project_ok": result["case_no_project_ok"],
                "case_orchestrator_workspace_ok": result["case_orchestrator_workspace_ok"],
                "case_dpm_prepare_workspace_ok": result["case_dpm_prepare_workspace_ok"],
                "anti_bias_ok": result["anti_bias_ok"],
            }.items()
            if not ok
        ]

        if failed:
            print("FAILED_CHECKS:", ", ".join(failed))
            sys.exit(1)


if __name__ == "__main__":
    main()
