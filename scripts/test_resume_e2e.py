#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_PATH = ROOT / "mcp_server" / "tools.py"
REGISTRY_PATH = ROOT / "PROJECT_REGISTRY.md"


def _load_tools_module():
    spec = importlib.util.spec_from_file_location("mcp_tools", str(TOOLS_PATH))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def _walk_strings(obj, path: str = ""):
    if isinstance(obj, str):
        yield path, obj
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            kp = f"{path}.{k}" if path else str(k)
            yield from _walk_strings(v, kp)
        return
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            kp = f"{path}[{i}]"
            yield from _walk_strings(v, kp)
        return


def _assert_reference_based_compact(context_pack: dict) -> None:
    assert isinstance(context_pack, dict)

    # Guardrail: no strings enormes (dumps) en el context_pack.
    for p, s in _walk_strings(context_pack):
        assert len(s) <= 4000, f"context_pack contiene string demasiado largo en {p} ({len(s)} chars)"

    exclusions = context_pack.get("exclusions")
    assert isinstance(exclusions, dict)
    pog = exclusions.get("paths_or_globs")
    assert isinstance(pog, list) and pog, f"exclusions.paths_or_globs inválido: {pog}"


def _write_minimal_onboarding_ready_docs(docs_dir: Path) -> None:
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Crear el set mínimo requerido por _probe_project_onboarding.
    required = [
        "PROJECT_PROFILE.md",
        "PROJECT_RESUME.md",
        "CURRENT_FRONTIER.md",
        "ERRORS_AND_FIXES.md",
        "CONTEXT_INDEX.md",
        "CODE_CONTEXT_MAP.md",
        "DOCUMENTATION_AUDIT.md",
        "CRITICAL_ALERTS.md",
        "LESSONS_LOCAL.md",
        "SYNC_STATUS.md",
        "HANDOFF_LOG.md",
    ]

    for name in required:
        p = docs_dir / name
        if p.exists():
            continue
        p.write_text(f"# {name}\n\n(stub)\n", encoding="utf-8")

    # Enriquecer los 2 archivos clave con campos parseables.
    (docs_dir / "CURRENT_FRONTIER.md").write_text(
        "# CURRENT_FRONTIER\n\n"
        "- status: `blocked`\n"
        "- blocking_threshold: `authorization_required`\n"
        "- next_action: autorizar build low-risk y despachar\n"
        "- requires_user_action: sí\n",
        encoding="utf-8",
    )

    (docs_dir / "PROJECT_RESUME.md").write_text(
        "# PROJECT_RESUME\n\n"
        "- status_classification: `parcialmente_listo`\n"
        "- branch: `main`\n"
        "- last_commit: `abc1234 stub`\n\n"
        "<!-- AUTO:last_event_refs:start -->\n"
        "- run_id: `20260101_000000_deadbeef`\n"
        "<!-- AUTO:last_event_refs:end -->\n",
        encoding="utf-8",
    )


