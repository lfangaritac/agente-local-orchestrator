"""
test_verify_master_files_stdio.py

Prueba local del servidor MCP por stdio validando la herramienta
verify_master_files.

Valida:
- initialize
- tools/list (verify_master_files aparece)
- tools/call verify_master_files
- total_checked > 0
- sha256 presente para archivos existentes tipo file
- reporte de AGENT_ORCHESTRATION.md en raÃ­z
- reporte de docs/AGENT_ORCHESTRATION.md
- reporte de MODEL_ROUTING.md
- duplicate_candidates si aplica
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


def find_response(responses: list[dict], msg_id: int) -> dict | None:
    for r in responses:
        if r.get("id") == msg_id and "result" in r:
            return r
    return None


def extract_tool_result(response: dict | None) -> dict | None:
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
                "clientInfo": {
                    "name": "local-mcp-test-verify-master-files",
                    "version": "0.1.0",
                },
            },
        },
        {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        },
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "verify_master_files",
                "arguments": {},
            },
        },
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

    init_ok = bool(find_response(responses, 1))
    tools_list_resp = find_response(responses, 2)
    verify_resp = find_response(responses, 3)
    verify_result = extract_tool_result(verify_resp)

    # Validar que verify_master_files aparece en tools/list
    tools = []
    if tools_list_resp:
        tools = tools_list_resp.get("result", {}).get("tools", [])
    verify_in_list = any(t.get("name") == "verify_master_files" for t in tools)

    # Validar resultado de verify_master_files
    summary = verify_result.get("parsed", {}).get("summary", {}) if verify_result else {}
    files = verify_result.get("parsed", {}).get("files", []) if verify_result else []

    total_checked = summary.get("total_checked", 0)
    duplicate_candidates = summary.get("duplicate_candidates", [])

    # Buscar archivos especÃ­ficos
    file_map = {f.get("path"): f for f in files}
    orchestration_root = file_map.get("AGENT_ORCHESTRATION.md")
    orchestration_docs = file_map.get("docs/AGENT_ORCHESTRATION.md")
    model_routing = file_map.get("MODEL_ROUTING.md")

    # sha256 presente para archivos existentes tipo file
    sha256_present = any(
        f.get("type") == "file" and f.get("exists") and f.get("sha256")
        for f in files
    )

    checks = {
        "initialize_ok": init_ok,
        "tools_list_ok": bool(tools_list_resp),
        "verify_master_files_in_tools_list": verify_in_list,
        "verify_master_files_call_ok": bool(verify_resp),
        "total_checked_gt_0": total_checked > 0,
        "sha256_present_for_existing_files": sha256_present,
        "reports_agent_orchestration_root": orchestration_root is not None,
        "reports_agent_orchestration_docs": orchestration_docs is not None,
        "reports_model_routing": model_routing is not None,
        "duplicate_candidates_reported": isinstance(duplicate_candidates, list),
    }

    result = {
        "stdout_response_count": len(responses),
        "stderr_lines": stderr_lines,
        "checks": checks,
        "summary": {
            "total_checked": total_checked,
            "total_existing": summary.get("total_existing"),
            "total_missing": summary.get("total_missing"),
            "all_ok": summary.get("all_ok"),
            "duplicate_candidates_count": len(duplicate_candidates),
        },
        "file_reports": {
            "AGENT_ORCHESTRATION.md": {
                "exists": orchestration_root.get("exists") if orchestration_root else None,
                "status": orchestration_root.get("status") if orchestration_root else None,
            },
            "docs/AGENT_ORCHESTRATION.md": {
                "exists": orchestration_docs.get("exists") if orchestration_docs else None,
                "status": orchestration_docs.get("status") if orchestration_docs else None,
            },
            "MODEL_ROUTING.md": {
                "exists": model_routing.get("exists") if model_routing else None,
                "status": model_routing.get("status") if model_routing else None,
            },
        },
    }

    print(json.dumps(result, ensure_ascii=True, indent=2))

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("FAILED_CHECKS:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()

