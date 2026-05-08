"""
server.py

Servidor MCP local mínimo por stdio para Continue.

Fase v0.1:
- Implementación JSON-RPC 2.0 básica.
- Expone herramientas diagnósticas del orquestador.
- No ejecuta comandos arbitrarios.
- No edita código.
- No accede a secrets.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from schemas import TOOL_SCHEMAS
from tools import call_tool


os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


SERVER_INFO = {
    "name": "agente-local-orchestrator",
    "version": "0.1.0",
}


def respond(message_id: Any, result: Any = None, error: Any = None) -> None:
    payload: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": message_id,
    }

    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result

    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def log(message: str) -> None:
    sys.stderr.write(message + "\n")
    sys.stderr.flush()


def as_tool_content(data: Any) -> dict[str, Any]:
    is_error = bool(isinstance(data, dict) and data.get("ok") is False)
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    limit = 32768

    if len(raw) > limit:
        data = {
            "ok": not is_error,
            "truncated": True,
            "original_chars": len(raw),
            "preview_chars": limit,
            "preview": raw[:limit],
        }
        raw = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    return {
        "content": [
            {
                "type": "text",
                "text": raw,
            }
        ],
        "isError": is_error,
    }



def handle_initialize(params: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {},
        },
        "serverInfo": SERVER_INFO,
    }


def handle_tools_list() -> dict[str, Any]:
    return {
        "tools": TOOL_SCHEMAS,
    }


def handle_tools_call(params: dict[str, Any] | None = None) -> dict[str, Any]:
    params = params or {}
    name = params.get("name")
    arguments = params.get("arguments") or {}

    if not name:
        return as_tool_content({
            "ok": False,
            "error": "Falta params.name.",
        })

    result = call_tool(str(name), arguments)
    return as_tool_content(result)


def handle_request(message: dict[str, Any]) -> None:
    message_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}

    try:
        if method == "initialize":
            respond(message_id, handle_initialize(params))
            return

        if method == "tools/list":
            respond(message_id, handle_tools_list())
            return

        if method == "tools/call":
            respond(message_id, handle_tools_call(params))
            return

        if method == "ping":
            respond(message_id, {})
            return

        if method and method.startswith("notifications/"):
            return

        respond(
            message_id,
            error={
                "code": -32601,
                "message": f"Método no soportado: {method}",
            },
        )

    except Exception as exc:
        respond(
            message_id,
            error={
                "code": -32603,
                "message": "Error interno del servidor MCP.",
                "data": str(exc),
            },
        )


def main() -> None:
    log("MCP server agente-local-orchestrator iniciado por stdio.")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            respond(
                None,
                error={
                    "code": -32700,
                    "message": "JSON inválido.",
                    "data": str(exc),
                },
            )
            continue

        handle_request(message)


if __name__ == "__main__":
    main()
