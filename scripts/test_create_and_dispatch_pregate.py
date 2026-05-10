"""test_create_and_dispatch_pregate.py

Standalone tests for the operational_status pre-gate in
create_and_dispatch_opencode_handoff.

Usage:
    python scripts/test_create_and_dispatch_pregate.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]

# Ensure ROOT is on sys.path so we can import the target module.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _make_opencode_handoff_args(
    *, extra: list[str] | None = None, project_id: str = "orchestrator"
) -> list[str]:
    args = [
        "create_and_dispatch_opencode_handoff.py",
        "--project-id", project_id,
        "--objective", "test objective for pre-gate",
        "--target-agent", "light-builder",
        "--model", "opencode-go/deepseek-v4-flash",
        "--risk-level", "low",
        "--scenario", "implementation",
    ]
    if extra:
        args.extend(extra)
    return args


class TestPregateBlocked(unittest.TestCase):
    """Pre-gate blocks and no artifacts are created."""

    @patch("scripts.create_and_dispatch_opencode_handoff.compute_operational_status")
    def test_blocked_pregate_creates_no_artifacts(self, mock_compute):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            mock_queue = tmp_path / "queue"
            mock_runs = tmp_path / "runs"

            mock_compute.return_value = (
                {
                    "ok": False,
                    "status": "error",
                    "mode": "operational-status",
                    "build_blocked": True,
                    "ready_to_advance": False,
                    "overall_status": "error",
                    "blockers": ["git_dirty", "quick_failed"],
                    "next_action": {
                        "decision": "stop",
                        "tool": "git",
                        "command": "git status --short",
                    },
                    "git_clean": False,
                    "runner_quick": {"status": "failed", "passed": 0, "failed": 1},
                    "verify_master_files": {"status": "ok"},
                    "elapsed_ms": 42,
                },
                1,
            )

            with patch(
                "scripts.create_and_dispatch_opencode_handoff.QUEUE_INBOX", mock_queue
            ), patch("scripts.create_and_dispatch_opencode_handoff.RUNS", mock_runs):

                from scripts.create_and_dispatch_opencode_handoff import main

                test_args = _make_opencode_handoff_args()

                with patch.object(sys, "argv", test_args):
                    with self.assertRaises(SystemExit) as cm:
                        main()

                self.assertEqual(cm.exception.code, 1)

                self.assertFalse(
                    mock_queue.exists(), "QUEUE_INBOX should not exist when blocked"
                )
                self.assertFalse(
                    mock_runs.exists(), "RUNS should not exist when blocked"
                )


class TestPregatePassingWithAuth(unittest.TestCase):
    """Pre-gate passes but requires_authorization -> waiting_authorization + pre_gate in JSON."""

    @patch("scripts.create_and_dispatch_opencode_handoff.compute_operational_status")
    def test_passing_with_auth_includes_pregate(self, mock_compute):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            mock_queue = tmp_path / "queue"
            mock_runs = tmp_path / "runs"

            mock_compute.return_value = (
                {
                    "ok": True,
                    "status": "ok",
                    "mode": "operational-status",
                    "build_blocked": False,
                    "ready_to_advance": True,
                    "overall_status": "ok",
                    "blockers": [],
                    "next_action": {
                        "decision": "advance",
                        "tool": "audit_agent_artifacts",
                        "command": "avanzar a siguiente tarea o build",
                    },
                    "git_clean": True,
                    "runner_quick": {
                        "status": "ok",
                        "passed": 5,
                        "failed": 0,
                    },
                    "verify_master_files": {"status": "ok"},
                    "elapsed_ms": 37,
                },
                0,
            )

            with patch(
                "scripts.create_and_dispatch_opencode_handoff.QUEUE_INBOX", mock_queue
            ), patch("scripts.create_and_dispatch_opencode_handoff.RUNS", mock_runs):

                from scripts.create_and_dispatch_opencode_handoff import main

                test_args = _make_opencode_handoff_args(
                    extra=[
                        "--requires-authorization",
                        "true",
                        "--authorization-granted",
                        "false",
                    ]
                )

                with patch.object(sys, "argv", test_args):
                    main()

                self.assertTrue(
                    mock_queue.exists(), "QUEUE_INBOX should exist when passing"
                )
                self.assertTrue(
                    mock_runs.exists(), "RUNS should exist when passing"
                )

                json_files = list(mock_queue.glob("*.json"))
                self.assertEqual(len(json_files), 1)

                package = json.loads(json_files[0].read_text(encoding="utf-8"))

                self.assertIn("pre_gate", package, "package JSON should include pre_gate")
                pg = package["pre_gate"]
                self.assertIsInstance(pg, dict)
                self.assertEqual(pg.get("overall_status"), "ok")
                self.assertEqual(pg.get("build_blocked"), False)
                self.assertEqual(pg.get("ready_to_advance"), True)
                self.assertIsNotNone(pg.get("elapsed_ms"))

                self.assertEqual(package.get("status"), "created")
                self.assertEqual(package.get("authorization_granted"), False)
                self.assertEqual(package.get("requires_authorization"), True)


def _write_registry_file(path: Path, entries: list[dict[str, object]]) -> None:
    """Create a minimal registry markdown file for end-to-end tests."""

    lines: list[str] = ["# PROJECT_REGISTRY.md", ""]
    for e in entries:
        lines.append(f"project_id: {e.get('project_id', '')}")
        lines.append(f"nombre_canónico: {e.get('nombre_canónico', '')}")
        aliases = e.get("alias_permitidos") or []
        if isinstance(aliases, list):
            lines.append(f"alias_permitidos: {', '.join(str(a) for a in aliases)}")
        else:
            lines.append(f"alias_permitidos: {aliases}")
        lines.append(f"ruta_local: {e.get('ruta_local', '')}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


class TestResolveTargetProjectEndToEnd(unittest.TestCase):
    """End-to-end dry-run validation: registry temp -> resolution -> handoff artifacts."""

    @patch("scripts.create_and_dispatch_opencode_handoff.compute_operational_status")
    def test_a_project_resolved_and_attached(self, mock_compute):
        """Resolved project via project_id auto-resolution attaches target_project + MD/TRACE/SUMMARY lines."""

        mock_compute.return_value = (
            {
                "ok": True,
                "build_blocked": False,
                "ready_to_advance": True,
                "overall_status": "ok",
                "blockers": [],
                "next_action": {"decision": "advance"},
                "git_clean": True,
                "runner_quick": {"status": "ok", "passed": 5, "failed": 0},
                "verify_master_files": {"status": "ok"},
                "elapsed_ms": 37,
            },
            0,
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            reg_path = tmp_path / "PROJECT_REGISTRY.md"
            _write_registry_file(
                reg_path,
                [
                    {
                        "project_id": "alpha",
                        "nombre_canónico": "Alpha Project",
                        "ruta_local": str(tmp_path / "alpha"),
                        "alias_permitidos": ["a", "alfa"],
                    }
                ],
            )

            mock_queue = tmp_path / "queue"
            mock_runs = tmp_path / "runs"

            with patch(
                "scripts.create_and_dispatch_opencode_handoff.QUEUE_INBOX", mock_queue
            ), patch("scripts.create_and_dispatch_opencode_handoff.RUNS", mock_runs):

                from scripts.create_and_dispatch_opencode_handoff import main

                # requires_authorization=true to avoid actual async OpenCode dispatch
                test_args = _make_opencode_handoff_args(
                    project_id="alpha",
                    extra=[
                        "--requires-authorization",
                        "true",
                        "--registry-path",
                        str(reg_path),
                    ],
                )

                with patch.object(sys, "argv", test_args):
                    main()

                json_files = list(mock_queue.glob("*.json"))
                self.assertEqual(len(json_files), 1)
                package = json.loads(json_files[0].read_text(encoding="utf-8"))

                self.assertIn("target_project", package)
                tp = package["target_project"]
                self.assertTrue(tp.get("ok"))
                self.assertTrue(tp.get("project_found"))
                self.assertEqual(tp.get("matched_by"), "project_id")
                self.assertEqual(tp.get("project", {}).get("id"), "alpha")
                self.assertEqual(tp.get("project", {}).get("name"), "Alpha Project")
                self.assertEqual(tp.get("resolution_source"), "project_id auto-resolution")
                self.assertEqual(tp.get("query"), "alpha")

                # MD includes compact target_project summary
                md_files = list(mock_queue.glob("*.md"))
                self.assertEqual(len(md_files), 1)
                md_content = md_files[0].read_text(encoding="utf-8")
                self.assertIn("target_project_id: `alpha`", md_content)
                self.assertIn("target_project_name: `Alpha Project`", md_content)
                self.assertIn("target_project_matched_by: `project_id`", md_content)

                run_id = package.get("run_id")
                self.assertTrue(run_id)

                trace_content = (mock_runs / str(run_id) / "TRACE.md").read_text(encoding="utf-8")
                self.assertIn("target_project_id: alpha", trace_content)
                self.assertIn("target_project_name: Alpha Project", trace_content)

                summary_content = (mock_runs / str(run_id) / "RUN_SUMMARY.md").read_text(encoding="utf-8")
                self.assertIn("target_project_id: alpha", summary_content)
                self.assertIn("target_project_name: Alpha Project", summary_content)

    @patch("scripts.create_and_dispatch_opencode_handoff.compute_operational_status")
    def test_b_project_ambiguous_blocks_without_artifacts(self, mock_compute):
        """Ambiguous alias blocks with status=blocked_target_project and creates no artifacts."""

        mock_compute.return_value = (
            {
                "ok": True,
                "build_blocked": False,
                "ready_to_advance": True,
                "overall_status": "ok",
                "blockers": [],
                "next_action": {"decision": "advance"},
                "git_clean": True,
                "runner_quick": {"status": "ok", "passed": 5, "failed": 0},
                "verify_master_files": {"status": "ok"},
                "elapsed_ms": 37,
            },
            0,
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            reg_path = tmp_path / "PROJECT_REGISTRY.md"
            _write_registry_file(
                reg_path,
                [
                    {
                        "project_id": "project-a",
                        "nombre_canónico": "Project A",
                        "ruta_local": "/fake/path/a",
                        "alias_permitidos": ["shared"],
                    },
                    {
                        "project_id": "project-b",
                        "nombre_canónico": "Project B",
                        "ruta_local": "/fake/path/b",
                        "alias_permitidos": ["shared"],
                    },
                ],
            )

            mock_queue = tmp_path / "queue"
            mock_runs = tmp_path / "runs"

            with patch(
                "scripts.create_and_dispatch_opencode_handoff.QUEUE_INBOX", mock_queue
            ), patch("scripts.create_and_dispatch_opencode_handoff.RUNS", mock_runs):

                from scripts.create_and_dispatch_opencode_handoff import main

                test_args = _make_opencode_handoff_args(
                    project_id="shared",
                    extra=["--registry-path", str(reg_path)],
                )

                buf = StringIO()
                with patch.object(sys, "stdout", buf), patch.object(sys, "argv", test_args):
                    with self.assertRaises(SystemExit) as cm:
                        main()

                self.assertEqual(cm.exception.code, 1)

                payload = json.loads(buf.getvalue())
                self.assertEqual(payload.get("status"), "blocked_target_project")
                tp = payload.get("target_project") or {}
                self.assertFalse(tp.get("ok"))
                self.assertEqual(tp.get("matched_by"), "alias")
                self.assertGreaterEqual(len(tp.get("candidates") or []), 2)

                self.assertFalse(mock_queue.exists(), "QUEUE_INBOX should not exist when blocked")
                self.assertFalse(mock_runs.exists(), "RUNS should not exist when blocked")

    @patch("scripts.create_and_dispatch_opencode_handoff.compute_operational_status")
    def test_c_project_not_found_blocks_without_artifacts(self, mock_compute):
        """Not found blocks with status=blocked_target_project and creates no artifacts."""

        mock_compute.return_value = (
            {
                "ok": True,
                "build_blocked": False,
                "ready_to_advance": True,
                "overall_status": "ok",
                "blockers": [],
                "next_action": {"decision": "advance"},
                "git_clean": True,
                "runner_quick": {"status": "ok", "passed": 5, "failed": 0},
                "verify_master_files": {"status": "ok"},
                "elapsed_ms": 37,
            },
            0,
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            reg_path = tmp_path / "PROJECT_REGISTRY.md"
            _write_registry_file(
                reg_path,
                [
                    {
                        "project_id": "alpha",
                        "nombre_canónico": "Alpha Project",
                        "ruta_local": "/fake/path/alpha",
                        "alias_permitidos": ["a"],
                    }
                ],
            )

            mock_queue = tmp_path / "queue"
            mock_runs = tmp_path / "runs"

            with patch(
                "scripts.create_and_dispatch_opencode_handoff.QUEUE_INBOX", mock_queue
            ), patch("scripts.create_and_dispatch_opencode_handoff.RUNS", mock_runs):

                from scripts.create_and_dispatch_opencode_handoff import main

                test_args = _make_opencode_handoff_args(
                    project_id="does-not-exist",
                    extra=["--registry-path", str(reg_path)],
                )

                buf = StringIO()
                with patch.object(sys, "stdout", buf), patch.object(sys, "argv", test_args):
                    with self.assertRaises(SystemExit) as cm:
                        main()

                self.assertEqual(cm.exception.code, 1)

                payload = json.loads(buf.getvalue())
                self.assertEqual(payload.get("status"), "blocked_target_project")
                tp = payload.get("target_project") or {}
                self.assertFalse(tp.get("ok"))
                errors = tp.get("errors") or []
                self.assertTrue(any("no project matched" in str(e) for e in errors))

                self.assertFalse(mock_queue.exists(), "QUEUE_INBOX should not exist when blocked")
                self.assertFalse(mock_runs.exists(), "RUNS should not exist when blocked")


    @patch("scripts.create_and_dispatch_opencode_handoff.compute_operational_status")
    def test_d_project_via_flag_resolved(self, mock_compute):
        """--project flag forces resolution even when project_id would be skipped."""

        mock_compute.return_value = (
            {
                "ok": True,
                "build_blocked": False,
                "ready_to_advance": True,
                "overall_status": "ok",
                "blockers": [],
                "next_action": {"decision": "advance"},
                "git_clean": True,
                "runner_quick": {"status": "ok", "passed": 5, "failed": 0},
                "verify_master_files": {"status": "ok"},
                "elapsed_ms": 37,
            },
            0,
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            reg_path = tmp_path / "PROJECT_REGISTRY.md"
            _write_registry_file(
                reg_path,
                [
                    {
                        "project_id": "orchestrator",
                        "nombre_canónico": "Local Orchestrator",
                        "ruta_local": str(ROOT),
                        "alias_permitidos": ["agente", "orq"],
                    }
                ],
            )

            mock_queue = tmp_path / "queue"
            mock_runs = tmp_path / "runs"

            with patch(
                "scripts.create_and_dispatch_opencode_handoff.QUEUE_INBOX", mock_queue
            ), patch("scripts.create_and_dispatch_opencode_handoff.RUNS", mock_runs):

                from scripts.create_and_dispatch_opencode_handoff import main

                test_args = _make_opencode_handoff_args(
                    project_id="orchestrator",
                    extra=[
                        "--requires-authorization",
                        "true",
                        "--project",
                        "orchestrator",
                        "--registry-path",
                        str(reg_path),
                    ],
                )

                with patch.object(sys, "argv", test_args):
                    main()

                json_files = list(mock_queue.glob("*.json"))
                self.assertEqual(len(json_files), 1)
                package = json.loads(json_files[0].read_text(encoding="utf-8"))

                self.assertIn("target_project", package)
                tp = package["target_project"]
                self.assertTrue(tp.get("ok"))
                self.assertTrue(tp.get("project_found"))
                self.assertEqual(tp.get("resolution_source"), "--project flag")
                self.assertEqual(tp.get("query"), "orchestrator")
                self.assertEqual(tp.get("project", {}).get("id"), "orchestrator")

                md_files = list(mock_queue.glob("*.md"))
                self.assertEqual(len(md_files), 1)
                md_content = md_files[0].read_text(encoding="utf-8")
                self.assertIn("target_project_id: `orchestrator`", md_content)
                self.assertIn(
                    "target_project_resolution_source: `--project flag`", md_content
                )

    @patch("scripts.create_and_dispatch_opencode_handoff.compute_operational_status")
    def test_e_orchestrator_without_flag_no_resolution(self, mock_compute):
        """project_id=orchestrator without --project flag skips resolution entirely."""

        mock_compute.return_value = (
            {
                "ok": True,
                "build_blocked": False,
                "ready_to_advance": True,
                "overall_status": "ok",
                "blockers": [],
                "next_action": {"decision": "advance"},
                "git_clean": True,
                "runner_quick": {"status": "ok", "passed": 5, "failed": 0},
                "verify_master_files": {"status": "ok"},
                "elapsed_ms": 37,
            },
            0,
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            mock_queue = tmp_path / "queue"
            mock_runs = tmp_path / "runs"

            with patch(
                "scripts.create_and_dispatch_opencode_handoff.QUEUE_INBOX", mock_queue
            ), patch("scripts.create_and_dispatch_opencode_handoff.RUNS", mock_runs):

                from scripts.create_and_dispatch_opencode_handoff import main

                test_args = _make_opencode_handoff_args(
                    project_id="orchestrator",
                    extra=["--requires-authorization", "true"],
                )

                with patch.object(sys, "argv", test_args):
                    main()

                json_files = list(mock_queue.glob("*.json"))
                self.assertEqual(len(json_files), 1)
                package = json.loads(json_files[0].read_text(encoding="utf-8"))

                self.assertNotIn("target_project", package)

                md_files = list(mock_queue.glob("*.md"))
                self.assertEqual(len(md_files), 1)
                md_content = md_files[0].read_text(encoding="utf-8")
                self.assertNotIn("target_project_id:", md_content)
                self.assertNotIn("target_project_resolution_source:", md_content)


if __name__ == "__main__":
    unittest.main()
