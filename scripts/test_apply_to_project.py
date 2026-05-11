#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

# Fase 6 — Cambio mínimo controlado (handoff 20260510_190034_a2de4ca5)

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "apply_to_project.py"
ORCHESTRATOR_ROOT = HERE.parent


def _run(args: list[str]) -> dict:
    cmd = [sys.executable, str(SCRIPT)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ORCHESTRATOR_ROOT)
    if result.returncode != 0:
        raise RuntimeError(
            f"Script fallo con codigo {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
    return json.loads(result.stdout.strip())


def _run_raw(args: list[str]) -> tuple[dict, int]:
    cmd = [sys.executable, str(SCRIPT)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ORCHESTRATOR_ROOT)
    try:
        data = json.loads(result.stdout.strip())
    except (json.JSONDecodeError, ValueError):
        data = {}
    return data, result.returncode


def _count_items(path: Path) -> int:
    count = 0
    if path.is_dir():
        for _ in path.rglob("*"):
            count += 1
    return count


_REGISTRY_TEMPLATE = """\
project_id: {id}
nombre_can\u00f3nico: {name}
alias_permitidos: {aliases}
ruta_local: {path}
"""


def _write_registry(entries: list[dict], path: Path) -> None:
    blocks = []
    for e in entries:
        blocks.append(_REGISTRY_TEMPLATE.format(**e))
    path.write_text("\n".join(blocks), encoding="utf-8")


def test_dry_run_creates_nothing() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "destino"
        target.mkdir(parents=True)

        data = _run(["--target", str(target), "--dry-run", "--output", "json"])

        assert data["ok"] is True, "ok debe ser True"
        assert data["dry_run"] is True, "dry_run debe ser True"
        assert data["target"] == str(target), "target debe coincidir"
        assert data["created_dirs"] == [], "dry-run no debe crear directorios"
        assert data["copied_files"] == [], "dry-run no debe copiar archivos"
        assert len(data["skipped"]) > 0, "dry-run debe reportar acciones en skipped"

        items_after = _count_items(target)
        assert items_after == 0, (
            f"dry-run no debe crear archivos/dirs en destino, "
            f"pero se encontraron {items_after} items"
        )

    print("[PASS] Case A: dry-run + json no crea nada")


def test_real_execution_creates_items() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "destino"
        target.mkdir(parents=True)

        data = _run(["--target", str(target), "--output", "json"])

        assert data["ok"] is True, "ok debe ser True"
        assert data["dry_run"] is False, "dry_run debe ser False"
        assert data["target"] == str(target), "target debe coincidir"

        assert len(data["created_dirs"]) >= 1, (
            f"debe crear al menos un directorio, pero created_dirs={data['created_dirs']}"
        )

        assert len(data["copied_files"]) >= 1, (
            f"debe copiar al menos un archivo, pero copied_files={data['copied_files']}"
        )

        for d in data["created_dirs"]:
            d_path = Path(d)
            assert d_path.is_dir(), f"directorio no creado: {d}"

        for f in data["copied_files"]:
            f_path = Path(f)
            assert f_path.exists(), f"item no copiado: {f}"

    print("[PASS] Case B: ejecucion real copia archivos y crea directorios")


def test_no_overwrite_skips_existing() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "destino"
        target.mkdir(parents=True)

        existing_file = target / "AGENT_RULES.md"
        original_content = "CONTENIDO ORIGINAL NO SOBRESCRITO"
        existing_file.write_text(original_content, encoding="utf-8")

        existing_script_dir = target / "scripts"
        existing_script_dir.mkdir(exist_ok=True)

        data = _run(["--target", str(target), "--output", "json"])

        assert data["ok"] is True, "ok debe ser True"

        skipped_strs = [str(s) for s in data["skipped"]]
        assert str(existing_file) in skipped_strs, (
            f"AGENT_RULES.md debe aparecer en skipped, pero skipped={data['skipped']}"
        )

        assert existing_file.read_text(encoding="utf-8") == original_content, (
            "AGENT_RULES.md no debe sobrescribirse"
        )

        if str(existing_script_dir) in data["created_dirs"]:
            print(
                f"  [WARN] scripts/ aparecio en created_dirs (esperable si "
                f"create_dir_if_missing reporta aunque ya exista)"
            )

    print("[PASS] Case C: archivos existentes no se sobrescriben")


def test_resolve_project_id() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        reg_path = Path(tmp) / "registry.md"
        proj_path = Path(tmp) / "proj_alpha"
        proj_path.mkdir(parents=True)

        _write_registry(
            [
                {
                    "id": "alpha",
                    "name": "Alpha Project",
                    "aliases": "alpha, a1",
                    "path": str(proj_path),
                },
            ],
            reg_path,
        )

        data = _run(
            [
                "--project",
                "alpha",
                "--resolve-only",
                "--registry-path",
                str(reg_path),
            ]
        )

        assert data["ok"] is True, f"ok debe ser True, got: {data}"
        assert data["project_found"] is True, "project_found debe ser True"
        assert data["matched_by"] == "project_id", (
            f"matched_by debe ser project_id, got: {data['matched_by']}"
        )
        assert data["project"]["id"] == "alpha"
        assert data["project"]["name"] == "Alpha Project"

        # Verify nothing was written to the project path
        items = _count_items(proj_path)
        assert items == 0, (
            f"resolve-only no debe crear archivos en proyecto, "
            f"pero se encontraron {items} items"
        )

    print("[PASS] Case D: resolve-only por project_id")


def test_resolve_alias() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        reg_path = Path(tmp) / "registry.md"
        proj_path = Path(tmp) / "proj_beta"
        proj_path.mkdir(parents=True)

        _write_registry(
            [
                {
                    "id": "beta",
                    "name": "Beta Project",
                    "aliases": "beta, b1, b-project",
                    "path": str(proj_path),
                },
            ],
            reg_path,
        )

        data = _run(
            [
                "--project",
                "b1",
                "--resolve-only",
                "--registry-path",
                str(reg_path),
            ]
        )

        assert data["ok"] is True, f"ok debe ser True, got: {data}"
        assert data["project_found"] is True, "project_found debe ser True"
        assert data["matched_by"] == "alias", (
            f"matched_by debe ser alias, got: {data['matched_by']}"
        )
        assert data["project"]["id"] == "beta"
        assert data["project"]["name"] == "Beta Project"
        assert "b1" in data["project"]["aliases"]

    print("[PASS] Case E: resolve-only por alias")


def test_resolve_preserves_remote_metadata() -> None:
    """Campos opcionales: deben preservarse en resolve-only cuando están en el registry."""

    with tempfile.TemporaryDirectory() as tmp:
        reg_path = Path(tmp) / "registry.md"

        reg_path.write_text(
            "\n".join(
                [
                    "project_id: remote-1",
                    "nombre_canónico: Remote One",
                    "alias_permitidos: r1",
                    "ruta_local:",
                    "environment_type: replit-git",
                    "replit_workspace_path: /home/runner/workspace",
                    "replit_join_url: https://replit.com/join/example",
                    "repo_url: https://github.com/example/repo",
                    "local_path: null",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        data = _run(
            [
                "--project",
                "r1",
                "--resolve-only",
                "--registry-path",
                str(reg_path),
            ]
        )

        assert data["ok"] is True
        assert data["project_found"] is True
        assert data["matched_by"] == "alias"

        proj = data["project"]
        assert proj["id"] == "remote-1"
        assert proj["name"] == "Remote One"
        assert proj["path"] == "", "ruta_local vacía debe resolver a path vacío"

        assert proj.get("environment_type") == "replit-git"
        assert proj.get("replit_workspace_path") == "/home/runner/workspace"
        assert proj.get("replit_join_url") == "https://replit.com/join/example"
        assert proj.get("repo_url") == "https://github.com/example/repo"
        assert proj.get("local_path") is None, "local_path: null debe normalizarse a None"

    print("[PASS] Case E2: resolve-only preserva metadata remota")


def test_ambiguity() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        reg_path = Path(tmp) / "registry.md"
        proj_a = Path(tmp) / "proj_a"
        proj_b = Path(tmp) / "proj_b"
        proj_a.mkdir(parents=True)
        proj_b.mkdir(parents=True)

        _write_registry(
            [
                {
                    "id": "gamma",
                    "name": "Gamma One",
                    "aliases": "gamma, shared, g1",
                    "path": str(proj_a),
                },
                {
                    "id": "delta",
                    "name": "Delta Two",
                    "aliases": "delta, shared, d1",
                    "path": str(proj_b),
                },
            ],
            reg_path,
        )

        data, rc = _run_raw(
            [
                "--project",
                "shared",
                "--resolve-only",
                "--registry-path",
                str(reg_path),
            ]
        )

        assert rc != 0, f"returncode debe ser != 0 para ambiguedad, got {rc}"
        assert data["ok"] is False, "ok debe ser False para ambiguedad"
        assert len(data.get("candidates", [])) >= 2, (
            f"debe haber al menos 2 candidates, got: {data.get('candidates')}"
        )
        assert data["matched_by"] == "alias"

    print("[PASS] Case F: ambiguedad detectada correctamente")


def main() -> None:
    print("Ejecutando tests para apply_to_project.py...\n")
    tests = [
        test_dry_run_creates_nothing,
        test_real_execution_creates_items,
        test_no_overwrite_skips_existing,
        test_resolve_project_id,
        test_resolve_alias,
        test_resolve_preserves_remote_metadata,
        test_ambiguity,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1

    print(f"\nResultado: {passed} pasaron, {failed} fallaron")
    raise SystemExit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
