#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

# Keep consistent with scripts/apply_to_project.py (minimal subset + remote metadata)
REGISTRY_KEYS = {
    "project_id",
    "nombre_canónico",
    "alias_permitidos",
    "ruta_local",
    "repositorio_remoto",
    "origen",
    "environment_type",
    "replit_workspace_path",
    "replit_join_url",
    "repo_url",
    "local_path",
}


def parse_registry(registry_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not registry_path.exists():
        return [], [f"registry file not found: {registry_path}"]

    content = registry_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    entries: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    warnings: list[str] = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if current:
                entries.append(current)
                current = {}
            continue

        if stripped.startswith("#") or stripped.startswith("|---"):
            continue

        match = re.match(r'^-?\s*(.+?):\s*(.*)$', stripped)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()

            if key in REGISTRY_KEYS:
                if key == "alias_permitidos":
                    current[key] = [a.strip() for a in value.split(",") if a.strip()]
                else:
                    current[key] = value

    if current:
        entries.append(current)

    if not entries:
        warnings.append("registry_empty")

    return entries, warnings


def _null_if_blank_or_nullish(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        v = value.strip()
        if not v or v.lower() in {"null", "none", "n/a"}:
            return None
        return v
    return str(value)


def _resolve_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": entry.get("project_id", ""),
        "name": entry.get("nombre_canónico", ""),
        "aliases": entry.get("alias_permitidos", []),
        "environment_type": _null_if_blank_or_nullish(entry.get("environment_type"))
        or _null_if_blank_or_nullish(entry.get("origen")),
        "replit_workspace_path": _null_if_blank_or_nullish(entry.get("replit_workspace_path")),
        "replit_join_url": _null_if_blank_or_nullish(entry.get("replit_join_url")),
        "repo_url": _null_if_blank_or_nullish(entry.get("repo_url"))
        or _null_if_blank_or_nullish(entry.get("repositorio_remoto")),
        "local_path": _null_if_blank_or_nullish(entry.get("local_path")),
    }


def resolve_project(query: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "ok": True,
        "query": query,
        "project_found": False,
        "matched_by": None,
        "project": None,
        "candidates": [],
        "errors": [],
        "warnings": [],
    }

    query_lower = query.lower()

    for entry in entries:
        pid = entry.get("project_id", "")
        if pid and pid.lower() == query_lower:
            result["project_found"] = True
            result["matched_by"] = "project_id"
            result["project"] = _resolve_entry(entry)
            return result

    alias_matches: list[dict[str, Any]] = []
    for entry in entries:
        aliases = entry.get("alias_permitidos", [])
        if any(a.lower() == query_lower for a in aliases):
            alias_matches.append(entry)

    if len(alias_matches) == 1:
        result["project_found"] = True
        result["matched_by"] = "alias"
        result["project"] = _resolve_entry(alias_matches[0])
        return result

    if len(alias_matches) > 1:
        result["ok"] = False
        result["matched_by"] = "alias"
        result["candidates"] = [_resolve_entry(e) for e in alias_matches]
        result["errors"].append(
            f"ambiguous alias '{query}' matches {len(alias_matches)} projects"
        )
        return result

    for entry in entries:
        name = entry.get("nombre_canónico", "")
        if name and name.lower() == query_lower:
            result["project_found"] = True
            result["matched_by"] = "nombre_canonico"
            result["project"] = _resolve_entry(entry)
            return result

    result["ok"] = False
    result["errors"].append(f"no project matched query '{query}'")
    return result


def _sanitize_folder_name(value: str) -> str:
    v = (value or "").strip()
    v = re.sub(r"[^a-zA-Z0-9._-]+", "-", v)
    v = re.sub(r"-+", "-", v).strip("-.")
    return v or "unknown-project"


def _infer_repo_name(repo_url: str) -> str:
    # Very small helper: works for https://github.com/org/repo(.git)
    tail = repo_url.rstrip("/").split("/")[-1]
    if tail.endswith(".git"):
        tail = tail[: -len(".git")]
    return _sanitize_folder_name(tail)


def _get_projects_root(arg_value: str | None, warnings: list[str]) -> Path:
    if arg_value:
        return Path(arg_value).expanduser().resolve()

    env_value = os.environ.get("AGENTE_PROJECTS_HOME")
    if env_value:
        warnings.append("projects_root_from_env:AGENTE_PROJECTS_HOME")
        return Path(env_value).expanduser().resolve()

    # Default: sibling next to orchestrator root (not inside the repo)
    warnings.append("projects_root_defaulted")
    return (ROOT.parent / "Agente_Projects").resolve()


def prepare_workspace(
    *,
    project_query: str,
    registry_path: Path,
    projects_root: str | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "ok": False,
        "project_found": False,
        "project_id": None,
        "repo_url": None,
        "suggested_local_path": None,
        "local_exists": False,
        "git_repo_exists": False,
        "clone_required": False,
        "recommended_next_command": None,
        "warnings": [],
        "errors": [],
    }

    entries, reg_warnings = parse_registry(registry_path)
    if reg_warnings:
        result["warnings"].extend(reg_warnings)

    resolve_result = resolve_project(project_query, entries)
    if not resolve_result.get("ok"):
        result["errors"].extend(resolve_result.get("errors", []))
        return result

    project = resolve_result.get("project")
    if not project:
        result["errors"].append("project_not_resolved")
        return result

    pid = (project.get("id") or "").strip()
    result["project_found"] = True
    result["project_id"] = pid or None

    repo_url = (project.get("repo_url") or "").strip()
    if not repo_url:
        result["errors"].append("missing_repo_url")
        return result

    result["repo_url"] = repo_url

    pr_warnings: list[str] = []
    root_path = _get_projects_root(projects_root, pr_warnings)
    result["warnings"].extend(pr_warnings)

    # Guardrail: do not suggest the orchestrator root (or a subdir) as the projects root
    try:
        root_resolved = root_path.resolve()
        orch_root = ROOT.resolve()

        if root_resolved == orch_root:
            result["errors"].append("projects_root_invalid_equals_orchestrator_root")
            return result

        # If projects_root is inside the orchestrator repo, block.
        try:
            root_resolved.relative_to(orch_root)
            result["errors"].append("projects_root_invalid_inside_orchestrator_repo")
            return result
        except ValueError:
            pass
    except Exception:
        # Best-effort; continue
        pass

    folder = _sanitize_folder_name(pid) if pid else _infer_repo_name(repo_url)
    suggested = (root_path / folder).expanduser()

    result["suggested_local_path"] = str(suggested)

    local_exists = suggested.exists() and suggested.is_dir()
    result["local_exists"] = bool(local_exists)

    git_dir = suggested / ".git"
    git_repo_exists = git_dir.exists() and git_dir.is_dir()
    result["git_repo_exists"] = bool(git_repo_exists)

    if local_exists and not git_repo_exists:
        result["warnings"].append("local_dir_exists_but_no_git")

    result["clone_required"] = not git_repo_exists

    if result["clone_required"]:
        result["recommended_next_command"] = f'git clone "{repo_url}" "{suggested}"'
    else:
        result["recommended_next_command"] = f'cd "{suggested}"'

    result["ok"] = True
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Planificar preparación local de un proyecto Git registrado (sin clonar)."
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project ID, alias o nombre canónico a resolver desde PROJECT_REGISTRY.",
    )
    parser.add_argument(
        "--projects-root",
        default=None,
        help=(
            "Directorio raíz sugerido para repos locales. "
            "Si no se pasa, usa $AGENTE_PROJECTS_HOME o un default fuera del repo."
        ),
    )
    parser.add_argument(
        "--registry-path",
        default=None,
        help="Ruta al archivo PROJECT_REGISTRY.md (default: <ROOT>/PROJECT_REGISTRY.md).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No tiene side-effects; mantenido por consistencia (siempre no escribe).",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="json",
        help="Formato de salida (default: json).",
    )
    args = parser.parse_args()

    registry_path = (
        Path(args.registry_path).expanduser().resolve()
        if args.registry_path
        else ROOT / "PROJECT_REGISTRY.md"
    )

    data = prepare_workspace(
        project_query=args.project,
        registry_path=registry_path,
        projects_root=args.projects_root,
    )

    if args.output == "json":
        print(json.dumps(data, ensure_ascii=False, indent=None))
        raise SystemExit(0 if data.get("ok") else 1)

    # text output (compact)
    if not data.get("ok"):
        print("ERROR")
        for e in data.get("errors", []):
            print(f"- {e}")
        raise SystemExit(1)

    print(f"project_id: {data.get('project_id')}")
    print(f"repo_url: {data.get('repo_url')}")
    print(f"suggested_local_path: {data.get('suggested_local_path')}")
    print(f"local_exists: {data.get('local_exists')}")
    print(f"git_repo_exists: {data.get('git_repo_exists')}")
    print(f"clone_required: {data.get('clone_required')}")
    if data.get("warnings"):
        print("warnings:")
        for w in data["warnings"]:
            print(f"- {w}")
    print(f"next: {data.get('recommended_next_command')}")


if __name__ == "__main__":
    main()
