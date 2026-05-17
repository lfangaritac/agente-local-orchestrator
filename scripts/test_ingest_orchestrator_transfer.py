#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_SCRIPT = ROOT / "scripts" / "orchestrator_bridge.py"
TOOLS_PATH = ROOT / "mcp_server" / "tools.py"


def _load_tools_module():
    spec = importlib.util.spec_from_file_location("mcp_tools", str(TOOLS_PATH))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def _run_bridge(*, workspace_path: Path, out_dir: Path, instruction: str, return_to_replit: bool = False) -> dict:
    cmd = [
        sys.executable,
        str(BRIDGE_SCRIPT),
        instruction,
        "--workspace-path",
        str(workspace_path),
        "--output-dir",
        str(out_dir),
    ]
    if return_to_replit:
        cmd.append("--return-to-replit")

    p = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    assert p.returncode == 0, f"bridge rc={p.returncode} stderr={p.stderr} stdout={p.stdout}"
    data = json.loads(p.stdout)
    assert data.get("ok") is True
    return data


def test_ingest_valid_handoff_plan_only() -> None:
    tools = _load_tools_module()

    with tempfile.TemporaryDirectory(prefix="ingest_transfer_test_") as tmp:
        ws = Path(tmp)
        out_dir = ws / "docs" / "handoffs"
        out_dir.mkdir(parents=True)

        bridge = _run_bridge(
            workspace_path=ROOT,
            out_dir=out_dir,
            instruction="Diagnostica este proyecto.",
            return_to_replit=False,
        )

        handoff_json = Path(bridge["created"]["json"])
        assert handoff_json.exists()

        result = tools.ingest_orchestrator_transfer(
            {
                "handoff_json_path": str(handoff_json),
                "include_git": False,
                "include_orchestrator_status": False,
                "include_preflight": False,
            }
        )

        assert result.get("ok") is True
        assert result.get("status") == "ok"

        handoff = result.get("handoff")
        assert isinstance(handoff, dict)
        assert handoff.get("handoff_json_path") == str(handoff_json)
        assert handoff.get("channel") == "shell_bridge"

        flow = result.get("flow")
        assert isinstance(flow, dict)
        assert flow.get("mode") == "plan"

        plan = flow.get("plan")
        assert isinstance(plan, dict)
        assert plan.get("project_id") == "orchestrator"

    print("[PASS] ingest procesa handoff válido y devuelve Plan interno")


def test_ingest_invalid_handoff_rejected() -> None:
    tools = _load_tools_module()

    with tempfile.TemporaryDirectory(prefix="ingest_transfer_test_") as tmp:
        ws = Path(tmp)
        bad = ws / "orchestrator_transfer_20990101_000000_deadbe.json"
        bad.write_text(json.dumps({"mode": "wrong"}), encoding="utf-8")

        result = tools.ingest_orchestrator_transfer({"handoff_json_path": str(bad)})
        assert result.get("ok") is True
        assert result.get("status") == "invalid_handoff"
        assert isinstance(result.get("error"), str) and result.get("error")

    print("[PASS] ingest rechaza handoff inválido")


def test_ingest_return_to_replit_flag() -> None:
    tools = _load_tools_module()

    with tempfile.TemporaryDirectory(prefix="ingest_transfer_test_") as tmp:
        ws = Path(tmp)
        out_dir = ws / "docs" / "handoffs"
        out_dir.mkdir(parents=True)

        bridge = _run_bridge(
            workspace_path=ROOT,
            out_dir=out_dir,
            instruction="volver a replit",
            return_to_replit=True,
        )

        handoff_json = Path(bridge["created"]["json"])
        assert handoff_json.exists()

        result = tools.ingest_orchestrator_transfer(
            {
                "handoff_json_path": str(handoff_json),
                "include_git": False,
                "include_orchestrator_status": False,
                "include_preflight": False,
            }
        )

        assert result.get("ok") is True
        assert result.get("status") == "return_to_replit"
        assert result.get("authorizations_required") == ["replit"]

    print("[PASS] return_to_replit no activa Replit; solo recomienda + pide autorización")


def main() -> None:
    test_ingest_valid_handoff_plan_only()
    test_ingest_invalid_handoff_rejected()
    test_ingest_return_to_replit_flag()


if __name__ == "__main__":
    main()
