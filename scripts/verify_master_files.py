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
import time
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

# Pairs que se consideran referencias/stubs aceptados (no duplicidad problemática).
# Regla: si ambos archivos existen, se reportan en `accepted_reference_pairs` y
# se excluyen de `duplicate_candidates`.
ACCEPTED_REFERENCE_PAIRS: list[dict[str, str]] = [
    {
        "canonical": "AGENT_ORCHESTRATION.md",
        "reference": "docs/AGENT_ORCHESTRATION.md",
        "reason": "docs/AGENT_ORCHESTRATION.md is an accepted stub/reference to the canonical root document.",
    }
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


def _accepted_pair_index() -> set[tuple[str, str]]:
    """Índice para excluir pares aceptados de duplicidad.

    Se indexa en ambas direcciones para que (a,b) y (b,a) sean equivalentes.
    """

    idx: set[tuple[str, str]] = set()
    for p in ACCEPTED_REFERENCE_PAIRS:
        a = p.get("canonical")
        b = p.get("reference")
        if a and b:
            idx.add((a, b))
            idx.add((b, a))
    return idx


def find_accepted_reference_pairs(files: list[dict[str, object]]) -> list[dict[str, object]]:
    """Reporta pares canónico→referencia aceptados cuando ambos existen."""

    accepted = []
    path_map = {f["path"]: f for f in files}

    for p in ACCEPTED_REFERENCE_PAIRS:
        canonical = p["canonical"]
        reference = p["reference"]
        reason = p.get("reason")

        fc = path_map.get(canonical)
        fr = path_map.get(reference)

        if fc and fr and fc.get("exists") and fr.get("exists"):
            accepted.append({
                "canonical": canonical,
                "reference": reference,
                "reason": reason,
                "sha256_canonical": fc.get("sha256"),
                "sha256_reference": fr.get("sha256"),
                "same_hash": fc.get("sha256") == fr.get("sha256"),
            })

    return accepted


def find_duplicate_candidates(root: Path, files: list[dict[str, object]]) -> list[dict[str, object]]:
    candidates = []
    path_map = {f["path"]: f for f in files}
    accepted_idx = _accepted_pair_index()

    for a, b in DUPLICATE_CANDIDATE_PAIRS:
        if (a, b) in accepted_idx:
            # Es un stub/referencia aceptado; no reportar como duplicidad problemática.
            continue

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

    accepted_reference_pairs = find_accepted_reference_pairs(files)
    duplicate_candidates = find_duplicate_candidates(root, files)

    summary = {
        "total_checked": len(files),
        "total_existing": len(existing),
        "total_missing": len(missing),
        "total_errors": len(errors),
        "missing_files": [f["path"] for f in missing],
        # Compatibilidad: mantener siempre la clave como lista.
        "duplicate_candidates": duplicate_candidates,
        "accepted_reference_pairs": accepted_reference_pairs,
        "duplicate_candidates_count": len(duplicate_candidates),
        "accepted_reference_pairs_count": len(accepted_reference_pairs),
        "all_ok": len(missing) == 0 and len(errors) == 0,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
    }

    return {
        "ok": True,
        "files": files,
        "summary": summary,
    }


def _summarize_accepted_reference_pairs(pairs: list[dict[str, object]], max_items: int = 20) -> tuple[list[dict[str, object]], bool]:
    """Devuelve una versión compacta de accepted_reference_pairs.

    Quita hashes largos por defecto, dejando solo campos útiles para diagnóstico.
    """

    truncated = len(pairs) > max_items
    trimmed = pairs[:max_items]

    slim: list[dict[str, object]] = []
    for p in trimmed:
        slim.append({
            "canonical": p.get("canonical"),
            "reference": p.get("reference"),
            "same_hash": p.get("same_hash"),
            "reason": p.get("reason"),
        })

    return slim, truncated


def to_compact(full_result: dict[str, object], elapsed_ms: int) -> dict[str, object]:
    summary = (full_result.get("summary") or {}) if isinstance(full_result, dict) else {}
    missing_files = summary.get("missing_files") or []
    accepted_pairs = summary.get("accepted_reference_pairs") or []

    accepted_slim, accepted_truncated = _summarize_accepted_reference_pairs(
        accepted_pairs if isinstance(accepted_pairs, list) else [],
        max_items=20,
    )

    missing_truncated = False
    if isinstance(missing_files, list) and len(missing_files) > 50:
        missing_truncated = True
        missing_files = missing_files[:50]

    truncated = bool(accepted_truncated or missing_truncated)

    return {
        "ok": bool(full_result.get("ok", True)) if isinstance(full_result, dict) else True,
        "status": "ok",
        "elapsed_ms": elapsed_ms,
        "truncated": truncated,
        "total_checked": summary.get("total_checked"),
        "total_existing": summary.get("total_existing"),
        "total_missing": summary.get("total_missing"),
        "total_errors": summary.get("total_errors"),
        "all_ok": summary.get("all_ok"),
        "duplicate_candidates_count": summary.get("duplicate_candidates_count"),
        "accepted_reference_pairs_count": summary.get("accepted_reference_pairs_count"),
        "missing_files": missing_files,
        "accepted_reference_pairs": accepted_slim,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verifica archivos maestros del orquestador.")
    parser.add_argument(
        "--paths",
        nargs="+",
        help="Rutas relativas a ROOT para verificar (por defecto usa la lista maestra).",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Imprime solo un resumen compacto (sin lista completa de archivos).",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Imprime el resultado completo (default).",
    )
    args = parser.parse_args()

    # Compatibilidad: si el usuario no pide --compact, mantener el output full.
    compact = bool(args.compact) and not bool(args.full)

    start = time.perf_counter()
    result = verify(args.paths)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    if compact:
        out = to_compact(result, elapsed_ms)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    # Full mode
    if isinstance(result, dict):
        result["elapsed_ms"] = elapsed_ms
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
