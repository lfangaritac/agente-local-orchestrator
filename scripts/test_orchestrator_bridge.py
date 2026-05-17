#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "orchestrator_bridge.py"


def _run(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    p = subprocess.run(
        [sys.executable, str(SCRIPT), *cmd],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return p.returncode, p.stdout, p.stderr


def _assert_required_fields(payload: dict) -> None:
    assert payload.get("mode") == "orchestrator_transfer"
    assert payload.get("channel") == "shell_bridge"
    assert isinstance(payload.get("timestamp"), str) and payload["timestamp"]
    assert isinstance(payload.get("instruction"), str) and payload["instruction"]

    assertions = payload.get("assertions")
    assert isinstance(assertions, dict)
    assert assertions.get("replit_agent_executed") is False
    assert assertions.get("functional_changes_made") is False


def test_generates_handoff_files() -> None:
    with tempfile.TemporaryDirectory(prefix="bridge_test_") as tmp:
        ws = Path(tmp)
        out_dir = ws / "docs" / "handoffs"
        out_dir.mkdir(parents=True)

        rc, out, err = _run(
            [
                "Avanza con este proyecto hasta la siguiente frontera segura",
                "--output-dir",
                str(out_dir),
            ],
            cwd=ws,
        )
        assert rc == 0, f"rc={rc} err={err} out={out}"

        data = json.loads(out)
        assert data.get("ok") is True
        created = data.get("created")
        assert isinstance(created, dict)

        json_path = Path(created["json"])
        md_path = Path(created["md"])
        assert json_path.exists()
        assert md_path.exists()

        payload = json.loads(json_path.read_text(encoding="utf-8", errors="replace"))
        _assert_required_fields(payload)

    print("[PASS] bridge genera JSON+MD con campos mínimos")


def test_return_to_replit_intent_flag() -> None:
    with tempfile.TemporaryDirectory(prefix="bridge_test_") as tmp:
        ws = Path(tmp)
        out_dir = ws / "docs" / "handoffs"
        out_dir.mkdir(parents=True)

        rc, out, err = _run(
            [
                "volver a replit",
                "--output-dir",
                str(out_dir),
                "--return-to-replit",
            ],
            cwd=ws,
        )
        assert rc == 0, f"rc={rc} err={err} out={out}"

        data = json.loads(out)
        payload = data.get("handoff")
        assert isinstance(payload, dict)
        assert payload.get("intent") == "return_to_replit"

    print("[PASS] intent return_to_replit soportado")


def main() -> None:
    test_generates_handoff_files()
    test_return_to_replit_intent_flag()


if __name__ == "__main__":
    main()
