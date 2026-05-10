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
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]

# Ensure ROOT is on sys.path so we can import the target module.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _make_opencode_handoff_args(*, extra: list[str] | None = None) -> list[str]:
    args = [
        "create_and_dispatch_opencode_handoff.py",
        "--project-id", "test-pregate",
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


if __name__ == "__main__":
    unittest.main()
