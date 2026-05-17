#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

FILES_TO_COPY = [
    "AGENT_RULES.md",
    "PROJECT_CONTEXT.md",
    "REPLIT_HANDOFF.md",
    "SECURITY_POLICY.md",
    "MODEL_ROUTING.md",
    "DEVELOPMENT_CHECKS.md",
    "PROJECT_ACTIVATION_PROTOCOL.md",
    "CONTINUE_USAGE_PROTOCOL.md",
    "SECRETS_MANIFEST.md",
    "QUICK_START.md",
    "activate-agents.bat",

    # Replit/Shell bridge (opcional; no afecta proyectos locales si no se usa)
    "orquestador",
]

DIRS_TO_COPY = [
    ".continue",
]

DIRS_TO_CREATE = [
    "scripts",
    "docs/handoffs",
    "docs/decisions",
    "docs/test_reports",
]

REGISTRY_KEYS = {
    "project_id",
    "nombre_can\u00f3nico",
    "alias_permitidos",
    "ruta_local",
    "repositorio_remoto",
    "origen",
    "stack_detectado",
    "documentaci\u00f3n_principal",
    "c\u00f3digo_fuente_relevante",
    "estado_sincronizaci\u00f3n",
    "alertas_cr\u00edticas",
    "lecciones_locales",
    "\u00faltimo_an\u00e1lisis",
    "responsable",

    # --- extended metadata (remote / replit-git) ---
    # Nota: estos campos son opcionales y no afectan los fixtures existentes.
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


def _resolve_entry(entry: dict) -> dict:
    # Back-compat: mantener {id,name,path,aliases} como keys base.
    # Extensión: preservar metadata útil para proyectos remotos (p.ej. Replit+Git).
    return {
        "id": entry.get("project_id", ""),
        "name": entry.get("nombre_can\u00f3nico", ""),
        "path": entry.get("ruta_local", ""),
        "aliases": entry.get("alias_permitidos", []),
        "environment_type": _null_if_blank_or_nullish(entry.get("environment_type"))
        or _null_if_blank_or_nullish(entry.get("origen")),
        "replit_workspace_path": _null_if_blank_or_nullish(entry.get("replit_workspace_path")),
        "replit_join_url": _null_if_blank_or_nullish(entry.get("replit_join_url")),
        "repo_url": _null_if_blank_or_nullish(entry.get("repo_url"))
        or _null_if_blank_or_nullish(entry.get("repositorio_remoto")),
        "local_path": _null_if_blank_or_nullish(entry.get("local_path")),
    }


def resolve_project(query: str, entries: list[dict]) -> dict:
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

    query_path = Path(query).expanduser().resolve()
    if query_path.is_dir():
        for entry in entries:
            rl = entry.get("ruta_local", "")
            if rl:
                try:
                    if Path(rl).expanduser().resolve() == query_path:
                        result["project_found"] = True
                        result["matched_by"] = "path_direct"
                        result["project"] = _resolve_entry(entry)
                        return result
                except Exception:
                    pass

        result["project_found"] = True
        result["matched_by"] = "path_direct"
        result["project"] = {
            "id": "",
            "name": query_path.name,
            "path": str(query_path),
            "aliases": [],
        }
        return result

    query_lower = query.lower()

    for entry in entries:
        pid = entry.get("project_id", "")
        if pid and pid.lower() == query_lower:
            result["project_found"] = True
            result["matched_by"] = "project_id"
            result["project"] = _resolve_entry(entry)
            return result

    alias_matches = []
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
        name = entry.get("nombre_can\u00f3nico", "")
        if name and name.lower() == query_lower:
            result["project_found"] = True
            result["matched_by"] = "nombre_canonico"
            result["project"] = _resolve_entry(entry)
            return result

    try:
        for entry in entries:
            rl = entry.get("ruta_local", "")
            if rl:
                try:
                    if Path(rl).expanduser().resolve() == query_path:
                        result["project_found"] = True
                        result["matched_by"] = "ruta_local"
                        result["project"] = _resolve_entry(entry)
                        return result
                except Exception:
                    pass
    except Exception:
        pass

    result["ok"] = False
    result["errors"].append(f"no project matched query '{query}'")
    return result


def _dry_register(source: Path, target: Path, dry_actions: list[str], label: str) -> None:
    if not source.exists():
        dry_actions.append(f"[SKIP] {label} fuente no existe: {source}")
        return
    if target.exists():
        dry_actions.append(f"[SKIP] {label} ya existe: {target}")
        return
    dry_actions.append(f"[COPY] {label}: {source} -> {target}")


def copy_file_if_missing(source: Path, target: Path, copied: list[str], skipped: list[str]) -> None:
    if not source.exists():
        skipped.append(f"{source.name} no existe en orquestador")
        return
    if target.exists():
        skipped.append(str(target))
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    copied.append(str(target))


def copy_dir_missing(source: Path, target: Path, copied: list[str], skipped: list[str]) -> None:
    if not source.exists():
        skipped.append(f"{source.name} no existe en orquestador")
        return
    if target.exists():
        skipped.append(str(target))
        return
    shutil.copytree(source, target)
    copied.append(str(target))


def create_dir_if_missing(target: Path, created: list[str]) -> None:
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)
        created.append(str(target))


