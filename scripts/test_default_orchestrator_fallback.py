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

    # Sin project_query ni workspace_path: debe caer al orquestador (daily-use default)
    plan = tools.plan_general_instruction(
        {
            "instruction": "Diagnostica este proyecto.",
            "include_git": False,
            "include_orchestrator_status": False,
            "include_preflight": False,
        }
    )

    assert plan.get("ok") is True
    assert plan.get("status") == "ok"
    assert plan.get("project_id") == "orchestrator"

    print("[PASS] plan_general_instruction defaulta al orquestador cuando no hay project_query/workspace_path")


if __name__ == "__main__":
    main()
