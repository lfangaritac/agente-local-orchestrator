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
import sys
import time
import zipfile
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


def _resolve_within_root(path: Path) -> Path:
    """Resuelve y bloquea rutas fuera del repo ROOT."""

    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("Ruta fuera de ROOT (bloqueada).") from exc
    return resolved


def _iter_files_recursive(base_dir: Path) -> list[Path]:
    try:
        return [p for p in base_dir.rglob("*") if p.is_file()]
    except Exception:
        return []


def archive_run(run_id: str, archive_dir_arg: str) -> dict[str, object]:
    """Crea un zip no destructivo con evidencia local del run.

    Incluye (si existen):
    - docs/agent_runs/<run_id>/**
    - docs/agent_queue/inbox/<run_id>.{md,json}

    No borra ni mueve originales.
    """

    start = time.perf_counter()

    # Resolver destino dentro de ROOT
    archive_dir = Path(archive_dir_arg)
    if not archive_dir.is_absolute():
        archive_dir = ROOT / archive_dir

    try:
        archive_dir = _resolve_within_root(archive_dir)
    except Exception as exc:
        return {
            "ok": False,
            "status": "error",
            "run_id": run_id,
            "error": f"archive_dir inválido: {exc}",
            "archive_dir": str(archive_dir),
        }

    archive_dir.mkdir(parents=True, exist_ok=True)

    run_dir = RUNS_DIR / run_id
    inbox_md = INBOX_DIR / f"{run_id}.md"
    inbox_json = INBOX_DIR / f"{run_id}.json"

    files_to_add: list[tuple[Path, str]] = []

    if run_dir.exists() and run_dir.is_dir():
        for f in _iter_files_recursive(run_dir):
            try:
                rel = f.relative_to(ROOT).as_posix()
            except Exception:
                continue
            arcname = f"{run_id}/" + rel
            files_to_add.append((f, arcname))

    for f in [inbox_md, inbox_json]:
        if f.exists() and f.is_file():
            try:
                rel = f.relative_to(ROOT).as_posix()
            except Exception:
                continue
            arcname = f"{run_id}/" + rel
            files_to_add.append((f, arcname))

    if not files_to_add:
        return {
            "ok": False,
            "status": "not_found",
            "run_id": run_id,
            "error": "No se encontraron archivos del run ni handoffs asociados para archivar.",
            "archive_dir": str(archive_dir.relative_to(ROOT)).replace("\\", "/"),
            "elapsed_ms": int((time.perf_counter() - start) * 1000),
        }

    ts = time.strftime("%Y%m%d_%H%M%S")
    zip_path = archive_dir / f"{run_id}_{ts}.zip"

    try:
        zip_path = _resolve_within_root(zip_path)
    except Exception as exc:
        return {
            "ok": False,
            "status": "error",
            "run_id": run_id,
            "error": f"zip_path inválido: {exc}",
            "archive_dir": str(archive_dir.relative_to(ROOT)).replace("\\", "/"),
        }

    try:
        with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for src, arcname in files_to_add:
                try:
                    zf.write(src, arcname=arcname)
                except Exception:
                    continue
    except Exception as exc:
        return {
            "ok": False,
            "status": "error",
            "run_id": run_id,
            "error": f"No se pudo crear zip: {exc}",
            "archive_dir": str(archive_dir.relative_to(ROOT)).replace("\\", "/"),
        }

    try:
        size_bytes = int(zip_path.stat().st_size)
    except Exception:
        size_bytes = 0

    return {
        "ok": True,
        "status": "archived",
        "run_id": run_id,
        "archive_path": str(zip_path.relative_to(ROOT)).replace("\\", "/"),
        "archive_bytes": size_bytes,
        "included_files": len(files_to_add),
        "elapsed_ms": int((time.perf_counter() - start) * 1000),
        "note": "Archive-only: no se borraron ni movieron originales.",
    }


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
    parser.add_argument(
        "--archive",
        default=None,
        help=(
            "Modo archive-only (no destructivo): crea un .zip del run y handoffs asociados en el directorio indicado. "
            "Por seguridad requiere --run-id (o --all explícito)."
        ),
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Permite archivar múltiples runs cuando se usa --archive (respeta --max-runs).",
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

    # Archive-only (no destructivo): por defecto el script NO escribe nada.
    archive_results: list[dict[str, object]] = []
    if args.archive:
        if not args.run_id and not args.all:
            print(json.dumps({
                "ok": False,
                "status": "error",
                "error": "--archive requiere --run-id (o --all explícito).",
                "archive_dir": str(args.archive),
            }, ensure_ascii=False, indent=2))
            sys.exit(2)

        for run_id in target_ids:
            archive_results.append(archive_run(run_id, str(args.archive)))

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
        "archive": {
            "requested": bool(args.archive),
            "mode": "archive-only" if args.archive else "audit-only",
            "results": archive_results,
        },
        "policy": {
            "dry_run_only": not bool(args.archive),
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