def test_resume_by_active_project(tools) -> None:
    fixture_pid = "fixture-resume-ready"
    fixture_alias = "fixture-ready"

    docs_dir = ROOT / "docs" / "projects" / fixture_pid
    fixture_root = ROOT / ".tmp_fixture_resume_ready"

    original_registry = REGISTRY_PATH.read_bytes()

    try:
        # workspace mínimo para que git_repo_exists=true
        if fixture_root.exists():
            shutil.rmtree(fixture_root)
        (fixture_root / ".git").mkdir(parents=True, exist_ok=True)

        # docs/projects/<pid> listo
        if docs_dir.exists():
            shutil.rmtree(docs_dir)
        _write_minimal_onboarding_ready_docs(docs_dir)

        # registry entry
        entry = (
            "\n\n### fixture-resume-ready\n\n"
            f"project_id: {fixture_pid}\n"
            "nombre_canónico: Fixture Resume Ready\n"
            f"alias_permitidos: {fixture_alias}\n"
            f"local_path: {fixture_root}\n"
            "repo_url: \n"
            "environment_type: local\n"
            "origen: local\n\n"
        ).encode("utf-8")
        REGISTRY_PATH.write_bytes(original_registry + entry)

        # active_project.json con last_event
        state_dir = ROOT / ".orchestrator_state"
        state_dir.mkdir(parents=True, exist_ok=True)
        tools.ACTIVE_PROJECT_PATH.write_text(
            json.dumps(
                {
                    "project_id": fixture_pid,
                    "set_at": "2026-01-01T00:00:00",
                    "note": "test",
                    "last_event": {
                        "updated_at": "2026-01-01T00:00:01",
                        "source": "run_general_instruction_flow",
                        "mode": "plan",
                        "instruction": "retoma",
                        "status": "ok",
                        "next_frontier": "dispatch_opencode",
                        "next_question": None,
                        "handoff_json_path": None,
                        "run_id": "20260101_000000_deadbeef",
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        plan = tools.plan_general_instruction(
            {
                "instruction": "Retoma el proyecto activo y continúa donde quedamos.",
                "include_git": False,
                "include_orchestrator_status": False,
                "include_preflight": False,
            }
        )

        assert plan.get("ok") is True
        assert plan.get("status") == "ok"
        assert plan.get("project_id") == fixture_pid

        assert plan.get("context_pack_level") == 0
        cp = plan.get("context_pack")
        assert isinstance(cp, dict)
        assert cp.get("level") == 0
        _assert_reference_based_compact(cp)

        # Memoria versionada debe estar presente (por referencias) y usable.
        vm = cp.get("versioned_memory")
        assert isinstance(vm, dict), f"versioned_memory faltante: {cp.keys()}"
        assert vm.get("status") == "ready"
        extracts = vm.get("extracts")
        assert isinstance(extracts, dict)
        assert "current_frontier" in extracts

        # Memoria de sesión (active_project.last_event) debe estar presente.
        sm = cp.get("session_memory")
        assert isinstance(sm, dict)
        le = sm.get("last_event")
        assert isinstance(le, dict)
        assert le.get("run_id") == "20260101_000000_deadbeef"

        # Guardrail: CURRENT_FRONTIER no debe forzar status=blocked.
        assert plan.get("status") == "ok"

    finally:
        REGISTRY_PATH.write_bytes(original_registry)
        if fixture_root.exists():
            shutil.rmtree(fixture_root)
        if docs_dir.exists():
            shutil.rmtree(docs_dir)
        # limpiar active_project.json
        try:
            if tools.ACTIVE_PROJECT_PATH.exists():
                tools.ACTIVE_PROJECT_PATH.unlink()
        except Exception:
            pass


def test_resume_by_alias(tools) -> None:
    fixture_pid = "fixture-resume-ready-2"
    fixture_alias = "fixture-ready-2"

    docs_dir = ROOT / "docs" / "projects" / fixture_pid
    fixture_root = ROOT / ".tmp_fixture_resume_ready_2"

    original_registry = REGISTRY_PATH.read_bytes()

    try:
        if fixture_root.exists():
            shutil.rmtree(fixture_root)
        (fixture_root / ".git").mkdir(parents=True, exist_ok=True)

        if docs_dir.exists():
            shutil.rmtree(docs_dir)
        _write_minimal_onboarding_ready_docs(docs_dir)

        entry = (
            "\n\n### fixture-resume-ready-2\n\n"
            f"project_id: {fixture_pid}\n"
            "nombre_canónico: Fixture Resume Ready 2\n"
            f"alias_permitidos: {fixture_alias}\n"
            f"local_path: {fixture_root}\n"
            "repo_url: \n"
            "environment_type: local\n"
            "origen: local\n\n"
        ).encode("utf-8")
        REGISTRY_PATH.write_bytes(original_registry + entry)

        plan = tools.plan_general_instruction(
            {
                "instruction": "Continúa donde quedamos.",
                "project_query": fixture_alias,
                "include_git": False,
                "include_orchestrator_status": False,
                "include_preflight": False,
            }
        )

        assert plan.get("ok") is True
        assert plan.get("status") == "ok"
        assert plan.get("project_id") == fixture_pid

        # Sigue siendo retoma (intent=resume) -> nivel 0.
        assert plan.get("context_pack_level") == 0
        cp = plan.get("context_pack")
        assert isinstance(cp, dict)
        _assert_reference_based_compact(cp)

        vm = cp.get("versioned_memory")
        assert isinstance(vm, dict)
        assert vm.get("status") == "ready"

    finally:
        REGISTRY_PATH.write_bytes(original_registry)
        if fixture_root.exists():
            shutil.rmtree(fixture_root)
        if docs_dir.exists():
            shutil.rmtree(docs_dir)


def test_incomplete_project_onboarding_required(tools) -> None:
    fixture_pid = "fixture-resume-incomplete"
    fixture_alias = "fixture-incomp"

    docs_dir = ROOT / "docs" / "projects" / fixture_pid
    fixture_root = ROOT / ".tmp_fixture_resume_incomplete"

    original_registry = REGISTRY_PATH.read_bytes()

    try:
        if fixture_root.exists():
            shutil.rmtree(fixture_root)
        (fixture_root / ".git").mkdir(parents=True, exist_ok=True)

        # Asegurar que NO exista scaffold
        if docs_dir.exists():
            shutil.rmtree(docs_dir)

        entry = (
            "\n\n### fixture-resume-incomplete\n\n"
            f"project_id: {fixture_pid}\n"
            "nombre_canónico: Fixture Resume Incomplete\n"
            f"alias_permitidos: {fixture_alias}\n"
            f"local_path: {fixture_root}\n"
            "repo_url: \n"
            "environment_type: local\n"
            "origen: local\n\n"
        ).encode("utf-8")
        REGISTRY_PATH.write_bytes(original_registry + entry)

        plan = tools.plan_general_instruction(
            {
                "instruction": "Retoma este proyecto.",
                "project_query": fixture_alias,
                "include_git": False,
                "include_orchestrator_status": False,
                "include_preflight": False,
            }
        )

        assert plan.get("ok") is True
        assert plan.get("status") == "onboarding_required"
        missing_files = plan.get("missing_files")
        assert isinstance(missing_files, list) and missing_files

        assert plan.get("context_pack_level") == 0
        cp = plan.get("context_pack")
        assert isinstance(cp, dict)
        _assert_reference_based_compact(cp)

        # En onboarding_required no debe inventar versioned_memory listo.
        assert cp.get("versioned_memory") is None

    finally:
        REGISTRY_PATH.write_bytes(original_registry)
        if fixture_root.exists():
            shutil.rmtree(fixture_root)
        if docs_dir.exists():
            shutil.rmtree(docs_dir)


def main() -> None:
    tools = _load_tools_module()
    test_resume_by_active_project(tools)
    test_resume_by_alias(tools)
    test_incomplete_project_onboarding_required(tools)
    print("[PASS] resume E2E: usa memoria versionada + session last_event + context_pack nivel 0/1")


if __name__ == "__main__":
    main()
