#!/usr/bin/env python3
"""
apply_to_project.py

Aplica el sistema operativo de agentes desde este orquestador local hacia otro proyecto.

Uso:
python scripts/apply_to_project.py --target "C:\Ruta\Del\Proyecto"

No copia secrets.
No sobrescribe archivos existentes.
No hace commit ni push en el proyecto destino.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path.cwd()

FILES_TO_COPY = [
    "AGENT_RULES.md",
    "PROJECT_CONTEXT.md",
    "REPLIT_HANDOFF.md",
    "SECURITY_POLICY.md",
    "MODEL_ROUTING.md",
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Aplicar sistema de agentes a otro proyecto.")
    parser.add_argument("--target", required=True, help="Ruta del proyecto destino.")
    args = parser.parse_args()

    target_root = Path(args.target).expanduser().resolve()

    if not target_root.exists():
        raise SystemExit(f"El proyecto destino no existe: {target_root}")

    copied: list[str] = []
    skipped: list[str] = []
    created: list[str] = []

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

    print("\nSistema aplicado al proyecto destino.\n")
    print(f"Destino: {target_root}")

    if created:
        print("\nCarpetas creadas:")
        for item in created:
            print(f"- {item}")

    if copied:
        print("\nArchivos copiados:")
        for item in copied:
            print(f"- {item}")

    if skipped:
        print("\nOmitidos porque ya existían o no estaban disponibles:")
        for item in skipped:
            print(f"- {item}")

    print("\nSiguientes pasos en el proyecto destino:")
    print("1. Revisar PROJECT_CONTEXT.md.")
    print("2. Revisar SECRETS_MANIFEST.md.")
    print("3. Ejecutar: .\\activate-agents.bat")
    print("4. Ejecutar: python .\\scripts\\check_env.py")
    print("5. Revisar: git status")
    print("6. Versionar manualmente si corresponde.")


if __name__ == "__main__":
    main()
