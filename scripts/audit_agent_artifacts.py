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
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "docs" / "agent_runs"
INBOX_DIR = ROOT / "docs" / "agent_queue" / "inbox"
RUN_INDEX = ROOT / "docs" / "context" / "RUN_INDEX.md"

# Destino recomendado para archivos de archive-only (fuera del repo).
# Motivo: no ensuciar Git con zips de evidencia operacional.
RECOMMENDED_ARCHIVE_DIR = Path(r"C:\Agente_Archives")


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


def _is_within_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT)
        return True
    except Exception:
        return False


def _resolve_safe(path: Path) -> Path:
    """Resuelve una ruta sin restringirla a ROOT.

    Se usa para destinos de archivado fuera del repo.
    """

    return path.resolve()


def _iter_files_recursive(base_dir: Path) -> list[Path]:
    try:
        return [p for p in base_dir.rglob("*") if p.is_file()]
    except Exception:
        return []


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_text_prefix(path: Path, max_chars: int = 12000) -> str:
    """Lee un prefijo corto de un archivo (sin cargarlo completo)."""

    try:
        if not path.exists() or not path.is_file():
            return ""
        with path.open("r", encoding="utf-8", errors="replace") as f:
            return f.read(max_chars)
    except Exception:
        return ""


def _find_first_status(obj: Any, max_depth: int = 4) -> str | None:
    """Busca un campo `status` en JSON de forma best-effort con profundidad limitada."""

    if max_depth < 0:
        return None

    if isinstance(obj, dict):
        status = obj.get("status")
        if isinstance(status, str) and status.strip():
            return status.strip()
        for v in obj.values():
            found = _find_first_status(v, max_depth=max_depth - 1)
            if found:
                return found
        return None

    if isinstance(obj, list):
        for v in obj:
            found = _find_first_status(v, max_depth=max_depth - 1)
            if found:
                return found
        return None

    return None


def infer_latest_status(run_dir: Path) -> str | None:
    """Infiera latest_status sin leer artefactos completos.

    Orden:
    1) Prefijo de RUN_SUMMARY.md
    2) Último agent_output JSON (si es razonablemente pequeño)
    """

    # 1) RUN_SUMMARY prefix
    summary_prefix = _read_text_prefix(run_dir / "RUN_SUMMARY.md", max_chars=12000)
    if summary_prefix:
        m = re.search(r"[ÚU]ltimo\s+estado\s+registrado:\s*`([^`]+)`", summary_prefix)
        if m:
            return m.group(1).strip()

    # 2) último agent_output
    agent_dir = run_dir / "agent_outputs"
    outputs = sorted(agent_dir.glob("*.json")) if agent_dir.exists() else []
    if not outputs:
        return None

    try:
        latest = max(outputs, key=lambda p: p.stat().st_mtime)
        if latest.stat().st_size > 1_000_000:
            return None
        data = json.loads(latest.read_text(encoding="utf-8", errors="replace"))
        return _find_first_status(data)
    except Exception:
        return None


