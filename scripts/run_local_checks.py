"""run_local_checks.py

Runner local mínimo y reproducible para ejecutar checks críticos del repo.

Diseño:
- No ejecuta OpenCode real.
- Salida JSON compacta.
- Exit code 0 si todo OK; !=0 si algún check falla o si --require-clean y git está sucio.

Uso:
  python .\\scripts\\run_local_checks.py --mode quick
  python .\\scripts\\run_local_checks.py --mode full --include-git-status
  python .\\scripts\\run_local_checks.py --mode quick --include-git-status --require-clean
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class CheckResult:
    name: str
    command: list[str]
    ok: bool
    returncode: int
    elapsed_ms: int
    stdout_preview: str
    stderr_preview: str


def _preview(text: str, limit: int = 800) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n")
    if len(text) <= limit:
        return text
    return text[:limit] + "...<truncated>"


def _run_check(name: str, command: list[str], timeout_s: int = 120) -> CheckResult:
    start = time.perf_counter()

    try:
        completed = subprocess.run(
            command,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
        )
        rc = int(completed.returncode)
        out = completed.stdout or ""
        err = completed.stderr or ""
        ok = rc == 0
    except subprocess.TimeoutExpired as exc:
        rc = 124
        out = getattr(exc, "stdout", "") or ""
        err = (getattr(exc, "stderr", "") or "") + "\nTIMEOUT"
        ok = False
    except Exception as exc:
        rc = 125
        out = ""
        err = f"EXCEPTION: {exc}"
        ok = False

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    return CheckResult(
        name=name,
        command=command,
        ok=ok,
        returncode=rc,
        elapsed_ms=elapsed_ms,
        stdout_preview=_preview(out),
        stderr_preview=_preview(err),
    )


def _py_compile(path: str) -> tuple[str, list[str]]:
    return (f"py_compile:{path}", [sys.executable, "-m", "py_compile", path])


def _py_run(path: str) -> tuple[str, list[str]]:
    return (f"run:{path}", [sys.executable, path])


def _git_status_short() -> tuple[str, list[str]]:
    return ("git:status_short", ["git", "status", "--short"])


def _build_checks(mode: str, *, include_mcp_stdio_tests: bool) -> list[tuple[str, list[str]]]:
    """Construye la lista de checks.

    Regla de side-effects:
    - quick: sin side-effects.
    - full: sin side-effects por defecto.
    - full + include_mcp_stdio_tests: incluye tests stdio MCP que pueden crear
      artefactos operativos ignorados por Git (runs/handoffs de prueba).
    """

    # Nota: usamos rutas con .\ para que coincidan con los comandos operativos del repo.
    quick: list[tuple[str, list[str]]] = [
        _py_compile(r".\scripts\audit_agent_artifacts.py"),
        _py_compile(r".\scripts\run_opencode_from_handoff.py"),

        _py_run(r".\scripts\test_opencode_cli_model_resolution.py"),
        _py_run(r".\scripts\test_postcheck_scope_guardrail.py"),
        _py_run(r".\scripts\test_audit_agent_artifacts_health.py"),
        _py_run(r".\scripts\test_audit_agent_artifacts_archive.py"),
                _py_run(r".\scripts\test_create_and_dispatch_pregate.py"),

    ]

    if mode == "quick":
        return quick


    # full (por defecto): checks adicionales sin side-effects.
    full_extra: list[tuple[str, list[str]]] = [
        _py_compile(r".\scripts\create_and_dispatch_opencode_handoff.py"),
        _py_compile(r".\scripts\start_opencode_from_handoff_async.py"),
        _py_compile(r".\mcp_server\tools.py"),
        _py_compile(r".\mcp_server\schemas.py"),
    ]

    if not include_mcp_stdio_tests:
        return quick + full_extra

        # Opcional (side-effects): tests stdio MCP que crean artefactos operativos ignorados por Git.
    mcp_stdio_tests: list[tuple[str, list[str]]] = [
        _py_run(r".\mcp_server\test_guardrails_autoapprove_permissions_stdio.py"),
        _py_run(r".\mcp_server\test_create_and_dispatch_opencode_handoff_stdio.py"),
        _py_run(r".\mcp_server\test_run_health_check_stdio.py"),
        _py_run(r".\mcp_server\test_enable_target_project_stdio.py"),
    ]

    return quick + full_extra + mcp_stdio_tests



def main() -> None:
    parser = argparse.ArgumentParser(description="Runner local de checks (compact-first).")
    parser.add_argument("--mode", choices=["quick", "full"], default="quick")
    parser.add_argument("--include-git-status", action="store_true")
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument(
        "--include-mcp-stdio-tests",
        action="store_true",
        help=(
            "Incluye tests stdio del MCP server que pueden crear runs/handoffs de prueba "
            "(artefactos operativos ignorados por Git). Por defecto están excluidos para evitar side-effects."
        ),
    )
    parser.add_argument("--timeout-s", type=int, default=120, help="Timeout por check.")

    args = parser.parse_args()

    start_all = time.perf_counter()

    check_specs: list[tuple[str, list[str]]] = []
    if args.include_git_status:
        check_specs.append(_git_status_short())

    check_specs.extend(
        _build_checks(
            str(args.mode),
            include_mcp_stdio_tests=bool(args.include_mcp_stdio_tests),
        )
    )

    results: list[CheckResult] = []
    require_clean_failed = False
    git_clean: bool | None = None

    for name, cmd in check_specs:
        r = _run_check(name=name, command=cmd, timeout_s=int(args.timeout_s))

        if name == "git:status_short":
            # No falla por dirty salvo --require-clean.
            dirty = bool((r.stdout_preview or "").strip())
            git_clean = not dirty
            if args.require_clean and dirty:
                r.ok = False
                r.returncode = 1
                require_clean_failed = True
                if not any("working tree" in e.lower() for e in [r.stderr_preview]):
                    r.stderr_preview = (r.stderr_preview + "\n" if r.stderr_preview else "") + "Working tree no está limpio (--require-clean)."

        results.append(r)

    passed = sum(1 for r in results if r.ok)
    failed = sum(1 for r in results if not r.ok)

    failed_checks = [r for r in results if not r.ok]

    duration_ms = int((time.perf_counter() - start_all) * 1000)

    first_failure: dict | None = None
    if failed_checks:
        f = failed_checks[0]
        first_failure = {
            "name": f.name,
            "returncode": f.returncode,
            "elapsed_ms": f.elapsed_ms,
            "command": f.command,
            "stdout_preview": f.stdout_preview,
            "stderr_preview": f.stderr_preview,
        }

    out = {
        "ok": failed == 0,
        "mode": str(args.mode),
        "total_checks": len(results),
        "passed": passed,
        "failed": failed,
        "duration_ms": duration_ms,
        "include_git_status": bool(args.include_git_status),
        "require_clean": bool(args.require_clean),
        "git_clean": git_clean,
        "mcp_stdio_tests_included": bool(args.include_mcp_stdio_tests),
        "failed_checks_names": [r.name for r in failed_checks],
        "first_failure": first_failure,
        "checks": [
            {
                "name": r.name,
                "command": r.command,
                "ok": r.ok,
                "returncode": r.returncode,
                "elapsed_ms": r.elapsed_ms,
                "stdout_preview": r.stdout_preview,
                "stderr_preview": r.stderr_preview,
            }
            for r in results
        ],
        "root": str(ROOT),
        "platform": {
            "python": sys.version.split()[0],
            "exe": sys.executable,
            "cwd": os.getcwd(),
        },
    }

    print(json.dumps(out, ensure_ascii=False, separators=(",", ":")))

    # Exit code confiable
    if failed != 0 or require_clean_failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
