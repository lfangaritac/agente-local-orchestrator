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


def _safe_rm_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


def main() -> None:
    tools = _load_tools_module()

    project_id = "data-privacy-management-d"  # dpm fixture (registry already contains alias)
    docs_dir = ROOT / "docs" / "projects" / project_id

    # Track original state to keep repo clean.
    existed_before = docs_dir.exists()
    backups: dict[Path, bytes] = {}
    created_paths: list[Path] = []

    try:
        # 1) Ensure onboarding docs exist (create missing without overwrite)
        scaffold = tools.init_project_onboarding_scaffold({"project_id": project_id, "dry_run": False})
        assert scaffold.get("ok") is True, f"scaffold failed: {scaffold}"
        created = scaffold.get("created") if isinstance(scaffold, dict) else None
        if isinstance(created, list):
            created_paths = [Path(p) for p in created if isinstance(p, str) and p]

        # 2) Backup + write non-stub memory (PROJECT_RESUME + CURRENT_FRONTIER)
        resume_path = docs_dir / "PROJECT_RESUME.md"
        frontier_path = docs_dir / "CURRENT_FRONTIER.md"
        for p in (resume_path, frontier_path):
            if p.exists():
                backups[p] = p.read_bytes()

        resume_path.write_text(
            "\n".join(
                [
                    f"# PROJECT_RESUME — {project_id}",
                    "",
                    "## 4) Frontera actual",
                    "- Ver: `CURRENT_FRONTIER.md`",
                    "",
                    "## 9) Qué consultar antes de actuar",
                    "- `CURRENT_FRONTIER.md`",
                    "- `CRITICAL_ALERTS.md`",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        frontier_path.write_text(
            "\n".join(
                [
                    f"# CURRENT_FRONTIER — {project_id}",
                    "",
                    "- status: `in_progress`",
                    "- blocking_threshold: `none`",
                    "",
                    "## Próxima acción recomendada (única)",
                    "- next_action: Revisar HANDOFF_LOG y confirmar la siguiente tarea concreta.",
                    "- requires_user_action: no",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        # 3) Active project + last_event (session memory)
        tools.set_active_project({"project_id": project_id, "note": "resume_flow_test"})
        _write_active_state(
            tools,
            {
                "project_id": project_id,
                "set_at": "2026-05-20T00:00:00",
                "note": "resume_flow_test",
                "last_event": {
                    "updated_at": "2026-05-20T00:00:01",
                    "source": "test",
                    "mode": "plan",
                    "instruction": "Diagnostica este proyecto.",
                    "status": "ok",
                    "next_frontier": "local_diagnostic_ready",
                    "next_question": "",
                    "handoff_json_path": "",
                    "run_id": "",
                },
            },
        )

        # --- Test A: "retoma dpm" uses memory (no clone required) + context_pack level 0
        plan = tools.plan_general_instruction(
            {
                "instruction": "Retoma dpm.",
                "include_git": False,
                "include_orchestrator_status": False,
                "include_preflight": False,
            }
        )
        assert plan.get("status") == "ok", f"plan.status expected ok, got {plan}"
        assert plan.get("project_id") == project_id
        cp = plan.get("context_pack")
        assert isinstance(cp, dict) and int(cp.get("level")) == 0, f"context_pack.level expected 0, got {cp}"
        session_memory = cp.get("session_memory")
        assert isinstance(session_memory, dict) and isinstance(session_memory.get("last_event"), dict), "session_memory.last_event missing in context_pack"
        assert plan.get("next_frontier") == "resume_ready", f"next_frontier expected resume_ready, got {plan.get('next_frontier')}"

        # --- Test B: "retoma este proyecto" uses active_project (hands-free)
        flow = tools.run_general_instruction_flow(
            {
                # mode omitted on purpose: auto-mode should still be safe.
                "instruction": "Retoma este proyecto.",
                "include_git": False,
                "include_orchestrator_status": False,
                "include_preflight": False,
            }
        )
        assert flow.get("ok") is True
        assert flow.get("plan", {}).get("project_id") == project_id
        assert flow.get("dispatch", {}).get("status") in {"not_required", "not_safe_to_dispatch"}, f"dispatch expected not_required-like, got {flow.get('dispatch')}"

        # --- Test C: CURRENT_FRONTIER next_action can trigger executor suggestion (no premature stop)
        frontier_path.write_text(
            "\n".join(
                [
                    f"# CURRENT_FRONTIER — {project_id}",
                    "",
                    "- status: `in_progress`",
                    "- blocking_threshold: `none`",
                    "",
                    "## Próxima acción recomendada (única)",
                    "- next_action: Ejecutar context-validator para validar el estado real del repo.",
                    "- requires_user_action: no",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        plan2 = tools.plan_general_instruction(
            {
                "instruction": "Retoma dpm y avanza con el proyecto activo.",
                "include_git": False,
                "include_orchestrator_status": False,
                "include_preflight": False,
            }
        )
        assert plan2.get("status") == "ok"
        assert plan2.get("next_frontier") in {"dispatch_opencode", "fix_orchestrator", "request_authorization"}, f"expected a frontier that advances, got {plan2.get('next_frontier')}"
        rec = plan2.get("recommended_next_tool_call")
        assert isinstance(rec, dict) and rec.get("tool") == "create_and_dispatch_opencode_handoff", f"expected dispatch tool call, got {rec}"

        print("[PASS] resume flow: retoma dpm / active_project / frontier-driven dispatch suggestion")

    finally:
        # Restore modified files
        for p, b in backups.items():
            try:
                p.write_bytes(b)
            except Exception:
                pass

        # Cleanup scaffold artifacts to keep git clean.
        if not existed_before:
            _safe_rm_tree(docs_dir)
        else:
            # Remove only files created by the scaffold in this test run.
            for p in created_paths:
                try:
                    pp = Path(p)
                    if pp.exists() and pp.is_file() and pp not in backups:
                        pp.unlink()
                except Exception:
                    pass


if __name__ == "__main__":
    main()
