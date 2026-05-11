#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "check_portability.py"
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


def test_json_output_ok() -> None:
    data = _run(["--output", "json"])
    assert data["ok"] is True, f"ok debe ser True, got: {data.get('ok')}"
    assert "elapsed_ms" in data, "debe incluir elapsed_ms"
    assert "checks" in data, "debe incluir checks"
    assert "warnings" in data, "debe incluir warnings"
    assert "summary" in data, "debe incluir summary"
    assert "root" in data, "debe incluir root"
    print("[PASS] test_json_output_ok")


def test_summary_fields() -> None:
    data = _run(["--output", "json"])
    s = data["summary"]
    assert "root_ok" in s
    assert "python_ok" in s
    assert "git_ok" in s
    assert "verify_master_ok" in s
    assert "hardcoded_path_warnings" in s
    assert isinstance(s["root_ok"], bool)
    assert isinstance(s["python_ok"], bool)
    assert isinstance(s["git_ok"], bool)
    assert s["root_ok"] is True, "root debe existir"
    assert s["python_ok"] is True, "python debe estar disponible"
    print("[PASS] test_summary_fields")


def test_checks_structure() -> None:
    data = _run(["--output", "json"])
    c = data["checks"]
    for key in ("root", "python", "git", "verify_master_files", "operational_status"):
        assert key in c, f"check '{key}' debe existir"
    assert isinstance(c["root"]["exists"], bool)
    assert isinstance(c["python"]["available"], bool)
    assert isinstance(c["git"]["available"], bool)
    assert c["root"]["exists"] is True, "root debe existir en filesystem"
    assert c["python"]["available"] is True, "python debe estar disponible"
    print("[PASS] test_checks_structure")


def test_warnings_structure() -> None:
    data = _run(["--output", "json"])
    w = data["warnings"]
    assert "hardcoded_paths_count" in w
    assert "hardcoded_paths" in w
    assert isinstance(w["hardcoded_paths"], list)
    print("[PASS] test_warnings_structure")


def test_no_side_effects() -> None:
    git_before = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=ORCHESTRATOR_ROOT,
    ).stdout.strip()
    _run(["--output", "json"])
    git_after = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=ORCHESTRATOR_ROOT,
    ).stdout.strip()
    assert git_before == git_after, "check_portability no debe modificar archivos"
    print("[PASS] test_no_side_effects")


def test_include_quick_flag() -> None:
    data = _run(["--output", "json", "--include-quick"])

    op_outer = data["checks"]["operational_status"]
    op = op_outer.get("operational_status") or {}
    parsed = op.get("parsed") or {}

    runner_quick = parsed.get("runner_quick") or {}
    rq_status = runner_quick.get("status")

    assert rq_status is not None, "runner_quick.status debe existir"
    assert rq_status != "not_run", "--include-quick debe ejecutar quick checks (runner_quick.status != not_run)"

    print("[PASS] test_include_quick_flag")


def main() -> None:
    print("Ejecutando tests para check_portability.py...\n")
    tests = [
        test_json_output_ok,
        test_summary_fields,
        test_checks_structure,
        test_warnings_structure,
        test_no_side_effects,
        test_include_quick_flag,
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
