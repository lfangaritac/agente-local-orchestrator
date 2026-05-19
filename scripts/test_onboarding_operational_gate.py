#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import tempfile
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


def _rm_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


def _git_init(repo_dir: Path) -> None:
    repo_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True, text=True)


def _append_temp_registry_entry(*, project_id: str, local_path: str) -> bytes:
    # Importante: preservar bytes exactos (incl. CRLF) para que la prueba NO deje git dirty.
    original = REGISTRY_PATH.read_bytes()

    # Formato mínimo compatible con _parse_registry_entries (separa por blanco).
    entry = (
        "\r\n\r\n"
        f"- project_id: {project_id}\r\n"
        f"- nombre_canónico: {project_id}\r\n"
        f"- alias_permitidos: {project_id}\r\n"
        f"- local_path: {local_path}\r\n"
        "- repo_url: \r\n"
        "- environment_type: local\r\n"
    ).encode("utf-8")

    REGISTRY_PATH.write_bytes(original + entry)
    return original


def main() -> None:
    tools = _load_tools_module()

    project_id = "tmp-onboarding-gate-proj"
    docs_dir = ROOT / "docs" / "projects" / project_id

    with tempfile.TemporaryDirectory(prefix="agente_tmp_ws_") as tmp_ws:
        ws = Path(tmp_ws)

        # 1) Workspace local (git repo) para resolver por workspace_path contra registry.
        _git_init(ws)

        # 2) Inject temporal entry en PROJECT_REGISTRY.md (fixture controlada) + cleanup robusto.
        original_registry_bytes = _append_temp_registry_entry(project_id=project_id, local_path=str(ws))

        try:
            # Ensure no onboarding docs exist -> debe degradar a onboarding_required.
            _rm_tree(docs_dir)

            plan = tools.plan_general_instruction(
                {
                    "instruction": "Diagnostica este proyecto.",
                    "workspace_path": str(ws),
                    "include_git": False,
                    "include_orchestrator_status": False,
                    "include_preflight": False,
                }
            )

            assert plan.get("status") == "onboarding_required", f"expected onboarding_required, got {plan}"
            missing = plan.get("missing_files")
            assert isinstance(missing, list) and missing, f"missing_files inválido: {missing}"

            required = list(getattr(tools, "PROJECT_ONBOARDING_REQUIRED_FILES"))
            assert set(missing) == set(required), f"missing_files != required (missing={missing} required={required})"

            flow = tools.run_general_instruction_flow(
                {
                    "instruction": "Diagnostica este proyecto.",
                    "mode": "plan",
                    "workspace_path": str(ws),
                    "include_git": False,
                    "include_orchestrator_status": False,
                    "include_preflight": False,
                }
            )

            assert flow.get("status") == "onboarding_required", f"flow.status esperado onboarding_required, got {flow}"
            assert isinstance(flow.get("missing_files"), list) and flow.get("missing_files"), "flow.missing_files faltante"

            # Guardrail: create_and_dispatch no debe continuar sin onboarding.
            dispatch = tools.create_and_dispatch_opencode_handoff(
                {
                    "project_id": project_id,
                    "objective": "Onboarding gate test: no dispatch sin scaffold.",
                    "target_agent": "builder",
                    "model": "opencode-go/kimi-k2.6",
                    "risk_level": "low",
                    "scenario": "implementation",
                    "requires_authorization": True,
                    "authorization_granted": False,
                }
            )
            assert dispatch.get("status") == "onboarding_required", f"expected onboarding_required, got {dispatch}"
            assert isinstance(dispatch.get("missing_files"), list) and dispatch.get("missing_files"), "dispatch.missing_files faltante"

            # 3) Completar onboarding y verificar que el flujo continúa normalmente.
            scaffold = tools.init_project_onboarding_scaffold({"project_id": project_id, "dry_run": False})
            assert scaffold.get("ok") is True, f"scaffold falló: {scaffold}"

            plan2 = tools.plan_general_instruction(
                {
                    "instruction": "Diagnostica este proyecto.",
                    "workspace_path": str(ws),
                    "include_git": False,
                    "include_orchestrator_status": False,
                    "include_preflight": False,
                }
            )
            assert plan2.get("status") == "ok", f"expected ok, got {plan2}"

            onboarding2 = plan2.get("onboarding")
            assert isinstance(onboarding2, dict) and onboarding2.get("status") == "ready", f"onboarding esperado ready, got {onboarding2}"

            flow2 = tools.run_general_instruction_flow(
                {
                    "instruction": "Diagnostica este proyecto.",
                    "mode": "plan",
                    "workspace_path": str(ws),
                    "include_git": False,
                    "include_orchestrator_status": False,
                    "include_preflight": False,
                }
            )
            assert flow2.get("status") == "ok", f"flow2.status esperado ok, got {flow2}"

        finally:
            # Cleanup: restore registry + borrar docs fixture.
            REGISTRY_PATH.write_bytes(original_registry_bytes)
            _rm_tree(docs_dir)

    print("[PASS] onboarding gate: plan/run/dispatch detect missing_files y recomiendan scaffold; con scaffold continúan")


if __name__ == "__main__":
    main()
