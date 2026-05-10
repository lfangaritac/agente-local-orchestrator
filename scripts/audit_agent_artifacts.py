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

    background_meta_files = [p for p in background_files if "_meta.json" in p.name]
    background_meta_count = len(background_meta_files)

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

    # in_progress: background meta exists, no outputs, not stale, not failed
    in_progress = bool(
        background_meta_count > 0
        and agent_outputs_count == 0
        and raw_outputs_count == 0
        and not stale
        and not failed
    )

    if health_status == "partial" and background_files_count > 0 and agent_outputs_count == 0 and raw_outputs_count == 0:
        has_meta = any("_meta.json" in p.name for p in background_files)
        if has_meta:
            recommendations.append("Reintentar check_opencode_run_status en unos segundos.")
            recommendations.append("Reconsultar run_health_check luego de un intervalo.")
            recommendations.append("Si persiste, revisar background logs por referencia (sin abrirlos automáticamente).")

    if has_handoff_md and not has_run_dir:
        recommendations.append("Handoff presente sin run_dir: verificar dispatch/autorización y reconsultar.")

    if has_run_dir and not has_trace:
        issues.append("Falta TRACE.md")
    if has_run_dir and not has_run_summary:
        issues.append("Falta RUN_SUMMARY.md")
    if has_run_dir and agent_outputs_count == 0:
        issues.append("Sin agent_outputs")

    # archive_recommended: cuando hay evidencia valiosa o pesada (heurística simple)
    has_outputs = agent_outputs_count > 0 or raw_outputs_count > 0
    archive_recommended = bool(
        has_run_dir and (
            indexed_in_run_index or
            has_outputs or
            (background_files_count > 0 and (stale or failed))
        )
    )
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
        "background_meta_count": background_meta_count,
        "in_progress": in_progress,
        "latest_status": latest_status,
        "opencode_registered": opencode_registered,
        "archive_recommended": archive_recommended,
        "indexed_in_RUN_INDEX": indexed_in_run_index,
        "health_status": health_status,
        "issues": issues[:10],
        "recommendations": recommendations[:10],
        "elapsed_ms": elapsed_ms,
    }


def _recovery_matrix(health: dict) -> dict[str, object]:
    """Matriz compacta de recuperación: dado health, produce guía consistente."""

    health_status = str(health.get("health_status", ""))
    in_progress = bool(health.get("in_progress", False))
    archive_recommended = bool(health.get("archive_recommended", False))
    latest_status = health.get("latest_status")

    if health_status == "missing":
        return {
            "decision": "verify",
            "severity": "info",
            "recommended_tool": "run_health_check",
            "recommended_command": "(MCP) run_health_check",
            "next_actions": [
                "Verify run_id is correct",
                "If run_id is valid, create/dispatch a new run",
            ],
            "should_wait": False,
            "should_retry": False,
            "should_stop": False,
            "review_reference_only": True,
            "archive_recommended": False,
            "reason": "Run ID not found. Verify the run_id or create a new run.",
        }

    if health_status == "partial" and in_progress:
        return {
            "decision": "wait",
            "severity": "warn",
            "recommended_tool": "check_opencode_run_status",
            "recommended_command": "(MCP) check_opencode_run_status",
            "next_actions": [
                "Wait for current run to complete",
                "Re-consult check_opencode_run_status",
                "Do NOT archive prematurely",
            ],
            "should_wait": True,
            "should_retry": False,
            "should_stop": True,
            "review_reference_only": False,
            "archive_recommended": False,
            "reason": "Run appears in-progress (background meta without outputs). Block advance, wait and re-consult.",
        }

    if health_status == "partial":
        return {
            "decision": "verify",
            "severity": "info",
            "recommended_tool": "check_opencode_run_status",
            "recommended_command": "(MCP) check_opencode_run_status",
            "next_actions": [
                "Verify run state via check_opencode_run_status",
                "Review background logs by reference if needed",
            ],
            "should_wait": False,
            "should_retry": False,
            "should_stop": False,
            "review_reference_only": True,
            "archive_recommended": archive_recommended,
            "reason": "Run is partial (incomplete artifacts). Verify state before proceeding.",
        }

    if health_status == "stale":
        return {
            "decision": "wait",
            "severity": "warn",
            "recommended_tool": "check_opencode_run_status",
            "recommended_command": "(MCP) check_opencode_run_status + run_health_check",
            "next_actions": [
                "Wait and re-consult check_opencode_run_status",
                "Review background logs by reference",
                "If persists, consider re-dispatch",
            ],
            "should_wait": True,
            "should_retry": True,
            "should_stop": True,
            "review_reference_only": False,
            "archive_recommended": archive_recommended,
            "reason": "Run is stale (background meta without recent outputs). Block advance, wait/re-consult.",
        }

    if health_status == "failed":
        return {
            "decision": "stop",
            "severity": "error",
            "recommended_tool": "check_opencode_run_status",
            "recommended_command": "(MCP) check_opencode_run_status + run_health_check",
            "next_actions": [
                "Diagnose failure cause",
                "Review agent_outputs (processed) by reference",
                "Re-dispatch agent or correct error",
            ],
            "should_wait": False,
            "should_retry": False,
            "should_stop": True,
            "review_reference_only": False,
            "archive_recommended": archive_recommended,
            "reason": f"Run failed (status: {latest_status or 'unknown'}). Block advance, diagnose and correct.",
        }

    # healthy or unknown
    return {
        "decision": "advance",
        "severity": "ok",
        "recommended_tool": "audit_agent_artifacts",
        "recommended_command": "avanzar a siguiente tarea o build",
        "next_actions": [
            "Proceed with next task or build",
        ],
        "should_wait": False,
        "should_retry": False,
        "should_stop": False,
        "review_reference_only": False,
        "archive_recommended": archive_recommended,
        "reason": "Run is healthy or no issues detected. Safe to advance.",
    }


