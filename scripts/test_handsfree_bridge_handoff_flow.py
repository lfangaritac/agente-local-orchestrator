#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_PATH = ROOT / "mcp_server" / "tools.py"
BRIDGE_SCRIPT = ROOT / "scripts" / "orchestrator_bridge.py"


def _load_tools_module():
    spec = importlib.util.spec_from_file_location("mcp_tools", str(TOOLS_PATH))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def _run_bridge(*, workspace_path: Path, out_dir: Path, instruction: str, project_id: str | None = None) -> dict:
    cmd = [
        sys.executable,
        str(BRIDGE_SCRIPT),
        instruction,
        "--workspace-path",
        str(workspace_path),
        "--output-dir",
        str(out_dir),
    ]
    if project_id:
        cmd.extend(["--project-id", project_id])

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


def test_explicit_project_with_workspace_path() -> None:
    tools = _load_tools_module()

    with tempfile.TemporaryDirectory(prefix="handsfree_bridge_ws_") as tmp:
        ws = Path(tmp)
        out_dir = ws / "docs" / "handoffs"
        out_dir.mkdir(parents=True)

        _run_bridge(
            workspace_path=ws,
            out_dir=out_dir,
            instruction="Bridge test instruction (explicit project)",
            project_id=None,
        )

        result = tools.run_general_instruction_flow(
            {
                "mode": "plan",
                "instruction": "Toma el handoff generado por ./orquestador en dpm y avanza hasta la siguiente frontera segura.",
                "workspace_path": str(ws),
                "include_git": False,
                "include_orchestrator_status": False,
                "include_preflight": False,
            }
        )

        assert result.get("ok") is True
        assert result.get("routed_to") == "ingest_orchestrator_transfer"
        assert result.get("classified", {}).get("bridge_project_query") in {"dpm", "data-privacy-management-d", None}
        assert result.get("mode") == "plan"
        ingest = result.get("ingest")
        assert isinstance(ingest, dict)
        assert ingest.get("status") in {"ok", "project_not_confirmed", "handoff_not_found", "invalid_handoff"}

        # Should at least locate a handoff in this workspace
        if ingest.get("status") == "ok":
            handoff = ingest.get("handoff")
            assert isinstance(handoff, dict)
            assert str(handoff.get("handoff_json_path") or "").endswith(".json")

    print("[PASS] hands-free: proyecto explícito + workspace_path")


def test_active_project_uses_orchestrator_workspace() -> None:
    tools = _load_tools_module()

    # Create a temporary handoff inside orchestrator/docs/handoffs, then clean it.
    out_dir = ROOT / "docs" / "handoffs"
    out_dir.mkdir(parents=True, exist_ok=True)

    created_paths: list[Path] = []

    try:
        bridge = _run_bridge(
            workspace_path=ROOT,
            out_dir=out_dir,
            instruction="Diagnostica este proyecto.",
            project_id="orchestrator",
        )
        created_paths = [Path(bridge["created"]["json"]), Path(bridge["created"]["md"])]

        tools.set_active_project({"project_id": "orchestrator", "note": "handsfree_test"})

        result = tools.run_general_instruction_flow(
            {
                "mode": "plan",
                "instruction": "Continúa con el último handoff del proyecto activo.",
                "include_git": False,
                "include_orchestrator_status": False,
                "include_preflight": False,
            }
        )

        assert result.get("ok") is True
        assert result.get("routed_to") == "ingest_orchestrator_transfer"
        ingest = result.get("ingest")
        assert isinstance(ingest, dict)
        assert ingest.get("status") == "ok"

    finally:
        # Cleanup created handoff files
        for p in created_paths:
            try:
                if p.exists():
                    p.unlink()
            except Exception:
                pass

    print("[PASS] hands-free: proyecto activo (orchestrator) sin rutas explícitas")


def test_missing_active_project_prompts_minimum_question() -> None:
    tools = _load_tools_module()

    # Best-effort clear active_project
    try:
        state_path = Path(getattr(tools, "ACTIVE_PROJECT_PATH"))
        if state_path.exists():
            state_path.unlink()
    except Exception:
        pass

    result = tools.run_general_instruction_flow(
        {
            "mode": "plan",
            "instruction": "Procesa el último handoff del bridge.",
            "include_git": False,
            "include_orchestrator_status": False,
            "include_preflight": False,
        }
    )

    assert result.get("ok") is True
    assert result.get("status") in {"missing_inputs", "project_not_confirmed"}
    assert isinstance(result.get("next_question"), str) and result.get("next_question")

    print("[PASS] hands-free: sin proyecto activo pide dato mínimo")


def test_explicit_handoff_path_in_instruction() -> None:
    tools = _load_tools_module()

    with tempfile.TemporaryDirectory(prefix="handsfree_bridge_ws_") as tmp:
        ws = Path(tmp)
        out_dir = ws / "docs" / "handoffs"
        out_dir.mkdir(parents=True)

        bridge = _run_bridge(
            workspace_path=ws,
            out_dir=out_dir,
            instruction="Bridge test instruction (explicit path)",
            project_id=None,
        )
        handoff_json = Path(bridge["created"]["json"])
        assert handoff_json.exists()

        result = tools.run_general_instruction_flow(
            {
                "mode": "plan",
                "instruction": f"Procesa este handoff: {handoff_json}",
                "include_git": False,
                "include_orchestrator_status": False,
                "include_preflight": False,
            }
        )

        assert result.get("ok") is True
        assert result.get("routed_to") == "ingest_orchestrator_transfer"
        ingest = result.get("ingest")
        assert isinstance(ingest, dict)
        assert ingest.get("handoff", {}).get("handoff_json_path") == str(handoff_json)

    print("[PASS] hands-free: ruta explícita embebida en la instrucción")


def main() -> None:
    test_explicit_project_with_workspace_path()
    test_active_project_uses_orchestrator_workspace()
    test_missing_active_project_prompts_minimum_question()
    test_explicit_handoff_path_in_instruction()


if __name__ == "__main__":
    main()
