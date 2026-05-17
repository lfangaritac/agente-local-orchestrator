#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
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


def _rm_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


def test_scaffold_creates_new_files() -> None:
    tools = _load_tools_module()

    project_id = "tmp-scaffold-test-create"
    docs_dir = ROOT / "docs" / "projects" / project_id

    _rm_tree(docs_dir)

    required = list(getattr(tools, "PROJECT_ONBOARDING_REQUIRED_FILES"))
    assert required, "PROJECT_ONBOARDING_REQUIRED_FILES vacío"

    res = tools.init_project_onboarding_scaffold({"project_id": project_id, "dry_run": False})
    assert res.get("ok") is True

    created = res.get("created")
    skipped = res.get("skipped")
    assert isinstance(created, list)
    assert isinstance(skipped, list)

    assert len(created) == len(required), f"created={len(created)} required={len(required)}"

    for name in required:
        assert (docs_dir / name).exists(), f"Falta archivo requerido: {name}"

    _rm_tree(docs_dir)


def test_scaffold_idempotent_no_overwrite() -> None:
    tools = _load_tools_module()

    project_id = "tmp-scaffold-test-idempotent"
    docs_dir = ROOT / "docs" / "projects" / project_id

    _rm_tree(docs_dir)

    required = list(getattr(tools, "PROJECT_ONBOARDING_REQUIRED_FILES"))

    # Primera ejecución: crea todo
    res1 = tools.init_project_onboarding_scaffold({"project_id": project_id, "dry_run": False})
    assert res1.get("ok") is True

    # Segunda ejecución: no debe crear; todo debe quedar en skipped
    res2 = tools.init_project_onboarding_scaffold({"project_id": project_id, "dry_run": False})
    assert res2.get("ok") is True

    created2 = res2.get("created")
    skipped2 = res2.get("skipped")
    assert isinstance(created2, list)
    assert isinstance(skipped2, list)

    assert len(created2) == 0, f"Idempotencia rota: created2={created2}"
    assert len(skipped2) == len(required), f"skipped2={len(skipped2)} required={len(required)}"

    _rm_tree(docs_dir)


def test_scaffold_skips_existing_file() -> None:
    tools = _load_tools_module()

    project_id = "tmp-scaffold-test-skip"
    docs_dir = ROOT / "docs" / "projects" / project_id

    _rm_tree(docs_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)

    marker = "DO_NOT_OVERWRITE"
    preexisting = docs_dir / "PROJECT_PROFILE.md"
    preexisting.write_text(marker, encoding="utf-8")

    required = list(getattr(tools, "PROJECT_ONBOARDING_REQUIRED_FILES"))

    res = tools.init_project_onboarding_scaffold({"project_id": project_id, "dry_run": False})
    assert res.get("ok") is True

    created = res.get("created")
    skipped = res.get("skipped")
    assert isinstance(created, list)
    assert isinstance(skipped, list)

    assert str(preexisting) in skipped, "El archivo preexistente debería quedar en skipped"

    content_after = preexisting.read_text(encoding="utf-8", errors="replace")
    assert content_after == marker, "El scaffold sobrescribió un archivo existente (prohibido)"

    for name in required:
        assert (docs_dir / name).exists(), f"Falta archivo requerido: {name}"

    _rm_tree(docs_dir)


def main() -> None:
    test_scaffold_creates_new_files()
    print("[PASS] scaffold crea archivos nuevos")

    test_scaffold_idempotent_no_overwrite()
    print("[PASS] scaffold es idempotente (no sobrescribe)")

    test_scaffold_skips_existing_file()
    print("[PASS] scaffold respeta skipped y no sobrescribe archivos existentes")


if __name__ == "__main__":
    main()
