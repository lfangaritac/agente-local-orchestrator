"""audit_agent_artifacts.py

Auditoría *read-only* de artefactos operacionales del orquestador.

Objetivo:
- Mantener eficiencia operativa y working tree limpio.
- Evitar que runs/handoffs/raw_outputs/logs se usen como contexto base.
- Reportar (sin abrir contenidos) conteos/tamaños y candidatos a limpieza.

Importante:
- NO borra nada.
- Modo dry-run por defecto (único modo en esta iteración).

Salida:
- JSON compacto con totales + resumen por run.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import os
import subprocess
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "docs" / "agent_runs"
INBOX_DIR = ROOT / "docs" / "agent_queue" / "inbox"
RUN_INDEX = ROOT / "docs" / "context" / "RUN_INDEX.md"


@dataclass(frozen=True)
class RunArtifactSummary:
    run_id: str
    exists: bool
    agent_outputs_count: int
    raw_outputs_count: int
    background_files_count: int
    total_bytes: int
    registered_in_run_index: bool


def _safe_list_dirs(path: Path) -> list[Path]:
    try:
        return sorted([p for p in path.iterdir() if p.is_dir()])
    except Exception:
        return []


def _safe_glob(path: Path, pattern: str) -> list[Path]:
    try:
        return sorted(path.glob(pattern))
    except Exception:
        return []


def _sum_bytes(paths: Iterable[Path]) -> int:
    total = 0
    for p in paths:
        try:
            if p.is_file():
                total += p.stat().st_size
        except Exception:
            continue
    return total


def _read_text_small(path: Path, max_chars: int = 200_000) -> str:
    """Lee un archivo de texto con límite (para evitar cargar artefactos enormes)."""

    try:
        if not path.exists() or not path.is_file():
            return ""
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""


def is_registered_in_run_index(run_id: str) -> bool:
    text = _read_text_small(RUN_INDEX, max_chars=200_000)
    return run_id in text


def summarize_run(run_id: str) -> RunArtifactSummary:
    run_dir = RUNS_DIR / run_id

    agent_outputs = _safe_glob(run_dir / "agent_outputs", "*.json")
    raw_outputs = _safe_glob(run_dir / "raw_outputs", "*.json")
    background = []
    if (run_dir / "background").exists():
        background = [p for p in (run_dir / "background").glob("*") if p.is_file()]

    # Tamaño aproximado: contar solo archivos dentro de subcarpetas esperadas + TRACE/RUN_SUMMARY
    extra = []
    for name in ["TRACE.md", "RUN_SUMMARY.md", "RESULTADO_PARA_CHAT.md", "validation_output.log"]:
        p = run_dir / name
        if p.exists() and p.is_file():
            extra.append(p)

    total_bytes = _sum_bytes(agent_outputs) + _sum_bytes(raw_outputs) + _sum_bytes(background) + _sum_bytes(extra)

    return RunArtifactSummary(
        run_id=run_id,
        exists=run_dir.exists(),
        agent_outputs_count=len(agent_outputs),
        raw_outputs_count=len(raw_outputs),
        background_files_count=len(background),
        total_bytes=total_bytes,
        registered_in_run_index=is_registered_in_run_index(run_id),
    )


def git_dirty_porcelain() -> dict[str, object]:
    """Devuelve un resumen compacto del estado git (sin imprimir diffs)."""

    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc), "dirty": None}

    lines = [ln for ln in (completed.stdout or "").splitlines() if ln.strip()]
    return {
        "ok": completed.returncode == 0,
        "dirty": bool(lines),
        "entries": len(lines),
        "returncode": completed.returncode,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audita artefactos operacionales (read-only).")
    parser.add_argument("--run-id", default=None, help="Si se indica, audita solo ese run_id.")
    parser.add_argument("--max-runs", type=int, default=50, help="Máximo de runs a reportar (default 50).")
    parser.add_argument(
        "--large-file-kb",
        type=int,
        default=512,
        help="Umbral (KB) para reportar candidatos a archivo grande (default 512KB).",
    )
    parser.add_argument(
        "--include-git-status",
        action="store_true",
        help="Incluye resumen de `git status --porcelain`.",
    )
    args = parser.parse_args()

    # Runs disponibles (carpetas). Ojo: ignorar README/notes en docs/agent_runs.
    run_dirs = [p for p in _safe_list_dirs(RUNS_DIR) if p.name and not p.name.endswith(".md")]

    if args.run_id:
        target_ids = [args.run_id]
    else:
        # Orden por mtime desc (best-effort), sin fallar si stat falla.
        def _mtime(p: Path) -> float:
            try:
                return p.stat().st_mtime
            except Exception:
                return 0.0

        run_dirs = sorted(run_dirs, key=_mtime, reverse=True)
        target_ids = [p.name for p in run_dirs[: max(0, args.max_runs)]]

    summaries = [summarize_run(run_id) for run_id in target_ids]

    # Archivos grandes (best-effort): solo scan de files bajo agent_runs (sin leer contenido)
    large_threshold = int(args.large_file_kb) * 1024
    large_files: list[dict[str, object]] = []
    try:
        for p in RUNS_DIR.rglob("*"):
            if not p.is_file():
                continue
            try:
                size = p.stat().st_size
            except Exception:
                continue
            if size >= large_threshold:
                large_files.append({"path": str(p.relative_to(ROOT)).replace("\\", "/"), "bytes": size})
    except Exception:
        pass

    large_files = sorted(large_files, key=lambda x: int(x.get("bytes") or 0), reverse=True)[:25]

    # Inbox counts (solo conteo/size)
    inbox_json = _safe_glob(INBOX_DIR, "*.json")
    inbox_md = _safe_glob(INBOX_DIR, "*.md")

    result: dict[str, object] = {
        "ok": True,
        "status": "ok",
        "root": str(ROOT),
        "runs_dir_exists": RUNS_DIR.exists(),
        "inbox_dir_exists": INBOX_DIR.exists(),
        "counts": {
            "runs_dirs": len(run_dirs),
            "reported_runs": len(summaries),
            "inbox_json": len(inbox_json),
            "inbox_md": len(inbox_md),
        },
        "runs": [
            {
                "run_id": s.run_id,
                "exists": s.exists,
                "agent_outputs": s.agent_outputs_count,
                "raw_outputs": s.raw_outputs_count,
                "background_files": s.background_files_count,
                "total_kb": round(s.total_bytes / 1024, 1),
                "registered_in_run_index": s.registered_in_run_index,
            }
            for s in summaries
        ],
        "large_files_top": large_files,
        "policy": {
            "dry_run_only": True,
            "do_not_version": [
                "docs/agent_runs/<run_id>/**",
                "docs/agent_queue/inbox/<run_id>.*",
                "**/raw_outputs/**",
                "**/*stdout*.log",
                "**/*stderr*.log",
            ],
            "traceability": "Use docs/context/RUN_INDEX.md + run_id + tool check_opencode_run_status/get_run_status (compact-first).",
        },
    }

    if args.include_git_status:
        result["git"] = git_dirty_porcelain()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
