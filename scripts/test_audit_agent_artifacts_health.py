"""test_audit_agent_artifacts_health.py

Pruebas unitarias (script standalone) para `check_run_health()` en:
  scripts/audit_agent_artifacts.py

Objetivo:
- Cubrir health_status: missing / partial / stale / failed / healthy.
- No invoca OpenCode.
- No toca evidencia real en docs/agent_runs del repo.
- Usa un filesystem temporal y monkeypatch de rutas globales del módulo.

Ejecución sugerida:
  python .\\scripts\\test_audit_agent_artifacts_health.py
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _touch(path: Path, *, mtime: float | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")
    if mtime is not None:
        os.utime(path, (mtime, mtime))


def _patch_module_paths(audit_mod, root: Path) -> None:
    """Redirige ROOT/RUNS_DIR/INBOX_DIR/RUN_INDEX al filesystem temporal."""

    audit_mod.ROOT = root
    audit_mod.RUNS_DIR = root / "docs" / "agent_runs"
    audit_mod.INBOX_DIR = root / "docs" / "agent_queue" / "inbox"
    audit_mod.RUN_INDEX = root / "docs" / "context" / "RUN_INDEX.md"


def main() -> None:
    # Import local: al ejecutarse desde scripts/, Python incluye este dir en sys.path.
    import audit_agent_artifacts as audit

    cases: list[dict[str, object]] = []

    def check(label: str, *, setup_fn, run_id: str = "run_001", stale_minutes: int = 15, expect: str) -> None:
        with tempfile.TemporaryDirectory(prefix="audit-health-") as td:
            root = Path(td)
            _patch_module_paths(audit, root)

            # RUN_INDEX vacío por defecto (no debe fallar si no registra el run).
            _write_text(audit.RUN_INDEX, "# RUN_INDEX\n")

            setup_fn(root=root, run_id=run_id)

            got = audit.check_run_health(run_id, stale_minutes=stale_minutes)

            if got.get("health_status") != expect:
                raise AssertionError(f"{label}: health_status esperado={expect!r} got={got!r}")

            cases.append({"label": label, "ok": True, "health_status": got.get("health_status"), "got": got})

    # 1) missing: no existe run_dir ni handoff.
    def setup_missing(*, root: Path, run_id: str) -> None:
        # No crear nada.
        return

    check("missing", setup_fn=setup_missing, run_id="run_missing", expect="missing")

    # 2) partial: existe run_dir pero faltan artefactos mínimos.
    def setup_partial_run_dir_only(*, root: Path, run_id: str) -> None:
        (root / "docs" / "agent_runs" / run_id).mkdir(parents=True, exist_ok=True)

    check("partial_run_dir_only", setup_fn=setup_partial_run_dir_only, run_id="run_partial", expect="partial")

    # 3) stale: existe background meta pero no hay outputs y el meta es antiguo.
    def setup_stale(*, root: Path, run_id: str) -> None:
        run_dir = root / "docs" / "agent_runs" / run_id
        bg_dir = run_dir / "background"

        now = time.time()
        old = now - (60 * 60)  # 1h atrás
        _touch(bg_dir / f"{run_id}_meta.json", mtime=old)

        # Sin agent_outputs / raw_outputs.

    check("stale_meta_no_outputs", setup_fn=setup_stale, run_id="run_stale", stale_minutes=1, expect="stale")

    # 4) failed: RUN_SUMMARY indica fallo (no requiere outputs).
    def setup_failed(*, root: Path, run_id: str) -> None:
        run_dir = root / "docs" / "agent_runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # Nota: el regex busca: "Último estado registrado: `...`"
        _write_text(run_dir / "RUN_SUMMARY.md", "Último estado registrado: `failed`\n")

    check("failed_from_run_summary", setup_fn=setup_failed, run_id="run_failed", expect="failed")

    # 5) healthy: run_dir con TRACE, RUN_SUMMARY, agent_outputs + raw_outputs (opencode_registered=true).
    def setup_healthy(*, root: Path, run_id: str) -> None:
        run_dir = root / "docs" / "agent_runs" / run_id
        
        # Crear estructura completa
        _write_text(run_dir / "TRACE.md", "# TRACE\n\nExecution trace for run.\n")
        _write_text(run_dir / "RUN_SUMMARY.md", "Último estado registrado: `diagnostic`\n")
        
        # Agent output con status no failed + nombre con "_opencode" para opencode_registered
        agent_output = {
            "run_id": run_id,
            "status": "diagnostic",
            "message": "Run completed successfully",
            "timestamp": time.time(),
        }
        _write_text(run_dir / "agent_outputs" / f"{run_id}_opencode_output.json", json.dumps(agent_output))
        
        # Raw output con "_opencode_raw" para completar opencode_registered
        raw_output = {
            "run_id": run_id,
            "raw": "diagnostic output data",
        }
        _write_text(run_dir / "raw_outputs" / f"{run_id}_opencode_raw_output.json", json.dumps(raw_output))

    check("healthy_complete_run", setup_fn=setup_healthy, run_id="run_healthy", expect="healthy")

    # 6) partial-in-progress: background meta reciente sin outputs, no archive prematuro.
    def setup_partial_in_progress_meta_no_outputs(*, root: Path, run_id: str) -> None:
        run_dir = root / "docs" / "agent_runs" / run_id
        bg_dir = run_dir / "background"
        now = time.time()
        recent = now - 60
        _touch(bg_dir / f"{run_id}_meta.json", mtime=recent)
        # Sin agent_outputs / raw_outputs

    label = "partial_in_progress_meta_no_outputs"
    run_id = "run_in_progress"
    with tempfile.TemporaryDirectory(prefix="audit-health-") as td:
        root = Path(td)
        _patch_module_paths(audit, root)
        _write_text(audit.RUN_INDEX, "# RUN_INDEX\n")
        setup_partial_in_progress_meta_no_outputs(root=root, run_id=run_id)
        got = audit.check_run_health(run_id, stale_minutes=15)

        if got.get("health_status") != "partial":
            raise AssertionError(f"{label}: health_status esperado='partial' got={got}")

        recs_lower = [r.lower() for r in got.get("recommendations", [])]
        if not any("check_opencode_run_status" in r for r in recs_lower):
            raise AssertionError(
                f"{label}: recommendations debe contener 'check_opencode_run_status'. Got: {got.get('recommendations')}"
            )
        if any("archivar" in r for r in recs_lower):
            raise AssertionError(
                f"{label}: recommendations no debe contener 'Archivar' (archive prematuro). Got: {got.get('recommendations')}"
            )
        if got.get("archive_recommended", False):
            raise AssertionError(
                f"{label}: archive_recommended debe ser False (run en progreso). Got: {got}"
            )

        cases.append({"label": label, "ok": True, "health_status": got.get("health_status"), "got": got})

    print(json.dumps({"ok": True, "cases": cases}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
