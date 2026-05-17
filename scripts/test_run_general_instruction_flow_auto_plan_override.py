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

    flow = tools.run_general_instruction_flow(
        {
            # Nota: sin "mode" a propósito (auto-mode). Debe respetar "modo plan".
            "instruction": "Modo plan: diagnostica este proyecto.",
            "workspace_path": str(ROOT),
            "include_git": False,
            "include_orchestrator_status": False,
            "include_preflight": False,
        }
    )

    assert flow.get("ok") is True
    assert flow.get("mode") == "plan"

    # En plan: no debe despachar.
    assert "dispatch" not in flow

    print("[PASS] run_general_instruction_flow respeta 'modo plan' cuando mode no fue especificado")


if __name__ == "__main__":
    main()
