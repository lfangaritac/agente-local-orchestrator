#!/usr/bin/env python3
"""orchestrator_bridge.py

Shell-friendly bridge para transferir intención hacia el Orquestador (Continue/MCP)
SIN activar Replit Agent.

Objetivo:
- Generar un handoff compacto (MD + JSON) que el usuario pueda llevar a Continue.
- No ejecutar diagnósticos amplios.
- No modificar código funcional.
- No leer ni imprimir secrets.

Este script está pensado para copiarse a proyectos (incl. Replit) vía scripts/apply_to_project.py.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _detect_workspace_path(explicit: str | None) -> str:
    if explicit:
        return str(Path(explicit).expanduser())
    try:
        return str(Path.cwd())
    except Exception:
        return ""


def _read_git_remote_origin(workspace: Path) -> str | None:
    """Best-effort: lee .git/config sin invocar git.

    Importante:
    - Read-only.
    - No intenta autenticarse.
    - Si no existe, devuelve None.
    """

    cfg = workspace / ".git" / "config"
    if not cfg.exists() or not cfg.is_file():
        return None

    try:
        text = cfg.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    # Parse mínimo: buscar bloque [remote "origin"] y su url.
    in_origin = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            in_origin = line.lower() == '[remote "origin"]'
            continue
        if in_origin and line.lower().startswith("url") and "=" in line:
            _, url = line.split("=", 1)
            u = url.strip()
            return u or None

    return None


@dataclass
class BridgeRequest:
    instruction: str
    project_id: str | None
    workspace_path: str
    intent: str
    channel: str


def _infer_intent(instruction: str, return_to_replit_flag: bool) -> str:
    if return_to_replit_flag:
        return "return_to_replit"

    norm = (instruction or "").strip().lower()
    if norm in {"volver a replit", "volver a repl", "volver replit", "return to replit"}:
        return "return_to_replit"

    return "orchestrator_transfer"


def _build_handoff(req: BridgeRequest) -> dict[str, Any]:
    return {
        "mode": "orchestrator_transfer",
        "channel": req.channel,
        "timestamp": _now_iso_utc(),
        "intent": req.intent,
        "instruction": req.instruction,
        "project": {
            "project_id": req.project_id,
        },
        "workspace": {
            "path": req.workspace_path,
        },
        "assertions": {
            "replit_agent_executed": False,
            "functional_changes_made": False,
            "no_secrets_read_or_printed": True,
            "no_build_test_db_migrations_deploy": True,
        },
        "next_destination": "continue_orchestrator",
        "notes": [
            "Este handoff fue generado por vía Shell/no-agent.",
            "Replit Agent sigue disponible cuando el usuario lo pida explícitamente o cuando el Orquestador lo recomiende y el usuario autorice.",
        ],
    }


def _render_markdown(handoff: dict[str, Any], *, git_origin: str | None) -> str:
    # Mantenerlo corto y pegable.
    origin_line = f"- git_origin (best-effort): `{git_origin}`\n" if git_origin else ""

    payload = json.dumps(handoff, ensure_ascii=False, indent=2)

    return (
        "# Orchestrator Transfer (Shell Bridge)\n\n"
        "Copia este bloque en Continue (Orquestador local).\n\n"
        "## Resumen\n"
        f"- mode: `{handoff.get('mode')}`\n"
        f"- channel: `{handoff.get('channel')}`\n"
        f"- intent: `{handoff.get('intent')}`\n"
        f"- timestamp: `{handoff.get('timestamp')}`\n"
        f"- project_id: `{(handoff.get('project') or {}).get('project_id')}`\n"
        f"- workspace_path: `{(handoff.get('workspace') or {}).get('path')}`\n"
        f"{origin_line}"
        "- Declaración: No se ejecutó Replit Agent.\n"
        "- Declaración: No se modificaron archivos funcionales.\n\n"
        "## Handoff (JSON)\n"
        "```json\n"
        f"{payload}\n"
        "```\n\n"
        "## Volver manualmente a Replit Agent\n"
        "Si quieres que Replit Agent ejecute/valide, indícalo explícitamente (p.ej. \"que lo ejecute Replit Agent\" / \"usar Replit Agent para validar\").\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bridge Shell: genera un handoff compacto para el Orquestador sin activar Replit Agent."
    )

    parser.add_argument(
        "instruction",
        nargs="*",
        help="Texto libre de instrucción a transferir al Orquestador. Ej: orquestador 'Avanza hasta la siguiente frontera segura'",
    )

    parser.add_argument("--project-id", default=None, help="project_id si lo conoces (opcional).")
    parser.add_argument(
        "--workspace-path",
        default=None,
        help="Ruta del workspace (opcional; default: cwd).",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directorio donde se generarán los handoffs (default: ./docs/handoffs si existe; si no, cwd).",
    )
    parser.add_argument(
        "--return-to-replit",
        action="store_true",
        help="Marca la intención como return_to_replit (alternativa a escribir 'volver a replit').",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Si está presente, imprime el handoff Markdown por stdout.",
    )

    args = parser.parse_args()

    instruction = _safe_text(" ".join(args.instruction))
    if not instruction:
        raise SystemExit("instruction es obligatorio. Usa: orquestador \"<texto>\" o python scripts/orchestrator_bridge.py \"<texto>\"")

    workspace_path = _detect_workspace_path(args.workspace_path)
    workspace = Path(workspace_path) if workspace_path else Path.cwd()

    intent = _infer_intent(instruction, bool(args.return_to_replit))

    req = BridgeRequest(
        instruction=instruction,
        project_id=_safe_text(args.project_id) or None,
        workspace_path=workspace_path,
        intent=intent,
        channel="shell_bridge",
    )

    handoff = _build_handoff(req)

    # Best-effort workspace metadata (read-only)
    git_origin = _read_git_remote_origin(workspace)
    if git_origin:
        (handoff.get("workspace") or {})["git_origin"] = git_origin

    md = _render_markdown(handoff, git_origin=git_origin)

    # Output dir
    default_dir = workspace / "docs" / "handoffs"
    out_dir = Path(args.output_dir).expanduser() if args.output_dir else (default_dir if default_dir.exists() else workspace)
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    suffix = secrets.token_hex(3)
    base = f"orchestrator_transfer_{stamp}_{suffix}"

    json_path = out_dir / f"{base}.json"
    md_path = out_dir / f"{base}.md"

    json_path.write_text(json.dumps(handoff, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")

    result = {
        "ok": True,
        "status": "ok",
        "created": {
            "json": str(json_path),
            "md": str(md_path),
        },
        "handoff": handoff,
        "notes": [
            "No se ejecutó Replit Agent.",
            "No se modificaron archivos funcionales.",
        ],
    }

    if args.stdout:
        print(md)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # Defensa: este script no debe depender de REPLIT Agent ni de variables sensibles.
    # No leer .env ni imprimir entorno.
    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    main()