def check_run_health(run_id: str, stale_minutes: int = 15) -> dict[str, object]:
    """Health check compacto de un run (sin abrir raw_outputs/TRACE/RUN_SUMMARY completos)."""

    start = time.perf_counter()

    run_dir = RUNS_DIR / run_id
    has_run_dir = bool(run_dir.exists() and run_dir.is_dir())

    handoff_md = INBOX_DIR / f"{run_id}.md"
    handoff_json = INBOX_DIR / f"{run_id}.json"

    has_handoff_md = handoff_md.exists()
    has_handoff_json = handoff_json.exists()

    trace_path = run_dir / "TRACE.md"
    summary_path = run_dir / "RUN_SUMMARY.md"

    has_trace = trace_path.exists()
    has_run_summary = summary_path.exists()

    agent_outputs = sorted((run_dir / "agent_outputs").glob("*.json")) if (run_dir / "agent_outputs").exists() else []
    raw_outputs = sorted((run_dir / "raw_outputs").glob("*.json")) if (run_dir / "raw_outputs").exists() else []

    background_files = []
    background_dir = run_dir / "background"
    if background_dir.exists():
        background_files = [p for p in background_dir.glob("*") if p.is_file()]

    agent_outputs_count = len(agent_outputs)
    raw_outputs_count = len(raw_outputs)
    background_files_count = len(background_files)

    opencode_outputs = [p for p in agent_outputs if "_opencode" in p.name]
    opencode_raw_outputs = [p for p in raw_outputs if "_opencode_raw" in p.name]
    opencode_registered = bool(opencode_outputs and opencode_raw_outputs)

    indexed_in_run_index = is_registered_in_run_index(run_id)

    latest_status = infer_latest_status(run_dir) if has_run_dir else None

    # stale: hay background meta pero no hay outputs luego de cierto tiempo
    now = time.time()
    stale = False
    try:
        meta_files = sorted(background_dir.glob("*_meta.json")) if background_dir.exists() else []
        if meta_files and agent_outputs_count == 0 and raw_outputs_count == 0:
            newest_meta = max(meta_files, key=lambda p: p.stat().st_mtime)
            age_s = now - newest_meta.stat().st_mtime
            if age_s > max(1, int(stale_minutes)) * 60:
                stale = True
    except Exception:
        stale = False

    # failed: status explícito
    failed = False
    if isinstance(latest_status, str) and latest_status.strip().lower() in {"failed", "error", "errored"}:
        failed = True

    exists = bool(has_run_dir or has_handoff_md or has_handoff_json)

    issues: list[str] = []
    recommendations: list[str] = []

    if not exists:
        health_status = "missing"
        issues.append("run_id no encontrado (sin run_dir ni handoff).")
        recommendations.append("Verifica el run_id o crea/dispatch un nuevo run.")
    elif has_run_dir and has_trace and has_run_summary and agent_outputs_count > 0:
        health_status = "healthy"
        if not opencode_registered:
            issues.append("No hay evidencia completa de OpenCode (opencode_registered=false).")
            recommendations.append("Si se esperaba OpenCode, reintentar dispatch o revisar background logs (por referencia).")
    else:
        health_status = "partial"

    if failed:
        health_status = "failed"
        issues.append(f"Último status indica fallo: {latest_status}")
        recommendations.append("Revisar agent_outputs (procesado) o reintentar el agente según el escenario.")

    if stale and health_status not in {"failed"}:
        health_status = "stale"
        issues.append("Ejecución parece estancada (background meta sin outputs recientes).")
        recommendations.append("Revisar proceso async/estado y reintentar check_opencode_run_status en unos segundos.")

    if has_run_dir and not has_trace:
        issues.append("Falta TRACE.md")
    if has_run_dir and not has_run_summary:
        issues.append("Falta RUN_SUMMARY.md")
    if has_run_dir and agent_outputs_count == 0:
        issues.append("Sin agent_outputs")

    # archive_recommended: cuando hay evidencia valiosa o pesada (heurística simple)
    archive_recommended = bool(has_run_dir and (indexed_in_run_index or raw_outputs_count > 0 or background_files_count > 0))
    if archive_recommended:
        recommendations.append(f"Archivar (no destructivo) con --archive {RECOMMENDED_ARCHIVE_DIR}")

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    return {
        "run_id": run_id,
        "exists": exists,
        "has_run_dir": has_run_dir,
        "has_handoff_md": bool(has_handoff_md),
        "has_handoff_json": bool(has_handoff_json),
        "has_trace": bool(has_trace),
        "has_run_summary": bool(has_run_summary),
        "agent_outputs_count": agent_outputs_count,
        "raw_outputs_count": raw_outputs_count,
        "background_files_count": background_files_count,
        "latest_status": latest_status,
        "opencode_registered": opencode_registered,
        "archive_recommended": archive_recommended,
        "indexed_in_RUN_INDEX": indexed_in_run_index,
        "health_status": health_status,
        "issues": issues[:10],
        "recommendations": recommendations[:10],
        "elapsed_ms": elapsed_ms,
    }


