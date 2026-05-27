from __future__ import annotations

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def test_gate_finds_voiceflow_identity_context() -> None:
    from scripts.semantic_context_gate import build_report

    report = build_report(
        "embajadores-backend",
        "corrige envio de informe WhatsApp usando userId wa_id wa_from identity_context Voiceflow administrador",
        8,
    )

    assert report["status"] == "needs_context_review"
    paths = [str(match["path"]).replace("\\", "/").lower() for match in report["matches"]]
    joined = "\n".join(paths)
    assert "docs/technical_documentation.md" in joined
    assert ".agents/skills/voiceflow-project-rules/skill.md" in joined


def test_plan_blocks_dispatch_until_context_review() -> None:
    from mcp_server import tools

    plan = tools.plan_general_instruction(
        {
            "instruction": "corrige envio de informe WhatsApp usando userId wa_id wa_from identity_context Voiceflow administrador",
            "project_query": "embajadores-backend",
            "include_git": False,
            "include_orchestrator_status": False,
            "include_preflight": False,
        }
    )

    assert plan["ok"] is True
    assert plan["status"] == "ok", json.dumps(plan, ensure_ascii=False)[:1000]
    assert plan["next_frontier"] == "review_semantic_context"
    assert plan["recommended_next_tool_call"] is None
    assert plan["semantic_context_gate"]["status"] == "needs_context_review"


def main() -> None:
    test_gate_finds_voiceflow_identity_context()
    test_plan_blocks_dispatch_until_context_review()
    print("[PASS] semantic_context_gate encuentra contexto y bloquea dispatch hasta revision")


if __name__ == "__main__":
    main()
