#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_PATH = ROOT / "mcp_server" / "tools.py"


def _load_tools_module():
    spec = importlib.util.spec_from_file_location("mcp_tools", str(TOOLS_PATH))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def _write_active_state(tools, payload: dict) -> None:
    state_path = Path(getattr(tools, "ACTIVE_PROJECT_PATH"))
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> None:
    tools = _load_tools_module()

    # Clean previous state best-effort
    state_path = Path(getattr(tools, "ACTIVE_PROJECT_PATH"))
    try:
        if state_path.exists():
            state_path.unlink()
    except Exception:
        pass

    # Case 1: missing_inputs (no active_project.json)
    r1 = tools.sync_active_last_event_to_project_docs({"dry_run": True})
    assert r1.get("status") == "missing_inputs", f"expected missing_inputs, got {r1}"

    project_id = "sync-fixture-project"
    docs_dir = ROOT / "docs" / "projects" / project_id

    # Ensure a clean fixture directory
    if docs_dir.exists():
        shutil.rmtree(docs_dir)

    docs_dir.mkdir(parents=True, exist_ok=True)

    resume_path = docs_dir / "PROJECT_RESUME.md"
    frontier_path = docs_dir / "CURRENT_FRONTIER.md"

    resume_path.write_text(
        "\n".join(
            [
                f"# PROJECT_RESUME — {project_id}",
                "",
                "## 7) Handoffs / runs / returns relevantes",
                "",
                "- (stub)",
                "",
            ]
        ),
        encoding="utf-8",
    )

    frontier_path.write_text(
        "\n".join(
            [
                f"# CURRENT_FRONTIER — {project_id}",
                "",
                "## Referencias",
                "",
                "- (stub)",
                "",
            ]
        ),
        encoding="utf-8",
    )

    # Prepare active_project.json with last_event
    _write_active_state(
        tools,
        {
            "project_id": project_id,
            "set_at": "2026-01-01T00:00:00",
            "note": "fixture",
            "last_event": {
                "updated_at": "2026-01-02T03:04:05",
                "source": "test",
                "mode": "plan",
                "instruction": "Retoma y actualiza referencias.",
                "status": "ok",
                "next_frontier": "local_diagnostic_ready",
                "next_question": "¿Continuar?",
                "handoff_json_path": "docs/agent_queue/inbox/00000000_000000_abcdef01.json",
                "run_id": "20260509_103815_2841ce6d",
            },
        },
    )

    # Case 2: mismatch guardrail (requested project_id != active_project.project_id)
    r_mismatch = tools.sync_active_last_event_to_project_docs({"dry_run": True, "apply": False, "project_id": "other-project"})
    assert r_mismatch.get("ok") is False
    assert r_mismatch.get("status") == "error"
    assert "project_id_mismatch" in str(r_mismatch.get("error") or "")

    # Case 3: dry_run
    r2 = tools.sync_active_last_event_to_project_docs({"dry_run": True, "apply": False})
    assert r2.get("status") == "dry_run_ready", f"expected dry_run_ready, got {r2}"
    assert r2.get("changed") is False
    assert r2.get("would_change") is True

    # Case 3: apply
    r3 = tools.sync_active_last_event_to_project_docs({"dry_run": False, "apply": True})
    assert r3.get("status") == "applied", f"expected applied, got {r3}"

    # Verify markers were written
    resume_txt = _read_text(resume_path)
    frontier_txt = _read_text(frontier_path)

    assert "<!-- AUTO:last_event_refs:start -->" in resume_txt
    assert "<!-- AUTO:last_event_refs:end -->" in resume_txt
    assert "<!-- AUTO:last_event_refs:start -->" in frontier_txt
    assert "<!-- AUTO:last_event_refs:end -->" in frontier_txt

    # Case 4: idempotence (second apply should be no-op)
    r4 = tools.sync_active_last_event_to_project_docs({"dry_run": False, "apply": True})
    assert r4.get("status") == "applied"
    assert r4.get("changed") is False, f"expected changed=false on idempotent apply, got {r4}"

    # Case 5: no voluminoso
    max_chars = int(getattr(tools, "MAX_AUTO_BLOCK_CHARS", 1400))
    start = resume_txt.find("<!-- AUTO:last_event_refs:start -->")
    end = resume_txt.find("<!-- AUTO:last_event_refs:end -->")
    assert start != -1 and end != -1 and end > start
    block = resume_txt[start : end + len("<!-- AUTO:last_event_refs:end -->")]
    assert len(block) <= max_chars + 40, f"block too large: {len(block)} chars (max {max_chars})"

    # Case 6: no duplicación documental
    assert not (docs_dir / "DECISION_LOG.md").exists()
    assert not (docs_dir / "EVENT_LOG.md").exists()

    # Case 7: onboarding_required if required files missing
    resume_path.unlink()
    r5 = tools.sync_active_last_event_to_project_docs({"dry_run": True, "apply": False, "project_id": project_id})
    assert r5.get("status") == "onboarding_required", f"expected onboarding_required, got {r5}"

    # Cleanup
    try:
        if state_path.exists():
            state_path.unlink()
    except Exception:
        pass

    if docs_dir.exists():
        shutil.rmtree(docs_dir)

    print("[PASS] sync_active_last_event_to_project_docs: missing_inputs/onboarding_required/dry_run/apply/idempotent/compact/no-duplication")


if __name__ == "__main__":
    main()