def archive_run(run_id: str, archive_dir_arg: str) -> dict[str, object]:
    """Crea un zip no destructivo con evidencia local del run.

    Incluye (si existen):
    - docs/agent_runs/<run_id>/**
    - docs/agent_queue/inbox/<run_id>.{md,json}

    No borra ni mueve originales.

    Seguridad:
    - El destino recomendado es fuera del repo (para no ensuciar Git).
    - El archivo zip se crea *únicamente* dentro del directorio indicado.
    """

    start = time.perf_counter()

    archive_dir = Path(archive_dir_arg)
    if not archive_dir.is_absolute():
        # Si es relativo, se interpreta relativo a ROOT (puede ensuciar git si queda dentro del repo).
        archive_dir = ROOT / archive_dir

    try:
        archive_dir = _resolve_safe(archive_dir)
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
            "archive_dir": str(archive_dir),
            "elapsed_ms": int((time.perf_counter() - start) * 1000),
        }

    ts = time.strftime("%Y%m%d_%H%M%S")
    zip_path = _resolve_safe(archive_dir / f"{run_id}_{ts}.zip")

    # Garantía: el zip debe quedar dentro del directorio solicitado.
    try:
        if zip_path.parent.resolve() != archive_dir.resolve():
            raise ValueError("zip_path fuera del directorio de archivo (bloqueado).")
    except Exception as exc:
        return {
            "ok": False,
            "status": "error",
            "run_id": run_id,
            "error": f"zip_path inválido: {exc}",
            "archive_dir": str(archive_dir),
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
            "archive_dir": str(archive_dir),
        }

    try:
        size_bytes = int(zip_path.stat().st_size)
    except Exception:
        size_bytes = 0

    created_at = datetime.now(timezone.utc).isoformat()

    # sha256 del zip (integridad)
    try:
        archive_sha256 = sha256_file(zip_path)
    except Exception as exc:
        archive_sha256 = f"error: {exc}"

    # Paths incluidos (solo rutas, no contenido)
    included_paths = sorted(list({arcname for _, arcname in files_to_add}))
    included_paths_truncated = False
    max_paths = 5000
    if len(included_paths) > max_paths:
        included_paths_truncated = True
        included_paths = included_paths[:max_paths]

    manifest = {
        "schema": "run-archive-manifest-v0.1",
        "created_at": created_at,
        "run_id": run_id,
        "archive": {
            "bytes": size_bytes,
            "sha256": archive_sha256,
            "included_files_count": len(files_to_add),
            "included_paths_truncated": included_paths_truncated,
            "included_paths": included_paths,
        },
        "sources": {
            "run_dir": str(run_dir),
            "handoff_md": str(inbox_md),
            "handoff_json": str(inbox_json),
        },
        "notes": [
            "Manifest contiene solo metadatos y rutas; no incluye contenido.",
            "Archive-only: no se borraron ni movieron originales.",
        ],
    }

    # Sidecar manifest junto al zip
    manifest_path = Path(str(zip_path) + ".manifest.json")
    manifest_bytes = 0
    manifest_error: str | None = None

    try:
        if manifest_path.parent.resolve() != archive_dir.resolve():
            raise ValueError("manifest_path fuera del directorio de archivo (bloqueado).")
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest_bytes = int(manifest_path.stat().st_size)
    except Exception as exc:
        manifest_error = str(exc)
        manifest_path = None

    archive_path = str(zip_path)
    manifest_path_out: str | None = str(manifest_path) if manifest_path else None

    if _is_within_root(zip_path):
        archive_path = str(zip_path.relative_to(ROOT)).replace("\\", "/")
    if manifest_path and _is_within_root(manifest_path):
        manifest_path_out = str(manifest_path.relative_to(ROOT)).replace("\\", "/")

    return {
        "ok": True,
        "status": "archived",
        "run_id": run_id,
        "archive_path": archive_path,
        "archive_bytes": size_bytes,
        "archive_sha256": archive_sha256,
        "manifest_path": manifest_path_out,
        "manifest_bytes": manifest_bytes,
        "manifest_error": manifest_error,
        "included_files": len(files_to_add),
        "elapsed_ms": int((time.perf_counter() - start) * 1000),
        "archive_dir_within_repo": _is_within_root(archive_dir),
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
        "--health",
        action="store_true",
        help="Devuelve health check compacto para un run_id (requiere --run-id).",
    )
    parser.add_argument(
        "--stale-minutes",
        type=int,
        default=15,
        help="Umbral en minutos para marcar stale cuando hay background meta sin outputs (default 15).",
    )
    parser.add_argument(
        "--archive",
        default=None,
        help=(
            "Modo archive-only (no destructivo): crea un .zip del run y handoffs asociados en el directorio indicado. "
            "Por seguridad requiere --run-id (o --all explícito). "
            f"Destino recomendado (fuera del repo): {RECOMMENDED_ARCHIVE_DIR}"
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

    # Health check compacto (no escribe archivos)
    if args.health:
        if not args.run_id:
            print(json.dumps({
                "ok": False,
                "status": "error",
                "error": "--health requiere --run-id.",
            }, ensure_ascii=False, indent=2))
            sys.exit(2)

        health = check_run_health(str(args.run_id), stale_minutes=int(args.stale_minutes))

        out: dict[str, object] = {
            "ok": True,
            "status": "ok",
            "mode": "health",
            "root": str(ROOT),
            "health": health,
        }

        if args.include_git_status:
            out["git"] = git_dirty_porcelain()

        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

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
            "recommended_dir": str(RECOMMENDED_ARCHIVE_DIR),
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
