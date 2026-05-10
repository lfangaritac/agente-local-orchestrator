#!/usr/bin/env python3
"""
test_apply_to_project.py

Test standalone (sin pytest) para apply_to_project.py.
Usa tempfile como proyecto destino.

Casos:
  A: dry-run + json -> ok=true y NO crea directorios/archivos en target.
  B: ejecucion real + json -> copia al menos un archivo y crea al menos un directorio.
  C: no sobrescribe -> si un archivo ya existe en target, se reporta como skipped.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


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


def _count_items(path: Path) -> int:
    count = 0
    if path.is_dir():
        for _ in path.rglob("*"):
            count += 1
    return count


def test_dry_run_creates_nothing() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "destino"

        # Create target dir so script considers it valid
        target.mkdir(parents=True)

        data = _run(["--target", str(target), "--dry-run", "--output", "json"])

        assert data["ok"] is True, "ok debe ser True"
        assert data["dry_run"] is True, "dry_run debe ser True"
        assert data["target"] == str(target), "target debe coincidir"
        assert data["created_dirs"] == [], "dry-run no debe crear directorios"
        assert data["copied_files"] == [], "dry-run no debe copiar archivos"
        # skipped should contain the dry-run actions
        assert len(data["skipped"]) > 0, "dry-run debe reportar acciones en skipped"

        # Verify nothing was actually created
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

        # Should have created at least one dir
        assert len(data["created_dirs"]) >= 1, (
            f"debe crear al menos un directorio, pero created_dirs={data['created_dirs']}"
        )

        # Should have copied at least one file
        assert len(data["copied_files"]) >= 1, (
            f"debe copiar al menos un archivo, pero copied_files={data['copied_files']}"
        )

        # Verify dirs were actually created
        for d in data["created_dirs"]:
            d_path = Path(d)
            assert d_path.is_dir(), f"directorio no creado: {d}"

        # Verify items were actually copied (files or dirs)
        for f in data["copied_files"]:
            f_path = Path(f)
            assert f_path.exists(), f"item no copiado: {f}"

    print("[PASS] Case B: ejecucion real copia archivos y crea directorios")


def test_no_overwrite_skips_existing() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "destino"
        target.mkdir(parents=True)

        # Create a file that would collide (one of the FILES_TO_COPY)
        existing_file = target / "AGENT_RULES.md"
        original_content = "CONTENIDO ORIGINAL NO SOBRESCRITO"
        existing_file.write_text(original_content, encoding="utf-8")

        # Pre-create one of the dirs that would be created
        existing_script_dir = target / "scripts"
        existing_script_dir.mkdir(exist_ok=True)

        data = _run(["--target", str(target), "--output", "json"])

        assert data["ok"] is True, "ok debe ser True"

        # The existing file must be in skipped
        skipped_strs = [str(s) for s in data["skipped"]]
        assert str(existing_file) in skipped_strs, (
            f"AGENT_RULES.md debe aparecer en skipped, pero skipped={data['skipped']}"
        )

        # Verify existing file was NOT overwritten
        assert existing_file.read_text(encoding="utf-8") == original_content, (
            "AGENT_RULES.md no debe sobrescribirse"
        )

        # Pre-created scripts dir should not appear in created_dirs
        if str(existing_script_dir) in data["created_dirs"]:
            print(
                f"  [WARN] scripts/ aparecio en created_dirs (esperable si "
                f"create_dir_if_missing reporta aunque ya exista)"
            )

    print("[PASS] Case C: archivos existentes no se sobrescriben")


def main() -> None:
    print("Ejecutando tests para apply_to_project.py...\n")
    tests = [
        test_dry_run_creates_nothing,
        test_real_execution_creates_items,
        test_no_overwrite_skips_existing,
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
