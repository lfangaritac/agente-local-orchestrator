"""
test_guardrails_autoapprove_permissions_stdio.py

Prueba de regresión por stdio del servidor MCP para el guardrail de
auto_approve_permissions (skip de permisos de OpenCode).

Objetivo:
- Validar que --dangerously-skip-permissions (auto_approve_permissions) solo
  puede usarse cuando existan señales explícitas y alcance seguro.

Diseño:
- Ejecuta MCP server por stdio.
- Invoca create_and_dispatch_opencode_handoff con combinaciones de argumentos.
- Evita dispatch real usando requires_authorization=true y authorization_granted=false.

Notas:
- La herramienta crea artefactos operativos en docs/agent_runs/** y
  docs/agent_queue/inbox/**, que están ignorados por Git.
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
        assert proc.stdin is not None
        proc.stdin.write(raw + "\n")
        proc.stdin.flush()
    except OSError as exc:
        raise RuntimeError(
            "No se pudo escribir en stdin del servidor MCP. "
            f"returncode={proc.poll()}. stderr={stderr_lines}"
        ) from exc


def parse_json_lines(stdout_lines: list[str]) -> list[dict]:
    responses: list[dict] = []
    for line in stdout_lines:
        try:
            responses.append(json.loads(line))
        except Exception:
            responses.append({"raw": line})
    return responses


def extract_tool_result(response: dict | None) -> dict | None:
    """Extrae el JSON producido por tools/call.

    El server devuelve {result: {content: [{text: "{...}"}]}}.
    Dentro de tools.py, create_and_dispatch_opencode_handoff incluye una key
    "parsed" que contiene el JSON del script subyacente.

    Para mantener el test estable, devolvemos preferentemente response.parsed.
    """

    if not response:
        return None

    content = response.get("result", {}).get("content", [])
    if not content:
        return None

    text = content[0].get("text", "")
    try:
        outer = json.loads(text)
    except Exception:
        return None

    parsed = outer.get("parsed")
    if isinstance(parsed, dict):
        return parsed

    if isinstance(outer, dict):
        return outer

    return None


def wait_for_response_id(stdout_lines: list[str], message_id: int, timeout_s: float = 10.0) -> dict | None:
    deadline = time.time() + timeout_s

    # Espera activa: el reader_thread agrega líneas en paralelo.
    while time.time() < deadline:
        responses = parse_json_lines(stdout_lines)
        for r in responses:
            if r.get("id") == message_id:
                return r
        time.sleep(0.05)

    return None


def assert_contains(haystack: str, needle: str, label: str) -> None:
    if needle not in haystack:
        raise AssertionError(f"{label}: no contiene {needle!r}. Valor: {haystack!r}")


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

    # Inicialización mínima
    try:
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "guardrails-test", "version": "0.1.0"},
                },
            },
            stderr_lines,
        )
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            },
            stderr_lines,
        )
        send(
            proc,
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            stderr_lines,
        )

        tools_list_resp = wait_for_response_id(stdout_lines, 2, timeout_s=10)
        if not tools_list_resp:
            raise RuntimeError(f"Timeout esperando tools/list. stderr={stderr_lines}")

        tool_names = [t.get("name") for t in tools_list_resp.get("result", {}).get("tools", [])]
        if "create_and_dispatch_opencode_handoff" not in tool_names:
            raise AssertionError(
                "tools/list no incluye create_and_dispatch_opencode_handoff. "
                f"tool_names={tool_names}"
            )

        # Helper para ejecutar un caso y devolver el resultado parseado.
        def call_create_and_dispatch(message_id: int, arguments: dict) -> dict:
            send(
                proc,
                {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "method": "tools/call",
                    "params": {"name": "create_and_dispatch_opencode_handoff", "arguments": arguments},
                },
                stderr_lines,
            )
            resp = wait_for_response_id(stdout_lines, message_id, timeout_s=15)
            if not resp:
                raise RuntimeError(f"Timeout esperando tools/call id={message_id}. stderr={stderr_lines}")

            parsed = extract_tool_result(resp)
            if not isinstance(parsed, dict):
                raise AssertionError(f"No se pudo extraer parsed dict para id={message_id}. resp={resp}")

            # Sanity mínima
            if not parsed.get("run_id"):
                raise AssertionError(f"Respuesta sin run_id para id={message_id}. parsed={parsed}")

            return parsed

        base_args = {
            "project_id": "orchestrator",
            "objective": "Guardrail test (auto_approve_permissions).",
            "target_agent": "builder",
            "model": "opencode-go/kimi-k2.6",
            "scenario": "implementation",
            # Importante: evitar dispatch real.
            "requires_authorization": True,
            "authorization_granted": False,
            # Señales de Build.
            "build_authorized": True,
        }

        # 1) Caso permitido
        r1 = call_create_and_dispatch(
            10,
            {
                **base_args,
                "objective": "Caso permitido: auto_approve_permissions con señales explícitas (sin dispatch real).",
                "risk_level": "low",
                "auto_approve_permissions": True,
                "user_authorized_build": True,
                "allowed_files": ["QUICK_START.md"],
                "validation_commands": [],
            },
        )
        if r1.get("status") == "blocked":
            raise AssertionError(f"Caso permitido quedó blocked. parsed={r1}")
        if r1.get("status") != "waiting_authorization":
            raise AssertionError(f"Caso permitido: status inesperado. parsed={r1}")
        if r1.get("guardrail_error") is not None:
            raise AssertionError(f"Caso permitido: guardrail_error debe ser null. parsed={r1}")

        # 2) Bloqueo por falta de user_authorized_build
        r2 = call_create_and_dispatch(
            11,
            {
                **base_args,
                "objective": "Bloqueo: falta user_authorized_build.",
                "risk_level": "low",
                "auto_approve_permissions": True,
                "user_authorized_build": False,
                "allowed_files": ["QUICK_START.md"],
            },
        )
        if r2.get("status") != "blocked":
            raise AssertionError(f"Caso 2: status esperado blocked. parsed={r2}")
        assert_contains(str(r2.get("guardrail_error") or ""), "user_authorized_build", "Caso 2 guardrail_error")

        # 3) Bloqueo por allowed_files vacío
        r3 = call_create_and_dispatch(
            12,
            {
                **base_args,
                "objective": "Bloqueo: allowed_files vacío.",
                "risk_level": "low",
                "auto_approve_permissions": True,
                "user_authorized_build": True,
                "allowed_files": [],
            },
        )
        if r3.get("status") != "blocked":
            raise AssertionError(f"Caso 3: status esperado blocked. parsed={r3}")
        assert_contains(str(r3.get("guardrail_error") or ""), "allowed_files", "Caso 3 guardrail_error")

        # 4) Bloqueo por archivo sensible (.env)
        r4 = call_create_and_dispatch(
            13,
            {
                **base_args,
                "objective": "Bloqueo: allowed_files contiene .env.",
                "risk_level": "low",
                "auto_approve_permissions": True,
                "user_authorized_build": True,
                "allowed_files": [".env"],
            },
        )
        if r4.get("status") != "blocked":
            raise AssertionError(f"Caso 4: status esperado blocked. parsed={r4}")
        assert_contains(str(r4.get("guardrail_error") or ""), "sensible/bloqueada", "Caso 4 guardrail_error")

        # 5) Bloqueo por risk_level != low
        r5 = call_create_and_dispatch(
            14,
            {
                **base_args,
                "objective": "Bloqueo: risk_level=medium.",
                "risk_level": "medium",
                "auto_approve_permissions": True,
                "user_authorized_build": True,
                "allowed_files": ["QUICK_START.md"],
            },
        )
        if r5.get("status") != "blocked":
            raise AssertionError(f"Caso 5: status esperado blocked. parsed={r5}")
        assert_contains(str(r5.get("guardrail_error") or ""), "risk_level", "Caso 5 guardrail_error")

        # 6) Bloqueo por wildcard / ruta no exacta
        r6 = call_create_and_dispatch(
            15,
            {
                **base_args,
                "objective": "Bloqueo: wildcard en allowed_files.",
                "risk_level": "low",
                "auto_approve_permissions": True,
                "user_authorized_build": True,
                "allowed_files": ["*.md"],
            },
        )
        if r6.get("status") != "blocked":
            raise AssertionError(f"Caso 6: status esperado blocked. parsed={r6}")
        assert_contains(str(r6.get("guardrail_error") or ""), "sin wildcards", "Caso 6 guardrail_error")

        # 7) Bloqueo por path traversal / ruta absoluta
        r7a = call_create_and_dispatch(
            16,
            {
                **base_args,
                "objective": "Bloqueo: path traversal en allowed_files.",
                "risk_level": "low",
                "auto_approve_permissions": True,
                "user_authorized_build": True,
                "allowed_files": ["../QUICK_START.md"],
            },
        )
        if r7a.get("status") != "blocked":
            raise AssertionError(f"Caso 7a: status esperado blocked. parsed={r7a}")
        assert_contains(str(r7a.get("guardrail_error") or ""), "rutas relativas", "Caso 7a guardrail_error")

        r7b = call_create_and_dispatch(
            17,
            {
                **base_args,
                "objective": "Bloqueo: ruta absoluta en allowed_files.",
                "risk_level": "low",
                "auto_approve_permissions": True,
                "user_authorized_build": True,
                "allowed_files": [r"C:\\Agente\\QUICK_START.md"],
            },
        )
        if r7b.get("status") != "blocked":
            raise AssertionError(f"Caso 7b: status esperado blocked. parsed={r7b}")
        assert_contains(str(r7b.get("guardrail_error") or ""), "rutas relativas", "Caso 7b guardrail_error")

        # Reporte compacto para debugging local si algo falla.
        result = {
            "ok": True,
            "cases": {
                "allowed": {"status": r1.get("status"), "guardrail_error": r1.get("guardrail_error")},
                "missing_user_authorized_build": {"status": r2.get("status"), "guardrail_error": r2.get("guardrail_error")},
                "empty_allowed_files": {"status": r3.get("status"), "guardrail_error": r3.get("guardrail_error")},
                "sensitive_file": {"status": r4.get("status"), "guardrail_error": r4.get("guardrail_error")},
                "risk_not_low": {"status": r5.get("status"), "guardrail_error": r5.get("guardrail_error")},
                "wildcard": {"status": r6.get("status"), "guardrail_error": r6.get("guardrail_error")},
                "path_traversal": {"status": r7a.get("status"), "guardrail_error": r7a.get("guardrail_error")},
                "absolute_path": {"status": r7b.get("status"), "guardrail_error": r7b.get("guardrail_error")},
            },
        }

        print(json.dumps(result, ensure_ascii=True, indent=2))

    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    # Nota: en Windows, un proceso terminado vía proc.terminate() puede retornar
    # un código no-cero (p.ej. 1). Eso no implica falla del test: las aserciones
    # anteriores validan el comportamiento real.


if __name__ == "__main__":
    main()
