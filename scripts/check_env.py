#!/usr/bin/env python3
"""
check_env.py

Valida configuración mínima del orquestador local.

Este proyecto no debe exigir variables de base de datos por defecto.
Las variables sensibles de proyectos específicos deben validarse dentro de cada proyecto activado,
no en el orquestador base.
"""

from __future__ import annotations

import os


OPTIONAL_VARS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GITHUB_TOKEN",
    "REPLIT_API_TOKEN",
    "OLLAMA_HOST",
]


def main() -> None:
    print("Base orchestrator environment check completed.")

    configured_optional = [name for name in OPTIONAL_VARS if os.getenv(name)]

    if configured_optional:
        print("Configured optional variables:")
        for name in configured_optional:
            print(f"- {name}")
    else:
        print("No optional integration variables detected.")

    print("No required environment variables are enforced at the base orchestrator level.")


if __name__ == "__main__":
    main()
