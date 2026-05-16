#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "prepare_project_workspace.py"
ORCHESTRATOR_ROOT = HERE.parent


def _run_json(args: list[str]) -> tuple[dict, int]:
    cmd = [sys.executable, str(SCRIPT)] + args + ["--output", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ORCHESTRATOR_ROOT)
    try:
        data = json.loads((result.stdout or "").strip())
    except Exception:
        data = {}
    return data, result.returncode


def _write_registry_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def test_clone_required_when_missing_locally() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        reg = tmp_path / "PROJECT_REGISTRY.md"

        _write_registry_text(
            reg,
            "\n".join(
                [
                    "project_id: p1",
                    "nombre_canónico: Proj One",
                    "alias_permitidos: p1, one",
                    "ruta_local:",
                    "repo_url: https://github.com/example/repo1",
                    "",
                ]
            ),
        )

        projects_root = tmp_path / "Projects"
        # Nota: no crear projects_root; el script solo sugiere rutas.

        data, rc = _run_json(
            [
                "--project",
                "one",
                "--registry-path",
                str(reg),
                "--projects-root",
                str(projects_root),
            ]
        )

        assert rc == 0, f"returncode debe ser 0, got {rc}, data={data}"
        assert data["ok"] is True
        assert data["project_found"] is True
        assert data["project_id"] == "p1"
        assert data["repo_url"] == "https://github.com/example/repo1"
        assert data["local_exists"] is False
        assert data["git_repo_exists"] is False
        assert data["clone_required"] is True
        assert "git clone" in (data.get("recommended_next_command") or "")

        # No side-effects: no debe crear la ruta sugerida
        suggested = Path(data["suggested_local_path"])
        assert not suggested.exists(), "no debe crear directorios ni clonar"

    print("[PASS] Case A: repo_url presente + no existe local -> clone_required")


def test_git_repo_detected_when_dot_git_exists() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        reg = tmp_path / "PROJECT_REGISTRY.md"

        _write_registry_text(
            reg,
            "\n".join(
                [
                    "project_id: p2",
                    "nombre_canónico: Proj Two",
                    "alias_permitidos: p2, two",
                    "ruta_local:",
                    "repo_url: https://github.com/example/repo2",
                    "",
                ]
            ),
        )

        projects_root = tmp_path / "Projects"
        local = projects_root / "p2"
        (local / ".git").mkdir(parents=True)

        data, rc = _run_json(
            [
                "--project",
                "p2",
                "--registry-path",
                str(reg),
                "--projects-root",
                str(projects_root),
            ]
        )

        assert rc == 0
        assert data["ok"] is True
        assert data["local_exists"] is True
        assert data["git_repo_exists"] is True
        assert data["clone_required"] is False
        assert (data.get("recommended_next_command") or "").startswith("cd ")

    print("[PASS] Case B: .git existe -> git_repo_exists")


def test_missing_repo_url_is_error() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        reg = tmp_path / "PROJECT_REGISTRY.md"

        _write_registry_text(
            reg,
            "\n".join(
                [
                    "project_id: p3",
                    "nombre_canónico: Proj Three",
                    "alias_permitidos: p3",
                    "ruta_local:",
                    "",
                ]
            ),
        )

        data, rc = _run_json(["--project", "p3", "--registry-path", str(reg)])

        assert rc != 0, "debe fallar si no hay repo_url"
        assert data.get("ok") is False
        assert "missing_repo_url" in (data.get("errors") or [])

    print("[PASS] Case C: missing repo_url -> error claro")


def test_registry_resolution_works() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        reg = tmp_path / "PROJECT_REGISTRY.md"

        _write_registry_text(
            reg,
            "\n".join(
                [
                    "project_id: alpha",
                    "nombre_canónico: Alpha Project",
                    "alias_permitidos: a1, alpha",
                    "repo_url: https://github.com/example/alpha",
                    "",
                ]
            ),
        )

        data, rc = _run_json(["--project", "a1", "--registry-path", str(reg)])

        assert rc == 0
        assert data["ok"] is True
        assert data["project_found"] is True
        assert data["project_id"] == "alpha"

    print("[PASS] Case D: resolve por alias")


def main() -> None:
    print("Ejecutando tests para prepare_project_workspace.py...\n")

    tests = [
        test_clone_required_when_missing_locally,
        test_git_repo_detected_when_dot_git_exists,
        test_missing_repo_url_is_error,
        test_registry_resolution_works,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"[FAIL] {test.__name__}: {exc}")
            failed += 1

    print(f"\nResultado: {passed} pasaron, {failed} fallaron")
    raise SystemExit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