def next_actions_for_run(run_id: str, stale_minutes: int = 15) -> dict[str, object]:
    """Devuelve JSON compacto con próximas acciones recomendadas para un run.

    Reutiliza check_run_health() sin lecturas adicionales voluminosas.
    No abre raw_outputs/TRACE/RUN_SUMMARY completos.
    """

    health = check_run_health(run_id, stale_minutes=stale_minutes)

    observed_recommendations: list[str] = list(health.get("recommendations", []))[:5]

    suggested_tools: list[str] = ["run_health_check"]
    health_status = health.get("health_status", "")
    bg_count = health.get("background_files_count", 0)
    if health_status in ("partial", "stale") or (isinstance(bg_count, int) and int(bg_count) > 0):
        suggested_tools.append("check_opencode_run_status")

    matrix = _recovery_matrix(health)

    matrix_actions = list(matrix.get("next_actions", []))

    combined_actions: list[str] = []
    for a in matrix_actions + observed_recommendations:
        a = str(a).strip()
        if not a:
            continue
        if a not in combined_actions:
            combined_actions.append(a)

    next_actions = combined_actions[:8]

    result: dict[str, object] = {
        "ok": True,
        "status": "ok",
        "run_id": run_id,
        "exists": health.get("exists", False),
        "health_status": health.get("health_status", "unknown"),
        "in_progress": health.get("in_progress", False),
        "background_meta_count": health.get("background_meta_count", 0),
        "latest_status": health.get("latest_status"),
        "next_actions": next_actions,
        "observed_recommendations": observed_recommendations,
        "suggested_tools": suggested_tools,
    }

    for key in ("decision", "severity", "recommended_tool", "recommended_command",
                 "should_wait", "should_retry", "should_stop", "review_reference_only",
                 "archive_recommended", "reason"):
        result[key] = matrix.get(key)

    # Back-compat: keep extended_actions as the matrix-driven action list.
    result["extended_actions"] = matrix_actions

    return result


