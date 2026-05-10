"""test_postcheck_scope_guardrail.py

Prueba unitaria del guardrail post-run de alcance (post-check):
validación del diff (git diff --name-only) contra allowed_files.

Requisitos:
- No invoca OpenCode.
- No ejecuta git.
- No toca el working tree.

Ejecución sugerida:
  python .\\scripts\\test_postcheck_scope_guardrail.py
"""

from __future__ import annotations

import json


def main() -> None:
    # Import local: al ejecutarse desde scripts/, Python incluye este dir en sys.path.
    import run_opencode_from_handoff as runner

    cases = []

    def check(label: str, changed_files: list[str], allowed_files: list[str], expected_status: str, expected_out: list[str]) -> None:
        got = runner.validate_diff_scope(changed_files=changed_files, allowed_files=allowed_files)

        if got.get("status") != expected_status:
            raise AssertionError(f"{label}: status esperado={expected_status!r} got={got!r}")

        out = got.get("out_of_scope_changes")
        if out != expected_out:
            raise AssertionError(f"{label}: out_of_scope esperado={expected_out!r} got={got!r}")

        cases.append({"label": label, "ok": True, "got": got})

    # 1) OK: todo dentro de allowed_files.
    check(
        "ok_single_allowed",
        changed_files=["QUICK_START.md"],
        allowed_files=["QUICK_START.md"],
        expected_status="build_applied",
        expected_out=[],
    )

    # 2) Error: hay cambios fuera de allowed_files.
    check(
        "error_out_of_scope",
        changed_files=["QUICK_START.md", "README.md"],
        allowed_files=["QUICK_START.md"],
        expected_status="error",
        expected_out=["README.md"],
    )

    # 3) No-op: sin cambios.
    check(
        "no_changes",
        changed_files=[],
        allowed_files=["QUICK_START.md"],
        expected_status="no_changes",
        expected_out=[],
    )

    # 4) Normalización: separadores Windows vs POSIX.
    check(
        "normalize_slashes",
        changed_files=[r"docs\foo.md"],
        allowed_files=["docs/foo.md"],
        expected_status="build_applied",
        expected_out=[],
    )

    print(json.dumps({"ok": True, "cases": cases}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
