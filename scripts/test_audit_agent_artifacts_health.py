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

    # --- Tests for infer_latest_run_id() ---

    # 7) infer_latest_run_id desde runs_dir
    label_inf = "infer_latest_run_id_from_runs_dir"
    with tempfile.TemporaryDirectory(prefix="audit-latest-run-") as td:
        root = Path(td)
        _patch_module_paths(audit, root)
        run_a = root / "docs" / "agent_runs" / "run_20260510_112400"
        run_b = root / "docs" / "agent_runs" / "run_20260510_113000"
        run_a.mkdir(parents=True)
        run_b.mkdir(parents=True)
        now = time.time()
        os.utime(run_a, (now - 3600, now - 3600))
        os.utime(run_b, (now, now))

        got = audit.infer_latest_run_id()
        if got != "run_20260510_113000":
            raise AssertionError(f"{label_inf}: expected run_20260510_113000, got {got}")
        cases.append({"label": label_inf, "ok": True, "got": got})

    # 8) infer_latest_run_id fallback inbox
    label_inf = "infer_latest_run_id_fallback_inbox"
    with tempfile.TemporaryDirectory(prefix="audit-latest-run-") as td:
        root = Path(td)
        _patch_module_paths(audit, root)
        inbox_dir = root / "docs" / "agent_queue" / "inbox"
        inbox_dir.mkdir(parents=True)
        handoff = inbox_dir / "run_20260510_114500.md"
        handoff.write_text("handoff")
        now = time.time()
        os.utime(handoff, (now, now))

        got = audit.infer_latest_run_id()
        if got != "run_20260510_114500":
            raise AssertionError(f"{label_inf}: expected run_20260510_114500, got {got}")
        cases.append({"label": label_inf, "ok": True, "got": got})

    # 9) infer_latest_run_id none
    label_inf = "infer_latest_run_id_none"
    with tempfile.TemporaryDirectory(prefix="audit-latest-run-") as td:
        root = Path(td)
        _patch_module_paths(audit, root)
        got = audit.infer_latest_run_id()
        if got is not None:
            raise AssertionError(f"{label_inf}: expected None, got {got}")
        cases.append({"label": label_inf, "ok": True, "got": got})

    # --- Tests for compute_operational_status() ---

    # 10) compute_operational_status sin git/subprocess, latest_run failed -> overall_status=error
    label_cs = "compute_operational_status_latest_run_failed"
    with tempfile.TemporaryDirectory(prefix="audit-op-status-") as td:
        root = Path(td)
        _patch_module_paths(audit, root)
        _write_text(audit.RUN_INDEX, "# RUN_INDEX\n")

        run_dir = root / "docs" / "agent_runs" / "run_failed_001"
        run_dir.mkdir(parents=True)
        _write_text(run_dir / "RUN_SUMMARY.md", "Último estado registrado: `failed`\n")

        result, exit_code = audit.compute_operational_status(
            include_git_status=False,
            run_quick_checks=False,
            verify_master_files=False,
        )

        if result.get("overall_status") != "error":
            raise AssertionError(f"{label_cs}: overall_status debe ser 'error'. Got: {result}")
        if exit_code != 2:
            raise AssertionError(f"{label_cs}: exit_code debe ser 2. Got: {exit_code}")
        if result.get("latest_run_relevant") is None:
            raise AssertionError(f"{label_cs}: latest_run_relevant no debe ser None. Got: {result}")
        if (result.get("latest_run_relevant") or {}).get("health_status") != "failed":
            raise AssertionError(f"{label_cs}: latest_run health_status debe ser 'failed'. Got: {result}")
        if result.get("build_blocked") is not True:
            raise AssertionError(f"{label_cs}: build_blocked debe ser True. Got: {result}")
        if "latest_run_failed" not in result.get("blockers", []):
            raise AssertionError(f"{label_cs}: blockers debe contener 'latest_run_failed'. Got: {result}")
        if (result.get("next_action") or {}).get("decision") != "stop":
            raise AssertionError(f"{label_cs}: next_action.decision debe ser 'stop'. Got: {result}")
        cases.append({"label": label_cs, "ok": True, "result": result})

    # 11) compute_operational_status sin git/subprocess, sin runs -> overall_status=ok
    label_cs = "compute_operational_status_empty"
    with tempfile.TemporaryDirectory(prefix="audit-op-status-") as td:
        root = Path(td)
        _patch_module_paths(audit, root)
        _write_text(audit.RUN_INDEX, "# RUN_INDEX\n")

        result, exit_code = audit.compute_operational_status(
            include_git_status=False,
            run_quick_checks=False,
            verify_master_files=False,
        )

        if result.get("overall_status") != "ok":
            raise AssertionError(f"{label_cs}: overall_status debe ser 'ok'. Got: {result}")
        if exit_code != 0:
            raise AssertionError(f"{label_cs}: exit_code debe ser 0. Got: {exit_code}")
        if result.get("latest_run_relevant") is not None:
            raise AssertionError(f"{label_cs}: latest_run_relevant debe ser None. Got: {result}")
        if result.get("ready_to_advance") is not True:
            raise AssertionError(f"{label_cs}: ready_to_advance debe ser True. Got: {result}")
        if result.get("build_blocked") is not False:
            raise AssertionError(f"{label_cs}: build_blocked debe ser False. Got: {result}")
        if (result.get("next_action") or {}).get("decision") != "advance":
            raise AssertionError(f"{label_cs}: next_action.decision debe ser 'advance'. Got: {result}")
        cases.append({"label": label_cs, "ok": True, "result": result})

    # 12) compute_operational_status quick fail with first_failure.command -> rerun specific command
    label_cs = "compute_operational_status_quick_fail_rerun_specific"
    with tempfile.TemporaryDirectory(prefix="audit-op-status-") as td:
        root = Path(td)
        _patch_module_paths(audit, root)
        _write_text(audit.RUN_INDEX, "# RUN_INDEX\n")

        simulated_first_failure = {
            "name": "test_mypy",
            "returncode": 1,
            "command": ["python", "-m", "mypy", "scripts/audit_agent_artifacts.py"],
        }

        def _mock_run_subprocess_json(command, timeout_s=120):
            return {
                "ok": False,
                "mode": "quick",
                "total_checks": 2,
                "passed": 1,
                "failed": 1,
                "first_failure": simulated_first_failure,
                "checks": [
                    {"name": "test_flake8", "command": ["python", "-m", "flake8", "scripts/audit_agent_artifacts.py"], "ok": True, "returncode": 0},
                    {"name": "test_mypy", "command": simulated_first_failure["command"], "ok": False, "returncode": 1},
                ],
            }

        original_fn = audit._run_subprocess_json
        audit._run_subprocess_json = _mock_run_subprocess_json
        try:
            result, exit_code = audit.compute_operational_status(
                include_git_status=False,
                run_quick_checks=True,
                verify_master_files=False,
            )
        finally:
            audit._run_subprocess_json = original_fn

        if result.get("runner_quick") is None or result["runner_quick"].get("status") != "failed":
            raise AssertionError(f"{label_cs}: runner_quick debe ser failed. Got: {result.get('runner_quick')}")
        if result.get("overall_status") != "warn":
            raise AssertionError(f"{label_cs}: overall_status debe ser 'warn'. Got: {result}")
        if exit_code != 1:
            raise AssertionError(f"{label_cs}: exit_code debe ser 1. Got: {exit_code}")
        if "quick_failed" not in result.get("blockers", []):
            raise AssertionError(f"{label_cs}: blockers debe contener 'quick_failed'. Got: {result}")
        next_action = result.get("next_action") or {}
        if next_action.get("decision") != "correct":
            raise AssertionError(f"{label_cs}: next_action.decision debe ser 'correct'. Got: {next_action}")
        if next_action.get("tool") != "python":
            raise AssertionError(f"{label_cs}: next_action.tool debe ser 'python'. Got: {next_action}")
        expected_cmd = " ".join(simulated_first_failure["command"])
        if next_action.get("command") != expected_cmd:
            raise AssertionError(f"{label_cs}: next_action.command debe ser {expected_cmd!r}. Got: {next_action}")
        if "first_failure" in result.get("runner_quick", {}):
            ff = result["runner_quick"]["first_failure"]
            if ff and ff.get("command") != simulated_first_failure["command"]:
                raise AssertionError(f"{label_cs}: runner_quick.first_failure.command no coincide. Got: {ff}")
        cases.append({"label": label_cs, "ok": True, "result": result})

    # 13) compute_operational_status quick fail without first_failure.command -> fallback to full suite
    label_cs = "compute_operational_status_quick_fail_fallback_no_command"
    with tempfile.TemporaryDirectory(prefix="audit-op-status-") as td:
        root = Path(td)
        _patch_module_paths(audit, root)
        _write_text(audit.RUN_INDEX, "# RUN_INDEX\n")

        def _mock_run_subprocess_no_cmd(command, timeout_s=120):
            return {
                "ok": False,
                "mode": "quick",
                "total_checks": 2,
                "passed": 0,
                "failed": 2,
                "first_failure": {
                    "name": "test_flake8",
                    "returncode": 1,
                },
                "checks": [
                    {"name": "test_flake8", "command": ["python", "-m", "flake8", "."], "ok": False, "returncode": 1},
                ],
            }

        original_fn2 = audit._run_subprocess_json
        audit._run_subprocess_json = _mock_run_subprocess_no_cmd
        try:
            result, exit_code = audit.compute_operational_status(
                include_git_status=False,
                run_quick_checks=True,
                verify_master_files=False,
            )
        finally:
            audit._run_subprocess_json = original_fn2

        if result.get("runner_quick") is None or result["runner_quick"].get("status") != "failed":
            raise AssertionError(f"{label_cs}: runner_quick debe ser failed. Got: {result.get('runner_quick')}")
        next_action = result.get("next_action") or {}
        if next_action.get("decision") != "correct":
            raise AssertionError(f"{label_cs}: next_action.decision debe ser 'correct'. Got: {next_action}")
        if next_action.get("tool") != "run_local_checks":
            raise AssertionError(f"{label_cs}: next_action.tool debe ser 'run_local_checks'. Got: {next_action}")
        cases.append({"label": label_cs, "ok": True, "result": result})

    # --- Tests for next_actions_for_run() ---

    # 12) next_actions missing: run_id no encontrado
    label_nx = "next_actions_missing"
    with tempfile.TemporaryDirectory(prefix="audit-next-actions-") as td:
        root = Path(td)
        _patch_module_paths(audit, root)
        _write_text(audit.RUN_INDEX, "# RUN_INDEX\n")
        # No crear nada -> missing
        got = audit.next_actions_for_run("run_missing")

        if got.get("ok") is not True:
            raise AssertionError(f"{label_nx}: ok debe ser True, got={got}")
        if got.get("status") != "ok":
            raise AssertionError(f"{label_nx}: status debe ser 'ok', got={got}")
        if got.get("exists") is not False:
            raise AssertionError(f"{label_nx}: exists debe ser False, got={got}")
        if got.get("health_status") != "missing":
            raise AssertionError(f"{label_nx}: health_status debe ser 'missing', got={got}")
        if "run_health_check" not in got.get("suggested_tools", []):
            raise AssertionError(f"{label_nx}: suggested_tools debe contener 'run_health_check', got={got}")

        cases.append({"label": label_nx, "ok": True, "got": got})

    # 8) next_actions partial_in_progress: background meta reciente sin outputs
    label_nx = "next_actions_partial_in_progress"
    with tempfile.TemporaryDirectory(prefix="audit-next-actions-") as td:
        root = Path(td)
        _patch_module_paths(audit, root)
        _write_text(audit.RUN_INDEX, "# RUN_INDEX\n")
        setup_partial_in_progress_meta_no_outputs(root=root, run_id="run_in_progress")
        got = audit.next_actions_for_run("run_in_progress", stale_minutes=15)

        if got.get("ok") is not True:
            raise AssertionError(f"{label_nx}: ok debe ser True, got={got}")
        if "check_opencode_run_status" not in got.get("suggested_tools", []):
            raise AssertionError(
                f"{label_nx}: suggested_tools debe contener 'check_opencode_run_status', got={got}"
            )
        if len(got.get("next_actions", [])) == 0:
            raise AssertionError(f"{label_nx}: next_actions no debe estar vacío, got={got}")

        cases.append({"label": label_nx, "ok": True, "got": got})

    print(json.dumps({"ok": True, "cases": cases}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