def _build_result(
    target_root: Path,
    dry_run: bool,
    created: list[str],
    copied: list[str],
    skipped: list[str],
    resolved_project: dict | None = None,
) -> dict:
    next_steps = [
        "1. Revisar PROJECT_CONTEXT.md.",
        "2. Revisar SECRETS_MANIFEST.md.",
        "3. Revisar DEVELOPMENT_CHECKS.md.",
        "4. Ejecutar: .\\activate-agents.bat",
        "5. Ejecutar: python .\\scripts\\check_env.py",
        "6. Revisar: git status",
        "7. Versionar manualmente si corresponde.",
    ]

    notes = []
    if not dry_run:
        notes.append(
            "scripts/check_env.py se copia como plantilla inicial. "
            "Cada proyecto destino debe ajustarlo a sus variables reales "
            "y actualizar SECRETS_MANIFEST.md sin incluir valores sensibles."
        )

    result = {
        "ok": True,
        "target": str(target_root),
        "dry_run": dry_run,
        "created_dirs": created,
        "copied_files": copied,
        "skipped": skipped,
        "notes": notes,
        "next_steps": next_steps,
    }

    if resolved_project:
        result["resolved_project"] = resolved_project

    return result


def _output_text(result: dict) -> None:
    rp = result.get("resolved_project")
    if rp:
        print(f"Proyecto resuelto: {rp.get('name') or rp.get('id') or rp.get('path', '')}")
        print()

    if result.get("resolve_only"):
        print("(resolve-only: no se realizaron cambios)")
        return

    print("Sistema aplicado al proyecto destino.\n")
    print(f"Destino: {result['target']}")
    if result["dry_run"]:
        print("(dry-run: no se realizaron cambios)")

    if result["created_dirs"]:
        print("\nCarpetas creadas:")
        for item in result["created_dirs"]:
            print(f"- {item}")

    if result["copied_files"]:
        print("\nArchivos copiados:")
        for item in result["copied_files"]:
            print(f"- {item}")

    if result["skipped"]:
        print("\nOmitidos porque ya existian o no estaban disponibles:")
        for item in result["skipped"]:
            print(f"- {item}")

    if result["notes"]:
        for note in result["notes"]:
            print(f"\nNota: {note}")

    print("\nSiguientes pasos en el proyecto destino:")
    for step in result["next_steps"]:
        print(step)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aplicar sistema de agentes a otro proyecto.")
    parser.add_argument("--target", help="Ruta del proyecto destino.")
    parser.add_argument(
        "--project",
        help="Project ID, alias, nombre canonico o ruta a resolver desde PROJECT_REGISTRY.",
    )
    parser.add_argument(
        "--resolve-only",
        action="store_true",
        help="Solo resolver proyecto desde el registro sin copiar archivos.",
    )
    parser.add_argument(
        "--registry-path",
        default=None,
        help="Ruta al archivo PROJECT_REGISTRY.md (default: <ROOT>/PROJECT_REGISTRY.md).",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Solo mostrar que hariamos sin ejecutar."
    )
    parser.add_argument(
        "--output", choices=["text", "json"], default="text", help="Formato de salida."
    )
    args = parser.parse_args()

    if not args.project and not args.target:
        raise SystemExit("Se requiere --project o --target.")

    if args.resolve_only and not args.project:
        raise SystemExit("--resolve-only requiere --project.")

    registry_path = (
        Path(args.registry_path).expanduser().resolve()
        if args.registry_path
        else ROOT / "PROJECT_REGISTRY.md"
    )

    resolved_project = None
    if args.project:
        entries, warnings = parse_registry(registry_path)
        resolve_result = resolve_project(args.project, entries)
        if warnings:
            resolve_result.setdefault("warnings", []).extend(warnings)

        if args.resolve_only:
            print(json.dumps(resolve_result, ensure_ascii=False, indent=None))
            raise SystemExit(0 if resolve_result["ok"] else 1)

        if not resolve_result["ok"]:
            errors = "; ".join(resolve_result["errors"])
            detail = json.dumps(resolve_result, ensure_ascii=False)
            raise SystemExit(
                f"Project resolution failed: {errors}\n{detail}"
            )

        resolved_project = resolve_result["project"]

        if not args.target:
            rl = resolved_project.get("path", "")
            if rl:
                args.target = rl
            else:
                raise SystemExit(
                    "--target no especificado y el proyecto resuelto no tiene ruta_local."
                )

    if not args.target:
        raise SystemExit("--target es requerido.")

    target_root = Path(args.target).expanduser().resolve()
    if not target_root.exists():
        raise SystemExit(f"El proyecto destino no existe: {target_root}")

    copied: list[str] = []
    skipped: list[str] = []
    created: list[str] = []

    if args.dry_run:
        dry_actions: list[str] = []
        for directory in DIRS_TO_CREATE:
            d = target_root / directory
            if d.exists():
                dry_actions.append(f"[SKIP] directorio ya existe: {d}")
            else:
                dry_actions.append(f"[CREATE] directorio: {d}")
        for file_name in FILES_TO_COPY:
            _dry_register(ROOT / file_name, target_root / file_name, dry_actions, "archivo")
        for dir_name in DIRS_TO_COPY:
            _dry_register(ROOT / dir_name, target_root / dir_name, dry_actions, "directorio")
        _dry_register(
            ROOT / "scripts" / "activate_agent_system.py",
            target_root / "scripts" / "activate_agent_system.py",
            dry_actions,
            "archivo",
        )
        _dry_register(
            ROOT / "scripts" / "check_env.py",
            target_root / "scripts" / "check_env.py",
            dry_actions,
            "archivo",
        )
        skipped = dry_actions
    else:
        for directory in DIRS_TO_CREATE:
            create_dir_if_missing(target_root / directory, created)

        for file_name in FILES_TO_COPY:
            copy_file_if_missing(ROOT / file_name, target_root / file_name, copied, skipped)

        for dir_name in DIRS_TO_COPY:
            copy_dir_missing(ROOT / dir_name, target_root / dir_name, copied, skipped)

        copy_file_if_missing(
            ROOT / "scripts" / "activate_agent_system.py",
            target_root / "scripts" / "activate_agent_system.py",
            copied,
            skipped,
        )

        copy_file_if_missing(
            ROOT / "scripts" / "check_env.py",
            target_root / "scripts" / "check_env.py",
            copied,
            skipped,
        )

        # Bridge Shell hacia Orquestador (no ejecuta Replit Agent; solo genera handoff)
        copy_file_if_missing(
            ROOT / "scripts" / "orchestrator_bridge.py",
            target_root / "scripts" / "orchestrator_bridge.py",
            copied,
            skipped,
        )

    result = _build_result(target_root, args.dry_run, created, copied, skipped, resolved_project)

    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=None))
    else:
        _output_text(result)


if __name__ == "__main__":
    main()
