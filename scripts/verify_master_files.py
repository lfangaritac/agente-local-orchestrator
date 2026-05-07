"""
verify_master_files.py

Verifica físicamente la existencia e integridad SHA-256 de los archivos maestros
críticos del orquestador, reduciendo el riesgo de diagnósticos falsos por
visibilidad parcial del IDE.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_root() -> Path:
    return Path(__file__).resolve().parents[1]


MASTER_FILES = [
    "TARGET_PROJECT_CONTEXT_CONTRACT.md",
    "PROJECT_REGISTRY.md",
    "AGENT_RULES.md",
    "MODEL_ROUTING.md",
    "AGENT_ORCHESTRATION.md",
    "docs/AGENT_ORCHESTRATION.md",
    "CONTINUE_USAGE_PROTOCOL.md",
    "REPLIT_HANDOFF.md",
    "docs/protocols/PROJECT_ENABLEMENT_PROTOCOL.md",
    "docs/protocols/CONTEXT_SYNC_PROTOCOL.md",
    "docs/protocols/DOCUMENTATION_CODE_ALIGNMENT_PROTOCOL.md",
    "docs/protocols/AGENT_AUTOMATION_PROTOCOL.md",
    "docs/protocols/MCP_CONTINUE_INTEGRATION_PROTOCOL.md",
    "docs/alerts/GLOBAL_CRITICAL_ALERTS.md",
    "docs/lessons/GLOBAL_LESSONS_LEARNED.md",
]

DUPLICATE_CANDIDATE_PAIRS = [
    ("AGENT_ORCHESTRATION.md", "docs/AGENT_ORCHESTRATION.md"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_file(root: Path, rel_path: str) -> dict[str, object]:
    result: dict[str, object] = {
        "path": rel_path,
        "absolute_path": None,
        "exists": False,
        "type": "missing",
        "size_bytes": None,
        "sha256": None,
        "modified_time": None,
        "status": "missing",
        "error": None,
    }

    try:
        full = root / rel_path
        # Bloquear rutas fuera de ROOT usando relative_to, no startswith
        try:
            full.relative_to(root)
        except ValueError:
            result["error"] = "Ruta fuera de ROOT."
            result["status"] = "error"
            return result

        result["absolute_path"] = str(full.resolve())

        if not full.exists():
            result["exists"] = False
            result["type"] = "missing"
            result["status"] = "missing"
            return result

        result["exists"] = True

        if full.is_file():
            result["type"] = "file"
            result["size_bytes"] = full.stat().st_size
            result["sha256"] = sha256_file(full)
            mtime = full.stat().st_mtime
            result["modified_time"] = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
            result["status"] = "ok"
        elif full.is_dir():
            result["type"] = "directory"
            result["status"] = "ok"
        else:
            result["type"] = "other"
            result["status"] = "ok"

    except Exception as exc:
        result["error"] = str(exc)
        result["status"] = "error"

    return result


def find_duplicate_candidates(root: Path, files: list[dict[str, object]]) -> list[dict[str, object]]:
    candidates = []
    path_map = {f["path"]: f for f in files}

    for a, b in DUPLICATE_CANDIDATE_PAIRS:
        fa = path_map.get(a)
        fb = path_map.get(b)
        if fa and fb and fa.get("exists") and fb.get("exists"):
            candidates.append({
                "pair": [a, b],
                "sha256_a": fa.get("sha256"),
                "sha256_b": fb.get("sha256"),
                "same_hash": fa.get("sha256") == fb.get("sha256"),
            })

    return candidates


def verify(paths: list[str] | None = None) -> dict[str, object]:
    root = get_root()
    target_paths = paths if paths else MASTER_FILES

    files = []
    for rel in target_paths:
        files.append(verify_file(root, rel))

    existing = [f for f in files if f.get("exists")]
    missing = [f for f in files if not f.get("exists")]
    errors = [f for f in files if f.get("status") == "error"]

    duplicate_candidates = find_duplicate_candidates(root, files)

    summary = {
        "total_checked": len(files),
        "total_existing": len(existing),
        "total_missing": len(missing),
        "total_errors": len(errors),
        "missing_files": [f["path"] for f in missing],
        "duplicate_candidates": duplicate_candidates,
        "all_ok": len(missing) == 0 and len(errors) == 0,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
    }

    return {
        "ok": True,
        "files": files,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verifica archivos maestros del orquestador.")
    parser.add_argument(
        "--paths",
        nargs="+",
        help="Rutas relativas a ROOT para verificar (por defecto usa la lista maestra).",
    )
    args = parser.parse_args()

    result = verify(args.paths)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
