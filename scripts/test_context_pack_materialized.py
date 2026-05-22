#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
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


def _assert_compact_reference_based(context_pack: dict) -> None:
    assert isinstance(context_pack, dict)

    # Guardrail: no strings enormes (dumps) en el context_pack.
    for p, s in _walk_strings(context_pack):
        assert len(s) <= 4000, f"context_pack contiene string demasiado largo en {p} ({len(s)} chars)"

    # Guardrail: debe declarar exclusiones por defecto (paths_or_globs)
    exclusions = context_pack.get("exclusions")
    assert isinstance(exclusions, dict), f"exclusions inválido: {exclusions}"
    pog = exclusions.get("paths_or_globs")
    assert isinstance(pog, list) and pog, f"exclusions.paths_or_globs inválido: {pog}"


def test_orchestrator_default_has_context_pack(tools) -> None:
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

    assert "context_pack_level" in plan, "plan debe incluir context_pack_level"
    assert "context_pack" in plan, "plan debe incluir context_pack"

    level = plan.get("context_pack_level")
    assert level in {0, 1}, f"context_pack_level inesperado: {level}"

    context_pack = plan.get("context_pack")
    assert isinstance(context_pack, dict)
    assert context_pack.get("level") == level

    _assert_compact_reference_based(context_pack)


def test_onboarding_required_has_minimal_context_pack(tools) -> None:
    fixture_pid = "fixture-context-pack"
    fixture_alias = "fixture-cp"

    # Asegurar que no exista scaffold previo (si quedó de corridas anteriores)
    docs_dir = ROOT / "docs" / "projects" / fixture_pid
    if docs_dir.exists():
        shutil.rmtree(docs_dir)

    # Preparar un "repo" local mínimo que no dispare clone_required:
    # basta con que exista el directorio y un .git/ para que git_repo_exists=true.
    fixture_root = ROOT / ".tmp_fixture_context_pack_project"
    if fixture_root.exists():
        shutil.rmtree(fixture_root)
    (fixture_root / ".git").mkdir(parents=True, exist_ok=True)

    original_bytes = REGISTRY_PATH.read_bytes()

    entry = (
        "\n\n### fixture-context-pack\n\n"
        f"project_id: {fixture_pid}\n"
        "nombre_canónico: Fixture Context Pack\n"
        f"alias_permitidos: {fixture_alias}\n"
        f"local_path: {fixture_root}\n"
        "repo_url: \n"
        "environment_type: local\n"
        "origen: local\n"
        "\n"
    ).encode("utf-8")

    try:
        REGISTRY_PATH.write_bytes(original_bytes + entry)

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
        assert plan.get("status") == "onboarding_required", f"status esperado onboarding_required, got {plan}"

        missing_files = plan.get("missing_files")
        assert isinstance(missing_files, list) and missing_files, f"missing_files inválido: {missing_files}"

        assert plan.get("context_pack_level") == 0
        context_pack = plan.get("context_pack")
        assert isinstance(context_pack, dict)
        _assert_compact_reference_based(context_pack)

        onboarding = context_pack.get("onboarding")
        assert isinstance(onboarding, dict)
        mf2 = onboarding.get("missing_files")
        assert isinstance(mf2, list) and mf2, f"onboarding.missing_files inválido: {mf2}"

    finally:
        # Restaurar registry y limpiar fixtures para dejar git limpio.
        REGISTRY_PATH.write_bytes(original_bytes)
        if fixture_root.exists():
            shutil.rmtree(fixture_root)
        if docs_dir.exists():
            shutil.rmtree(docs_dir)


def test_flow_propagates_context_pack(tools) -> None:
    flow = tools.run_general_instruction_flow(
        {
            "instruction": "Diagnostica este proyecto.",
            "include_git": False,
            "include_orchestrator_status": False,
            "include_preflight": False,
            "mode": "plan",
        }
    )

    assert flow.get("ok") is True
    assert "plan" in flow and isinstance(flow.get("plan"), dict)

    assert "context_pack_level" in flow
    assert "context_pack" in flow

    plan = flow["plan"]
    assert plan.get("context_pack_level") == flow.get("context_pack_level")


def main() -> None:
    tools = _load_tools_module()

    test_orchestrator_default_has_context_pack(tools)
    test_onboarding_required_has_minimal_context_pack(tools)
    test_flow_propagates_context_pack(tools)

    print("[PASS] context_pack materializado (plan_general_instruction) y propagado (run_general_instruction_flow)")


if __name__ == "__main__":
    main()