def infer_latest_run_id() -> str | None:
    """Infiero el último run_id sin abrir artefactos voluminosos.

    Orden de preferencia:
    1) Directorios bajo RUNS_DIR (excluyendo .md).
    2) Fallback a archivos .md en INBOX_DIR.
    """

    candidates: list[tuple[str, float]] = []

    try:
        for p in RUNS_DIR.iterdir():
            if p.is_dir() and p.name and not p.name.endswith(".md"):
                try:
                    mtime = p.stat().st_mtime
                    candidates.append((p.name, mtime))
                except Exception:
                    continue
    except Exception:
        pass

    if not candidates:
        try:
            for p in INBOX_DIR.glob("*.md"):
                try:
                    name = p.stem
                    mtime = p.stat().st_mtime
                    candidates.append((name, mtime))
                except Exception:
                    continue
        except Exception:
            pass

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]


def _run_subprocess_json(command: list[str], timeout_s: int = 120) -> dict[str, Any] | None:
    """Ejecuta un comando y parsea su stdout como JSON. Devuelve None si falla."""

    try:
        completed = subprocess.run(
            command,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
        )
        stdout = (completed.stdout or "").strip()
        if not stdout:
            return None
        return json.loads(stdout)
    except Exception:
        return None


def compute_operational_status(
    *,
    include_git_status: bool,
    run_quick_checks: bool,
    verify_master_files: bool,
) -> tuple[dict[str, object], int]:
    """Compute operational status read-only (compact-first).

    Retorna (result_dict, exit_code).
    Exit codes:
      0 = overall_status ok
      1 = warn
      2 = error (o error de ejecución interna)
    """

    start = time.perf_counter()

    result: dict[str, object] = {
        "ok": True,
        "status": "ok",
        "mode": "operational-status",
    }

    blockers: list[str] = []
    attention: list[str] = []
    next_action: dict[str, str] | None = None
    exit_code = 0

    # 1) git status
    git_info: dict[str, object] | None = None
    if include_git_status:
        git_info = git_dirty_porcelain()
        result["git"] = git_info
        if git_info.get("ok") is not True:
            blockers.append("git_status_error")
            next_action = {"decision": "stop", "tool": "git", "command": "git status --porcelain"}
            result["git_clean"] = None
            exit_code = max(exit_code, 2)
        else:
            dirty = bool(git_info.get("dirty"))
            result["git_clean"] = not dirty
            if dirty:
                blockers.append("git_dirty")
                next_action = {"decision": "correct", "tool": "git", "command": "git status --short"}
                exit_code = max(exit_code, 1)
    else:
        result["git_clean"] = None

    # 2) runner_quick
    runner_quick: dict[str, object] = {"status": "not_run"}
    if run_quick_checks:
        quick_data = _run_subprocess_json(
            [sys.executable, str(ROOT / "scripts" / "run_local_checks.py"), "--mode", "quick"],
            timeout_s=120,
        )
        if quick_data is None:
            runner_quick = {
                "status": "error",
                "error": "failed to run or parse quick checks",
            }
            blockers.append("quick_failed")
            if next_action is None:
                next_action = {"decision": "correct", "tool": "run_local_checks", "command": r"python .\scripts\run_local_checks.py --mode full --include-git-status"}
            exit_code = max(exit_code, 2)
        else:
            ok = bool(quick_data.get("ok"))
            passed = int(quick_data.get("passed", 0))
            failed = int(quick_data.get("failed", 0))
            first_failure = quick_data.get("first_failure")
            runner_quick = {
                "status": "ok" if ok else "failed",
                "passed": passed,
                "failed": failed,
                "first_failure": {
                    "name": first_failure.get("name") if isinstance(first_failure, dict) else None,
                    "returncode": first_failure.get("returncode") if isinstance(first_failure, dict) else None,
                    "command": first_failure.get("command") if isinstance(first_failure, dict) else None,
                } if first_failure else None,
            }
            if not ok:
                blockers.append("quick_failed")
                if next_action is None:
                    ff_cmd = first_failure.get("command") if isinstance(first_failure, dict) else None
                    if isinstance(ff_cmd, list) and ff_cmd:
                        next_action = {"decision": "correct", "tool": "python", "command": " ".join(str(c) for c in ff_cmd)}
                    else:
                        next_action = {"decision": "correct", "tool": "run_local_checks", "command": r"python .\scripts\run_local_checks.py --mode full --include-git-status"}
                quick_failed_flag = runner_quick.get("status") == "failed"
                exit_code = max(exit_code, 1 if quick_failed_flag else 2)
        result["runner_quick"] = runner_quick
    else:
        result["runner_quick"] = runner_quick

    # 3) verify_master_files
    verify_info: dict[str, object] = {"status": "not_run"}
    if verify_master_files:
        vm_data = _run_subprocess_json(
            [sys.executable, str(ROOT / "scripts" / "verify_master_files.py"), "--compact"],
            timeout_s=60,
        )
        if vm_data is None:
            verify_info = {
                "status": "error",
                "error": "failed to run or parse verify_master_files",
            }
            blockers.append("master_files_missing")
            if next_action is None:
                next_action = {"decision": "verify", "tool": "verify_master_files", "command": r"python .\scripts\verify_master_files.py --compact"}
            exit_code = max(exit_code, 2)
        else:
            all_ok = bool(vm_data.get("all_ok")) if isinstance(vm_data, dict) else False
            total_missing = int(vm_data.get("total_missing", 0)) if isinstance(vm_data, dict) else 0
            total_errors = int(vm_data.get("total_errors", 0)) if isinstance(vm_data, dict) else 0
            missing_files = vm_data.get("missing_files") if isinstance(vm_data, dict) else []
            verify_info = {
                "status": "ok" if all_ok else "missing",
                "total_missing": total_missing,
                "total_errors": total_errors,
                "missing_files": missing_files[:10] if isinstance(missing_files, list) else [],
            }
            if not all_ok:
                blockers.append("master_files_missing")
                if next_action is None:
                    next_action = {"decision": "verify", "tool": "verify_master_files", "command": r"python .\scripts\verify_master_files.py --compact"}
                vm_missing_flag = verify_info.get("status") == "missing"
                exit_code = max(exit_code, 1 if vm_missing_flag else 2)
        result["verify_master_files"] = verify_info
    else:
        result["verify_master_files"] = verify_info

    # 4) latest_run_relevant
    latest_run_id = infer_latest_run_id()
    latest_run_info: dict[str, object] | None = None
    if latest_run_id:
        nx = next_actions_for_run(latest_run_id)

        decision = str(nx.get("decision") or "advance")
        in_progress = bool(nx.get("in_progress", False))
        hs = str(nx.get("health_status") or "")
        should_stop = bool(nx.get("should_stop", False))

        latest_run_info = {
            "run_id": latest_run_id,
            "health_status": hs,
            "in_progress": in_progress,
            "decision": nx.get("decision"),
            "severity": nx.get("severity"),
            "should_stop": should_stop,
            "should_wait": nx.get("should_wait", False),
            "should_retry": nx.get("should_retry", False),
            "review_reference_only": nx.get("review_reference_only", False),
            "archive_recommended": nx.get("archive_recommended", False),
            "reason": nx.get("reason", ""),
            "next_actions": nx.get("next_actions"),
            "extended_actions": nx.get("extended_actions", []),
        }

        # Use recovery matrix to decide blocker vs attention
        if decision == "stop":
            blockers.append("latest_run_failed")
            if next_action is None:
                next_action = {"decision": "stop", "tool": "mcp:run_health_check", "command": "(MCP) run_health_check + check_opencode_run_status"}
            exit_code = max(exit_code, 2)
        elif decision == "wait" and should_stop:
            # stale or partial+in_progress: block advance (attention, not blocker)
            if hs == "stale":
                attention.append("latest_run_stale")
            elif hs == "partial":
                attention.append("latest_run_partial_in_progress")
            if next_action is None:
                next_action = {"decision": "wait", "tool": "mcp:check_opencode_run_status", "command": "(MCP) check_opencode_run_status"}
            exit_code = max(exit_code, 1)
        elif decision == "verify" and not should_stop:
            # non-blocking verify guidance: does NOT change overall_status/exit_code.
            if hs == "partial":
                attention.append("latest_run_partial")
                if next_action is None:
                    next_action = {"decision": "verify", "tool": "mcp:check_opencode_run_status", "command": "(MCP) check_opencode_run_status"}
            elif hs == "missing":
                # missing does not block the repo
                attention.append("latest_run_missing")
                if next_action is None:
                    next_action = {"decision": "verify", "tool": "run_health_check", "command": "(MCP) run_health_check"}

        # archive_suggested
        next_actions_list = latest_run_info.get("next_actions") or []
        if isinstance(next_actions_list, list) and any("Archivar" in str(a) for a in next_actions_list):
            attention.append("archive_suggested")

    result["latest_run_relevant"] = latest_run_info

    # i) default next_action
    if next_action is None:
        next_action = {"decision": "advance", "tool": "audit_agent_artifacts", "command": "avanzar a siguiente tarea o build"}

    build_blocked = bool(blockers)
    overall_status = "ok" if exit_code == 0 else ("warn" if exit_code == 1 else "error")
    ready_to_advance = (overall_status == "ok" and not build_blocked)

    suggested_next_step = f"{next_action['decision']}: {next_action['command']}"

    warnings = list(blockers) + list(attention)

    result["blockers"] = blockers
    result["attention"] = attention
    result["build_blocked"] = build_blocked
    result["ready_to_advance"] = ready_to_advance
    result["next_action"] = next_action
    result["suggested_next_step"] = suggested_next_step
    result["overall_status"] = overall_status
    result["ok"] = exit_code == 0
    result["status"] = overall_status
    result["warnings"] = warnings
    result["elapsed_ms"] = int((time.perf_counter() - start) * 1000)

    return result, exit_code


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


