#!/usr/bin/env python3
"""
apply_to_project.py

Aplica el sistema operativo de agentes desde este orquestador local hacia otro proyecto.

Uso:
  python scripts/apply_to_project.py --target "C:/Ruta/Del/Proyecto"
  python scripts/apply_to_project.py --target "C:/Ruta/Del/Proyecto" --dry-run
  python scripts/apply_to_project.py --target "C:/Ruta/Del/Proyecto" --output json
  python scripts/apply_to_project.py --target "C:/Ruta/Del/Proyecto" --dry-run --output json

No copia secrets.
No sobrescribe archivos existentes.
No hace commit ni push en el proyecto destino.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


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

    return {
        "ok": True,
        "target": str(target_root),
        "dry_run": dry_run,
        "created_dirs": created,
        "copied_files": copied,
        "skipped": skipped,
        "notes": notes,
        "next_steps": next_steps,
    }


def _output_text(result: dict) -> None:
    print("\nSistema aplicado al proyecto destino.\n")
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
    parser.add_argument("--target", required=True, help="Ruta del proyecto destino.")
    parser.add_argument("--dry-run", action="store_true", help="Solo mostrar que hariamos sin ejecutar.")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Formato de salida.")
    args = parser.parse_args()

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

    result = _build_result(target_root, args.dry_run, created, copied, skipped)

    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=None))
    else:
        _output_text(result)


if __name__ == "__main__":
    main()
