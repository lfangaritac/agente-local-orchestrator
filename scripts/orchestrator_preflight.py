"""
orchestrator_preflight.py

Preflight semiautomático del orquestador local.

Objetivo:
- Identificar si existe contexto mínimo para iniciar una tarea.
- Verificar archivos transversales obligatorios.
- Reportar alertas/lecciones disponibles.
- Operar en modo diagnóstico, no ejecución.

Este script no modifica archivos.
"""

from __future__ import annotations

from pathlib import Path
import json
import datetime


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "TARGET_PROJECT_CONTEXT_CONTRACT.md",
    "PROJECT_REGISTRY.md",
    "AGENT_RULES.md",
    "MODEL_ROUTING.md",
    "AGENT_ORCHESTRATION.md",
    "CONTINUE_USAGE_PROTOCOL.md",
    "REPLIT_HANDOFF.md",
    "docs/protocols/PROJECT_ENABLEMENT_PROTOCOL.md",
    "docs/protocols/CONTEXT_SYNC_PROTOCOL.md",
    "docs/protocols/DOCUMENTATION_CODE_ALIGNMENT_PROTOCOL.md",
    "docs/protocols/AGENT_AUTOMATION_PROTOCOL.md",
    "docs/alerts/GLOBAL_CRITICAL_ALERTS.md",
    "docs/lessons/GLOBAL_LESSONS_LEARNED.md",
]


def check_required_files() -> list[dict]:
    results = []
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        results.append({
            "path": rel,
            "exists": path.exists(),
            "type": "file" if path.is_file() else "missing",
        })
    return results


def main() -> None:
    now = datetime.datetime.now().isoformat(timespec="seconds")
    checks = check_required_files()
    missing = [item["path"] for item in checks if not item["exists"]]

    result = {
        "timestamp": now,
        "root": str(ROOT),
        "mode": "diagnostic",
        "required_files": checks,
        "missing_files": missing,
        "status": "ok" if not missing else "context_incomplete",
        "next_action": (
            "Contexto transversal mínimo disponible."
            if not missing
            else "Faltan fuentes obligatorias. Operar en modo diagnóstico."
        ),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