def verify_archive(zip_path_arg: str) -> dict[str, object]:
    """Verifica la integridad de un archive ZIP contra su manifest sidecar.

    Reglas:
    - No extrae el ZIP.
    - No abre contenidos internos.
    """

    start = time.perf_counter()

    zip_path = Path(zip_path_arg)
    manifest_path = Path(str(zip_path) + ".manifest.json")

    errors: list[str] = []
    error_codes: list[str] = []
    zip_exists = zip_path.is_file()
    manifest_exists = manifest_path.is_file()

    if not zip_exists:
        errors.append(f"ZIP no encontrado: {zip_path}")
        error_codes.append("zip_missing")
    if not manifest_exists:
        errors.append(f"Manifest no encontrado: {manifest_path}")
        error_codes.append("manifest_missing")

    archive_sha256_actual = ""
    archive_sha256_manifest = ""
    sha256_matches = False
    zip_entries_count = 0
    manifest_included_files_count: int | None = None
    included_files_count_matches = False

    manifest_archive_obj: dict[str, Any] | None = None
    manifest_parsed = False
    manifest_schema_ok = False

    if zip_exists and manifest_exists:
        # 1) Leer manifest (solo metadatos)
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
            manifest_archive_obj = manifest.get("archive") if isinstance(manifest, dict) else None
            if not isinstance(manifest_archive_obj, dict):
                error_codes.append("manifest_schema_error")
                raise ValueError("Campo 'archive' inválido o ausente.")

            archive_sha256_manifest = str(manifest_archive_obj.get("sha256") or "").strip()
            raw_count = manifest_archive_obj.get("included_files_count")
            try:
                manifest_included_files_count = int(raw_count)
            except Exception:
                error_codes.append("manifest_bad_included_files_count")
                raise ValueError("Campo 'archive.included_files_count' no es int.")

            if not archive_sha256_manifest:
                errors.append("Manifest sin archive.sha256.")
                error_codes.append("manifest_missing_sha256")
        except Exception as exc:
            errors.append(f"Error leyendo manifest: {exc}")
            if not error_codes or error_codes[-1] not in ("manifest_schema_error", "manifest_bad_included_files_count"):
                error_codes.append("manifest_read_error")
        else:
            manifest_parsed = True

        if manifest_parsed:
            manifest_schema_ok = bool(archive_sha256_manifest)

        # 2) Recalcular SHA256 del ZIP
        try:
            archive_sha256_actual = sha256_file(zip_path)
        except Exception as exc:
            errors.append(f"Error calculando SHA256: {exc}")
            error_codes.append("sha256_calc_error")

        # 3) Contar entries del ZIP (sin extraer). Contar solo archivos (no directorios).
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                infos = zf.infolist()
                zip_entries_count = sum(0 if getattr(zi, "is_dir", lambda: False)() else 1 for zi in infos)
        except Exception as exc:
            errors.append(f"Error leyendo ZIP: {exc}")
            error_codes.append("zip_read_error")

        # 4) Comparaciones
        if archive_sha256_actual and archive_sha256_manifest:
            sha256_matches = archive_sha256_actual == archive_sha256_manifest
            if not sha256_matches:
                errors.append("Mismatch de SHA256.")
                error_codes.append("sha256_mismatch")

        if manifest_included_files_count is not None:
            included_files_count_matches = zip_entries_count == manifest_included_files_count
            if not included_files_count_matches:
                errors.append(
                    f"Mismatch de conteo de archivos: ZIP={zip_entries_count}, manifest={manifest_included_files_count}"
                )
                error_codes.append("included_files_count_mismatch")

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    return {
        "ok": len(errors) == 0,
        "status": "ok" if len(errors) == 0 else "error",
        "error_codes": error_codes,
        "manifest_parsed": manifest_parsed,
        "manifest_schema_ok": manifest_schema_ok,
        "archive_path": str(zip_path),
        "manifest_path": str(manifest_path),
        "archive_exists": zip_exists,
        "manifest_exists": manifest_exists,
        "archive_sha256_actual": archive_sha256_actual,
        "archive_sha256_manifest": archive_sha256_manifest,
        "sha256_matches": sha256_matches,
        "zip_entries_count": zip_entries_count,
        "manifest_included_files_count": manifest_included_files_count or 0,
        "included_files_count_matches": included_files_count_matches,
        "errors": errors,
        "elapsed_ms": elapsed_ms,
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
    parser.add_argument(
        "--verify-archive",
        default=None,
        help="Verifica la integridad de un archive ZIP (recalcula SHA256 y compara con manifest sidecar).",
    )
    parser.add_argument(
        "--next-actions",
        default=None,
        help="Devuelve JSON compacto con próximas acciones recomendadas para un RUN_ID (basado en check_run_health). No escanea docs/agent_runs completo.",
    )
    parser.add_argument(
        "--operational-status",
        action="store_true",
        help="Modo diagnóstico operativo compact-first (read-only). Devuelve JSON con estado del repo + siguiente paso seguro.",
    )
    parser.add_argument(
        "--run-quick-checks",
        action="store_true",
        help="Ejecuta python scripts/run_local_checks.py --mode quick (solo con --operational-status).",
    )
    parser.add_argument(
        "--no-verify-master-files",
        action="store_true",
        help="Deshabilita verify_master_files en --operational-status (por defecto está activo).",
    )

    args = parser.parse_args()

    # Modo operational-status (read-only, compact-first)
    if args.operational_status:
        op_result, op_exit = compute_operational_status(
            include_git_status=bool(args.include_git_status),
            run_quick_checks=bool(args.run_quick_checks),
            verify_master_files=not bool(args.no_verify_master_files),
        )
        print(json.dumps(op_result, ensure_ascii=False, separators=(",", ":")))
        sys.exit(op_exit)

    # Modo verify-archive (no requiere escanear docs/agent_runs)
    if args.verify_archive:
        result_verify = verify_archive(str(args.verify_archive))
        # JSON compacto (una línea) para facilitar consumo por tooling.
        print(json.dumps(result_verify, ensure_ascii=False, separators=(",", ":")))
        sys.exit(0 if result_verify["ok"] else 1)

    # Modo next-actions compact-first (no requiere escanear docs/agent_runs)
    if args.next_actions:
        result_nx = next_actions_for_run(str(args.next_actions), stale_minutes=int(args.stale_minutes))
        print(json.dumps(result_nx, ensure_ascii=False, separators=(",", ":")))
        sys.exit(0)

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
