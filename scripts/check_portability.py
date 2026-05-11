#!/usr/bin/env python3
"""
check_portability.py

Read-only validator for rehydration/portability of the orchestrator.

Checks:
  - ROOT existence and structure
  - python/git availability
  - verify_master_files integrity
  - operational status (without quick checks by default)
  - hard-coded absolute path warnings

Output: JSON (--output json) or human-readable text (default).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# Best-effort: force UTF-8 stdout on Windows to avoid UnicodeEncodeError when
# printing JSON with non-ASCII characters.
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def get_root() -> Path:
    return Path(__file__).resolve().parents[1]


def check_python() -> dict[str, object]:
    info: dict[str, object] = {
        "available": True,
        "version": sys.version.split()[0],
        "executable": sys.executable,
    }
    return info


def check_git() -> dict[str, object]:
    info: dict[str, object] = {
        "available": False,
        "version": None,
        "error": None,
    }
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            info["available"] = True
            info["version"] = result.stdout.strip()
    except FileNotFoundError:
        info["error"] = "git binary not found in PATH"
    except Exception as exc:
        info["error"] = str(exc)
    return info


def check_root(root: Path) -> dict[str, object]:
    info: dict[str, object] = {
        "exists": root.exists(),
        "is_dir": root.is_dir(),
        "absolute_path": str(root.resolve()),
    }
    if root.exists():
        items = list(root.iterdir())
        info["item_count"] = len(items)
    return info


def run_verify_master_files(root: Path) -> dict[str, object]:
    script = root / "scripts" / "verify_master_files.py"
    info: dict[str, object] = {
        "script_exists": script.exists(),
        "result": None,
        "error": None,
    }
    if not script.exists():
        info["error"] = "verify_master_files.py not found"
        return info
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--compact"],
            capture_output=True, text=True, timeout=30,
            cwd=str(root),
        )
        if result.returncode == 0:
            try:
                info["result"] = json.loads(result.stdout.strip())
            except (json.JSONDecodeError, ValueError):
                info["result"] = {"raw_stdout": result.stdout.strip()}
        else:
            info["error"] = f"exit code {result.returncode}: {result.stderr.strip()}"
    except Exception as exc:
        info["error"] = str(exc)
    return info


def run_operational_status_script(root: Path, include_quick: bool) -> dict[str, object]:
    """Ejecuta audit_agent_artifacts.py --operational-status (read-only) y parsea JSON."""

    script = root / "scripts" / "audit_agent_artifacts.py"
    info: dict[str, object] = {
        "script_exists": script.exists(),
        "ok": None,
        "parsed": None,
        "returncode": None,
        "error": None,
    }

    if not script.exists():
        info["error"] = "audit_agent_artifacts.py not found"
        return info

    cmd = [
        sys.executable,
        str(script),
        "--operational-status",
        "--include-git-status",
    ]
    if include_quick:
        cmd.append("--run-quick-checks")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            cwd=str(root),
        )
        info["returncode"] = result.returncode
        stdout = (result.stdout or "").strip()
        if stdout:
            try:
                info["parsed"] = json.loads(stdout)
            except Exception:
                info["parsed"] = {"raw_stdout_truncated": stdout[:2000]}
        info["ok"] = result.returncode == 0
        if result.returncode != 0 and not info.get("parsed"):
            info["error"] = (result.stderr or "").strip()[:2000]
    except Exception as exc:
        info["error"] = str(exc)

    return info


def get_operational_status(root: Path, include_quick: bool = False) -> dict[str, object]:
    """Resumen compacto de estado operativo (sin modificar repo)."""

    status: dict[str, object] = {
        "python": check_python()["available"],
        "git": check_git()["available"],
        "run_local_checks_available": (root / "scripts" / "run_local_checks.py").exists(),
        "operational_status": run_operational_status_script(root, include_quick=include_quick),
    }

    # Extraer valores compactos útiles si el JSON parseó.
    parsed = status["operational_status"].get("parsed")
    if isinstance(parsed, dict):
        status["operational_overall_status"] = parsed.get("overall_status")
        status["operational_build_blocked"] = parsed.get("build_blocked")
        status["operational_ready_to_advance"] = parsed.get("ready_to_advance")

    return status


HARDCODED_PATH_PATTERNS = [
    "C:\\Agente",
    "C:\\Agente_Archives",
    "C:/Agente",
    "C:/Agente_Archives",
]

SCAN_EXCLUDE_DIRS = {
    "docs\\agent_runs",
    "docs/agent_runs",
    "docs\\agent_queue",
    "docs/agent_queue",
    "raw_outputs",
    ".git",
}


def _should_scan(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return False
    for excluded in SCAN_EXCLUDE_DIRS:
        excluded_posix = excluded.replace("\\", "/")
        if rel == excluded_posix or rel.startswith(excluded_posix + "/"):
            return False
    return True


def scan_hardcoded_paths(root: Path, *, max_findings: int = 25) -> list[dict[str, object]]:
    """Escanea menciones de rutas absolutas comunes (best-effort, acotado)."""

    warnings: list[dict[str, object]] = []
    allowed_suffixes = {".py", ".md", ".txt", ".bat", ".ps1", ".json"}

    for dirpath, dirnames, filenames in os.walk(str(root)):
        current = Path(dirpath)
        if not _should_scan(current, root):
            dirnames[:] = []
            continue

        for filename in filenames:
            if len(warnings) >= max_findings:
                return warnings

            file_path = current / filename
            suffix = file_path.suffix.lower()
            if suffix and suffix not in allowed_suffixes:
                continue

            try:
                # Evitar archivos muy grandes.
                if file_path.stat().st_size > 1_000_000:
                    continue
            except Exception:
                continue

            try:
                rel = file_path.relative_to(root).as_posix()
            except ValueError:
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            for pattern in HARDCODED_PATH_PATTERNS:
                idx = content.find(pattern)
                if idx != -1:
                    line_number = content[:idx].count("\n") + 1
                    warnings.append({
                        "file": rel,
                        "pattern": pattern,
                        "line": line_number,
                        "snippet": content[max(0, idx - 20):idx + len(pattern) + 40].replace("\n", " ").strip(),
                    })
                    break

    return warnings


def verify(root: Path, include_quick: bool = False) -> dict[str, object]:
    start = time.perf_counter()

    root_info = check_root(root)
    python_info = check_python()
    git_info = check_git()
    master_info = run_verify_master_files(root)
    op_status = get_operational_status(root, include_quick=include_quick)
    warnings = scan_hardcoded_paths(root, max_findings=25)

    # Derivar estado de verify_master_files
    verify_master_ok = False
    if master_info.get("result") and isinstance(master_info["result"], dict):
        verify_master_ok = bool(master_info["result"].get("all_ok"))

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    root_ok = root_info.get("exists") is True and root_info.get("is_dir") is True
    python_ok = python_info.get("available") is True
    git_ok = git_info.get("available") is True

    errors: list[str] = []
    if not root_ok:
        errors.append("root_not_found")
    if not python_ok:
        errors.append("python_not_available")
    if not git_ok:
        errors.append("git_not_available")
    if master_info.get("script_exists") is not True:
        errors.append("verify_master_files_missing")
    elif not verify_master_ok:
        errors.append("verify_master_files_failed")

    # operational-status es read-only; si build_blocked=true (p.ej. git_dirty),
    # reportarlo como warning pero no bloquear portabilidad.
    op_parsed = (op_status.get("operational_status") or {}).get("parsed")
    if isinstance(op_parsed, dict):
        if op_parsed.get("build_blocked") is True:
            warnings.append({
                "file": "(operational_status)",
                "pattern": "build_blocked=true",
                "line": 0,
                "snippet": f"overall_status={op_parsed.get('overall_status')} blockers={op_parsed.get('blockers')}"
            })

    ok = len(errors) == 0
    status = "ok" if ok else "error"
    if ok and warnings:
        status = "warn"

    result = {
        "ok": ok,
        "status": status,
        "elapsed_ms": elapsed_ms,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root.resolve()),
        "checks": {
            "root": root_info,
            "python": python_info,
            "git": git_info,
            "verify_master_files": master_info,
            "operational_status": op_status,
        },
        "warnings": {
            "hardcoded_paths_count": len(warnings),
            "hardcoded_paths": warnings,
        },
        "errors": errors,
        "next_action": (
            "Run: python .\\scripts\\run_local_checks.py --mode full --include-git-status"
            if ok else
            "Fix errors and re-run: python .\\scripts\\check_portability.py --output json"
        ),
        "summary": {
            "root_ok": root_ok,
            "python_ok": python_ok,
            "git_ok": git_ok,
            "verify_master_ok": verify_master_ok,
            "hardcoded_path_warnings": len(warnings),
        },
    }

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Valida rehidratación/portabilidad del orquestador."
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Formato de salida (default: text).",
    )
    parser.add_argument(
        "--include-quick",
        action="store_true",
        help="Incluir quick checks en operational_status.",
    )
    args = parser.parse_args()

    root = get_root()
    result = verify(root, include_quick=bool(args.include_quick))

    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        s = result["summary"]
        print(f"=== Portability Check ===")
        print(f"Root exists : {'YES' if s['root_ok'] else 'NO'}")
        print(f"Python      : {'YES' if s['python_ok'] else 'NO'} ({result['checks']['python'].get('version', '?')})")
        print(f"Git         : {'YES' if s['git_ok'] else 'NO'}")
        print(f"Master files: {'OK' if s['verify_master_ok'] else 'ISSUES'}")
        print(f"Path warnings: {s['hardcoded_path_warnings']}")
        if result["warnings"]["hardcoded_paths"]:
            for w in result["warnings"]["hardcoded_paths"]:
                print(f"  WARN: {w['file']}:{w['line']} contains '{w['pattern']}'")
        print(f"Elapsed: {result['elapsed_ms']} ms")


if __name__ == "__main__":
    main()
