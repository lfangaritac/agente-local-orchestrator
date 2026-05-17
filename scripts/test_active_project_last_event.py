#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_PATH = ROOT / "mcp_server" / "tools.py"


def _load_tools_module():
    spec = importlib.util.spec_from_file_location("mcp_tools", str(TOOLS_PATH))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def main() -> None:
    tools = _load_tools_module()

    # Clear active state best-effort
    try:
        state_path = Path(getattr(tools, "ACTIVE_PROJECT_PATH"))
        if state_path.exists():
            state_path.unlink()
    except Exception:
        pass

    # Plan-only general instruction should set last_event
    flow = tools.run_general_instruction_flow(
        {
            "mode": "plan",
            "instruction": "Diagnostica este proyecto.",
            "workspace_path": str(ROOT),
            "include_git": False,
            "include_orchestrator_status": False,
            "include_preflight": False,
        }
    )

    assert flow.get("ok") is True

    active = tools.get_active_project({})
    assert active.get("ok") is True
    ap = active.get("active_project")
    assert isinstance(ap, dict)
    assert ap.get("project_id") == "orchestrator"

    last = ap.get("last_event")
    assert isinstance(last, dict)
    assert last.get("source") == "run_general_instruction_flow"
    assert last.get("mode") == "plan"
    assert isinstance(last.get("next_frontier"), str)

    print("[PASS] active_project incluye last_event actualizado por run_general_instruction_flow")


if __name__ == "__main__":
    main()
